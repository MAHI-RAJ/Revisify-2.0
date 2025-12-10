import { create } from 'zustand';
import { 
  dashboardApi, 
  DashboardStats, 
  RecentActivity, 
  StudyTimeData, 
  AccuracyData, 
  TopicPerformance, 
  WeakTopic,
  CompletionData 
} from '@/api/dashboardApi';

interface DashboardState {
  stats: DashboardStats | null;
  recentActivity: RecentActivity[];
  studyTimeData: StudyTimeData[];
  accuracyData: AccuracyData[];
  topicPerformance: TopicPerformance[];
  weakTopics: WeakTopic[];
  completionData: CompletionData[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchStats: () => Promise<void>;
  fetchRecentActivity: (limit?: number) => Promise<void>;
  fetchStudyTimeChart: (days?: number) => Promise<void>;
  fetchAccuracyChart: (days?: number) => Promise<void>;
  fetchTopicPerformance: () => Promise<void>;
  fetchWeakTopics: (limit?: number) => Promise<void>;
  fetchCompletionStats: () => Promise<void>;
  fetchAllDashboardData: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  stats: null,
  recentActivity: [],
  studyTimeData: [],
  accuracyData: [],
  topicPerformance: [],
  weakTopics: [],
  completionData: [],
  isLoading: false,
  error: null,
};

export const useDashboardStore = create<DashboardState>()((set) => ({
  ...initialState,

  fetchStats: async () => {
    try {
      const stats = await dashboardApi.getStats();
      set({ stats });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch stats.';
      set({ error: message });
    }
  },

  fetchRecentActivity: async (limit = 10) => {
    try {
      const recentActivity = await dashboardApi.getRecentActivity(limit);
      set({ recentActivity });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch activity.';
      set({ error: message });
    }
  },

  fetchStudyTimeChart: async (days = 7) => {
    try {
      const studyTimeData = await dashboardApi.getStudyTimeChart(days);
      set({ studyTimeData });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch study time data.';
      set({ error: message });
    }
  },

  fetchAccuracyChart: async (days = 7) => {
    try {
      const accuracyData = await dashboardApi.getAccuracyChart(days);
      set({ accuracyData });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch accuracy data.';
      set({ error: message });
    }
  },

  fetchTopicPerformance: async () => {
    try {
      const topicPerformance = await dashboardApi.getTopicPerformance();
      set({ topicPerformance });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch topic performance.';
      set({ error: message });
    }
  },

  fetchWeakTopics: async (limit = 5) => {
    try {
      const weakTopics = await dashboardApi.getWeakTopics(limit);
      set({ weakTopics });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch weak topics.';
      set({ error: message });
    }
  },

  fetchCompletionStats: async () => {
    try {
      const completionData = await dashboardApi.getCompletionStats();
      set({ completionData });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch completion stats.';
      set({ error: message });
    }
  },

  fetchAllDashboardData: async () => {
    set({ isLoading: true, error: null });
    try {
      const [stats, recentActivity, studyTimeData, accuracyData, topicPerformance, weakTopics, completionData] = 
        await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getRecentActivity(10),
          dashboardApi.getStudyTimeChart(7),
          dashboardApi.getAccuracyChart(7),
          dashboardApi.getTopicPerformance(),
          dashboardApi.getWeakTopics(5),
          dashboardApi.getCompletionStats(),
        ]);
      set({
        stats,
        recentActivity,
        studyTimeData,
        accuracyData,
        topicPerformance,
        weakTopics,
        completionData,
        isLoading: false,
      });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to fetch dashboard data.';
      set({ isLoading: false, error: message });
    }
  },

  clearError: () => set({ error: null }),
  reset: () => set(initialState),
}));
