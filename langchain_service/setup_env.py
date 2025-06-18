#!/usr/bin/env python3
"""
Environment Setup Script for LangChain Service
Helps create a .env file with proper configuration
"""

import os
import sys

ENV_TEMPLATE = """# ===============================================
# LangChain Service Environment Configuration
# ===============================================

# OpenAI Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Vector Store Configuration (ChromaDB)
CHROMA_PERSIST_DIR=./data/chroma
EMBEDDINGS_MODEL=all-MiniLM-L6-v2

# Rails API Configuration
RAILS_API_URL=http://localhost:8000
RAILS_API_KEY=your_rails_api_key_here

# Logging Configuration
LOG_LEVEL=INFO

# RAG Configuration
MAX_CONTEXT_NOTES=5
CONVERSATION_WINDOW=10
RELEVANCE_THRESHOLD=0.3

# Development Settings
RELOAD=true
DEBUG=false

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Performance Settings
MAX_TOKENS=1000
REQUEST_TIMEOUT=30
"""

def create_env_file():
    """Create .env file from template"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        response = input(f"⚠️  {env_path} already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled.")
            return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(ENV_TEMPLATE)
        
        print(f"✅ Created {env_path}")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and add your OpenAI API key")
        print("2. Get your API key from: https://platform.openai.com/api-keys")
        print("3. Replace 'your_openai_api_key_here' with your actual key")
        print("\n🔧 To edit the file:")
        print(f"   nano {env_path}")
        print(f"   # or use your preferred editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating {env_path}: {e}")
        return False

def validate_env():
    """Validate existing .env file"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print(f"❌ {env_path} not found. Run this script to create it.")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check required variables
        required_vars = [
            "OPENAI_API_KEY",
            "PORT",
            "HOST"
        ]
        
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif "your_" in value.lower() or "here" in value.lower():
                placeholder_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required variables: {', '.join(missing_vars)}")
            return False
        
        if placeholder_vars:
            print(f"⚠️  Placeholder values found in: {', '.join(placeholder_vars)}")
            print("   Please update these with your actual values.")
            return False
        
        print("✅ Environment configuration looks good!")
        
        # Show current config
        print("\n📋 Current configuration:")
        print(f"   OpenAI Model: {os.getenv('OPENAI_MODEL', 'Not set')}")
        print(f"   Server Port: {os.getenv('PORT', 'Not set')}")
        print(f"   Vector Store: {os.getenv('CHROMA_PERSIST_DIR', 'Not set')}")
        print(f"   Embeddings Model: {os.getenv('EMBEDDINGS_MODEL', 'Not set')}")
        
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error validating environment: {e}")
        return False

def main():
    """Main function"""
    print("🚀 LangChain Service Environment Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        print("🔍 Validating existing .env file...")
        validate_env()
    else:
        print("📁 Creating .env file...")
        if create_env_file():
            print("\n🔍 Validating configuration...")
            validate_env()

if __name__ == "__main__":
    main() 