from fastapi import Body, FastAPI, UploadFile, Form, HTTPException, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber, ollama
from database import init_db, execute_query, insert_subject, insert_test, get_existing_flashcard_fronts, insert_flashcards
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from pydantic import BaseModel

# Pydantic models for authentication
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FlashcardCreate(BaseModel):
    front: str
    back: str
    subject: str
    test: str

class FlashcardsBatch(BaseModel):
    flashcards: list[FlashcardCreate]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Authentication endpoints
@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login a user"""
    user_data = authenticate_user(user.username, user.password)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_data["id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/upload_flashcards")
async def upload_flashcards_batch(batch: FlashcardsBatch, current_user: dict = Depends(get_current_user)):
    """Upload multiple flashcards created locally"""
    try:
        uploaded_count = 0
        skipped_count = 0
        
        for card_data in batch.flashcards:
            # Create subject and test
            subject_id = insert_subject(card_data.subject, current_user["id"])
            test_id = insert_test(card_data.test, subject_id)
            
            # Check if flashcard already exists
            existing_fronts = get_existing_flashcard_fronts(test_id)
            
            if card_data.front not in existing_fronts:
                insert_flashcards(test_id, [(card_data.front, card_data.back)])
                uploaded_count += 1
            else:
                skipped_count += 1
        
        return {
            "message": f"Uploaded {uploaded_count} new flashcards, skipped {skipped_count} duplicates",
            "uploaded": uploaded_count,
            "skipped": skipped_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def upload_pdf(file: UploadFile, subject: str = Form(...), test: str = Form(...), current_user: dict = Depends(get_current_user)):
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

        # Store in database
        subject_id = insert_subject(subject, current_user["id"])
        test_id = insert_test(test, subject_id)

        # Get existing flashcards for this test to check for duplicates
        existing_fronts = get_existing_flashcard_fronts(test_id)

        # Only insert new flashcards (check by front text)
        new_cards = [(front, back) for front, back in cards if front not in existing_fronts]
        
        if new_cards:
            insert_flashcards(test_id, new_cards)

        skipped = len(cards) - len(new_cards)
        return {"message": f"Added {len(new_cards)} new flashcards (skipped {skipped} duplicates)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    from fastapi import Path

@app.get("/subjects")
def get_subjects(current_user: dict = Depends(get_current_user)):
    rows = execute_query("SELECT * FROM subjects WHERE user_id = %s", (current_user["id"],))
    return [{"id": row['id'], "name": row['name']} for row in rows]

@app.get("/subjects/{subject_id}/tests")
def get_tests(subject_id: int = Path(...), current_user: dict = Depends(get_current_user)):
    # Verify the subject belongs to the user
    subject = execute_query("SELECT id FROM subjects WHERE id = %s AND user_id = %s", (subject_id, current_user["id"]), fetch_one=True)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    rows = execute_query("SELECT * FROM tests WHERE subject_id = %s", (subject_id,))
    return [{"id": row['id'], "subject_id": row['subject_id'], "name": row['name']} for row in rows]

@app.get("/tests/{test_id}/flashcards")
def get_flashcards(test_id: int = Path(...), current_user: dict = Depends(get_current_user)):
    # Verify the test belongs to the user through the subject
    test = execute_query("""
        SELECT t.id FROM tests t 
        JOIN subjects s ON t.subject_id = s.id 
        WHERE t.id = %s AND s.user_id = %s
    """, (test_id, current_user["id"]), fetch_one=True)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    rows = execute_query("SELECT * FROM flashcards WHERE test_id = %s", (test_id,))
    return [{"id": row['id'], "test_id": row['test_id'], "front": row['front'], "back": row['back'], "mastered": bool(row['mastered'])} for row in rows]

@app.patch("/flashcards/{flashcard_id}/mastered")
def update_mastered(flashcard_id: int, mastered: bool = Body(...), current_user: dict = Depends(get_current_user)):
    # Verify the flashcard belongs to the user
    flashcard = execute_query("""
        SELECT f.id FROM flashcards f
        JOIN tests t ON f.test_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE f.id = %s AND s.user_id = %s
    """, (flashcard_id, current_user["id"]), fetch_one=True)
    
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    execute_query("UPDATE flashcards SET mastered=%s WHERE id=%s", (mastered, flashcard_id), fetch_all=False)
    return {"id": flashcard_id, "mastered": mastered}

# Removed reset_db endpoint for production safety

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)