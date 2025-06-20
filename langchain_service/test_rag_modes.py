#!/usr/bin/env python3
"""
Test script to demonstrate switching between traditional and LangGraph RAG modes
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from app.services.rag_service import RAGService
    from app.services.vector_store_service import VectorStoreService
except ImportError:
    # If running from different location, try absolute import
    from langchain_service.app.services.rag_service import RAGService
    from langchain_service.app.services.vector_store_service import VectorStoreService


async def test_rag_modes():
    """Test both RAG modes and compare responses"""
    
    # Initialize vector store (this would normally be done in your app startup)
    print("Initializing vector store...")
    vector_store = VectorStoreService()
    await vector_store.initialize()
    
    test_question = "What is machine learning?"
    
    print(f"\nTesting question: '{test_question}'\n")
    
    # Test Traditional RAG
    print("=" * 50)
    print("TESTING TRADITIONAL RAG")
    print("=" * 50)
    
    try:
        traditional_rag = RAGService(vector_store, use_langgraph=False)
        await traditional_rag.initialize()
        
        traditional_response = await traditional_rag.chat(test_question)
        stats = traditional_rag.get_service_stats()
        
        print(f"Service type: {stats['service_type']}")
        print(f"Response: {traditional_response.response}")
        print(f"Sources found: {len(traditional_response.sources)}")
        print(f"Tokens used: {traditional_response.tokens_used}")
        
    except Exception as e:
        print(f"Error with traditional RAG: {e}")
    
    # Test LangGraph RAG
    print("\n" + "=" * 50)
    print("TESTING LANGGRAPH RAG")
    print("=" * 50)
    
    try:
        langgraph_rag = RAGService(vector_store, use_langgraph=True)
        await langgraph_rag.initialize()
        
        langgraph_response = await langgraph_rag.chat(test_question)
        stats = langgraph_rag.get_service_stats()
        
        print(f"Service type: {stats['service_type']}")
        print(f"Response: {langgraph_response.response}")
        print(f"Sources found: {len(langgraph_response.sources)}")
        print(f"Tokens used: {langgraph_response.tokens_used}")
        
    except ImportError as e:
        print(f"LangGraph dependencies not available: {e}")
        print("Install with: pip install langgraph langchain-community tavily-python")
    except Exception as e:
        print(f"Error with LangGraph RAG: {e}")
    
    # Test Environment Variable Configuration
    print("\n" + "=" * 50)
    print("TESTING ENVIRONMENT VARIABLE CONFIG")
    print("=" * 50)
    
    # Test with environment variable set to true
    os.environ["USE_LANGGRAPH"] = "true"
    
    try:
        env_rag = RAGService(vector_store)  # No explicit parameter
        await env_rag.initialize()
        
        stats = env_rag.get_service_stats()
        print(f"With USE_LANGGRAPH=true, service type: {stats.get('service_type', 'unknown')}")
        
    except Exception as e:
        print(f"Environment config test failed: {e}")
    
    # Reset environment
    os.environ["USE_LANGGRAPH"] = "false"
    
    try:
        env_rag2 = RAGService(vector_store)  # No explicit parameter
        await env_rag2.initialize()
        
        stats = env_rag2.get_service_stats()
        print(f"With USE_LANGGRAPH=false, service type: {stats.get('service_type', 'unknown')}")
        
    except Exception as e:
        print(f"Environment config test failed: {e}")


async def check_dependencies():
    """Check if all required dependencies are available"""
    print("Checking dependencies...")
    
    # Basic dependencies
    try:
        import langchain
        import langchain_openai
        print("✓ Basic LangChain dependencies available")
    except ImportError as e:
        print(f"✗ Missing basic dependencies: {e}")
        return False
    
    # LangGraph dependencies
    try:
        import langgraph
        import langchain_community
        print("✓ LangGraph dependencies available")
    except ImportError as e:
        print(f"⚠ LangGraph dependencies missing: {e}")
        print("  LangGraph RAG mode will fall back to traditional mode")
    
    # Web search dependency
    try:
        import tavily
        print("✓ Tavily (web search) dependency available")
    except ImportError:
        print("⚠ Tavily dependency missing - web search will be disabled")
    
    # Check environment variables
    if os.getenv("OPENAI_API_KEY"):
        print("✓ OPENAI_API_KEY is set")
    else:
        print("✗ OPENAI_API_KEY not set - tests will fail")
        return False
    
    if os.getenv("TAVILY_API_KEY"):
        print("✓ TAVILY_API_KEY is set")
    else:
        print("⚠ TAVILY_API_KEY not set - web search will be disabled")
    
    return True


if __name__ == "__main__":
    print("RAG Service Mode Testing")
    print("=" * 50)
    
    # Check dependencies first
    if not asyncio.run(check_dependencies()):
        print("\nCannot proceed due to missing dependencies or configuration")
        sys.exit(1)
    
    print("\nStarting tests...\n")
    
    try:
        asyncio.run(test_rag_modes())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc() 