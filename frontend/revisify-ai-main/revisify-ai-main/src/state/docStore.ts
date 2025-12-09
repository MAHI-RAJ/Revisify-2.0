import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { docsApi, Document, UploadProgress } from '@/api/docsApi';
import { roadmapApi, Roadmap } from '@/api/roadmapApi';

interface DocState {
  documents: Document[];
  currentDocument: Document | null;
  currentRoadmap: Roadmap | null;
  uploadProgress: UploadProgress | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchDocuments: () => Promise<void>;
  fetchDocument: (docId: string) => Promise<void>;
  uploadDocument: (file: File, onProgress?: (progress: UploadProgress) => void) => Promise<Document>;
  deleteDocument: (docId: string) => Promise<void>;
  renameDocument: (docId: string, title: string) => Promise<void>;
  fetchRoadmap: (docId: string) => Promise<void>;
  pollDocumentStatus: (docId: string) => Promise<Document>;
  setCurrentDocument: (doc: Document | null) => void;
  setUploadProgress: (progress: UploadProgress | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  documents: [],
  currentDocument: null,
  currentRoadmap: null,
  uploadProgress: null,
  isLoading: false,
  error: null,
};

export const useDocStore = create<DocState>()(
  persist(
    (set, get) => ({
      ...initialState,

      fetchDocuments: async () => {
        set({ isLoading: true, error: null });
        try {
          const documents = await docsApi.getDocuments();
          set({ documents, isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to fetch documents.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      fetchDocument: async (docId: string) => {
        set({ isLoading: true, error: null });
        try {
          const document = await docsApi.getDocument(docId);
          set({ currentDocument: document, isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to fetch document.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      uploadDocument: async (file: File, onProgress?: (progress: UploadProgress) => void) => {
        set({ isLoading: true, error: null, uploadProgress: null });
        try {
          const progressHandler = (progress: UploadProgress) => {
            set({ uploadProgress: progress });
            onProgress?.(progress);
          };
          const document = await docsApi.uploadDocument(file, progressHandler);
          const documents = get().documents;
          set({ 
            documents: [document, ...documents], 
            currentDocument: document,
            isLoading: false,
            uploadProgress: null,
          });
          return document;
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to upload document.';
          set({ isLoading: false, error: message, uploadProgress: null });
          throw error;
        }
      },

      deleteDocument: async (docId: string) => {
        try {
          await docsApi.deleteDocument(docId);
          const documents = get().documents.filter(d => d.id !== docId);
          set({ documents });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to delete document.';
          set({ error: message });
          throw error;
        }
      },

      renameDocument: async (docId: string, title: string) => {
        try {
          const updatedDoc = await docsApi.renameDocument(docId, title);
          const documents = get().documents.map(d => 
            d.id === docId ? updatedDoc : d
          );
          set({ documents });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to rename document.';
          set({ error: message });
          throw error;
        }
      },

      fetchRoadmap: async (docId: string) => {
        set({ isLoading: true, error: null });
        try {
          const roadmap = await roadmapApi.getRoadmap(docId);
          set({ currentRoadmap: roadmap, isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.message || 'Failed to fetch roadmap.';
          set({ isLoading: false, error: message });
          throw error;
        }
      },

      pollDocumentStatus: async (docId: string) => {
        const status = await docsApi.getDocumentStatus(docId);
        const currentDoc = get().currentDocument;
        if (currentDoc && currentDoc.id === docId) {
          const updatedDoc = { ...currentDoc, status: status.status as Document['status'], progress: status.progress };
          set({ currentDocument: updatedDoc });
          return updatedDoc;
        }
        return currentDoc as Document;
      },

      setCurrentDocument: (doc) => set({ currentDocument: doc }),
      setUploadProgress: (progress) => set({ uploadProgress: progress }),
      clearError: () => set({ error: null }),
      reset: () => set(initialState),
    }),
    {
      name: 'revisify-docs',
      partialize: (state) => ({
        documents: state.documents,
        currentDocument: state.currentDocument,
      }),
    }
  )
);
