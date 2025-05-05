# Memory Agent Integration

## Overview

The Memory Agent integration provides GitGit with the ability to store, retrieve, and search through conversational history using ArangoDB's vector search capabilities. The system embeds all message exchanges, creates relationships between related conversations, and enables semantic search across the memory bank.

## Key Features

1. **Conversation Storage**
   - Stores user-agent message exchanges in ArangoDB
   - Creates embeddings for each message and the combined exchange
   - Maintains conversation context and history

2. **Semantic Search**
   - Uses hybrid search (BM25 + vector similarity) to find relevant past conversations
   - Configurable search parameters for precision tuning
   - Tag-based filtering for domain-specific searches

3. **Relationship Management**
   - Automatically creates relationships between semantically similar conversations
   - Uses the RelationshipBuilder to generate AI-powered relationship rationales
   - Calculates accurate similarity scores based on vector embeddings
   - Builds a knowledge graph of related topics
   - Enables graph traversal to discover related information

4. **Memory Retrieval**
   - Fetches conversation context for contextual understanding
   - Retrieves related memories based on semantic similarity
   - Supports different relationship types and traversal depths

## Architecture

The Memory Agent uses a multi-layered architecture:

```
┌───────────────────┐      ┌─────────────────┐     ┌───────────────────┐
│                   │      │                 │     │                   │
│  MemoryAgent API  │─────▶│  ArangoDB Ops   │────▶│  Storage Layer    │
│                   │      │                 │     │                   │
└───────────────────┘      └─────────────────┘     └───────────────────┘
         │                          │                        │
         │                          │                        │
         ▼                          ▼                        ▼
┌───────────────────┐      ┌─────────────────┐     ┌───────────────────┐
│                   │      │                 │     │                   │
│  Search Interface │◀────▶│  Hybrid Search  │◀───▶│  Embedding Layer  │
│                   │      │                 │     │                   │
└───────────────────┘      └─────────────────┘     └───────────────────┘
         │                          │                        │
         │                          │                        │
         ▼                          ▼                        ▼
┌───────────────────┐      ┌─────────────────┐     ┌───────────────────┐
│                   │      │                 │     │                   │
│ Relationship API  │◀────▶│Relationship Mgmt│◀───▶│  Graph Traversal  │
│                   │      │                 │     │                   │
└───────────────────┘      └─────────────────┘     └───────────────────┘
```

## Implementation Details

### Database Structure

The Memory Agent uses the following collections in ArangoDB:

- **agent_messages**: Stores individual messages (user or agent)
- **agent_memories**: Stores combined user-agent exchanges with metadata
- **agent_relationships**: Stores relationships between messages and memories
- **agent_memory_view**: ArangoSearch view for hybrid search

### Message Storage Schema

Each message in the `agent_messages` collection has the following structure:

```json
{
  "_key": "unique_id",
  "conversation_id": "conversation_uuid",
  "message_type": "USER" | "AGENT",
  "content": "Message content",
  "timestamp": "ISO-8601 timestamp",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "topic": "topic name",
    "tags": ["tag1", "tag2"],
    "custom_field": "custom value"
  }
}
```

### Memory Document Schema

Each memory in the `agent_memories` collection has the following structure:

```json
{
  "_key": "unique_id",
  "conversation_id": "conversation_uuid",
  "content": "User: question\nAgent: response",
  "summary": "Brief summary of the exchange",
  "timestamp": "ISO-8601 timestamp",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "topic": "topic name",
    "tags": ["tag1", "tag2"],
    "custom_field": "custom value"
  }
}
```

### Relationship Schema

Relationships in the `agent_relationships` collection have the following structure:

```json
{
  "_from": "collection/document_id",
  "_to": "collection/document_id",
  "type": "RESPONSE_TO" | "RELATED_TO" | "PART_OF",
  "timestamp": "ISO-8601 timestamp",
  "strength": 0.85,
  "rationale": "Reason for the relationship"
}
```

## Usage

### Basic Usage

```python
from complexity.arangodb.memory_agent import MemoryAgent
# Import the correct setup functions
from complexity.arangodb.arango_setup import (
    connect_arango,
    ensure_database,
    ensure_collection,
    ensure_memory_agent_collections,
    ensure_arangosearch_view
)

# Initialize the agent
memory_agent = MemoryAgent()

# Store a conversation
result = memory_agent.store_conversation(
    user_message="How do I implement quicksort in Python?",
    agent_response="Here's a quicksort implementation: [code]",
    metadata={"topic": "algorithms", "tags": ["python", "sorting"]}
)

# Search for relevant memories
memories = memory_agent.search_memory(
    query="What's the best sorting algorithm?",
    top_n=5,
    tag_filters=["python"]
)

# Get conversation context
context = memory_agent.get_conversation_context(result["conversation_id"])

# Get related memories through graph traversal
related = memory_agent.get_related_memories(result["memory_key"])
```

### Advanced Usage

#### Custom Search Parameters

```python
# Advanced search with custom parameters
results = memory_agent.search_memory(
    query="complex algorithms",
    top_n=10,
    collections=["agent_memories", "another_collection"],
    filter_expr="doc.tags[*] IN ['advanced', 'algorithms'] AND LENGTH(doc.content) > 100",
    tag_filters=["python", "algorithms"]
)
```

#### Graph Traversal

```python
# Advanced graph traversal
related = memory_agent.get_related_memories(
    memory_key="document_key",
    relationship_type="SEMANTIC_SIMILARITY",
    max_depth=3,
    limit=20
)
```

## API Reference

### MemoryAgent

#### Constructor

```python
MemoryAgent(
    db=None,
    db_name="memory_bank",
    message_collection="agent_messages",
    memory_collection="agent_memories",
    edge_collection="agent_relationships",
    view_name="agent_memory_view",
    embedding_field="embedding"
)
```

#### Methods

- **store_conversation(conversation_id, user_message, agent_response, metadata)**
  
  Stores a user-agent message exchange in the database.
  
  Returns: Dict with conversation_id, user_key, agent_key, and memory_key.

- **search_memory(query, top_n, collections, filter_expr, tag_filters)**
  
  Searches for relevant memories using hybrid search.
  
  Returns: List of matching documents with similarity scores.

- **get_related_memories(memory_key, relationship_type, max_depth, limit)**
  
  Gets related memories using graph traversal.
  
  Returns: List of related memories with relationship information.

- **get_conversation_context(conversation_id, limit)**
  
  Gets the context of a conversation by retrieving previous messages.
  
  Returns: List of messages in the conversation.

## RelationshipBuilder Integration

The Memory Agent integrates with the RelationshipBuilder component to create high-quality semantic relationships between memories:

```python
# The MemoryAgent uses a RelationshipBuilderAdapter to:
# 1. Override collection names to use configured collections
# 2. Utilize the sophisticated vector search capabilities
# 3. Generate LLM-based rationales for relationships

def _generate_relationships(self, memory_key):
    # Create adapter with our collection configuration
    builder = RelationshipBuilderAdapter(
        self.db, 
        self.memory_collection, 
        self.edge_collection
    )
    
    # Create relationships with LLM-powered rationales
    count = builder._build_relationships_direct_arangodb(threshold=0.75)
    
    # Relationships include:
    # - Accurate similarity scores (strength)
    # - LLM-generated rationales explaining the relationship
    # - Proper timestamps and metadata
    
    return count
```

The RelationshipBuilder generates meaningful rationales using LLM calls when the similarity between memories exceeds a threshold:

```python
# For high-similarity pairs, generate a specific rationale
if similarity > 0.75:
    try:
        # Create a prompt for the LLM to analyze the relationship
        prompt = f"""
        Analyze these two related conversation snippets:
        
        Snippet 1: {from_snippet}
        Snippet 2: {to_snippet}
        
        In one brief sentence (15 words or less), explain why these conversations are related or similar.
        """
        
        # Get LLM-generated rationale
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        
        # Use the generated rationale if available
        rationale = response.choices[0].message.content.strip()
    except Exception as e:
        # Fall back to default if LLM call fails
        rationale = "Semantically similar based on vector similarity"
```

## Integration with GitGit

To integrate the Memory Agent with GitGit:

1. Import the MemoryAgent class in your GitGit module
2. Initialize the agent at startup
3. Store each user-agent exchange after processing
4. Use search_memory() to retrieve relevant past conversations

Example integration in GitGit:

```python
from complexity.arangodb.memory_agent import MemoryAgent
from complexity.arangodb.arango_setup import (
    connect_arango,
    ensure_database,
    ensure_collection,
    ensure_memory_agent_collections,
    ensure_arangosearch_view
)

class GitGit:
    def __init__(self, config):
        self.config = config
        # Connect to ArangoDB
        self.client = connect_arango()
        self.db = ensure_database(self.client)
        # Initialize memory agent
        self.memory_agent = MemoryAgent(db=self.db)
        
    def process_request(self, user_query):
        # 1. Search memory for relevant past interactions
        relevant_memories = self.memory_agent.search_memory(user_query, top_n=3)
        
        # 2. Include relevant memories in the context
        context = self._build_context(user_query, relevant_memories)
        
        # 3. Process the request with the context
        response = self._generate_response(context)
        
        # 4. Store the new interaction
        self.memory_agent.store_conversation(
            user_message=user_query,
            agent_response=response,
            metadata={"source": "gitgit"}
        )
        
        return response
```

## Testing

The Memory Agent includes a comprehensive test suite in `tests/arangodb/memory_agent/test_memory_agent.py`. Run the tests with:

```bash
pytest tests/arangodb/memory_agent/test_memory_agent.py -v
```

The test suite covers:
- Storing conversations
- Searching memories
- Retrieving related memories
- Managing conversation context

## Performance Considerations

- Use `initial_k` and `top_n` parameters in search_memory() to control result count
- Set appropriate thresholds for similarity to reduce noise
- Use tag filters to narrow search scope
- Consider implementing caching for frequently accessed memories
- For large-scale deployments, consider scaling ArangoDB horizontally

## Security Notes

- The Memory Agent stores all conversation data in ArangoDB
- Ensure proper authentication and authorization for ArangoDB access
- Consider encryption for sensitive data in the metadata field
- Implement data retention policies for conversation data

## Future Enhancements

1. LLM-based summarization for longer conversations
2. Automatic tagging of conversations using content analysis
3. Enhanced relationship detection using causality analysis
4. Multi-modal memory storage (text, images, code)
5. Memory consolidation for repeated information
6. Forgetting mechanisms for outdated information
7. Confidence scoring for memory retrieval

## References

- [ArangoDB Documentation](https://www.arangodb.com/docs/stable/)
- [Vector Search in ArangoDB](https://www.arangodb.com/docs/stable/arangosearch.html)
- [Hybrid Search Implementation](https://www.arangodb.com/docs/stable/aql/functions-search.html)