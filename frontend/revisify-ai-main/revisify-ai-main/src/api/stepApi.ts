import apiClient from './client';

export interface MCQOption {
  id: string;
  text: string;
  isCorrect: boolean;
}

export interface MCQ {
  id: string;
  question: string;
  options: MCQOption[];
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topic: string;
}

export interface Flashcard {
  id: string;
  front: string;
  back: string;
  tags: string[];
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface Note {
  id: string;
  stepId: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface Citation {
  id: string;
  title: string;
  source: string;
  url?: string;
  pageNumber?: number;
  excerpt: string;
  type?: 'document' | 'book' | 'web';
}

export interface StepContent {
  mcqs: MCQ[];
  flashcards: Flashcard[];
  notes: Note | null;
  citations: Citation[];
}

export const stepApi = {
  getStepContent: async (stepId: string) => {
    const response = await apiClient.get<StepContent>(`/step/${stepId}/content`);
    return response.data;
  },

  getMCQs: async (stepId: string) => {
    const response = await apiClient.get<MCQ[]>(`/step/${stepId}/mcqs`);
    return response.data;
  },

  getFlashcards: async (stepId: string) => {
    const response = await apiClient.get<Flashcard[]>(`/step/${stepId}/flashcards`);
    return response.data;
  },

  getNotes: async (stepId: string) => {
    const response = await apiClient.get<Note>(`/step/${stepId}/notes`);
    return response.data;
  },

  saveNotes: async (stepId: string, content: string) => {
    const response = await apiClient.post<Note>(`/step/${stepId}/notes`, { content });
    return response.data;
  },

  getCitations: async (stepId: string) => {
    const response = await apiClient.get<Citation[]>(`/step/${stepId}/citations`);
    return response.data;
  },
};
