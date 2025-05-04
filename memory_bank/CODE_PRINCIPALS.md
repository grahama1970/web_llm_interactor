# CODE DETAILS
> Comprehensive code standards for PDF extraction

## Execution Standards
- Always use uv for package management; never pip
- Run Python scripts with: `uv run script.py`
- For environment variables, always use the `env` command:
  ```sh
  env VAR_NAME="value" uv run command
  ```

## Validation Requirements
**Every PDF extractor function must validate results:**

```python
# 1. Define expected outputs
EXPECTED_RESULTS = {
  "expected_sections": 2,
  "expected_tables": 1,
  "expected_properties": {"extraction_accuracy": 95.0}
}

# 2. Compare actual results
assert len(extracted_sections) == EXPECTED_RESULTS["expected_sections"]
assert len(extracted_tables) == EXPECTED_RESULTS["expected_tables"]
assert extraction_accuracy >= EXPECTED_RESULTS["expected_properties"]["extraction_accuracy"]

# 3. Report validation status
if validation_passed:
  print("✅ VALIDATION COMPLETE - All PDF extraction results match expected values")
  sys.exit(0)
else:
  print("❌ VALIDATION FAILED - PDF extraction results don't match expected values") 
  print(f"Expected: {expected}, Got: {actual}")
  sys.exit(1)
```

## Module Structure Requirements
- **Documentation**: Every extractor module must include purpose and sample PDFs
- **Size**: No module should exceed 500 lines
- **Validation**: Every module must test against sample PDFs in src/input

## Error Handling for PDFs
1. Handle malformed PDFs gracefully
2. Follow systematic debugging approach:
   - Review PDF structure
   - Test with simpler PDFs
   - Analyze extraction patterns
   - Implement robust fallbacks

## Async Recursive Workflows Debugging
When building or debugging async recursive workflows:
- Add deep contextual logging
- Propagate error messages explicitly
- Never rely solely on inner function error handling
- Refactor orchestration layer if needed
- Ensure failures are observable, diagnosable, fixable

## Lesson Logging Management
- Add concise lesson entries to ArangoDB for novel techniques/patterns
- Use CLI script: `src/mcp_doc_retriever/lessons_cli.py add`
- Required fields: role, problem, solution, tags
- Environment variables: ARANGO_HOST, ARANGO_USER, ARANGO_PASSWORD, ARANGO_DB
- Lesson updates must be done directly in ArangoDB; CLI updates not supported

## Package Management
- Using the right packages is more important than writing clever code
- Follow 95/5 rule: 95% package functionality, 5% customization
- Follow code reuse enforcement policy:
  - Required sources: python: ["pypi", "internal-utils>=2.3"]
  - Check order: organization_registry → public_registry → approved_vendors
  - Security requirements: vulnerability scanning with max CVE age of 30 days

## Dependency Requirements
- Include version constraints (e.g., Pandas==2.1.3)
- Validate licenses using `license_checker` tool
- For custom code (>50 lines):
  - Create `reuse_exception.md` with cost-benefit analysis
  - Obtain Architect approval

## Static Analysis Priorities
- Prioritize creating functional code before addressing Pylance errors
- Verify code produces expected results before focusing on type annotations
- Do not obsess over static analysis warnings if code functions correctly
- Address runtime issues before improving static type checking

## Package Research Requirements
> Implements the Up-to-date Package Research principle from CODING_PRINCIPLES.md

- **CRITICAL**: Always use perplexity to research packages before adding them
- Do NOT rely on model training data which may be outdated
- Research queries should include:
  - "Latest version of [package_name]"
  - "[package_name] vs alternatives for [specific task]"
  - "[package_name] known issues 2025"
  - "[package_name] integration with [other project components]"
- Document your package selection reasoning based on current research
- Include links to current documentation in code comments