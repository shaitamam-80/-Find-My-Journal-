"""
Trust & Safety Engine for Journal Verification.

This module provides verification services for detecting:
- Predatory/unreliable journals (via blacklists)
- Verified quality journals (via MEDLINE, DOAJ)
- Behavioral red flags (volume spikes, low impact)

Usage:
    from app.services.trust_safety import verify_journal, verify_journals_batch

    # Single journal
    status = await verify_journal(journal)

    # Batch (concurrent)
    journals = await verify_journals_batch(journals)
"""

from .service import (
    verify_journal,
    verify_journals_batch,
    get_verification_status,
)

from .blacklist import BlacklistService
from .nlm_service import NLMService
from .issn_validator import validate_issn_format, validate_issn_checksum
from .heuristics import check_volume_spike, check_impact_ratio, aggregate_flags
from .cache import VerificationCache

__all__ = [
    # Main service functions
    "verify_journal",
    "verify_journals_batch",
    "get_verification_status",
    # Individual services
    "BlacklistService",
    "NLMService",
    "VerificationCache",
    # Utilities
    "validate_issn_format",
    "validate_issn_checksum",
    "check_volume_spike",
    "check_impact_ratio",
    "aggregate_flags",
]
