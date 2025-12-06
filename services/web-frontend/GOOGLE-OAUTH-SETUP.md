# 🔐 Google OAuth Setup - Step by Step

## Prerequisites
- A Google account (Gmail)
- Your Next.js app ready (already done ✅)

---

## Step 1: Access Google Cloud Console

1. Open your browser and go to:
   ```
   https://console.cloud.google.com/
   ```

2. Sign in with your Google account

---

## Step 2: Create a New Project

1. Click the **project dropdown** at the top (next to "Google Cloud")
   - It might say "Select a project" or show an existing project name

2. Click **"NEW PROJECT"** button (top right of the dialog)

3. Fill in project details:
   ```
   Project name: IIoT Predictive Maintenance
   Location: No organization
   ```

4. Click **"CREATE"**

5. Wait for the project to be created (10-30 seconds)

6. Click **"SELECT PROJECT"** when the notification appears

---

## Step 3: Enable Google+ API (Required for OAuth)

1. In the search bar at the top, type: `Google+ API`

2. Click on **"Google+ API"** from the results

3. Click the **"ENABLE"** button

4. Wait for it to enable (a few seconds)

---

## Step 4: Configure OAuth Consent Screen

1. In the left sidebar, click **"APIs & Services"** → **"OAuth consent screen"**
   
   OR use direct link:
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```

2. Choose **"External"** user type
   - This allows any Google user to sign in (for testing, you'll add specific test users)

3. Click **"CREATE"**

### 4.1: OAuth Consent Screen - App Information

Fill in the required fields:

```
App name: IIoT Predictive Maintenance Dashboard

User support email: [YOUR_EMAIL@gmail.com]
  → Select your email from dropdown

App logo: [Skip this - it's optional]

Application home page: http://localhost:3001

Application privacy policy: [Leave empty for now]

Application terms of service: [Leave empty for now]
```

Scroll down to **Developer contact information**:
```
Email addresses: [YOUR_EMAIL@gmail.com]
```

4. Click **"SAVE AND CONTINUE"**

### 4.2: Scopes (What data your app can access)

1. Click **"ADD OR REMOVE SCOPES"**

2. Select these scopes (they should be pre-selected):
   - ✅ `.../auth/userinfo.email`
   - ✅ `.../auth/userinfo.profile`
   - ✅ `openid`

3. Click **"UPDATE"** at the bottom

4. Click **"SAVE AND CONTINUE"**

### 4.3: Test Users (IMPORTANT!)

Since your app is in "Testing" mode, only test users can sign in.

1. Click **"+ ADD USERS"**

2. Enter your Gmail address:
   ```
   yourname@gmail.com
   ```

3. Click **"ADD"**

4. Add any other Gmail accounts you want to test with

5. Click **"SAVE AND CONTINUE"**

### 4.4: Summary

1. Review your settings

2. Click **"BACK TO DASHBOARD"**

---

## Step 5: Create OAuth 2.0 Credentials

1. In the left sidebar, click **"Credentials"**
   
   OR use direct link:
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. Click **"+ CREATE CREDENTIALS"** at the top

3. Select **"OAuth client ID"**

### 5.1: Application Type

1. Choose **"Web application"** from dropdown

2. Name your OAuth client:
   ```
   Name: IIoT Web Client
   ```

### 5.2: Authorized JavaScript Origins (Optional for now)

Leave this empty or add:
```
http://localhost:3001
```

### 5.3: Authorized Redirect URIs (CRITICAL!)

1. Click **"+ ADD URI"** under "Authorized redirect URIs"

2. Enter **EXACTLY** this URL:
   ```
   http://localhost:3001/api/auth/callback/google
   ```

   ⚠️ **IMPORTANT:** 
   - Must be exact (no trailing slash)
   - Port must be `3001` (the port your Next.js is running on)
   - Must include `/api/auth/callback/google`

3. Click **"CREATE"**

---

## Step 6: Copy Your Credentials

A dialog will appear with your credentials:

```
Your Client ID:
123456789-abcdefghijklmnop.apps.googleusercontent.com

Your Client Secret:
GOCSPX-1234567890abcdefghij
```

### 6.1: Save to `.env.local`

1. Click **"DOWNLOAD JSON"** (optional - for backup)

2. **Copy the Client ID**

3. Open your project in VS Code

4. Open `frontend/.env.local`

5. Replace the placeholder values:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-super-secret-key-min-32-chars-long-change-this-in-production

# Google OAuth - PASTE YOUR CREDENTIALS HERE
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdefghij

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

6. Generate a secure NEXTAUTH_SECRET:

**Option A - PowerShell:**
```powershell
# Generate random 32-character string
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Option B - Online:**
Visit: https://generate-secret.vercel.app/32

Copy the generated string and replace `your-super-secret-key-min-32-chars-long-change-this-in-production`

7. **Save the file** (Ctrl + S)

---

## Step 7: Test Your Setup

### 7.1: Start Your Backend
```powershell
# Terminal 1
cd C:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance
python api_server.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7.2: Start Your Frontend
```powershell
# Terminal 2
cd C:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance\frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3001
  
✓ Ready in 2.5s
```

### 7.3: Test Google Login

1. Open browser: http://localhost:3001

2. Click **"Sign In"** (top right) or **"Enter Console"**

3. You'll be redirected to: http://localhost:3001/login

4. Click **"Continue with Google"**

5. **Google's login page will appear:**
   - Sign in with the Gmail account you added as a test user
   - Click your account

6. **Google will ask for permissions:**
   ```
   IIoT Predictive Maintenance Dashboard wants to:
   ✓ See your email address
   ✓ See your personal info
   ```

7. Click **"Continue"** or **"Allow"**

8. **You'll be redirected to:** http://localhost:3001/dashboard

9. ✅ **Success!** You should see:
   - Your name/email in the top right
   - Real-time metrics (if backend is running)
   - Live chart

---

## Troubleshooting

### ❌ Error: "redirect_uri_mismatch"

**Problem:** The redirect URI doesn't match what you configured in Google Console.

**Solution:**
1. Check your browser's address bar - what port is Next.js using?
2. Go back to Google Cloud Console → Credentials
3. Click on your OAuth client
4. Update "Authorized redirect URIs" to match the correct port:
   ```
   http://localhost:3001/api/auth/callback/google
   ```
5. Click "SAVE"
6. Try logging in again

### ❌ Error: "Access blocked: This app's request is invalid"

**Problem:** You forgot to configure the OAuth consent screen.

**Solution:**
Go back to Step 4 and complete the OAuth consent screen configuration.

### ❌ Error: "Sign in with Google temporarily disabled"

**Problem:** Your account is not added as a test user.

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to "Test users"
3. Add your Gmail address
4. Try again

### ❌ NextAuth Error: "OAUTH_CALLBACK_ERROR"

**Problem:** Environment variables not loaded.

**Solution:**
1. Make sure `.env.local` is in the `frontend` folder (not root)
2. Restart Next.js dev server: Stop (Ctrl+C) and run `npm run dev` again
3. Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET have no extra spaces

---

## ✅ Verification Checklist

Before testing, make sure:

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Test user added (your Gmail)
- [ ] OAuth 2.0 credentials created
- [ ] Redirect URI is exactly: `http://localhost:3001/api/auth/callback/google`
- [ ] `frontend/.env.local` has correct GOOGLE_CLIENT_ID
- [ ] `frontend/.env.local` has correct GOOGLE_CLIENT_SECRET
- [ ] `frontend/.env.local` has NEXTAUTH_SECRET generated
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3001

---

## Production Deployment (Future)

When deploying to production (e.g., Vercel):

1. **Add production redirect URI:**
   ```
   https://yourdomain.com/api/auth/callback/google
   ```

2. **Update environment variables:**
   ```
   NEXTAUTH_URL=https://yourdomain.com
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

3. **Publish OAuth app:**
   - Go to OAuth consent screen
   - Click "PUBLISH APP"
   - Fill out verification form (required for production)

---

## 🎉 You're Done!

Your Google OAuth is now configured. Users can sign in with their Google accounts!

**Next steps:**
1. Start backend: `python api_server.py`
2. Start frontend: `npm run dev`
3. Visit: http://localhost:3001
4. Click "Sign In" → Test the flow!
