#!/usr/bin/env python3
import json
import sys
import os
import re
from bs4 import BeautifulSoup
import requests

def preprocess_html(html_content):
    """
    Preprocess HTML to remove unnecessary elements and simplify structure
    for better LLM parsing.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove all script tags and their contents
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove all style tags and their contents
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove navigation, header, footer and other non-content elements
    for tag in soup.select('nav, header, footer, iframe, button, meta, link, noscript, svg'):
        tag.decompose()
    
    # Remove elements with classes/ids that typically contain UI elements or JavaScript
    for tag in soup.find_all(lambda tag: tag.has_attr('class') or tag.has_attr('id')):
        if tag.has_attr('class') and any(word in ' '.join(tag.get('class', [])).lower() 
                                   for word in ['nav', 'menu', 'footer', 'header', 'sidebar', 'widget', 'banner', 'ad-']):
            tag.decompose()
        elif tag.has_attr('id') and any(word in tag.get('id', '').lower() 
                                 for word in ['nav', 'menu', 'footer', 'header', 'sidebar', 'widget', 'banner', 'ad-']):
            tag.decompose()
    
    # Get rid of all onclick, onload and other event attributes
    for tag in soup.find_all(True):
        attrs_to_remove = []
        for attr in tag.attrs:
            if attr.startswith('on') or attr in ['href', 'src'] and tag.name not in ['img', 'a']:
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            del tag[attr]
    
    # Try to identify the main content area
    main_content = None
    
    # Look for elements with content-related classes/ids
    content_elements = soup.select('main, article, .content, .main, #content, .article, .post, .message, .question, .answer')
    
    if content_elements:
        # Look for elements that likely contain Q&A content
        qa_elements = [el for el in content_elements if ('question' in str(el.get('class', '')).lower() or 
                                                        'answer' in str(el.get('class', '')).lower() or
                                                        'message' in str(el.get('class', '')).lower() or
                                                        'query' in str(el.get('class', '')).lower() or
                                                        'response' in str(el.get('class', '')).lower())]
        
        if qa_elements:
            # Find the nearest common parent of Q&A elements
            main_content = qa_elements[0].parent
        else:
            # Otherwise use the first content element that has substantial text
            for element in content_elements:
                if len(element.get_text(strip=True)) > 100:
                    main_content = element
                    break
            
            # If still no match, use the first content element
            if not main_content and content_elements:
                main_content = content_elements[0]
    
    # If we found a main content area, use it
    if main_content:
        clean_html = str(main_content)
    else:
        # Fallback to body if no content containers found
        clean_html = str(soup.body) if soup.body else str(soup)
    
    # Extract plain text from HTML with minimal formatting
    text_content = []
    for tag in BeautifulSoup(clean_html, 'html.parser').find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'pre']):
        if tag.name == 'pre':
            # Preserve code blocks
            text_content.append("<pre>" + tag.get_text(strip=True) + "</pre>")
        else:
            text = tag.get_text(strip=True)
            if text and len(text) > 5:  # Skip very short text fragments
                text_content.append(text)
    
    return "\n\n".join(text_content)

def extract_with_llm(processed_html, api_key=None, model="text-davinci-003"):
    """
    Use OpenAI's API to extract structured data from HTML.
    Falls back to a local extraction method if API key is not provided.
    """
    if not api_key:
        # Fallback to non-LLM extraction
        return extract_with_heuristics(processed_html)
    
    # Truncate HTML if it's too long
    if len(processed_html) > 4000:
        # Keep the first and last parts which typically contain the Q&A
        processed_html = processed_html[:2000] + "\n...[content truncated]...\n" + processed_html[-2000:]
    
    prompt = f"""
    Extract the following information from this HTML content:
    1. The question or query (typically what the user asked)
    2. Any thinking or reasoning process (if present)
    3. The final answer or response
    
    Return ONLY a JSON object with these keys: "question", "thinking", "answer".
    If any part is not found, use an empty string for that field.
    
    HTML Content:
    {processed_html}
    """
    
    try:
        # Call OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.1
            }
        )
        
        if response.status_code == 200:
            response_json = response.json()
            extracted_text = response_json['choices'][0]['text'].strip()
            
            # Parse the JSON response
            try:
                result = json.loads(extracted_text)
                # Ensure we have all expected keys
                for key in ['question', 'thinking', 'answer']:
                    if key not in result:
                        result[key] = ""
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract using regex
                return extract_with_heuristics(extracted_text)
        
    except Exception as e:
        print(f"Error using LLM API: {e}")
    
    # Fallback to heuristic extraction
    return extract_with_heuristics(processed_html)

def extract_with_heuristics(html_content):
    """Fallback method using regex patterns and heuristics"""
    # Convert HTML to plain text
    text_content = re.sub(r'<[^>]+>', ' ', html_content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    result = {
        'question': '',
        'thinking': '',
        'answer': ''
    }
    
    # Extract question
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
    
    # Extract thinking section
    thinking_patterns = [
        r'(?:Thinking|Reasoning|Thought process):\s*(.+?)(?:Answer:|Response:|$)',
        r'<thinking>(.+?)</thinking>'
    ]
    
    for pattern in thinking_patterns:
        match = re.search(pattern, text_content, re.DOTALL | re.IGNORECASE)
        if match:
            result['thinking'] = match.group(1).strip()
            break
    
    # Extract answer section
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

def parse_html_with_llm(html_file, api_key=None):
    """
    Main function to parse HTML file with LLM assistance.
    
    Args:
        html_file: Path to the HTML file
        api_key: OpenAI API key (optional)
        
    Returns:
        dict: Extracted question, thinking, and answer
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Preprocess HTML to remove unnecessary elements
    processed_html = preprocess_html(html_content)
    
    # Extract structured data using LLM or fallback method
    result = extract_with_llm(processed_html, api_key)
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python llm_html_parser.py <html_file> [output_file] [api_key]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        print(f"Error: File '{html_file}' not found")
        sys.exit(1)
    
    # Get API key from args or environment variable
    api_key = None
    if len(sys.argv) > 3:
        api_key = sys.argv[3]
    else:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    result = parse_html_with_llm(html_file, api_key)
    
    # Output to file if specified, otherwise print to console
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results written to {output_file}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()