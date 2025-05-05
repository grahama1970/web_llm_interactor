from bs4 import BeautifulSoup
import json
import sys
import re
from loguru import logger
from file_utils import load_text_file
from json_utils import clean_json_string


# Configure loguru to ignore warnings (set level to INFO or higher)
# log_level = "ERROR"
logger.remove()
logger.add(
    sys.stdout,
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
                    # logger.warning("Failed to parse JSON from script tag content")
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
                    # logger.warning(f"Failed to parse JSON from {attr} attribute")
                    continue

    # 3. Extract JSON from text content of all elements
    json_pattern = r"\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
    all_elements = soup.find_all(string=True)
    logger.debug(f"Found {len(all_elements)} text elements with potential JSON")
    for element in all_elements:
        text = element.strip()
        if text:
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
                    # logger.warning("Failed to parse JSON from text content")
                    continue

    logger.info(
        f"Extracted {len(json_objects)} valid JSON objects with required fields"
    )
    return json_objects


# Example usage
if __name__ == "__main__":

    html_doc = """
    <html>
    <body>
        <script>
            var data = {"name": "John", "age": 30};
            var settings = {"theme": "dark", "lang": "en"};
        </script>
        <div data-info='{"id": 123, "type": "user"}'></div>
        <p data-spm-anchor-id="a2ty_o01.29997173.0.i0.1ac9c921IgxNEp">{
          "question": "What is the capital of Oklahoma?",
          "thinking": "Oklahoma's capital was originally Guthrie until 1910, when it was moved to Oklahoma City. Oklahoma City has been the capital since then and remains so today.",
          "answer": "Oklahoma City"
        } </p>
        <p data-spm-anchor-id="invalid">{
          "question": "",
          "thinking": "Some thought",
          "answer": "Some answer"
        } </p>
    </body>
    </html>
    """
    # Read HTML file
    file_path = "qwen_response_final.html"
    html_content = load_text_file(file_path)
    
    if html_content is None:
        # logger.warning(f"Failed to load file, using hardcoded HTML instead")
        html_content = html_doc
    logger.info(
        f"Reading HTML from {file_path if load_text_file(file_path) else 'hardcoded string'}"
    )

    json_data = extract_json_from_html(html_content)
    for item in json_data:
        print(item)

    # Example with custom fields
    custom_fields = ["question", "thinking", "answer"]
    json_data_custom = extract_json_from_html(html_content, custom_fields)
    # for item in json_data_custom:
    #     print(item)
