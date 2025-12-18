"""
NLM (National Library of Medicine) API Service.

Provides MEDLINE and PMC status checking for journals.

Critical Distinction:
- MEDLINE = Quality verified (passed NLM selection committee)
- PMC = Archive only (no quality implication)

API Documentation:
https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlencode

import aiohttp

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MedlineStatus(str, Enum):
    """MEDLINE indexing status from NLM."""
    CURRENTLY_INDEXED = "currently_indexed"  # Green badge
    PMC_ONLY = "pmc_only"  # Yellow badge (in archive but not indexed)
    NOT_FOUND = "not_found"  # Continue to other checks
    ERROR = "error"  # API error


@dataclass
class NLMResult:
    """Result from NLM API check."""
    status: MedlineStatus
    medline_ta: Optional[str] = None  # MEDLINE title abbreviation
    nlm_id: Optional[str] = None  # NLM unique ID
    indexing_status: Optional[str] = None  # Raw status string
    pmc_id: Optional[str] = None  # PMC journal ID if applicable
    error_message: Optional[str] = None


class NLMService:
    """
    Service for checking journal status in NLM databases.

    Uses NCBI E-utilities API to check:
    1. NLM Catalog - For MEDLINE indexing status
    2. PMC - For archive presence

    Rate Limits:
    - Without API key: 3 requests/second
    - With API key: 10 requests/second

    Usage:
        service = NLMService()
        result = await service.check_medline_status("0028-0836")  # Nature

        if result.status == MedlineStatus.CURRENTLY_INDEXED:
            # Journal is MEDLINE indexed - high quality
        elif result.status == MedlineStatus.PMC_ONLY:
            # In PMC but not MEDLINE - warning flag
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    ESEARCH_URL = f"{BASE_URL}esearch.fcgi"
    EFETCH_URL = f"{BASE_URL}efetch.fcgi"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NLM service.

        Args:
            api_key: NLM API key (optional but recommended)
        """
        settings = get_settings()
        self._api_key = api_key or settings.nlm_api_key
        self._semaphore = asyncio.Semaphore(
            10 if self._api_key else 3
        )  # Rate limiting

    async def check_medline_status(self, issn: str) -> NLMResult:
        """
        Check if a journal is indexed in MEDLINE.

        Args:
            issn: Journal ISSN (format: ####-#### or ########)

        Returns:
            NLMResult with status and metadata
        """
        # Normalize ISSN
        issn = issn.replace("-", "").strip()
        if len(issn) != 8:
            return NLMResult(
                status=MedlineStatus.ERROR,
                error_message=f"Invalid ISSN format: {issn}"
            )

        async with self._semaphore:
            try:
                # Step 1: Search NLM Catalog for the journal
                catalog_result = await self._search_nlm_catalog(issn)
                if catalog_result:
                    return catalog_result

                # Step 2: If not in NLM Catalog, check PMC
                pmc_result = await self._check_pmc(issn)
                if pmc_result:
                    return pmc_result

                # Not found anywhere
                return NLMResult(status=MedlineStatus.NOT_FOUND)

            except asyncio.TimeoutError:
                logger.warning(f"Timeout checking NLM for ISSN {issn}")
                return NLMResult(
                    status=MedlineStatus.ERROR,
                    error_message="API timeout"
                )
            except Exception as e:
                logger.error(f"Error checking NLM for ISSN {issn}: {e}")
                return NLMResult(
                    status=MedlineStatus.ERROR,
                    error_message=str(e)
                )

    async def _search_nlm_catalog(self, issn: str) -> Optional[NLMResult]:
        """Search NLM Catalog for journal by ISSN."""
        params = {
            "db": "nlmcatalog",
            "term": f"{issn}[ISSN]",
            "retmode": "json",
            "retmax": "1",
        }
        if self._api_key:
            params["api_key"] = self._api_key

        url = f"{self.ESEARCH_URL}?{urlencode(params)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])

                if not id_list:
                    return None

                # Fetch full record to check indexing status
                nlm_id = id_list[0]
                return await self._fetch_nlm_record(nlm_id)

    async def _fetch_nlm_record(self, nlm_id: str) -> Optional[NLMResult]:
        """Fetch full NLM Catalog record to check indexing status."""
        params = {
            "db": "nlmcatalog",
            "id": nlm_id,
            "rettype": "xml",
            "retmode": "xml",
        }
        if self._api_key:
            params["api_key"] = self._api_key

        url = f"{self.EFETCH_URL}?{urlencode(params)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None

                xml_text = await response.text()

                # Parse indexing status from XML
                # Look for: <CurrentIndexingStatus>Y</CurrentIndexingStatus>
                # or: <IndexingSourceName>MEDLINE</IndexingSourceName>
                is_currently_indexed = (
                    "<CurrentIndexingStatus>Y</CurrentIndexingStatus>" in xml_text
                    or ">Currently indexed<" in xml_text
                    or "CurrentlyIndexedForMEDLINE" in xml_text
                )

                # Extract MEDLINE TA (title abbreviation)
                medline_ta = None
                ta_match = re.search(r"<MedlineTA>([^<]+)</MedlineTA>", xml_text)
                if ta_match:
                    medline_ta = ta_match.group(1)

                if is_currently_indexed:
                    return NLMResult(
                        status=MedlineStatus.CURRENTLY_INDEXED,
                        nlm_id=nlm_id,
                        medline_ta=medline_ta,
                        indexing_status="Currently indexed for MEDLINE",
                    )

                # Found in catalog but not currently indexed
                # Check if it was previously indexed or just in PMC
                if "<IndexingSourceName>PubMed" in xml_text:
                    return NLMResult(
                        status=MedlineStatus.PMC_ONLY,
                        nlm_id=nlm_id,
                        medline_ta=medline_ta,
                        indexing_status="In PubMed but not MEDLINE indexed",
                    )

                return None

    async def _check_pmc(self, issn: str) -> Optional[NLMResult]:
        """Check if journal is in PMC (PubMed Central)."""
        # PMC journal list can be checked via the journals API
        # For now, we'll use a simplified search
        params = {
            "db": "pmc",
            "term": f"{issn}[ISSN]",
            "retmode": "json",
            "retmax": "1",
        }
        if self._api_key:
            params["api_key"] = self._api_key

        url = f"{self.ESEARCH_URL}?{urlencode(params)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                count = int(data.get("esearchresult", {}).get("count", 0))

                if count > 0:
                    # Found in PMC but not in MEDLINE
                    return NLMResult(
                        status=MedlineStatus.PMC_ONLY,
                        indexing_status="In PMC archive but not MEDLINE indexed",
                    )

                return None

    async def check_batch(
        self,
        issns: list[str],
        max_concurrent: int = 3,
    ) -> dict[str, NLMResult]:
        """
        Check multiple ISSNs concurrently.

        Args:
            issns: List of ISSNs to check
            max_concurrent: Maximum concurrent requests

        Returns:
            Dict mapping ISSN -> NLMResult
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def check_with_limit(issn: str) -> tuple[str, NLMResult]:
            async with semaphore:
                result = await self.check_medline_status(issn)
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
                return issn, result

        tasks = [check_with_limit(issn) for issn in issns]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for item in results:
            if isinstance(item, Exception):
                logger.error(f"Error in batch check: {item}")
                continue
            issn, result = item
            output[issn] = result

        return output


# Global service instance
_nlm_instance: Optional[NLMService] = None


def get_nlm_service() -> NLMService:
    """Get the global NLM service instance."""
    global _nlm_instance
    if _nlm_instance is None:
        _nlm_instance = NLMService()
    return _nlm_instance


def reset_nlm_service() -> None:
    """Reset the global NLM service instance (for testing)."""
    global _nlm_instance
    _nlm_instance = None
