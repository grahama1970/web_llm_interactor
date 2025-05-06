#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Web LLM Interactor Demo Script ===${NC}"
echo -e "${YELLOW}This script demonstrates different usage patterns for the web-llm-interactor tool.${NC}\n"

# Define the command with different options
COMMAND="web-llm-interactor"

echo -e "${CYAN}=== Basic Usage (Qwen Default) ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"What is the capital of Georgia?\"${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "What is the capital of Georgia?"

echo -e "\n${CYAN}=== Using a Different Chat URL (Perplexity) ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"What is the capital of France?\" --url \"https://chat.perplexity.ai/\"${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "What is the capital of France?" --url "https://chat.perplexity.ai/"

echo -e "\n${CYAN}=== Saving HTML Output to Custom Location ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"What is the tallest mountain?\" --output-html \"./mountain_response.html\"${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "What is the tallest mountain?" --output-html "./mountain_response.html"

echo -e "\n${CYAN}=== Finding All JSON Objects in Response (not just the last one) ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"List the 3 largest oceans\" --all${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "List the 3 largest oceans" --all

echo -e "\n${CYAN}=== Custom JSON Fields ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"Explain quantum computing\" --fields \"question,answer\"${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "Explain quantum computing" --fields "question,answer"

echo -e "\n${CYAN}=== Disable JSON Format Instructions ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"What's the weather like in Paris?\" --no-json-format${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "What's the weather like in Paris?" --no-json-format

echo -e "\n${CYAN}=== Timeout and Retry Configuration ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} ask \"Explain quantum computing\" --timeout 45 --max-attempts 2${NC}"
read -p "Press Enter to execute..." 
${COMMAND} ask "Explain quantum computing" --timeout 45 --max-attempts 2

echo -e "\n${CYAN}=== CLI Help Information ===${NC}"
echo -e "${YELLOW}Command: ${COMMAND} --help${NC}"
read -p "Press Enter to execute..." 
${COMMAND} --help

echo -e "\n${BLUE}Demo complete! Use 'web-llm-interactor usage' for additional examples.${NC}"