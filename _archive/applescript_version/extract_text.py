#!/usr/bin/env python3
import sys
import re
import json
from bs4 import BeautifulSoup
import html2text

def extract_with_bs4(html_file):
    """Extract text using BeautifulSoup with minimal formatting"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Extract text
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up the text
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_with_html2text(html_file):
    """Convert HTML to markdown using html2text"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = False
    h.ignore_emphasis = True
    h.body_width = 0  # No wrapping
    
    text = h.handle(html_content)
    return text

# Remove the other extraction methods that have dependency issues

def find_json_in_text(text):
    """Try to find JSON structures in the text"""
    # Try to find JSON-like structures
    json_patterns = [
        r'({[\s\S]*?"question"[\s\S]*?"thinking"[\s\S]*?"answer"[\s\S]*?})',
        r'({[\s\S]*?"answer"[\s\S]*?"thinking"[\s\S]*?"question"[\s\S]*?})',
        r'({[\s\S]*?"response"[\s\S]*?})',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <html_file> [method]")
        print("Methods: bs4, html2text, all (default)")
        sys.exit(1)
    
    html_file = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    methods = {
        "bs4": extract_with_bs4,
        "html2text": extract_with_html2text
    }
    
    if method == "all":
        for name, extractor in methods.items():
            print(f"\n===== {name} =====")
            try:
                text = extractor(html_file)
                print(f"Extracted {len(text)} characters")
                
                # Look for common patterns that might indicate the answer
                if "What is the capital of Rhode Island" in text:
                    print("\nFound question about Rhode Island capital!")
                    
                if "Providence" in text:
                    print("Found mention of Providence!")
                    
                # Try to find JSON
                json_matches = find_json_in_text(text)
                if json_matches:
                    print(f"\nFound {len(json_matches)} potential JSON matches!")
                    for i, match in enumerate(json_matches[:2]):  # Show first 2
                        print(f"Match {i+1}:\n{match[:200]}...")
                        try:
                            # Try to parse as JSON
                            json_obj = json.loads(match)
                            print("Valid JSON!")
                            print(json.dumps(json_obj, indent=2))
                        except json.JSONDecodeError:
                            print("Not valid JSON")
                
                # Find patterns that look like answers
                answer_pattern = r'The capital of Rhode Island is ([A-Za-z]+)'
                answer_matches = re.findall(answer_pattern, text)
                if answer_matches:
                    print(f"\nFound answer: The capital of Rhode Island is {answer_matches[0]}")
                
                # Save the output to a file
                output_file = f"{html_file}_{name}_output.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Full text written to {output_file}")
                
            except Exception as e:
                print(f"Error with {name}: {str(e)}")
    else:
        if method not in methods:
            print(f"Unknown method: {method}")
            print(f"Available methods: {', '.join(methods.keys())}")
            sys.exit(1)
        
        text = methods[method](html_file)
        print(f"Extracted {len(text)} characters")
        
        # Try to find JSON
        json_matches = find_json_in_text(text)
        if json_matches:
            print(f"\nFound {len(json_matches)} potential JSON matches!")
            for i, match in enumerate(json_matches):
                print(f"Match {i+1}:\n{match[:200]}..." if len(match) > 200 else f"Match {i+1}:\n{match}")
                try:
                    # Try to parse as JSON
                    json_obj = json.loads(match)
                    print("Valid JSON!")
                    print(json.dumps(json_obj, indent=2))
                except json.JSONDecodeError:
                    print("Not valid JSON")
        
        # Find patterns that look like answers
        answer_pattern = r'The capital of Rhode Island is ([A-Za-z]+)'
        answer_matches = re.findall(answer_pattern, text)
        if answer_matches:
            print(f"\nFound answer: The capital of Rhode Island is {answer_matches[0]}")
        
        # Save the output to a file
        output_file = f"{html_file}_{method}_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Full text written to {output_file}")