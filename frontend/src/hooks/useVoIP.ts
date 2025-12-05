import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  VoIPCallFull,
  CallsListResponse,
  CallsStats,
} from '../types';

// ============================================
// QUERY KEYS
// ============================================
const CALLS_KEY = 'calls';
const CALLS_STATS_KEY = 'calls-stats';
const CLIENTS_SEARCH_KEY = 'clients-search';

// ============================================
// TYPES
// ============================================
export interface CallsFilters {
  direction?: 'incoming' | 'outgoing' | 'missed';
  status?: 'active' | 'completed' | 'missed' | 'failed';
  client_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

// ============================================
// HOOKS
// ============================================

/**
 * Fetch calls list with filters and pagination
 */
export function useCalls(filters: CallsFilters = {}) {
  return useQuery({
    queryKey: [CALLS_KEY, filters],
    queryFn: async () => {
      const params: Record<string, string | number | undefined> = {};

      if (filters.direction) params.direction = filters.direction;
      if (filters.status) params.status = filters.status;
      if (filters.client_id) params.client_id = filters.client_id;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.search) params.search = filters.search;
      if (filters.page) params.page = filters.page;
      if (filters.page_size) params.page_size = filters.page_size;

      const response = await apiClient.get<CallsListResponse>('/api/v1/calls/', {
        params,
      });
      return response.data;
    },
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Fetch single call detail
 */
export function useCall(id: number) {
  return useQuery({
    queryKey: [CALLS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<VoIPCallFull>(`/api/v1/calls/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Fetch calls statistics
 */
export function useCallsStats() {
  return useQuery({
    queryKey: [CALLS_STATS_KEY],
    queryFn: async () => {
      const response = await apiClient.get<CallsStats>('/api/v1/calls/stats/');
      return response.data;
    },
    staleTime: 60000, // 1 minute
  });
}

/**
 * Match a call to a client
 */
export function useMatchCallToClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ callId, clientId }: { callId: number; clientId: number }) => {
      const response = await apiClient.post(`/api/v1/calls/${callId}/match_client/`, {
        client_id: clientId,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY] });
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY, variables.callId] });
    },
  });
}

/**
 * Create ticket from a call
 */
export function useCreateTicketFromCall() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      callId,
      title,
      description,
      priority,
    }: {
      callId: number;
      title: string;
      description?: string;
      priority?: 'low' | 'medium' | 'high' | 'urgent';
    }) => {
      const response = await apiClient.post(`/api/v1/calls/${callId}/create_ticket/`, {
        title,
        description,
        priority,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY] });
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY, variables.callId] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
}

/**
 * Update call notes
 */
export function useUpdateCallNotes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ callId, notes }: { callId: number; notes: string }) => {
      const response = await apiClient.patch(`/api/v1/calls/${callId}/`, {
        notes,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY] });
      queryClient.invalidateQueries({ queryKey: [CALLS_KEY, variables.callId] });
    },
  });
}

/**
 * Search clients for matching to a call
 */
export function useSearchClientsForMatch(query: string) {
  return useQuery({
    queryKey: [CLIENTS_SEARCH_KEY, query],
    queryFn: async () => {
      const response = await apiClient.get<Array<{ id: number; eponimia: string; afm: string }>>(
        '/api/v1/clients/search-for-match/',
        { params: { q: query } }
      );
      return response.data;
    },
    enabled: query.length >= 2,
    staleTime: 10000, // 10 seconds
  });
}
