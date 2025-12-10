import apiClient from './client';

export interface DashboardStats {
  totalDocuments: number;
  completedRoadmaps: number;
  totalStudyTime: number; // in minutes
  averageScore: number;
  streakDays: number;
}

export interface RecentActivity {
  id: string;
  type: 'document_uploaded' | 'step_completed' | 'quiz_taken' | 'chat_session';
  title: string;
  description: string;
  timestamp: string;
  documentId?: string;
  stepId?: string;
}

export interface StudyTimeData {
  date: string;
  minutes: number;
}

export interface AccuracyData {
  date: string;
  accuracy: number;
  questionsAttempted: number;
}

export interface TopicPerformance {
  topic: string;
  accuracy: number;
  questionsAttempted: number;
  averageTime: number;
}

export interface WeakTopic {
  topic: string;
  accuracy: number;
  recommendedSteps: string[];
}

export interface CompletionData {
  label: string;
  value: number;
  total: number;
}

export const dashboardApi = {
  getStats: async () => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },

  getRecentActivity: async (limit: number = 10) => {
    const response = await apiClient.get<RecentActivity[]>('/dashboard/activity', {
      params: { limit },
    });
    return response.data;
  },

  getStudyTimeChart: async (days: number = 7) => {
    const response = await apiClient.get<StudyTimeData[]>('/dashboard/study-time', {
      params: { days },
    });
    return response.data;
  },

  getAccuracyChart: async (days: number = 7) => {
    const response = await apiClient.get<AccuracyData[]>('/dashboard/accuracy', {
      params: { days },
    });
    return response.data;
  },

  getTopicPerformance: async () => {
    const response = await apiClient.get<TopicPerformance[]>('/dashboard/topics');
    return response.data;
  },

  getWeakTopics: async (limit: number = 5) => {
    const response = await apiClient.get<WeakTopic[]>('/dashboard/weak-topics', {
      params: { limit },
    });
    return response.data;
  },

  getCompletionStats: async () => {
    const response = await apiClient.get<CompletionData[]>('/dashboard/completion');
    return response.data;
  },
};
