# StudyGenie - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Prerequisites Check
```bash
# Check if you have the required tools
python --version    # Should be 3.8+
node --version      # Should be 18+
git --version       # Any recent version
```

### Step 2: Project Setup
```bash
# Clone the project (if from repository)
git clone <your-repo-url>
cd studygenie

# Open in VS Code
code .
```

### Step 3: Automated Setup Check
```bash
# Run the setup verification script
python setup_check.py
```

### Step 4: Environment Configuration

1. **MongoDB Atlas:**
   - Create account at mongodb.com/atlas
   - Create a free cluster
   - Get connection string
   - Add your IP to Network Access

2. **Google OAuth:**
   - Go to console.cloud.google.com
   - Create project → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID for Web Application
   - Add `http://localhost:3000` to JavaScript origins
   - Add `http://localhost:8001/api/auth/google/callback` to redirect URIs

3. **Environment Files:**
   ```bash
   # Copy templates and edit with your values
   cp backend/.env.template backend/.env
   cp frontend/.env.template frontend/.env
   
   # Edit the .env files with your actual credentials
   ```

### Step 5: Quick Start
```bash
# Automated startup (recommended)
python start_development.py

# Choose option 1 to start both servers
```

### Step 6: Manual Start (Alternative)
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend  
cd frontend
yarn install  # or npm install
yarn start    # or npm start
```

### Step 7: Access Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/docs
- **Login with Google** to start using the app

## 🎯 Next Steps
1. Upload a PDF or image to test file processing
2. Try generating summaries, quizzes, and flashcards  
3. Use the AI tutor to ask questions about your documents
4. Explore the code to understand the architecture

## 🆘 Need Help?
- **Setup issues:** Run `python setup_check.py`
- **Detailed guide:** See `LOCAL_SETUP_GUIDE.md`
- **VS Code integration:** Check `.vscode/` folder for tasks and debug config
- **Troubleshooting:** Look for error messages in terminal output

Happy coding! 🎉