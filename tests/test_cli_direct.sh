#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Web LLM Interactor Direct CLI Test ===${NC}"
echo -e "${YELLOW}This script directly tests the CLI with Qwen.ai${NC}\n"

# Check if Chrome is running
if ! pgrep -x "Google Chrome" > /dev/null; then
  echo -e "${RED}Error: Google Chrome must be running.${NC}"
  echo -e "Please open Chrome with a tab to https://chat.qwen.ai/ before running this test."
  exit 1
fi

# Set PYTHONPATH to include project root
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd):$PYTHONPATH"

# Test simple question
echo -e "${CYAN}=== Testing Basic Question ===${NC}"
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"What is the capital of Oregon?\" --timeout 45${NC}"
read -p "Press Enter to execute..." 
python -m web_llm_interactor.cli ask "What is the capital of Oregon?" --timeout 45

# Test with custom fields
echo -e "\n${CYAN}=== Testing Custom Fields ===${NC}"
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"What is the tallest mountain in Oregon?\" --fields \"question,answer\" --timeout 45${NC}"
read -p "Press Enter to execute..." 
python -m web_llm_interactor.cli ask "What is the tallest mountain in Oregon?" --fields "question,answer" --timeout 45

# Test with no JSON format
echo -e "\n${CYAN}=== Testing No JSON Format ===${NC}"
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"Describe Oregon briefly\" --no-json-format --timeout 45${NC}"
read -p "Press Enter to execute..." 
python -m web_llm_interactor.cli ask "Describe Oregon briefly" --no-json-format --timeout 45