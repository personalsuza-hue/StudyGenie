# StudyGenie - Local Development Setup Guide

This guide will help you clone and run StudyGenie locally on your machine using VS Code.

## Prerequisites

Before starting, make sure you have the following installed on your machine:

### Required Software
1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Python** (v3.8 or higher)
   - Download from: https://python.org/
   - Verify installation: `python --version`

3. **MongoDB** 
   - **Option A - MongoDB Community Server (Local Installation):**
     - Download from: https://www.mongodb.com/try/download/community
     - Follow installation guide for your OS
   - **Option B - MongoDB Docker Container (Recommended):**
     ```bash
     docker run --name studygenie-mongo -p 27017:27017 -d mongo:latest
     ```

4. **Git**
   - Download from: https://git-scm.com/
   - Verify installation: `git --version`

5. **VS Code**
   - Download from: https://code.visualstudio.com/

### Recommended VS Code Extensions
- Python
- JavaScript (ES6) code snippets
- MongoDB for VS Code
- Thunder Client (for API testing)
- GitLens

## Installation Steps

### 1. Clone the Repository

```bash
# Clone from your repository
git clone <your-repository-url>
cd studygenie

# Or copy the project files to a new directory
mkdir studygenie
cd studygenie
# Copy all files from the current project
```

### 2. Backend Setup

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

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for Google OAuth
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies using Yarn (recommended)
yarn install

# If you don't have Yarn, install it first:
npm install -g yarn
# Then run: yarn install

# Or use npm (though yarn is recommended):
# npm install
```

### 4. Environment Configuration

#### Backend Environment (.env)
Create or update `backend/.env`:

```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=studygenie_db

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000

# Google OAuth Configuration
GOOGLE_CLIENT_ID=92975282494-o9l8lqlgjbl35v0ssc2hb69ts8reqnnt.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# JWT Secret (generate a secure secret)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# LLM Configuration (keep existing)
EMERGENT_LLM_KEY=sk-emergent-874Fa11661817D1EeC
OPENAI_API_KEY=sk-emergent-874Fa11661817D1EeC
```

#### Frontend Environment (.env)
Create or update `frontend/.env`:

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Google OAuth Client ID (for frontend)
REACT_APP_GOOGLE_CLIENT_ID=92975282494-o9l8lqlgjbl35v0ssc2hb69ts8reqnnt.apps.googleusercontent.com
```

### 5. Database Setup

Make sure MongoDB is running:

```bash
# If using local MongoDB installation:
mongod

# If using Docker:
docker start studygenie-mongo

# Verify MongoDB is running (should connect without errors):
mongosh mongodb://localhost:27017
```

## Running the Application

### 1. Start Backend Server

```bash
# From backend directory with activated virtual environment
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The backend will be available at: `http://localhost:8001`
API docs will be available at: `http://localhost:8001/docs`

### 2. Start Frontend Server

```bash
# From frontend directory (in a new terminal)
cd frontend
yarn start
# or: npm start
```

The frontend will be available at: `http://localhost:3000`

## Accessing the Application

1. Open your browser and go to `http://localhost:3000`
2. You should see the StudyGenie interface
3. Click on "Login with Google" to authenticate
4. Upload a PDF or image file to test the AI features

## Development Workflow

### Using VS Code

1. Open VS Code in the project root directory
2. Use the integrated terminal (Terminal → New Terminal)
3. You can split terminals to run both backend and frontend simultaneously

### Recommended VS Code Workspace Setup

Create a `.vscode/settings.json` file:

```json
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/venv": true
    }
}
```

### Debugging

#### Backend Debugging
1. Set breakpoints in Python files
2. Use VS Code's Python debugger
3. Check logs in terminal
4. Use API testing tools (Thunder Client, Postman)

#### Frontend Debugging
1. Use browser Developer Tools (F12)
2. Check React Developer Tools extension
3. Console logs will appear in terminal and browser

## Common Issues and Solutions

### Port Already in Use
```bash
# Kill process on port 8001 (backend)
sudo lsof -t -i tcp:8001 | xargs kill -9

# Kill process on port 3000 (frontend)  
sudo lsof -t -i tcp:3000 | xargs kill -9
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongosh mongodb://localhost:27017

# If using Docker, check container status
docker ps -a
docker start studygenie-mongo
```

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Node.js/Yarn Issues
```bash
# Clear npm/yarn cache
npm cache clean --force
yarn cache clean

# Delete node_modules and reinstall
rm -rf node_modules
yarn install
```

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