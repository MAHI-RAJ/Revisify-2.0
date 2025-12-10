import { useState } from 'react';
import { Flashcard } from '@/api/stepApi';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight, RotateCcw, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FlashcardsProps {
  flashcards: Flashcard[];
  currentIndex: number;
  onNext: () => void;
  onPrev: () => void;
  onMarkDifficulty?: (flashcardId: string, difficulty: 'easy' | 'medium' | 'hard') => void;
}

export function Flashcards({ flashcards, currentIndex, onNext, onPrev, onMarkDifficulty }: FlashcardsProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [direction, setDirection] = useState(0);

  const currentCard = flashcards[currentIndex];

  const handleNext = () => {
    setDirection(1);
    setIsFlipped(false);
    onNext();
  };

  const handlePrev = () => {
    setDirection(-1);
    setIsFlipped(false);
    onPrev();
  };

  const handleMarkDifficulty = (difficulty: 'easy' | 'medium' | 'hard') => {
    if (currentCard && onMarkDifficulty) {
      onMarkDifficulty(currentCard.id, difficulty);
    }
    handleNext();
  };

  if (!currentCard) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <p className="text-muted-foreground">No flashcards available for this step.</p>
        </CardContent>
      </Card>
    );
  }

  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 300 : -300,
      opacity: 0,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 300 : -300,
      opacity: 0,
    }),
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-center gap-2">
        {flashcards.map((_, index) => (
          <div
            key={index}
            className={cn(
              'h-2 rounded-full transition-all',
              index === currentIndex ? 'w-8 bg-primary' : 'w-2 bg-muted'
            )}
          />
        ))}
      </div>

      <p className="text-center text-sm text-muted-foreground">
        Card {currentIndex + 1} of {flashcards.length}
      </p>

      {/* Card */}
      <div className="relative h-72 perspective-1000">
        <AnimatePresence initial={false} custom={direction} mode="wait">
          <motion.div
            key={currentCard.id}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="absolute inset-0 cursor-pointer"
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <motion.div
              animate={{ rotateY: isFlipped ? 180 : 0 }}
              transition={{ duration: 0.5, type: 'spring' }}
              style={{ transformStyle: 'preserve-3d' }}
              className="w-full h-full"
            >
              {/* Front */}
              <Card className="absolute inset-0 flex items-center justify-center p-8 backface-hidden border-2 border-primary/20 hover:border-primary/40 transition-colors">
                <CardContent className="text-center">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide mb-4 block">Question</span>
                  <p className="text-xl font-medium leading-relaxed">{currentCard.front}</p>
                </CardContent>
              </Card>

              {/* Back */}
              <Card
                className="absolute inset-0 flex items-center justify-center p-8 backface-hidden bg-gradient-to-br from-primary/5 to-accent/5 border-2 border-primary/30"
                style={{ transform: 'rotateY(180deg)' }}
              >
                <CardContent className="text-center">
                  <span className="text-xs text-primary uppercase tracking-wide mb-4 block">Answer</span>
                  <p className="text-lg leading-relaxed">{currentCard.back}</p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </div>

      <p className="text-center text-sm text-muted-foreground">
        Click card to flip
      </p>

      {/* Navigation */}
      <div className="flex justify-center gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={handlePrev}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsFlipped(false)}
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={handleNext}
          disabled={currentIndex === flashcards.length - 1}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Difficulty Rating (shown when flipped) */}
      {isFlipped && onMarkDifficulty && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center gap-3"
        >
          <p className="text-sm text-muted-foreground mr-2 self-center">How well did you know this?</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleMarkDifficulty('hard')}
            className="text-destructive border-destructive/30 hover:bg-destructive/10"
          >
            <ThumbsDown className="mr-1 h-4 w-4" />
            Hard
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleMarkDifficulty('medium')}
            className="text-warning border-warning/30 hover:bg-warning/10"
          >
            <Minus className="mr-1 h-4 w-4" />
            Okay
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleMarkDifficulty('easy')}
            className="text-success border-success/30 hover:bg-success/10"
          >
            <ThumbsUp className="mr-1 h-4 w-4" />
            Easy
          </Button>
        </motion.div>
      )}
    </div>
  );
}
