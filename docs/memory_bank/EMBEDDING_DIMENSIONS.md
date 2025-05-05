# Embedding Dimensions and Vector Configuration

This document explains how embeddings are configured and used throughout the complexity project, particularly for semantic search with ArangoDB.

## Embedding Configuration

The project uses the `BAAI/bge-large-en-v1.5` embedding model which produces 1024-dimensional embeddings. This configuration is defined in:

- `src/complexity/arangodb/config.py` (primary configuration)
- `src/complexity/beta/utils/config.py` (beta module configuration)

The embedding field name and dimensions are defined consistently as:

```python
EMBEDDING_FIELD = "embedding"
EMBEDDING_DIMENSIONS = 1024
```

## Test Fixtures

Test fixtures should use 1024-dimensional embeddings to match production code. The test document generator in `tests/arangodb/test_modules/test_fixtures.py` creates mock embeddings for testing purposes:

```python
# Create a 1024-dimensional vector to match production embedding dimensions
doc["embedding"] = [0.1] * 1024  # 1024-dimensional vector
```

## Vector Search Implementation

The semantic search implementation in `src/complexity/arangodb/search_api/semantic_search.py` uses ArangoDB's `APPROX_NEAR_COSINE` function to perform vector similarity searches but includes several fallback mechanisms:

1. **ArangoDB Vector Search**: The primary approach uses `APPROX_NEAR_COSINE` for optimal performance.
2. **Dimension Validation**: The code validates that query and document embedding dimensions match (1024).
3. **Manual Cosine Similarity**: When `APPROX_NEAR_COSINE` fails, a fallback using manual cosine calculation is used.

## Dimension Validation

Dimension validation is performed in several places:

1. When creating vector indexes in `arango_setup.py`:
   ```python
   # Create vector index
   cfg = {
       "type": "vector",
       "fields": [CONFIG["embedding"]["field"]],
       "params": {
           "metric": "cosine",
           "dimension": CONFIG["embedding"]["dimensions"],  # 1024
           "nLists": CONFIG["search"]["vector_index_nlists"]
       }
   }
   ```

2. In the vector search implementation:
   ```python
   # Validate query embedding dimensions match expected dimensions
   expected_dimension = EMBEDDING_DIMENSIONS  # From config.py (1024)
   actual_dimension = len(query_embedding)
   if actual_dimension != expected_dimension:
       logger.warning(f"Query embedding dimension mismatch: expected {expected_dimension}, got {actual_dimension}")
   ```

3. When checking documents:
   ```python
   # Check if dimensions match across documents and with query
   dimensions_found = set(sample["embedding_length"] for sample in embedding_samples)
   if len(dimensions_found) > 1:
       logger.warning(f"Inconsistent embedding dimensions in collection: {dimensions_found}")
   ```

## Best Practices

To ensure proper embedding handling:

1. Always use the standard 1024-dimensional embeddings from the BAAI/bge-large-en-v1.5 model.
2. For test environments, ensure test fixtures use 1024-dimensional vectors.
3. When adding new data to collections, verify embedding dimensions match the expected 1024 dimensions.
4. Use the validation functions in `arango_setup.py` to check collections for dimension consistency.

## AQL Queries

When writing AQL queries that involve embeddings:

1. Include a dimension check in the FILTER clause:
   ```aql
   FILTER HAS(doc, "embedding") 
       AND IS_LIST(doc.embedding) 
       AND LENGTH(doc.embedding) == 1024
   ```

2. When using APPROX_NEAR_COSINE, ensure vectors have the same dimensions:
   ```aql
   LET score = APPROX_NEAR_COSINE(doc.embedding, @query_embedding)
   ```

## Error Handling

When working with embeddings, handle these potential issues:

1. **Missing embedding field**: Check if documents have the embedding field.
2. **Empty embeddings**: Ensure embeddings are not empty arrays.
3. **Dimension mismatch**: Verify embeddings have the expected 1024 dimensions.
4. **Zero-norm vectors**: Normalize vectors before calculating cosine similarity.

The semantic search implementation includes comprehensive error handling for all these cases.