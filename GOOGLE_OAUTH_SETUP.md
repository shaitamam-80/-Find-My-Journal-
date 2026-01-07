# 🔐 Google OAuth Setup Guide - Find My Journal

## ✅ Checklist

- [ ] Google Cloud Console project created
- [ ] Google+ API enabled
- [ ] OAuth 2.0 Credentials created
- [ ] Redirect URIs configured
- [ ] Client ID and Secret saved securely
- [ ] Supabase Google provider enabled
- [ ] Client ID added to Supabase
- [ ] Client Secret added to Supabase
- [ ] Test login successful

---

## 📋 Step 1: Google Cloud Console Setup

### 1.1 Create or Select a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click **NEW PROJECT**
4. Enter project details:
   - **Project name**: `FindMyJournal` (or any name you prefer)
   - **Organization**: Leave as-is or select if you have one
5. Click **CREATE**
6. Wait for the project to be created (takes ~30 seconds)
7. Make sure the new project is selected in the dropdown

### 1.2 Enable Google+ API

1. In the left sidebar, click **APIs & Services** > **Library**
2. In the search box, type: `Google+ API`
3. Click on **Google+ API** from the results
4. Click the **ENABLE** button
5. Wait for it to enable (takes ~10 seconds)

> **Note**: You might also see "Google Identity" or "Google Sign-In" - those work too!

### 1.3 Create OAuth 2.0 Credentials

1. In the left sidebar, click **APIs & Services** > **Credentials**
2. Click the **+ CREATE CREDENTIALS** button at the top
3. Select **OAuth client ID** from the dropdown

#### Configure OAuth Consent Screen (if prompted)

If this is your first time, you'll be asked to configure the consent screen:

1. Click **CONFIGURE CONSENT SCREEN**
2. Select **External** (unless you have a Google Workspace)
3. Click **CREATE**
4. Fill in the required fields:
   - **App name**: `Find My Journal`
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click **SAVE AND CONTINUE**
6. On "Scopes" page, click **SAVE AND CONTINUE** (we don't need extra scopes)
7. On "Test users" page, click **SAVE AND CONTINUE**
8. Review and click **BACK TO DASHBOARD**

Now go back to create the OAuth client ID:

1. Click **APIs & Services** > **Credentials** again
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Select **Application type**: **Web application**
4. Enter a name: `Find My Journal Web Client`

### 1.4 Configure Authorized Redirect URIs

**IMPORTANT**: You need your Supabase Project URL first!

#### How to find your Supabase Project URL:

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your **Find My Journal** project
3. Click **Settings** (⚙️) > **API**
4. Copy the **Project URL** (example: `https://abcdefghijklmnop.supabase.co`)

#### Add the Redirect URI:

In the Google Cloud Console OAuth client setup:

1. Scroll down to **Authorized redirect URIs**
2. Click **+ ADD URI**
3. Paste: `https://<YOUR_SUPABASE_PROJECT>.supabase.co/auth/v1/callback`

   **Example**: If your Supabase URL is `https://abcdefghijklmnop.supabase.co`, then enter:
   ```
   https://abcdefghijklmnop.supabase.co/auth/v1/callback
   ```

4. (Optional) For local testing, add another URI:
   - Click **+ ADD URI** again
   - Paste: `http://localhost:54321/auth/v1/callback`

5. Click **CREATE**

### 1.5 Save Your Credentials

After clicking CREATE, a popup will appear with your credentials:

```
Client ID: 123456789-abc123def456.apps.googleusercontent.com
Client Secret: GOCSPX-xxxxxxxxxxxxxxxxxxxxx
```

**⚠️ CRITICAL**:
- Copy both values to a safe place (text file, password manager)
- You'll need these in the next step
- The Client Secret is shown only once - if you lose it, you'll need to regenerate

---

## 📋 Step 2: Supabase Dashboard Configuration

### 2.1 Enable Google Provider

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your **Find My Journal** project
3. In the left sidebar, click **Authentication** > **Providers**
4. Scroll down and find **Google**
5. Toggle the **Enable Sign in with Google** switch to **ON**

### 2.2 Add Your Credentials

Still on the Google provider settings page:

1. Paste your **Client ID** from Google Cloud Console into the **Client ID** field
2. Paste your **Client Secret** from Google Cloud Console into the **Client Secret** field
3. Leave other settings as default:
   - **Skip nonce check**: OFF (more secure)
   - **Authorized Client IDs**: Leave empty
4. Click **Save**

### 2.3 Verify Callback URL

On the same page, you should see:

```
Callback URL (for OAuth):
https://<your-project>.supabase.co/auth/v1/callback
```

**Verify**: This URL matches exactly what you entered in Google Cloud Console!

### 2.4 ⚠️ CRITICAL: Configure Redirect URLs

**This is the most important step!** Without this, OAuth will fail silently.

1. In the left sidebar, click **Authentication** > **URL Configuration**
2. Find the **Site URL** field and set it to:
   ```
   https://find-my-journal.vercel.app
   ```
3. Find the **Redirect URLs** field and add these URLs (one per line):
   ```
   https://find-my-journal.vercel.app/auth/callback
   https://find-my-journal.vercel.app/search
   https://find-my-journal.vercel.app/*
   http://localhost:3000/auth/callback
   http://localhost:3000/search
   http://localhost:3000/*
   ```
4. Click **Save**

**Why these URLs?**
- `/auth/callback` - OAuth redirect handler (processes Google callback)
- `/search` - Final destination after authentication
- `/*` - Wildcard for any other app pages
- `localhost:3000` - Local development URLs

---

## 📋 Step 3: Test Your Setup

### 3.1 Test Locally (if dev server is running)

If you have the frontend running locally:

1. Open http://localhost:3000/login
2. Click **Continue with Google**
3. You should be redirected to Google's login page
4. Sign in with your Google account
5. Grant permissions when asked
6. You should be redirected back to `/search`

**Expected behavior**:
- ✅ Redirects to Google login
- ✅ Shows consent screen
- ✅ Redirects back to your app
- ✅ User is logged in

**Common errors**:
- ❌ "redirect_uri_mismatch" → Check that URIs match exactly in Google Console
- ❌ "Access blocked" → Check Client ID/Secret in Supabase
- ❌ "Invalid client" → Regenerate credentials in Google Console

### 3.2 Test in Production (Vercel)

After deploying to Vercel:

1. Open https://find-my-journal.vercel.app/login
2. Click **Continue with Google**
3. Sign in and test

### 3.3 Verify User Creation

After successful login:

1. Go to Supabase Dashboard
2. Click **Authentication** > **Users**
3. You should see your user with:
   - **Provider**: `google`
   - **Email**: Your Google email
   - **User Metadata**: Contains name, picture, etc.

---

## 🔒 Security Checklist

Before going to production, verify:

- [ ] Client Secret is NOT in any frontend code
- [ ] Client Secret is NOT committed to Git
- [ ] Redirect URIs in Google Console match Supabase exactly
- [ ] RLS policies are enabled on all database tables
- [ ] Only production domains are in Redirect URIs (remove localhost for production)

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause**: The callback URL doesn't match what's in Google Console

**Fix**:
1. Go to Google Cloud Console > Credentials
2. Click on your OAuth client
3. Check **Authorized redirect URIs**
4. Make sure it includes: `https://<your-supabase-project>.supabase.co/auth/v1/callback`
5. Save and wait 5 minutes for changes to propagate

### Error: "Access blocked: This app's request is invalid"

**Cause**: Client ID or Client Secret mismatch

**Fix**:
1. Go to Google Cloud Console > Credentials
2. Copy the Client ID and Client Secret again
3. Go to Supabase Dashboard > Authentication > Providers > Google
4. Re-paste the values
5. Save

### Error: User created but not in database

**Cause**: Backend `/auth/me` endpoint might not handle OAuth users

**Fix**:
Check that `backend/app/api/v1/auth.py` creates a user profile automatically for new OAuth users.

---

## 📝 Notes

- Google OAuth credentials are free
- You can have multiple redirect URIs (local + production)
- Changes in Google Console can take up to 5 minutes to propagate
- Always test in an incognito window to avoid cached credentials

---

## ✅ Success!

If everything works, users can now:
- Sign in with "Continue with Google"
- No password management needed
- Secure authentication via Google

Your app now has Google OAuth! 🎉
