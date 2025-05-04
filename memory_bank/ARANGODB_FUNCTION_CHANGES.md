# ArangoDB Function Name Changes

This document describes important function name changes in the ArangoDB integration that developers should be aware of.

## `ensure_view` → `ensure_arangosearch_view`

### Change Description

The function previously known as `ensure_view` has been renamed to `ensure_arangosearch_view` for clarity and to better describe its purpose.

### Migration Guide

#### Option 1: Update Function Name (Recommended)

```python
# Before
from complexity.arangodb.arango_setup import ensure_view

# After
from complexity.arangodb.arango_setup import ensure_arangosearch_view
```

Update all calls to the function:

```python
# Before
ensure_view(db, "view_name", "collection_name")

# After
ensure_arangosearch_view(db, "view_name", "collection_name")
```

#### Option 2: Use Import Alias (For Backward Compatibility)

If you need to maintain backward compatibility without changing function calls:

```python
# Import with alias
from complexity.arangodb.arango_setup import ensure_arangosearch_view as ensure_view

# Function calls remain unchanged
ensure_view(db, "view_name", "collection_name")
```

### Function Details

The `ensure_arangosearch_view` function creates or updates an ArangoSearch view for text search:

```python
def ensure_arangosearch_view(db, view_name="complexity_view", collection_name="complexity"):
    """Create or update ArangoSearch view for text search."""
    try:
        # 1. Ensure text analyzer
        analyzers = {a["name"] for a in db.analyzers()}
        if "text_en" not in analyzers:
            logger.info("Analyzer 'text_en' not found. Creating...")
            db.create_analyzer(
                "text_en",
                {"type": "text", "properties": {"locale": "en", "stemming": True, "case": "lower"}}
            )
            logger.info("Analyzer 'text_en' created.")

        # 2. Define view properties
        view_props = {
            "links": {
                collection_name: {
                    "fields": {
                        "problem":  {"analyzers": ["text_en"]},
                        "solution": {"analyzers": ["text_en"]},
                        "context":  {"analyzers": ["text_en"]},
                        "tags":     {"analyzers": ["identity"]},
                        "embedding": {}
                    },
                    "includeAllFields": False
                }
            },
            "primarySort": [{"field": "_key", "direction": "asc"}],
            "commitIntervalMsec": 1000,
            "consolidationIntervalMsec": 1000
        }

        existing = {v["name"] for v in db.views()}
        if view_name in existing:
            # Update existing view
            logger.info(f"Updating search view '{view_name}'...")
            db.update_view(
                name=view_name,
                properties=view_props
            )
            logger.info(f"Search view '{view_name}' updated.")
        else:
            # Create new view
            logger.info(f"Creating search view '{view_name}'...")
            db.create_view(
                name=view_name,
                view_type="arangosearch",
                properties=view_props
            )
            logger.info(f"Search view '{view_name}' created.")
            
        return db.view(view_name)
    except Exception as e:
        logger.exception(f"Failed to ensure ArangoSearch view '{view_name}': {e}")
        sys.exit(1)
```

## Additional Notes

- The function name change was made to improve clarity and maintainability.
- The implementation details of the function remain the same.
- When fixing imports related to this function, ensure you're also using the correct module path: `complexity.arangodb.arango_setup` (not `complexity.arangodb.arango_setup_unknown`).

See [ARANGODB_IMPORT_GUIDELINES.md](./ARANGODB_IMPORT_GUIDELINES.md) for comprehensive import guidance.