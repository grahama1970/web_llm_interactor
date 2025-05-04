# VALIDATION_REQUIREMENTS
> Critical standards for ensuring correct PDF extraction validation

## Core Validation Principle
**CRITICAL**: Validation must verify ACTUAL RESULTS match EXPECTED RESULTS, not just check for absence of errors!
DO NOT MOCK Core functionality of the script.
For example, if you are testing a database query, DO NOT MOCK THE DATABASE CONNECTION. You can not test a query with a mocked connection. NEVER MOCK CORE FUNCTIONALY. 

## Complete Validation Requirements
Every module's `if __name__ == \"__main__\":` block **MUST** implement:

1. **Reference Data Validation**:
   - Use known, pre-processed sample PDFs with verified output
   - Store expected output as fixtures (JSON files) in `src/test_fixtures/`
   - Match extracted data with fixture data field-by-field, not just structure

2. **Structural Validation**:
   - Verify correct number of sections, tables, elements
   - Validate correct hierarchical relationships
   - Check for required fields presence and correct types

3. **Content Validation**:
   - Compare actual text content against known correct text
   - For tables: verify headers, rows, and cell content matches expected data
   - For structured elements: verify all attributes match expected values

4. **Precise Error Reporting**:
   ```python
   if not validation_passed:
       print("❌ VALIDATION FAILED - Results dont match expected values") 
       print(f"FAILURE DETAILS:")
       for field, details in validation_failures.items():
           print(f"  - {field}: Expected: {details[\"expected\"]}, Got: {details[\"actual\"]}")
       print(f"Total errors: {len(validation_failures)} fields mismatched")
       sys.exit(1)
   ```

## Implementation Example
```python
def validate_extraction(extracted_data, fixture_path):
    """Validate extraction results against known good fixture data."""
    # Load fixture data
    with open(fixture_path, "r") as f:
        expected_data = json.load(f)
    
    # Track all validation failures
    validation_failures = {}
    
    # Structural validation
    if len(extracted_data["sections"]) != len(expected_data["sections"]):
        validation_failures["section_count"] = {
            "expected": len(expected_data["sections"]),
            "actual": len(extracted_data["sections"])
        }
    
    # Content validation (deep comparison)
    for i, (extracted_section, expected_section) in enumerate(
        zip(extracted_data["sections"], expected_data["sections"])
    ):
        # Text content validation
        if extracted_section["text"] != expected_section["text"]:
            validation_failures[f"section_{i}_text"] = {
                "expected": expected_section["text"][:100] + "...",  # Truncate for readability
                "actual": extracted_section["text"][:100] + "..."
            }
        
        # Metadata validation
        for key in expected_section["metadata"]:
            if key not in extracted_section["metadata"]:
                validation_failures[f"section_{i}_metadata_{key}_missing"] = {
                    "expected": expected_section["metadata"][key],
                    "actual": "FIELD MISSING"
                }
            elif extracted_section["metadata"][key] != expected_section["metadata"][key]:
                validation_failures[f"section_{i}_metadata_{key}"] = {
                    "expected": expected_section["metadata"][key],
                    "actual": extracted_section["metadata"][key]
                }
    
    # Table validation
    for i, (extracted_table, expected_table) in enumerate(
        zip(extracted_data["tables"], expected_data["tables"])
    ):
        # Validate table dimensions
        if len(extracted_table["rows"]) != len(expected_table["rows"]):
            validation_failures[f"table_{i}_row_count"] = {
                "expected": len(expected_table["rows"]),
                "actual": len(extracted_table["rows"])
            }
        
        # Validate table content
        for r, (extracted_row, expected_row) in enumerate(
            zip(extracted_table["rows"], expected_table["rows"])
        ):
            for c, (extracted_cell, expected_cell) in enumerate(
                zip(extracted_row, expected_row)
            ):
                if extracted_cell != expected_cell:
                    validation_failures[f"table_{i}_content_r{r}c{c}"] = {
                        "expected": expected_cell,
                        "actual": extracted_cell
                    }
    
    return len(validation_failures) == 0, validation_failures
```

```python
if __name__ == "__main__":
    # Process a known test PDF
    test_pdf_path = "src/input/BHT_CV32A65X.pdf"
    fixture_path = "src/test_fixtures/BHT_CV32A65X_expected.json"
    
    # Extract data
    extracted_data = process_pdf(test_pdf_path)
    
    # Validate results
    validation_passed, validation_failures = validate_extraction(extracted_data, fixture_path)
    
    # Report validation status
    if validation_passed:
        print("✅ VALIDATION COMPLETE - All PDF extraction results match expected values")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED - Results dont match expected values") 
        print(f"FAILURE DETAILS:")
        for field, details in validation_failures.items():
            print(f"  - {field}: Expected: {details[\"expected\"]}, Got: {details[\"actual\"]}")
        print(f"Total errors: {len(validation_failures)} fields mismatched")
        sys.exit(1)
```

## Measuring Extraction Accuracy
When the validation requirements mention "extraction_accuracy", implement a concrete measurement:

1. **Text Extraction Accuracy**:
   - Compare extracted text with ground truth text character by character
   - Calculate: `accuracy = (matching_chars / total_chars) * 100`

2. **Structure Extraction Accuracy**:
   - Compare extracted structure with ground truth structure
   - Calculate: `accuracy = (matching_elements / total_elements) * 100`

3. **Table Extraction Accuracy**:
   - Compare extracted tables with ground truth tables
   - Calculate: `accuracy = (matching_cells / total_cells) * 100`

## Creating Fixtures for Validation
1. Manually verify the PDF extraction output for a representative set of PDFs
2. Save the verified output as JSON fixtures in `src/test_fixtures/`
3. Use these fixtures for validation in all future development

## Important: Never Skip Validation
- Validation is NOT an optional step
- NEVER consider a task complete without thorough validation
- "Runs without errors" is NOT a valid success criterion
- Always verify actual content against expected content

## Addressing Validation Failures
1. Identify the specific fields that failed validation
2. Investigate why the extraction produced different results
3. Fix the extraction logic to correctly handle the problematic cases
4. Re-run validation until ALL fields match expected values