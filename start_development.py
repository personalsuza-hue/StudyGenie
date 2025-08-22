#!/usr/bin/env python3
"""
StudyGenie Development Startup Script
This script helps start both backend and frontend servers for local development.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def run_backend():
    """Run the FastAPI backend server"""
    print_colored("🚀 Starting Backend Server...", Colors.OKBLUE)
    
    # Change to backend directory
    backend_dir = Path('backend')
    if not backend_dir.exists():
        print_colored("❌ Backend directory not found!", Colors.FAIL)
        return
    
    # Check if virtual environment exists
    venv_path = backend_dir / 'venv'
    if not venv_path.exists():
        print_colored("⚠️  Virtual environment not found. Creating it...", Colors.WARNING)
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)])
        print_colored("✅ Virtual environment created!", Colors.OKGREEN)
    
    # Determine the correct activation script and uvicorn path
    if os.name == 'nt':  # Windows
        activate_script = venv_path / 'Scripts' / 'activate.bat'
        uvicorn_path = venv_path / 'Scripts' / 'uvicorn.exe'
        python_path = venv_path / 'Scripts' / 'python.exe'
    else:  # Unix/Linux/macOS
        activate_script = venv_path / 'bin' / 'activate'
        uvicorn_path = venv_path / 'bin' / 'uvicorn'
        python_path = venv_path / 'bin' / 'python'
    
    # Install requirements if uvicorn is not found
    if not uvicorn_path.exists():
        print_colored("📦 Installing Python dependencies...", Colors.WARNING)
        subprocess.run([str(python_path), '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      cwd=backend_dir, check=True)
        print_colored("✅ Dependencies installed!", Colors.OKGREEN)
    
    # Start the backend server
    try:
        print_colored("🔥 Backend server starting on http://localhost:8001", Colors.OKGREEN)
        if os.name == 'nt':  # Windows
            subprocess.run([
                str(python_path), '-m', 'uvicorn', 'server:app', 
                '--host', '0.0.0.0', '--port', '8001', '--reload'
            ], cwd=backend_dir)
        else:  # Unix/Linux/macOS
            subprocess.run([
                str(uvicorn_path), 'server:app', 
                '--host', '0.0.0.0', '--port', '8001', '--reload'
            ], cwd=backend_dir)
    except KeyboardInterrupt:
        print_colored("\n🛑 Backend server stopped.", Colors.WARNING)
    except Exception as e:
        print_colored(f"❌ Backend server failed to start: {e}", Colors.FAIL)

def run_frontend():
    """Run the React frontend server"""
    print_colored("🚀 Starting Frontend Server...", Colors.OKBLUE)
    
    # Change to frontend directory
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print_colored("❌ Frontend directory not found!", Colors.FAIL)
        return
    
    # Check if node_modules exists
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print_colored("📦 Installing Node.js dependencies...", Colors.WARNING)
        
        # Try yarn first, then npm
        try:
            subprocess.run(['yarn', '--version'], capture_output=True, check=True)
            subprocess.run(['yarn', 'install'], cwd=frontend_dir, check=True)
            print_colored("✅ Dependencies installed with Yarn!", Colors.OKGREEN)
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print_colored("✅ Dependencies installed with NPM!", Colors.OKGREEN)
            except subprocess.CalledProcessError as e:
                print_colored(f"❌ Failed to install dependencies: {e}", Colors.FAIL)
                return
    
    # Start the frontend server
    try:
        print_colored("🔥 Frontend server starting on http://localhost:3000", Colors.OKGREEN)
        
        # Try yarn first, then npm
        try:
            subprocess.run(['yarn', '--version'], capture_output=True, check=True)
            subprocess.run(['yarn', 'start'], cwd=frontend_dir)
        except (subprocess.CalledProcessError, FileNotFoundError):
            subprocess.run(['npm', 'start'], cwd=frontend_dir)
            
    except KeyboardInterrupt:
        print_colored("\n🛑 Frontend server stopped.", Colors.WARNING)
    except Exception as e:
        print_colored(f"❌ Frontend server failed to start: {e}", Colors.FAIL)

def main():
    print_colored("🎯 StudyGenie Development Server Starter", Colors.HEADER)
    print_colored("=" * 50, Colors.HEADER)
    
    # Check if we're in the right directory
    if not (Path('backend').exists() and Path('frontend').exists()):
        print_colored("❌ Please run this script from the StudyGenie project root directory", Colors.FAIL)
        print_colored("   Expected structure:", Colors.WARNING)
        print_colored("   studygenie/", Colors.WARNING)
        print_colored("   ├── backend/", Colors.WARNING)
        print_colored("   ├── frontend/", Colors.WARNING)
        print_colored("   └── start_development.py", Colors.WARNING)
        return
    
    # Ask user what to start
    print_colored("\nWhat would you like to start?", Colors.OKBLUE)
    print("1. Both Backend and Frontend (Recommended)")
    print("2. Backend only")
    print("3. Frontend only")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        print_colored("\n🚀 Starting both servers...", Colors.OKGREEN)
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait a bit for backend to start
        time.sleep(3)
        
        # Start frontend in main thread
        run_frontend()
        
    elif choice == '2':
        run_backend()
        
    elif choice == '3':
        run_frontend()
        
    elif choice == '4':
        print_colored("👋 Goodbye!", Colors.OKGREEN)
        
    else:
        print_colored("❌ Invalid choice. Please select 1-4.", Colors.FAIL)

if __name__ == "__main__":
    main()