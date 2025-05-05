# ArangoDB Usage Guide

This guide provides practical examples and patterns for working with ArangoDB in this project, with particular focus on vector search, ArangoSearch, and optimization techniques.

> **IMPORTANT**: 
> - For guidelines on importing ArangoDB functionality, see [ARANGODB_IMPORT_GUIDELINES.md](./ARANGODB_IMPORT_GUIDELINES.md).
> - Always import from `complexity.arangodb.arango_setup` and not `complexity.arangodb.arango_setup_unknown`.
> - For function name changes (`ensure_view` → `ensure_arangosearch_view`), see [ARANGODB_FUNCTION_CHANGES.md](./ARANGODB_FUNCTION_CHANGES.md).

## 1. Connection and Setup

### Connecting to ArangoDB

```python
from arango import ArangoClient
from complexity.arangodb.config import (
    ARANGO_HOST, ARANGO_USER, ARANGO_PASSWORD, ARANGO_DB_NAME
)
import sys
from loguru import logger

def connect_arango():
    """Establish connection to ArangoDB."""
    logger.info(f"Connecting to ArangoDB at {ARANGO_HOST}...")
    if not ARANGO_PASSWORD:
        logger.error("ARANGO_PASSWORD environment variable is not set.")
        sys.exit(1)
        
    try:
        client = ArangoClient(hosts=ARANGO_HOST, request_timeout=30)
        sys_db = client.db("_system", username=ARANGO_USER, password=ARANGO_PASSWORD)
        version_info = sys_db.version()
        if isinstance(version_info, str):
            version = version_info
        elif isinstance(version_info, dict):
            version = version_info.get("version", "unknown")
        else:
            version = "unknown"
        logger.info(f"Successfully connected to ArangoDB version {version}.")
        return client
    except Exception as e:
        logger.exception(f"Failed to connect to ArangoDB: {e}")
        sys.exit(1)

def ensure_database(client):
    """Ensure database exists and return connection."""
    try:
        # System database for admin operations
        sys_db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)
        
        # Create our database if it doesn't exist
        if not sys_db.has_database(ARANGO_DB_NAME):
            logger.info(f"Database '{ARANGO_DB_NAME}' not found. Creating...")
            sys_db.create_database(ARANGO_DB_NAME)
            logger.info(f"Database '{ARANGO_DB_NAME}' created successfully.")
        else:
            logger.info(f"Database '{ARANGO_DB_NAME}' already exists.")
        
        # Connect to our database
        db = client.db(ARANGO_DB_NAME, username=ARANGO_USER, password=ARANGO_PASSWORD)
        return db
    except Exception as e:
        logger.exception(f"Failed to ensure database: {e}")
        sys.exit(1)
```

### Creating Collections and Indexes

```python
def ensure_collection(db, collection_name="complexity"):
    """Ensure collection exists and create if needed."""
    try:
        if not db.has_collection(collection_name):
            logger.info(f"Collection '{collection_name}' not found. Creating...")
            db.create_collection(collection_name)
            logger.info(f"Collection '{collection_name}' created successfully.")
        else:
            logger.info(f"Collection '{collection_name}' already exists.")
        return db.collection(collection_name)
    except Exception as e:
        logger.exception(f"Failed to ensure collection '{collection_name}': {e}")
        sys.exit(1)

def ensure_edge_collection(db, collection_name="relationships"):
    """Ensure the specified EDGE collection exists."""
    try:
        if db.has_collection(collection_name):
            props = db.collection(collection_name).properties()
            if props.get("type") != 3:  # 3 = edge
                logger.info(f"Collection '{collection_name}' is not edge; recreating...")
                db.delete_collection(collection_name)
                db.create_collection(collection_name, edge=True)
                logger.info(f"Edge collection '{collection_name}' recreated.")
            else:
                logger.info(f"Edge collection '{collection_name}' already exists.")
        else:
            logger.info(f"Edge collection '{collection_name}' not found. Creating...")
            db.create_collection(collection_name, edge=True)
            logger.info(f"Edge collection '{collection_name}' created.")
        return db.collection(collection_name)
    except Exception as e:
        logger.exception(f"Failed to ensure edge collection '{collection_name}': {e}")
        sys.exit(1)

def create_vector_index(collection, embedding_field="embedding", dimensions=1024):
    """Create vector index for embedding field."""
    try:
        indexes = collection.indexes()  # list all existing indexes

        # If an old 'vector_index' exists, drop it first
        for idx in indexes:
            if idx.get("name") == "vector_index":
                idx_id = idx.get("id") or idx.get("name")
                logger.info(f"Dropping existing 'vector_index' (id={idx_id})...")
                collection.delete_index(idx_id)
                break
                
        # Now create the new vector index
        index_config = {
            "type": "vector",
            "fields": [embedding_field],
            "params": {
                "dimension": dimensions,
                "metric": "cosine",  # Use "euclidean" for L2 distance
                "nLists": min(16, collection.count() // 1000 + 1)  # Scale with collection size
            },
            "name": "vector_index"
        }
        
        logger.info(f"Creating vector index on '{collection.name}.{embedding_field}'...")
        result = collection.add_index(index_config)
        logger.info(f"Vector index 'vector_index' created successfully.")
        return result
    except Exception as e:
        text = str(e).lower()
        # If ArangoDB still complains about a duplicate name, skip
        if "duplicate value" in text:
            logger.warning("Duplicate-name on 'vector_index'; assuming it exists and skipping.")
        else:
            logger.exception(f"Failed to ensure vector index: {e}")
            sys.exit(1)
```

## 2. Basic CRUD Operations

### Creating Documents

```python
def insert_documents(db, docs, collection_name="complexity"):
    """Insert multiple documents into a collection."""
    collection = db.collection(collection_name)
    return collection.insert_many(docs)

# Example usage:
docs = [
    {"_key": "doc1", "question": "What is ArangoDB?", "embedding": [0.1, 0.2, ...]}
    # More documents...
]
insert_documents(db, docs)
```

### Reading Documents

```python
def get_document(db, doc_key, collection_name="complexity"):
    """Get a single document by key."""
    collection = db.collection(collection_name)
    return collection.get(doc_key)

def query_documents(db, filter_expr, collection_name="complexity"):
    """Query documents using AQL filter expression."""
    aql = f"""
    FOR doc IN {collection_name}
    FILTER {filter_expr}
    RETURN doc
    """
    cursor = db.aql.execute(aql)
    return list(cursor)

# Example usage:
doc = get_document(db, "doc1")
docs = query_documents(db, "doc.question LIKE '%ArangoDB%'")
```

### Updating Documents

```python
def update_document(db, doc_key, update_data, collection_name="complexity"):
    """Update specific fields in a document."""
    collection = db.collection(collection_name)
    return collection.update(doc_key, update_data)

# Example usage:
update_document(db, "doc1", {"answer": "ArangoDB is a multi-model database."})
```

### Deleting Documents

```python
def delete_document(db, doc_key, collection_name="complexity"):
    """Delete a document by key."""
    collection = db.collection(collection_name)
    return collection.delete(doc_key)

def truncate_collection(db, collection_name="complexity"):
    """Remove all documents from a collection."""
    collection = db.collection(collection_name)
    return collection.truncate()
```

## 3. Vector Search Approaches

ArangoDB's vector search has limitations that require specific approaches based on query complexity.

### Direct ArangoDB Search (Simple Queries)

For simple queries without filtering, use direct ArangoDB vector search:

```python
def direct_semantic_search(db, query_embedding, collection_name, embedding_field, top_n=10):
    """
    Direct semantic search without filtering - fastest approach.
    
    Note: Do not use FILTER with score in AQL - this causes errors.
    Filter by score in Python instead.
    """
    aql = f"""
    FOR doc IN {collection_name}
    LET score = APPROX_NEAR_COSINE(doc.{embedding_field}, @query_embedding)
    SORT score DESC
    LIMIT {top_n}
    RETURN {{
        "doc": doc,
        "similarity_score": score
    }}
    """
    
    cursor = db.aql.execute(aql, bind_vars={"query_embedding": query_embedding})
    results = list(cursor)
    
    # Filter by minimum score in Python (if needed)
    min_score = 0.7  # Example threshold
    results = [r for r in results if r["similarity_score"] >= min_score]
    
    return results
```

### Two-Stage ArangoDB Approach (Filtered Queries)

For queries requiring filtering, use a two-stage approach:

```python
def filtered_semantic_search(db, query_embedding, filter_expr, collection_name, embedding_field, min_score=0.7, top_n=10):
    """
    Two-stage semantic search with filtering.
    
    Stage 1: Get documents matching filter criteria
    Stage 2: Perform vector search on all documents
    Stage 3: Join results in Python
    """
    # Stage 1: Get filtered documents
    filter_query = f"""
    FOR doc IN {collection_name}
    FILTER {filter_expr}
    RETURN doc
    """
    
    filtered_docs_cursor = db.aql.execute(filter_query)
    filtered_docs = list(filtered_docs_cursor)
    
    if not filtered_docs:
        return []
    
    # Create lookup map for joining results
    filtered_ids_map = {doc["_id"]: doc for doc in filtered_docs}
    
    # Stage 2: Perform vector search (no filtering)
    vector_query = f"""
    FOR doc IN {collection_name}
    LET score = APPROX_NEAR_COSINE(doc.{embedding_field}, @query_embedding)
    SORT score DESC
    LIMIT {top_n * 10}  # Get extra results to ensure enough after filtering
    RETURN {{
        "id": doc._id,
        "similarity_score": score
    }}
    """
    
    cursor = db.aql.execute(vector_query, bind_vars={"query_embedding": query_embedding})
    vector_results = list(cursor)
    
    # Stage 3: Join results in Python
    results = []
    for result in vector_results:
        doc_id = result["id"]
        score = result["similarity_score"]
        
        # Skip documents that don't meet criteria
        if score < min_score or doc_id not in filtered_ids_map:
            continue
        
        # Add matching document to results
        results.append({
            "doc": filtered_ids_map[doc_id],
            "similarity_score": score
        })
        
        # Stop once we have enough results
        if len(results) >= top_n:
            break
    
    return results
```

### PyTorch-based Search (Complex Nesting)

For complex queries with nesting, download data and use PyTorch:

```python
def pytorch_semantic_search(db, query_embedding, filter_conditions, collection_name, embedding_field, min_score=0.7, top_n=10):
    """
    PyTorch-based semantic search for complex nesting.
    
    This approach:
    1. Downloads filtered documents from ArangoDB
    2. Uses PyTorch for similarity calculations
    3. Returns formatted results
    """
    import torch
    import numpy as np
    from complexity.arangodb.search_api.pytorch_search import (
        load_documents_from_arango,
        pytorch_enhanced_search
    )
    
    # Load documents with filtering
    embeddings, ids, metadata = load_documents_from_arango(
        db, collection_name, embedding_field,
        filter_conditions=filter_conditions
    )
    
    if embeddings is None or len(embeddings) == 0:
        return []
    
    # Check if GPU is available
    has_gpu = torch.cuda.is_available()
    
    # Perform similarity search
    results, _ = pytorch_enhanced_search(
        embeddings=embeddings,
        query_embedding=query_embedding,
        ids=ids,
        metadata=metadata,
        threshold=min_score,
        top_k=top_n,
        batch_size=128,
        fp16=has_gpu,
        cuda_streams=has_gpu,
        use_ann=(len(embeddings) > 5000)
    )
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_result = {
            "doc": result["metadata"],
            "similarity_score": result["similarity"]
        }
        formatted_results.append(formatted_result)
    
    return formatted_results
```

## 4. Text Search with ArangoSearch

### Setting Up ArangoSearch View

```python
# Note: This function was previously named ensure_view
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

### BM25 Search

BM25 is a text relevance algorithm that works well with ArangoSearch:

```python
def bm25_search(db, query_text, collection_name="complexity", view_name="complexity_view", min_score=0.0, top_n=10):
    """
    Perform BM25 text search.
    
    Args:
        db: ArangoDB database
        query_text: Search query
        collection_name: Collection to search
        view_name: ArangoSearch view
        min_score: Minimum BM25 score
        top_n: Maximum results to return
        
    Returns:
        List of matching documents with scores
    """
    # Build the AQL query with BM25 scoring
    aql = f"""
    LET search_tokens = TOKENS(@query, "text_en")
    FOR doc IN {view_name}
    SEARCH ANALYZER(doc.question IN search_tokens, "text_en") OR
           ANALYZER(doc.answer IN search_tokens, "text_en")
    LET score = BM25(doc)
    FILTER score >= @min_score
    SORT score DESC
    LIMIT {top_n}
    RETURN {{
        "doc": doc,
        "score": score
    }}
    """
    
    # Execute the query
    cursor = db.aql.execute(aql, bind_vars={
        "query": query_text,
        "min_score": min_score
    })
    
    return list(cursor)
```

### Tokenization and Analyzers

Tokenization is crucial for text search. ArangoDB provides several analyzers:

```python
def ensure_analyzers(db):
    """Ensure required analyzers exist."""
    required_analyzers = [
        # Standard analyzers
        "text_en",            # English text analyzer
        "identity",           # Identity analyzer (no changes)
        
        # Custom analyzers (if needed)
        "text_custom",        # Custom text analyzer
    ]
    
    existing_analyzers = {a["name"] for a in db.analyzers()}
    
    # Create custom analyzer if needed
    if "text_custom" not in existing_analyzers:
        db.create_analyzer(
            "text_custom",
            "text",
            {
                "locale": "en",
                "case": "lower",
                "stopwords": [],
                "stemming": True
            },
            ["frequency", "norm", "position"]
        )
    
    return required_analyzers
```

## 5. Graph Traversal

ArangoDB excels at graph operations:

```python
def ensure_graph(db, graph_name="knowledge_graph", edge_collection="relationships", vertex_collection="complexity"):
    """Ensures the graph defining relationships exists."""
    try:
        if not (db.has_collection(vertex_collection) and db.has_collection(edge_collection)):
            logger.error("Cannot ensure graph: Required collections missing.")
            sys.exit(1)

        if not db.has_graph(graph_name):
            logger.info(f"Graph '{graph_name}' not found. Creating...")
            edge_def = {
                "edge_collection": edge_collection,
                "from_vertex_collections": [vertex_collection],
                "to_vertex_collections": [vertex_collection],
            }
            db.create_graph(graph_name, edge_definitions=[edge_def])
            logger.info(f"Graph '{graph_name}' created.")
        else:
            logger.info(f"Graph '{graph_name}' already exists.")
        
        return db.graph(graph_name)
    except Exception as e:
        logger.exception(f"Failed to ensure graph: {e}")
        sys.exit(1)

def create_relationship(db, from_id, to_id, relationship_type, edge_collection="relationships"):
    """Create a relationship (edge) between two documents."""
    edges = db.collection(edge_collection)
    edge = {
        "_from": from_id,
        "_to": to_id,
        "type": relationship_type,
        "created_at": int(time.time())
    }
    return edges.insert(edge)

def traverse_graph(db, start_vertex_id, min_depth=1, max_depth=1, direction="OUTBOUND", graph_name="knowledge_graph"):
    """
    Traverse the graph from a start vertex.
    
    Args:
        db: ArangoDB database
        start_vertex_id: ID of starting vertex
        min_depth: Minimum traversal depth
        max_depth: Maximum traversal depth
        direction: OUTBOUND, INBOUND, or ANY
        graph_name: Name of the graph
    
    Returns:
        List of vertices and paths
    """
    aql = f"""
    FOR v, e, p IN {min_depth}..{max_depth} {direction} @start_vertex GRAPH @graph_name
    RETURN {{
        "vertex": v,
        "edge": e,
        "path": p
    }}
    """
    
    cursor = db.aql.execute(aql, bind_vars={
        "start_vertex": start_vertex_id,
        "graph_name": graph_name
    })
    
    return list(cursor)
```

## 6. Testing and Validation

### Creating Test Documents

```python
def create_test_documents(db, collection_name="complexity"):
    """Create some test documents for validation."""
    try:
        col = db.collection(collection_name)
        logger.info(f"Truncating collection '{collection_name}'...")
        col.truncate()
        logger.info(f"Collection '{collection_name}' truncated.")

        # Import embedding function
        from complexity.arangodb.embedding_utils import get_embedding

        docs = [
            {"_key": "doc1", "problem": "Python error when processing JSON data",
             "solution": "Use try/except blocks to handle JSON parsing exceptions",
             "context": "Error handling in data processing", "tags": ["python", "json", "error-handling"]},
            {"_key": "doc2", "problem": "Python script runs out of memory with large datasets",
             "solution": "Use chunking to process large data incrementally",
             "context": "Performance optimization", "tags": ["python", "memory", "optimization"]},
            {"_key": "doc3", "problem": "Need to search documents efficiently",
             "solution": "Use ArangoDB's vector search with embeddings",
             "context": "Document retrieval", "tags": ["arangodb", "vector-search", "embeddings"]},
        ]

        logger.info("Generating and adding embeddings to test documents...")
        for doc in docs:
            text = f"{doc['problem']} {doc['solution']} {doc['context']}"
            vec = get_embedding(text)
            doc["embedding"] = vec
            col.insert(doc, overwrite=True)
            logger.info(f"Inserted/updated document '{doc['_key']}'.")

        count = col.count()
        logger.info(f"Collection '{collection_name}' now contains {count} documents.")
        return count
    except Exception as e:
        logger.exception(f"Failed to create test documents: {e}")
        sys.exit(1)
```

### Creating Test Relationships

```python
def create_test_relationships(db, edge_collection="relationships", vertex_collection="complexity"):
    """Create some test relationships for validation."""
    try:
        edge_col = db.collection(edge_collection)
        vert_col = db.collection(vertex_collection)

        if edge_col.count() > 0:
            logger.info(f"Edge collection '{edge_collection}' already populated.")
            return edge_col.count()

        rels = [
            {"_from": f"{vertex_collection}/doc1", "_to": f"{vertex_collection}/doc3",
             "type": "related_python_issue", "weight": 0.7},
            {"_from": f"{vertex_collection}/doc2", "_to": f"{vertex_collection}/doc3",
             "type": "related_performance_issue", "weight": 0.5},
        ]

        for r in rels:
            edge_col.insert(r)
            logger.info(f"Created relationship {r['_from']} → {r['_to']}")
        
        return edge_col.count()
    except Exception as e:
        logger.exception(f"Failed to create test relationships: {e}")
        sys.exit(1)
```

### Validating Setup

```python
def validate_setup(db):
    """Validate database setup end-to-end."""
    failures = {}
    collection_name = "complexity"
    edge_collection = "relationships"
    view_name = "complexity_view"
    graph_name = "knowledge_graph"

    try:
        # Check collections
        if not db.has_collection(collection_name):
            failures["missing_collection"] = {"expected": f"{collection_name} exists", "actual": "Not found"}
        
        if not db.has_collection(edge_collection):
            failures["missing_edge_collection"] = {"expected": f"{edge_collection} exists", "actual": "Not found"}
        
        # Check graph
        if not db.has_graph(graph_name):
            failures["missing_graph"] = {"expected": f"{graph_name} exists", "actual": "Not found"}
        
        # Check view
        if not any(v["name"] == view_name for v in db.views()):
            failures["missing_view"] = {"expected": f"{view_name} exists", "actual": "Not found"}
        
        # Check vector index
        col = db.collection(collection_name)
        has_vector_index = False
        for idx in col.indexes():
            if idx.get("type") == "vector" and "embedding" in idx.get("fields", []):
                has_vector_index = True
                break
        
        if not has_vector_index:
            failures["missing_vector_index"] = {"expected": "Vector index exists", "actual": "Not found"}
        
        # Check document counts
        if col.count() < 3:
            failures["document_count"] = {"expected": "At least 3", "actual": col.count()}
        
        # Return validation results
        return len(failures) == 0, failures

    except Exception as e:
        logger.exception(f"Validation error: {e}")
        return False, {"validation_error": {"expected": "no exception", "actual": str(e)}}
```

## 7. Complete Setup Script

Here's a complete setup script that brings everything together:

```python
def setup_arango():
    """Complete setup for ArangoDB."""
    import time
    from loguru import logger
    import sys
    
    logger.add(sys.stderr,
            format="{time:HH:mm:ss} | {level:<5} | {message}",
            level="INFO",
            colorize=True)
            
    try:
        # 1. Connect to ArangoDB
        client = connect_arango()
        db = ensure_database(client)
        
        # 2. Create collections
        ensure_collection(db, "complexity")
        ensure_edge_collection(db, "relationships")
        
        # 3. Create test data
        create_test_documents(db, "complexity")
        create_test_relationships(db, "relationships", "complexity") 
        
        # 4. Setup graph
        ensure_graph(db, "knowledge_graph", "relationships", "complexity")
        
        # 5. Setup search
        ensure_arangosearch_view(db, "complexity_view", "complexity")
        
        # 6. Create vector index
        collection = db.collection("complexity")
        create_vector_index(collection, "embedding", 1024)
        
        # 7. Validate setup
        passed, errors = validate_setup(db)
        if passed:
            logger.info("✅ ArangoDB setup completed successfully.")
            return True
        else:
            logger.error("❌ Validation failed:")
            for key, detail in errors.items():
                logger.error(f"  - {key}: expected={detail['expected']}, actual={detail['actual']}")
            return False
            
    except Exception as e:
        logger.exception(f"❌ ERROR during setup: {e}")
        return False

if __name__ == "__main__":
    setup_arango()
```