# Testing Your StudyBuddy App

## Local Testing Workflow

### 1. Backend Setup & Database Initialization

```bash
cd backend

# Install dependencies
uv sync

# Copy environment file
cp env.example .env

# Edit backend/.env file with your settings:
# DATABASE_URL=your_neon_postgres_url_here
# SECRET_KEY=your-secret-key-here
# ADMIN_USERNAME=your_username
# ADMIN_PASSWORD=your_secure_password

# Initialize database and create admin user
uv run python init_db.py

# Start the server
uv run uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (including new react-router-dom)
pnpm install

# Copy environment file
cp env.example .env

# Edit frontend/.env file:
# VITE_API_BASE_URL=http://localhost:8000

# Start the development server
pnpm dev
```

### 3. Test the Complete Workflow

#### A. Authentication

1. Go to `http://localhost:5173`
2. You should be redirected to `/login`
3. Login with your admin credentials
4. You should see the navigation bar with StudyBuddy

#### B. PDF Upload & Card Generation (LOCAL ONLY)

1. Click "Upload PDF" in navigation
2. Upload a PDF file (like your existing CSC280 PDFs)
3. Set subject: "CSC280" and test: "Test1"
4. Click "Generate Flashcards"
5. Cards should be created in your Neon PostgreSQL database
6. **Note**: PDF upload only works locally with Ollama running

#### C. Manual Card Creation

1. Click "Create Cards" in navigation
2. Fill out the form:
   - Subject: "CSC280"
   - Test: "Test2"
   - Front: "What is a binary tree?"
   - Back: "A tree data structure where each node has at most two children"
3. Click "Add Card"
4. Repeat for more cards
5. Click "Sync X Cards to Database"
6. Cards should be saved to your remote database

#### D. Study Session

1. Click "Study" in navigation (or go to `/`)
2. Select your subject and test
3. View flashcards list
4. Click "Study" to start flashcard session
5. Mark cards as mastered/unmastered

### 4. Verify Database Changes

You can check your Neon PostgreSQL database to see:

- Users table with your admin account (hashed password)
- Subjects table with your subjects
- Tests table with your tests
- Flashcards table with all your cards

### 5. Test Production Deployment

**Important**: Production deployment is for STUDYING ONLY, not card creation.

1. Set up Neon PostgreSQL database
2. Deploy to Vercel with environment variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
3. Update frontend environment:
   - `VITE_API_BASE_URL=https://your-app.vercel.app/api`

**Production Workflow:**

- ✅ Study flashcards on any device
- ✅ View your card collections
- ✅ Track mastery progress
- ❌ PDF upload (Ollama not available)
- ❌ Card creation (use local app for this)

## Expected Results

✅ **Local Development:**

- SQLite database for local development
- All features working locally
- Authentication with hashed passwords

✅ **Production:**

- PostgreSQL database (Neon)
- Secure authentication
- All cards synced to remote database
- Study cards on any device
- No card creation (use local app for that)

✅ **Features Working:**

- PDF upload and AI card generation
- Manual card creation
- Study sessions with mastery tracking
- Proper routing and navigation
- Secure authentication

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**

   - Check DATABASE_URL format
   - Verify Neon database is running
   - Check network connectivity

2. **Authentication Issues**

   - Run `python init_db.py` to create admin user
   - Check SECRET_KEY is set
   - Verify ADMIN_USERNAME/ADMIN_PASSWORD

3. **Frontend Routing Issues**

   - Make sure react-router-dom is installed
   - Check all components are imported correctly

4. **API Connection Issues**
   - Verify VITE_API_BASE_URL is correct
   - Check backend is running on port 8000
   - Check CORS settings in backend

### Database Verification:

```sql
-- Check users table
SELECT * FROM users;

-- Check subjects
SELECT * FROM subjects;

-- Check tests
SELECT * FROM tests;

-- Check flashcards
SELECT * FROM flashcards;
```

This workflow ensures you can create cards locally and have them properly synced to your remote PostgreSQL database! 🎯
