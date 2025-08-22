# Google OAuth Setup Guide for StudyGenie

This guide will help you set up Google OAuth authentication for local development.

## 🎯 Quick Status Check

Run this command to test your current configuration:
```bash
python test_google_auth.py
```

## 🔧 Step-by-Step Google Cloud Console Setup

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create a New Project**
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter project name: `studygenie-local-dev`
   - Click "Create"

### Step 2: Enable Required APIs

1. **Navigate to APIs & Services**
   - In the left sidebar: APIs & Services → Library
   
2. **Enable Google Identity Services**
   - Search for "Google Identity and Access Management (IAM) API"
   - Click on it and press "Enable"

### Step 3: Create OAuth Credentials

1. **Go to Credentials**
   - APIs & Services → Credentials
   
2. **Create OAuth Client ID**
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   
3. **Configure OAuth Consent Screen** (if prompted)
   - Choose "External" for user type
   - Fill in required fields:
     - App name: `StudyGenie Local Dev`
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   
4. **Configure OAuth Client**
   - Application type: "Web application"
   - Name: `StudyGenie Local Development`
   
5. **Add Authorized URLs**
   
   **Authorized JavaScript origins:**
   ```
   http://localhost:3000
   http://localhost:8001
   ```
   
   **Authorized redirect URIs:**
   ```
   http://localhost:8001/api/auth/google/callback
   ```
   
6. **Save and Get Credentials**
   - Click "Create"
   - Copy the "Client ID" and "Client Secret"

### Step 4: Update Environment Files

1. **Update `backend/.env`:**
   ```env
   GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET="GOCSPX-your-client-secret"
   ```

2. **Update `frontend/.env`:**
   ```env
   REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

## ⚡ Testing Your Setup

### Method 1: Automated Test
```bash
python test_google_auth.py
```

### Method 2: Manual Test
1. Start backend: `cd backend && uvicorn server:app --reload`
2. Start frontend: `cd frontend && yarn start`
3. Go to: `http://localhost:3000`
4. Click "Continue with Google"
5. Complete Google login flow

## 🐛 Common Issues and Solutions

### Issue 1: "redirect_uri_mismatch" Error
**Problem:** The redirect URI doesn't match what's configured in Google Console

**Solution:**
- Ensure you have `http://localhost:8001/api/auth/google/callback` in authorized redirect URIs
- Check for typos in the URL
- Ensure you're using HTTP (not HTTPS) for localhost

### Issue 2: "invalid_client" Error  
**Problem:** Client ID or secret is incorrect

**Solution:**
- Verify GOOGLE_CLIENT_ID in both `.env` files match exactly
- Ensure no extra spaces or quotes in the client ID
- Re-copy credentials from Google Console

### Issue 3: Cookies Not Working
**Problem:** Authentication tokens not persisting

**Solution:**
- Ensure `secure=False` in `backend/server.py` for localhost (already fixed)
- Check browser settings allow cookies from localhost
- Verify CORS is properly configured

### Issue 4: "origin_mismatch" Error
**Problem:** Frontend origin not authorized  

**Solution:**
- Add `http://localhost:3000` to "Authorized JavaScript origins"
- Clear browser cache and try again

### Issue 5: Google Identity Services Not Loading
**Problem:** Frontend can't load Google's authentication library

**Solution:**
- Check browser console for CSP (Content Security Policy) errors
- Ensure internet connection is stable
- Try disabling browser extensions temporarily

## 🔒 Security Considerations

### For Local Development:
- ✅ `secure=False` in cookies (HTTP localhost)
- ✅ JWT secret is generated and secure
- ✅ CORS properly configured for localhost

### For Production:
- 🔄 Change `secure=True` in cookies (HTTPS)
- 🔄 Update authorized origins to your production domain
- 🔄 Use environment-specific Google OAuth credentials
- 🔄 Generate new JWT secret for production

## 🧪 Advanced Testing

### Test Individual Components

1. **Test Google Token Verification:**
   ```bash
   # In backend directory with venv activated
   python -c "
   from auth import AuthService
   from motor.motor_asyncio import AsyncIOMotorClient
   import asyncio
   import os
   from dotenv import load_dotenv
   
   load_dotenv('.env')
   client = AsyncIOMotorClient(os.environ['MONGO_URL'])
   db = client[os.environ['DB_NAME']]
   auth = AuthService(db)
   print('Auth service initialized successfully')
   "
   ```

2. **Test Frontend Environment:**
   ```bash
   cd frontend
   npm start
   # Check browser console at http://localhost:3000
   # Verify REACT_APP_GOOGLE_CLIENT_ID is loaded
   ```

3. **Test Backend API:**
   ```bash
   cd backend
   uvicorn server:app --reload
   # Visit http://localhost:8001/docs
   # Try the /auth/me endpoint (should return 401)
   ```

## 📋 Verification Checklist

Before reporting issues, ensure:

- [ ] Google Cloud project created and APIs enabled
- [ ] OAuth client configured with correct redirect URIs
- [ ] Environment files updated with correct credentials  
- [ ] Frontend and backend client IDs match exactly
- [ ] Cookie security set to `secure=False` for localhost
- [ ] CORS configured for `http://localhost:3000`
- [ ] Both servers start without errors
- [ ] Browser allows cookies from localhost
- [ ] No browser extensions blocking OAuth

## 🆘 Getting Help

If you're still having issues:

1. **Run the diagnostic:**
   ```bash
   python test_google_auth.py
   ```

2. **Check logs:**
   - Backend: Look at terminal output where uvicorn is running
   - Frontend: Check browser Developer Tools (F12) → Console

3. **Common log messages:**
   - `Invalid Google token` → Check client ID configuration
   - `Token not for this application` → Client ID mismatch
   - `CORS error` → Check CORS_ORIGINS in backend/.env

---

**Note:** This setup is optimized for local development. For production deployment, update the OAuth configuration with your production domain and enable HTTPS security features.