# Testing Reference

## Pytest Setup

### Project Structure

```
backend/
├── app/
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Shared fixtures
│   ├── test_search.py
│   ├── test_auth.py
│   └── test_users.py
├── pytest.ini
└── requirements-dev.txt
```

### Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
```

```txt
# requirements-dev.txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.26.0
```

## Test Client

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    """Async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def auth_headers():
    """Authenticated headers."""
    return {"Authorization": "Bearer test-token"}
```

## Basic Tests

### Testing Endpoints

```python
# tests/test_search.py
import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_search_success(client):
    response = await client.post(
        "/api/search",
        json={
            "title": "Machine learning in healthcare",
            "abstract": "This paper explores the application of machine learning..."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

@pytest.mark.asyncio
async def test_search_validation_error(client):
    response = await client.post(
        "/api/search",
        json={
            "title": "Short",  # Too short
            "abstract": "Too short"  # Too short
        }
    )
    assert response.status_code == 422  # Validation error
```

### Testing with Auth

```python
@pytest.mark.asyncio
async def test_protected_endpoint_unauthorized(client):
    response = await client.get("/api/users/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_authorized(client, auth_headers):
    response = await client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
```

## Mocking

### Mock External APIs

```python
# tests/conftest.py
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_openalex():
    """Mock OpenAlex API responses."""
    with patch("app.services.external_api.fetch_openalex_data") as mock:
        mock.return_value = {
            "results": [
                {"id": "1", "title": "Test Journal"}
            ]
        }
        yield mock

# Usage in test
@pytest.mark.asyncio
async def test_search_with_mock(client, mock_openalex):
    response = await client.post("/api/search", json={...})
    assert response.status_code == 200
    mock_openalex.assert_called_once()
```

### Mock Supabase

```python
@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.services.supabase.get_supabase_client") as mock:
        client = AsyncMock()
        
        # Mock table operations
        client.table.return_value.select.return_value \
            .eq.return_value.execute.return_value.data = [
                {"id": "1", "name": "Test"}
            ]
        
        mock.return_value = client
        yield client
```

## Testing Services

```python
# tests/test_services.py
import pytest
from app.services.search import SearchService

@pytest.fixture
def search_service(mock_supabase):
    return SearchService(mock_supabase)

@pytest.mark.asyncio
async def test_search_service(search_service):
    results = await search_service.search("test query")
    assert len(results) > 0

@pytest.mark.asyncio
async def test_search_empty_query(search_service):
    with pytest.raises(ValueError):
        await search_service.search("")
```

## Testing Pydantic Models

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from app.models.requests import SearchRequest

def test_valid_search_request():
    request = SearchRequest(
        title="Valid title for testing",
        abstract="A" * 100  # Long enough
    )
    assert request.title == "Valid title for testing"

def test_invalid_title_too_short():
    with pytest.raises(ValidationError) as exc_info:
        SearchRequest(
            title="Short",
            abstract="A" * 100
        )
    assert "title" in str(exc_info.value)

def test_sanitization():
    request = SearchRequest(
        title="Title with <script>evil</script>",
        abstract="A" * 100
    )
    assert "<script>" not in request.title
```

## Test Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/test_search.py -v

# Run tests matching pattern
pytest -k "test_search" -v

# Run only failed tests
pytest --lf
```

## Fixtures Library

```python
# tests/conftest.py

@pytest.fixture
def sample_user():
    return {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User"
    }

@pytest.fixture
def sample_journal():
    return {
        "id": "journal-123",
        "title": "Nature",
        "publisher": "Springer Nature",
        "impact_factor": 49.96
    }

@pytest.fixture
def sample_search_results():
    return [
        {"id": "1", "title": "Journal A", "score": 0.95},
        {"id": "2", "title": "Journal B", "score": 0.85},
    ]
```

## Integration Tests

```python
# tests/test_integration.py
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_search_flow(client, auth_headers):
    """Test complete search workflow."""
    
    # 1. Create search
    response = await client.post(
        "/api/search",
        json={"title": "Test", "abstract": "A" * 100},
        headers=auth_headers
    )
    assert response.status_code == 200
    search_id = response.json().get("search_id")
    
    # 2. Get search results
    response = await client.get(
        f"/api/search/{search_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # 3. Save journal
    journal_id = response.json()["results"][0]["id"]
    response = await client.post(
        f"/api/journals/{journal_id}/save",
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Running Tests

```bash
# All tests
pytest

# Verbose
pytest -v

# With print output
pytest -s

# Stop on first failure
pytest -x

# Run specific file
pytest tests/test_search.py

# Run specific test
pytest tests/test_search.py::test_health_check

# Skip slow tests
pytest -m "not slow"

# Only integration tests
pytest -m integration
```
