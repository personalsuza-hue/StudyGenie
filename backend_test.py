import requests
import sys
import time
import json
import io
from datetime import datetime

class StudyGenieAPITester:
    def __init__(self, base_url="https://studygenie.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.document_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {}
        if data and not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)

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

    def test_upload_pdf(self):
        """Test PDF upload functionality"""
        # Create a simple test PDF content (mock)
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test Document Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n299\n%%EOF"
        
        files = {'file': ('test_document.pdf', test_content, 'application/pdf')}
        success, response = self.run_test("Upload PDF", "POST", "upload", 201, files=files)
        
        if success and isinstance(response, dict) and 'id' in response:
            self.document_id = response['id']
            print(f"   Document ID: {self.document_id}")
            return True
        return False

    def test_get_documents(self):
        """Test getting all documents"""
        return self.run_test("Get Documents", "GET", "documents", 200)

    def test_get_specific_document(self):
        """Test getting a specific document"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
        
        return self.run_test("Get Specific Document", "GET", f"documents/{self.document_id}", 200)

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
    test_results.append(tester.test_upload_pdf())
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