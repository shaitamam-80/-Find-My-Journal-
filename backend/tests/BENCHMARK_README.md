# Benchmark Tests for OpenAlex Search Algorithm

This directory contains comprehensive benchmark tests for evaluating the performance and accuracy of the OpenAlex search algorithm.

## Overview

The benchmark test suite (`test_benchmark_search.py`) validates that the search algorithm:
- Returns relevant journals for various academic disciplines
- Correctly detects the discipline from the abstract/title
- Includes expected high-quality journals in results
- Maintains acceptable performance (execution time)
- Provides proper quality metrics and categorization

## Test Cases

The benchmark includes test cases across multiple disciplines:

1. **Psychology - Child Development**: Tests empathy/social-emotional development research
2. **Medicine - Clinical Trial**: Tests COVID-19 vaccine efficacy research
3. **Computer Science - Machine Learning**: Tests transformer/NLP research
4. **Physics - Quantum Computing**: Tests superconducting qubit research

Each test case includes:
- Title and abstract of a realistic research paper
- Keywords
- Expected discipline
- Expected journals that should appear in results
- Minimum number of results required

## Running the Tests

### Run All Benchmark Tests

```bash
# From project root
cd backend
../venv/Scripts/python.exe -m pytest tests/test_benchmark_search.py -v -s -m benchmark

# Or from backend directory
pytest tests/test_benchmark_search.py -v -s -m benchmark
```

### Run Individual Test Cases

```bash
# Run only Psychology test
pytest tests/test_benchmark_search.py::TestSearchBenchmark::test_benchmark_case[Psychology - Child Development] -v -s

# Run only Medicine test
pytest tests/test_benchmark_search.py::TestSearchBenchmark::test_benchmark_case[Medicine - Clinical Trial] -v -s
```

### Run Quality Metrics Tests

```bash
# Test that results meet quality thresholds
pytest tests/test_benchmark_search.py::test_benchmark_quality_metrics -v -s -m benchmark
```

### Run Performance Tests

```bash
# Test execution time
pytest tests/test_benchmark_search.py::test_benchmark_execution_time -v -s -m benchmark
```

### Run Summary Report Only

```bash
# Run all benchmarks and generate summary
pytest tests/test_benchmark_search.py::test_benchmark_summary -v -s -m benchmark
```

## Understanding Results

### Individual Test Output

For each test case, you'll see:

```
================================================================================
BENCHMARK: Psychology - Child Development
================================================================================
Execution Time: 5.23s
Results Found: 15 (min required: 5)
Discipline: psychology (expected: psychology)
Discipline Correct: YES

Expected Journals (4):
  [FOUND] Frontiers in Psychology
  [FOUND] Child Development
  [MISSING] Developmental Psychology
  [FOUND] Infancy

Relevance Score: 75.00%

Top 5 Results:
  1. Frontiers in Psychology
     - H-index: 176
     - Works: 88234
     - Relevance: 195.80
     - Match Reason: High activity in relevant research topics
  ...
```

### Summary Report

After all tests complete, you'll see:

```
================================================================================
BENCHMARK SUMMARY REPORT
================================================================================

Total Tests: 4
Passed: 3 (75.0%)
Failed: 1

Execution Time:
  Total: 18.45s
  Average: 4.61s
  Min: 3.21s
  Max: 6.78s

Results per Test:
  Total: 58
  Average: 14.5

Discipline Detection:
  Correct: 4/4 (100.0%)

Journal Matching:
  Expected Journals: 13
  Found Journals: 10
  Average Relevance Score: 76.92%
```

## Success Criteria

A test passes if:
1. **Minimum Results**: Returns at least the minimum number of results (typically 5)
2. **Correct Discipline**: Detects the correct academic discipline
3. **Expected Journals**: Finds at least one of the expected journals
4. **Quality Metrics**: Results have proper H-index, categorization, and relevance scores
5. **Performance**: Executes within 30 seconds

The overall benchmark suite requires:
- **Pass Rate**: At least 75% of tests must pass
- **Discipline Accuracy**: At least 75% correct discipline detection
- **Journal Matching**: Average relevance score > 50%

## Adding New Test Cases

To add a new benchmark test case, add an entry to `BENCHMARK_CASES` in `test_benchmark_search.py`:

```python
{
    "name": "Your Discipline - Topic",
    "title": "Your Paper Title",
    "abstract": "Your paper abstract (realistic, 100+ words)...",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "expected_discipline": "discipline_name",  # Must match discipline detection
    "expected_journals_contain": [
        "Expected Journal 1",
        "Expected Journal 2",
        "Expected Journal 3",
    ],
    "min_results": 5,
}
```

## Interpreting Failures

### Common Failure Reasons

1. **Insufficient Results**: Algorithm not returning enough journals
   - Check if the topic is too niche
   - Verify keywords are relevant
   - Consider broadening search terms

2. **Wrong Discipline**: Discipline detection incorrect
   - Check if the abstract/title has clear discipline indicators
   - Review discipline keywords in `openalex_service.py`
   - May need to update discipline detection logic

3. **Missing Expected Journals**: Expected journals not appearing
   - Verify journal names are correct (check OpenAlex)
   - Journal might not have recent publications in this area
   - Consider if expected journals are too specific
   - Check if scoring algorithm is favoring different journals

4. **Low Relevance Score**: Few expected journals found
   - Expected journals might be too restrictive
   - Algorithm might be finding better alternatives
   - Review actual results to see if they're still high quality

## Best Practices

1. **Use Realistic Test Cases**: Base test cases on actual research papers
2. **Expected Journals**: Include a mix of top-tier and specialized journals
3. **Flexible Expectations**: Don't make expected journal lists too restrictive
4. **Run Regularly**: Run benchmarks after algorithm changes
5. **Monitor Trends**: Track pass rates over time to detect regressions

## Integration with CI/CD

To run benchmarks in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Benchmark Tests
  run: |
    cd backend
    pytest tests/test_benchmark_search.py -v -m benchmark --junit-xml=benchmark-results.xml
```

## Troubleshooting

### Tests Timing Out
- Increase `MAX_EXECUTION_TIME` in `test_benchmark_execution_time()`
- Check OpenAlex API rate limits
- Verify network connectivity

### Inconsistent Results
- OpenAlex data changes over time
- New publications affect journal rankings
- Update expected journals periodically

### Module Import Errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Run from correct directory

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Project development guide
- [test_openalex_live.py](./test_openalex_live.py) - Live API integration tests
- [test_search.py](./test_search.py) - Unit tests for search functionality

## Maintenance

- **Update Frequency**: Review and update test cases quarterly
- **Expected Journals**: Verify expected journals still publish in these areas
- **Threshold Tuning**: Adjust pass rate thresholds based on algorithm improvements
- **Performance Baselines**: Update execution time limits as API performance changes
