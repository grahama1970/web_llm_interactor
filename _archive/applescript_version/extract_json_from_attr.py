#!/usr/bin/env python3
import sys
import re
import json
from bs4 import BeautifulSoup

def extract_json_from_data_attr(html_file):
    """
    Extract JSON content from specific data attributes in HTML
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Try to find JSON pattern in data-spm-anchor-id attribute
    json_pattern = r'data-spm-anchor-id="[^"]*">({[\s\S]*?"question"[\s\S]*?"thinking"[\s\S]*?"answer"[\s\S]*?})'
    matches = re.findall(json_pattern, html_content)
    
    if matches:
        for match in matches:
            try:
                # Try to parse as JSON
                json_obj = json.loads(match)
                if isinstance(json_obj, dict) and "question" in json_obj and "thinking" in json_obj and "answer" in json_obj:
                    return json_obj
            except json.JSONDecodeError:
                pass
    
    # Try extracting from any attribute that might contain JSON
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all():
        for attr_name, attr_value in tag.attrs.items():
            if isinstance(attr_value, str) and '{' in attr_value and '}' in attr_value:
                # Look for JSON-like structures in attribute values
                json_matches = re.findall(r'({[\s\S]*?"question"[\s\S]*?"thinking"[\s\S]*?"answer"[\s\S]*?})', attr_value)
                for j_match in json_matches:
                    try:
                        json_obj = json.loads(j_match)
                        if isinstance(json_obj, dict) and "question" in json_obj and "thinking" in json_obj and "answer" in json_obj:
                            return json_obj
                    except json.JSONDecodeError:
                        pass
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_json_from_attr.py <html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    json_data = extract_json_from_data_attr(html_file)
    
    if json_data:
        print("Found JSON in HTML attribute:")
        print(json.dumps(json_data, indent=2))
    else:
        print("No JSON found in HTML attributes with question/thinking/answer structure.")