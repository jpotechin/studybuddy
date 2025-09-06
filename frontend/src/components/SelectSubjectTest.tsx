import { useState, useEffect } from "react";
import { useSubjects, useTests, useFlashcards } from "../api/hooks";
import { Button } from "@/components/ui/button";

interface Flashcard {
  id: number;
  front: string;
  back: string;
  mastered: boolean;
}

interface Subject {
  id: number;
  name: string;
}

interface Test {
  id: number;
  name: string;
}

interface Props {
  onSelectTest: (testId: number, subjectId: number) => void;
}

export default function SelectSubjectTest({ onSelectTest }: Props) {
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(
    null
  );

  // Fetch subjects
  const { data: subjects, isLoading: loadingSubjects } = useSubjects();

  // Fetch tests for the selected subject
  const { data: tests, isLoading: loadingTests } = useTests(
    selectedSubjectId || 0
  );

  // Fetch flashcards for a test
  const [selectedTestId, setSelectedTestId] = useState<number | null>(null);
  const { data: flashcards, isLoading: loadingFlashcards } = useFlashcards(
    selectedTestId || 0
  );

  // Handle test click
  const handleTestClick = (testId: number) => {
    setSelectedTestId(testId);
  };

  // When a test is selected, call parent
  useEffect(() => {
    if (selectedTestId !== null && selectedSubjectId !== null) {
      onSelectTest(selectedTestId, selectedSubjectId);
    }
  }, [selectedTestId, selectedSubjectId, onSelectTest]);

  // Loading states
  if (loadingSubjects) return <p>Loading subjects...</p>;
  if (selectedSubjectId && loadingTests) return <p>Loading tests...</p>;
  if (selectedTestId && loadingFlashcards) return <p>Loading flashcards...</p>;

  // Render subjects or tests
  if (!selectedSubjectId) {
    return (
      <div>
        <h2 className="text-xl mb-2">Choose Subject</h2>
        {subjects?.map((s: Subject) => (
          <Button
            key={s.id}
            className="m-2"
            onClick={() => setSelectedSubjectId(s.id)}
          >
            {s.name}
          </Button>
        ))}
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl mb-2">Choose Test</h2>
      {tests?.map((t: Test) => (
        <Button
          key={t.id}
          className="m-2"
          onClick={() => handleTestClick(t.id)}
        >
          {t.name}
        </Button>
      ))}

      <Button
        variant="outline"
        className="mt-4"
        onClick={() => setSelectedSubjectId(null)}
      >
        🔙 Back to Subjects
      </Button>
    </div>
  );
}
