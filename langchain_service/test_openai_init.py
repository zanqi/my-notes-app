#!/usr/bin/env python3
"""
Test script to verify OpenAI initialization works correctly
"""

import os
import sys
from pathlib import Path

def test_openai_init():
    """Test OpenAI and LangChain OpenAI initialization"""
    
    print("🔍 Testing OpenAI Initialization")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        print("💡 Set your API key: export OPENAI_API_KEY=your_key")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    
    # Test basic OpenAI import
    try:
        import openai
        print(f"✅ OpenAI library imported (version: {openai.__version__})")
    except Exception as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    # Test basic OpenAI client
    try:
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OpenAI client: {e}")
        print(f"Error details: {type(e).__name__}: {e}")
        return False
    
    # Test LangChain OpenAI import
    try:
        from langchain_openai import ChatOpenAI
        print("✅ LangChain OpenAI imported")
    except Exception as e:
        print(f"❌ Failed to import LangChain OpenAI: {e}")
        return False
    
    # Test LangChain OpenAI initialization with SecretStr
    try:
        from pydantic import SecretStr
        llm = ChatOpenAI(
            api_key=SecretStr(api_key),
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        print("✅ ChatOpenAI with SecretStr created successfully")
    except Exception as e:
        print(f"❌ Failed to create ChatOpenAI with SecretStr: {e}")
        print(f"Error details: {type(e).__name__}: {e}")
        return False
    
    # Test LangChain OpenAI initialization without SecretStr
    try:
        llm2 = ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo", 
            temperature=0.7
        )
        print("✅ ChatOpenAI without SecretStr created successfully")
    except Exception as e:
        print(f"❌ Failed to create ChatOpenAI without SecretStr: {e}")
        print(f"Error details: {type(e).__name__}: {e}")
        # This might fail but that's ok, we'll use SecretStr version
    
    # Test a simple LLM call (optional)
    try_llm_call = input("\n🤔 Test actual LLM call? (y/N): ").lower().strip() == 'y'
    
    if try_llm_call:
        try:
            from langchain.schema import HumanMessage
            messages = [HumanMessage(content="Say 'Hello from LangChain!'")]
            response = llm.invoke(messages)
            print(f"✅ LLM call successful: {response.content}")
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            print("💡 This might be due to API limits, network issues, or invalid API key")
    
    print("\n🎉 All basic tests passed!")
    return True

def show_versions():
    """Show relevant package versions"""
    print("\n📦 Package Versions:")
    print("-" * 20)
    
    packages = [
        "openai",
        "langchain",
        "langchain_openai", 
        "langchain_core",
        "pydantic",
        "httpx"
    ]
    
    for package in packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"  {package}: {version}")
        except ImportError:
            print(f"  {package}: not installed")
        except Exception as e:
            print(f"  {package}: error - {e}")

if __name__ == "__main__":
    print("OpenAI Initialization Test")
    print("=" * 40)
    
    show_versions()
    
    success = test_openai_init()
    
    if success:
        print("\n✅ Ready to use the RAG service!")
    else:
        print("\n❌ Please fix the issues above before using the RAG service")
        print("\n💡 Troubleshooting tips:")
        print("   • Make sure OPENAI_API_KEY is set correctly")
        print("   • Try: pip install -r requirements.txt")
        print("   • Check for conflicting package versions")
        
    sys.exit(0 if success else 1) 