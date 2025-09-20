import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// Get API base URL from environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

// Fetch subjects
export const useSubjects = () =>
  useQuery({
    queryKey: ["subjects"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/subjects`, {
        headers: getAuthHeaders(),
      }).then((res) => {
        if (!res.ok) throw new Error('Failed to fetch subjects');
        return res.json();
      }),
  });

// Fetch tests for a subject
export const useTests = (subjectId: number) =>
  useQuery({
    queryKey: ["tests", subjectId],
    queryFn: () =>
      fetch(`${API_BASE_URL}/subjects/${subjectId}/tests`, {
        headers: getAuthHeaders(),
      }).then((res) => {
        if (!res.ok) throw new Error('Failed to fetch tests');
        return res.json();
      }),
    enabled: !!subjectId, // only fetch if subjectId exists
  });

// Fetch flashcards for a test
export const useFlashcards = (testId: number) =>
  useQuery({
    queryKey: ["flashcards", testId],
    queryFn: () =>
      fetch(`${API_BASE_URL}/tests/${testId}/flashcards`, {
        headers: getAuthHeaders(),
      }).then((res) => {
        if (!res.ok) throw new Error('Failed to fetch flashcards');
        return res.json();
      }),
    enabled: !!testId,
  });

// ... your existing useSubjects, useTests, useFlashcards

// Update flashcard mastery
export const useUpdateMastery = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ flashcardId, mastered }: { flashcardId: number; mastered: boolean }) =>
      fetch(`${API_BASE_URL}/flashcards/${flashcardId}/mastered`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify(mastered),
      }).then((res) => {
        if (!res.ok) throw new Error('Failed to update flashcard');
        return res.json();
      }),
    onSuccess: () => {
      // Invalidate all flashcards queries to refetch the updated data
      queryClient.invalidateQueries({ queryKey: ["flashcards"] });
    },
  });
};
