import apiClient from './client';

export interface Document {
  id: string;
  title: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  status: 'uploading' | 'processing' | 'ready' | 'failed';
  progress: number;
  createdAt: string;
  updatedAt: string;
  roadmapId?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export const docsApi = {
  uploadDocument: async (
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    });
    return response.data;
  },

  getDocuments: async () => {
    const response = await apiClient.get<Document[]>('/documents');
    return response.data;
  },

  getDocument: async (docId: string) => {
    const response = await apiClient.get<Document>(`/documents/${docId}`);
    return response.data;
  },

  getDocumentStatus: async (docId: string) => {
    const response = await apiClient.get<{ status: string; progress: number }>(`/documents/${docId}/status`);
    return response.data;
  },

  deleteDocument: async (docId: string) => {
    const response = await apiClient.delete(`/documents/${docId}`);
    return response.data;
  },

  renameDocument: async (docId: string, title: string) => {
    const response = await apiClient.patch<Document>(`/documents/${docId}`, { title });
    return response.data;
  },
};
