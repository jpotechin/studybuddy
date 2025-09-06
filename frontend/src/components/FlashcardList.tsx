import { type FC } from "react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
      <div className="flex items-center justify-between p-4 bg-card border rounded-lg shadow-sm">
        <div>
          <h2 className="text-2xl font-bold">Flashcards List</h2>
          <p className="text-muted-foreground mt-1">
            {subjectName} - {testName}
          </p>
        </div>
        <Button variant="outline" onClick={onBack}>
          🔙 Back to Tests
        </Button>
      </div>

      {/* Content Section */}
      <div className="border rounded-lg shadow-sm">
        {flashcards.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-muted-foreground">No flashcards available.</p>
          </div>
        ) : (
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="w-[70%] font-semibold">Question</TableHead>
                <TableHead className="w-[20%] text-center font-semibold">Status</TableHead>
                <TableHead className="w-[10%] text-center font-semibold">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {flashcards.map((card, index) => (
                <TableRow
                  key={card.id}
                  className="cursor-pointer hover:bg-muted/50 transition-colors border-b last:border-b-0"
                  onClick={() => onStudy(index)}
                >
                  <TableCell className="font-medium py-4">
                    {card.front}
                  </TableCell>
                  <TableCell className="text-center py-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      card.mastered 
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" 
                        : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                    }`}>
                      {card.mastered ? "✅ Mastered" : "❌ Not Mastered"}
                    </span>
                  </TableCell>
                  <TableCell className="text-center py-4">
                    {card.mastered && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => handleUnmaster(e, card.id)}
                        className="text-xs"
                      >
                        Unmaster
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
};

export default FlashcardList;
