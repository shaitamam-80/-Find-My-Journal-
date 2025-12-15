"""
DEPRECATED: Import from app.services.openalex instead

This file exists for backward compatibility only and will be
removed in a future version.

Migration Guide:
    # Old (deprecated):
    from app.services.openalex_service import openalex_service
    from app.services.openalex_service import OpenAlexService

    # New (recommended):
    from app.services.openalex import openalex_service
    from app.services.openalex import OpenAlexService

    # Or use functions directly:
    from app.services.openalex import search_journals_by_text
"""
import warnings

# Emit deprecation warning on import
warnings.warn(
    "Importing from openalex_service is deprecated. "
    "Import from app.services.openalex instead. "
    "Example: from app.services.openalex import openalex_service",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
from .openalex import *  # noqa: F401, F403
from .openalex import openalex_service, OpenAlexService  # noqa: F401

# Also export the constants that were in the original file
from .openalex.constants import RELEVANT_TOPIC_KEYWORDS  # noqa: F401
