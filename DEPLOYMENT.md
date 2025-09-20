# StudyBuddy Deployment Guide

This guide will help you deploy your StudyBuddy app to Vercel with a PostgreSQL database.

## Architecture Overview

- **Frontend**: React + Vite (deployed to Vercel)
- **Backend**: FastAPI (deployed as Vercel serverless functions)
- **Database**: PostgreSQL (Neon or PlanetScale)

## Prerequisites

1. Vercel account
2. Neon or PlanetScale account (for PostgreSQL)
3. GitHub repository with your code

## Step 1: Set Up Database

### Option A: Neon (Recommended)

1. Go to [Neon](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string (it looks like: `postgresql://username:password@host/database`)

### Option B: PlanetScale

1. Go to [PlanetScale](https://planetscale.com) and create a free account
2. Create a new database
3. Get the connection string

## Step 2: Deploy to Vercel

### 2.1 Connect Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository

### 2.2 Configure Environment Variables

In Vercel dashboard, go to your project settings and add these environment variables:

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key-change-this-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here
```

### 2.3 Deploy

1. Vercel will automatically detect your configuration
2. The `vercel.json` file will handle routing:
   - `/api/*` routes go to your FastAPI backend
   - All other routes serve your React frontend

## Step 3: Update Frontend Environment

After deployment, update your frontend environment variable:

```
VITE_API_BASE_URL=https://your-app-name.vercel.app/api
```

## Step 4: Test Deployment

1. Visit your Vercel URL
2. Try uploading a PDF
3. Check if flashcards are generated and stored

## Local Development

### Backend Setup

```bash
cd backend
uv sync  # Install dependencies
cp ../env.example .env  # Copy environment template
# Edit .env and add your DATABASE_URL (or leave empty for SQLite)
# Set ADMIN_USERNAME and ADMIN_PASSWORD for security

# Initialize database and create admin user
uv run python init_db.py

# Start the server
uv run uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
pnpm install
cp ../frontend-env.example .env  # Copy environment template
# Edit .env and set VITE_API_BASE_URL=http://localhost:8000
pnpm dev
```

## Important Notes

### Authentication

- The app uses a simple single-user authentication system
- Admin credentials are set via environment variables
- Passwords are hashed using bcrypt before storage
- Run `python init_db.py` to create your admin account

### Local Card Creation

- You can create flashcards locally without uploading PDFs
- Use the "Create Flashcards Locally" feature in the app
- Cards are stored locally until you sync them to the remote database
- This allows you to study offline and sync when online

### Ollama Integration

- **Local Development**: Ollama is used for PDF processing and card generation
- **Production Deployment**: Ollama is NOT needed - production is for studying only
- **Workflow**: Create cards locally with Ollama → Sync to remote database → Study on any device

### Database Migration

- Your existing SQLite data won't automatically migrate
- You can export data from SQLite and import to PostgreSQL if needed
- Or start fresh with the new database

### File Uploads

- Vercel has limitations on request body size (4.5MB for Pro, 1MB for Hobby)
- Large PDF files might need to be handled differently

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

   - Verify DATABASE_URL is correct
   - Check if database allows connections from Vercel's IP ranges

2. **CORS Errors**

   - The FastAPI CORS middleware should handle this
   - If issues persist, update `allow_origins` in main.py

3. **Environment Variables Not Loading**

   - Ensure variables are set in Vercel dashboard
   - Redeploy after adding new environment variables

4. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies are in pyproject.toml

### Debugging

- Check Vercel function logs in the dashboard
- Use browser dev tools to inspect network requests
- Verify environment variables are loaded correctly

## Cost Considerations

- **Vercel Hobby**: Free tier with limitations
- **Vercel Pro**: $20/month for higher limits
- **Neon Free**: 3GB storage, good for development
- **PlanetScale Free**: 1GB storage, 1 billion reads/month

## Next Steps

1. Set up monitoring and error tracking
2. Configure custom domain
3. Set up automated backups
4. Consider implementing user authentication
5. Add rate limiting for API endpoints

## Support

If you encounter issues:

1. Check Vercel deployment logs
2. Verify database connectivity
3. Test endpoints individually
4. Check environment variable configuration
