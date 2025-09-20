import argparse
import ollama
import json
import re
import sys
from pathlib import Path
from database import execute_query, insert_subject, insert_test, get_existing_flashcard_fronts, insert_flashcards
from auth import get_password_hash

# -------------------------
# Text File Reading
# -------------------------
def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# -------------------------
# Chunking
# -------------------------
def chunk_text(words: list[str], chunk_size: int):
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

# -------------------------
# Check if Ollama is available
# -------------------------
def check_ollama_available():
    try:
        ollama.list()
        return True
    except Exception as e:
        print(f"❌ ERROR: Ollama is not available!")
        print(f"   Error: {e}")
        print(f"   Please make sure Ollama is running:")
        print(f"   1. Start Ollama: ollama serve")
        print(f"   2. Pull a model: ollama pull llama3.1")
        print(f"   3. Try running this script again")
        return False

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

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"❌ ERROR: Failed to generate flashcards with Ollama!")
        print(f"   Error: {e}")
        print(f"   Make sure Ollama is running and the model '{model}' is available")
        return []

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
def insert_flashcards_to_db(subject: str, test: str, flashcards: list[tuple[str,str]]):
    if not flashcards:
        print("No flashcards to insert.")
        return

    # Use admin user ID (1) since this is a local import script
    user_id = 1

    # Insert subject
    subject_id = insert_subject(subject, user_id)

    # Insert test
    test_id = insert_test(test, subject_id)

    # Get existing flashcards for this test (check by front text only)
    existing_fronts = get_existing_flashcard_fronts(test_id)

    # Filter out duplicates (check by front text only)
    new_cards = [(f, b) for f, b in flashcards if f not in existing_fronts]

    # Insert new flashcards
    if new_cards:
        insert_flashcards(test_id, new_cards)

    print(f"Added {len(new_cards)} new flashcards to {subject} - {test} (skipped {len(flashcards)-len(new_cards)} duplicates)")

# -------------------------
# Main CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Import TXT file and generate flashcards")
    parser.add_argument("--file", required=True, help="Path to TXT file")
    parser.add_argument("--subject", required=True, help="Subject name")
    parser.add_argument("--test", required=True, help="Test name")
    parser.add_argument("--model", default="llama3.1", help="Ollama model (llama3.1 or mistral)")
    parser.add_argument("--chunk_size", type=int, default=1000, help="Words per chunk")
    args = parser.parse_args()

    # Check if Ollama is available before doing anything else
    print("🔍 Checking if Ollama is available...")
    if not check_ollama_available():
        sys.exit(1)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ ERROR: File {file_path} does not exist")
        sys.exit(1)

    print(f"Reading TXT: {args.file}")
    text = extract_text_from_txt(args.file)
    if not text.strip():
        print("No text found in TXT file!")
        return

    words = text.split()
    total_words = len(words)
    num_chunks = (total_words + args.chunk_size - 1) // args.chunk_size

    print(f"TXT has {total_words} words → will be processed in {num_chunks} chunks (chunk size = {args.chunk_size})")

    all_flashcards = []

    # Process chunks
    for i, chunk in enumerate(chunk_text(words, chunk_size=args.chunk_size)):
        print(f"Processing chunk {i+1}/{num_chunks}...")
        flashcards = parse_flashcards(chunk, model=args.model)
        all_flashcards.extend(flashcards)

    insert_flashcards_to_db(args.subject, args.test, all_flashcards)
    print("Done!")

if __name__ == "__main__":
    main()