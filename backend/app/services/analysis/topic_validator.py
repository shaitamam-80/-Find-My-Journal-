"""
Topic Relevance Validator

Validates that journal topics are actually relevant to the search.
Filters out journals that appear in results but have irrelevant topics.
"""

from typing import List, Dict, Set, Optional


class TopicRelevanceValidator:
    """Validates topic relevance for search results."""

    # Topics that are too generic and should be weighted lower
    GENERIC_TOPICS = {
        "clinical research",
        "medical research",
        "health sciences",
        "biomedical research",
        "general medicine",
        "clinical medicine",
        "medical science",
        "health care",
        "healthcare",
    }

    # Topics that are clearly unrelated to certain disciplines
    # Format: {topic_pattern: [excluded_disciplines]}
    UNRELATED_TOPIC_PATTERNS: Dict[str, List[str]] = {
        "covid": ["urology", "gynecology", "rheumatology", "dermatology", "ophthalmology"],
        "coronavirus": ["urology", "gynecology", "rheumatology", "dermatology", "ophthalmology"],
        "sars-cov": ["urology", "gynecology", "rheumatology", "dermatology", "ophthalmology"],
        "cardiac": ["urology", "ophthalmology", "dermatology"],
        "heart": ["urology", "ophthalmology", "dermatology"],
        "ophthalmology": ["urology", "gynecology", "rheumatology", "cardiology", "gastroenterology"],
        "eye": ["urology", "gynecology", "rheumatology", "cardiology", "gastroenterology"],
        "dental": ["urology", "gynecology", "rheumatology", "cardiology", "neurology"],
        "oral health": ["urology", "gynecology", "rheumatology", "cardiology", "neurology"],
        "veterinary": ["urology", "gynecology", "rheumatology", "cardiology", "oncology"],
        "animal": ["urology", "gynecology", "rheumatology", "cardiology", "oncology"],
        "pediatric": ["geriatrics"],
        "geriatric": ["pediatrics"],
        "neonatal": ["geriatrics"],
    }

    def validate_journal_topics(
        self,
        journal: Dict,
        detected_disciplines: List[Dict],
        keywords: List[str],
    ) -> Dict:
        """
        Validate that a journal's topics are relevant.

        Args:
            journal: Journal data with topics.
            detected_disciplines: List of detected disciplines.
            keywords: Search keywords.

        Returns:
            {
                "is_relevant": bool,
                "relevance_score": float,  # 0-1
                "relevant_topics": List[str],
                "irrelevant_topics": List[str],
                "warning": Optional[str],
            }
        """
        # Get journal topics (handle both dict and list formats)
        journal_topics = journal.get("topics", [])
        if isinstance(journal_topics, list) and len(journal_topics) > 0:
            if isinstance(journal_topics[0], dict):
                topic_names = [t.get("display_name", "").lower() for t in journal_topics[:10]]
            else:
                topic_names = [str(t).lower() for t in journal_topics[:10]]
        else:
            topic_names = []

        # Build expected keyword set
        expected_keywords: Set[str] = set()
        discipline_names: Set[str] = set()

        for disc in detected_disciplines:
            evidence = disc.get("evidence", [])
            expected_keywords.update(e.lower() for e in evidence)
            disc_name = disc.get("name", "")
            if disc_name:
                discipline_names.add(disc_name.lower())

        expected_keywords.update(kw.lower() for kw in keywords)

        relevant_topics: List[str] = []
        irrelevant_topics: List[str] = []

        for topic in topic_names:
            is_relevant = False
            is_irrelevant = False

            # Skip generic topics
            if topic in self.GENERIC_TOPICS:
                continue

            # Check if topic contains any expected keyword
            for kw in expected_keywords:
                if kw in topic or topic in kw:
                    is_relevant = True
                    break

            # Check for known unrelated patterns
            if not is_relevant:
                for pattern, excluded_disciplines in self.UNRELATED_TOPIC_PATTERNS.items():
                    if pattern in topic:
                        # Check if any detected discipline is in the excluded list
                        if any(disc in excluded_disciplines for disc in discipline_names):
                            is_irrelevant = True
                            break

            if is_relevant:
                relevant_topics.append(topic)
            elif is_irrelevant:
                irrelevant_topics.append(topic)
            # Topics that are neither relevant nor clearly irrelevant are neutral

        # Calculate relevance score
        total_meaningful_topics = len(relevant_topics) + len(irrelevant_topics)
        if total_meaningful_topics > 0:
            relevance_score = len(relevant_topics) / total_meaningful_topics
        elif len(topic_names) > 0:
            # No meaningful topics found - neutral score
            relevance_score = 0.5
        else:
            # No topics at all - neutral score
            relevance_score = 0.5

        # Determine if journal should be included
        # Include if any relevant topics found OR no clearly irrelevant topics
        is_relevant = len(relevant_topics) >= 1 or len(irrelevant_topics) == 0

        # Generate warning if needed
        warning: Optional[str] = None
        if relevance_score < 0.3 and is_relevant and len(irrelevant_topics) > 0:
            top_irrelevant = ", ".join(irrelevant_topics[:3])
            warning = f"Low topic relevance ({relevance_score:.0%}). Main topics: {top_irrelevant}"

        return {
            "is_relevant": is_relevant,
            "relevance_score": round(relevance_score, 2),
            "relevant_topics": relevant_topics,
            "irrelevant_topics": irrelevant_topics,
            "warning": warning,
        }

    def filter_journals(
        self,
        journals: List[Dict],
        detected_disciplines: List[Dict],
        keywords: List[str],
        min_relevance: float = 0.1,
    ) -> List[Dict]:
        """
        Filter out journals with irrelevant topics.

        Args:
            journals: List of journal results.
            detected_disciplines: Detected disciplines.
            keywords: Search keywords.
            min_relevance: Minimum topic relevance score to include.

        Returns:
            Filtered list of journals with topic_validation added.
        """
        filtered: List[Dict] = []

        for journal in journals:
            validation = self.validate_journal_topics(
                journal,
                detected_disciplines,
                keywords
            )

            # Include if relevant and meets minimum score
            if validation["is_relevant"] and validation["relevance_score"] >= min_relevance:
                journal["topic_validation"] = validation
                filtered.append(journal)

        return filtered

    def add_validation_to_journals(
        self,
        journals: List[Dict],
        detected_disciplines: List[Dict],
        keywords: List[str],
    ) -> List[Dict]:
        """
        Add topic validation info to journals without filtering.

        Useful when you want to show warnings but not remove journals.

        Args:
            journals: List of journal results.
            detected_disciplines: Detected disciplines.
            keywords: Search keywords.

        Returns:
            Journals with topic_validation field added.
        """
        for journal in journals:
            validation = self.validate_journal_topics(
                journal,
                detected_disciplines,
                keywords
            )
            journal["topic_validation"] = validation

        return journals


# Convenience function for quick validation
def validate_topics(
    journal: Dict,
    detected_disciplines: List[Dict],
    keywords: List[str],
) -> Dict:
    """
    Quick function to validate journal topic relevance.

    Args:
        journal: Journal data with topics.
        detected_disciplines: Detected disciplines.
        keywords: Search keywords.

    Returns:
        Validation result dictionary.
    """
    validator = TopicRelevanceValidator()
    return validator.validate_journal_topics(journal, detected_disciplines, keywords)
