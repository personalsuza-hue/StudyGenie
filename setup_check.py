#!/usr/bin/env python3
"""
StudyGenie Setup Verification Script
This script checks if all required dependencies and configurations are properly set up.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} - OK")
        return True
    else:
        print(f"❌ {description} - Missing: {file_path}")
        return False

def check_command(command, description):
    """Check if a command is available"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ {description} - OK ({version})")
            return True
        else:
            print(f"❌ {description} - Command failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"❌ {description} - Not found")
        return False

def check_env_file(file_path, required_vars):
    """Check if .env file has required variables"""
    if not Path(file_path).exists():
        print(f"❌ Environment file missing: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ {file_path} - Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print(f"✅ {file_path} - All required variables present")
        return True

def check_python_packages():
    """Check if required Python packages can be imported"""
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('motor', 'Motor (MongoDB async driver)'),
        ('pymongo', 'PyMongo'),
        ('google.auth', 'Google Auth Library'),
        ('jwt', 'PyJWT'),
        ('dotenv', 'Python-dotenv'),
        ('emergentintegrations', 'Emergent Integrations')
    ]
    
    success = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {description} - OK")
        except ImportError:
            print(f"❌ {description} - Not installed ({package})")
            success = False
    
    return success

def main():
    print("🔍 StudyGenie Local Setup Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check Python version
    total_checks += 1
    if check_python_version():
        checks_passed += 1
    
    # Check system commands
    commands = [
        ('node', 'Node.js'),
        ('git', 'Git'),
    ]
    
    for command, description in commands:
        total_checks += 1
        if check_command(command, description):
            checks_passed += 1
    
    # Check if yarn or npm is available
    total_checks += 1
    if check_command('yarn', 'Yarn') or check_command('npm', 'NPM'):
        print("✅ Package manager (Yarn/NPM) - OK")
        checks_passed += 1
    else:
        print("❌ Package manager - Neither Yarn nor NPM found")
    
    # Check project structure
    files_to_check = [
        ('backend/server.py', 'Backend main file'),
        ('backend/auth.py', 'Backend auth file'),  
        ('backend/requirements.txt', 'Backend requirements'),
        ('frontend/package.json', 'Frontend package.json'),
        ('frontend/src/App.js', 'Frontend main component'),
        ('frontend/src/contexts/AuthContext.js', 'Auth context'),
        ('frontend/src/components/auth/GoogleLogin.js', 'Google login component'),
    ]
    
    for file_path, description in files_to_check:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1
    
    # Check environment files
    backend_env_vars = [
        'MONGO_URL', 'DB_NAME', 'CORS_ORIGINS', 
        'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'JWT_SECRET'
    ]
    
    frontend_env_vars = [
        'REACT_APP_BACKEND_URL', 'REACT_APP_GOOGLE_CLIENT_ID'
    ]
    
    total_checks += 2
    if check_env_file('backend/.env', backend_env_vars):
        checks_passed += 1
    if check_env_file('frontend/.env', frontend_env_vars):
        checks_passed += 1
    
    # Check Python packages (only if we're in the backend directory or venv is activated)
    if Path('backend/venv').exists() or 'VIRTUAL_ENV' in os.environ:
        print("\n🐍 Checking Python packages...")
        total_checks += 1
        if check_python_packages():
            checks_passed += 1
    else:
        print("\n⚠️  Virtual environment not detected. Activate it to check Python packages.")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Setup Check Results: {checks_passed}/{total_checks} passed")
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Your setup looks good.")
        print("\n📋 Next steps:")
        print("1. Start the backend: cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Start the frontend: cd frontend && yarn start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        print("\n📋 Common solutions:")
        print("1. Install missing dependencies: pip install -r backend/requirements.txt")
        print("2. Install frontend packages: cd frontend && yarn install")
        print("3. Create missing .env files using the LOCAL_SETUP_GUIDE.md")
        print("4. Activate Python virtual environment: source backend/venv/bin/activate")

if __name__ == "__main__":
    main()