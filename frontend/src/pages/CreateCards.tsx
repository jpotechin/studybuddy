import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Trash2, Upload } from 'lucide-react';

interface Flashcard {
  front: string;
  back: string;
  subject: string;
  test: string;
}

export const CreateCards: React.FC = () => {
  const { token } = useAuth();
  const [searchParams] = useSearchParams();
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentCard, setCurrentCard] = useState<Flashcard>({
    front: '',
    back: '',
    subject: '',
    test: ''
  });

  // Pre-fill subject and test from URL parameters
  useEffect(() => {
    const subject = searchParams.get('subject');
    const test = searchParams.get('test');
    
    if (subject || test) {
      setCurrentCard(prev => ({
        ...prev,
        subject: subject || prev.subject,
        test: test || prev.test
      }));
    }
  }, [searchParams]);

  const addCard = () => {
    if (currentCard.front.trim() && currentCard.back.trim() && currentCard.subject.trim() && currentCard.test.trim()) {
      setCards([...cards, { ...currentCard }]);
      // Keep subject and test, only clear front and back
      setCurrentCard(prev => ({ ...prev, front: '', back: '' }));
    }
  };

  const removeCard = (index: number) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  const syncToRemote = async () => {
    if (cards.length === 0) return;
    
    try {
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
    } catch (error) {
      alert('Failed to sync cards: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Flashcards</h1>
        <p className="text-gray-600">
          Create flashcards manually and sync them to your remote database
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card Creation Form */}
        <Card>
          <CardHeader>
            <CardTitle>Add New Card</CardTitle>
            <CardDescription>
              Fill in the details for your flashcard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Subject</label>
                <Input
                  placeholder="e.g., CSC280"
                  value={currentCard.subject}
                  onChange={(e) => setCurrentCard({ ...currentCard, subject: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Test</label>
                <Input
                  placeholder="e.g., Test1"
                  value={currentCard.test}
                  onChange={(e) => setCurrentCard({ ...currentCard, test: e.target.value })}
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700">Front (Question/Term)</label>
              <Input
                placeholder="What is the question or term?"
                value={currentCard.front}
                onChange={(e) => setCurrentCard({ ...currentCard, front: e.target.value })}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700">Back (Answer/Definition)</label>
              <Input
                placeholder="What is the answer or definition?"
                value={currentCard.back}
                onChange={(e) => setCurrentCard({ ...currentCard, back: e.target.value })}
              />
            </div>
            
            <Button onClick={addCard} className="w-full" disabled={!currentCard.front.trim() || !currentCard.back.trim() || !currentCard.subject.trim() || !currentCard.test.trim()}>
              <Plus className="h-4 w-4 mr-2" />
              Add Card
            </Button>
          </CardContent>
        </Card>

        {/* Cards List and Sync */}
        <Card>
          <CardHeader>
            <CardTitle>Your Cards ({cards.length})</CardTitle>
            <CardDescription>
              Review and sync your flashcards to the database
            </CardDescription>
          </CardHeader>
          <CardContent>
            {cards.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No cards created yet.</p>
                <p className="text-sm">Add your first card using the form on the left.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="max-h-96 overflow-y-auto space-y-3">
                  {cards.map((card, index) => (
                    <div key={index} className="p-4 border rounded-lg bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-xs text-gray-500 mb-1">
                            {card.subject} - {card.test}
                          </div>
                          <div className="font-medium text-sm mb-1">{card.front}</div>
                          <div className="text-sm text-gray-700">{card.back}</div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeCard(index)}
                          className="ml-2 text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
                
                <Button onClick={syncToRemote} className="w-full" size="lg">
                  <Upload className="h-4 w-4 mr-2" />
                  Sync {cards.length} Cards to Database
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
