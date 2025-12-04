import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  ClientFull,
  ClientDocument,
  Obligation,
  EmailLog,
  VoIPCall,
  VoIPTicket,
} from '../types';

// ============================================
// QUERY KEYS
// ============================================
const CLIENT_DETAILS_KEY = 'client-details';
const CLIENT_DOCUMENTS_KEY = 'client-documents';
const CLIENT_OBLIGATIONS_KEY = 'client-obligations';
const CLIENT_EMAILS_KEY = 'client-emails';
const CLIENT_CALLS_KEY = 'client-calls';
const CLIENT_TICKETS_KEY = 'client-tickets';

// ============================================
// API RESPONSE TYPES
// ============================================
interface ClientDocumentsResponse {
  client_id: number;
  client_name: string;
  total_count: number;
  documents: ClientDocument[];
}

interface ClientObligationsResponse {
  client_id: number;
  client_name: string;
  total_count: number;
  obligations: Obligation[];
}

interface ClientEmailsResponse {
  client_id: number;
  client_name: string;
  total_count: number;
  page: number;
  page_size: number;
  emails: EmailLog[];
}

interface ClientCallsResponse {
  client_id: number;
  client_name: string;
  total_count: number;
  page: number;
  page_size: number;
  calls: VoIPCall[];
}

interface ClientTicketsResponse {
  client_id: number;
  client_name: string;
  total_count: number;
  tickets: VoIPTicket[];
}

// ============================================
// HOOKS
// ============================================

/**
 * Get full client details with counts
 */
export function useClientFull(id: number) {
  return useQuery({
    queryKey: [CLIENT_DETAILS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ClientFull>(`/api/v1/clients/${id}/full/`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Get client documents
 */
export function useClientDocuments(id: number, category?: string) {
  return useQuery({
    queryKey: [CLIENT_DOCUMENTS_KEY, id, category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const response = await apiClient.get<ClientDocumentsResponse>(
        `/api/v1/clients/${id}/documents/`,
        { params }
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Get client obligations
 */
export function useClientObligations(
  id: number,
  filters?: { status?: string; year?: number; month?: number }
) {
  return useQuery({
    queryKey: [CLIENT_OBLIGATIONS_KEY, id, filters],
    queryFn: async () => {
      const response = await apiClient.get<ClientObligationsResponse>(
        `/api/v1/clients/${id}/obligations/`,
        { params: filters }
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Get client email history
 */
export function useClientEmails(id: number, page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: [CLIENT_EMAILS_KEY, id, page, pageSize],
    queryFn: async () => {
      const response = await apiClient.get<ClientEmailsResponse>(
        `/api/v1/clients/${id}/emails/`,
        { params: { page, page_size: pageSize } }
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Get client call history
 */
export function useClientCalls(id: number, page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: [CLIENT_CALLS_KEY, id, page, pageSize],
    queryFn: async () => {
      const response = await apiClient.get<ClientCallsResponse>(
        `/api/v1/clients/${id}/calls/`,
        { params: { page, page_size: pageSize } }
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Get client tickets
 */
export function useClientTickets(id: number, status?: string) {
  return useQuery({
    queryKey: [CLIENT_TICKETS_KEY, id, status],
    queryFn: async () => {
      const params = status ? { status } : {};
      const response = await apiClient.get<ClientTicketsResponse>(
        `/api/v1/clients/${id}/tickets/`,
        { params }
      );
      return response.data;
    },
    enabled: !!id,
  });
}

// ============================================
// MUTATIONS
// ============================================

/**
 * Upload document for client
 */
export function useUploadDocument(clientId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      file,
      category,
      description,
      obligationId,
    }: {
      file: File;
      category?: string;
      description?: string;
      obligationId?: number;
    }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (category) formData.append('category', category);
      if (description) formData.append('description', description);
      if (obligationId) formData.append('obligation_id', String(obligationId));

      const response = await apiClient.post(
        `/api/v1/clients/${clientId}/documents/upload/`,
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
      queryClient.invalidateQueries({ queryKey: [CLIENT_DOCUMENTS_KEY, clientId] });
      queryClient.invalidateQueries({ queryKey: [CLIENT_DETAILS_KEY, clientId] });
    },
  });
}

/**
 * Delete document
 */
export function useDeleteDocument(clientId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: number) => {
      const response = await apiClient.delete(
        `/api/v1/clients/${clientId}/documents/${documentId}/delete/`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENT_DOCUMENTS_KEY, clientId] });
      queryClient.invalidateQueries({ queryKey: [CLIENT_DETAILS_KEY, clientId] });
    },
  });
}

/**
 * Create ticket for client
 */
export function useCreateTicket(clientId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      title,
      description,
      priority,
    }: {
      title: string;
      description?: string;
      priority?: 'low' | 'medium' | 'high' | 'urgent';
    }) => {
      const response = await apiClient.post(`/api/v1/clients/${clientId}/tickets/`, {
        title,
        description,
        priority,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENT_TICKETS_KEY, clientId] });
      queryClient.invalidateQueries({ queryKey: [CLIENT_DETAILS_KEY, clientId] });
    },
  });
}

/**
 * Update client data
 */
export function useUpdateClientFull(clientId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ClientFull>) => {
      const response = await apiClient.patch(`/api/v1/clients/${clientId}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENT_DETAILS_KEY, clientId] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}
