# Complexity CLI Usage Guide (Updated)

## Overview

The Complexity CLI provides command-line access to search, database operations, and graph traversal functionality. This guide covers the key operations and features, including automatic embedding generation, current status, and troubleshooting.

## Requirements

Ensure the following environment variables are set before executing commands:
- `ARANGO_HOST`: URL of the ArangoDB instance (e.g., "http://localhost:8529").
- `ARANGO_USER`: ArangoDB username (e.g., "root").
- `ARANGO_PASSWORD`: ArangoDB password (IMPORTANT: use "openSesame").
- `ARANGO_DB_NAME`: Name of the target database (e.g., "memory_bank").
- API key for the configured embedding model (e.g., `OPENAI_API_KEY` if using OpenAI).

## Installation

The CLI is part of the Complexity package and can be executed using Python's module execution flag:

```bash
# Standard CLI
python -m src.complexity.cli [OPTIONS] COMMAND [ARGS]...

# Embedding-enhanced CLI
python -m src.complexity.cli_with_embeddings [OPTIONS] COMMAND [ARGS]...
```

## Embedding Support

The Complexity CLI now includes automatic embedding generation for document operations. This enables semantic search functionality by creating vector embeddings for document text content.

### When are embeddings generated?

Embeddings are automatically generated in these scenarios:
- When creating a new document with text content
- When updating a document's text content

Embedding generation applies to these collections:
- `messages`
- `test_docs`

### Using the Embedding-Enhanced CLI

To use the version with automatic embedding generation, use the `cli_with_embeddings.py` script:

```bash
# Create a document with automatic embedding generation
python -m src.complexity.cli_with_embeddings db create --collection messages --data '{"content": "This is a test document."}'

# Update a document (will regenerate embeddings if content changes)
python -m src.complexity.cli_with_embeddings db update <document_key> --collection messages --data '{"content": "Updated content will get a new embedding."}'
```

## Available Commands

### Search Commands

1. **Hybrid Search**
   ```bash
   python -m src.complexity.cli search hybrid "search query text"
   ```
   Combines keyword (BM25) and semantic search results using RRF re-ranking.
   
   Options:
   - `--top-n/-n`: Final number of ranked results (default: 5)
   - `--initial-k/-k`: Number of candidates from BM25/Semantic before RRF (default: 20)
   - `--bm25-th`: BM25 candidate retrieval score threshold (default: 0.01)
   - `--sim-th`: Similarity candidate retrieval score threshold (default: 0.70)
   - `--tags/-t`: Comma-separated list of tags to filter by
   - `--json-output/-j`: Output results as JSON array

2. **Semantic Search**
   ```bash
   python -m src.complexity.cli search semantic "search query text"
   ```
   Find documents based on conceptual meaning (vector similarity).
   
   Options:
   - `--threshold/-th`: Minimum similarity score (default: 0.75)
   - `--top-n/-n`: Number of results to return (default: 5)
   - `--tags/-t`: Comma-separated list of tags to filter by
   - `--json-output/-j`: Output results as JSON array

3. **BM25 Search**
   ```bash
   python -m src.complexity.cli search bm25 "search query text"
   ```
   Find documents based on keyword relevance (BM25 algorithm).
   
   Options:
   - `--threshold/-th`: Minimum BM25 score (default: 0.1)
   - `--top-n/-n`: Number of results to return (default: 5)
   - `--offset/-o`: Offset for pagination (default: 0)
   - `--tags/-t`: Comma-separated list of tags to filter by
   - `--json-output/-j`: Output results as JSON array

### Database Commands

1. **Create Document**
   ```bash
   python -m src.complexity.cli db create --collection <collection_name> [--data <json_string> | --data-file <path>]
   ```
   Create a new document in a collection.
   
   Options:
   - `--collection/-c`: Name of the collection to add document to
   - `--data/-d`: Document data as JSON string
   - `--data-file/-f`: Path to JSON file containing document data
   - `--json-output/-j`: Output metadata as JSON on success

2. **Read Document**
   ```bash
   python -m src.complexity.cli db read <key> --collection <collection_name>
   ```
   Retrieve a document by its key.
   
   Options:
   - `--collection/-c`: Name of the collection containing the document
   - `--json-output/-j`: Output document as JSON (default: True)

3. **Update Document**
   ```bash
   python -m src.complexity.cli db update <key> --collection <collection_name> [--data <json_string> | --data-file <path>]
   ```
   Update an existing document.
   
   Options:
   - `--collection/-c`: Name of the collection containing the document
   - `--data/-d`: Update data as JSON string
   - `--data-file/-f`: Path to JSON file containing update data
   - `--json-output/-j`: Output metadata as JSON on success

4. **Delete Document**
   ```bash
   python -m src.complexity.cli db delete <key> --collection <collection_name>
   ```
   Remove a document from a collection.
   
   Options:
   - `--collection/-c`: Name of the collection containing the document
   - `--yes/-y`: Confirm deletion without interactive prompt
   - `--json-output/-j`: Output status as JSON

### Graph Commands

1. **Add Edge**
   ```bash
   python -m src.complexity.cli graph add-edge <from_key> <to_key> --collection <collection_name> --edge-collection <edge_collection> --type <relationship_type> --rationale <reason>
   ```
   Create a relationship between two documents.
   
   Options:
   - `--collection/-c`: Name of the document collection
   - `--edge-collection/-e`: Name of the edge collection
   - `--type/-t`: Type of the relationship
   - `--rationale/-r`: Reason for linking these documents
   - `--attributes/-a`: Additional edge properties as JSON string
   - `--json-output/-j`: Output metadata as JSON on success

### Memory Agent Commands

1. **Store Memory**
   ```bash
   python -m src.complexity.cli memory store "User message" "Agent response" --conversation-id <conversation_id>
   ```
   Store a conversation between user and agent in the memory database.
   
   Options:
   - `--conversation-id/-cid`: Unique identifier for the conversation
   - `--metadata/-m`: Additional metadata as JSON string
   - `--json-output/-j`: Output metadata as JSON on success

2. **Search Memory**
   ```bash
   python -m src.complexity.cli memory search "query text" --top-n 5
   ```
   Search for relevant memories using hybrid search.
   
   Options:
   - `--top-n/-n`: Number of results to return (default: 5)
   - `--tags/-t`: Filter by specific tags
   - `--json-output/-j`: Output results as JSON array

3. **Get Related Memories**
   ```bash
   python -m src.complexity.cli memory related <memory_key>
   ```
   Find memories related to a specific memory through the knowledge graph.
   
   Options:
   - `--type/-t`: Relationship type filter
   - `--max-depth/-d`: Maximum traversal depth (default: 1)
   - `--limit/-l`: Maximum number of results to return (default: 10)
   - `--json-output/-j`: Output results as JSON array

4. **Get Conversation Context**
   ```bash
   python -m src.complexity.cli memory context <conversation_id>
   ```
   Retrieve all messages in a conversation in chronological order.
   
   Options:
   - `--limit/-l`: Maximum number of messages to return (default: 100)
   - `--json-output/-j`: Output results as JSON array

2. **Delete Edge**
   ```bash
   python -m src.complexity.cli graph delete-edge <edge_key> --edge-collection <edge_collection>
   ```
   Remove a relationship between documents.
   
   Options:
   - `--edge-collection/-e`: Name of the edge collection
   - `--yes/-y`: Confirm deletion without interactive prompt
   - `--json-output/-j`: Output status as JSON

3. **Traverse Graph**
   ```bash
   python -m src.complexity.cli graph traverse <start_key> --collection <collection_name> --graph-name <graph_name>
   ```
   Explore connections in the graph starting from a document.
   
   Options:
   - `--collection/-c`: Name of the document collection
   - `--graph-name/-g`: Name of the graph to traverse
   - `--min-depth`: Minimum traversal depth (default: 1)
   - `--max-depth`: Maximum traversal depth (default: 1)
   - `--direction/-dir`: Direction: OUTBOUND, INBOUND, or ANY (default: OUTBOUND)
   - `--limit/-lim`: Maximum number of paths to return (default: 10)
   - `--json-output/-j`: Output results as JSON (default: True)

### Initialization Command

```bash
python -m src.complexity.cli init [--create-collections] [--create-sample-data] [--force]
```
Initialize ArangoDB with collections and sample data for testing.

Options:
- `--create-collections/-c`: Create required collections (default: True)
- `--create-sample-data/-s`: Create sample data for testing (default: True)
- `--force/-f`: Force recreation of collections even if they exist (default: False)

## Examples

### Creating a Document with Automatic Embedding

```bash
python -m src.complexity.cli_with_embeddings db create --collection messages --data '{"content": "This document will have an embedding automatically generated."}'
```

### Updating a Document with Automatic Embedding Regeneration

```bash
python -m src.complexity.cli_with_embeddings db update <document_key> --collection messages --data '{"content": "Updated content that will get a new embedding."}'
```

### Creating a Relationship

```bash
python -m src.complexity.cli graph add-edge doc1 doc2 --collection messages --edge-collection relationships --type RELATED_TO --rationale "These documents cover similar topics"
```

### Performing Semantic Search

```bash
python -m src.complexity.cli search semantic "concepts similar to this query text" --threshold 0.8 --top-n 10
```

## Troubleshooting

### Common Issues

1. **No Search Results**: If search commands return no results, check:
   - The database has been initialized with test data (`python -m complexity.cli init --force`)
   - The search view is properly configured
   - The query text has matches in the database

2. **Vector Search Errors**: If seeing "failed vector search" errors:
   - There may be a mismatch between embedding dimensions 
   - Run the diagnostic script to check dimensions
   - Current system has an issue with embedding dimensions (320 vs 1024)

3. **Authentication Errors**: If seeing authentication failures:
   - Ensure ARANGO_PASSWORD is set to "openSesame"
   - Check that the ARANGO_HOST and ARANGO_USER are correct

### Diagnostic Tools

To help diagnose issues, use the following diagnostic scripts:

1. **Search API Diagnostics**:
   ```bash
   python -m complexity.arangodb.search_api.debug_search all
   ```

2. **CLI Verification**:
   ```bash
   python -m complexity.arangodb.cli_verification [--force]
   ```

## Known Issues and Workarounds

### BM25 Search Issues

- **Symptom**: BM25 search returns no results despite data being present
- **Fix**: Ensure the search view is properly configured with `includeAllFields: true`
- **Workaround**: Use tag search or semantic search until fixed

### Semantic Search Dimension Mismatch

- **Symptom**: Semantic search fails with "vector search" errors
- **Cause**: Mismatch between embedding dimensions in test data (320) vs. code config (1024)
- **Workaround**: Falls back to manual PyTorch search when ArangoDB vector search fails

## Verification

To verify that the CLI functionality is working correctly, run the CLI verification script. It tests all major CLI commands and reports success or failure:

```bash
python -m complexity.arangodb.cli_verification
```

For detailed debugging and diagnostics of specific search methods:

```bash
python -m complexity.arangodb.search_api.debug_search bm25
python -m complexity.arangodb.search_api.debug_search semantic
python -m complexity.arangodb.search_api.debug_search hybrid
```

## Advanced Usage

### Custom Embedding Fields

By default, embeddings are generated from the `content` field and stored in the `embedding` field. For custom field mappings, you'll need to modify the `embedded_db_operations.py` module.

### JSON Output

Most commands support a `--json-output/-j` flag to return data in a machine-readable JSON format, which is useful for scripting and automation.

## Current Development Status

The CLI functionality is currently under development. The following features are working:

- [x] Database initialization
- [x] Memory store, search, and context retrieval
- [ ] BM25 search (partially working)
- [ ] Semantic search (works with fallback)
- [ ] Hybrid search (depends on BM25 and semantic)
- [ ] Tag search (partially working)

See the task file at `src/complexity/arangodb/tasks/005_search_api_and_cli_fixes.md` for current progress and planned fixes.