import { useState } from 'react';
import { MCQ } from '@/api/stepApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CheckCircle, X, ChevronLeft, ChevronRight, Lightbulb } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MCQSetProps {
  mcqs: MCQ[];
  currentIndex: number;
  onAnswer: (mcqId: string, optionId: string) => Promise<{ isCorrect: boolean; explanation: string }>;
  onNext: () => void;
  onPrev: () => void;
  onGetHint: () => void;
  hint?: string | null;
}

export function MCQSet({ mcqs, currentIndex, onAnswer, onNext, onPrev, onGetHint, hint }: MCQSetProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentMCQ = mcqs[currentIndex];

  const handleSubmit = async () => {
    if (!selectedOption || !currentMCQ) return;
    setIsSubmitting(true);
    try {
      const result = await onAnswer(currentMCQ.id, selectedOption);
      setIsCorrect(result.isCorrect);
      setExplanation(result.explanation);
      setShowResult(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    setSelectedOption(null);
    setShowResult(false);
    onNext();
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-success/10 text-success';
      case 'hard': return 'bg-destructive/10 text-destructive';
      default: return 'bg-warning/10 text-warning';
    }
  };

  if (!currentMCQ) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <p className="text-muted-foreground">No MCQs available for this step.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentMCQ.id}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.2 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Question {currentIndex + 1} of {mcqs.length}
              </span>
              <span className={cn('text-xs px-2 py-1 rounded-full capitalize', getDifficultyColor(currentMCQ.difficulty))}>
                {currentMCQ.difficulty}
              </span>
            </div>
            <CardTitle className="text-xl leading-relaxed">{currentMCQ.question}</CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {/* Options */}
            {currentMCQ.options.map((opt, index) => (
              <button
                key={opt.id}
                onClick={() => !showResult && setSelectedOption(opt.id)}
                disabled={showResult}
                className={cn(
                  'w-full p-4 rounded-xl border text-left transition-all flex items-start gap-3',
                  selectedOption === opt.id ? 'border-primary bg-primary/5 shadow-sm' : 'hover:border-muted-foreground/50 hover:bg-muted/50',
                  showResult && opt.isCorrect && 'border-success bg-success/10',
                  showResult && selectedOption === opt.id && !opt.isCorrect && 'border-destructive bg-destructive/10'
                )}
              >
                <span className={cn(
                  'h-7 w-7 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0',
                  selectedOption === opt.id ? 'bg-primary text-primary-foreground' : 'bg-muted'
                )}>
                  {showResult && opt.isCorrect ? (
                    <CheckCircle className="h-4 w-4 text-success" />
                  ) : showResult && selectedOption === opt.id && !opt.isCorrect ? (
                    <X className="h-4 w-4 text-destructive" />
                  ) : (
                    String.fromCharCode(65 + index)
                  )}
                </span>
                <span className="flex-1 pt-0.5">{opt.text}</span>
              </button>
            ))}

            {/* Result */}
            {showResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  'p-4 rounded-xl',
                  isCorrect ? 'bg-success/10 border border-success/20' : 'bg-destructive/10 border border-destructive/20'
                )}
              >
                <p className={cn('font-semibold mb-1', isCorrect ? 'text-success' : 'text-destructive')}>
                  {isCorrect ? '✓ Correct!' : '✗ Incorrect'}
                </p>
                <p className="text-sm text-muted-foreground">{explanation}</p>
              </motion.div>
            )}

            {/* Hint */}
            {hint && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-warning/10 border border-warning/20"
              >
                <p className="text-sm flex items-start gap-2">
                  <Lightbulb className="h-4 w-4 text-warning flex-shrink-0 mt-0.5" />
                  <span>{hint}</span>
                </p>
              </motion.div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                size="icon"
                onClick={onPrev}
                disabled={currentIndex === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              {!showResult ? (
                <>
                  <Button
                    variant="outline"
                    onClick={onGetHint}
                    disabled={!!hint}
                    className="gap-2"
                  >
                    <Lightbulb className="h-4 w-4" />
                    Hint
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={!selectedOption || isSubmitting}
                    className="flex-1 gradient-primary"
                  >
                    {isSubmitting ? 'Checking...' : 'Submit Answer'}
                  </Button>
                </>
              ) : (
                <Button
                  onClick={handleNext}
                  className="flex-1"
                >
                  {currentIndex < mcqs.length - 1 ? 'Next Question' : 'Finish Quiz'}
                </Button>
              )}
              
              <Button
                variant="outline"
                size="icon"
                onClick={() => { setSelectedOption(null); setShowResult(false); onNext(); }}
                disabled={currentIndex === mcqs.length - 1}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}
