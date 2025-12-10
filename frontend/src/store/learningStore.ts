import { create } from 'zustand';
import { stepApi, MCQ, Flashcard, Note, Citation, StepContent } from '@/api/stepApi';
import { attemptApi, MCQAttempt, AttemptResult, ProgressData } from '@/api/attemptApi';
import { tutorApi, Hint } from '@/api/tutorApi';
import { RoadmapStep } from '@/api/roadmapApi';

interface LearningState {
  currentStep: RoadmapStep | null;
  stepContent: StepContent | null;
  mcqs: MCQ[];
  flashcards: Flashcard[];
  notes: Note | null;
  citations: Citation[];
  hints: Hint[];
  hintsUsed: number;
  currentMCQIndex: number;
  currentFlashcardIndex: number;
  mcqAttempts: MCQAttempt[];
  lastAttemptResult: AttemptResult | null;
  progress: ProgressData | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentStep: (step: RoadmapStep) => void;
  fetchStepContent: (stepId: string) => Promise<void>;
  fetchMCQs: (stepId: string) => Promise<void>;
  fetchFlashcards: (stepId: string) => Promise<void>;
  fetchNotes: (stepId: string) => Promise<void>;
  saveNotes: (stepId: string, content: string) => Promise<void>;
  fetchCitations: (stepId: string) => Promise<void>;
  fetchHint: (stepId: string, mcqId?: string) => Promise<Hint>;
  submitMCQAnswer: (stepId: string, mcqId: string, optionId: string, timeSpent: number) => Promise<{ isCorrect: boolean; explanation: string }>;
  submitAllMCQs: (stepId: string) => Promise<AttemptResult>;
  markFlashcardReviewed: (stepId: string, flashcardId: string, difficulty: 'easy' | 'medium' | 'hard') => Promise<void>;
  fetchProgress: (stepId: string) => Promise<void>;
  nextMCQ: () => void;
  prevMCQ: () => void;
  nextFlashcard: () => void;
  prevFlashcard: () => void;
  recordMCQAttempt: (attempt: MCQAttempt) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  currentStep: null,
  stepContent: null,
  mcqs: [],
  flashcards: [],
  notes: null,
  citations: [],
  hints: [],
  hintsUsed: 0,
  currentMCQIndex: 0,
  currentFlashcardIndex: 0,
  mcqAttempts: [],
  lastAttemptResult: null,
  progress: null,
  isLoading: false,
  error: null,
};

export const useLearningStore = create<LearningState>()((set, get) => ({
  ...initialState,

  setCurrentStep: (step) => set({ currentStep: step }),

  fetchStepContent: async (stepId: string) => {
    set({ isLoading: true, error: null });
    try {
      const content = await stepApi.getStepContent(stepId);
      set({
        stepContent: content,
        mcqs: content.mcqs,
        flashcards: content.flashcards,
        notes: content.notes,
        citations: content.citations,
        isLoading: false,
        currentMCQIndex: 0,
        currentFlashcardIndex: 0,
        mcqAttempts: [],
      });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch step content.';
      set({ isLoading: false, error: message });
      throw error;
    }
  },

  fetchMCQs: async (stepId: string) => {
    set({ isLoading: true, error: null });
    try {
      const mcqs = await stepApi.getMCQs(stepId);
      set({ mcqs, isLoading: false, currentMCQIndex: 0, mcqAttempts: [] });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch MCQs.';
      set({ isLoading: false, error: message });
      throw error;
    }
  },

  fetchFlashcards: async (stepId: string) => {
    set({ isLoading: true, error: null });
    try {
      const flashcards = await stepApi.getFlashcards(stepId);
      set({ flashcards, isLoading: false, currentFlashcardIndex: 0 });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch flashcards.';
      set({ isLoading: false, error: message });
      throw error;
    }
  },

  fetchNotes: async (stepId: string) => {
    try {
      const notes = await stepApi.getNotes(stepId);
      set({ notes });
    } catch (error: any) {
      // Notes might not exist yet, that's okay
      set({ notes: null });
    }
  },

  saveNotes: async (stepId: string, content: string) => {
    try {
      const notes = await stepApi.saveNotes(stepId, content);
      set({ notes });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to save notes.';
      set({ error: message });
      throw error;
    }
  },

  fetchCitations: async (stepId: string) => {
    try {
      const citations = await stepApi.getCitations(stepId);
      set({ citations });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch citations.';
      set({ error: message });
    }
  },

  fetchHint: async (stepId: string, mcqId?: string) => {
    set({ isLoading: true });
    try {
      const hint = await tutorApi.getHint(stepId, mcqId);
      const hints = [...get().hints, hint];
      set({ hints, hintsUsed: get().hintsUsed + 1, isLoading: false });
      return hint;
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch hint.';
      set({ isLoading: false, error: message });
      throw error;
    }
  },

  submitMCQAnswer: async (stepId: string, mcqId: string, optionId: string, timeSpent: number) => {
    try {
      const result = await attemptApi.submitSingleMCQ(stepId, mcqId, optionId, timeSpent);
      const attempt: MCQAttempt = {
        mcqId,
        selectedOptionId: optionId,
        isCorrect: result.isCorrect,
        timeSpent,
      };
      set({ mcqAttempts: [...get().mcqAttempts, attempt] });
      return result;
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to submit answer.';
      set({ error: message });
      throw error;
    }
  },

  submitAllMCQs: async (stepId: string) => {
    try {
      const result = await attemptApi.submitMCQAttempt(stepId, get().mcqAttempts);
      set({ lastAttemptResult: result });
      return result;
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to submit quiz.';
      set({ error: message });
      throw error;
    }
  },

  markFlashcardReviewed: async (stepId: string, flashcardId: string, difficulty: 'easy' | 'medium' | 'hard') => {
    try {
      await attemptApi.markFlashcardReviewed(stepId, flashcardId, difficulty);
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to mark flashcard.';
      set({ error: message });
    }
  },

  fetchProgress: async (stepId: string) => {
    try {
      const progress = await attemptApi.getProgress(stepId);
      set({ progress });
    } catch (error: any) {
      // Progress might not exist yet
    }
  },

  nextMCQ: () => {
    const { currentMCQIndex, mcqs } = get();
    if (currentMCQIndex < mcqs.length - 1) {
      set({ currentMCQIndex: currentMCQIndex + 1 });
    }
  },

  prevMCQ: () => {
    const { currentMCQIndex } = get();
    if (currentMCQIndex > 0) {
      set({ currentMCQIndex: currentMCQIndex - 1 });
    }
  },

  nextFlashcard: () => {
    const { currentFlashcardIndex, flashcards } = get();
    if (currentFlashcardIndex < flashcards.length - 1) {
      set({ currentFlashcardIndex: currentFlashcardIndex + 1 });
    }
  },

  prevFlashcard: () => {
    const { currentFlashcardIndex } = get();
    if (currentFlashcardIndex > 0) {
      set({ currentFlashcardIndex: currentFlashcardIndex - 1 });
    }
  },

  recordMCQAttempt: (attempt) => {
    set({ mcqAttempts: [...get().mcqAttempts, attempt] });
  },

  clearError: () => set({ error: null }),
  reset: () => set(initialState),
}));
