"""
Gemini LLM Service implementation.
"""
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import get_settings
from app.services.db_service import db_service
from .prompts import generate_explanation_prompt, get_static_fallback

logger = logging.getLogger(__name__)

# Cache TTL: 7 days
CACHE_TTL_DAYS = 7


class GeminiService:
    """
    Service for generating journal explanations via Gemini LLM.

    Features:
    - On-demand explanation generation
    - Supabase caching with MD5 key
    - Fallback to static text on errors
    """

    _instance: Optional["GeminiService"] = None
    _model = None
    _initialized: bool = False

    def __new__(cls) -> "GeminiService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            settings = get_settings()
            if settings.gemini_api_key and settings.gemini_explanation_enabled:
                try:
                    import google.generativeai as genai

                    genai.configure(api_key=settings.gemini_api_key)
                    self._model = genai.GenerativeModel("gemini-2.0-flash")
                    logger.info("Gemini LLM service initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini: {e}")
                    self._model = None
            else:
                logger.warning(
                    "Gemini API key not configured or explanations disabled"
                )
            self._initialized = True

    @property
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured."""
        return self._model is not None

    def _generate_cache_key(self, abstract: str, journal_id: str) -> str:
        """Generate MD5 hash cache key from abstract + journal_id."""
        content = f"{abstract[:2000]}:{journal_id}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    async def get_cached_explanation(self, cache_key: str) -> Optional[str]:
        """
        Retrieve cached explanation from Supabase.

        Args:
            cache_key: MD5 hash key

        Returns:
            Cached explanation or None
        """
        try:
            result = (
                db_service.client.table("explanation_cache")
                .select("explanation, expires_at")
                .eq("cache_key", cache_key)
                .single()
                .execute()
            )

            if result.data:
                expires_at_str = result.data["expires_at"]
                # Parse ISO format timestamp
                expires_at = datetime.fromisoformat(
                    expires_at_str.replace("Z", "+00:00")
                )
                now = datetime.now(timezone.utc)

                if now < expires_at:
                    logger.info(f"Cache hit for key: {cache_key[:8]}...")
                    return result.data["explanation"]

                # Expired - delete and return None
                db_service.client.table("explanation_cache").delete().eq(
                    "cache_key", cache_key
                ).execute()
                logger.info(f"Expired cache entry deleted: {cache_key[:8]}...")

            return None
        except Exception as e:
            # Log but don't fail - cache miss is acceptable
            logger.debug(f"Cache lookup failed (may not exist): {e}")
            return None

    async def cache_explanation(self, cache_key: str, explanation: str) -> None:
        """
        Store explanation in Supabase cache.

        Args:
            cache_key: MD5 hash key
            explanation: Generated explanation text
        """
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=CACHE_TTL_DAYS)

            db_service.client.table("explanation_cache").upsert(
                {
                    "cache_key": cache_key,
                    "explanation": explanation,
                    "created_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                }
            ).execute()
            logger.info(f"Cached explanation with key: {cache_key[:8]}...")
        except Exception as e:
            logger.error(f"Cache write failed: {e}")

    async def generate_explanation(
        self,
        abstract: str,
        journal: dict,
    ) -> tuple[str, bool]:
        """
        Generate explanation for why a journal fits the abstract.

        Args:
            abstract: User's article abstract
            journal: Journal data dict

        Returns:
            Tuple of (explanation_text, is_from_llm)
            is_from_llm is False if using fallback
        """
        journal_id = journal.get("id", "unknown")
        cache_key = self._generate_cache_key(abstract, journal_id)

        # Step 1: Check cache
        cached = await self.get_cached_explanation(cache_key)
        if cached:
            return cached, True

        # Step 2: Try Gemini
        if self.is_configured:
            try:
                prompt = generate_explanation_prompt(abstract, journal)
                response = await self._model.generate_content_async(
                    prompt,
                    generation_config={
                        "temperature": 0.3,  # Lower = more focused
                        "max_output_tokens": 300,
                        "top_p": 0.95,
                    },
                )

                explanation = response.text.strip()

                # Cache the result
                await self.cache_explanation(cache_key, explanation)

                logger.info(f"Generated explanation for journal: {journal_id}")
                return explanation, True

            except Exception as e:
                logger.error(f"Gemini API error: {e}")

        # Step 3: Fallback
        logger.warning(f"Using fallback for journal: {journal_id}")
        return get_static_fallback(journal), False


# Singleton accessor
_gemini_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance."""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService()
    return _gemini_instance
