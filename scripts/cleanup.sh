#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Define the primary files to keep
KEEP_FILES=(
  "__init__.py"
  "cli.py"
  "extract_json_from_html.py"
  "file_utils.py"
  "json_utils.py"
  "send_enter_save_source.applescript"
)

# Define colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Cleaning up temporary files in src/web_llm_interactor...${NC}"

# Keep track of removed files
REMOVED_FILES=()

# Move to the web_llm_interactor directory
cd "$PROJECT_ROOT/src/web_llm_interactor"

# First restore backups if needed
if [ -f "cli.py.backup" ]; then
  echo -e "${YELLOW}Restoring cli.py from backup...${NC}"
  cp "cli.py.backup" "cli.py"
  echo -e "${GREEN}Restored cli.py${NC}"
fi

if [ -f "extract_json_from_html.py.backup" ]; then
  echo -e "${YELLOW}Restoring extract_json_from_html.py from backup...${NC}"
  cp "extract_json_from_html.py.backup" "extract_json_from_html.py"
  echo -e "${GREEN}Restored extract_json_from_html.py${NC}"
fi

if [ -f "send_enter_save_source.applescript.backup" ]; then
  echo -e "${YELLOW}Restoring send_enter_save_source.applescript from backup...${NC}"
  cp "send_enter_save_source.applescript.backup" "send_enter_save_source.applescript"
  echo -e "${GREEN}Restored send_enter_save_source.applescript${NC}"
fi

# Check for debug_applesript.scpt
if [ -f "debug_applesript.scpt" ]; then
  echo -e "${YELLOW}Removing debug script...${NC}"
  rm "debug_applesript.scpt"
  echo -e "${GREEN}Removed debug_applesript.scpt${NC}"
  REMOVED_FILES+=("debug_applesript.scpt")
fi

# Check for send_enter_save_source copy.applescript
if [ -f "send_enter_save_source copy.applescript" ]; then
  echo -e "${YELLOW}Removing backup copy of source script...${NC}"
  rm "send_enter_save_source copy.applescript"
  echo -e "${GREEN}Removed send_enter_save_source copy.applescript${NC}"
  REMOVED_FILES+=("send_enter_save_source copy.applescript")
fi

# Ask about removing __pycache__ files
echo -e "${YELLOW}Do you want to remove __pycache__ files? (y/n)${NC}"
read -r remove_pycache

if [ "$remove_pycache" = "y" ]; then
  echo -e "${YELLOW}Removing __pycache__ files...${NC}"
  if [ -d "__pycache__" ]; then
    find "__pycache__" -name "*.pyc" -delete
    echo -e "${GREEN}Removed __pycache__ files${NC}"
    REMOVED_FILES+=("__pycache__/*.pyc")
  else
    echo -e "${YELLOW}No __pycache__ directory found${NC}"
  fi
fi

# Remove any other temporary files
echo -e "${YELLOW}Checking for other temporary files...${NC}"
for file in *; do
  # Skip directories and KEEP_FILES
  if [ -d "$file" ]; then
    continue
  fi
  
  # Check if file should be kept
  KEEP=0
  for keep_file in "${KEEP_FILES[@]}"; do
    if [ "$file" = "$keep_file" ]; then
      KEEP=1
      break
    fi
  done
  
  # Remove if not in keep list
  if [ $KEEP -eq 0 ] && [ "$file" != "debug_applesript.scpt" ] && [ "$file" != "send_enter_save_source copy.applescript" ] && [[ "$file" != *.backup ]]; then
    echo -e "${YELLOW}Removing: $file${NC}"
    rm "$file"
    REMOVED_FILES+=("$file")
  fi
done

# Remove test files in responses directory
echo -e "${YELLOW}Do you want to remove test HTML files from the responses directory? (y/n)${NC}"
read -r remove_test_responses

if [ "$remove_test_responses" = "y" ]; then
  echo -e "${YELLOW}Removing test HTML files...${NC}"
  if [ -d "$PROJECT_ROOT/responses" ]; then
    # Save number of files found
    num_files=$(find "$PROJECT_ROOT/responses" -name "test_*.html" -type f | wc -l)
    find "$PROJECT_ROOT/responses" -name "test_*.html" -type f -delete
    echo -e "${GREEN}Removed $num_files test HTML files${NC}"
  else
    echo -e "${YELLOW}No responses directory found${NC}"
  fi
fi

echo ""
echo -e "${GREEN}Cleanup complete. Removed ${#REMOVED_FILES[@]} temporary files.${NC}"
echo -e "${YELLOW}Remaining files in src/web_llm_interactor:${NC}"
ls -la

echo ""
echo -e "${YELLOW}Do you want to clean up test scripts from the scripts directory? (y/n)${NC}"
read -r remove_test_scripts

if [ "$remove_test_scripts" = "y" ]; then
  cd "$PROJECT_ROOT/scripts"
  TEST_SCRIPTS=(
    "test_basic.sh"
    "test_cli_json.sh"
    "test_complete.sh"
    "test_final.sh"
    "test_final_solution.sh"
    "test_fixed_wait.sh"
    "test_flexible.sh"
    "test_improved_extraction.sh"
    "test_manual_send.sh"
    "test_simple_approach.sh"
    "test_updated_cli.sh"
    "test_updated_scraper.sh"
  )
  
  for script in "${TEST_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
      echo -e "${YELLOW}Removing $script...${NC}"
      rm "$script"
      echo -e "${GREEN}Removed $script${NC}"
    fi
  done
  
  echo -e "${GREEN}Test scripts cleanup complete.${NC}"
fi

echo ""
echo -e "${GREEN}All cleanup tasks completed successfully!${NC}"
echo -e "${YELLOW}You should now commit your changes to git.${NC}"