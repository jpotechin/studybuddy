import { type FC } from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { useUpdateMastery } from "../api/hooks";

interface Flashcard {
  id: number;
  front: string;
  back: string;
  mastered: boolean;
}

interface FlashcardListProps {
  flashcards: Flashcard[];
  subjectName: string;
  testName: string;
  onStudy: (startIndex: number) => void;
  onBack: () => void;
}

const FlashcardList: FC<FlashcardListProps> = ({
  flashcards,
  subjectName,
  testName,
  onStudy,
  onBack,
}) => {
  const { mutate: updateMastery } = useUpdateMastery();

  const handleUnmaster = (e: React.MouseEvent, cardId: number) => {
    e.stopPropagation(); // Prevent row click
    updateMastery({ flashcardId: cardId, mastered: false });
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-card border rounded-lg shadow-sm">
        <div>
          <h2 className="text-2xl font-bold">Flashcards List</h2>
          <p className="text-muted-foreground mt-1">
            {subjectName} - {testName}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <Link 
            to={`/create?subject=${encodeURIComponent(subjectName)}&test=${encodeURIComponent(testName)}`}
            className="w-full sm:w-auto"
          >
            <Button variant="default" className="w-full sm:w-auto">
              ➕ Create Cards for This Test
            </Button>
          </Link>
          <Button variant="outline" onClick={onBack} className="w-full sm:w-auto">
            🔙 Back to Tests
          </Button>
        </div>
      </div>

      {/* Content Section */}
      <div className="border rounded-lg shadow-sm">
        {flashcards.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-muted-foreground">No flashcards available.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {flashcards.map((card, index) => (
              <div
                key={card.id}
                className="flex flex-col sm:flex-row items-start sm:items-center gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => onStudy(index)}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm sm:text-base break-words">
                    {card.front}
                  </p>
                </div>
                
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    card.mastered 
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" 
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  }`}>
                    {card.mastered ? "✅ Mastered" : "❌ Not Mastered"}
                  </span>
                  
                  {card.mastered && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => handleUnmaster(e, card.id)}
                      className="text-xs w-full sm:w-auto"
                    >
                      Unmaster
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FlashcardList;
