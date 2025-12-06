import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  Obligation,
  ObligationFormData,
  ObligationStatus,
  PaginatedResponse,
  ObligationTypeData,
  BulkObligationFormData,
  BulkUpdateFormData,
  ObligationGroup,
  ObligationProfileBundle,
  GenerateMonthRequest,
  GenerateMonthResult,
} from '../types';

const OBLIGATIONS_KEY = 'obligations';
const OBLIGATION_TYPES_KEY = 'obligation-types';

interface ObligationParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ObligationStatus;
  client?: number;
  type?: string;
  month?: number;
  year?: number;
  deadline_from?: string;
  deadline_to?: string;
}

export function useObligations(params?: ObligationParams) {
  return useQuery({
    queryKey: [OBLIGATIONS_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<Obligation>>('/api/v1/obligations/', {
        params,
      });
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - shorter for frequently changing data
  });
}

export function useObligation(id: number) {
  return useQuery({
    queryKey: [OBLIGATIONS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<Obligation>(`/api/v1/obligations/${id}/`);
      return response.data;
    },
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useCreateObligation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ObligationFormData) => {
      const response = await apiClient.post<Obligation>('/api/v1/obligations/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

export function useUpdateObligation(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ObligationFormData>) => {
      const response = await apiClient.patch<Obligation>(`/api/v1/obligations/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

export function useDeleteObligation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/v1/obligations/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

// ============================================
// OBLIGATION TYPES HOOKS
// ============================================

export function useObligationTypes() {
  return useQuery({
    queryKey: [OBLIGATION_TYPES_KEY],
    queryFn: async () => {
      const response = await apiClient.get<ObligationTypeData[]>('/api/v1/obligation-types/');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

// ============================================
// BULK OPERATIONS HOOKS
// ============================================

export function useBulkCreateObligations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: BulkObligationFormData) => {
      const response = await apiClient.post('/api/v1/obligations/bulk_create/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

export function useBulkUpdateObligations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: BulkUpdateFormData) => {
      const response = await apiClient.post('/api/v1/obligations/bulk_update/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

export function useBulkDeleteObligations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (obligationIds: number[]) => {
      const response = await apiClient.post('/api/v1/obligations/bulk_delete/', {
        obligation_ids: obligationIds,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}

// ============================================
// EXPORT FUNCTION
// ============================================

export async function exportObligationsToExcel(params?: ObligationParams): Promise<void> {
  const response = await apiClient.get('/api/v1/obligations/export/', {
    params,
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;

  // Get filename from Content-Disposition header or use default
  const contentDisposition = response.headers['content-disposition'];
  let filename = `υποχρεώσεις_${new Date().toISOString().slice(0, 10)}.xlsx`;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?(.+)"?/);
    if (match) {
      filename = match[1];
    }
  }

  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ============================================
// OBLIGATION PROFILE HOOKS
// ============================================

/**
 * Get obligation types grouped by category
 */
export function useObligationTypesGrouped() {
  return useQuery({
    queryKey: ['obligation-types-grouped'],
    queryFn: async () => {
      // Note: apiClient baseURL already includes /accounting, so don't prefix it again
      const response = await apiClient.get<ObligationGroup[]>('/api/v1/obligation-types/grouped/');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

/**
 * Get reusable obligation profiles
 */
export function useObligationProfiles() {
  return useQuery({
    queryKey: ['obligation-profiles'],
    queryFn: async () => {
      // Note: apiClient baseURL already includes /accounting, so don't prefix it again
      const response = await apiClient.get<ObligationProfileBundle[]>('/api/v1/obligation-profiles/');
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

/**
 * Generate monthly obligations based on client profiles
 */
export function useGenerateMonthlyObligations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GenerateMonthRequest) => {
      // Note: apiClient baseURL already includes /accounting, so don't prefix it again
      const response = await apiClient.post<GenerateMonthResult>(
        '/api/v1/obligations/generate-month/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      // Invalidate obligations list to refresh
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}
