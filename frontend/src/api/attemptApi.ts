import apiClient from './client';

export interface MCQAttempt {
  mcqId: string;
  selectedOptionId: string;
  isCorrect: boolean;
  timeSpent: number; // in seconds
}

export interface AttemptResult {
  id: string;
  stepId: string;
  totalQuestions: number;
  correctAnswers: number;
  score: number;
  timeSpent: number;
  attempts: MCQAttempt[];
  createdAt: string;
}

export interface ProgressData {
  stepId: string;
  mcqProgress: number;
  mcqScore: number;
  flashcardProgress: number;
  overallProgress: number;
  hintsUsed: number;
  lastAttemptAt: string;
}

export const attemptApi = {
  submitMCQAttempt: async (stepId: string, attempts: MCQAttempt[]) => {
    const response = await apiClient.post<AttemptResult>(`/attempt/${stepId}/mcq`, { attempts });
    return response.data;
  },

  submitSingleMCQ: async (stepId: string, mcqId: string, selectedOptionId: string, timeSpent: number) => {
    const response = await apiClient.post<{ isCorrect: boolean; explanation: string }>(
      `/attempt/${stepId}/mcq/${mcqId}`,
      { selectedOptionId, timeSpent }
    );
    return response.data;
  },

  getAttemptHistory: async (stepId: string) => {
    const response = await apiClient.get<AttemptResult[]>(`/attempt/${stepId}/history`);
    return response.data;
  },

  getProgress: async (stepId: string) => {
    const response = await apiClient.get<ProgressData>(`/attempt/${stepId}/progress`);
    return response.data;
  },

  markFlashcardReviewed: async (stepId: string, flashcardId: string, difficulty: 'easy' | 'medium' | 'hard') => {
    const response = await apiClient.post(`/attempt/${stepId}/flashcard/${flashcardId}`, { difficulty });
    return response.data;
  },
};
