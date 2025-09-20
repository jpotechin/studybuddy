import { useState, useEffect } from "react";
import { useUpdateMastery } from "../api/hooks";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface Flashcard {
  id: number;
  front: string;
  back: string;
  mastered: boolean;
}

interface FlashcardPlayerProps {
  cards: Flashcard[];
  startIndex?: number;
}

export function FlashcardPlayer({ cards, startIndex = 0 }: FlashcardPlayerProps) {
  const [current, setCurrent] = useState(startIndex);
  const [isFlipped, setIsFlipped] = useState(false);
  const { mutate: updateMastery } = useUpdateMastery();

  // Reset current index if it's out of bounds
  useEffect(() => {
    if (current >= cards.length) {
      setCurrent(Math.max(0, cards.length - 1));
    }
  }, [cards.length, current]);

  // Reset flip state when card changes
  useEffect(() => {
    setIsFlipped(false);
  }, [current]);

  const card = cards[current];

  const handleToggleMastery = () => {
    if (!card) return;
    
    // Update on server (cache invalidation will handle UI update)
    updateMastery({ flashcardId: card.id, mastered: !card.mastered });
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const goToPrevious = () => {
    setCurrent(Math.max(0, current - 1));
  };

  const goToNext = () => {
    setCurrent(Math.min(cards.length - 1, current + 1));
  };

  if (!card) {
    return (
      <div className="space-y-6">
        <Card className="border-2 border-dashed">
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground text-lg">No flashcards available.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Progress Header */}
      <Card className="p-6">
        <CardContent className="text-center space-y-6">
          <CardTitle className="text-2xl">Flashcard {current + 1} of {cards.length}</CardTitle>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              card.mastered 
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" 
                : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
            }`}>
              {card.mastered ? "✅ Mastered" : "❌ Not Mastered"}
            </span>
            <Button
              variant="outline"
              onClick={handleToggleMastery}
              className="flex items-center gap-2 px-4 py-2"
            >
              {card.mastered ? "❌ Mark as Not Mastered" : "✅ Mark as Mastered"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Flashcard */}
      <div className="flex justify-center items-center min-h-96">
        <div 
          className="relative w-full max-w-md cursor-pointer transition-all duration-300 hover:scale-105 hover:-translate-y-1"
          onClick={handleFlip}
        >
          <div 
            className="w-full aspect-[4/3] transition-transform duration-500"
            style={{
              transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
              transformStyle: 'preserve-3d'
            }}
          >
            {/* Front of card */}
            <div 
              className="absolute inset-0 w-full h-full"
              style={{
                backfaceVisibility: 'hidden'
              }}
            >
              <Card className="w-full h-full flex flex-col">
                <CardHeader className="pb-2 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                      Question
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Click to flip
                    </CardDescription>
                  </div>
                </CardHeader>
                
                <CardContent className="flex-1 flex items-center justify-center pt-0 overflow-hidden">
                  <div className="text-center w-full px-4">
                    <div className="text-lg font-semibold leading-relaxed break-words hyphens-auto">
                      {card.front}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Back of card */}
            <div 
              className="absolute inset-0 w-full h-full"
              style={{
                backfaceVisibility: 'hidden',
                transform: 'rotateY(180deg)'
              }}
            >
              <Card className="w-full h-full flex flex-col">
                <CardHeader className="pb-2 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                      Answer
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Click to flip
                    </CardDescription>
                  </div>
                </CardHeader>
                
                <CardContent className="flex-1 flex items-center justify-center pt-0 overflow-hidden">
                  <div className="text-center w-full px-4">
                    <div className="text-base leading-relaxed text-muted-foreground break-words hyphens-auto">
                      {card.back}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <Card className="p-6">
        <CardContent className="space-y-6">
          <div className="flex justify-center">
            <Button
              variant="outline"
              onClick={handleFlip}
              className="flex items-center gap-2 px-6 py-2"
            >
              {isFlipped ? "Show Question" : "Show Answer"}
            </Button>
          </div>
          
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <Button
              variant="outline"
              onClick={goToPrevious}
              disabled={current === 0}
              className="flex items-center gap-2 px-4 py-2 w-full sm:w-auto"
            >
              ◀ Previous
            </Button>
            
            <CardDescription className="text-lg font-medium px-4 whitespace-nowrap">
              {current + 1} / {cards.length}
            </CardDescription>
            
            <Button
              variant="outline"
              onClick={goToNext}
              disabled={current === cards.length - 1}
              className="flex items-center gap-2 px-4 py-2 w-full sm:w-auto"
            >
              Next ▶
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
