#!/usr/bin/env python3
import sys
import re
import json

def extract_embedded_json(file_path):
    """
    Extract JSON structure that's embedded within the response text
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for embedded JSON with our expected structure
    json_pattern = r'({[\s\S]*?"question"[\s\S]*?"thinking"[\s\S]*?"answer"[\s\S]*?})'
    matches = re.findall(json_pattern, content)
    
    for match in matches:
        try:
            # Try to parse as JSON
            json_obj = json.loads(match)
            # Validate it has our expected keys
            if "question" in json_obj and "thinking" in json_obj and "answer" in json_obj:
                return json_obj
        except json.JSONDecodeError:
            # Sometimes the JSON might have extra characters. Try a more cleaned version
            clean_match = re.sub(r'([^{]*{)', '{', match)  # Remove anything before the first {
            clean_match = re.sub(r'(}[^}]*)', '}', clean_match)  # Remove anything after the last }
            try:
                json_obj = json.loads(clean_match)
                if "question" in json_obj and "thinking" in json_obj and "answer" in json_obj:
                    return json_obj
            except:
                continue
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_embedded_json.py <file_path> [output_file]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Extract JSON
    json_obj = extract_embedded_json(file_path)
    
    if json_obj:
        # Output JSON
        json_output = json.dumps(json_obj, indent=2)
        print(json_output)
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"\nOutput written to {output_file}")
    else:
        print("No embedded JSON with question/thinking/answer structure found.")