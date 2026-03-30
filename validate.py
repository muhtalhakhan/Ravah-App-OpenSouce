#!/usr/bin/env python3
"""
Validation script to check project structure and files
"""
import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path}")
        return False

def main():
    print("🔍 Validating Full-Stack Agentic Application Structure\n")
    
    # Check main directories
    dirs_to_check = [
        ("backend", "Backend directory"),
        ("frontend", "Frontend directory"),
        ("backend/app", "Backend app package"),
        ("backend/app/models", "Models package"),
        ("backend/app/routers", "Routers package"),
        ("backend/app/schemas", "Schemas package"),
        ("backend/app/utils", "Utils package"),
        ("frontend/src", "Frontend source"),
        ("frontend/src/pages", "Frontend pages"),
        ("frontend/src/layouts", "Frontend layouts"),
    ]
    
    for dir_path, description in dirs_to_check:
        check_file_exists(dir_path, description)
    
    print("\n📁 Key Files:")
    
    # Check key files
    files_to_check = [
        ("backend/main.py", "FastAPI main application"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/app/config.py", "Configuration"),
        ("backend/app/database.py", "Database setup"),
        ("backend/app/models/user.py", "User model"),
        ("backend/app/models/item.py", "Item model"),
        ("backend/app/routers/auth.py", "Auth router"),
        ("backend/app/routers/items.py", "Items router"),
        ("backend/app/routers/agent.py", "Agent router"),
        ("backend/app/schemas/user.py", "User schemas"),
        ("backend/app/schemas/item.py", "Item schemas"),
        ("backend/app/utils/auth.py", "Auth utilities"),
        ("backend/app/utils/dependencies.py", "FastAPI dependencies"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/astro.config.mjs", "Astro configuration"),
        ("frontend/src/pages/index.astro", "Home page"),
        ("frontend/src/layouts/BaseLayout.astro", "Base layout"),
        ("docker-compose.yml", "Docker Compose"),
        (".env.example", "Environment example"),
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print(f"\n🧪 Testing Python syntax compilation...")
    
    # Test Python compilation
    try:
        import py_compile
        python_files = [
            "backend/main.py",
            "backend/app/config.py",
            "backend/app/database.py",
            "backend/app/models/user.py",
            "backend/app/models/item.py",
            "backend/app/routers/auth.py",
            "backend/app/routers/items.py",
            "backend/app/routers/agent.py",
            "backend/app/schemas/user.py",
            "backend/app/schemas/item.py",
            "backend/app/utils/auth.py",
            "backend/app/utils/dependencies.py",
        ]
        
        for py_file in python_files:
            if os.path.exists(py_file):
                try:
                    py_compile.compile(py_file, doraise=True)
                    print(f"✅ Syntax OK: {py_file}")
                except py_compile.PyCompileError as e:
                    print(f"❌ Syntax Error: {py_file} - {e}")
                    all_good = False
            
    except Exception as e:
        print(f"⚠️  Could not test Python compilation: {e}")
    
    print(f"\n{'🎉 Project structure is valid!' if all_good else '⚠️  Issues found in project structure'}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Install dependencies: cd backend && pip install -r requirements.txt")
    print(f"2. Set up database: docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=agentapp -p 5432:5432 postgres:15-alpine")
    print(f"3. Start backend: cd backend && python main.py")
    print(f"4. Install frontend deps: cd frontend && npm install")
    print(f"5. Start frontend: cd frontend && npm run dev")
    print(f"6. Or use Docker: docker-compose up -d")

if __name__ == "__main__":
    main()
