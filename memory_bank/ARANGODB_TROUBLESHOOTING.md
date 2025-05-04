# ArangoDB Troubleshooting Guide

This document provides solutions to common issues encountered with ArangoDB integration in the complexity project.

## Authentication & Connection Issues

**Important Note:** The ArangoDB password is always `openSesame`. This should be used in all connection configurations.

**Symptoms:** 
- You see error messages like `[HTTP 401][ERR 11] not authorized to execute this request`
- Connection failures with "unauthorized" errors

**Solution:** 
- Always use the password `openSesame` for ArangoDB connections
- Example environment configuration:
  ```python
  os.environ["ARANGO_HOST"] = "http://localhost:8529"
  os.environ["ARANGO_USER"] = "root"
  os.environ["ARANGO_PASSWORD"] = "openSesame"
  os.environ["ARANGO_DB_NAME"] = "memory_bank"
  ```

## Vector Search Limitations

The specific limitation in ArangoDB regarding vector search filtering:
- ArangoDB's current vector search implementation has limitations when combining with filtering
- This can affect hybrid search implementations that need both vector similarity and attribute filtering

The three-stage approach we've implemented to work around it:
1. Perform the vector search first to get candidate documents
2. Apply filters to the candidates
3. Blend the results with BM25 text search for better overall relevance

## Performance Optimization Tips

- Use appropriate indexing for all search fields
- Configure proper analyzer settings for text fields
- Set reasonable limits on search results
- Use pagination for large result sets
- Consider caching for frequently accessed data

## Common Errors and Their Solutions

### "No results found" in BM25 searches

**Problem:** BM25 search returns no results even when matching content exists.

**Solution:** 
- Ensure the ArangoSearch view is configured to index all relevant fields
- Use `includeAllFields: true` in view configuration
- Make sure search queries include all relevant document fields
- Set appropriate analyzers for text fields

See `BM25_SEARCH_FIXES.md` for detailed information.

### Vector index creation failures

**Problem:** Errors when trying to create or use vector indices.

**Solution:**
- Verify embedding dimensions match the configured dimensions
- Ensure embeddings are stored as arrays, not strings or other types
- Check that documents contain the embedding field
- Verify memory and disk space availability for index creation

### Test database inconsistencies

**Problem:** Tests pass sometimes and fail other times.

**Solution:**
- Increase wait time for indexing after document creation (2+ seconds)
- Use minimum expected counts rather than exact counts 
- Clear test data between runs to prevent interference
- Ensure view configurations before running search tests