# CLAUDE_TEST_REQUIREMENTS
> Critical standards for ensuring Claude creates useful, valid tests

## The Problem with Claude-Generated Tests

Claude has a tendency to create tests that:
1. Mock core functionality instead of testing actual implementations
2. Create overly complex fixtures that don't test actual behavior
3. Make incorrect assumptions about APIs instead of reading actual code
4. Pass without validating actual results (false positives)
5. Focus on implementation details rather than behavior verification
6. Include meaningless assertions that always pass

## Required Test Approach for Claude

1. **Read Before Writing**: ALWAYS read the actual implementation code before writing tests
   - Understand the real API, not what you think it should be
   - Map the public interfaces correctly
   - Verify return types and parameter requirements

2. **Test Real Functionality**: NEVER mock core components
   - Process actual files or repositories, not fake data
   - Use real repositories like `python-arango` or `minimal-readme` for tests
   - Write tests that would fail if the underlying functionality breaks

3. **Test Simple Cases First**: Always start with the simplest passing test case
   - Write one basic test that works, then expand
   - Verify the test actually fails when it should
   - Document expected output with concrete, real-world examples

4. **Focus on Behavior, Not Implementation**: Test what code does, not how it does it
   - Does it produce the expected output given specific inputs?
   - Does it handle error cases appropriately?
   - Does it correctly integrate with other components?

5. **Use Simple Fixtures**: Fixtures should be minimal and focused
   - Small, readable samples of actual data
   - Documented purpose for each fixture
   - Store fixtures separately from test code

6. **Verify Actual Results**: ALWAYS compare actual results with expected results
   - Have concrete expected outputs for each test
   - Line-by-line verification of critical fields
   - Explicit error messages when verification fails

## Test Structure Requirements

Every test module MUST include:

1. **Test Setup**:
   ```python
   def setup_test_environment():
       """Set up any required test environment."""
       # Use actual repositories, files, or data
       # Return resources required for testing
   ```

2. **Direct Functionality Tests**:
   ```python
   def test_actual_function_with_real_data():
       """Test specific function with real data."""
       # 1. Arrange - prepare actual data
       real_data = get_real_test_data()
       
       # 2. Act - call the actual function (no mocking)
       result = function_to_test(real_data)
       
       # 3. Assert - verify expected output (specific fields)
       assert result["specific_field"] == expected_value
       # Add more specific assertions
   ```

3. **Error Handling Tests**:
   ```python
   def test_error_handling_with_actual_errors():
       """Test error handling with real error scenarios."""
       # Use corrupted but realistic input
       bad_data = get_bad_test_data()
       
       # Verify it handles errors appropriately
       result = function_to_test(bad_data)
       assert "error" in result
       assert result["error"] == expected_error_message
   ```

4. **Integration Verification**:
   ```python
   def test_component_interaction():
       """Test how components interact together."""
       # Test with real components, not mocks
       result = integrated_function(real_data)
       assert result["component1_output"] == expected_1
       assert result["component2_output"] == expected_2
   ```

5. **Verification Recap**:
   ```python
   def recap_test_verification():
       """Summarize test verification status."""
       # Run actual validation checks
       validation_result = validate_all_test_results()
       # Print detailed pass/fail information
       for test, status in validation_result.items():
           print(f"{test}: {'PASS' if status else 'FAIL'}")
   ```

## Concrete Examples Over Abstractions

Bad:
```python
def test_processing():
    """Test processing some abstract data."""
    # This test doesn't test anything real
    mock_data = {"mock": "data"}
    assert process_data(mock_data) is not None  # Meaningless
```

Good:
```python
def test_markdown_extraction_from_python_arango_readme():
    """Test actual markdown extraction from python-arango README."""
    # Clone specific file from actual repository
    readme_path = clone_file("https://github.com/arangodb/python-arango", "README.md")
    
    # Process real file
    sections = parse_markdown(readme_path)
    
    # Verify specific expected content from the real file
    assert len(sections) >= 10  # Actual expected number
    assert sections[0]["section_title"] == "Python-Arango"
    assert "pip install python-arango" in sections[2]["content"]
```

## IMPORTANT: No Meaningless Assertions

NEVER write tests with assertions that will always pass, such as:
- `assert len(result) > 0` when you don't know what's in the result
- `assert isinstance(result, dict)` without checking contents
- `assert function_call() is not None` without checking return value

INSTEAD, write assertions that verify SPECIFIC expected values:
- `assert result["exact_key"] == "exact expected value"`
- `assert len(result["items"]) == 15`  # The actual expected number
- `assert "Connection error" in str(exception)`

## Final Test Requirements

1. Tests MUST run against ACTUAL functionality
2. Tests MUST use REAL data examples
3. Tests MUST verify SPECIFIC expected outputs
4. Tests MUST include meaningful assertions
5. Tests MUST document what is being tested and why
6. Tests MUST FAIL when the functionality breaks

PROHIBITED:
1. DO NOT write tests that mock core functionality
2. DO NOT write tests with always-passing assertions
3. DO NOT assume API structure without reading code
4. DO NOT create tests that can't fail when code breaks