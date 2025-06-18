# Environment Setup Guide

## Step 1: Create .env File

Create a `.env` file in the `langchain_service` directory with the following contents:

```bash
# ===============================================
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
```

## Step 2: Required Configuration

### 🔑 Essential Variables (Must Configure):

1. **OPENAI_API_KEY** - Your OpenAI API key
   - Sign up at https://platform.openai.com/
   - Go to API keys section
   - Create a new secret key
   - Make sure you have credits in your account

2. **RAILS_API_KEY** - API key for Rails backend communication
   - This will be set up in the Rails backend configuration

### ⚙️ Optional Configuration:

- **OPENAI_MODEL**: Change to `gpt-4` for better responses (costs more)
- **OPENAI_TEMPERATURE**: 0.0-1.0 (lower = more focused, higher = more creative)  
- **MAX_CONTEXT_NOTES**: Number of notes to include as context (3-10)
- **EMBEDDINGS_MODEL**: Sentence transformer model for embeddings

## Step 3: Quick Setup Command

```bash
# Navigate to langchain_service directory
cd langchain_service

# Copy and create .env file (you'll need to edit it)
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
HOST=0.0.0.0
PORT=8001
CHROMA_PERSIST_DIR=./data/chroma
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
RAILS_API_URL=http://localhost:8000
RAILS_API_KEY=your_rails_api_key_here
LOG_LEVEL=INFO
MAX_CONTEXT_NOTES=5
CONVERSATION_WINDOW=10
RELEVANCE_THRESHOLD=0.3
RELOAD=true
DEBUG=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_TOKENS=1000
REQUEST_TIMEOUT=30
EOF

# Edit the file to add your actual API keys
nano .env  # or use your preferred editor
```

## Step 4: Verify Configuration

After creating the `.env` file, you can test it by running:

```bash
# Check if environment loads correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

## Security Notes

- **Never commit your `.env` file to version control**
- Keep your OpenAI API key secure
- The `.env` file should already be in `.gitignore`
- Consider using environment-specific files for production (.env.production)

---

✅ **Next Step**: After creating your `.env` file with the correct API keys, you'll be ready for Step 2.5: Create Startup Script 