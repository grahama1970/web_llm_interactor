#!/usr/bin/env python3
import json
import sys
import os
import re
from bs4 import BeautifulSoup

def parse_html(html_file):
    """
    Parse HTML and extract question, thinking, and answer.
    
    Simple but effective approach that handles various HTML structures.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # First try: Extract based on the full HTML content using regex
    # This is especially useful for Qwen/Perplexity style responses
    result = extract_by_content_pattern(html_content)
    
    # If that doesn't work, try with BeautifulSoup
    if not any(result.values()):
        soup = BeautifulSoup(html_content, 'html.parser')
        result = extract_by_soup(soup)
    
    return result

def extract_by_content_pattern(html_content):
    """Extract content using regex patterns that match common format"""
    result = {
        'question': '',
        'thinking': '',
        'answer': ''
    }
    
    # Convert HTML to plain text first to simplify pattern matching
    text_content = re.sub(r'<[^>]+>', ' ', html_content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # Find question - looking for user queries
    question_patterns = [
        r'(?:User|Question|Query):\s*([^.!?]+[.!?])',
        r'(?:User|Human)(?:[^:]*):(.+?)(?:Assistant:|AI:|$)',
        r'(?:[Aa]nswer concisely|[Aa]nswer briefly|[Tt]ell me):\s*([^.!?]+[.!?])'
    ]
    
    for pattern in question_patterns:
        match = re.search(pattern, text_content)
        if match:
            result['question'] = match.group(1).strip()
            break
    
    # Find thinking section
    thinking_patterns = [
        r'(?:Thinking|Reasoning|Thought process):\s*(.+?)(?:Answer:|Response:|$)',
        r'<thinking>(.+?)</thinking>'
    ]
    
    for pattern in thinking_patterns:
        match = re.search(pattern, text_content, re.DOTALL | re.IGNORECASE)
        if match:
            result['thinking'] = match.group(1).strip()
            break
    
    # Find answer section
    answer_patterns = [
        r'(?:Answer|Response|Output):\s*(.+?)(?:$|User:|Question:)',
        r'(?:Assistant|AI)(?:[^:]*):(.+?)(?:User:|Human:|$)'
    ]
    
    for pattern in answer_patterns:
        match = re.search(pattern, text_content, re.DOTALL)
        if match:
            result['answer'] = match.group(1).strip()
            break
    
    return result

def extract_by_soup(soup):
    """Extract content using BeautifulSoup to analyze HTML structure"""
    result = {
        'question': '',
        'thinking': '',
        'answer': ''
    }
    
    # Try to find elements by common class names
    for element in soup.find_all(['div', 'p', 'span']):
        text = element.get_text(strip=True)
        if not text:
            continue
            
        # Skip very short texts as they're unlikely to be content
        if len(text) < 10:
            continue
            
        # Check class names if they exist
        class_name = element.get('class', '')
        if class_name:
            class_str = ' '.join(class_name).lower()
            if 'user' in class_str or 'question' in class_str or 'query' in class_str:
                result['question'] = text
            elif 'thinking' in class_str or 'reasoning' in class_str:
                result['thinking'] = text
            elif 'answer' in class_str or 'response' in class_str:
                result['answer'] = text
    
    # If we still don't have all components, try a heuristic approach
    if not result['question'] or not result['answer']:
        all_text_elements = [elem for elem in soup.find_all(['p', 'div']) 
                            if elem.get_text(strip=True)]
        
        if len(all_text_elements) >= 2:
            # Assume first is question, last is answer
            if not result['question']:
                result['question'] = all_text_elements[0].get_text(strip=True)
            if not result['answer']:
                result['answer'] = all_text_elements[-1].get_text(strip=True)
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python html_parser.py <html_file> [output_file]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        print(f"Error: File '{html_file}' not found")
        sys.exit(1)
    
    result = parse_html(html_file)
    
    # If output file is specified, write to it, otherwise print to console
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results written to {output_file}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()