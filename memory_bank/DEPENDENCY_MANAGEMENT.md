# Dependency Management Best Practices

## Conditional Imports

### When to Use Conditional Imports

Conditional imports should only be used for **optional dependencies** that are not required for core functionality. This approach helps make a package more flexible and adaptable to different environments while avoiding unnecessary dependencies.

**Good use cases for conditional imports:**

1. Optional features that enhance functionality but aren't essential
2. Integration with specialized libraries that not all users need
3. Platform-specific code that may not work on all systems
4. Performance optimizations that can fallback to slower implementations

**Example of appropriate conditional import:**

```python
# Good: Conditionally importing an optional GPU acceleration library
try:
    import cupy as np
    GPU_AVAILABLE = True
except ImportError:
    import numpy as np
    GPU_AVAILABLE = False
    logger.info("GPU acceleration not available, using CPU implementation")
```

### When NOT to Use Conditional Imports

**Do NOT use conditional imports for packages that are:**

1. Listed as required dependencies in pyproject.toml/requirements.txt
2. Necessary for core functionality
3. Used throughout the codebase
4. Already known to be installed in the environment

**Example of inappropriate conditional import:**

```python
# Bad: Conditionally importing a required dependency
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.warning("tiktoken not available, using fallback token counting")
    TIKTOKEN_AVAILABLE = False
```

### Preferred Approach for Required Dependencies

For dependencies that are required for core functionality:

1. Declare them properly in `pyproject.toml` or `requirements.txt`
2. Import them directly at the module level
3. Handle specific errors that might occur when using them, not when importing them

**Example of proper approach:**

```python
# Good: Direct import with error handling during use
import tiktoken

def count_tokens(text, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens: {e}")
        return len(text) // 4  # Fallback estimation
```

## Error Handling Best Practices

1. Be specific about which exceptions you catch
2. Handle errors at the point of use, not at import time
3. Provide meaningful error messages that guide users to a solution
4. Implement graceful fallbacks when appropriate

```python
# Good error handling example
def load_spacy_model(model_name):
    try:
        return spacy.load(model_name)
    except OSError:
        logger.warning(f"SpaCy model '{model_name}' not found. Please install with: python -m spacy download {model_name}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading SpaCy model: {e}")
        return None
```

## Project-Specific Guidelines

In the Complexity project, the following packages are core dependencies and should **never** use conditional imports:

- tiktoken
- spacy
- tree-sitter
- tree-sitter-languages
- tree-sitter-language-pack
- rich
- markdown-it-py
- loguru

When using these packages:

1. Import them directly at the top of the module
2. Handle specific errors that might occur during their use
3. Implement appropriate fallbacks or error messages

This ensures that our code remains clean, maintainable, and explicit about its dependencies.