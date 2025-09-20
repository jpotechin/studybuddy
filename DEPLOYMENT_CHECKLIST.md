# Vercel Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Variables in Vercel Dashboard

Go to Project Settings → Environment Variables and add:

**Backend Variables:**

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
```

**Frontend Variables:**

```
VITE_API_BASE_URL=https://your-app-name.vercel.app
```

### 2. Set Environment for All Deployments

- ✅ Production
- ✅ Preview
- ✅ Development

## Files Created/Updated

### ✅ Configuration Files

- `vercel.json` - Updated with proper Python configuration
- `backend/requirements.txt` - Created for Python dependencies
- `.vercelignore` - Created to exclude unnecessary files

### ✅ Documentation

- `VERCEL_ENV_SETUP.md` - Environment variable setup guide
- `DEPLOYMENT_CHECKLIST.md` - This checklist

## Common Build Issues Fixed

### 1. Python Dependencies

- ✅ Removed `ollama` and `pdfplumber` from main requirements
- ✅ Added `requirements.txt` for Vercel compatibility
- ✅ Increased Lambda size limit to 50mb

### 2. Environment Variables

- ✅ Organized with clear prefixes
- ✅ Proper VITE\_ prefix for frontend
- ✅ No quotes in Vercel dashboard

### 3. File Exclusions

- ✅ Added `.vercelignore` to exclude local files
- ✅ Excluded import scripts (local only)
- ✅ Excluded database files

## Deployment Steps

1. **Push to GitHub**
2. **Connect to Vercel** (if not already)
3. **Set environment variables** in Vercel dashboard
4. **Deploy** - Vercel will automatically build both frontend and backend
5. **Test** - Check both frontend and API endpoints

## Testing After Deployment

### Frontend

- ✅ Visit your Vercel URL
- ✅ Login with admin credentials
- ✅ Browse subjects/tests/flashcards

### Backend API

- ✅ Test login: `POST https://your-app.vercel.app/api/login`
- ✅ Test subjects: `GET https://your-app.vercel.app/api/subjects`

## Troubleshooting

### If Build Fails

1. Check Vercel function logs
2. Verify environment variables are set
3. Check Python dependencies in requirements.txt

### If Frontend Can't Connect to Backend

1. Verify `VITE_API_BASE_URL` is set correctly
2. Check API routes in vercel.json
3. Test API endpoints directly

### If Database Connection Fails

1. Verify `DATABASE_URL` is correct
2. Check if Neon database allows external connections
3. Test database connection locally first
