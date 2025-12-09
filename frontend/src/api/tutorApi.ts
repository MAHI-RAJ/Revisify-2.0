import apiClient from './client';

export interface Hint {
  id: string;
  content: string;
  type: 'general' | 'specific' | 'example';
  relatedTopic: string;
}

export interface ExplanationRequest {
  stepId: string;
  mcqId?: string;
  topic?: string;
  question?: string;
}

export interface Explanation {
  id: string;
  content: string;
  examples: string[];
  relatedTopics: string[];
}

export const tutorApi = {
  getHint: async (stepId: string, mcqId?: string) => {
    const params = mcqId ? { mcqId } : {};
    const response = await apiClient.get<Hint>(`/tutor/${stepId}/hint`, { params });
    return response.data;
  },

  getExplanation: async (data: ExplanationRequest) => {
    const response = await apiClient.post<Explanation>('/tutor/explain', data);
    return response.data;
  },

  askQuestion: async (stepId: string, question: string) => {
    const response = await apiClient.post<{ answer: string; sources: string[] }>(
      `/tutor/${stepId}/ask`,
      { question }
    );
    return response.data;
  },

  getStudyTips: async (stepId: string) => {
    const response = await apiClient.get<string[]>(`/tutor/${stepId}/tips`);
    return response.data;
  },

  generatePracticeQuestions: async (stepId: string, count: number = 5) => {
    const response = await apiClient.post(`/tutor/${stepId}/practice`, { count });
    return response.data;
  },
};
