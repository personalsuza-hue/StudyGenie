# StudyGenie - AI-Powered Study Guide Generator

> Transform your study materials into interactive learning experiences with AI-powered summaries, quizzes, flashcards, and an intelligent tutor.

## 🎯 Features

- **📄 Smart Document Processing** - Upload PDFs and images with automatic text extraction and OCR
- **🤖 AI-Powered Content Generation** - Create summaries, quizzes, and flashcards using advanced LLM
- **💬 Interactive AI Tutor** - Ask questions about your documents and get intelligent responses  
- **🔐 Secure Authentication** - Google OAuth integration with user-specific data isolation
- **📱 Modern UI/UX** - Responsive design built with React and Tailwind CSS
- **⚡ Real-time Processing** - Background AI processing with live updates

## 🚀 Quick Start for Local Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB Atlas account
- Google Cloud Console project (for OAuth)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd studygenie
code .  # Open in VS Code
```

### 2. Run Setup Check
```bash
python setup_check.py
```

### 3. Quick Start (Automated)
```bash
python start_development.py
```

### 4. Manual Setup
See `LOCAL_SETUP_GUIDE.md` for detailed instructions.

## 📁 Project Structure

```
studygenie/
├── backend/                    # FastAPI Python backend
│   ├── server.py              # Main application & API routes
│   ├── auth.py               # Google OAuth & JWT authentication
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── contexts/        # React contexts (Auth)
│   │   └── App.js          # Main application component
│   └── package.json        # Node.js dependencies
├── .vscode/                   # VS Code configuration
├── LOCAL_SETUP_GUIDE.md     # Detailed setup instructions
└── setup_check.py           # Setup verification script
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- MongoDB (Atlas cloud database)
- Google OAuth 2.0 & JWT authentication
- Emergent Integrations (LLM API)
- PyPDF2 & Tesseract (file processing)

**Frontend:**
- React 19 with modern hooks
- Tailwind CSS + shadcn/ui components
- Axios for API communication
- Google Identity Services

## 🔧 Development Workflow

### VS Code Integration
This project is optimized for VS Code with:
- **Integrated terminals** for running both servers
- **Debug configuration** for Python backend
- **Task runner** for common operations
- **Extension recommendations** for enhanced development

### Available VS Code Commands
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Backend Server"
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Frontend Server"  
- `F5` → Debug backend with breakpoints
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup Check"

## 📚 API Documentation

When running locally, visit:
- **Interactive API docs:** `http://localhost:8001/docs`
- **Alternative docs:** `http://localhost:8001/redoc`

### Key Endpoints
```
POST   /api/auth/google       # Google OAuth login
GET    /api/auth/me          # Current user info
POST   /api/upload           # Upload & process documents
GET    /api/documents        # List user documents
GET    /api/documents/{id}/quiz      # Generated quiz
GET    /api/documents/{id}/flashcards # Generated flashcards  
POST   /api/chat            # AI tutor interaction
```

## 🔐 Environment Configuration

### Backend (.env)
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/studygenie_db
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
JWT_SECRET=your-jwt-secret
EMERGENT_LLM_KEY=your-llm-api-key
```

### Frontend (.env)  
```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts:** Kill processes on ports 3000/8001
2. **MongoDB connection:** Check Atlas credentials and IP whitelist
3. **Google OAuth:** Verify redirect URIs in Cloud Console
4. **Package issues:** Delete node_modules/venv and reinstall

### Getting Help
1. Run `python setup_check.py` to verify setup
2. Check terminal output for specific error messages
3. Review `LOCAL_SETUP_GUIDE.md` for detailed instructions

## 📖 Documentation

- **`LOCAL_SETUP_GUIDE.md`** - Comprehensive setup guide
- **`setup_check.py`** - Automated setup verification
- **`start_development.py`** - Development server starter
- **`.vscode/`** - VS Code configuration files

## 🎨 UI Components

Built with modern, accessible components:
- Authentication flow with Google OAuth
- Drag-and-drop file upload
- Interactive quiz interface
- Flip-card flashcards
- Real-time chat interface
- Responsive navigation and layouts

## 🚀 Deployment

This project is configured for local development. For production deployment:
1. Update CORS origins
2. Use production MongoDB cluster
3. Configure proper JWT secrets
4. Set up HTTPS with proper OAuth redirect URIs

## 📄 License

This project is for educational and development purposes.

---

**Need help?** Check the `LOCAL_SETUP_GUIDE.md` for detailed setup instructions or run `python setup_check.py` to verify your configuration.
