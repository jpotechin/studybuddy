import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// Fetch subjects
export const useSubjects = () =>
  useQuery({
    queryKey: ["subjects"],
    queryFn: () =>
      fetch("http://localhost:8000/subjects").then((res) => res.json()),
  });

// Fetch tests for a subject
export const useTests = (subjectId: number) =>
  useQuery({
    queryKey: ["tests", subjectId],
    queryFn: () =>
      fetch(`http://localhost:8000/subjects/${subjectId}/tests`).then((res) =>
        res.json()
      ),
    enabled: !!subjectId, // only fetch if subjectId exists
  });

// Fetch flashcards for a test
export const useFlashcards = (testId: number) =>
  useQuery({
    queryKey: ["flashcards", testId],
    queryFn: () =>
      fetch(`http://localhost:8000/tests/${testId}/flashcards`).then((res) =>
        res.json()
      ),
    enabled: !!testId,
  });

// ... your existing useSubjects, useTests, useFlashcards

// Update flashcard mastery
export const useUpdateMastery = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ flashcardId, mastered }: { flashcardId: number; mastered: boolean }) =>
      fetch(`http://localhost:8000/flashcards/${flashcardId}/mastered`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mastered),
      }).then((res) => res.json()),
    onSuccess: () => {
      // Invalidate all flashcards queries to refetch the updated data
      queryClient.invalidateQueries({ queryKey: ["flashcards"] });
    },
  });
};
