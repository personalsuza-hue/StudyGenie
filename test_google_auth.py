#!/usr/bin/env python3
"""
Google Authentication Configuration Test
This script verifies the Google OAuth setup and identifies potential issues.
"""

import os
import urllib.request
import urllib.error
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
backend_dir = Path(__file__).parent / 'backend'
load_dotenv(backend_dir / '.env')

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def test_google_oauth_config():
    """Test Google OAuth configuration"""
    print_colored("🔍 Testing Google OAuth Configuration", Colors.HEADER)
    print("=" * 60)
    
    # Check environment variables
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip('"')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip('"')
    jwt_secret = os.environ.get('JWT_SECRET', '').strip('"')
    
    issues_found = []
    
    # 1. Check if Google Client ID exists and format
    if not google_client_id:
        print_colored("❌ GOOGLE_CLIENT_ID not found in environment", Colors.FAIL)
        issues_found.append("Missing GOOGLE_CLIENT_ID")
    elif not google_client_id.endswith('.apps.googleusercontent.com'):
        print_colored("⚠️  GOOGLE_CLIENT_ID format seems incorrect", Colors.WARNING)
        print(f"   Current: {google_client_id}")
        print("   Expected format: xxxxxxxxxx-xxxxxxxxxx.apps.googleusercontent.com")
        issues_found.append("Invalid GOOGLE_CLIENT_ID format")
    else:
        print_colored("✅ GOOGLE_CLIENT_ID found and format looks correct", Colors.OKGREEN)
        print(f"   Client ID: {google_client_id}")
    
    # 2. Check Google Client Secret
    if not google_client_secret:
        print_colored("❌ GOOGLE_CLIENT_SECRET not found in environment", Colors.FAIL)
        issues_found.append("Missing GOOGLE_CLIENT_SECRET")
    elif not google_client_secret.startswith('GOCSPX-'):
        print_colored("⚠️  GOOGLE_CLIENT_SECRET format seems incorrect", Colors.WARNING)
        print(f"   Current format: {google_client_secret[:20]}...")
        print("   Expected to start with: GOCSPX-")
        issues_found.append("Invalid GOOGLE_CLIENT_SECRET format")
    else:
        print_colored("✅ GOOGLE_CLIENT_SECRET found and format looks correct", Colors.OKGREEN)
        print(f"   Secret: {google_client_secret[:15]}...")
    
    # 3. Check JWT Secret
    if not jwt_secret or jwt_secret == "your-super-secret-jwt-key-change-this-in-production-make-it-very-long-and-random":
        print_colored("⚠️  JWT_SECRET is using default value or empty", Colors.WARNING)
        print("   You should generate a secure random string for production")
        issues_found.append("Default JWT_SECRET")
    elif len(jwt_secret) < 32:
        print_colored("⚠️  JWT_SECRET is too short (should be at least 32 characters)", Colors.WARNING)
        issues_found.append("JWT_SECRET too short")
    else:
        print_colored("✅ JWT_SECRET looks secure", Colors.OKGREEN)
        print(f"   Length: {len(jwt_secret)} characters")
    
    # 4. Test Google tokeninfo endpoint accessibility
    print_colored("\n🌐 Testing Google OAuth endpoint accessibility...", Colors.OKBLUE)
    try:
        # Test with a dummy token to see if endpoint is accessible
        url = "https://oauth2.googleapis.com/tokeninfo?id_token=dummy"
        req = urllib.request.Request(url)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                # We don't expect this to succeed, just testing connectivity
                pass
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print_colored("✅ Google OAuth tokeninfo endpoint is accessible", Colors.OKGREEN)
            else:
                print_colored(f"⚠️  Unexpected response from Google: HTTP {e.code}", Colors.WARNING)
                
    except Exception as e:
        print_colored(f"❌ Cannot reach Google OAuth endpoint: {e}", Colors.FAIL)
        issues_found.append("Google OAuth endpoint not accessible")
    
    # 5. Check frontend environment variables
    frontend_env_path = Path(__file__).parent / 'frontend' / '.env'
    if frontend_env_path.exists():
        print_colored("\n📱 Checking frontend environment...", Colors.OKBLUE)
        with open(frontend_env_path, 'r') as f:
            frontend_env = f.read()
        
        if 'REACT_APP_GOOGLE_CLIENT_ID' in frontend_env:
            # Extract the client ID from frontend
            for line in frontend_env.split('\n'):
                if 'REACT_APP_GOOGLE_CLIENT_ID' in line and '=' in line:
                    frontend_client_id = line.split('=')[1].strip()
                    if frontend_client_id == google_client_id:
                        print_colored("✅ Frontend and backend Google Client IDs match", Colors.OKGREEN)
                    else:
                        print_colored("❌ Frontend and backend Google Client IDs don't match", Colors.FAIL)
                        print(f"   Backend: {google_client_id}")
                        print(f"   Frontend: {frontend_client_id}")
                        issues_found.append("Mismatched Client IDs")
        else:
            print_colored("❌ REACT_APP_GOOGLE_CLIENT_ID not found in frontend/.env", Colors.FAIL)
            issues_found.append("Missing frontend Google Client ID")
    else:
        print_colored("⚠️  Frontend .env file not found", Colors.WARNING)
        issues_found.append("Missing frontend .env file")
    
    # 6. Check cookie security settings
    print_colored("\n🍪 Checking cookie security configuration...", Colors.OKBLUE)
    print_colored("⚠️  Note: secure=True in cookie settings requires HTTPS", Colors.WARNING)
    print("   For local development (HTTP), this might cause issues")
    print("   Consider setting secure=False for localhost testing")
    
    # 7. Print Google Cloud Console setup instructions
    print_colored("\n🔧 Google Cloud Console Configuration Checklist:", Colors.HEADER)
    print("For your Google OAuth to work with localhost, ensure:")
    print("1. Go to https://console.cloud.google.com")
    print("2. Navigate to 'APIs & Services' → 'Credentials'")
    print("3. Find your OAuth 2.0 Client ID")
    print("4. In 'Authorized JavaScript origins', add:")
    print("   - http://localhost:3000")
    print("   - http://localhost:8001")
    print("5. In 'Authorized redirect URIs', you may need:")
    print("   - http://localhost:8001/api/auth/google/callback (if using server-side flow)")
    print("6. Enable Google Identity Services API if not already enabled")
    print("7. Save the configuration")
    
    # 8. Check for known issues
    print_colored("\n⚠️  Known Issues and Solutions:", Colors.WARNING)
    print("1. 'Cookie secure=True' issue:")
    print("   - For localhost, set secure=False in backend/server.py line ~344")
    print("2. CORS issues:")
    print("   - Ensure CORS_ORIGINS includes http://localhost:3000")
    print("3. Google Identity Services not loading:")
    print("   - Check browser console for CSP or network errors")
    
    # Summary
    print_colored(f"\n📊 Google OAuth Configuration Test Results:", Colors.HEADER)
    if not issues_found:
        print_colored("🎉 All Google OAuth configurations look good!", Colors.OKGREEN)
        print_colored("\n📋 Next steps:", Colors.OKBLUE)
        print("1. Ensure your Google Cloud Console is configured (see checklist above)")
        print("2. Consider setting secure=False for local development cookies")
        print("3. Start the backend server: cd backend && uvicorn server:app --reload")
        print("4. Start the frontend: cd frontend && yarn start")
        print("5. Test login at http://localhost:3000")
    else:
        print_colored(f"⚠️  Found {len(issues_found)} issue(s):", Colors.WARNING)
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print_colored("\n🔧 How to fix:", Colors.OKBLUE)
        if "Missing GOOGLE_CLIENT_ID" in issues_found or "Missing GOOGLE_CLIENT_SECRET" in issues_found:
            print("• Get OAuth credentials from Google Cloud Console:")
            print("  1. Go to console.cloud.google.com")
            print("  2. Create project → APIs & Services → Credentials")
            print("  3. Create OAuth 2.0 Client ID")
            print("  4. Update backend/.env with the credentials")
        
        if "Default JWT_SECRET" in issues_found:
            print("• Generate a secure JWT secret:")
            print("  python -c \"import secrets; print(secrets.token_urlsafe(64))\"")
            print("  Update JWT_SECRET in backend/.env")

def main():
    test_google_oauth_config()

if __name__ == "__main__":
    main()