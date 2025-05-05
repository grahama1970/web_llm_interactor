# ArangoDB Import Guidelines

## Overview

This document provides guidelines for properly importing ArangoDB-related functionality in the complexity project. Following these guidelines ensures consistent code structure and prevents import errors.

## Core Import Patterns

### Database Connection and Setup

Always import database connection and setup functions from the correct module path:

```python
# CORRECT: Import from arango_setup (not arango_setup_unknown)
from complexity.arangodb.arango_setup import (
    connect_arango,
    ensure_database,
    ensure_collection,
    ensure_edge_collection,
    ensure_graph,
    ensure_arangosearch_view  # Note: use this name, not ensure_view
)
```

### Search API Functions

For search API functionality, use the established import pattern:

```python
# Search API imports
from complexity.arangodb.search_api.semantic_search import semantic_search
from complexity.arangodb.search_api.keyword_search import keyword_search
from complexity.arangodb.search_api.hybrid_search import hybrid_search
```

### Memory Agent

When using the Memory Agent API, import from the memory_agent module:

```python
# Memory Agent imports
from complexity.arangodb.memory_agent import MemoryAgent

# Initialize and use
agent = MemoryAgent()
```

## Common Import Mistakes

### Incorrect Module Names

❌ **Incorrect**:
```python
# DO NOT use these imports
from complexity.arangodb.arango_setup_unknown import connect_arango  # Wrong module name
from complexity.arangodb.arango_setup import ensure_view  # Function doesn't exist
```

✅ **Correct**:
```python
# Use these instead
from complexity.arangodb.arango_setup import connect_arango  # Correct module name
from complexity.arangodb.arango_setup import ensure_arangosearch_view  # Correct function name
```

### Function Alias For Backward Compatibility

If you need backward compatibility with code that uses `ensure_view`, use an import alias:

```python
# Import with alias for backward compatibility
from complexity.arangodb.arango_setup import ensure_arangosearch_view as ensure_view
```

## Module Structure

The project's ArangoDB integration is structured as follows:

```
complexity/
├── arangodb/
│   ├── arango_setup.py         # Core setup functions
│   ├── config.py               # Configuration variables
│   ├── embedding_utils.py      # Embedding utilities
│   ├── memory_agent/           # Memory Agent functionality
│   └── search_api/             # Search API modules
│       ├── semantic_search.py
│       ├── keyword_search.py
│       ├── hybrid_search.py
│       └── ...
```

## Best Practices

1. **Use Explicit Imports**: Always explicitly import specific functions rather than using wildcard imports (`from x import *`).
2. **Group Related Imports**: Group imports from the same module together.
3. **Use Consistent Naming**: Maintain consistent naming across the codebase (e.g., `ensure_arangosearch_view`).
4. **Check Function Existence**: Before importing, verify that the function exists in the module.
5. **Use Import Aliases**: When needed for backward compatibility, use import aliases.

## Migration Notes

If you encounter code that imports from `arango_setup_unknown`, update it to import from `arango_setup` instead. This incorrect module name has been removed from the codebase.

For code that references `ensure_view`, replace it with `ensure_arangosearch_view` or use an import alias as shown above.