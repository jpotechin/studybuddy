# 📚 StudyBuddy

A modern flashcard application that helps you study by generating flashcards from PDFs and text files using AI. Built with React, TypeScript, FastAPI, and SQLite.

## ✨ Features

- **AI-Powered Flashcard Generation**: Automatically creates flashcards from PDF and text files using Ollama
- **Interactive Study Mode**: Flip cards, track mastery status, and navigate through your flashcards
- **Smart Duplicate Detection**: Prevents duplicate questions from being added
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Instant synchronization across all components
- **Modern UI**: Built with Shadcn UI components and Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with `uv` package manager
- **Node.js 18+** with `pnpm` package manager
- **Ollama** installed and running locally

### 1. Install Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull the AI model (in a new terminal)
ollama pull llama3.1
```

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd studybuddy
```

### 3. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Initialize database
uv run python -c "from db import init_db; init_db(); print('Database initialized!')"

# Start the FastAPI server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Setup Frontend (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
studybuddy/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database schema and connection
│   ├── import_pdf.py        # PDF import script
│   ├── import_txt.py        # Text file import script
│   ├── study.db             # SQLite database (auto-created)
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api/            # API hooks and queries
│   │   └── lib/            # Utilities
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── pdf/                    # PDF uploads (gitignored)
├── txt/                    # Text file uploads (gitignored)
└── README.md
```

## 🛠️ Usage

### Import Flashcards

#### From PDF Files

```bash
# Navigate to backend directory
cd backend

# Import PDF file
uv run python import_pdf.py --file ./pdf/subject/test/file.pdf --subject "Subject Name" --test "Test Name"
```

#### From Text Files

```bash
# Navigate to backend directory
cd backend

# Import text file
uv run python import_txt.py --file ./txt/subject/test/file.txt --subject "Subject Name" --test "Test Name"
```

#### Via Web Interface

1. Start both frontend and backend servers (see setup instructions above)
2. Navigate to http://localhost:5173
3. Select a subject and test
4. Upload PDF or text files through the interface

### Study Mode

1. **Select Subject**: Choose from available subjects
2. **Select Test**: Pick a test within the subject
3. **View List**: See all flashcards in a table format
4. **Study**: Click any flashcard to start studying from that card
5. **Track Progress**: Mark cards as mastered/unmastered
6. **Navigate**: Use Previous/Next buttons or click to flip cards

## 🔧 Configuration

### AI Model Configuration

The application uses Ollama with the `llama3.1` model by default. You can change this in:

- **Backend API**: `main.py` - `parse_flashcards()` function
- **Import Scripts**: `import_pdf.py` and `import_txt.py` - `--model` parameter

Available models: `llama3.1`, `mistral`, `codellama`, etc.

## 📊 Database Schema

### Subjects Table

- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT UNIQUE NOT NULL)

### Tests Table

- `id` (INTEGER PRIMARY KEY)
- `subject_id` (INTEGER FOREIGN KEY)
- `name` (TEXT NOT NULL)
- `UNIQUE(subject_id, name)`

### Flashcards Table

- `id` (INTEGER PRIMARY KEY)
- `test_id` (INTEGER FOREIGN KEY)
- `front` (TEXT NOT NULL) - Question
- `back` (TEXT NOT NULL) - Answer
- `mastered` (BOOLEAN DEFAULT 0)

## 🚀 Deployment

### Vercel Deployment

1. **Setup Database**: Use Vercel Postgres or similar
2. **Deploy Backend**: Deploy FastAPI to Vercel
3. **Deploy Frontend**: Deploy React app to Vercel
4. **Configure Ollama**: Set up Ollama service for AI functionality

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🧪 Development

### Backend Development

```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
pnpm run dev
```

### Database Management

```bash
# Navigate to backend directory
cd backend

# Reset database (development only)
rm -f study.db
uv run python -c "from db import init_db; init_db(); print('Database reset!')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**

- Ensure Ollama is running: `ollama serve`
- Check if port 8000 is available: `lsof -i :8000`
- Verify Python dependencies: `cd backend && uv sync`
- Check if you're in the correct directory: `cd backend`

**Frontend won't connect:**

- Ensure backend is running on port 8000
- Check if backend is accessible: `curl http://localhost:8000/subjects`
- Verify both servers are running simultaneously

**AI model not working:**

- Ensure Ollama is installed and running: `ollama serve`
- Pull the required model: `ollama pull llama3.1`
- Check model name in the code (default: llama3.1)
- Test Ollama directly: `ollama run llama3.1`

**Database errors:**

- Delete `study.db` and restart to reset: `cd backend && rm study.db`
- Check database permissions
- Verify SQLite installation
- Reinitialize database: `uv run python -c "from db import init_db; init_db()"`

**Import errors:**

- Ensure you're in the backend directory: `cd backend`
- Check file paths are correct
- Verify PDF/text files exist
- Check Ollama is running before importing

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the API documentation at http://localhost:8000/docs
- Ensure all prerequisites are installed correctly

## 🎯 Roadmap

- [ ] Spaced repetition algorithm
- [ ] Study statistics and analytics
- [ ] Deployment setup
- [ ] Advanced search and filtering

---

**Happy Studying! 📚✨**
