import requests
import sys
import time
import json
import io
from datetime import datetime
import os

class StudyGenieAPITester:
    def __init__(self, base_url=None):
        # Use environment variable or default to localhost
        if base_url is None:
            base_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.document_id = None
        self.access_token = None
        self.user_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        
        # Default headers
        test_headers = {}
        if data and not files:
            test_headers['Content-Type'] = 'application/json'
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Override with custom headers if provided
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.post(url, files=files, data=data, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_google_auth_invalid_token(self):
        """Test Google OAuth with invalid token"""
        invalid_token_data = {"token": "invalid_google_token_12345"}
        success, response = self.run_test("Google Auth - Invalid Token", "POST", "auth/google", 401, data=invalid_token_data)
        return success

    def test_google_auth_missing_token(self):
        """Test Google OAuth with missing token"""
        success, response = self.run_test("Google Auth - Missing Token", "POST", "auth/google", 422, data={})
        return success

    def test_auth_me_without_token(self):
        """Test /auth/me endpoint without authentication"""
        success, response = self.run_test("Auth Me - No Token", "GET", "auth/me", 401)
        return success

    def test_logout_endpoint(self):
        """Test logout endpoint"""
        success, response = self.run_test("Logout", "POST", "auth/logout", 200)
        return success

    def test_protected_routes_without_auth(self):
        """Test that protected routes return 401 without authentication"""
        print("\n🔒 Testing Protected Routes Without Authentication...")
        
        results = []
        
        # Test upload without auth
        test_data = {"test": "data"}
        success1, _ = self.run_test("Upload - No Auth", "POST", "upload", 401, data=test_data)
        results.append(success1)
        
        # Test get documents without auth
        success2, _ = self.run_test("Get Documents - No Auth", "GET", "documents", 401)
        results.append(success2)
        
        # Test get specific document without auth
        success3, _ = self.run_test("Get Document - No Auth", "GET", "documents/test-id", 401)
        results.append(success3)
        
        # Test quiz without auth
        success4, _ = self.run_test("Get Quiz - No Auth", "GET", "documents/test-id/quiz", 401)
        results.append(success4)
        
        # Test flashcards without auth
        success5, _ = self.run_test("Get Flashcards - No Auth", "GET", "documents/test-id/flashcards", 401)
        results.append(success5)
        
        # Test chat without auth
        chat_data = {"document_id": "test-id", "message": "test"}
        success6, _ = self.run_test("Chat - No Auth", "POST", "chat", 401, data=chat_data)
        results.append(success6)
        
        # Test chat history without auth
        success7, _ = self.run_test("Chat History - No Auth", "GET", "documents/test-id/chat-history", 401)
        results.append(success7)
        
        return all(results)

    def simulate_google_auth(self):
        """Simulate Google authentication by creating a mock JWT token"""
        print("\n🔐 Simulating Google Authentication...")
        
        # For testing purposes, we'll create a mock user and token
        # In a real scenario, this would involve actual Google OAuth flow
        
        # Create a test user directly in the database simulation
        import jwt
        from datetime import datetime, timedelta
        
        # Mock JWT token (this is for testing only)
        mock_user_data = {
            "user_id": "test_user_123",
            "email": "testuser@studygenie.com",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Use the same secret as in the backend
        jwt_secret = "your-super-secret-jwt-key-change-this-in-production-make-it-very-long-and-random"
        
        try:
            mock_token = jwt.encode(mock_user_data, jwt_secret, algorithm="HS256")
            self.access_token = mock_token
            self.user_data = {
                "id": "test_user_123",
                "email": "testuser@studygenie.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.jpg"
            }
            print("✅ Mock authentication successful")
            print(f"   User: {self.user_data['name']} ({self.user_data['email']})")
            return True
        except Exception as e:
            print(f"❌ Mock authentication failed: {e}")
            return False

    def test_auth_me_with_token(self):
        """Test /auth/me endpoint with valid token"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        success, response = self.run_test("Auth Me - With Token", "GET", "auth/me", 200)
        
        if success and isinstance(response, dict):
            print(f"   User ID: {response.get('id', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Name: {response.get('name', 'N/A')}")
        
        return success

    def test_upload_image(self):
        """Test image upload functionality with OCR (authenticated)"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        # Create a simple test image content
        try:
            # Create a minimal PNG image (1x1 pixel)
            import base64
            
            # Minimal PNG data (1x1 transparent pixel)
            png_data = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77yQAAAABJRU5ErkJggg=='
            )
            
            files = {'file': ('test_image.png', png_data, 'image/png')}
            success, response = self.run_test("Upload Image (Authenticated)", "POST", "upload", 200, files=files)
            
            if success and isinstance(response, dict) and 'id' in response:
                self.document_id = response['id']
                print(f"   Document ID: {self.document_id}")
                print(f"   User ID: {response.get('user_id', 'N/A')}")
                return True
            return False
            
        except Exception as e:
            print(f"   Error creating test image: {e}")
            return False

    def test_get_documents(self):
        """Test getting all documents (authenticated)"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        success, response = self.run_test("Get Documents (Authenticated)", "GET", "documents", 200)
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} documents")
            for doc in response:
                if doc.get('user_id') != self.user_data.get('id'):
                    print(f"   ⚠️  Document {doc.get('id')} has wrong user_id: {doc.get('user_id')}")
        
        return success

    def test_get_specific_document(self):
        """Test getting a specific document (authenticated)"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        success, response = self.run_test("Get Specific Document (Authenticated)", "GET", f"documents/{self.document_id}", 200)
        
        if success and isinstance(response, dict):
            if response.get('user_id') != self.user_data.get('id'):
                print(f"   ⚠️  Document has wrong user_id: {response.get('user_id')}")
        
        return success

    def test_user_data_isolation(self):
        """Test that users can only access their own documents"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        print("\n🔒 Testing User Data Isolation...")
        
        # Try to access a document with a different user ID
        fake_document_id = "other_user_document_123"
        success, response = self.run_test("Access Other User's Document", "GET", f"documents/{fake_document_id}", 404)
        
        return success

    def test_get_quiz(self):
        """Test getting quiz for document"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        # Wait a bit for background processing
        print("   Waiting 10 seconds for quiz generation...")
        time.sleep(10)
        
        success, response = self.run_test("Get Quiz", "GET", f"documents/{self.document_id}/quiz", 200)
        
        if success and isinstance(response, dict):
            questions = response.get('questions', [])
            print(f"   Quiz has {len(questions)} questions")
            if questions:
                print(f"   Sample question: {questions[0].get('question', 'N/A')[:50]}...")
        
        return success

    def test_get_flashcards(self):
        """Test getting flashcards for document"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        success, response = self.run_test("Get Flashcards", "GET", f"documents/{self.document_id}/flashcards", 200)
        
        if success and isinstance(response, dict):
            cards = response.get('cards', [])
            print(f"   Flashcards has {len(cards)} cards")
            if cards:
                print(f"   Sample card: {cards[0].get('term', 'N/A')[:30]}...")
        
        return success

    def test_chat_functionality(self):
        """Test AI tutor chat"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        chat_data = {
            "document_id": self.document_id,
            "message": "What is this document about?"
        }
        
        success, response = self.run_test("AI Chat", "POST", "chat", 200, data=chat_data)
        
        if success and isinstance(response, dict):
            ai_response = response.get('response', '')
            print(f"   AI Response length: {len(ai_response)} characters")
            print(f"   AI Response preview: {ai_response[:100]}...")
        
        return success

    def test_get_chat_history(self):
        """Test getting chat history"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        return self.run_test("Get Chat History", "GET", f"documents/{self.document_id}/chat-history", 200)

    def test_error_handling(self):
        """Test error handling with invalid requests"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid document ID
        success1, _ = self.run_test("Invalid Document ID", "GET", "documents/invalid-id", 404)
        
        # Test invalid quiz request
        success2, _ = self.run_test("Invalid Quiz Request", "GET", "documents/invalid-id/quiz", 404)
        
        # Test invalid chat request
        invalid_chat = {"document_id": "invalid-id", "message": "test"}
        success3, _ = self.run_test("Invalid Chat Request", "POST", "chat", 404, data=invalid_chat)
        
        return success1 and success2 and success3

def main():
    print("🚀 Starting StudyGenie API Tests")
    print("=" * 50)
    
    tester = StudyGenieAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic API tests
    test_results.append(tester.test_api_root())
    test_results.append(tester.test_upload_image())
    test_results.append(tester.test_get_documents())
    test_results.append(tester.test_get_specific_document())
    
    # AI content generation tests (these might take time)
    test_results.append(tester.test_get_quiz())
    test_results.append(tester.test_get_flashcards())
    test_results.append(tester.test_chat_functionality())
    test_results.append(tester.test_get_chat_history())
    
    # Error handling tests
    test_results.append(tester.test_error_handling())
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.document_id:
        print(f"Test Document ID: {tester.document_id}")
    
    # Return appropriate exit code
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())