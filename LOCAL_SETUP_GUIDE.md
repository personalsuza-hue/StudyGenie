# StudyGenie - Local Development Setup Guide for VS Code

This comprehensive guide will help you clone and run StudyGenie locally on your machine using VS Code with MongoDB Atlas.

## Prerequisites

Before starting, make sure you have the following installed on your machine:

### Required Software
1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Python** (v3.8 or higher)
   - Download from: https://python.org/
   - Verify installation: `python --version`

3. **Git**
   - Download from: https://git-scm.com/
   - Verify installation: `git --version`

4. **VS Code**
   - Download from: https://code.visualstudio.com/

5. **Yarn Package Manager** (Recommended for frontend)
   - Install globally: `npm install -g yarn`
   - Verify installation: `yarn --version`

### Cloud Services Setup

6. **MongoDB Atlas Account**
   - Create account at: https://www.mongodb.com/atlas
   - Create a new cluster (free tier available)
   - Get your connection string

### Recommended VS Code Extensions
- **Python** - Python language support
- **JavaScript (ES6) code snippets** - Enhanced JavaScript support
- **Thunder Client** or **REST Client** - For API testing
- **GitLens** - Enhanced Git integration
- **Prettier - Code formatter** - Code formatting
- **ES7+ React/Redux/React-Native snippets** - React development
- **Auto Rename Tag** - HTML/JSX tag renaming
- **Bracket Pair Colorizer 2** - Color matching brackets
- **MongoDB for VS Code** (Optional) - MongoDB database management

## Step-by-Step Installation

### Step 1: Clone or Set Up the Project

**Option A: If you have the project repository:**
```bash
git clone <your-repository-url>
cd studygenie
```

**Option B: If you're copying files manually:**
```bash
mkdir studygenie
cd studygenie
# Copy all your project files here
```

### Step 2: Open Project in VS Code
```bash
# Open the project in VS Code
code .
# Or open VS Code and use File > Open Folder to select your studygenie directory
```

### Step 3: Backend Setup

Open VS Code integrated terminal (Terminal → New Terminal) and run:

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

**Note:** The requirements.txt includes all necessary packages including:
- FastAPI and Uvicorn for the web server
- Google authentication libraries
- MongoDB drivers (PyMongo, Motor)
- AI integration libraries (emergentintegrations)
- File processing libraries (PyPDF2, pytesseract, Pillow)
- JWT authentication libraries

### Step 4: Frontend Setup

Open a new terminal in VS Code (Terminal → New Terminal):

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies using Yarn (recommended)
yarn install

# If you don't have Yarn installed:
npm install -g yarn
# Then run: yarn install

# Alternative: Use npm (though yarn is recommended for this project)
# npm install
```

### Step 5: MongoDB Atlas Configuration

1. **Create MongoDB Atlas Account:**
   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for a free account
   - Create a new cluster (free tier M0 is sufficient for development)

2. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (it looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`)

3. **Configure Database Access:**
   - Go to "Database Access" in the Atlas dashboard
   - Add a new database user with read and write permissions
   - Note the username and password

4. **Configure Network Access:**
   - Go to "Network Access" in the Atlas dashboard
   - Add your IP address (or 0.0.0.0/0 for development - not recommended for production)

### Step 6: Environment Configuration

#### Backend Environment (.env)
Create or update `backend/.env` file in VS Code:

```env
# MongoDB Atlas Configuration
MONGO_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/studygenie_db?retryWrites=true&w=majority
DB_NAME=studygenie_db

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000

# Google OAuth Configuration
# You need to get these from Google Cloud Console
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Secret (generate a secure secret)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-make-it-very-long-and-random

# LLM Configuration 
EMERGENT_LLM_KEY=your-emergent-llm-key
OPENAI_API_KEY=your-openai-api-key-or-emergent-key
```

**Important Notes:**
- Replace `<username>`, `<password>`, and cluster URL with your actual MongoDB Atlas credentials
- The database name `studygenie_db` will be automatically created when you first run the application
- Replace the Google OAuth credentials with your own (see Google OAuth setup below)

#### Frontend Environment (.env)
Create or update `frontend/.env` file in VS Code:

```env
# Backend API URL (for local development)
REACT_APP_BACKEND_URL=http://localhost:8001

# Google OAuth Client ID (same as in backend, used for frontend authentication)
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### Step 7: Google OAuth Setup

To enable Google authentication, you need to set up Google OAuth credentials:

1. **Go to Google Cloud Console:**
   - Visit [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one

2. **Enable Google+ API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it

3. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add these URLs to "Authorized redirect URIs":
     - `http://localhost:8001/api/auth/google/callback`
   - Add these URLs to "Authorized JavaScript origins":
     - `http://localhost:3000`
     - `http://localhost:8001`

4. **Copy Credentials:**
   - Copy the "Client ID" and "Client Secret"
   - Update both `backend/.env` and `frontend/.env` files with these values

## Running the Application

### Method 1: Using VS Code Integrated Terminal (Recommended)

1. **Open VS Code in your project directory**
2. **Split Terminal:** Click the split terminal button in VS Code or use `Ctrl+Shift+5`
3. **Run Backend (Terminal 1):**
   ```bash
   cd backend
   # Activate virtual environment if not already active
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Run Frontend (Terminal 2):**
   ```bash
   cd frontend
   yarn start
   # or: npm start
   ```

### Method 2: Using VS Code Tasks (Advanced)

Create `.vscode/tasks.json` in your project root:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Backend",
            "type": "shell",
            "command": "uvicorn",
            "args": ["server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
            "options": {
                "cwd": "${workspaceFolder}/backend"
            },
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Start Frontend",
            "type": "shell",
            "command": "yarn",
            "args": ["start"],
            "options": {
                "cwd": "${workspaceFolder}/frontend"
            },
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ]
}
```

Then use `Ctrl+Shift+P` → "Tasks: Run Task" to start either service.

## Accessing the Application

1. **Open your browser** and go to `http://localhost:3000`
2. **You should see the StudyGenie login page**
3. **Click "Continue with Google"** to authenticate
4. **Upload a PDF or image file** to test the AI features
5. **Explore the features:** Summary, Quiz, Flashcards, and AI Tutor

## VS Code Development Tips

### Workspace Configuration

Create `.vscode/settings.json` in your project root:

```json
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/venv": true,
        "**/.git": true
    },
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Launch Configuration for Debugging

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/venv/bin/uvicorn",
            "args": ["server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
            "cwd": "${workspaceFolder}/backend",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/backend/.env"
        }
    ]
}
```

### Development Workflow

1. **Use integrated terminal:** View → Terminal
2. **Split terminals:** Run backend and frontend simultaneously
3. **Use debugger:** Set breakpoints in Python files and use F5 to debug
4. **Hot reload:** Both backend and frontend have hot reload enabled
5. **API testing:** Use Thunder Client extension to test API endpoints at `http://localhost:8001/docs`

## Common Issues and Solutions

### Port Already in Use
```bash
# Kill process on port 8001 (backend)
# Windows:
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# macOS/Linux:
sudo lsof -t -i tcp:8001 | xargs kill -9

# Kill process on port 3000 (frontend)  
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
sudo lsof -t -i tcp:3000 | xargs kill -9
```

### MongoDB Atlas Connection Issues
```bash
# Check your connection string format:
# mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/studygenie_db

# Common issues:
# 1. Password contains special characters - URL encode them
# 2. IP address not whitelisted - add your IP in Atlas Network Access
# 3. Database user doesn't have proper permissions
# 4. Network firewall blocking connection
```

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv  # On Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Node.js/Yarn Issues
```bash
# Clear cache and reinstall
yarn cache clean
rm -rf node_modules  # On Windows: rmdir /s node_modules
yarn install

# If yarn is not working, use npm:
npm cache clean --force
npm install
```

### Google OAuth Issues
1. **Check Google Cloud Console settings:**
   - Ensure OAuth client is configured for "Web application"
   - Verify redirect URIs and JavaScript origins
   - Make sure Google+ API is enabled

2. **Environment variables:**
   - Ensure GOOGLE_CLIENT_ID matches in both backend and frontend .env files
   - Check for typos in client ID and secret

### AI Features Not Working
1. **Check LLM API keys:**
   - Verify EMERGENT_LLM_KEY is valid
   - Check if you have sufficient credits/quota
   
2. **File processing issues:**
   - For Windows: Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
   - For macOS: `brew install tesseract`
   - For Linux: `sudo apt-get install tesseract-ocr`

## Google OAuth Setup Verification

To ensure Google OAuth is properly configured:

1. **Google Cloud Console Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to "APIs & Services" → "Credentials"
   - Find your OAuth 2.0 Client ID
   - Ensure these URLs are in "Authorized redirect URIs":
     - `http://localhost:8001/api/auth/google/callback`
   - Ensure these URLs are in "Authorized JavaScript origins":
     - `http://localhost:3000`
     - `http://localhost:8001`

2. **Test Authentication:**
   - Start both backend and frontend servers
   - Go to `http://localhost:3000`
   - Click "Login with Google"
   - Should redirect to Google login page
   - After successful login, should redirect back to your app

## Project Structure

```
studygenie/
├── backend/
│   ├── server.py          # FastAPI main application
│   ├── requirements.txt   # Python dependencies
│   ├── .env              # Backend environment variables
│   └── venv/             # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── components/   # UI components
│   │   └── ...
│   ├── package.json      # Node.js dependencies
│   ├── .env             # Frontend environment variables
│   └── node_modules/    # Node.js modules
├── LOCAL_SETUP_GUIDE.md # This file
└── README.md            # Project documentation
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

## Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all environment variables are set correctly
3. Ensure MongoDB is running and accessible
4. Check Google Cloud Console for OAuth configuration
5. Test API endpoints using `http://localhost:8001/docs`

Happy coding! 🚀