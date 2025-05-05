web_llm_interactor 🤖
A toolkit for automating interactions with web-based Large Language Models (LLMs) like Qwen, Perplexity, and more. This project leverages AppleScript to control a real Chrome browser (bypassing bot detection) and Python to extract structured responses from the resulting HTML.

Why web_llm_interactor? 💡
Many cutting-edge LLMs are only accessible through browser-based interfaces, lacking public or affordable APIs. This restricts programmatic access for agents, scripts, or CLI workflows, unlike models with REST APIs.
web_llm_interactor solves this by enabling seamless interaction with web-based LLMs as if they had API endpoints. It automates browser actions using AppleScript to mimic human behavior, submits queries, waits for responses, and extracts structured data (e.g., JSON) from the page. This makes web-only LLMs fully compatible with your automation workflows.

How It Works ⚙️
graph TD
    A[User/Agent calls AppleScript] --> B[AppleScript activates Chrome, finds correct tab]
    B --> C[AppleScript injects JavaScript to input query and submit]
    C --> D[AppleScript waits for LLM response to stabilize]
    D --> E[AppleScript saves page HTML to file]
    E --> F[AppleScript triggers Python script with HTML path]
    F --> G[Python parses HTML, extracts JSON]
    G --> H[Python outputs JSON to stdout]
    H --> I[AppleScript returns JSON to caller]


Features ✨

Bypass Bot Detection: Uses AppleScript to control a real Chrome browser, mimicking human interactions.
Structured Output: Extracts responses as JSON for easy integration into workflows.
Flexible Queries: Retrieve the latest response or all responses in the chat window.
Lightweight: Minimal dependencies for easy setup and maintenance.


Installation 🛠️

Create a virtual environment:
python3 -m venv .venv
source .venv/bin/activate


Install dependencies:
pip install -r requirements.txt



requirements.txt:
beautifulsoup4
loguru


Note: Add optional dependencies (e.g., pyperclip) if needed for your workflow.


Usage 🚀
AppleScript Automation
Run queries directly via AppleScript to interact with the LLM:

Get the latest response:
osascript src/send_enter_save_source.applescript "What is the capital of Georgia? Return in well-ordered JSON with fields: question, thinking, answer"


Get all responses:
osascript src/send_enter_save_source.applescript "What is the capital of Florida? Return in well-ordered JSON with fields: question, thinking, answer" --all



Python CLI
Extract structured data from saved HTML:

Extract the latest response:
python src/extract_json_from_html.py /path/to/qwen_response_final.html


Extract all responses:
python src/extract_json_from_html.py /path/to/qwen_response_final.html --all



Example: Integrating with an Agent
Call the AppleScript from a Python script or agent and capture the JSON response:
import subprocess

question = "What is the capital of Idaho? Return in well-ordered JSON with fields: question, thinking, answer"
result = subprocess.check_output([
    "osascript", "src/send_enter_save_source.applescript", question
], text=True)
print(result)  # Outputs JSON response from the web LLM

To retrieve all chat responses:
result = subprocess.check_output([
    "osascript", "src/send_enter_save_source.applescript", question, "--all"
], text=True)
print(result)


Why AppleScript Instead of Selenium? 🛡️

Stealth: AppleScript controls a real Chrome browser, making interactions indistinguishable from a human user.
Reliability: Unlike Selenium, which is often detected via browser fingerprinting or navigator.webdriver, this approach works with sites that block bots.
Simplicity: No need for complex browser drivers or additional configurations.


Project Structure 📂
web_llm_interactor/
├── src/
│   ├── send_enter_save_source.applescript  # Browser automation script
│   ├── extract_json_from_html.py          # HTML-to-JSON extractor
│   └── ...
├── README.md
├── requirements.txt


License 📜
MIT License

web_llm_interactor empowers agents and CLI workflows to harness web-only LLMs, delivering API-like functionality with minimal setup. 🌟
