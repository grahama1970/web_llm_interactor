#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Web LLM Interactor Integration Test ===${NC}"
echo -e "${YELLOW}This script tests the integration with Qwen.ai${NC}\n"

# Check if Chrome is running
if ! pgrep -x "Google Chrome" > /dev/null; then
  echo -e "${RED}Error: Google Chrome must be running.${NC}"
  echo -e "Please open Chrome with a tab to https://chat.qwen.ai/ before running this test."
  exit 1
fi

# Run the Python test
echo -e "${CYAN}Running integration tests...${NC}"
echo -e "${YELLOW}Note: This test will interact with a real Qwen.ai session in Chrome.${NC}"
echo -e "${YELLOW}Make sure you have Chrome open with a tab to https://chat.qwen.ai/\n${NC}"

# Set PYTHONPATH to include project root
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd):$PYTHONPATH"
python3 -m tests.web_llm_interactor.test_cli_integration

# Check exit code
if [ $? -eq 0 ]; then
  echo -e "\n${GREEN}Tests completed successfully!${NC}"
else
  echo -e "\n${RED}Tests failed.${NC}"
  echo -e "${YELLOW}Please check error messages above and ensure Chrome is open with a Qwen.ai tab.${NC}"
fi