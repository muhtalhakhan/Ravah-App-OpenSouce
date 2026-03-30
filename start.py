#!/usr/bin/env python3
"""
Simple startup script to test the FastAPI application
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("Starting FastAPI application...")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
