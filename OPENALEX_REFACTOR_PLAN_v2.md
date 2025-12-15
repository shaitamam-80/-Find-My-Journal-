# 🔧 OpenAlex Service Refactoring Plan v2.0
## God File → Clean Architecture
## Project: Find-My-Journal

---

<role>
You are a Senior Python Architect specializing in code refactoring and 
clean architecture. You have extensive experience breaking down monolithic 
services into well-organized, maintainable modules following SOLID principles.
</role>

<context>
<current_state>
File: backend/app/services/openalex_service.py
Size: 1,230 lines (God File / monolith)
Purpose: Service layer for OpenAlex API integration
Stack: Python 3.11+, FastAPI, Pydantic, httpx/requests
Project: Find-My-Journal
</current_state>

<target_state>
- 7-9 separate Python modules
- ~150-250 lines per file maximum
- Clear separation of concerns (Single Responsibility)
- Maintained backward compatibility (existing imports should work)
- Proper logging (already implemented in Phase 2)
- Type hints on all public functions
- Full unit test coverage
</target_state>

<project_agents>
Available agents for parallel execution:
- backend-agent: Primary executor for this refactoring
- qa-agent: Testing and validation
- docs-agent: Documentation updates
</project_agents>
</context>

<constraints>
- Preserve all existing function signatures (no breaking changes)
- Group by domain/responsibility, not by technical type
- Consider circular import risks and propose solutions
- Include type hints preservation strategy
- Estimate lines per new file
- Include caching strategy if exists in original
- Realistic time estimates with buffer
</constraints>

---

# 📊 TIME ESTIMATES (REALISTIC)

| Phase | Duration | Parallel? | Notes |
|-------|----------|-----------|-------|
| Phase 0: Analysis | 45 min | No | Must complete first |
| Phase 1: Structure | 15 min | No | Quick setup |
| Phase 2: Foundation | 75 min | Yes (partial) | exceptions→models→config→utils |
| Phase 3: Core Modules | 90 min | Yes | client, cache can parallel |
| Phase 4: Domain | 90 min | Yes | journals ∥ search |
| Phase 5: Backward Compat | 30 min | No | Requires Phase 4 |
| Phase 6: Testing | 75 min | Yes | Per module |
| Phase 7: Documentation | 30 min | Yes | docs-agent |
|---------|----------|-----------|-------|
| **Total (Sequential)** | **7.5 hrs** | | |
| **Total (Parallel)** | **4-5 hrs** | | With agents |

---

# 🚀 EXECUTION COMMAND

```bash
# Create branch first
git checkout -b refactor/openalex-service

# Option 1: Full execution with orchestrator
claude orchestrator "Execute OPENALEX_REFACTOR_PLAN_v2.md all phases"

# Option 2: Phase by phase
claude backend-agent "Execute OPENALEX_REFACTOR_PLAN_v2.md Phase 0"
claude backend-agent "Execute OPENALEX_REFACTOR_PLAN_v2.md Phase 1-5"
claude qa-agent "Execute OPENALEX_REFACTOR_PLAN_v2.md Phase 6"
claude docs-agent "Execute OPENALEX_REFACTOR_PLAN_v2.md Phase 7"
```

---

# PHASE 0: Pre-Refactoring Analysis
## Agent: backend-agent
## Time: 45 min
## Parallel: No (must complete first)

<task>
Before any code changes, perform deep analysis of openalex_service.py.
This phase is CRITICAL - do not skip or rush.
</task>

```yaml
task: "Analyze openalex_service.py structure"
priority: CRITICAL
estimated_time: 45 min

actions:
  1. Generate function/class inventory:
     ```bash
     # List all functions and classes with line numbers
     grep -n "^def \|^class \|^async def " backend/app/services/openalex_service.py > /tmp/openalex_inventory.txt
     cat /tmp/openalex_inventory.txt
     ```
  
  2. Count and categorize:
     ```bash
     # Count functions
     grep -c "^def \|^async def " backend/app/services/openalex_service.py
     
     # Count classes
     grep -c "^class " backend/app/services/openalex_service.py
     ```
  
  3. Identify imports and dependencies:
     ```bash
     # External imports
     grep "^import \|^from " backend/app/services/openalex_service.py | head -50
     ```
  
  4. Check for caching patterns:
     ```bash
     grep -n "cache\|@lru_cache\|redis\|TTL\|expire\|@cached" backend/app/services/openalex_service.py
     ```
  
  5. Check for configuration/constants:
     ```bash
     grep -n "^[A-Z_]* = \|BASE_URL\|API_URL\|TIMEOUT\|MAX_" backend/app/services/openalex_service.py
     ```
  
  6. Identify HTTP client usage:
     ```bash
     grep -n "httpx\|requests\|aiohttp\|fetch\|\.get(\|\.post(" backend/app/services/openalex_service.py
     ```

  7. Create dependency graph:
     - Which functions call which other functions?
     - What external imports are used where?
     - Identify shared state/constants

  8. Categorize by responsibility:
     □ API client/HTTP operations
     □ Data transformation/parsing
     □ Journal-specific logic
     □ Search operations
     □ Caching (if exists)
     □ Utilities/helpers
     □ Configuration/constants
     □ Models/schemas

output:
  Create file: OPENALEX_ANALYSIS.md
  
  Content:
  ## Function Inventory
  | Line | Name | Type | Calls | Called By | Category |
  |------|------|------|-------|-----------|----------|
  | ... | ... | ... | ... | ... | ... |
  
  ## Identified Responsibilities
  1. HTTP Client Layer (~X lines)
  2. Journal Operations (~X lines)
  3. Search Operations (~X lines)
  4. Data Transformation (~X lines)
  5. Utilities (~X lines)
  6. Configuration (~X lines)
  7. Caching (~X lines or N/A)
  
  ## Caching Decision
  - [ ] No caching exists → Skip cache.py
  - [ ] Simple @lru_cache → Keep inline
  - [ ] Complex caching → Create cache.py
  
  ## Circular Import Risks
  - Risk 1: ...
  - Risk 2: ...
  
  ## Extraction Order (dependency-safe)
  1. exceptions.py (no deps)
  2. models.py (no deps)
  3. config.py (no deps)
  4. utils.py (may use models)
  5. cache.py (uses config) - if needed
  6. client.py (uses config, exceptions)
  7. journals.py (uses client, models, utils)
  8. search.py (uses client, models, utils)
```

---

# PHASE 1: Create Module Structure
## Agent: backend-agent
## Time: 15 min
## Depends on: Phase 0

```yaml
task: "Create new openalex package structure"
priority: HIGH
estimated_time: 15 min

actions:
  1. Create directory structure:
     ```bash
     # Create package directory
     mkdir -p backend/app/services/openalex
     
     # Create all module files
     touch backend/app/services/openalex/__init__.py
     touch backend/app/services/openalex/exceptions.py
     touch backend/app/services/openalex/models.py
     touch backend/app/services/openalex/config.py
     touch backend/app/services/openalex/utils.py
     touch backend/app/services/openalex/client.py
     touch backend/app/services/openalex/journals.py
     touch backend/app/services/openalex/search.py
     
     # Create test directory
     mkdir -p backend/tests/services/openalex
     touch backend/tests/services/openalex/__init__.py
     touch backend/tests/services/openalex/conftest.py
     ```

  2. Conditional: Create cache.py if needed (based on Phase 0 analysis):
     ```bash
     # Only if caching was identified in Phase 0
     touch backend/app/services/openalex/cache.py
     ```

  3. Verify structure:
     ```bash
     tree backend/app/services/openalex/
     tree backend/tests/services/openalex/
     ```

expected_structure: |
  backend/app/services/openalex/
  ├── __init__.py      # Public API - re-exports for backward compatibility
  ├── exceptions.py    # Custom exceptions
  ├── models.py        # Pydantic models, TypedDicts, dataclasses
  ├── config.py        # Configuration with environment variables
  ├── utils.py         # Shared utilities, validators, formatters
  ├── cache.py         # Caching layer (CONDITIONAL)
  ├── client.py        # HTTP client, connection, rate limiting
  ├── journals.py      # Journal-specific operations
  └── search.py        # Search functionality
  
  backend/tests/services/openalex/
  ├── __init__.py
  └── conftest.py      # Shared test fixtures

validation:
  - All files created successfully
  - No permission errors
  - Directory structure matches expected
```

---

# PHASE 2: Extract Foundation Modules (No Dependencies)
## Agent: backend-agent
## Time: 75 min
## Depends on: Phase 1
## Parallel: exceptions → (models ∥ config) → utils

<task>
Extract modules with NO internal dependencies first.
These are "leaf nodes" in the dependency tree.
Order: exceptions → models/config (parallel) → utils
</task>

---

### Step 2.1: Extract Exceptions
```yaml
file: backend/app/services/openalex/exceptions.py
estimated_lines: 60-80
depends_on: None (leaf node)
time: 10 min

content: |
  """
  OpenAlex API Custom Exceptions
  
  This module defines all custom exceptions for OpenAlex operations.
  All exceptions inherit from OpenAlexError for easy catching.
  
  Usage:
      try:
          result = await get_journal_by_issn("invalid")
      except ISSNValidationError as e:
          print(f"Invalid ISSN: {e.issn}")
      except OpenAlexAPIError as e:
          print(f"API failed: {e.status_code}")
      except OpenAlexError as e:
          print(f"OpenAlex error: {e}")
  """
  from typing import Optional
  
  
  class OpenAlexError(Exception):
      """Base exception for all OpenAlex operations"""
      pass
  
  
  class OpenAlexAPIError(OpenAlexError):
      """
      API request failed with non-success status code
      
      Attributes:
          status_code: HTTP status code
          message: Error message from API
      """
      def __init__(self, status_code: int, message: str):
          self.status_code = status_code
          self.message = message
          super().__init__(f"API Error {status_code}: {message}")
  
  
  class OpenAlexNotFoundError(OpenAlexError):
      """
      Resource not found (HTTP 404)
      
      Attributes:
          resource: The resource identifier that was not found
      """
      def __init__(self, resource: str):
          self.resource = resource
          super().__init__(f"Resource not found: {resource}")
  
  
  class OpenAlexRateLimitError(OpenAlexError):
      """
      Rate limit exceeded (HTTP 429)
      
      Attributes:
          retry_after: Seconds to wait before retrying (if provided)
      """
      def __init__(self, retry_after: Optional[int] = None):
          self.retry_after = retry_after
          msg = "Rate limit exceeded"
          if retry_after:
              msg += f" (retry after {retry_after}s)"
          super().__init__(msg)
  
  
  class OpenAlexTimeoutError(OpenAlexError):
      """
      Request timed out
      
      Attributes:
          timeout: The timeout value that was exceeded
      """
      def __init__(self, timeout: float):
          self.timeout = timeout
          super().__init__(f"Request timed out after {timeout}s")
  
  
  class OpenAlexValidationError(OpenAlexError):
      """Base class for validation errors"""
      pass
  
  
  class ISSNValidationError(OpenAlexValidationError):
      """
      Invalid ISSN format
      
      Attributes:
          issn: The invalid ISSN value
      """
      def __init__(self, issn: str):
          self.issn = issn
          super().__init__(
              f"Invalid ISSN: '{issn}'. Expected format: XXXX-XXXX "
              f"where X is a digit (last digit can be 'X')"
          )
  
  
  class OpenAlexConnectionError(OpenAlexError):
      """Failed to connect to OpenAlex API"""
      pass

actions:
  1. Identify all exception patterns in original file:
     ```bash
     grep -n "raise \|except \|Exception\|Error" backend/app/services/openalex_service.py
     ```
  
  2. Create exceptions.py with content above
  
  3. Customize based on actual exceptions found in original

validation:
  - File syntax is valid: python -c "from app.services.openalex.exceptions import *"
  - All original exception cases covered
```

---

### Step 2.2: Extract Models
```yaml
file: backend/app/services/openalex/models.py
estimated_lines: 100-150
depends_on: None (leaf node)
time: 20 min

content: |
  """
  OpenAlex Data Models and Schemas
  
  This module defines all data structures used for OpenAlex API
  responses and internal data transfer.
  
  All models use Pydantic for validation and serialization.
  """
  from typing import Optional, List, Dict, Any
  from pydantic import BaseModel, Field
  from datetime import datetime
  
  
  class JournalInfo(BaseModel):
      """
      Journal information from OpenAlex API
      
      Represents core journal metadata.
      """
      id: str = Field(..., description="OpenAlex journal ID")
      display_name: str = Field(..., description="Journal display name")
      issn_l: Optional[str] = Field(None, description="Linking ISSN")
      issns: List[str] = Field(default_factory=list, description="All ISSNs")
      publisher: Optional[str] = Field(None, description="Publisher name")
      homepage_url: Optional[str] = Field(None, description="Journal homepage")
      works_count: Optional[int] = Field(None, description="Total works published")
      cited_by_count: Optional[int] = Field(None, description="Total citations")
      is_oa: Optional[bool] = Field(None, description="Is open access")
      is_in_doaj: Optional[bool] = Field(None, description="Listed in DOAJ")
      updated_date: Optional[datetime] = Field(None, description="Last update")
      
      class Config:
          extra = "ignore"  # Ignore extra fields from API
  
  
  class JournalMetrics(BaseModel):
      """
      Journal bibliometric metrics
      
      Contains h-index, impact metrics, and publication statistics.
      """
      h_index: Optional[int] = Field(None, description="H-index")
      i10_index: Optional[int] = Field(None, description="i10-index")
      cited_by_count: Optional[int] = Field(None, description="Total citations")
      works_count: Optional[int] = Field(None, description="Total works")
      two_year_mean_citedness: Optional[float] = Field(
          None, description="2-year mean citedness (similar to impact factor)"
      )
      
      class Config:
          extra = "ignore"
  
  
  class SearchMeta(BaseModel):
      """Metadata for search results pagination"""
      count: int = Field(..., description="Total results count")
      page: int = Field(1, description="Current page number")
      per_page: int = Field(25, description="Results per page")
      
      @property
      def total_pages(self) -> int:
          """Calculate total number of pages"""
          if self.per_page <= 0:
              return 0
          return (self.count + self.per_page - 1) // self.per_page
  
  
  class SearchResult(BaseModel):
      """
      Search result container
      
      Wraps journal results with pagination metadata.
      """
      results: List[JournalInfo] = Field(default_factory=list)
      meta: SearchMeta
      
      @property
      def count(self) -> int:
          return self.meta.count
      
      @property
      def page(self) -> int:
          return self.meta.page
      
      @property
      def per_page(self) -> int:
          return self.meta.per_page
      
      def has_next_page(self) -> bool:
          """Check if there are more pages"""
          return self.meta.page < self.meta.total_pages
  
  
  class Concept(BaseModel):
      """Academic concept/discipline"""
      id: str
      display_name: str
      level: int = Field(..., description="Concept hierarchy level (0=root)")
      score: Optional[float] = Field(None, description="Relevance score")
  
  
  class Publisher(BaseModel):
      """Publisher information"""
      id: str
      display_name: str
      country_codes: List[str] = Field(default_factory=list)
      works_count: Optional[int] = None

actions:
  1. Find all model/schema definitions in original:
     ```bash
     grep -n "class.*BaseModel\|TypedDict\|dataclass\|Dict\[str" backend/app/services/openalex_service.py
     ```
  
  2. Find type aliases:
     ```bash
     grep -n "^[A-Za-z]*Dict = \|^[A-Za-z]*Type = " backend/app/services/openalex_service.py
     ```
  
  3. Create models.py with all identified structures
  
  4. Add type hints and docstrings

validation:
  - python -c "from app.services.openalex.models import *"
  - All original model usages covered
```

---

### Step 2.3: Extract Configuration
```yaml
file: backend/app/services/openalex/config.py
estimated_lines: 50-70
depends_on: None (leaf node)
time: 15 min

content: |
  """
  OpenAlex Service Configuration
  
  Centralized configuration with environment variable support.
  Uses Pydantic Settings for validation and .env file loading.
  
  Environment Variables:
      OPENALEX_API_BASE_URL: API base URL (default: https://api.openalex.org)
      OPENALEX_TIMEOUT: Request timeout in seconds (default: 30.0)
      OPENALEX_EMAIL: Email for polite pool (optional, gives higher rate limits)
      OPENALEX_MAX_RETRIES: Max retry attempts (default: 3)
      OPENALEX_CACHE_TTL: Cache TTL in seconds (default: 3600)
  
  Usage:
      from app.services.openalex.config import get_settings
      
      settings = get_settings()
      print(settings.api_base_url)
  """
  from functools import lru_cache
  from typing import Optional
  
  from pydantic_settings import BaseSettings, SettingsConfigDict
  
  
  class OpenAlexSettings(BaseSettings):
      """
      OpenAlex API Configuration Settings
      
      All settings can be overridden via environment variables
      with OPENALEX_ prefix.
      """
      # API Configuration
      api_base_url: str = "https://api.openalex.org"
      timeout: float = 30.0
      email: Optional[str] = None  # For polite pool (higher rate limits)
      
      # Retry Configuration
      max_retries: int = 3
      retry_min_wait: float = 2.0
      retry_max_wait: float = 10.0
      
      # Cache Configuration
      cache_enabled: bool = True
      cache_ttl: int = 3600  # 1 hour
      
      # Pagination Defaults
      default_per_page: int = 25
      max_per_page: int = 200
      
      model_config = SettingsConfigDict(
          env_prefix="OPENALEX_",
          env_file=".env",
          env_file_encoding="utf-8",
          case_sensitive=False,
          extra="ignore",
      )
  
  
  @lru_cache
  def get_settings() -> OpenAlexSettings:
      """
      Get cached settings instance
      
      Settings are loaded once and cached for performance.
      To reload settings, call get_settings.cache_clear()
      
      Returns:
          OpenAlexSettings instance
      """
      return OpenAlexSettings()
  
  
  def reload_settings() -> OpenAlexSettings:
      """
      Force reload settings from environment
      
      Useful for testing or after environment changes.
      
      Returns:
          Fresh OpenAlexSettings instance
      """
      get_settings.cache_clear()
      return get_settings()

actions:
  1. Find all constants in original file:
     ```bash
     grep -n "^[A-Z_]* = " backend/app/services/openalex_service.py
     grep -n "BASE_URL\|API_URL\|TIMEOUT\|MAX_\|DEFAULT_" backend/app/services/openalex_service.py
     ```
  
  2. Move constants to config.py as settings
  
  3. Add to .env.example:
     ```bash
     echo "# OpenAlex Configuration" >> backend/.env.example
     echo "OPENALEX_EMAIL=your-email@example.com" >> backend/.env.example
     echo "OPENALEX_TIMEOUT=30.0" >> backend/.env.example
     ```

validation:
  - python -c "from app.services.openalex.config import get_settings; print(get_settings())"
  - Environment variables work correctly
```

---

### Step 2.4: Extract Utilities
```yaml
file: backend/app/services/openalex/utils.py
estimated_lines: 80-120
depends_on: models.py (may use for type hints)
time: 15 min

content: |
  """
  OpenAlex Utility Functions
  
  Shared helper functions for validation, formatting, and data processing.
  """
  import re
  import logging
  from typing import Optional, Dict, Any, List
  
  from .config import get_settings
  
  logger = logging.getLogger(__name__)
  
  # ISSN pattern: 4 digits, hyphen, 3 digits + check digit (0-9 or X)
  ISSN_PATTERN = re.compile(r"^\d{4}-\d{3}[\dX]$", re.IGNORECASE)
  
  
  def validate_issn(issn: str) -> bool:
      """
      Validate ISSN format
      
      Args:
          issn: ISSN string to validate
          
      Returns:
          True if valid format (XXXX-XXXX), False otherwise
          
      Examples:
          >>> validate_issn("0028-0836")
          True
          >>> validate_issn("1234-567X")
          True
          >>> validate_issn("invalid")
          False
      """
      if not issn or not isinstance(issn, str):
          return False
      return bool(ISSN_PATTERN.match(issn.strip().upper()))
  
  
  def normalize_issn(issn: str) -> str:
      """
      Normalize ISSN to standard format (XXXX-XXXX)
      
      Args:
          issn: ISSN in any format
          
      Returns:
          Normalized ISSN with hyphen and uppercase X
          
      Examples:
          >>> normalize_issn("00280836")
          "0028-0836"
          >>> normalize_issn("1234-567x")
          "1234-567X"
      """
      # Remove all non-alphanumeric characters
      cleaned = re.sub(r"[^0-9Xx]", "", issn)
      cleaned = cleaned.upper()
      
      # Add hyphen if missing
      if len(cleaned) == 8 and "-" not in issn:
          return f"{cleaned[:4]}-{cleaned[4:]}"
      
      # Already has hyphen, just uppercase
      if len(issn.replace("-", "")) == 8:
          return issn.upper().strip()
      
      return issn.strip()
  
  
  def build_query_params(
      page: int = 1,
      per_page: Optional[int] = None,
      search: Optional[str] = None,
      filters: Optional[Dict[str, Any]] = None,
      sort: Optional[str] = None,
  ) -> Dict[str, Any]:
      """
      Build OpenAlex API query parameters
      
      Args:
          page: Page number (1-indexed)
          per_page: Results per page (default from settings)
          search: Search query string
          filters: Filter dictionary
          sort: Sort field and direction
          
      Returns:
          Dictionary of query parameters
      """
      settings = get_settings()
      
      params: Dict[str, Any] = {
          "page": max(1, page),
          "per_page": min(
              per_page or settings.default_per_page,
              settings.max_per_page
          ),
      }
      
      if search:
          params["search"] = search.strip()
      
      if filters:
          filter_parts = []
          for key, value in filters.items():
              if isinstance(value, list):
                  filter_parts.append(f"{key}:{','.join(str(v) for v in value)}")
              else:
                  filter_parts.append(f"{key}:{value}")
          if filter_parts:
              params["filter"] = ",".join(filter_parts)
      
      if sort:
          params["sort"] = sort
      
      return params
  
  
  def parse_openalex_id(url_or_id: str) -> str:
      """
      Extract OpenAlex ID from URL or return as-is
      
      Args:
          url_or_id: Full OpenAlex URL or just the ID
          
      Returns:
          The OpenAlex ID (e.g., "J1234567")
          
      Examples:
          >>> parse_openalex_id("https://openalex.org/J1234567")
          "J1234567"
          >>> parse_openalex_id("J1234567")
          "J1234567"
      """
      if url_or_id.startswith("https://openalex.org/"):
          return url_or_id.split("/")[-1]
      return url_or_id
  
  
  def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
      """
      Safely get nested dictionary value
      
      Args:
          data: Dictionary to search
          *keys: Keys to traverse
          default: Default value if not found
          
      Returns:
          Value at nested key path or default
      """
      result = data
      for key in keys:
          if isinstance(result, dict):
              result = result.get(key)
          else:
              return default
          if result is None:
              return default
      return result

actions:
  1. Find all helper functions in original:
     ```bash
     grep -n "^def " backend/app/services/openalex_service.py | grep -v "get_\|search_\|fetch_"
     ```
  
  2. Identify validation and formatting functions
  
  3. Move to utils.py with proper docstrings

validation:
  - python -c "from app.services.openalex.utils import *"
  - Unit tests pass for validators
```

---

# PHASE 3: Extract Core Infrastructure
## Agent: backend-agent
## Time: 90 min
## Depends on: Phase 2
## Parallel: cache.py ∥ client.py (if cache exists)

---

### Step 3.1: Extract Cache Layer (CONDITIONAL)
```yaml
file: backend/app/services/openalex/cache.py
estimated_lines: 70-100
depends_on: config.py
time: 25 min
condition: Only if caching was identified in Phase 0

content: |
  """
  OpenAlex Caching Layer
  
  Provides caching decorators for API responses.
  Uses in-memory cache by default, can be extended for Redis.
  
  Usage:
      @cached(ttl=3600)
      async def get_journal(issn: str) -> JournalInfo:
          ...
  """
  import hashlib
  import json
  import time
  import logging
  from functools import wraps
  from typing import Callable, Any, Optional, TypeVar, ParamSpec
  from collections import OrderedDict
  
  from .config import get_settings
  
  logger = logging.getLogger(__name__)
  
  P = ParamSpec("P")
  T = TypeVar("T")
  
  
  class LRUCache:
      """
      Thread-safe LRU cache with TTL support
      """
      def __init__(self, maxsize: int = 1000):
          self.maxsize = maxsize
          self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
      
      def get(self, key: str) -> Optional[Any]:
          """Get value if exists and not expired"""
          if key not in self._cache:
              return None
          
          value, expires = self._cache[key]
          if time.time() > expires:
              del self._cache[key]
              return None
          
          # Move to end (most recently used)
          self._cache.move_to_end(key)
          return value
      
      def set(self, key: str, value: Any, ttl: int) -> None:
          """Set value with TTL"""
          expires = time.time() + ttl
          
          # Remove oldest if at capacity
          while len(self._cache) >= self.maxsize:
              self._cache.popitem(last=False)
          
          self._cache[key] = (value, expires)
          self._cache.move_to_end(key)
      
      def clear(self) -> None:
          """Clear all cached values"""
          self._cache.clear()
      
      def stats(self) -> dict:
          """Return cache statistics"""
          return {
              "size": len(self._cache),
              "maxsize": self.maxsize,
          }
  
  
  # Global cache instance
  _cache = LRUCache()
  
  
  def _build_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
      """Build unique cache key from function call"""
      key_data = {
          "func": func_name,
          "args": [str(a) for a in args],
          "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
      }
      key_json = json.dumps(key_data, sort_keys=True)
      return hashlib.sha256(key_json.encode()).hexdigest()[:16]
  
  
  def cached(ttl: Optional[int] = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
      """
      Cache decorator for async functions
      
      Args:
          ttl: Time-to-live in seconds (default from settings)
          
      Returns:
          Decorated function with caching
      """
      def decorator(func: Callable[P, T]) -> Callable[P, T]:
          @wraps(func)
          async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
              settings = get_settings()
              
              if not settings.cache_enabled:
                  return await func(*args, **kwargs)
              
              cache_key = _build_cache_key(func.__name__, args, kwargs)
              
              # Try cache
              cached_value = _cache.get(cache_key)
              if cached_value is not None:
                  logger.debug(f"Cache hit: {func.__name__}")
                  return cached_value
              
              # Execute and cache
              logger.debug(f"Cache miss: {func.__name__}")
              result = await func(*args, **kwargs)
              
              cache_ttl = ttl or settings.cache_ttl
              _cache.set(cache_key, result, cache_ttl)
              
              return result
          
          return wrapper
      return decorator
  
  
  def clear_cache() -> None:
      """Clear all cached data"""
      _cache.clear()
      logger.info("OpenAlex cache cleared")
  
  
  def get_cache_stats() -> dict:
      """Get cache statistics"""
      return _cache.stats()

actions:
  1. Check if caching exists in original:
     ```bash
     grep -c "@lru_cache\|@cached\|cache" backend/app/services/openalex_service.py
     ```
  
  2. If exists: Create cache.py with above content
  3. If not exists: Skip this file, add note for future enhancement

validation:
  - python -c "from app.services.openalex.cache import cached, clear_cache"
  - Cache decorator works with async functions
```

---

### Step 3.2: Extract HTTP Client
```yaml
file: backend/app/services/openalex/client.py
estimated_lines: 150-200
depends_on: config.py, exceptions.py
time: 40 min

content: |
  """
  OpenAlex API HTTP Client
  
  Handles all HTTP communication with the OpenAlex API.
  Features:
  - Async context manager for connection pooling
  - Automatic retries with exponential backoff
  - Rate limit handling
  - Consistent error handling
  
  Usage:
      async with OpenAlexClient() as client:
          data = await client.get("/journals", params={"search": "nature"})
  """
  import logging
  from typing import Optional, Dict, Any
  
  import httpx
  from tenacity import (
      retry,
      stop_after_attempt,
      wait_exponential,
      retry_if_exception_type,
  )
  
  from .config import get_settings
  from .exceptions import (
      OpenAlexAPIError,
      OpenAlexNotFoundError,
      OpenAlexRateLimitError,
      OpenAlexTimeoutError,
      OpenAlexConnectionError,
  )
  
  logger = logging.getLogger(__name__)
  
  
  class OpenAlexClient:
      """
      Async HTTP client for OpenAlex API
      
      Designed to be used as an async context manager for proper
      connection management.
      
      Attributes:
          base_url: API base URL
          timeout: Request timeout in seconds
          email: Email for polite pool (optional)
      
      Example:
          async with OpenAlexClient() as client:
              result = await client.get("/journals/issn:0028-0836")
              print(result["display_name"])
      """
      
      def __init__(
          self,
          base_url: Optional[str] = None,
          timeout: Optional[float] = None,
          email: Optional[str] = None,
      ):
          """
          Initialize OpenAlex client
          
          Args:
              base_url: Override default API URL
              timeout: Override default timeout
              email: Override email for polite pool
          """
          settings = get_settings()
          
          self.base_url = base_url or settings.api_base_url
          self.timeout = timeout or settings.timeout
          self.email = email or settings.email
          self._client: Optional[httpx.AsyncClient] = None
          self._settings = settings
      
      async def __aenter__(self) -> "OpenAlexClient":
          """Enter async context - create HTTP client"""
          self._client = httpx.AsyncClient(
              base_url=self.base_url,
              timeout=self.timeout,
              headers=self._build_headers(),
              follow_redirects=True,
          )
          logger.debug(f"OpenAlex client created: {self.base_url}")
          return self
      
      async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
          """Exit async context - close HTTP client"""
          if self._client:
              await self._client.aclose()
              logger.debug("OpenAlex client closed")
      
      def _build_headers(self) -> Dict[str, str]:
          """Build request headers"""
          headers = {
              "Accept": "application/json",
              "User-Agent": "FindMyJournal/1.0",
          }
          if self.email:
              # Email header for polite pool (higher rate limits)
              headers["mailto"] = self.email
          return headers
      
      @retry(
          stop=stop_after_attempt(3),
          wait=wait_exponential(multiplier=1, min=2, max=10),
          retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
          before_sleep=lambda retry_state: logger.warning(
              f"Retry {retry_state.attempt_number} for OpenAlex API"
          ),
      )
      async def get(
          self,
          endpoint: str,
          params: Optional[Dict[str, Any]] = None,
      ) -> Dict[str, Any]:
          """
          Make GET request to OpenAlex API
          
          Args:
              endpoint: API endpoint (e.g., "/journals")
              params: Query parameters
              
          Returns:
              JSON response as dictionary
              
          Raises:
              OpenAlexNotFoundError: Resource not found (404)
              OpenAlexRateLimitError: Rate limit exceeded (429)
              OpenAlexAPIError: Other API errors
              OpenAlexTimeoutError: Request timed out
              OpenAlexConnectionError: Connection failed
          """
          if not self._client:
              raise RuntimeError("Client not initialized. Use 'async with' context.")
          
          logger.debug(f"GET {endpoint} params={params}")
          
          try:
              response = await self._client.get(endpoint, params=params)
          except httpx.TimeoutException as e:
              logger.error(f"Timeout: {endpoint}")
              raise OpenAlexTimeoutError(self.timeout) from e
          except httpx.ConnectError as e:
              logger.error(f"Connection error: {endpoint}")
              raise OpenAlexConnectionError(f"Failed to connect: {e}") from e
          
          # Handle error responses
          if response.status_code == 404:
              raise OpenAlexNotFoundError(endpoint)
          
          if response.status_code == 429:
              retry_after = response.headers.get("Retry-After")
              raise OpenAlexRateLimitError(
                  int(retry_after) if retry_after else None
              )
          
          if response.status_code >= 400:
              raise OpenAlexAPIError(
                  response.status_code,
                  response.text[:500]  # Limit error message length
              )
          
          return response.json()
      
      async def get_single(self, endpoint: str) -> Dict[str, Any]:
          """
          Get single resource (convenience method)
          
          Args:
              endpoint: Full endpoint path
              
          Returns:
              Single resource data
          """
          return await self.get(endpoint)
      
      async def get_list(
          self,
          endpoint: str,
          params: Optional[Dict[str, Any]] = None,
      ) -> Dict[str, Any]:
          """
          Get list of resources with pagination info
          
          Args:
              endpoint: API endpoint
              params: Query parameters including pagination
              
          Returns:
              Response with 'results' and 'meta' keys
          """
          return await self.get(endpoint, params)
  
  
  async def get_client() -> OpenAlexClient:
      """
      Factory function for creating client instances
      
      For use with dependency injection in FastAPI.
      
      Returns:
          Configured OpenAlexClient instance
      """
      return OpenAlexClient()

actions:
  1. Find HTTP client code in original:
     ```bash
     grep -n "httpx\|requests\|\.get(\|\.post(\|async with" backend/app/services/openalex_service.py
     ```
  
  2. Extract all HTTP-related code
  
  3. Add tenacity for retries if not present
  
  4. Ensure proper async context manager

validation:
  - python -c "from app.services.openalex.client import OpenAlexClient"
  - Test with: async with OpenAlexClient() as c: print(await c.get("/journals", {"per_page": 1}))
```

---

# PHASE 4: Extract Domain Modules
## Agent: backend-agent
## Time: 90 min
## Depends on: Phase 3
## Parallel: journals.py ∥ search.py

---

### Step 4.1: Extract Journal Operations
```yaml
file: backend/app/services/openalex/journals.py
estimated_lines: 180-220
depends_on: client.py, models.py, utils.py, exceptions.py
time: 45 min

content: |
  """
  Journal-specific OpenAlex Operations
  
  This module provides all journal-related functionality:
  - Fetching journal by ISSN
  - Getting journal details
  - Retrieving journal metrics
  - Batch operations
  
  All functions support optional client injection for testing.
  """
  import logging
  from typing import Optional, List
  
  from .client import OpenAlexClient
  from .models import JournalInfo, JournalMetrics
  from .utils import validate_issn, normalize_issn, parse_openalex_id
  from .exceptions import ISSNValidationError, OpenAlexNotFoundError
  # Uncomment if cache.py exists:
  # from .cache import cached
  
  logger = logging.getLogger(__name__)
  
  
  async def get_journal_by_issn(
      issn: str,
      client: Optional[OpenAlexClient] = None,
  ) -> Optional[JournalInfo]:
      """
      Fetch journal information by ISSN
      
      Args:
          issn: Journal ISSN (format: XXXX-XXXX)
          client: Optional pre-configured client (for testing)
          
      Returns:
          JournalInfo if found, None if not found
          
      Raises:
          ISSNValidationError: If ISSN format is invalid
          
      Example:
          journal = await get_journal_by_issn("0028-0836")
          print(journal.display_name)  # "Nature"
      """
      normalized = normalize_issn(issn)
      
      if not validate_issn(normalized):
          raise ISSNValidationError(issn)
      
      logger.info(f"Fetching journal by ISSN: {normalized}")
      
      async def _fetch():
          async with OpenAlexClient() as c:
              return await c.get(f"/journals/issn:{normalized}")
      
      try:
          if client:
              data = await client.get(f"/journals/issn:{normalized}")
          else:
              data = await _fetch()
          
          return JournalInfo(**data) if data else None
          
      except OpenAlexNotFoundError:
          logger.info(f"Journal not found: {normalized}")
          return None
  
  
  async def get_journal_by_id(
      journal_id: str,
      client: Optional[OpenAlexClient] = None,
  ) -> Optional[JournalInfo]:
      """
      Fetch journal by OpenAlex ID
      
      Args:
          journal_id: OpenAlex journal ID (e.g., "J1234567" or full URL)
          client: Optional pre-configured client
          
      Returns:
          JournalInfo if found, None if not found
      """
      parsed_id = parse_openalex_id(journal_id)
      
      logger.info(f"Fetching journal by ID: {parsed_id}")
      
      try:
          async with (client or OpenAlexClient()) as c:
              data = await c.get(f"/journals/{parsed_id}")
          return JournalInfo(**data) if data else None
          
      except OpenAlexNotFoundError:
          logger.info(f"Journal not found: {parsed_id}")
          return None
  
  
  async def get_journal_details(
      journal_id: str,
      client: Optional[OpenAlexClient] = None,
  ) -> Optional[JournalInfo]:
      """
      Get full journal details including all available fields
      
      Args:
          journal_id: OpenAlex journal ID
          client: Optional pre-configured client
          
      Returns:
          Complete JournalInfo with all fields
      """
      return await get_journal_by_id(journal_id, client)
  
  
  async def get_journal_metrics(
      journal_id: str,
      client: Optional[OpenAlexClient] = None,
  ) -> Optional[JournalMetrics]:
      """
      Get journal bibliometric metrics
      
      Args:
          journal_id: OpenAlex journal ID
          client: Optional pre-configured client
          
      Returns:
          JournalMetrics with h-index, citation counts, etc.
      """
      parsed_id = parse_openalex_id(journal_id)
      
      logger.info(f"Fetching metrics for: {parsed_id}")
      
      try:
          async with (client or OpenAlexClient()) as c:
              data = await c.get(f"/journals/{parsed_id}")
          
          if not data:
              return None
          
          return JournalMetrics(
              h_index=data.get("summary_stats", {}).get("h_index"),
              i10_index=data.get("summary_stats", {}).get("i10_index"),
              cited_by_count=data.get("cited_by_count"),
              works_count=data.get("works_count"),
              two_year_mean_citedness=data.get("summary_stats", {}).get(
                  "2yr_mean_citedness"
              ),
          )
          
      except OpenAlexNotFoundError:
          return None
  
  
  async def get_journals_batch(
      issns: List[str],
      batch_size: int = 50,
      skip_invalid: bool = True,
      client: Optional[OpenAlexClient] = None,
  ) -> List[JournalInfo]:
      """
      Fetch multiple journals efficiently
      
      Args:
          issns: List of ISSNs to fetch
          batch_size: Number of concurrent requests
          skip_invalid: Skip invalid ISSNs instead of raising
          client: Optional pre-configured client
          
      Returns:
          List of JournalInfo for found journals
      """
      results: List[JournalInfo] = []
      
      # Validate and normalize
      valid_issns = []
      for issn in issns:
          normalized = normalize_issn(issn)
          if validate_issn(normalized):
              valid_issns.append(normalized)
          elif not skip_invalid:
              raise ISSNValidationError(issn)
          else:
              logger.warning(f"Skipping invalid ISSN: {issn}")
      
      # Use filter API for batch fetching
      if valid_issns:
          async with (client or OpenAlexClient()) as c:
              # OpenAlex supports OR filter for multiple ISSNs
              issn_filter = "|".join(valid_issns)
              data = await c.get(
                  "/journals",
                  params={
                      "filter": f"issn:{issn_filter}",
                      "per_page": min(len(valid_issns), 200),
                  }
              )
              
              for item in data.get("results", []):
                  results.append(JournalInfo(**item))
      
      logger.info(f"Batch fetch: {len(results)}/{len(issns)} journals found")
      return results

actions:
  1. Find all journal-related functions:
     ```bash
     grep -n "journal\|issn" backend/app/services/openalex_service.py | grep "^[0-9]*:.*def "
     ```
  
  2. Move all identified functions to journals.py
  
  3. Update function signatures to support client injection
  
  4. Add proper error handling and logging

validation:
  - python -c "from app.services.openalex.journals import get_journal_by_issn"
  - Test: await get_journal_by_issn("0028-0836")
```

---

### Step 4.2: Extract Search Operations
```yaml
file: backend/app/services/openalex/search.py
estimated_lines: 180-220
depends_on: client.py, models.py, utils.py
time: 45 min

content: |
  """
  OpenAlex Search Operations
  
  This module provides search functionality:
  - Text search across journals
  - Discipline/concept filtering
  - Advanced multi-criteria search
  - Pagination support
  """
  import logging
  from typing import Optional, List, Dict, Any
  
  from .client import OpenAlexClient
  from .models import SearchResult, JournalInfo, SearchMeta
  from .utils import build_query_params
  
  logger = logging.getLogger(__name__)
  
  
  async def search_journals(
      query: str,
      page: int = 1,
      per_page: int = 25,
      filters: Optional[Dict[str, Any]] = None,
      sort: Optional[str] = None,
      client: Optional[OpenAlexClient] = None,
  ) -> SearchResult:
      """
      Search journals by text query
      
      Args:
          query: Search text (searches title, publisher, etc.)
          page: Page number (1-indexed)
          per_page: Results per page (max 200)
          filters: Additional OpenAlex filters
          sort: Sort field (e.g., "cited_by_count:desc")
          client: Optional pre-configured client
          
      Returns:
          SearchResult with matching journals and pagination info
          
      Example:
          results = await search_journals("machine learning", per_page=10)
          for journal in results.results:
              print(journal.display_name)
      """
      params = build_query_params(
          page=page,
          per_page=per_page,
          search=query,
          filters=filters,
          sort=sort,
      )
      
      logger.info(f"Searching journals: '{query}' (page {page})")
      
      async with (client or OpenAlexClient()) as c:
          data = await c.get("/journals", params=params)
      
      meta = data.get("meta", {})
      
      return SearchResult(
          results=[JournalInfo(**j) for j in data.get("results", [])],
          meta=SearchMeta(
              count=meta.get("count", 0),
              page=page,
              per_page=per_page,
          ),
      )
  
  
  async def search_by_discipline(
      discipline: str,
      page: int = 1,
      per_page: int = 25,
      min_works: Optional[int] = None,
      is_oa: Optional[bool] = None,
      client: Optional[OpenAlexClient] = None,
  ) -> SearchResult:
      """
      Search journals by academic discipline/concept
      
      Args:
          discipline: Discipline name (e.g., "Computer Science")
          page: Page number
          per_page: Results per page
          min_works: Minimum works count filter
          is_oa: Filter by open access status
          client: Optional pre-configured client
          
      Returns:
          SearchResult with journals in the discipline
      """
      filters: Dict[str, Any] = {
          "concepts.display_name": discipline,
      }
      
      if min_works is not None:
          filters["works_count"] = f">{min_works}"
      
      if is_oa is not None:
          filters["is_oa"] = str(is_oa).lower()
      
      logger.info(f"Searching by discipline: {discipline}")
      
      return await search_journals(
          query="",
          page=page,
          per_page=per_page,
          filters=filters,
          client=client,
      )
  
  
  async def search_by_publisher(
      publisher: str,
      page: int = 1,
      per_page: int = 25,
      client: Optional[OpenAlexClient] = None,
  ) -> SearchResult:
      """
      Search journals by publisher name
      
      Args:
          publisher: Publisher name to search
          page: Page number
          per_page: Results per page
          client: Optional pre-configured client
          
      Returns:
          SearchResult with publisher's journals
      """
      filters = {"publisher": publisher}
      
      logger.info(f"Searching by publisher: {publisher}")
      
      return await search_journals(
          query="",
          page=page,
          per_page=per_page,
          filters=filters,
          client=client,
      )
  
  
  async def advanced_search(
      query: Optional[str] = None,
      issn: Optional[str] = None,
      publisher: Optional[str] = None,
      discipline: Optional[str] = None,
      is_oa: Optional[bool] = None,
      is_in_doaj: Optional[bool] = None,
      min_h_index: Optional[int] = None,
      min_works: Optional[int] = None,
      min_citations: Optional[int] = None,
      page: int = 1,
      per_page: int = 25,
      sort: str = "cited_by_count:desc",
      client: Optional[OpenAlexClient] = None,
  ) -> SearchResult:
      """
      Advanced search with multiple criteria
      
      All parameters are optional and combined with AND logic.
      
      Args:
          query: Text search query
          issn: Filter by ISSN
          publisher: Filter by publisher name
          discipline: Filter by discipline/concept
          is_oa: Filter by open access status
          is_in_doaj: Filter by DOAJ listing
          min_h_index: Minimum h-index
          min_works: Minimum works count
          min_citations: Minimum citation count
          page: Page number
          per_page: Results per page
          sort: Sort field and direction
          client: Optional pre-configured client
          
      Returns:
          SearchResult matching all criteria
          
      Example:
          results = await advanced_search(
              discipline="Biology",
              is_oa=True,
              min_h_index=50,
              sort="works_count:desc"
          )
      """
      filters: Dict[str, Any] = {}
      
      if issn:
          filters["issn"] = issn
      if publisher:
          filters["publisher"] = publisher
      if discipline:
          filters["concepts.display_name"] = discipline
      if is_oa is not None:
          filters["is_oa"] = str(is_oa).lower()
      if is_in_doaj is not None:
          filters["is_in_doaj"] = str(is_in_doaj).lower()
      if min_h_index is not None:
          filters["summary_stats.h_index"] = f">{min_h_index}"
      if min_works is not None:
          filters["works_count"] = f">{min_works}"
      if min_citations is not None:
          filters["cited_by_count"] = f">{min_citations}"
      
      logger.info(f"Advanced search: query='{query}', filters={len(filters)}")
      
      return await search_journals(
          query=query or "",
          page=page,
          per_page=per_page,
          filters=filters if filters else None,
          sort=sort,
          client=client,
      )
  
  
  async def get_top_journals(
      discipline: Optional[str] = None,
      limit: int = 10,
      sort_by: str = "cited_by_count",
      client: Optional[OpenAlexClient] = None,
  ) -> List[JournalInfo]:
      """
      Get top journals by metric
      
      Args:
          discipline: Optional discipline filter
          limit: Number of journals to return
          sort_by: Metric to sort by (cited_by_count, works_count, h_index)
          client: Optional pre-configured client
          
      Returns:
          List of top journals
      """
      filters = None
      if discipline:
          filters = {"concepts.display_name": discipline}
      
      result = await search_journals(
          query="",
          page=1,
          per_page=limit,
          filters=filters,
          sort=f"{sort_by}:desc",
          client=client,
      )
      
      return result.results

actions:
  1. Find all search-related functions:
     ```bash
     grep -n "search\|find\|query" backend/app/services/openalex_service.py | grep "^[0-9]*:.*def "
     ```
  
  2. Move all identified functions to search.py
  
  3. Ensure consistent pagination handling
  
  4. Add sorting options

validation:
  - python -c "from app.services.openalex.search import search_journals"
  - Test: await search_journals("nature", per_page=5)
```

---

# PHASE 5: Backward Compatibility Layer
## Agent: backend-agent
## Time: 30 min
## Depends on: Phase 4

```yaml
task: "Create backward-compatible exports"
priority: CRITICAL
estimated_time: 30 min

actions:
  1. Create __init__.py:
```

```python
# File: backend/app/services/openalex/__init__.py
"""
OpenAlex Service Package

This module provides integration with the OpenAlex API for journal
discovery and bibliometric data retrieval.

Backward Compatibility:
    All functions previously available from openalex_service.py
    are re-exported here for backward compatibility.

Usage:
    # Recommended (new style)
    from app.services.openalex import get_journal_by_issn, search_journals
    
    # Still works (old style - deprecated)
    from app.services.openalex_service import get_journal_by_issn

Modules:
    - journals: Journal-specific operations
    - search: Search functionality
    - client: HTTP client
    - models: Data models
    - utils: Utility functions
    - exceptions: Custom exceptions
    - config: Configuration
"""

# Version
__version__ = "2.0.0"

# Re-export all public functions for backward compatibility

# Journal operations
from .journals import (
    get_journal_by_issn,
    get_journal_by_id,
    get_journal_details,
    get_journal_metrics,
    get_journals_batch,
)

# Search operations
from .search import (
    search_journals,
    search_by_discipline,
    search_by_publisher,
    advanced_search,
    get_top_journals,
)

# Models
from .models import (
    JournalInfo,
    JournalMetrics,
    SearchResult,
    SearchMeta,
    Concept,
    Publisher,
)

# Exceptions
from .exceptions import (
    OpenAlexError,
    OpenAlexAPIError,
    OpenAlexNotFoundError,
    OpenAlexRateLimitError,
    OpenAlexTimeoutError,
    OpenAlexValidationError,
    ISSNValidationError,
    OpenAlexConnectionError,
)

# Client (for advanced usage)
from .client import OpenAlexClient, get_client

# Configuration
from .config import OpenAlexSettings, get_settings

# Utilities (commonly used)
from .utils import validate_issn, normalize_issn

# Public API definition
__all__ = [
    # Version
    "__version__",
    # Journals
    "get_journal_by_issn",
    "get_journal_by_id",
    "get_journal_details",
    "get_journal_metrics",
    "get_journals_batch",
    # Search
    "search_journals",
    "search_by_discipline",
    "search_by_publisher",
    "advanced_search",
    "get_top_journals",
    # Models
    "JournalInfo",
    "JournalMetrics",
    "SearchResult",
    "SearchMeta",
    "Concept",
    "Publisher",
    # Client
    "OpenAlexClient",
    "get_client",
    # Config
    "OpenAlexSettings",
    "get_settings",
    # Exceptions
    "OpenAlexError",
    "OpenAlexAPIError",
    "OpenAlexNotFoundError",
    "OpenAlexRateLimitError",
    "OpenAlexTimeoutError",
    "OpenAlexValidationError",
    "ISSNValidationError",
    "OpenAlexConnectionError",
    # Utilities
    "validate_issn",
    "normalize_issn",
]
```

```yaml
  2. Create deprecated facade (old file):
```

```python
# File: backend/app/services/openalex_service.py
"""
DEPRECATED: Import from app.services.openalex instead

This file exists for backward compatibility only and will be
removed in version 3.0.0.

Migration Guide:
    # Old (deprecated):
    from app.services.openalex_service import get_journal_by_issn
    
    # New (recommended):
    from app.services.openalex import get_journal_by_issn
    
    # Or with explicit module:
    from app.services.openalex.journals import get_journal_by_issn
"""
import warnings
from typing import TYPE_CHECKING

# Emit deprecation warning on import
warnings.warn(
    "openalex_service is deprecated. "
    "Import from app.services.openalex instead. "
    "This module will be removed in version 3.0.0",
    DeprecationWarning,
    stacklevel=2
)

# TYPE_CHECKING block for IDE support
if TYPE_CHECKING:
    from .openalex import (
        get_journal_by_issn,
        get_journal_by_id,
        get_journal_details,
        get_journal_metrics,
        get_journals_batch,
        search_journals,
        search_by_discipline,
        search_by_publisher,
        advanced_search,
        get_top_journals,
        JournalInfo,
        JournalMetrics,
        SearchResult,
        OpenAlexClient,
        OpenAlexError,
        OpenAlexAPIError,
        validate_issn,
        normalize_issn,
    )

# Runtime re-exports
from .openalex import *  # noqa: F401, F403
```

```yaml
  3. Update all existing imports in codebase:
     ```bash
     # Find all files importing from openalex_service
     grep -rn "from.*openalex_service import\|import openalex_service" backend/app/
     
     # For each file, update to new import path
     # Example:
     # OLD: from app.services.openalex_service import get_journal_by_issn
     # NEW: from app.services.openalex import get_journal_by_issn
     ```
  
  4. Test backward compatibility:
     ```bash
     python -c "
     # Test new imports
     from app.services.openalex import get_journal_by_issn
     print('New import: OK')
     
     # Test old imports (should show deprecation warning)
     from app.services.openalex_service import get_journal_by_issn
     print('Old import: OK (with warning)')
     "
     ```

validation:
  - All existing code still works
  - Deprecation warning appears for old imports
  - No import errors anywhere
  - IDE autocomplete works with both paths
```

---

# PHASE 6: Testing & Validation
## Agent: qa-agent
## Time: 75 min
## Depends on: Phase 5
## Parallel: Test files can be created in parallel

---

### Step 6.1: Create Test Fixtures
```yaml
file: backend/tests/services/openalex/conftest.py
estimated_lines: 80-100
time: 15 min

content: |
  """
  Shared test fixtures for OpenAlex tests
  """
  import pytest
  from unittest.mock import AsyncMock, MagicMock, patch
  from typing import Dict, Any
  
  
  @pytest.fixture
  def mock_client():
      """Mock OpenAlex client for unit tests"""
      client = AsyncMock()
      client.get = AsyncMock(return_value={"results": [], "meta": {"count": 0}})
      client.__aenter__ = AsyncMock(return_value=client)
      client.__aexit__ = AsyncMock(return_value=None)
      return client
  
  
  @pytest.fixture
  def sample_journal_data() -> Dict[str, Any]:
      """Sample journal response data from OpenAlex API"""
      return {
          "id": "https://openalex.org/J137773608",
          "display_name": "Nature",
          "issn_l": "0028-0836",
          "issns": ["0028-0836", "1476-4687"],
          "publisher": "Springer Nature",
          "homepage_url": "https://www.nature.com/nature/",
          "works_count": 423847,
          "cited_by_count": 34567890,
          "is_oa": False,
          "is_in_doaj": False,
          "summary_stats": {
              "h_index": 1234,
              "i10_index": 56789,
              "2yr_mean_citedness": 45.67,
          },
      }
  
  
  @pytest.fixture
  def sample_search_response(sample_journal_data) -> Dict[str, Any]:
      """Sample search response with pagination"""
      return {
          "results": [sample_journal_data],
          "meta": {
              "count": 1,
              "page": 1,
              "per_page": 25,
          },
      }
  
  
  @pytest.fixture
  def mock_httpx_client():
      """Mock httpx.AsyncClient for integration tests"""
      with patch("httpx.AsyncClient") as mock:
          client_instance = AsyncMock()
          mock.return_value.__aenter__.return_value = client_instance
          mock.return_value.__aexit__.return_value = None
          yield client_instance
  
  
  @pytest.fixture
  def invalid_issns():
      """Collection of invalid ISSNs for testing validation"""
      return [
          "",
          "invalid",
          "1234-56789",  # Too long
          "123-4567",    # Too short
          "ABCD-EFGH",   # Letters
          "1234567",     # No hyphen (8 digits) - this might be normalized
          None,
      ]
  
  
  @pytest.fixture
  def valid_issns():
      """Collection of valid ISSNs for testing"""
      return [
          "0028-0836",   # Nature
          "1234-567X",   # With X check digit
          "0000-0000",   # Edge case
      ]
```

---

### Step 6.2: Create Unit Tests
```yaml
files:
  - backend/tests/services/openalex/test_utils.py
  - backend/tests/services/openalex/test_models.py
  - backend/tests/services/openalex/test_exceptions.py
  - backend/tests/services/openalex/test_client.py
  - backend/tests/services/openalex/test_journals.py
  - backend/tests/services/openalex/test_search.py
  
time: 45 min (all tests)
```

```python
# File: backend/tests/services/openalex/test_utils.py
"""Tests for OpenAlex utilities"""
import pytest
from app.services.openalex.utils import (
    validate_issn,
    normalize_issn,
    build_query_params,
    parse_openalex_id,
)


class TestValidateISSN:
    """Tests for ISSN validation"""
    
    def test_valid_issn_standard(self):
        assert validate_issn("0028-0836") is True
    
    def test_valid_issn_with_x(self):
        assert validate_issn("1234-567X") is True
    
    def test_valid_issn_lowercase_x(self):
        assert validate_issn("1234-567x") is True
    
    def test_invalid_issn_no_hyphen(self):
        assert validate_issn("00280836") is False
    
    def test_invalid_issn_too_short(self):
        assert validate_issn("1234-567") is False
    
    def test_invalid_issn_too_long(self):
        assert validate_issn("1234-56789") is False
    
    def test_invalid_issn_letters(self):
        assert validate_issn("ABCD-EFGH") is False
    
    def test_invalid_issn_empty(self):
        assert validate_issn("") is False
    
    def test_invalid_issn_none(self):
        assert validate_issn(None) is False


class TestNormalizeISSN:
    """Tests for ISSN normalization"""
    
    def test_already_normalized(self):
        assert normalize_issn("0028-0836") == "0028-0836"
    
    def test_no_hyphen(self):
        assert normalize_issn("00280836") == "0028-0836"
    
    def test_lowercase_x(self):
        assert normalize_issn("1234-567x") == "1234-567X"
    
    def test_with_spaces(self):
        assert normalize_issn(" 0028-0836 ") == "0028-0836"


class TestBuildQueryParams:
    """Tests for query parameter building"""
    
    def test_default_params(self):
        params = build_query_params()
        assert params["page"] == 1
        assert "per_page" in params
    
    def test_with_search(self):
        params = build_query_params(search="nature")
        assert params["search"] == "nature"
    
    def test_with_filters(self):
        params = build_query_params(filters={"is_oa": True})
        assert "filter" in params


class TestParseOpenAlexId:
    """Tests for OpenAlex ID parsing"""
    
    def test_full_url(self):
        assert parse_openalex_id("https://openalex.org/J1234") == "J1234"
    
    def test_just_id(self):
        assert parse_openalex_id("J1234") == "J1234"
```

```python
# File: backend/tests/services/openalex/test_journals.py
"""Tests for journal operations"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.openalex.journals import (
    get_journal_by_issn,
    get_journal_metrics,
)
from app.services.openalex.exceptions import ISSNValidationError
from app.services.openalex.models import JournalInfo


class TestGetJournalByISSN:
    """Tests for get_journal_by_issn"""
    
    @pytest.mark.asyncio
    async def test_valid_issn_returns_journal(self, mock_client, sample_journal_data):
        mock_client.get.return_value = sample_journal_data
        
        with patch("app.services.openalex.journals.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await get_journal_by_issn("0028-0836")
        
        assert result is not None
        assert isinstance(result, JournalInfo)
        assert result.display_name == "Nature"
        assert result.issn_l == "0028-0836"
    
    @pytest.mark.asyncio
    async def test_invalid_issn_raises_error(self):
        with pytest.raises(ISSNValidationError) as exc_info:
            await get_journal_by_issn("invalid-issn")
        
        assert "invalid-issn" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_not_found_returns_none(self, mock_client):
        from app.services.openalex.exceptions import OpenAlexNotFoundError
        mock_client.get.side_effect = OpenAlexNotFoundError("not found")
        
        with patch("app.services.openalex.journals.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await get_journal_by_issn("0000-0000")
        
        assert result is None


class TestGetJournalMetrics:
    """Tests for get_journal_metrics"""
    
    @pytest.mark.asyncio
    async def test_returns_metrics(self, mock_client, sample_journal_data):
        mock_client.get.return_value = sample_journal_data
        
        with patch("app.services.openalex.journals.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await get_journal_metrics("J137773608")
        
        assert result is not None
        assert result.h_index == 1234
        assert result.cited_by_count == 34567890
```

```python
# File: backend/tests/services/openalex/test_search.py
"""Tests for search operations"""
import pytest
from unittest.mock import patch

from app.services.openalex.search import (
    search_journals,
    advanced_search,
)
from app.services.openalex.models import SearchResult


class TestSearchJournals:
    """Tests for search_journals"""
    
    @pytest.mark.asyncio
    async def test_basic_search(self, mock_client, sample_search_response):
        mock_client.get.return_value = sample_search_response
        
        with patch("app.services.openalex.search.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await search_journals("nature")
        
        assert isinstance(result, SearchResult)
        assert len(result.results) == 1
        assert result.meta.count == 1
    
    @pytest.mark.asyncio
    async def test_empty_results(self, mock_client):
        mock_client.get.return_value = {"results": [], "meta": {"count": 0}}
        
        with patch("app.services.openalex.search.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await search_journals("nonexistent")
        
        assert len(result.results) == 0
        assert result.meta.count == 0


class TestAdvancedSearch:
    """Tests for advanced_search"""
    
    @pytest.mark.asyncio
    async def test_with_filters(self, mock_client, sample_search_response):
        mock_client.get.return_value = sample_search_response
        
        with patch("app.services.openalex.search.OpenAlexClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = None
            
            result = await advanced_search(
                discipline="Biology",
                is_oa=True,
                min_h_index=50,
            )
        
        assert isinstance(result, SearchResult)
        # Verify filters were applied (check mock call)
        call_args = mock_client.get.call_args
        assert "filter" in call_args.kwargs.get("params", {}) or \
               "filter" in (call_args.args[1] if len(call_args.args) > 1 else {})
```

---

### Step 6.3: Run Validation Suite
```yaml
task: "Run all validation checks"
time: 15 min

actions:
  1. Run unit tests:
     ```bash
     cd backend
     pytest tests/services/openalex/ -v --tb=short
     ```
  
  2. Check import integrity:
     ```bash
     python -c "
     print('Testing imports...')
     
     # Test new package imports
     from app.services.openalex import (
         get_journal_by_issn,
         search_journals,
         JournalInfo,
         OpenAlexClient,
         OpenAlexError,
     )
     print('✓ Package imports OK')
     
     # Test module imports
     from app.services.openalex.journals import get_journal_by_issn
     from app.services.openalex.search import search_journals
     from app.services.openalex.client import OpenAlexClient
     from app.services.openalex.models import JournalInfo
     from app.services.openalex.config import get_settings
     print('✓ Module imports OK')
     
     # Test backward compatibility (expect warning)
     import warnings
     with warnings.catch_warnings(record=True) as w:
         warnings.simplefilter('always')
         from app.services.openalex_service import get_journal_by_issn
         assert len(w) == 1
         assert 'deprecated' in str(w[0].message).lower()
     print('✓ Backward compatibility OK (with deprecation warning)')
     
     print('\\nAll import tests passed!')
     "
     ```
  
  3. Check for circular imports:
     ```bash
     python -c "
     import sys
     
     # Import in different orders to detect circular imports
     orderings = [
         ['client', 'models', 'utils', 'journals', 'search'],
         ['search', 'journals', 'utils', 'models', 'client'],
         ['models', 'exceptions', 'config', 'utils', 'client', 'journals', 'search'],
     ]
     
     for order in orderings:
         # Clear cached imports
         for mod in list(sys.modules.keys()):
             if 'openalex' in mod:
                 del sys.modules[mod]
         
         for module in order:
             exec(f'from app.services.openalex import {module}')
     
     print('✓ No circular imports detected')
     "
     ```
  
  4. Verify line counts:
     ```bash
     echo "Line counts per file:"
     wc -l backend/app/services/openalex/*.py | sort -n
     echo ""
     echo "Target: Each file should be under 250 lines"
     ```
  
  5. Integration smoke test:
     ```bash
     # Start server and test endpoints
     cd backend
     timeout 30 uvicorn app.main:app --port 8001 &
     sleep 5
     
     # Test if endpoints still work
     curl -s http://localhost:8001/api/v1/health || echo "Health check"
     curl -s "http://localhost:8001/api/v1/journals/search?q=test&limit=1" || echo "Search test"
     
     # Cleanup
     pkill -f "uvicorn.*8001"
     ```

validation_checklist:
  - [ ] All unit tests pass
  - [ ] No import errors
  - [ ] No circular imports
  - [ ] Each file < 250 lines
  - [ ] Backward compatibility works with deprecation warning
  - [ ] API endpoints still functional
  - [ ] No runtime errors
```

---

# PHASE 7: Documentation & Cleanup
## Agent: docs-agent
## Time: 30 min
## Depends on: Phase 6

```yaml
task: "Update documentation"
priority: MEDIUM
estimated_time: 30 min

actions:
  1. Create module README:
     ```bash
     cat > backend/app/services/openalex/README.md << 'EOF'
     # OpenAlex Service Module
     
     Integration with the [OpenAlex API](https://docs.openalex.org/) for journal discovery
     and bibliometric data retrieval.
     
     ## Installation
     
     The module is part of the Find-My-Journal backend. No additional installation required.
     
     ## Quick Start
     
     ```python
     from app.services.openalex import (
         get_journal_by_issn,
         search_journals,
     )
     
     # Get journal by ISSN
     journal = await get_journal_by_issn("0028-0836")
     print(journal.display_name)  # Nature
     
     # Search journals
     results = await search_journals("machine learning", per_page=10)
     for journal in results.results:
         print(f"{journal.display_name}: h-index {journal.h_index}")
     ```
     
     ## Module Structure
     
     ```
     openalex/
     ├── __init__.py      # Public API exports
     ├── config.py        # Configuration settings
     ├── exceptions.py    # Custom exceptions
     ├── models.py        # Data models (Pydantic)
     ├── utils.py         # Utility functions
     ├── client.py        # HTTP client
     ├── journals.py      # Journal operations
     └── search.py        # Search operations
     ```
     
     ## Configuration
     
     Set these environment variables (all optional):
     
     | Variable | Default | Description |
     |----------|---------|-------------|
     | `OPENALEX_EMAIL` | None | Email for polite pool (higher rate limits) |
     | `OPENALEX_TIMEOUT` | 30.0 | Request timeout in seconds |
     | `OPENALEX_MAX_RETRIES` | 3 | Max retry attempts |
     | `OPENALEX_CACHE_TTL` | 3600 | Cache TTL in seconds |
     
     ## Migration from openalex_service.py
     
     The old `openalex_service.py` module is deprecated. Update imports:
     
     ```python
     # Old (deprecated)
     from app.services.openalex_service import get_journal_by_issn
     
     # New (recommended)
     from app.services.openalex import get_journal_by_issn
     ```
     
     ## API Reference
     
     ### Journal Operations
     
     - `get_journal_by_issn(issn)` - Fetch journal by ISSN
     - `get_journal_by_id(id)` - Fetch journal by OpenAlex ID
     - `get_journal_details(id)` - Get full journal details
     - `get_journal_metrics(id)` - Get bibliometric metrics
     - `get_journals_batch(issns)` - Batch fetch multiple journals
     
     ### Search Operations
     
     - `search_journals(query)` - Text search
     - `search_by_discipline(discipline)` - Filter by discipline
     - `search_by_publisher(publisher)` - Filter by publisher
     - `advanced_search(...)` - Multi-criteria search
     - `get_top_journals(...)` - Get top journals by metric
     
     ## Error Handling
     
     ```python
     from app.services.openalex import (
         get_journal_by_issn,
         ISSNValidationError,
         OpenAlexAPIError,
     )
     
     try:
         journal = await get_journal_by_issn("invalid")
     except ISSNValidationError as e:
         print(f"Invalid ISSN: {e.issn}")
     except OpenAlexAPIError as e:
         print(f"API error {e.status_code}: {e.message}")
     ```
     EOF
     ```
  
  2. Update project ARCHITECTURE.md (if exists):
     - Add section about OpenAlex module structure
     - Include dependency diagram
  
  3. Verify all docstrings are complete:
     ```bash
     # Check for missing docstrings
     python -c "
     import ast
     import os
     
     for filename in os.listdir('backend/app/services/openalex'):
         if filename.endswith('.py'):
             filepath = f'backend/app/services/openalex/{filename}'
             with open(filepath) as f:
                 tree = ast.parse(f.read())
             
             missing = []
             for node in ast.walk(tree):
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                     if not ast.get_docstring(node):
                         missing.append(node.name)
             
             if missing:
                 print(f'{filename}: Missing docstrings for: {missing}')
             else:
                 print(f'{filename}: ✓ All docstrings present')
     "
     ```

final_cleanup:
  1. Delete old monolith (ONLY after verification):
     ```bash
     # Only run after all tests pass and team approval
     # git rm backend/app/services/openalex_service.py
     # Or keep for one release cycle with deprecation warning
     ```
  
  2. Commit with detailed message:
     ```bash
     git add backend/app/services/openalex/
     git add backend/tests/services/openalex/
     git add backend/app/services/openalex_service.py  # Deprecated facade
     
     git commit -m "refactor(openalex): split monolith into clean modules
     
     Breaking down 1,230-line openalex_service.py into focused modules:
     - exceptions.py: Custom exception hierarchy
     - models.py: Pydantic data models
     - config.py: Configuration with env var support
     - utils.py: Validation and helper functions
     - client.py: HTTP client with retries
     - journals.py: Journal operations
     - search.py: Search functionality
     
     Changes:
     - Each module now < 250 lines
     - Added comprehensive unit tests
     - Added proper type hints and docstrings
     - Backward compatible via __init__.py re-exports
     - Old import path shows deprecation warning
     
     Migration:
     - from app.services.openalex_service import X  # deprecated
     + from app.services.openalex import X          # new
     "
     ```
```

---

# 📊 EXPECTED FINAL STRUCTURE

```
backend/app/services/openalex/
├── __init__.py       # ~70 lines   - Public API, re-exports
├── config.py         # ~60 lines   - Configuration settings
├── exceptions.py     # ~80 lines   - Custom exceptions
├── models.py         # ~140 lines  - Data models
├── utils.py          # ~110 lines  - Utilities
├── cache.py          # ~100 lines  - Caching (optional)
├── client.py         # ~180 lines  - HTTP client
├── journals.py       # ~200 lines  - Journal operations
├── search.py         # ~200 lines  - Search operations
└── README.md         # Documentation

backend/tests/services/openalex/
├── __init__.py
├── conftest.py       # ~100 lines  - Shared fixtures
├── test_utils.py     # ~80 lines
├── test_models.py    # ~60 lines
├── test_exceptions.py # ~40 lines
├── test_client.py    # ~100 lines
├── test_journals.py  # ~120 lines
└── test_search.py    # ~100 lines

Total Production Code: ~1,140 lines (vs 1,230 original)
Total Test Code: ~600 lines (NEW)
Max File Size: 200 lines ✓
Files: 9 modules + 7 test files
```

---

# ⚠️ RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Circular imports | Medium | High | Extract leaf nodes first |
| Breaking changes | Low | High | __init__.py re-exports all |
| Lost functionality | Low | High | Test after each phase |
| Type hint loss | Low | Medium | Explicit imports per file |
| Caching issues | Medium | Medium | Analyze first in Phase 0 |

---

# 🔄 ROLLBACK PLAN

```bash
# If issues arise, rollback to original:
git checkout main -- backend/app/services/openalex_service.py
git checkout main -- backend/app/services/

# Or if on feature branch:
git checkout main
git branch -D refactor/openalex-service
```

---

# ✅ SUCCESS CRITERIA

- [ ] Original 1,230 line file split into 8-9 modules
- [ ] Each module < 250 lines
- [ ] All existing tests pass
- [ ] New unit tests for each module
- [ ] No breaking changes to API
- [ ] Clear separation of concerns
- [ ] Proper logging throughout
- [ ] Complete documentation
- [ ] Backward compatibility with deprecation warning
- [ ] No circular imports
- [ ] Configuration via environment variables
