#!/usr/bin/env python3
"""
LangChain Service Startup Script (Python Version)
Cross-platform startup script for the LangChain service
"""

import os
import sys
import subprocess
import platform
import time
import signal
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.NC):
    """Print colored message"""
    print(f"{color}{message}{Colors.NC}")

def print_status(message):
    print_colored(f"✅ {message}", Colors.GREEN)

def print_warning(message):
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_error(message):
    print_colored(f"❌ {message}", Colors.RED)

def print_info(message):
    print_colored(f"ℹ️  {message}", Colors.BLUE)

def get_python_command():
    """Determine the Python command to use"""
    try:
        # Try python3 first
        result = subprocess.run(['python3', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return 'python3'
    except FileNotFoundError:
        pass
    
    try:
        # Try python
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return 'python'
    except FileNotFoundError:
        pass
    
    print_error("Python not found. Please install Python 3.8 or higher.")
    sys.exit(1)

def get_venv_activation():
    """Get virtual environment activation command"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "activate")
    else:
        return os.path.join("venv", "bin", "activate")

def run_command(cmd, shell=False, check=True):
    """Run a command and handle errors"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=False, text=True)
        else:
            result = subprocess.run(cmd, check=check, 
                                  capture_output=False, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if check:
            sys.exit(1)
        return e

def setup_virtual_environment():
    """Setup Python virtual environment"""
    print_info("Setting up virtual environment...")
    
    python_cmd = get_python_command()
    
    if not os.path.exists("venv"):
        print_info("Creating virtual environment...")
        run_command([python_cmd, "-m", "venv", "venv"])
        print_status("Virtual environment created")
    else:
        print_status("Virtual environment already exists")
    
    return python_cmd

def install_dependencies():
    """Install required dependencies"""
    print_info("Installing dependencies...")
    
    # Determine pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")
    
    # Upgrade pip
    print_info("Upgrading pip...")
    run_command([pip_cmd, "install", "--upgrade", "pip"])
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        print_info("Installing from requirements.txt...")
        run_command([pip_cmd, "install", "-r", "requirements.txt"])
        print_status("Dependencies installed successfully")
    else:
        print_error("requirements.txt not found")
        sys.exit(1)

def setup_environment():
    """Setup environment configuration"""
    print_info("Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print_warning(".env file not found")
        print_info("Creating .env file from template...")
        
        if os.path.exists("setup_env.py"):
            # Use venv python to run setup
            if platform.system() == "Windows":
                python_cmd = os.path.join("venv", "Scripts", "python")
            else:
                python_cmd = os.path.join("venv", "bin", "python")
            
            run_command([python_cmd, "setup_env.py"])
        else:
            print_error("setup_env.py not found. Please create .env file manually.")
            sys.exit(1)
    else:
        print_status(".env file found")
        
        # Validate environment
        print_info("Validating environment configuration...")
        if platform.system() == "Windows":
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:
            python_cmd = os.path.join("venv", "bin", "python")
        
        result = run_command([python_cmd, "setup_env.py", "validate"], check=False)
        if result.returncode != 0:
            print_error("Environment configuration has issues. Please fix and try again.")
            sys.exit(1)
        print_status("Environment configuration is valid")

def setup_directories():
    """Create necessary directories"""
    print_info("Setting up data directories...")
    
    os.makedirs("data/chroma", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print_status("Data directories created")

def start_service():
    """Start the LangChain service"""
    print_info("Starting LangChain Service...")
    
    # Add current directory to Python path
    current_dir = os.getcwd()
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = current_dir
    
    # Determine Python command in venv
    if platform.system() == "Windows":
        python_cmd = os.path.join("venv", "Scripts", "python")
    else:
        python_cmd = os.path.join("venv", "bin", "python")
    
    # Load environment to get port info
    try:
        from dotenv import load_dotenv
        load_dotenv()
        host = os.getenv('HOST', '0.0.0.0')
        port = os.getenv('PORT', '8001')
        print_status(f"Service starting on http://{host}:{port}")
    except ImportError:
        print_status("Service starting on http://localhost:8001")
    
    print_info("Press Ctrl+C to stop the service")
    print_info("Health check: http://localhost:8003/health")
    print("")
    
    # Start the service
    try:
        process = subprocess.Popen([python_cmd, "main.py"], env=env)
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            print_info("Shutting down service...")
            process.terminate()
            process.wait()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print_info("Service interrupted by user")
        if 'process' in locals():
            process.terminate()
            process.wait()
    except Exception as e:
        print_error(f"Failed to start service: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print_colored("🚀 LangChain Service Startup", Colors.BLUE)
    print("=" * 40)
    print("Starting LangChain Service setup and launch...")
    print("")
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    try:
        # Setup steps
        setup_virtual_environment()
        install_dependencies()
        setup_environment()
        setup_directories()
        
        print("")
        print_colored("🎉 Setup complete! Starting service...", Colors.GREEN)
        print("")
        
        # Start service
        start_service()
        
    except KeyboardInterrupt:
        print_info("Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 