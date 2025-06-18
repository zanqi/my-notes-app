# LangChain Service Startup Guide 🚀

Complete guide for starting and managing the LangChain Service with multiple startup options and development tools.

## Quick Start Options

### Option 1: Bash Script (Recommended for macOS/Linux)
```bash
cd langchain_service
./start.sh
```

### Option 2: Python Script (Cross-platform)
```bash
cd langchain_service
python start.py
```

### Option 3: Manual Setup
```bash
cd langchain_service
python setup_env.py           # Create .env file
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

## 📋 Prerequisites

- **Python 3.8+** installed
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Internet connection** (for dependencies and AI model)

## 🔧 Setup Process

Both startup scripts automatically handle:

1. ✅ **Python Environment Check** - Validates Python installation
2. ✅ **Virtual Environment** - Creates and activates Python venv
3. ✅ **Dependencies** - Installs all required packages
4. ✅ **Environment Configuration** - Creates `.env` file if missing
5. ✅ **Data Directories** - Sets up ChromaDB and logs folders
6. ✅ **Service Launch** - Starts the FastAPI server

## 🗂️ File Overview

| File | Purpose | Platform |
|------|---------|----------|
| `start.sh` | Bash startup script | macOS/Linux |
| `start.py` | Python startup script | Cross-platform |
| `setup_env.py` | Environment setup utility | All |
| `dev_tools.py` | Development testing tools | All |
| `environment_setup.md` | Manual setup guide | All |

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with these essential settings:

```bash
# Essential - You MUST set these
OPENAI_API_KEY=your_openai_api_key_here
RAILS_API_KEY=dev-local-123

# Server settings (defaults shown)
HOST=0.0.0.0
PORT=8001

# AI Configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
MAX_CONTEXT_NOTES=5
```

### Quick Environment Setup
```bash
# Auto-create .env file
python setup_env.py

# Validate configuration
python setup_env.py validate
```

## 🧪 Development Tools

Use the development tools for testing and debugging:

```bash
# Health check
python dev_tools.py health

# Test chat functionality
python dev_tools.py chat -m "What notes do I have?"

# Sync test notes for development
python dev_tools.py sync

# Run all tests
python dev_tools.py test

# Show current configuration
python dev_tools.py config
```

## 🌐 Service Endpoints

Once running, the service provides these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:8001/` | GET | Basic health check |
| `http://localhost:8001/health` | GET | Detailed health status |
| `http://localhost:8001/chat` | POST | AI chat with RAG |
| `http://localhost:8001/sync_notes` | POST | Sync notes to vector store |
| `http://localhost:8001/add_note` | POST | Add single note |
| `http://localhost:8001/notes/{id}` | DELETE | Remove note |

## 🔍 Testing the Service

### 1. Health Check
```bash
curl http://localhost:8001/health
```

### 2. Chat Test
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me with my notes?"}'
```

### 3. Sync Test Notes
```bash
python dev_tools.py sync
python dev_tools.py chat -m "What notes do I have about development?"
```

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
- Check Python version: `python --version` (need 3.8+)
- Verify OpenAI API key in `.env` file
- Check port 8001 isn't already in use: `lsof -i :8001`

**Import errors:**
- Virtual environment not activated
- Run `pip install -r requirements.txt` in the venv

**OpenAI errors:**
- Invalid API key
- No credits remaining in OpenAI account
- Rate limits exceeded

**Vector store issues:**
- Delete `data/chroma` directory and restart
- Check disk space available

### Debug Commands

```bash
# Check service logs
python dev_tools.py logs

# Validate environment
python setup_env.py validate

# Check configuration
python dev_tools.py config

# Test all endpoints
python dev_tools.py test
```

## 📊 Service Status

**Running Successfully When You See:**
```
✅ Python found: 3.x.x
✅ Virtual environment activated  
✅ Dependencies installed
✅ Environment configuration is valid
✅ Data directories created
🎉 Setup complete! Starting service...
ℹ️  Service starting on http://0.0.0.0:8001
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "services": {
    "rag_service": "running", 
    "vector_store": "running"
  },
  "collection_info": {
    "collection_name": "notes_collection",
    "document_count": 0
  }
}
```

## 🔄 Development Workflow

1. **Start Service:** `./start.sh` or `python start.py`
2. **Add Test Data:** `python dev_tools.py sync`
3. **Test Chat:** `python dev_tools.py chat`
4. **Monitor Health:** `python dev_tools.py health`
5. **Make Changes:** Edit code (service auto-reloads in dev mode)
6. **Test Again:** `python dev_tools.py test`

## 🛑 Stopping the Service

- **Ctrl+C** in the terminal where it's running
- Service handles graceful shutdown automatically

## 📁 Directory Structure

```
langchain_service/
├── start.sh              # Bash startup script
├── start.py              # Python startup script  
├── setup_env.py          # Environment setup
├── dev_tools.py          # Development tools
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (create this)
├── venv/                 # Virtual environment
├── data/chroma/         # Vector database
├── logs/                # Service logs
└── app/                 # Application code
    ├── models/          # Pydantic models
    └── services/        # Business logic
```

## 🎯 Next Steps

After successfully starting the service:

1. **Configure OpenAI API Key** in `.env` file
2. **Test with sample data:** `python dev_tools.py sync`
3. **Try chat functionality:** Visit http://localhost:8001 
4. **Integrate with Rails API** (Phase 1 of the project)
5. **Add frontend integration** (Phase 3 of the project)

---

## 🆘 Getting Help

If you encounter issues:

1. Check this README first
2. Run `python dev_tools.py test` for diagnostics
3. Validate environment: `python setup_env.py validate`
4. Check service logs and console output
5. Verify OpenAI API key and credits

**Happy coding! 🎉** 