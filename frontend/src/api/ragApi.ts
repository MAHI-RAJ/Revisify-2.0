import apiClient from './client';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: ChatCitation[];
  timestamp: string;
}

export interface ChatCitation {
  id: string;
  text: string;
  pageNumber?: number;
  section?: string;
}

export interface ChatSession {
  id: string;
  documentId: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

export interface DocumentSection {
  id: string;
  title: string;
  pageStart: number;
  pageEnd: number;
}

export const ragApi = {
  sendMessage: async (docId: string, message: string, sessionId?: string) => {
    const response = await apiClient.post<ChatMessage>(`/rag/${docId}/chat`, {
      message,
      sessionId,
    });
    return response.data;
  },

  getChatSessions: async (docId: string) => {
    const response = await apiClient.get<ChatSession[]>(`/rag/${docId}/sessions`);
    return response.data;
  },

  getChatSession: async (docId: string, sessionId: string) => {
    const response = await apiClient.get<ChatSession>(`/rag/${docId}/sessions/${sessionId}`);
    return response.data;
  },

  createChatSession: async (docId: string, title?: string) => {
    const response = await apiClient.post<ChatSession>(`/rag/${docId}/sessions`, { title });
    return response.data;
  },

  deleteChatSession: async (docId: string, sessionId: string) => {
    const response = await apiClient.delete(`/rag/${docId}/sessions/${sessionId}`);
    return response.data;
  },

  getDocumentSections: async (docId: string) => {
    const response = await apiClient.get<DocumentSection[]>(`/rag/${docId}/sections`);
    return response.data;
  },

  searchDocument: async (docId: string, query: string) => {
    const response = await apiClient.post<{ results: ChatCitation[] }>(`/rag/${docId}/search`, { query });
    return response.data;
  },
};
