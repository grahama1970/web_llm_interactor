from bs4 import BeautifulSoup
import json
import sys
import re
from loguru import logger
from web_llm_interactor.file_utils import load_text_file
from web_llm_interactor.json_utils import clean_json_string
import typer

app = typer.Typer()

# Configure loguru to ignore warnings (set level to INFO or higher)
logger.remove()
logger.add(
    sys.stderr,  # Send logs to stderr so stdout is clean for JSON
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    filter=lambda record: record["extra"].get("name") not in ["httpx", "websockets"]
    and record["name"] != "json_utils",
    backtrace=False,
    diagnose=False,
    colorize=True,
)


def is_valid_json_obj(json_obj, required_fields=["question", "thinking", "answer"]):
    """Check if the JSON object has non-empty fields specified in required_fields."""
    return (
        isinstance(json_obj, dict)
        and all(field in json_obj for field in required_fields)
        and all(
            json_obj[field] and isinstance(json_obj[field], str)
            for field in required_fields
        )
    )


def extract_json_from_html(
    html_content, required_fields=["question", "thinking", "answer"]
):
    # Parse the HTML content
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        logger.debug(f"Parsed HTML content ({len(html_content)} bytes)")
    except Exception as e:
        logger.error(f"Failed to parse HTML content: {str(e)}")
        return []

    # List to store all found JSON objects
    json_objects = []

    # Special case for Qwen.ai: Look specifically for code blocks that might contain JSON
    pre_code_blocks = soup.find_all("pre")
    logger.debug(f"Found {len(pre_code_blocks)} pre blocks")
    for pre in pre_code_blocks:
        code = pre.find("code")
        if code and code.string:
            text = code.string.strip()
            if "{" in text and "}" in text:
                try:
                    json_obj = clean_json_string(text, return_dict=True)
                    if json_obj != {} and is_valid_json_obj(json_obj, required_fields):
                        json_objects.append(json_obj)
                        logger.debug("Extracted valid JSON from code block")
                        # Return immediately if we find it in a code block since this is most likely
                        # the intended JSON in the Qwen.ai context
                        return json_objects
                except json.JSONDecodeError:
                    logger.debug("Failed to parse JSON from code block")

    # If no JSON found in code blocks, try the following methods:
    
    # 1. Extract JSON from <script> tags
    script_tags = soup.find_all("script")
    logger.debug(f"Found {len(script_tags)} script tags")
    for script in script_tags:
        script_content = script.string
        if script_content:
            # Look for JSON-like patterns
            json_pattern = r"\{.*?\}(?=\s*;)|\{.*?\}(?=\s*<)|\{.*?\}(?=\s*\))"
            matches = re.finditer(json_pattern, script_content, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group()
                    json_obj = clean_json_string(json_str, return_dict=True)
                    if json_obj != {} and is_valid_json_obj(json_obj, required_fields):
                        json_objects.append(json_obj)
                        logger.debug("Extracted valid JSON from script tag")
                    else:
                        logger.debug(
                            "JSON from script tag lacks required fields or has empty values"
                        )
                except json.JSONDecodeError:
                    continue

    # 2. Extract JSON from inline attributes (e.g., data- attributes)
    elements_with_data = soup.find_all(
        lambda tag: any(attr.startswith("data-") for attr in tag.attrs.keys())
    )
    logger.debug(f"Found {len(elements_with_data)} elements with data- attributes")
    for element in elements_with_data:
        for attr, value in element.attrs.items():
            if attr.startswith("data-"):
                try:
                    json_obj = clean_json_string(value, return_dict=True)
                    if json_obj != {} and is_valid_json_obj(json_obj, required_fields):
                        json_objects.append(json_obj)
                        logger.debug(f"Extracted valid JSON from {attr} attribute")
                    else:
                        logger.debug(
                            f"JSON from {attr} attribute lacks required fields or has empty values"
                        )
                except (json.JSONDecodeError, TypeError):
                    continue

    # 3. Extract JSON from text content of all elements - more aggressive pattern matching
    json_pattern = r"\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
    all_elements = soup.find_all(string=True)
    logger.debug(f"Found {len(all_elements)} text elements with potential JSON")
    
    # First look for elements that might contain all required fields
    for element in all_elements:
        text = element.strip()
        has_all_fields = all(field in text for field in required_fields)
        if has_all_fields:
            matches = re.finditer(json_pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group()
                    json_obj = clean_json_string(json_str, return_dict=True)
                    if json_obj != {} and is_valid_json_obj(json_obj, required_fields):
                        json_objects.append(json_obj)
                        logger.debug("Extracted valid JSON from text content with all fields")
                except json.JSONDecodeError:
                    continue
    
    # If we didn't find any JSON with all fields, try all elements
    if not json_objects:
        for element in all_elements:
            text = element.strip()
            if text and "{" in text and "}" in text:
                matches = re.finditer(json_pattern, text, re.DOTALL)
                for match in matches:
                    try:
                        json_str = match.group()
                        json_obj = clean_json_string(json_str, return_dict=True)
                        if json_obj != {} and is_valid_json_obj(json_obj, required_fields):
                            json_objects.append(json_obj)
                            logger.debug("Extracted valid JSON from text content")
                        else:
                            logger.debug(
                                "JSON from text content lacks required fields or has empty values"
                            )
                    except json.JSONDecodeError:
                        continue

    # If we still have no JSON, attempt to construct one from the page content
    if not json_objects:
        try:
            # Look for specific elements that might contain question/thinking/answer content
            thinking_section = soup.find(class_="thinking")
            markdown_content = soup.find(class_="markdown-content-container")
            user_message = soup.find(class_="user-message")
            
            if thinking_section and markdown_content:
                question_text = user_message.get_text().strip() if user_message else "Unknown question"
                thinking_text = thinking_section.get_text().strip()
                answer_text = markdown_content.get_text().strip()
                
                # Only pursue this if we have some content in each field
                if thinking_text and answer_text:
                    constructed_json = {
                        "question": question_text,
                        "thinking": thinking_text,
                        "answer": answer_text
                    }
                    
                    if is_valid_json_obj(constructed_json, required_fields):
                        json_objects.append(constructed_json)
                        logger.debug("Constructed valid JSON from page elements")
        except Exception as e:
            logger.debug(f"Failed to construct JSON from page elements: {e}")

    logger.info(
        f"Extracted {len(json_objects)} valid JSON objects with required fields"
    )
    return json_objects


@app.command()
def main(
    html_file: str = typer.Argument(..., help="Path to HTML file"),
    all: bool = typer.Option(
        False, "--all", "-all", help="Return all JSON objects, not just the last one"
    ),
    fields: str = typer.Option(
        "question,thinking,answer", "--fields", help="Comma-separated list of required fields"
    ),
):
    """
    Extract JSON objects from an HTML file.
    """
    html_content = load_text_file(html_file)
    if html_content is None:
        print("{}")
        raise typer.Exit(1)

    # Parse the comma-separated fields into a list
    required_fields = [field.strip() for field in fields.split(",")]
    logger.info(f"Using required fields: {required_fields}")
    
    json_data_custom = extract_json_from_html(html_content, required_fields)

    if all:
        print(json.dumps(json_data_custom, indent=2, ensure_ascii=False))
    else:
        if json_data_custom:
            print(json.dumps(json_data_custom[-1], indent=2, ensure_ascii=False))
        else:
            print("{}")


if __name__ == "__main__":
    app()
