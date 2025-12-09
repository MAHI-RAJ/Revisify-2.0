import apiClient from './client';

export interface RoadmapStep {
  id: string;
  order: number;
  title: string;
  description: string;
  estimatedTime: number; // in minutes
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  progress: number;
  mcqCount: number;
  flashcardCount: number;
  icon?: string;
}

export interface Roadmap {
  id: string;
  documentId: string;
  title: string;
  description: string;
  totalSteps: number;
  completedSteps: number;
  estimatedTotalTime: number;
  steps: RoadmapStep[];
  createdAt: string;
  updatedAt: string;
}

export const roadmapApi = {
  getRoadmap: async (docId: string) => {
    const response = await apiClient.get<Roadmap>(`/roadmap/${docId}`);
    return response.data;
  },

  generateRoadmap: async (docId: string) => {
    const response = await apiClient.post<Roadmap>(`/roadmap/generate/${docId}`);
    return response.data;
  },

  getStepDetails: async (stepId: string) => {
    const response = await apiClient.get<RoadmapStep>(`/roadmap/step/${stepId}`);
    return response.data;
  },

  updateStepProgress: async (stepId: string, progress: number) => {
    const response = await apiClient.patch(`/roadmap/step/${stepId}/progress`, { progress });
    return response.data;
  },

  completeStep: async (stepId: string) => {
    const response = await apiClient.post(`/roadmap/step/${stepId}/complete`);
    return response.data;
  },
};
