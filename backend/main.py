from fastapi import Body, FastAPI, UploadFile, Form, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, pdfplumber, ollama
from db import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_db():
    return sqlite3.connect("study.db")

def parse_flashcards(text: str, model: str = "llama3.1"):
    import json, re

    prompt = f"""
Turn the following study material into flashcards. Generate as many as possible (at least 5 per chunk).
Respond ONLY in JSON as a list of objects with keys 'front' and 'back'.

Text:
{text}
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]

    all_cards = []

    try:
        # Try parsing the whole thing as JSON first
        all_cards.extend([(c["front"], c["back"]) for c in json.loads(raw)])
    except Exception:
        # Fallback: extract all JSON-looking arrays from the text
        matches = re.findall(r"\[.*?\]", raw, re.DOTALL)
        for m in matches:
            try:
                data = json.loads(m)
                all_cards.extend([(c["front"], c["back"]) for c in data])
            except Exception:
                continue  # skip invalid blocks

    return all_cards

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile, subject: str = Form(...), test: str = Form(...)):
    try:
        # Extract text
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")

        # Generate flashcards
        cards = parse_flashcards(text)
        if not cards:
            raise HTTPException(status_code=500, detail="Failed to generate flashcards")

        # Store in SQLite
        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT OR IGNORE INTO subjects(name) VALUES (?)", (subject,))
        subject_id = cur.execute("SELECT id FROM subjects WHERE name=?", (subject,)).fetchone()[0]

        cur.execute("INSERT OR IGNORE INTO tests(name, subject_id) VALUES (?,?)", (subject_id, test))
        test_id = cur.execute("SELECT id FROM tests WHERE name=? AND subject_id=?", (test, subject_id)).fetchone()[0]

        # Get existing flashcards for this test to check for duplicates
        cur.execute("SELECT front FROM flashcards WHERE test_id=?", (test_id,))
        existing_fronts = set(row[0] for row in cur.fetchall())

        # Only insert new flashcards (check by front text)
        new_cards = [(front, back) for front, back in cards if front not in existing_fronts]
        
        for front, back in new_cards:
            cur.execute("INSERT INTO flashcards(test_id, front, back) VALUES (?,?,?)",
                        (test_id, front, back))

        conn.commit()
        conn.close()

        skipped = len(cards) - len(new_cards)
        return {"message": f"Added {len(new_cards)} new flashcards (skipped {skipped} duplicates)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    from fastapi import Path

@app.get("/subjects")
def get_subjects():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects")
    rows = cur.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]

@app.get("/subjects/{subject_id}/tests")
def get_tests(subject_id: int = Path(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tests WHERE subject_id = ?", (subject_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": row[0], "subject_id": row[1], "name": row[2]} for row in rows]

@app.get("/tests/{test_id}/flashcards")
def get_flashcards(test_id: int = Path(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM flashcards WHERE test_id = ?", (test_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": row[0], "test_id": row[1], "front": row[2], "back": row[3], "mastered": bool(row[4])} for row in rows]

@app.patch("/flashcards/{flashcard_id}/mastered")
def update_mastered(flashcard_id: int, mastered: bool = Body(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE flashcards SET mastered=? WHERE id=?", (mastered, flashcard_id))
    conn.commit()
    conn.close()
    return {"id": flashcard_id, "mastered": mastered}

# Removed reset_db endpoint for production safety

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)