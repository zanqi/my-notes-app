#!/bin/bash
# ===============================================
# LangChain Service Startup Script
# ===============================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 LangChain Service Startup${NC}"
echo "========================================"

# Function to print colored messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is available
check_python() {
    print_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
        print_status "Python found: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | cut -d" " -f2)
        print_status "Python found: $PYTHON_VERSION"
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # macOS/Linux
        source venv/bin/activate
    fi
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed from requirements.txt"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_info "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        print_info "Creating .env file from template..."
        
        if [ -f "setup_env.py" ]; then
            $PYTHON_CMD setup_env.py
        else
            print_error "setup_env.py not found. Please create .env file manually."
            exit 1
        fi
    else
        print_status ".env file found"
        
        # Validate environment
        print_info "Validating environment configuration..."
        if $PYTHON_CMD setup_env.py validate; then
            print_status "Environment configuration is valid"
        else
            print_error "Environment configuration has issues. Please fix and try again."
            exit 1
        fi
    fi
}

# Create data directories
setup_directories() {
    print_info "Setting up data directories..."
    
    # Create ChromaDB directory
    mkdir -p data/chroma
    mkdir -p logs
    
    print_status "Data directories created"
}

# Start the service
start_service() {
    print_info "Starting LangChain Service..."
    
    # Set environment variables for this session
    export PYTHONPATH="${SCRIPT_DIR}:$PYTHONPATH"
    
    print_status "Service starting on http://$(python -c "import os; print(os.getenv('HOST', '0.0.0.0')):$(python -c "import os; print(os.getenv('PORT', '8001'))")")"
    print_info "Press Ctrl+C to stop the service"
    print_info "Health check: http://localhost:8003/health"
    echo ""
    
    # Start the service
    $PYTHON_CMD main.py
}

# Health check function
health_check() {
    print_info "Performing health check..."
    
    # Wait a moment for service to start
    sleep 2
    
    # Check if service is responding
    if command -v curl &> /dev/null; then
        if curl -s http://localhost:8001/health > /dev/null; then
            print_status "Service is healthy"
        else
            print_warning "Service may not be responding yet"
        fi
    else
        print_info "curl not available for health check"
    fi
}

# Cleanup function
cleanup() {
    print_info "Shutting down service..."
    exit 0
}

# Handle interrupts
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "Starting LangChain Service setup and launch..."
    echo ""
    
    check_python
    setup_venv
    install_dependencies
    setup_environment
    setup_directories
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete! Starting service...${NC}"
    echo ""
    
    start_service
}

# Run main function
main "$@" 