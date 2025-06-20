# LangGraph RAG Implementation

This service now supports two different RAG approaches:
1. **Traditional RAG** - Direct LLM calls with context injection
2. **LangGraph RAG** - Graph-based workflow with automatic document grading, web search, and hallucination detection

## Configuration

You can switch between the two approaches using environment variables or direct parameters:

### Environment Variable (Recommended)
```bash
# Use traditional RAG (default)
USE_LANGGRAPH=false

# Use LangGraph RAG
USE_LANGGRAPH=true
```

### Direct Parameter
```python
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService

vector_store = VectorStoreService()
await vector_store.initialize()

# Traditional RAG
rag_service = RAGService(vector_store, use_langgraph=False)

# LangGraph RAG
rag_service = RAGService(vector_store, use_langgraph=True)

await rag_service.initialize()
```

## LangGraph Features

When using LangGraph mode, you get additional capabilities:

### 1. Document Relevance Grading
- Automatically filters out irrelevant retrieved documents
- Uses an LLM to assess document relevance to the query

### 2. Web Search Fallback
- If no relevant documents are found, automatically searches the web
- Requires `TAVILY_API_KEY` environment variable
- Integrates web results with local knowledge

### 3. Hallucination Detection
- Checks if generated answers are grounded in the source documents
- Regenerates answers if they're not properly supported

### 4. Answer Quality Assessment
- Evaluates if the generated answer is useful for the query
- Triggers web search for additional context if needed

## Environment Variables

### Required for both modes:
```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo  # optional, defaults to gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7      # optional, defaults to 0.7
```

### Required for LangGraph mode:
```bash
USE_LANGGRAPH=true
```

### Optional for LangGraph mode:
```bash
TAVILY_API_KEY=your_tavily_api_key  # for web search functionality
```

## Dependencies

**Important**: Due to complex version dependencies, install all requirements together:

```bash
# Recommended: Install all requirements at once
pip install -r requirements.txt

# Quick test after installation
python quick_test.py
```

**Note**: Individual package installation may cause version conflicts. The requirements.txt contains tested compatible versions:
- `openai==1.54.0` 
- `langchain-openai==0.2.8` (requires openai>=1.54.0)
- `httpx==0.25.2` (avoids proxies parameter issues)

If LangGraph dependencies are not available, the service will automatically fall back to traditional RAG mode.

## Usage Example

```python
import asyncio
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService

async def main():
    # Initialize services
    vector_store = VectorStoreService()
    await vector_store.initialize()
    
    # Create RAG service (will use environment variable or default to traditional)
    rag_service = RAGService(vector_store)
    await rag_service.initialize()
    
    # Chat with the service
    response = await rag_service.chat("What is machine learning?")
    print(f"Response: {response.response}")
    print(f"Service type: {rag_service.get_service_stats()['service_type']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Performance Considerations

- **Traditional RAG**: Faster, simpler, fewer API calls
- **LangGraph RAG**: More robust, higher quality, but more API calls and higher cost

Choose based on your needs:
- Use traditional RAG for speed and cost efficiency
- Use LangGraph RAG for higher quality and more reliable responses

## Monitoring

You can check which service is active using:

```python
stats = rag_service.get_service_stats()
print(f"Service type: {stats['service_type']}")  # "traditional" or "langgraph"
```

## Troubleshooting

1. **LangGraph not working**: Check that dependencies are installed
2. **Web search not working**: Ensure TAVILY_API_KEY is set
3. **High API costs**: Consider switching to traditional RAG for cost optimization
4. **Slow responses**: LangGraph mode uses multiple LLM calls and may be slower 