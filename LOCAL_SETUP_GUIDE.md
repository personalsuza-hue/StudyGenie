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