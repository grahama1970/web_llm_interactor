# Search API Known Issues

This document outlines known issues with the ArangoDB search API implementation that need to be addressed in future work. These issues became apparent during testing after fixing import statements and parameter mismatches.

## Current Status

- ✅ **Tag search**: Working correctly
- ❌ **BM25 search**: Test failures
- ❌ **Semantic search**: Vector search implementation error
- ❌ **Hybrid search**: Fails due to dependency on BM25 and semantic search
- ❌ **Graph traversal search**: Test failures

## 1. BM25 Search Issues

**File**: `src/complexity/arangodb/search_api/bm25_search.py`

**Problem**: BM25 search tests are failing to return any results, even though the test data is properly created.

**Details**:
- All BM25 search tests return zero results when they should return between 1-3 results depending on the query
- The implementation appears to have the correct parameters with the `bind_vars` parameter added
- The AQL query may not be properly matching the text fields in the test documents

**Possible solutions**:
- Check the ArangoDB view configuration to ensure it's properly indexing text fields
- Verify that the text analyzer is correctly configured in the ArangoDB view
- Examine the AQL query to ensure it's using the correct operators for text matching
- Add debug logging to verify the values being passed to the query
- Validate that the test documents contain the expected content

## 2. Semantic Vector Search Issues

**File**: `src/complexity/arangodb/search_api/semantic_search.py`

**Problem**: Semantic search fails with ArangoDB error related to vector search.

**Details**:
- Error: `AQL: failed vector search [node #3: CalculationNode]`
- The embedding model appears to be loading correctly
- The embeddings are being generated successfully 
- The ArangoDB database may not be properly configured for vector search
- The test documents may not have proper vector embeddings stored

**Possible solutions**:
- Verify the ArangoDB version supports vector search (3.10.0+ required)
- Check for proper vector index configuration on the collection
- Verify the embedding dimension matches the dimension configured in ArangoDB
- Add proper error handling to provide more diagnostic information
- Check that test documents have valid embedding vectors with correct dimensions

## 3. Hybrid Search Issues

**File**: `src/complexity/arangodb/search_api/hybrid_search.py`

**Problem**: Hybrid search is failing as it depends on both BM25 and semantic search.

**Details**:
- Failures cascade from the BM25 and semantic search issues
- The implementation appears to have the correct parameter signatures
- Reciprocal Rank Fusion (RRF) cannot function properly without inputs from both search methods

**Possible solutions**:
- Fix the underlying BM25 and semantic search issues first
- Add better error handling to provide clear diagnostic information
- Consider adding a fallback mode that can use just one search method if the other fails

## 4. Graph Traversal Search Issues

**File**: `src/complexity/arangodb/search_api/graph_traverse.py`

**Problem**: Graph traversal tests fail to return expected results.

**Details**:
- The test relationships appear to be created successfully
- The `graph_traverse` function has the added required parameters
- The graph traversal query may not be properly structured for the test graph
- The issue could be with how the test graph is being defined or queried

**Possible solutions**:
- Verify the graph definition in the test environment
- Check the AQL query for proper traversal syntax
- Validate relationship creation in the test setup
- Add debug logging in the graph traversal function
- Ensure relationship types are being correctly filtered

## 5. Environment Configuration Issues

There may be broader configuration issues affecting multiple search methods:

- ArangoDB version compatibility
- View and index configuration
- Embedding model compatibility
- Test data generation and embedding

## Action Plan

1. Fix BM25 search first as it's the simplest and doesn't require vector search
2. Address semantic search vector implementation issues
3. Once BM25 and semantic work, hybrid search should be functional
4. Fix graph traversal search separately
5. Consider adding additional diagnostic tools and tests

## References

- [ArangoDB Vector Search Documentation](https://www.arangodb.com/docs/stable/arangosearch-vectors.html)
- [ArangoDB AQL Syntax for Graph Traversal](https://www.arangodb.com/docs/stable/aql/graphs-traversals.html)
- [Test Data Creation Code](https://github.com/user/repo/tests/arangodb/test_modules/test_fixtures.py)