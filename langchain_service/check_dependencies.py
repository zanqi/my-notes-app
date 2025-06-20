#!/usr/bin/env python3
"""
Dependency checker script to verify all requirements work together
"""

import sys
import importlib
from typing import List, Tuple

def check_import(module_name: str, friendly_name: str | None = None) -> Tuple[bool, str]:
    """Check if a module can be imported"""
    display_name = friendly_name or module_name
    try:
        importlib.import_module(module_name)
        return True, f"✓ {display_name}"
    except ImportError as e:
        return False, f"✗ {display_name}: {e}"
    except Exception as e:
        return False, f"⚠ {display_name}: {e}"

def check_version_compatibility():
    """Check version compatibility for critical packages"""
    results = []
    
    try:
        import pydantic
        results.append(f"✓ Pydantic version: {pydantic.version.VERSION}")
    except Exception as e:
        results.append(f"✗ Pydantic version check failed: {e}")
    
    try:
        import fastapi  # type: ignore
        results.append(f"✓ FastAPI version: {fastapi.__version__}")
    except Exception as e:
        results.append(f"✗ FastAPI version check failed: {e}")
    
    try:
        import langchain
        results.append(f"✓ LangChain version: {langchain.__version__}")
    except Exception as e:
        results.append(f"✗ LangChain version check failed: {e}")
    
    return results

def main():
    """Main dependency checker"""
    print("🔍 Checking Dependencies for LangGraph RAG Service")
    print("=" * 60)
    
    # Core dependencies
    core_deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("python_dotenv", "Python Dotenv"),
        ("httpx", "HTTPX"),
        ("requests", "Requests"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("structlog", "StructLog"),
    ]
    
    # LangChain dependencies
    langchain_deps = [
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_core", "LangChain Core"),
        ("langchain_text_splitters", "LangChain Text Splitters"),
        ("openai", "OpenAI"),
    ]
    
    # LangGraph dependencies (optional)
    langgraph_deps = [
        ("langgraph", "LangGraph"),
        ("langchain_community", "LangChain Community"),
        ("tavily", "Tavily (Web Search)"),
    ]
    
    # Vector store dependencies
    vector_deps = [
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
    ]
    
    # Development dependencies
    dev_deps = [
        ("pytest", "Pytest"),
        ("pytest_asyncio", "Pytest Asyncio"),
    ]
    
    all_passed = True
    
    # Check each category
    categories = [
        ("Core Dependencies", core_deps),
        ("LangChain Dependencies", langchain_deps),
        ("LangGraph Dependencies (Optional)", langgraph_deps),
        ("Vector Store Dependencies", vector_deps),
        ("Development Dependencies", dev_deps),
    ]
    
    for category_name, deps in categories:
        print(f"\n📦 {category_name}")
        print("-" * len(category_name))
        
        category_passed = True
        for module_name, friendly_name in deps:
            passed, message = check_import(module_name, friendly_name)
            print(f"  {message}")
            if not passed:
                category_passed = False
                if "Optional" not in category_name:
                    all_passed = False
        
        if category_passed:
            print(f"  ✅ All {category_name.lower()} working!")
        elif "Optional" in category_name:
            print(f"  ⚠️  Some optional dependencies missing (LangGraph features will be disabled)")
        else:
            print(f"  ❌ Some {category_name.lower()} failed!")
    
    # Check version compatibility
    print(f"\n🔧 Version Compatibility Check")
    print("-" * 30)
    version_results = check_version_compatibility()
    for result in version_results:
        print(f"  {result}")
    
    # Test basic functionality
    print(f"\n🧪 Basic Functionality Test")
    print("-" * 25)
    
    try:
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        test = TestModel(name="test", value=42)
        print(f"  ✓ Pydantic models working: {test.name}={test.value}")
    except Exception as e:
        print(f"  ✗ Pydantic test failed: {e}")
        all_passed = False
    
    try:
        import langchain_core
        print(f"  ✓ LangChain core imports working")
    except Exception as e:
        print(f"  ✗ LangChain core test failed: {e}")
        all_passed = False
    
    # Final summary
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL DEPENDENCIES WORKING! Ready to use both RAG modes.")
    else:
        print("⚠️  SOME ISSUES FOUND. Traditional RAG should work, LangGraph may have issues.")
    
    print(f"\n💡 Next steps:")
    if all_passed:
        print("   • Set your environment variables (OPENAI_API_KEY, etc.)")
        print("   • Run: python test_rag_modes.py")
        print("   • Start using the RAG service!")
    else:
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Check for version conflicts")
        print("   • Re-run this checker")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 