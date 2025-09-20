import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface Flashcard {
  front: string;
  back: string;
  subject: string;
  test: string;
}

interface LocalCardCreatorProps {
  onSync: (cards: Flashcard[]) => void;
}

export const LocalCardCreator: React.FC<LocalCardCreatorProps> = ({ onSync }) => {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentCard, setCurrentCard] = useState<Flashcard>({
    front: '',
    back: '',
    subject: '',
    test: ''
  });

  const addCard = () => {
    if (currentCard.front.trim() && currentCard.back.trim() && currentCard.subject.trim() && currentCard.test.trim()) {
      setCards([...cards, { ...currentCard }]);
      setCurrentCard({ front: '', back: '', subject: '', test: '' });
    }
  };

  const removeCard = (index: number) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  const syncToRemote = async () => {
    if (cards.length === 0) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/upload_flashcards`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ flashcards: cards }),
      });

      if (!response.ok) {
        throw new Error('Failed to sync cards');
      }

      const result = await response.json();
      alert(`Successfully synced ${result.uploaded} cards! ${result.skipped} duplicates skipped.`);
      setCards([]); // Clear local cards after successful sync
      onSync(cards);
    } catch (error) {
      alert('Failed to sync cards: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Create Flashcards Locally</CardTitle>
        <CardDescription>
          Create flashcards offline and sync them to your remote database
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Card Creation Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 border rounded-lg">
          <div>
            <label className="text-sm font-medium">Subject</label>
            <Input
              placeholder="e.g., CSC280"
              value={currentCard.subject}
              onChange={(e) => setCurrentCard({ ...currentCard, subject: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Test</label>
            <Input
              placeholder="e.g., Test1"
              value={currentCard.test}
              onChange={(e) => setCurrentCard({ ...currentCard, test: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Front</label>
            <Input
              placeholder="Question or term"
              value={currentCard.front}
              onChange={(e) => setCurrentCard({ ...currentCard, front: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Back</label>
            <Input
              placeholder="Answer or definition"
              value={currentCard.back}
              onChange={(e) => setCurrentCard({ ...currentCard, back: e.target.value })}
            />
          </div>
          <div className="md:col-span-2">
            <Button onClick={addCard} className="w-full">
              Add Card
            </Button>
          </div>
        </div>

        {/* Local Cards List */}
        {cards.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium">Local Cards ({cards.length})</h3>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {cards.map((card, index) => (
                <div key={index} className="p-3 border rounded-lg bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm text-gray-600">
                        {card.subject} - {card.test}
                      </div>
                      <div className="font-medium">{card.front}</div>
                      <div className="text-sm text-gray-700">{card.back}</div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeCard(index)}
                      className="ml-2"
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <Button onClick={syncToRemote} className="w-full" variant="default">
              Sync {cards.length} Cards to Remote
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
