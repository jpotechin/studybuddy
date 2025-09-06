import { useState } from "react";
import SelectSubjectTest from "./components/SelectSubjectTest";
import FlashcardList from "./components/FlashcardList";
import { FlashcardPlayer } from "./components/FlashcardPlayer";
import { useFlashcards, useSubjects, useTests } from "./api/hooks";

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

function App() {
  // State for selected test and subject
  const [selectedTestId, setSelectedTestId] = useState<number | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  
  // Get data from the API cache
  const { data: flashcards = [] } = useFlashcards(selectedTestId || 0);
  const { data: subjects = [] } = useSubjects();
  const { data: tests = [] } = useTests(selectedSubjectId || 0);

  // UI mode: "select" | "list" | "study"
  const [mode, setMode] = useState<"select" | "list" | "study">("select");
  
  // Track which card to start studying from
  const [startIndex, setStartIndex] = useState<number>(0);

  // Called when a test is selected
  const handleSelectTest = (testId: number, subjectId: number) => {
    setSelectedTestId(testId);
    setSelectedSubjectId(subjectId);
    setMode("list"); // show flashcard list first
  };

  // View list or study directly
  const handleStudy = (cardIndex: number = 0) => {
    setStartIndex(cardIndex);
    setMode("study");
  };

  const handleBackToTests = () => {
    setMode("select");
    setSelectedTestId(null);
    setSelectedSubjectId(null);
  };

  const handleBackToList = () => {
    setMode("list");
  };

  // Calculate mastered count
  const masteredCount = flashcards.filter((card: Flashcard) => card.mastered).length;
  const totalCount = flashcards.length;

  // Get subject and test names
  const subjectName = subjects.find((s: Subject) => s.id === selectedSubjectId)?.name || "";
  const testName = tests.find((t: Test) => t.id === selectedTestId)?.name || "";

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">📚 StudyBuddy</h1>
          {totalCount > 0 && (
            <div className="text-lg text-muted-foreground">
              <span className="font-semibold text-green-600 dark:text-green-400">
                {masteredCount}
              </span>
              {" / "}
              <span className="font-semibold">
                {totalCount}
              </span>
              {" mastered"}
            </div>
          )}
        </div>

        {mode === "select" && (
          <SelectSubjectTest onSelectTest={handleSelectTest} />
        )}

        {mode === "list" && (
          <FlashcardList
            flashcards={flashcards}
            subjectName={subjectName}
            testName={testName}
            onStudy={handleStudy}
            onBack={handleBackToTests}
          />
        )}

        {mode === "study" && (
          <div className="space-y-6">
            <FlashcardPlayer cards={flashcards} startIndex={startIndex} />
            <div className="flex justify-center">
              <button
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                onClick={handleBackToList}
              >
                🔙 Back to List
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
