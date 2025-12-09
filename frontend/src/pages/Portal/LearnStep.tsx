import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useLearningStore } from '@/state/learningStore';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader } from '@/components/Loader';
import { toast } from '@/components/Toast';
import { MCQSet } from '@/components/MCQSet';
import { Flashcards } from '@/components/Flashcards';
import { NotesPanel } from '@/components/NotesPanel';
import { CitationsPanel } from '@/components/CitationsPanel';
import { StepHeader } from '@/components/StepHeader';
import { BookOpen, Brain, FileText, Link2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LearnStep() {
  const { stepId } = useParams<{ stepId: string }>();
  const [searchParams] = useSearchParams();
  const docId = searchParams.get('docId') || '';
  
  const {
    mcqs,
    flashcards,
    notes,
    citations,
    currentMCQIndex,
    currentFlashcardIndex,
    currentStep,
    progress,
    fetchStepContent,
    saveNotes,
    fetchHint,
    submitMCQAnswer,
    nextMCQ,
    prevMCQ,
    nextFlashcard,
    prevFlashcard,
    markFlashcardReviewed,
    isLoading,
    error,
  } = useLearningStore();

  const [hint, setHint] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('mcq');

  useEffect(() => {
    if (stepId) {
      fetchStepContent(stepId);
    }
  }, [stepId, fetchStepContent]);

  useEffect(() => {
    setHint(null);
  }, [currentMCQIndex]);

  const handleSubmitAnswer = async (mcqId: string, optionId: string) => {
    if (!stepId) throw new Error('No step ID');
    try {
      const result = await submitMCQAnswer(stepId, mcqId, optionId, 0);
      return result;
    } catch (err) {
      toast({ type: 'error', title: 'Failed to submit answer' });
      throw err;
    }
  };

  const handleGetHint = async () => {
    if (!stepId) return;
    try {
      const h = await fetchHint(stepId, mcqs[currentMCQIndex]?.id);
      setHint(h.content);
    } catch (err) {
      toast({ type: 'error', title: 'Failed to get hint' });
    }
  };

  const handleSaveNotes = async (content: string) => {
    if (!stepId) return;
    try {
      await saveNotes(stepId, content);
      toast({ type: 'success', title: 'Notes saved!' });
    } catch (err) {
      toast({ type: 'error', title: 'Failed to save notes' });
      throw err;
    }
  };

  const handleMarkFlashcard = async (flashcardId: string, difficulty: 'easy' | 'medium' | 'hard') => {
    if (!stepId) return;
    try {
      await markFlashcardReviewed(stepId, flashcardId, difficulty);
    } catch (err) {
      // Silent fail for flashcard marking
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader size="lg" text="Loading content..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center text-destructive">
        {error}
      </div>
    );
  }

  // Create a mock step for header if not available
  const stepInfo = currentStep || {
    id: stepId || '',
    order: 1,
    title: 'Learning Step',
    description: '',
    status: 'in_progress' as const,
    estimatedTime: 15,
    mcqCount: mcqs.length,
    flashcardCount: flashcards.length,
    progress: 0,
  };

  return (
    <div className="min-h-screen pb-8">
      {/* Header */}
      <StepHeader
        step={stepInfo}
        docId={docId}
        progress={progress?.overallProgress}
        score={progress?.mcqScore}
      />

      {/* Content */}
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 h-12">
              <TabsTrigger value="mcq" className="gap-2">
                <Brain className="h-4 w-4" />
                <span className="hidden sm:inline">MCQs</span>
                <span className="text-xs text-muted-foreground">({mcqs.length})</span>
              </TabsTrigger>
              <TabsTrigger value="flashcards" className="gap-2">
                <BookOpen className="h-4 w-4" />
                <span className="hidden sm:inline">Cards</span>
                <span className="text-xs text-muted-foreground">({flashcards.length})</span>
              </TabsTrigger>
              <TabsTrigger value="notes" className="gap-2">
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Notes</span>
              </TabsTrigger>
              <TabsTrigger value="citations" className="gap-2">
                <Link2 className="h-4 w-4" />
                <span className="hidden sm:inline">Sources</span>
                <span className="text-xs text-muted-foreground">({citations.length})</span>
              </TabsTrigger>
            </TabsList>

            {/* MCQ Tab */}
            <TabsContent value="mcq">
              <MCQSet
                mcqs={mcqs}
                currentIndex={currentMCQIndex}
                onAnswer={handleSubmitAnswer}
                onNext={nextMCQ}
                onPrev={prevMCQ}
                onGetHint={handleGetHint}
                hint={hint}
              />
            </TabsContent>

            {/* Flashcards Tab */}
            <TabsContent value="flashcards">
              <Flashcards
                flashcards={flashcards}
                currentIndex={currentFlashcardIndex}
                onNext={nextFlashcard}
                onPrev={prevFlashcard}
                onMarkDifficulty={handleMarkFlashcard}
              />
            </TabsContent>

            {/* Notes Tab */}
            <TabsContent value="notes">
              <NotesPanel
                initialContent={notes?.content || ''}
                onSave={handleSaveNotes}
              />
            </TabsContent>

            {/* Citations Tab */}
            <TabsContent value="citations">
              <CitationsPanel citations={citations} />
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}
