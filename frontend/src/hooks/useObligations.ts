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
      const response = await apiClient.get<PaginatedResponse<Obligation>>('api/v1/obligations/', {
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
      const response = await apiClient.get<Obligation>(`api/v1/obligations/${id}/`);
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
      const response = await apiClient.post<Obligation>('api/v1/obligations/', data);
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
      const response = await apiClient.patch<Obligation>(`api/v1/obligations/${id}/`, data);
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
      await apiClient.delete(`api/v1/obligations/${id}/`);
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
      const response = await apiClient.get<ObligationTypeData[]>('api/v1/obligation-types/');
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
      const response = await apiClient.post('api/v1/obligations/bulk_create/', data);
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
      const response = await apiClient.post('api/v1/obligations/bulk_update/', data);
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
      const response = await apiClient.post('api/v1/obligations/bulk_delete/', {
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
  const response = await apiClient.get('api/v1/obligations/export/', {
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
      const response = await apiClient.get<ObligationGroup[]>('api/v1/obligation-types/grouped/');
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
        'api/v1/obligations/generate-month/',
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

// ============================================
// CLIENT OBLIGATION PROFILE HOOKS
// ============================================

export interface ClientWithObligationStatus {
  id: number;
  afm: string;
  eponimia: string;
  is_active: boolean;
  has_obligation_profile: boolean;
  obligation_types_count: number;
  obligation_profile_names: string[];
}

export interface BulkAssignRequest {
  client_ids: number[];
  obligation_type_ids?: number[];
  obligation_profile_ids?: number[];
  mode: 'add' | 'replace';
}

export interface BulkAssignResult {
  success: boolean;
  created_count: number;
  updated_count: number;
  clients_processed: number;
  message: string;
}

/**
 * Get clients with their obligation profile status
 * Useful for showing which clients have configured obligations
 */
export function useClientsWithObligationStatus() {
  return useQuery({
    queryKey: ['clients-obligation-status'],
    queryFn: async () => {
      const response = await apiClient.get<ClientWithObligationStatus[]>(
        'api/v1/clients/obligation-status/'
      );
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Get a specific client's obligation profile
 */
export function useClientObligationProfile(clientId: number) {
  return useQuery({
    queryKey: ['client-obligation-profile', clientId],
    queryFn: async () => {
      const response = await apiClient.get(`api/v1/clients/${clientId}/obligation-profile/`);
      return response.data;
    },
    enabled: !!clientId,
    staleTime: 1000 * 60 * 2,
  });
}

/**
 * Update a client's obligation profile
 */
export function useUpdateClientObligationProfile(clientId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { obligation_type_ids: number[]; obligation_profile_ids: number[] }) => {
      const response = await apiClient.put(`api/v1/clients/${clientId}/obligation-profile/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-obligation-profile', clientId] });
      queryClient.invalidateQueries({ queryKey: ['clients-obligation-status'] });
    },
  });
}

/**
 * Bulk assign obligations to multiple clients
 */
export function useBulkAssignObligations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: BulkAssignRequest) => {
      const response = await apiClient.post<BulkAssignResult>(
        'api/v1/obligations/bulk-assign/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients-obligation-status'] });
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}
