#!/bin/bash

# This script runs Claude with the Hacker system prompt to analyze the security of the codebase

# Check if claude-cli is installed
if ! command -v claude &> /dev/null; then
    echo "Claude CLI is not installed. Please install it first."
    echo "You can install it with: npm install -g @anthropic-ai/claude-cli"
    exit 1
fi

# ANSI color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "\n${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║  PERPLEXITY.AI STEALTH - CLAUDE HACKER MODE                 ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}This script will run Claude with a security-focused system prompt to analyze the codebase for vulnerabilities.${NC}"
echo -e "${YELLOW}Make sure you have the Claude CLI installed and authenticated.${NC}"

# Ask for confirmation
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Operation cancelled.${NC}"
    exit 1
fi

# Create a temporary file for the hacker prompt
TEMP_PROMPT_FILE=$(mktemp)
echo "Analyze the security of the Perplexity.ai stealth automation codebase. Focus on identifying potential vulnerabilities, security risks, and providing recommendations for improvement." > "$TEMP_PROMPT_FILE"

echo -e "\n${GREEN}${BOLD}[STARTING CLAUDE HACKER MODE]${NC}"
echo -e "Loading system prompt and analyzing codebase...\n"

# Run Claude with the hacker system prompt
claude --system-prompt ./claude-hacker-system-prompt.md --message-file "$TEMP_PROMPT_FILE"

# Clean up the temporary file
rm "$TEMP_PROMPT_FILE"

echo -e "\n${GREEN}${BOLD}[ANALYSIS COMPLETE]${NC}"