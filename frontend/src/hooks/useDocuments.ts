/**
 * useDocuments.ts
 * Hook for document management - list, upload, delete, attach to obligations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  ClientDocument,
  PaginatedResponse,
  DocumentUploadRequest,
  DocumentUploadResult,
} from '../types';

const DOCUMENTS_KEY = 'documents';

interface DocumentFilters {
  client_id?: number;
  obligation_id?: number;
  category?: string;
  year?: number;
  month?: number;
  search?: string;
  page?: number;
  page_size?: number;
}

/**
 * Fetch documents with optional filters
 */
export function useDocuments(filters?: DocumentFilters) {
  return useQuery({
    queryKey: [DOCUMENTS_KEY, filters],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<ClientDocument>>(
        '/api/v1/documents/',
        { params: filters }
      );
      return response.data;
    },
    enabled: true,
  });
}

/**
 * Fetch a single document by ID
 */
export function useDocument(id: number) {
  return useQuery({
    queryKey: [DOCUMENTS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ClientDocument>(`api/v1/documents/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Fetch documents for a specific obligation
 */
export function useObligationDocuments(obligationId: number) {
  return useQuery({
    queryKey: [DOCUMENTS_KEY, 'obligation', obligationId],
    queryFn: async () => {
      const response = await apiClient.get<{
        obligation_id: number;
        client_id: number;
        client_name: string;
        obligation_type: string | null;
        period: string;
        count: number;
        documents: ClientDocument[];
      }>(`/api/v1/obligations/${obligationId}/documents/`);
      return response.data;
    },
    enabled: !!obligationId,
  });
}

/**
 * Upload a new document
 */
export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: DocumentUploadRequest): Promise<DocumentUploadResult> => {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('client_id', String(data.client_id));

      if (data.obligation_id) {
        formData.append('obligation_id', String(data.obligation_id));
      }
      if (data.document_category) {
        formData.append('document_category', data.document_category);
      }
      if (data.description) {
        formData.append('description', data.description);
      }

      const response = await apiClient.post<DocumentUploadResult>(
        '/api/v1/documents/upload/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
    },
  });
}

/**
 * Attach an existing document to an obligation
 */
export function useAttachDocumentToObligation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      obligationId,
      documentId,
    }: {
      obligationId: number;
      documentId: number;
    }) => {
      const response = await apiClient.post(
        `/api/v1/obligations/${obligationId}/attach-document/`,
        { document_id: documentId }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
    },
  });
}

/**
 * Upload and attach a document to an obligation
 */
export function useUploadToObligation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      obligationId,
      file,
      description,
    }: {
      obligationId: number;
      file: File;
      description?: string;
    }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (description) {
        formData.append('description', description);
      }

      const response = await apiClient.post(
        `/api/v1/obligations/${obligationId}/attach-document/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
    },
  });
}

/**
 * Delete a document
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: number) => {
      await apiClient.delete(`api/v1/documents/${documentId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
    },
  });
}

/**
 * Detach a document from an obligation
 */
export function useDetachDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: number) => {
      const response = await apiClient.post(
        `api/v1/documents/${documentId}/detach-from-obligation/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
    },
  });
}

/**
 * Download a document
 */
export async function downloadDocument(clientDoc: ClientDocument): Promise<void> {
  const fileUrl = clientDoc.file_url || clientDoc.file;
  if (!fileUrl) {
    throw new Error('No file URL available');
  }

  // If it's a full URL, open in new tab
  if (fileUrl.startsWith('http')) {
    window.open(fileUrl, '_blank');
    return;
  }

  // Otherwise fetch and download
  const response = await apiClient.get(fileUrl, { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = window.document.createElement('a');
  link.href = url;
  link.setAttribute('download', clientDoc.filename);
  window.document.body?.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ============================================
// VERSIONING SUPPORT
// ============================================

export interface ExistingDocumentInfo {
  exists: boolean;
  document: {
    id: number;
    filename: string;
    original_filename?: string;
    version: number;
    file_size?: number;
    file_size_display?: string;
    category?: string;
    uploaded_at: string;
    uploaded_by?: string | null;
    url?: string | null;
  } | null;
}

export interface UploadWithVersionParams {
  file: File;
  client_id: number;
  obligation_id?: number;
  category?: string;
  year?: number;
  month?: number;
  description?: string;
  version_action: 'replace' | 'new_version' | 'auto';
}

export interface UploadWithVersionResult {
  success: boolean;
  action: 'created' | 'new_version' | 'replaced' | 'exists';
  message: string;
  document?: ClientDocument;
  existing_document?: ExistingDocumentInfo['document'];
  requires_decision?: boolean;
  error?: string;
}

/**
 * Check if a document already exists for given parameters
 */
export async function checkExistingDocument(params: {
  client_id: number;
  obligation_id?: number;
  category?: string;
  year?: number;
  month?: number;
}): Promise<ExistingDocumentInfo> {
  const response = await apiClient.get<ExistingDocumentInfo>(
    '/accounting/api/v1/documents/check-existing/',
    { params }
  );
  return response.data;
}

/**
 * Hook for checking existing document
 */
export function useCheckExistingDocument() {
  return useMutation({
    mutationFn: checkExistingDocument,
  });
}

/**
 * Upload document with versioning support
 */
export function useUploadDocumentWithVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: UploadWithVersionParams): Promise<UploadWithVersionResult> => {
      const formData = new FormData();
      formData.append('file', params.file);
      formData.append('client_id', String(params.client_id));
      formData.append('version_action', params.version_action);

      if (params.obligation_id) {
        formData.append('obligation_id', String(params.obligation_id));
      }
      if (params.category) {
        formData.append('category', params.category);
      }
      if (params.year) {
        formData.append('year', String(params.year));
      }
      if (params.month) {
        formData.append('month', String(params.month));
      }
      if (params.description) {
        formData.append('description', params.description);
      }

      const response = await apiClient.post<UploadWithVersionResult>(
        '/accounting/api/v1/documents/upload-with-version/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOCUMENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligations'] });
    },
  });
}

/**
 * Get document preview info
 */
export async function getDocumentPreview(documentId: number): Promise<{
  id: number;
  filename: string;
  file_type: string;
  preview_type: 'pdf' | 'image' | 'unknown';
  can_preview: boolean;
  url: string | null;
  file_size: number;
  file_size_display: string;
  uploaded_at: string;
  version: number;
  client_name?: string;
}> {
  const response = await apiClient.get(`/accounting/api/v1/documents/${documentId}/preview/`);
  return response.data;
}
