"""
Main Trust & Safety Verification Service.

Orchestrates all verification checks and returns unified status.

Verification Flow:
1. Check cache for existing result
2. Check blacklist (fast fail)
3. Check MEDLINE status (highest trust)
4. Check DOAJ (from OpenAlex data)
5. Run heuristics (volume spike, impact ratio)
6. Aggregate results and cache

IMPORTANT: Uses factual, non-defamatory language throughout.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from app.models.journal import (
    Journal,
    JournalMetrics,
    BadgeColor,
    VerificationSource,
    VerificationStatus,
    VerificationFlag,
)
from app.core.config import get_settings

from .cache import get_cache, VerificationCache
from .blacklist import get_blacklist_service, BlacklistService
from .nlm_service import get_nlm_service, NLMService, MedlineStatus
from .heuristics import run_all_heuristics, aggregate_flags
from .issn_validator import validate_issn_format

logger = logging.getLogger(__name__)


async def verify_journal(journal: Journal) -> Journal:
    """
    Verify a single journal and attach verification status.

    Args:
        journal: Journal object to verify

    Returns:
        Journal with verification field populated
    """
    settings = get_settings()

    # Check if verification is enabled
    if not settings.trust_safety_enabled:
        return journal

    # Get verification status
    status = await get_verification_status(
        issn=journal.issn or journal.issn_l,
        name=journal.name,
        publisher=journal.publisher,
        is_in_doaj=journal.is_in_doaj,
        metrics=journal.metrics,
    )

    journal.verification = status
    return journal


async def verify_journals_batch(
    journals: List[Journal],
    max_concurrent: int = 5,
) -> List[Journal]:
    """
    Verify multiple journals concurrently.

    Uses semaphore to limit concurrent API calls and respect rate limits.

    Args:
        journals: List of journals to verify
        max_concurrent: Maximum concurrent verifications

    Returns:
        List of journals with verification status populated
    """
    settings = get_settings()

    # Check if verification is enabled
    if not settings.trust_safety_enabled:
        return journals

    semaphore = asyncio.Semaphore(max_concurrent)

    async def verify_with_limit(journal: Journal) -> Journal:
        async with semaphore:
            return await verify_journal(journal)

    tasks = [verify_with_limit(j) for j in journals]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions
    verified_journals = []
    for journal, result in zip(journals, results):
        if isinstance(result, Exception):
            logger.error(f"Error verifying journal {journal.name}: {result}")
            # Return journal without verification on error
            verified_journals.append(journal)
        else:
            verified_journals.append(result)

    return verified_journals


async def get_verification_status(
    issn: Optional[str] = None,
    name: Optional[str] = None,
    publisher: Optional[str] = None,
    is_in_doaj: bool = False,
    metrics: Optional[JournalMetrics] = None,
) -> VerificationStatus:
    """
    Get verification status for a journal.

    This is the main entry point for verification logic.

    Args:
        issn: Journal ISSN
        name: Journal name
        publisher: Publisher name
        is_in_doaj: Whether journal is in DOAJ (from OpenAlex)
        metrics: Journal metrics for heuristic analysis

    Returns:
        VerificationStatus with badge color and reasons
    """
    cache = get_cache()
    blacklist = get_blacklist_service()
    nlm = get_nlm_service()

    sources_checked: List[VerificationSource] = []
    flags: List[VerificationFlag] = []

    # Generate cache key
    cache_key = issn or name or "unknown"

    # Step 0: Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Step 1: Blacklist check (fast fail)
    sources_checked.append(VerificationSource.BLACKLIST)

    if blacklist.is_blacklisted(issn=issn, name=name):
        reason = blacklist.get_blacklist_reason(issn=issn, name=name)
        status = VerificationStatus(
            badge_color=BadgeColor.RED,
            status_text="Publication Risk Detected",
            reasons=[reason or "Appears on community watchlists"],
            flags=[VerificationFlag(
                source=VerificationSource.BLACKLIST,
                reason=reason or "Appears on community watchlists",
                severity="critical",
            )],
            sources_checked=sources_checked,
        )
        cache.set(cache_key, status)
        return status

    if blacklist.is_blacklisted_publisher(publisher):
        status = VerificationStatus(
            badge_color=BadgeColor.YELLOW,
            status_text="Exercise Caution",
            subtitle="Publisher flagged",
            reasons=["Publisher appears on community watchlists"],
            flags=[VerificationFlag(
                source=VerificationSource.BLACKLIST,
                reason="Publisher appears on community watchlists",
                severity="medium",
            )],
            sources_checked=sources_checked,
        )
        cache.set(cache_key, status)
        return status

    # Step 2: MEDLINE check (highest trust)
    if issn and validate_issn_format(issn):
        sources_checked.append(VerificationSource.MEDLINE)

        nlm_result = await nlm.check_medline_status(issn)

        if nlm_result.status == MedlineStatus.CURRENTLY_INDEXED:
            status = VerificationStatus(
                badge_color=BadgeColor.GREEN,
                status_text="Verified Source",
                subtitle="MEDLINE",
                reasons=["Currently indexed in MEDLINE"],
                sources_checked=sources_checked,
                verified_by=VerificationSource.MEDLINE,
            )
            cache.set(cache_key, status)
            return status

        if nlm_result.status == MedlineStatus.PMC_ONLY:
            # PMC-only is a yellow flag, but continue checking
            sources_checked.append(VerificationSource.PMC)
            flags.append(VerificationFlag(
                source=VerificationSource.PMC,
                reason="In PubMed Central archive but not MEDLINE indexed",
                severity="low",
            ))

    # Step 3: DOAJ check (from OpenAlex data)
    sources_checked.append(VerificationSource.DOAJ)

    if is_in_doaj:
        # If no red flags from PMC check, DOAJ gives green
        if not flags:
            status = VerificationStatus(
                badge_color=BadgeColor.GREEN,
                status_text="Verified Source",
                subtitle="DOAJ",
                reasons=["Listed in Directory of Open Access Journals"],
                sources_checked=sources_checked,
                verified_by=VerificationSource.DOAJ,
            )
            cache.set(cache_key, status)
            return status
        else:
            # DOAJ + PMC only = still green, but note PMC status
            status = VerificationStatus(
                badge_color=BadgeColor.GREEN,
                status_text="Verified Source",
                subtitle="DOAJ",
                reasons=[
                    "Listed in Directory of Open Access Journals",
                    "Note: Not currently indexed in MEDLINE",
                ],
                flags=flags,
                sources_checked=sources_checked,
                verified_by=VerificationSource.DOAJ,
            )
            cache.set(cache_key, status)
            return status

    # Step 4: Heuristic analysis
    sources_checked.append(VerificationSource.HEURISTIC)

    if metrics:
        heuristic_flags = run_all_heuristics(metrics)
        flags.extend(heuristic_flags)

    # Step 5: Aggregate results
    if flags:
        badge_color, status_text = aggregate_flags(flags)
        reasons = [f.reason for f in flags]

        status = VerificationStatus(
            badge_color=badge_color,
            status_text=status_text,
            reasons=reasons,
            flags=flags,
            sources_checked=sources_checked,
        )
    else:
        # No verification data available
        status = VerificationStatus(
            badge_color=BadgeColor.GRAY,
            status_text="Unverified Source",
            reasons=["Not found in major indexing databases"],
            sources_checked=sources_checked,
        )

    cache.set(cache_key, status)
    return status


def create_verified_status(
    source: VerificationSource,
    subtitle: str,
    reason: str,
) -> VerificationStatus:
    """Helper to create a verified (green) status."""
    return VerificationStatus(
        badge_color=BadgeColor.GREEN,
        status_text="Verified Source",
        subtitle=subtitle,
        reasons=[reason],
        verified_by=source,
        checked_at=datetime.now(),
    )


def create_warning_status(
    reasons: List[str],
    flags: List[VerificationFlag],
) -> VerificationStatus:
    """Helper to create a warning (yellow/red) status."""
    badge_color, status_text = aggregate_flags(flags)
    return VerificationStatus(
        badge_color=badge_color,
        status_text=status_text,
        reasons=reasons,
        flags=flags,
        checked_at=datetime.now(),
    )
