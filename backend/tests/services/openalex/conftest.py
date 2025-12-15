"""
Shared test fixtures for OpenAlex tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Set


@pytest.fixture
def mock_pyalex_sources():
    """Mock pyalex.Sources for unit tests."""
    with patch("pyalex.Sources") as mock:
        yield mock


@pytest.fixture
def mock_pyalex_works():
    """Mock pyalex.Works for unit tests."""
    with patch("pyalex.Works") as mock:
        yield mock


@pytest.fixture
def sample_journal_data() -> Dict[str, Any]:
    """Sample journal response data from OpenAlex API."""
    return {
        "id": "https://openalex.org/J137773608",
        "display_name": "Nature",
        "issn_l": "0028-0836",
        "issn": ["0028-0836", "1476-4687"],
        "publisher": "Springer Nature",
        "host_organization_name": "Springer Nature",
        "homepage_url": "https://www.nature.com/nature/",
        "works_count": 423847,
        "cited_by_count": 34567890,
        "is_oa": False,
        "is_in_doaj": False,
        "type": "journal",
        "apc_usd": 11690,
        "topics": [
            {"display_name": "Multidisciplinary Science"},
            {"display_name": "Biology"},
        ],
        "summary_stats": {
            "h_index": 1234,
            "i10_index": 56789,
            "2yr_mean_citedness": 45.67,
        },
    }


@pytest.fixture
def sample_work_data() -> Dict[str, Any]:
    """Sample work (paper) response data from OpenAlex API."""
    return {
        "id": "https://openalex.org/W123456789",
        "title": "Sample Research Paper",
        "publication_date": "2023-01-15",
        "primary_location": {
            "source": {
                "id": "https://openalex.org/J137773608",
                "display_name": "Nature",
                "type": "journal",
            },
            "is_oa": False,
        },
        "topics": [
            {"id": "https://openalex.org/T1", "display_name": "Biology", "score": 0.9},
            {"id": "https://openalex.org/T2", "display_name": "Genetics", "score": 0.7},
        ],
    }


@pytest.fixture
def sample_core_journals() -> Set[str]:
    """Sample set of normalized core journal names."""
    return {
        "nature",
        "science",
        "cell",
        "the lancet",
        "new england journal of medicine",
        "jama",
        "physical review letters",
        "nature medicine",
    }


@pytest.fixture
def invalid_issns():
    """Collection of invalid ISSNs for testing validation."""
    return [
        "",
        "invalid",
        "1234-56789",  # Too long
        "123-4567",  # Too short
        "ABCD-EFGH",  # Letters
        None,
    ]


@pytest.fixture
def valid_issns():
    """Collection of valid ISSNs for testing."""
    return [
        "0028-0836",  # Nature
        "1234-567X",  # With X check digit
        "0000-0000",  # Edge case
    ]
