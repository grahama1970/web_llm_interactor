#!/bin/bash
# Helper script to run the proof-of-concept tests

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create debug directory if it doesn't exist
mkdir -p debug

# Function to display help
show_help() {
    echo "Usage: ./run_test.sh [test_name] [args...]"
    echo ""
    echo "Available tests:"
    echo "  detect    - Test chat input field detection"
    echo "  paste     - Test pasting text to chat input (requires text argument)"
    echo "  captcha   - Test CAPTCHA detection"
    echo "  extract   - Test response extraction"
    echo ""
    echo "Examples:"
    echo "  ./run_test.sh detect"
    echo "  ./run_test.sh paste \"What is the capital of France?\""
    echo "  ./run_test.sh captcha --monitor"
    echo "  ./run_test.sh extract --site perplexity --include-query"
    echo ""
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8 or later."
    exit 1
fi

# Check if first argument is provided
if [ -z "$1" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

TEST_NAME="$1"
shift  # Remove the first argument

case "$TEST_NAME" in
    detect)
        echo "Running chat input detection test..."
        python3 detect_chat_input.py "$@"
        ;;
    paste)
        if [ -z "$1" ]; then
            echo "Error: The paste test requires text to paste."
            echo "Usage: ./run_test.sh paste \"Your text here\""
            echo "   or: ./run_test.sh paste --query \"Your text here\""
            exit 1
        fi
        echo "Running paste-to-chat test..."
        # If first argument doesn't start with -, assume it's the query text
        if [[ "$1" != -* ]]; then
            # Convert positional argument to --query format
            QUERY="$1"
            shift
            python3 paste_to_chat.py --query "$QUERY" "$@"
        else
            # Pass all arguments as-is
            python3 paste_to_chat.py "$@"
        fi
        ;;
    captcha)
        echo "Running CAPTCHA detection test..."
        python3 captcha_detector.py "$@"
        ;;
    extract)
        echo "Running response extraction test..."
        python3 extract_response.py "$@"
        ;;
    *)
        echo "Error: Unknown test '$TEST_NAME'"
        show_help
        exit 1
        ;;
esac

echo "Test complete."