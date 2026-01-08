"""
OpenAlex Constants and Domain Knowledge

Contains:
- RELEVANT_TOPIC_KEYWORDS: Keywords for soft-boosting by discipline
- Core journals loading functionality

Note: Discipline detection now uses OpenAlex's ML classification directly.
The hardcoded DISCIPLINE_KEYWORDS and KEY_JOURNALS_BY_DISCIPLINE have been removed.
"""
import json
from pathlib import Path
from typing import Dict, List, Set

from app.core.logging import get_logger

logger = get_logger(__name__)


# Topics that indicate relevance for filtering (lowercase)
# Used for soft-boosting, not hard filtering
RELEVANT_TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "developmental_psychology": [
        "developmental",
        "child",
        "infant",
        "toddler",
        "adolescent",
        "emotional development",
        "social development",
        "empathy",
        "kindness",
        "prosocial",
        "emotion regulation",
        "attachment",
        "parenting",
    ],
    "psychology": [
        "psychology",
        "child",
        "infant",
        "development",
        "emotion",
        "cognitive",
        "social",
        "mental",
    ],
    "medicine": [
        "medicine",
        "medical",
        "clinical",
        "health",
        "disease",
        "therapy",
        "diagnosis",
        "patient",
        "treatment",
        "surgery",
        "cardiology",
        "neurology",
        "oncology",
        "gastroenterology",
        "urology",
        "rheumatology",
        "epidemiology",
        "pharmacology",
        "pathology",
        "radiology",
        "internal medicine",
        "general practice",
        "vaccine",
    ],
    "computer_science": [
        "computer",
        "machine learning",
        "artificial intelligence",
        "software",
        "neural",
        "deep learning",
    ],
    "biology": [
        "biology",
        "molecular",
        "cell",
        "gene",
        "organism",
        "genetic",
        "crispr",
        "biotechnology",
    ],
    "physics": [
        "physics",
        "quantum",
        "particle",
        "optics",
        "condensed matter",
        "superconductor",
        "qubit",
    ],
    "chemistry": [
        "chemistry",
        "chemical",
        "catalyst",
        "synthesis",
        "electrochemical",
        "molecular",
        "compound",
    ],
    "economics": [
        "economics",
        "economic",
        "market",
        "financial",
        "monetary",
        "fiscal",
        "trade",
    ],
    "engineering": [
        "engineering",
        "structural",
        "civil",
        "mechanical",
        "construction",
        "seismic",
    ],
    "law": [
        "law",
        "legal",
        "court",
        "judicial",
        "statute",
        "rights",
        "constitutional",
    ],
    "literature": [
        "literature",
        "literary",
        "fiction",
        "novel",
        "postcolonial",
        "narrative",
        "poetry",
    ],
    "environmental_science": [
        "environmental",
        "climate",
        "ecology",
        "sustainability",
        "pollution",
        "carbon",
    ],
}


def load_core_journals() -> Set[str]:
    """
    Load core journals list from JSON file.

    Returns:
        Set of normalized journal names for boosting.
    """
    core_journals: Set[str] = set()

    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "core_journals.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for discipline in data.get("disciplines", []):
                    for journal in discipline.get("journals", []):
                        name = journal.get("title", "")
                        # Normalize: lowercase, alphanumeric only
                        normalized = "".join(
                            c.lower() for c in name if c.isalnum() or c.isspace()
                        )
                        core_journals.add(" ".join(normalized.split()))
            logger.info(f"Loaded {len(core_journals)} core journals for boosting.")
    except Exception as e:
        logger.warning(f"Failed to load core journals: {e}")

    return core_journals
