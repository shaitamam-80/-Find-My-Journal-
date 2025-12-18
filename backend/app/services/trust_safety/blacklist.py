"""
Blacklist Service for Predatory Journal Detection.

Uses community-maintained watchlists to identify potentially predatory journals.

Data Sources:
- Stop Predatory Journals (https://github.com/stop-predatory-journals)
- Local watchlist additions

IMPORTANT: This service uses factual language only.
We never call journals "predatory" or "scam" directly.
Instead: "Appears on community watchlists"
"""

import csv
import logging
from pathlib import Path
from typing import Optional, Set, Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BlacklistEntry:
    """A single blacklist entry."""
    issn: Optional[str]
    name: str
    publisher: Optional[str]
    source: str  # Which watchlist this came from
    date_added: Optional[str] = None
    url: Optional[str] = None  # Journal website URL (from SPJ format)
    abbreviation: Optional[str] = None  # Journal abbreviation (from SPJ format)


class BlacklistService:
    """
    Service for checking journals against known watchlists.

    Usage:
        service = BlacklistService()
        service.load_from_csv("path/to/predatory_journals.csv")

        if service.is_blacklisted(issn="1234-5678"):
            # Journal appears on watchlists

        if service.is_blacklisted_publisher("Predatory Publisher Inc"):
            # Publisher appears on watchlists
    """

    def __init__(self):
        """Initialize empty blacklist service."""
        self._issn_set: Set[str] = set()
        self._name_set: Set[str] = set()
        self._publisher_set: Set[str] = set()
        self._entries: List[BlacklistEntry] = []
        self._loaded_files: List[str] = []

    def load_from_csv(
        self,
        filepath: str,
        source_name: str = "csv",
    ) -> int:
        """
        Load blacklist entries from CSV file.

        Supported CSV formats:
        1. Standard: issn,name,publisher,date_added
        2. Stop Predatory Journals: url,name,abbr

        Args:
            filepath: Path to CSV file
            source_name: Name of the source for attribution

        Returns:
            Number of entries loaded
        """
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Blacklist file not found: {filepath}")
            return 0

        count = 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Support both CSV formats
                    name = row.get("name", "").strip()
                    if not name:
                        continue  # Skip empty entries

                    # Standard format: issn,name,publisher,date_added
                    # SPJ format: url,name,abbr
                    entry = BlacklistEntry(
                        issn=row.get("issn", "").strip() or None,
                        name=name,
                        publisher=row.get("publisher", "").strip() or None,
                        source=source_name,
                        date_added=row.get("date_added", "").strip() or None,
                        url=row.get("url", "").strip() or None,  # SPJ format
                        abbreviation=row.get("abbr", "").strip() or None,  # SPJ format
                    )
                    self._add_entry(entry)
                    count += 1

            self._loaded_files.append(filepath)
            logger.info(f"Loaded {count} entries from {filepath}")

        except Exception as e:
            logger.error(f"Error loading blacklist from {filepath}: {e}")

        return count

    def _add_entry(self, entry: BlacklistEntry) -> None:
        """Add a single entry to the blacklist."""
        self._entries.append(entry)

        if entry.issn:
            # Normalize ISSN (uppercase, with hyphen)
            issn = entry.issn.upper().strip()
            if "-" not in issn and len(issn) == 8:
                issn = f"{issn[:4]}-{issn[4:]}"
            self._issn_set.add(issn)

        if entry.name:
            # Normalize name (lowercase, strip whitespace)
            self._name_set.add(entry.name.lower().strip())

        if entry.publisher:
            # Normalize publisher (lowercase, strip whitespace)
            self._publisher_set.add(entry.publisher.lower().strip())

    def is_blacklisted(
        self,
        issn: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """
        Check if a journal appears on any watchlist.

        Args:
            issn: Journal ISSN
            name: Journal name

        Returns:
            True if journal appears on watchlist
        """
        if issn:
            issn_normalized = issn.upper().strip()
            if "-" not in issn_normalized and len(issn_normalized) == 8:
                issn_normalized = f"{issn_normalized[:4]}-{issn_normalized[4:]}"
            if issn_normalized in self._issn_set:
                return True

        if name:
            if name.lower().strip() in self._name_set:
                return True

        return False

    def is_blacklisted_publisher(self, publisher: Optional[str]) -> bool:
        """
        Check if a publisher appears on any watchlist.

        Args:
            publisher: Publisher name

        Returns:
            True if publisher appears on watchlist
        """
        if not publisher:
            return False

        return publisher.lower().strip() in self._publisher_set

    def get_blacklist_reason(
        self,
        issn: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get the reason/source for blacklisting.

        Args:
            issn: Journal ISSN
            name: Journal name

        Returns:
            Reason string or None if not blacklisted
        """
        # Normalize inputs
        issn_normalized = None
        if issn:
            issn_normalized = issn.upper().strip()
            if "-" not in issn_normalized and len(issn_normalized) == 8:
                issn_normalized = f"{issn_normalized[:4]}-{issn_normalized[4:]}"

        name_normalized = name.lower().strip() if name else None

        # Search for matching entry
        for entry in self._entries:
            if issn_normalized and entry.issn:
                entry_issn = entry.issn.upper().strip()
                if "-" not in entry_issn and len(entry_issn) == 8:
                    entry_issn = f"{entry_issn[:4]}-{entry_issn[4:]}"
                if entry_issn == issn_normalized:
                    return f"Appears on community watchlist ({entry.source})"

            if name_normalized and entry.name:
                if entry.name.lower().strip() == name_normalized:
                    return f"Appears on community watchlist ({entry.source})"

        return None

    def size(self) -> int:
        """Get total number of unique entries."""
        return len(self._entries)

    def stats(self) -> Dict[str, int]:
        """Get blacklist statistics."""
        return {
            "total_entries": len(self._entries),
            "unique_issns": len(self._issn_set),
            "unique_names": len(self._name_set),
            "unique_publishers": len(self._publisher_set),
            "loaded_files": len(self._loaded_files),
        }


# Global service instance
_blacklist_instance: Optional[BlacklistService] = None


def get_blacklist_service() -> BlacklistService:
    """
    Get the global blacklist service instance.

    Automatically loads default blacklist files on first access.
    """
    global _blacklist_instance
    if _blacklist_instance is None:
        _blacklist_instance = BlacklistService()
        _load_default_blacklists(_blacklist_instance)
    return _blacklist_instance


def _load_default_blacklists(service: BlacklistService) -> None:
    """Load default blacklist files."""
    # Look for blacklist files in the data directory
    data_dir = Path(__file__).parent.parent.parent / "data"

    # Try to load predatory_journals.csv (standard format)
    predatory_csv = data_dir / "predatory_journals.csv"
    if predatory_csv.exists():
        service.load_from_csv(str(predatory_csv), "Stop Predatory Journals")
        return

    # Also try predatory_journals_raw.csv (SPJ format: url,name,abbr)
    predatory_raw_csv = data_dir / "predatory_journals_raw.csv"
    if predatory_raw_csv.exists():
        service.load_from_csv(str(predatory_raw_csv), "Stop Predatory Journals")
        return

    logger.info(
        f"No predatory_journals.csv or predatory_journals_raw.csv found at {data_dir}. "
        "Download from https://github.com/stop-predatory-journals"
    )


def reset_blacklist_service() -> None:
    """Reset the global blacklist instance (for testing)."""
    global _blacklist_instance
    _blacklist_instance = None
