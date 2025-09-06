import argparse
import sqlite3
import pdfplumber
import ollama
import json
import re
from tqdm import tqdm

DB_PATH = "study.db"

def get_db():
    return sqlite3.connect(DB_PATH)

# -------------------------
# PDF Text Extraction
# -------------------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# -------------------------
# Chunking
# -------------------------
def chunk_text(words: list[str], chunk_size: int):
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

# -------------------------
# Generate flashcards per chunk
# -------------------------
def parse_flashcards(text_chunk: str, model: str = "llama3.1"):
    prompt = f"""
Turn the following study material into flashcards. Generate as many as possible (at least 5 per chunk).
Respond ONLY in JSON as a list of objects with keys 'front' and 'back'.

Text:
{text_chunk}
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

# -------------------------
# Insert flashcards into DB
# -------------------------
def insert_flashcards(subject: str, test: str, flashcards: list[tuple[str,str]]):
    if not flashcards:
        print("No flashcards to insert.")
        return

    conn = get_db()
    cur = conn.cursor()

    # Insert subject
    cur.execute("INSERT OR IGNORE INTO subjects(name) VALUES(?)", (subject,))
    cur.execute("SELECT id FROM subjects WHERE name=?", (subject,))
    subject_id = cur.fetchone()[0]

    # Insert test
    cur.execute(
        "INSERT OR IGNORE INTO tests(name, subject_id) VALUES(?, ?)", (test, subject_id)
    )
    cur.execute("SELECT id FROM tests WHERE name=? AND subject_id=?", (test, subject_id))
    test_id = cur.fetchone()[0]

    # Get existing flashcards for this test (check by front text only)
    cur.execute("SELECT front FROM flashcards WHERE test_id=?", (test_id,))
    existing_fronts = set(row[0] for row in cur.fetchall())

    # Filter out duplicates (check by front text only)
    new_cards = [(f, b) for f, b in flashcards if f not in existing_fronts]

    # Insert new flashcards
    for front, back in new_cards:
        cur.execute(
            "INSERT INTO flashcards(front, back, test_id) VALUES(?, ?, ?)",
            (front, back, test_id),
        )

    conn.commit()
    conn.close()
    print(f"Added {len(new_cards)} new flashcards to {subject} - {test} (skipped {len(flashcards)-len(new_cards)} duplicates)")

# -------------------------
# Main CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Import PDF and generate flashcards")
    parser.add_argument("--file", required=True, help="Path to PDF file")
    parser.add_argument("--subject", required=True, help="Subject name")
    parser.add_argument("--test", required=True, help="Test name")
    parser.add_argument("--model", default="llama3.1", help="Ollama model (llama3.1 or mistral)")
    parser.add_argument("--chunk_size", type=int, default=1000, help="Words per chunk")
    args = parser.parse_args()

    print(f"Reading PDF: {args.file}")
    text = extract_text_from_pdf(args.file)
    if not text.strip():
        print("No text found in PDF!")
        return

    words = text.split()
    total_words = len(words)
    num_chunks = (total_words + args.chunk_size - 1) // args.chunk_size

    print(f"PDF has {total_words} words → will be processed in {num_chunks} chunks (chunk size = {args.chunk_size})")

    all_flashcards = []

    # Use tqdm for progress bar
    for i, chunk in enumerate(tqdm(chunk_text(words, chunk_size=args.chunk_size), total=num_chunks, desc="Processing chunks")):
        flashcards = parse_flashcards(chunk, model=args.model)
        all_flashcards.extend(flashcards)

    insert_flashcards(args.subject, args.test, all_flashcards)
    print("Done!")

if __name__ == "__main__":
    main()
