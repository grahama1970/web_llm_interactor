# CLI Test Verification Guide

This document outlines the process for ensuring that CLI functionality remains aligned with automated tests, providing a verification pathway to confirm that passing tests translate to working CLI commands.

## Why CLI Verification is Necessary

While automated tests cover individual components, they may not fully exercise the CLI entry points as a user would experience them. Tests passing does not always guarantee that the CLI works correctly due to:

1. Interface misalignment between CLI arguments and underlying functions
2. Environment differences between test and CLI execution contexts
3. Integration failures that don't appear in isolated component tests
4. Edge cases with real-world inputs

## CLI Verification Checklist

After tests pass, follow this verification checklist to ensure the CLI functionality works correctly:

### 1. Basic CLI Health Check

Run the CLI with help flag to verify it starts correctly:

```bash
python -m complexity.cli --help
```

Expected: Help text displays showing all available commands

### 2. Core Database Connection

Verify database connection without performing operations:

```bash
python -m complexity.cli db-status
```

Expected: Status message showing successful connection to ArangoDB

### 3. Search Functionality Verification

Perform a basic search using each search type:

```bash
# BM25 text search
python -m complexity.cli search keyword "python programming" --limit 3

# Semantic search
python -m complexity.cli search semantic "database concepts" --limit 3

# Hybrid search
python -m complexity.cli search hybrid "graph database implementation" --limit 3

# Tag search
python -m complexity.cli search tags python,database --limit 3
```

Expected: Each command returns relevant search results matching the query

### 4. Embedding Generation Check

Verify embedding generation with a sample text:

```bash
python -m complexity.cli generate-embedding "This is a test sentence to verify embedding generation" --verbose
```

Expected: 1024-dimensional embedding vector (or appropriate dimension based on model)

### 5. Document Operations

Create, retrieve, and delete a test document:

```bash
# Create document
python -m complexity.cli create-document --title "Test Document" --content "This is a test document for CLI verification" --tags "test,verification"

# List documents (retrieve ID of created document)
python -m complexity.cli list-documents --limit 5

# Delete document (use ID from previous step)
python -m complexity.cli delete-document [DOCUMENT_ID]
```

Expected: Document creation confirmation, document appears in list, deletion confirmation

### 6. Import/Export Functionality

Test import and export if applicable:

```bash
# Export a few documents
python -m complexity.cli export-documents --limit 3 --output test_export.json

# Import documents
python -m complexity.cli import-documents --file test_export.json
```

Expected: Export completes successfully, import confirms documents added

### 7. Error Handling Verification

Test error handling with invalid inputs:

```bash
# Invalid search type
python -m complexity.cli search invalid-type "test query"

# Non-existent document ID
python -m complexity.cli get-document non-existent-id-123
```

Expected: Clear error messages that explain the issue

## Automated CLI Verification Script

Create a verification script that runs after tests pass to automatically check CLI functionality:

```bash
#!/bin/bash
# cli_verification.sh
echo "Running CLI verification tests..."

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Array to track failed tests
failed_tests=()

# Function to run test and check result
run_test() {
  local test_name="$1"
  local command="$2"
  local expected_pattern="$3"
  
  echo -n "Testing $test_name... "
  
  # Run command and capture output
  output=$(eval "$command" 2>&1)
  
  # Check if output matches expected pattern
  if echo "$output" | grep -q "$expected_pattern"; then
    echo -e "${GREEN}PASS${NC}"
  else
    echo -e "${RED}FAIL${NC}"
    echo "  Expected pattern: $expected_pattern"
    echo "  Actual output: $output"
    failed_tests+=("$test_name")
  fi
}

# Run verification tests
run_test "help display" "python -m complexity.cli --help" "Usage:"
run_test "database connection" "python -m complexity.cli db-status" "Connected"
run_test "keyword search" "python -m complexity.cli search keyword 'python programming' --limit 3" "results"
run_test "semantic search" "python -m complexity.cli search semantic 'database concepts' --limit 3" "results"
run_test "hybrid search" "python -m complexity.cli search hybrid 'graph database' --limit 3" "results"
run_test "tag search" "python -m complexity.cli search tags python,database --limit 3" "results"
run_test "embedding generation" "python -m complexity.cli generate-embedding 'Test sentence' --verbose" "embedding"

# Report results
if [ ${#failed_tests[@]} -eq 0 ]; then
  echo -e "\n${GREEN}All CLI verification tests passed!${NC}"
  exit 0
else
  echo -e "\n${RED}Some CLI verification tests failed:${NC}"
  for test in "${failed_tests[@]}"; do
    echo "  - $test"
  done
  exit 1
fi
```

## Integration with CI/CD

Add CLI verification to your CI/CD pipeline to ensure CLI functionality always works:

```yaml
# Example CI/CD step
test_and_verify:
  script:
    - python -m pytest tests/
    - bash scripts/cli_verification.sh
```

## Troubleshooting Common CLI Issues

When CLI verification fails but tests pass, check for:

1. **Environment Variables**: Ensure CLI and tests use the same environment variables, especially for database connection
2. **Command Line Argument Parsing**: Check CLI argument parsing for regression
3. **Embedding Configuration**: Verify CLI uses the same embedding model and dimensions as tests
4. **Database Structure**: Ensure CLI expects the same database schema as tests

## Ensuring Test and CLI Alignment

To maintain alignment between tests and CLI:

1. Create CLI-specific test fixtures that mirror real-world usage patterns
2. Include CLI integration tests that invoke the CLI directly with subprocess
3. Document all CLI changes in both code and user documentation
4. Version CLI commands and alert users to breaking changes
5. Generate CLI help text from the same source that defines test expectations