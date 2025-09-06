const API_URL = "http://localhost:8000"; // no trailing slash

export async function fetchSubjects() {
  const res = await fetch(`${API_URL}/subjects`);
  return res.json();
}

export async function fetchTests(subjectId: number) {
  const res = await fetch(`${API_URL}/subjects/${subjectId}/tests`);
  return res.json();
}

export async function fetchFlashcards(testId: number) {
  const res = await fetch(`${API_URL}/tests/${testId}/flashcards`);
  return res.json();
}

export async function setFlashcardMastered(cardId: number, mastered: boolean) {
  const form = new FormData();
  form.append("mastered", String(mastered));
  await fetch(`${API_URL}/flashcards/${cardId}/mastered`, {
    method: "POST",
    body: form,
  });
}
