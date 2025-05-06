#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Web LLM Interactor Complete Test ===${NC}"
echo -e "${YELLOW}This script tests the CLI with a clean Qwen.ai session${NC}\n"

# Set PYTHONPATH to include project root
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd):$PYTHONPATH"

# Function to reset Chrome tab
reset_tab() {
  echo -e "${YELLOW}Resetting Chrome tab...${NC}"
  osascript -e 'tell application "Google Chrome" to tell the active tab of its first window to reload'
  sleep 5  # Allow time for page to reload
}

# Test simple question
echo -e "${CYAN}=== Test 1: Basic Question with Default Fields ===${NC}"
reset_tab
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"What is the capital of Texas?\" --timeout 60${NC}"
python -m web_llm_interactor.cli ask "What is the capital of Texas?" --timeout 60
echo -e "\n${GREEN}Test 1 completed.${NC}\n"
sleep 3

# Test with custom fields
echo -e "${CYAN}=== Test 2: Question with Custom Fields ===${NC}"
reset_tab
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"Who is the current president of USA?\" --fields \"question,answer\" --timeout 60${NC}"
python -m web_llm_interactor.cli ask "Who is the current president of USA?" --fields "question,answer" --timeout 60
echo -e "\n${GREEN}Test 2 completed.${NC}\n"
sleep 3

# Test with no JSON format
echo -e "${CYAN}=== Test 3: No JSON Format ===${NC}"
reset_tab
echo -e "${YELLOW}Command: python -m web_llm_interactor.cli ask \"List three popular programming languages\" --no-json-format --timeout 60${NC}"
python -m web_llm_interactor.cli ask "List three popular programming languages" --no-json-format --timeout 60
echo -e "\n${GREEN}Test 3 completed.${NC}\n"

echo -e "${GREEN}All tests completed!${NC}"