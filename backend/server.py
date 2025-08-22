from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Form, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import io
import tempfile
import shutil

# File processing imports
import PyPDF2
import pytesseract
from PIL import Image
import magic

# AI imports
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Authentication imports
from auth import AuthService, User, get_current_user, get_current_user_optional

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="StudyGenie API", description="AI-Powered Study Guide Generator")

# Store database in app state for dependency access
@app.on_event("startup")
async def startup_db_client():
    app.state.db = db

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Authentication Models
class GoogleTokenRequest(BaseModel):
    token: str

class LoginResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"

# Pydantic Models
class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Add user_id to associate documents with users
    filename: str
    file_type: str
    content: str
    summary: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    questions: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Flashcard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    cards: List[Dict[str, str]]  # [{"term": "...", "definition": "..."}]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    document_id: str
    message: str

# AI Service Classes
class AIContentGenerator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_summary(self, content: str) -> str:
        """Generate a concise summary of the document content"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"summary_{uuid.uuid4()}",
                system_message="You are an expert at creating concise, informative summaries of study materials. Create clear, structured summaries that capture the key concepts and main points."
            ).with_model("openai", "gpt-4o-mini")
            
            user_message = UserMessage(
                text=f"Please create a comprehensive summary of the following study material. Focus on key concepts, main points, and important details that a student should remember:\n\n{content[:8000]}"
            )
            
            response = await chat.send_message(user_message)
            return response
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Unable to generate summary at this time."

    async def generate_quiz(self, content: str) -> List[Dict[str, Any]]:
        """Generate a 10-question multiple choice quiz"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"quiz_{uuid.uuid4()}",
                system_message="You are an expert quiz creator. You MUST respond with valid JSON only. Do not include any text before or after the JSON array."
            ).with_model("openai", "gpt-4o-mini")
            
            user_message = UserMessage(
                text=f"""Create exactly 10 multiple-choice questions based on this study material. 

CRITICAL: Respond with ONLY a valid JSON array. No additional text, no markdown, no explanations.

Required JSON format:
[
  {{
    "question": "What is the main concept discussed?",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A",
    "explanation": "Brief explanation why this is correct"
  }}
]

Study Material:
{content[:6000]}"""
            )
            
            response = await chat.send_message(user_message)
            
            # Clean up response - remove markdown formatting if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()
            
            # Try parsing with retry logic
            for attempt in range(3):
                try:
                    questions = json.loads(cleaned_response)
                    
                    # Validate structure
                    if isinstance(questions, list) and len(questions) > 0:
                        # Validate each question has required fields
                        valid_questions = []
                        for q in questions:
                            if (isinstance(q, dict) and 
                                'question' in q and 
                                'options' in q and 
                                'correct_answer' in q and
                                isinstance(q['options'], list) and
                                len(q['options']) >= 4):
                                valid_questions.append(q)
                        
                        if valid_questions:
                            logger.info(f"Successfully generated {len(valid_questions)} quiz questions")
                            return valid_questions[:10]  # Limit to 10 questions
                    
                    break
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse attempt {attempt + 1} failed: {e}")
                    if attempt == 2:  # Last attempt
                        logger.error(f"Failed to parse quiz response after 3 attempts. Response: {cleaned_response[:500]}")
                        # Create a fallback quiz
                        return self._create_fallback_quiz(content)
                
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            
        return self._create_fallback_quiz(content)
    
    def _create_fallback_quiz(self, content: str) -> List[Dict[str, Any]]:
        """Create a simple fallback quiz when AI generation fails"""
        return [
            {
                "question": "Based on the uploaded material, what is the main topic discussed?",
                "options": [
                    "A) The content covers various educational concepts",
                    "B) The material focuses on technical information", 
                    "C) The document contains study-related content",
                    "D) The text discusses academic subjects"
                ],
                "correct_answer": "A",
                "explanation": "This is a general question based on your study material."
            },
            {
                "question": "What type of document did you upload?",
                "options": [
                    "A) Study notes or educational material",
                    "B) Entertainment content",
                    "C) Marketing material", 
                    "D) News article"
                ],
                "correct_answer": "A",
                "explanation": "You uploaded this document to create study materials."
            }
        ]

    async def generate_flashcards(self, content: str) -> List[Dict[str, str]]:
        """Generate flashcards with key terms and definitions"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"flashcards_{uuid.uuid4()}",
                system_message="You are an expert at creating educational flashcards. Extract key terms, concepts, and definitions from study materials."
            ).with_model("openai", "gpt-4o-mini")
            
            user_message = UserMessage(
                text=f"""Create flashcards from this study material. Return ONLY a JSON array in this exact format:
[
  {{
    "term": "Key term or concept",
    "definition": "Clear, concise definition or explanation"
  }}
]

Create 15-20 flashcards covering the most important concepts. Study Material:
{content[:6000]}"""
            )
            
            response = await chat.send_message(user_message)
            try:
                flashcards = json.loads(response)
                return flashcards
            except json.JSONDecodeError:
                logger.error("Failed to parse flashcards JSON response")
                return []
                
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return []

    async def chat_with_document(self, content: str, user_question: str) -> str:
        """AI tutor chat functionality with RAG"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"tutor_{uuid.uuid4()}",
                system_message=f"You are an AI tutor helping students understand their study material. Answer questions based on the provided document content. Be helpful, clear, and educational. Here's the document content for reference:\n\n{content[:6000]}"
            ).with_model("openai", "gpt-4o-mini")
            
            user_message = UserMessage(
                text=user_question
            )
            
            response = await chat.send_message(user_message)
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again."

# File Processing Functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_image(file_content: bytes) -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting image text: {e}")
        return ""

def get_file_type(file_content: bytes) -> str:
    """Determine file type using python-magic"""
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        return mime_type
    except Exception as e:
        logger.error(f"Error determining file type: {e}")
        return "unknown"

# Initialize AI generator
ai_generator = AIContentGenerator()

# Authentication Routes
@api_router.post("/auth/google", response_model=LoginResponse)
async def google_auth(
    request: Request, 
    token_request: GoogleTokenRequest
):
    """Authenticate with Google OAuth token"""
    try:
        auth_service = AuthService(db)
        
        # Verify Google token and get user data
        google_user_data = await auth_service.verify_google_token(token_request.token)
        
        # Get or create user
        user = await auth_service.get_or_create_user(google_user_data)
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        # Create response
        response = JSONResponse({
            "user": user.dict(),
            "access_token": access_token,
            "token_type": "bearer"
        })
        
        # Set HTTP-only cookie for web clients
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 7  # 7 days
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Google authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@api_router.post("/auth/logout")
async def logout():
    """Logout user"""
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# API Routes
@api_router.get("/")
async def root():
    return {"message": "StudyGenie API is running!"}

@api_router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document (PDF or image)"""
    try:
        # Read file content
        file_content = await file.read()
        file_type = get_file_type(file_content)
        
        # Extract text based on file type
        text_content = ""
        if "pdf" in file_type.lower():
            text_content = extract_text_from_pdf(file_content)
        elif "image" in file_type.lower():
            text_content = extract_text_from_image(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or image files.")
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file.")
        
        # Create document record with user association
        document = Document(
            user_id=current_user.id,  # Associate with current user
            filename=file.filename,
            file_type=file_type,
            content=text_content
        )
        
        # Save to database
        await db.documents.insert_one(document.dict())
        
        # Generate summary in background
        asyncio.create_task(generate_content_for_document(document.id, text_content))
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")

async def generate_content_for_document(document_id: str, content: str):
    """Background task to generate summary, quiz, and flashcards"""
    try:
        # Generate summary
        summary = await ai_generator.generate_summary(content)
        await db.documents.update_one(
            {"id": document_id},
            {"$set": {"summary": summary, "processed_at": datetime.now(timezone.utc)}}
        )
        
        # Generate quiz
        quiz_questions = await ai_generator.generate_quiz(content)
        if quiz_questions:
            quiz = Quiz(document_id=document_id, questions=quiz_questions)
            await db.quizzes.insert_one(quiz.dict())
        
        # Generate flashcards
        flashcard_data = await ai_generator.generate_flashcards(content)
        if flashcard_data:
            flashcards = Flashcard(document_id=document_id, cards=flashcard_data)
            await db.flashcards.insert_one(flashcards.dict())
        
        logger.info(f"Generated content for document {document_id}")
    except Exception as e:
        logger.error(f"Error generating content for document {document_id}: {e}")

@api_router.get("/documents", response_model=List[Document])
async def get_documents(current_user: User = Depends(get_current_user)):
    """Get all uploaded documents for the current user"""
    try:
        documents = await db.documents.find({"user_id": current_user.id}).to_list(100)
        return [Document(**doc) for doc in documents]
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@api_router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific document for the current user"""
    try:
        document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return Document(**document)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")

@api_router.get("/documents/{document_id}/quiz")
async def get_quiz(document_id: str, current_user: User = Depends(get_current_user)):
    """Get quiz for a document owned by current user"""
    try:
        # Verify document ownership first
        document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        quiz = await db.quizzes.find_one({"document_id": document_id})
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return Quiz(**quiz)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quiz")

@api_router.get("/documents/{document_id}/flashcards")
async def get_flashcards(document_id: str, current_user: User = Depends(get_current_user)):
    """Get flashcards for a document owned by current user"""
    try:
        # Verify document ownership first
        document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        flashcards = await db.flashcards.find_one({"document_id": document_id})
        if not flashcards:
            raise HTTPException(status_code=404, detail="Flashcards not found")
        return Flashcard(**flashcards)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching flashcards: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch flashcards")

@api_router.post("/chat")
async def chat_with_document(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Chat with AI tutor about a document owned by current user"""
    try:
        # Verify document ownership
        document = await db.documents.find_one({"id": request.document_id, "user_id": current_user.id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate response
        response = await ai_generator.chat_with_document(document["content"], request.message)
        
        # Save chat message
        chat_message = ChatMessage(
            document_id=request.document_id,
            message=request.message,
            response=response
        )
        await db.chat_messages.insert_one(chat_message.dict())
        
        return {"response": response}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")

@api_router.get("/documents/{document_id}/chat-history")
async def get_chat_history(document_id: str, current_user: User = Depends(get_current_user)):
    """Get chat history for a document owned by current user"""
    try:
        # Verify document ownership
        document = await db.documents.find_one({"id": document_id, "user_id": current_user.id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        messages = await db.chat_messages.find({"document_id": document_id}).sort("timestamp", 1).to_list(100)
        return [ChatMessage(**msg) for msg in messages]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()