#!/usr/bin/env python3
"""
Development Tools for LangChain Service
Utility functions for testing, debugging, and maintenance
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DevTools:
    def __init__(self):
        self.base_url = f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '8001')}"
        self.session = requests.Session()
        
    def health_check(self):
        """Check service health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            health_data = response.json()
            print("🟢 Service Health Check - PASSED")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            
            if 'collection_info' in health_data:
                collection = health_data['collection_info']
                print(f"   Vector Store: {collection.get('document_count', 0)} documents")
                print(f"   Collection: {collection.get('collection_name', 'unknown')}")
                
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"🔴 Service Health Check - FAILED")
            print(f"   Error: {e}")
            return False
    
    def test_chat(self, message="Hello, can you help me with my notes?"):
        """Test chat functionality"""
        try:
            payload = {
                "message": message,
                "include_sources": True
            }
            
            print(f"💬 Testing chat with message: '{message}'")
            response = self.session.post(f"{self.base_url}/chat", 
                                       json=payload, timeout=30)
            response.raise_for_status()
            
            chat_data = response.json()
            print("🟢 Chat Test - PASSED")
            print(f"   Response: {chat_data.get('response', 'No response')[:100]}...")
            print(f"   Sources: {len(chat_data.get('sources', []))} found")
            print(f"   Conversation ID: {chat_data.get('conversation_id', 'unknown')}")
            
            return chat_data
            
        except requests.exceptions.RequestException as e:
            print(f"🔴 Chat Test - FAILED")
            print(f"   Error: {e}")
            return None
    
    def sync_test_notes(self):
        """Sync test notes for development"""
        test_notes = [
            {
                "id": 1,
                "title": "Development Setup",
                "content": "Setting up the development environment for the notes app with AI chat functionality.",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
                "tags": ["development", "setup"],
                "category": "work"
            },
            {
                "id": 2,
                "title": "Meeting Notes",
                "content": "Discussed project timeline and requirements for AI integration. Need to implement RAG for better context.",
                "created_at": "2024-01-02T14:30:00Z",
                "updated_at": "2024-01-02T14:30:00Z",
                "tags": ["meeting", "ai"],
                "category": "work"
            },
            {
                "id": 3,
                "title": "Personal Todo",
                "content": "Remember to test the chat functionality and verify that embeddings are working correctly.",
                "created_at": "2024-01-03T09:15:00Z",
                "updated_at": "2024-01-03T09:15:00Z",
                "tags": ["todo", "testing"],
                "category": "personal"
            }
        ]
        
        try:
            payload = {"notes": test_notes}
            
            print(f"📚 Syncing {len(test_notes)} test notes...")
            response = self.session.post(f"{self.base_url}/sync_notes", 
                                       json=payload, timeout=30)
            response.raise_for_status()
            
            sync_data = response.json()
            print("🟢 Sync Test - PASSED")
            print(f"   Processed: {sync_data.get('processed', 0)}")
            print(f"   Total: {sync_data.get('total', 0)}")
            
            return sync_data
            
        except requests.exceptions.RequestException as e:
            print(f"🔴 Sync Test - FAILED")
            print(f"   Error: {e}")
            return None
    
    def test_endpoints(self):
        """Test all service endpoints"""
        print("🧪 Testing All Endpoints")
        print("=" * 40)
        
        # Test health check
        health_ok = self.health_check()
        print()
        
        if not health_ok:
            print("❌ Skipping other tests - service not healthy")
            return False
        
        # Sync test notes
        sync_ok = self.sync_test_notes()
        print()
        
        # Test chat
        chat_ok = self.test_chat("What notes do I have about development?")
        print()
        
        # Test with different query
        chat_ok2 = self.test_chat("Tell me about my meeting notes")
        print()
        
        # Summary
        print("📊 Test Summary")
        print("=" * 20)
        print(f"Health Check: {'✅' if health_ok else '❌'}")
        print(f"Sync Notes: {'✅' if sync_ok else '❌'}")
        print(f"Chat Test 1: {'✅' if chat_ok else '❌'}")
        print(f"Chat Test 2: {'✅' if chat_ok2 else '❌'}")
        
        return all([health_ok, sync_ok, chat_ok, chat_ok2])
    
    def clear_vector_store(self):
        """Clear the vector store (for testing)"""
        try:
            # This would need a clear endpoint in the service
            print("⚠️  Vector store clearing not implemented in API")
            print("   You can delete the data/chroma directory manually")
            return False
        except Exception as e:
            print(f"❌ Clear vector store failed: {e}")
            return False
    
    def show_config(self):
        """Show current configuration"""
        print("⚙️  Current Configuration")
        print("=" * 30)
        
        config_vars = [
            "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_TEMPERATURE",
            "HOST", "PORT", "CHROMA_PERSIST_DIR", "EMBEDDINGS_MODEL",
            "MAX_CONTEXT_NOTES", "CONVERSATION_WINDOW"
        ]
        
        for var in config_vars:
            value = os.getenv(var, "Not set")
            # Hide sensitive info
            if "KEY" in var and value != "Not set":
                value = f"{'*' * (len(value) - 4)}{value[-4:]}"
            print(f"   {var}: {value}")
    
    def monitor_logs(self):
        """Monitor service logs (placeholder)"""
        print("📝 Log Monitoring")
        print("=" * 20)
        print("Log monitoring not implemented - check service console output")
        
        # Could implement log file monitoring here
        logs_dir = os.path.join(os.getcwd(), "logs")
        if os.path.exists(logs_dir):
            print(f"Log directory: {logs_dir}")
            for log_file in os.listdir(logs_dir):
                print(f"   {log_file}")
        else:
            print("No logs directory found")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='LangChain Service Development Tools')
    parser.add_argument('command', choices=[
        'health', 'chat', 'sync', 'test', 'config', 'logs', 'clear'
    ], help='Command to run')
    parser.add_argument('--message', '-m', default="Hello, can you help me with my notes?",
                       help='Message for chat test')
    
    args = parser.parse_args()
    
    tools = DevTools()
    
    print(f"🔧 LangChain Service Dev Tools")
    print(f"Service URL: {tools.base_url}")
    print("=" * 40)
    
    if args.command == 'health':
        tools.health_check()
    elif args.command == 'chat':
        tools.test_chat(args.message)
    elif args.command == 'sync':
        tools.sync_test_notes()
    elif args.command == 'test':
        tools.test_endpoints()
    elif args.command == 'config':
        tools.show_config()
    elif args.command == 'logs':
        tools.monitor_logs()
    elif args.command == 'clear':
        tools.clear_vector_store()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 