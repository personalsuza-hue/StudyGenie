import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Auth Components
import ProtectedRoute from './components/auth/ProtectedRoute';

// Components
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Separator } from './components/ui/separator';
import { ScrollArea } from './components/ui/scroll-area';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';

// Icons
import { Upload, FileText, MessageCircle, Brain, BookOpen, Lightbulb, CheckCircle, Clock, Trophy, Target, LogOut, User } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// User Header Component
const UserHeader = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">StudyGenie</h1>
              <p className="text-slate-600">AI-Powered Study Guide Generator</p>
            </div>
          </div>
          
          {user && (
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                {user.picture && (
                  <img 
                    src={user.picture} 
                    alt={user.name}
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-800">{user.name}</p>
                  <p className="text-xs text-slate-600">{user.email}</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={logout}
                className="flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

// File Upload Component
const FileUploader = ({ onUpload, isUploading }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await axios.post(`${API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onUpload(response.data);
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && (file.type.includes('pdf') || file.type.includes('image'))) {
      handleFileSelect(file);
    }
  };

  return (
    <Card className="border-2 border-dashed border-slate-300 bg-gradient-to-br from-blue-50 to-indigo-50">
      <CardContent className="p-8">
        <div
          className={`text-center space-y-4 ${dragOver ? 'scale-105' : ''} transition-transform`}
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
        >
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <Upload className="w-8 h-8 text-blue-600" />
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">Upload Study Material</h3>
            <p className="text-slate-600 mb-4">Drop your PDF or image files here, or click to browse</p>
            
            <input
              type="file"
              accept=".pdf,image/*"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="hidden"
              id="file-upload"
            />
            
            <label htmlFor="file-upload">
              <Button variant="outline" className="cursor-pointer hover:bg-blue-50">
                Choose File
              </Button>
            </label>
          </div>
          
          {selectedFile && (
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-slate-700">{selectedFile.name}</span>
                </div>
                <Button onClick={handleUpload} disabled={isUploading} className="bg-blue-600 hover:bg-blue-700">
                  {isUploading ? 'Processing...' : 'Upload & Generate'}
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Document List Component
const DocumentsList = ({ documents, onSelectDocument, selectedDocument }) => {
  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <Card 
          key={doc.id} 
          className={`cursor-pointer transition-all hover:shadow-md ${
            selectedDocument?.id === doc.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-slate-50'
          }`}
          onClick={() => onSelectDocument(doc)}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-slate-800">{doc.filename}</h4>
                  <p className="text-sm text-slate-600">
                    Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                {doc.summary && <Badge variant="secondary">Summary</Badge>}
                {doc.processed_at && (
                  <>
                    <Badge variant="outline">Quiz</Badge>
                    <Badge variant="outline">Flashcards</Badge>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// Quiz Component
const QuizView = ({ documentId, onComplete }) => {
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const response = await axios.get(`${API}/documents/${documentId}/quiz`);
        setQuiz(response.data);
      } catch (error) {
        console.error('Failed to fetch quiz:', error);
      } finally {
        setLoading(false);
      }
    };

    if (documentId) {
      fetchQuiz();
    }
  }, [documentId]);

  const handleAnswerSelect = (questionIndex, answer) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer
    });
  };

  const calculateScore = () => {
    let correct = 0;
    quiz.questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.correct_answer) {
        correct++;
      }
    });
    setScore(correct);
    setShowResults(true);
    onComplete(correct, quiz.questions.length);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600">Loading quiz...</p>
        </CardContent>
      </Card>
    );
  }

  if (!quiz) {
    return (
      <Alert>
        <AlertDescription>Quiz is being generated. Please check back in a moment.</AlertDescription>
      </Alert>
    );
  }

  if (showResults) {
    return (
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-green-600">Quiz Complete!</CardTitle>
          <CardDescription>Here are your results</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-slate-800 mb-2">
              {score}/{quiz.questions.length}
            </div>
            <Progress value={(score / quiz.questions.length) * 100} className="w-full max-w-xs mx-auto" />
            <p className="text-slate-600 mt-2">
              {score >= quiz.questions.length * 0.8 ? 'Excellent work!' : 
               score >= quiz.questions.length * 0.6 ? 'Good job!' : 'Keep studying!'}
            </p>
          </div>
          
          <div className="space-y-4">
            {quiz.questions.map((question, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <p className="font-medium mb-2">{question.question}</p>
                <div className="space-y-1">
                  {question.options.map((option, optIndex) => (
                    <div 
                      key={optIndex}
                      className={`p-2 rounded ${
                        option.charAt(0) === question.correct_answer 
                          ? 'bg-green-100 text-green-800' 
                          : selectedAnswers[index] === option.charAt(0)
                          ? 'bg-red-100 text-red-800'
                          : 'bg-slate-50'
                      }`}
                    >
                      {option}
                    </div>
                  ))}
                </div>
                {question.explanation && (
                  <p className="mt-2 text-sm text-slate-600 italic">{question.explanation}</p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentQ = quiz.questions[currentQuestion];

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Quiz Question {currentQuestion + 1} of {quiz.questions.length}</CardTitle>
          <Progress value={((currentQuestion + 1) / quiz.questions.length) * 100} className="w-32" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="text-lg font-medium text-slate-800">
          {currentQ.question}
        </div>
        
        <div className="space-y-3">
          {currentQ.options.map((option, index) => (
            <Button
              key={index}
              variant={selectedAnswers[currentQuestion] === option.charAt(0) ? "default" : "outline"}
              className="w-full text-left justify-start h-auto p-4"
              onClick={() => handleAnswerSelect(currentQuestion, option.charAt(0))}
            >
              {option}
            </Button>
          ))}
        </div>
        
        <div className="flex justify-between">
          <Button 
            variant="outline" 
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
          >
            Previous
          </Button>
          
          {currentQuestion === quiz.questions.length - 1 ? (
            <Button 
              onClick={calculateScore}
              disabled={Object.keys(selectedAnswers).length < quiz.questions.length}
              className="bg-green-600 hover:bg-green-700"
            >
              Submit Quiz
            </Button>
          ) : (
            <Button 
              onClick={() => setCurrentQuestion(currentQuestion + 1)}
              disabled={!selectedAnswers[currentQuestion]}
            >
              Next
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Flashcards Component
const FlashcardsView = ({ documentId }) => {
  const [flashcards, setFlashcards] = useState(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFlashcards = async () => {
      try {
        const response = await axios.get(`${API}/documents/${documentId}/flashcards`);
        setFlashcards(response.data);
      } catch (error) {
        console.error('Failed to fetch flashcards:', error);
      } finally {
        setLoading(false);
      }
    };

    if (documentId) {
      fetchFlashcards();
    }
  }, [documentId]);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600">Loading flashcards...</p>
        </CardContent>
      </Card>
    );
  }

  if (!flashcards || !flashcards.cards.length) {
    return (
      <Alert>
        <AlertDescription>Flashcards are being generated. Please check back in a moment.</AlertDescription>
      </Alert>
    );
  }

  const currentFlashcard = flashcards.cards[currentCard];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">
          Card {currentCard + 1} of {flashcards.cards.length}
        </h3>
        <Progress value={((currentCard + 1) / flashcards.cards.length) * 100} className="w-48 mx-auto" />
      </div>
      
      <Card 
        className="min-h-[300px] cursor-pointer transition-transform hover:scale-105"
        onClick={() => setFlipped(!flipped)}
      >
        <CardContent className="p-8 flex items-center justify-center text-center">
          <div className="space-y-4">
            <div className="text-sm text-slate-500 uppercase tracking-wide">
              {flipped ? 'Definition' : 'Term'}
            </div>
            <div className="text-xl font-medium text-slate-800">
              {flipped ? currentFlashcard.definition : currentFlashcard.term}
            </div>
            <div className="text-sm text-slate-500">
              Click to {flipped ? 'see term' : 'reveal definition'}
            </div>
          </div>
        </CardContent>
      </Card>
      
      <div className="flex justify-between">
        <Button 
          variant="outline"
          onClick={() => {
            setCurrentCard(Math.max(0, currentCard - 1));
            setFlipped(false);
          }}
          disabled={currentCard === 0}
        >
          Previous
        </Button>
        
        <Button 
          onClick={() => {
            setCurrentCard(Math.min(flashcards.cards.length - 1, currentCard + 1));
            setFlipped(false);
          }}
          disabled={currentCard === flashcards.cards.length - 1}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

// AI Tutor Chat Component
const AITutorChat = ({ documentId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { message: input, response: null, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/chat`, {
        document_id: documentId,
        message: input
      });
      
      const aiMessage = { message: input, response: response.data.response, isUser: false };
      setMessages(prev => [...prev.slice(0, -1), userMessage, aiMessage]);
    } catch (error) {
      console.error('Chat failed:', error);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  return (
    <Card className="h-[500px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <MessageCircle className="w-5 h-5" />
          <span>AI Tutor</span>
        </CardTitle>
        <CardDescription>Ask questions about your study material</CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col space-y-4">
        <ScrollArea className="flex-1 border rounded-lg p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-slate-500 py-8">
                Start a conversation by asking a question about your document!
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-lg ${
                  msg.isUser 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-slate-100 text-slate-800'
                }`}>
                  {msg.isUser ? msg.message : msg.response}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 p-3 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            disabled={loading}
          />
          <Button onClick={sendMessage} disabled={loading || !input.trim()}>
            Send
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Study Interface
const StudyInterface = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const handleUpload = async (document) => {
    setIsUploading(true);
    try {
      await fetchDocuments();
      setSelectedDocument(document);
      setActiveTab('summary');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <UserHeader />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              <FileUploader onUpload={handleUpload} isUploading={isUploading} />
              
              {documents.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Your Documents</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <DocumentsList 
                      documents={documents}
                      onSelectDocument={setSelectedDocument}
                      selectedDocument={selectedDocument}
                    />
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {selectedDocument ? (
              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="summary" className="flex items-center space-x-2">
                    <BookOpen className="w-4 h-4" />
                    <span>Summary</span>
                  </TabsTrigger>
                  <TabsTrigger value="quiz" className="flex items-center space-x-2">
                    <Target className="w-4 h-4" />
                    <span>Quiz</span>
                  </TabsTrigger>
                  <TabsTrigger value="flashcards" className="flex items-center space-x-2">
                    <Lightbulb className="w-4 h-4" />
                    <span>Flashcards</span>
                  </TabsTrigger>
                  <TabsTrigger value="tutor" className="flex items-center space-x-2">
                    <MessageCircle className="w-4 h-4" />
                    <span>AI Tutor</span>
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="summary">
                  <Card>
                    <CardHeader>
                      <CardTitle>Document Summary</CardTitle>
                      <CardDescription>{selectedDocument.filename}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {selectedDocument.summary ? (
                        <div className="prose max-w-none">
                          <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                            {selectedDocument.summary}
                          </p>
                        </div>
                      ) : (
                        <Alert>
                          <Clock className="w-4 h-4" />
                          <AlertDescription>
                            Summary is being generated. This usually takes 1-2 minutes.
                          </AlertDescription>
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="quiz">
                  <QuizView 
                    documentId={selectedDocument.id} 
                    onComplete={(score, total) => {
                      console.log(`Quiz completed: ${score}/${total}`);
                    }}
                  />
                </TabsContent>

                <TabsContent value="flashcards">
                  <FlashcardsView documentId={selectedDocument.id} />
                </TabsContent>

                <TabsContent value="tutor">
                  <AITutorChat documentId={selectedDocument.id} />
                </TabsContent>
              </Tabs>
            ) : (
              <Card className="h-[500px] flex items-center justify-center">
                <CardContent className="text-center space-y-4">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto">
                    <FileText className="w-8 h-8 text-slate-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">No Document Selected</h3>
                    <p className="text-slate-600">Upload a document to get started with AI-powered study tools</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={
              <ProtectedRoute>
                <StudyInterface />
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;