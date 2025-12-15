import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  TicketFull,
  TicketsListResponse,
  TicketsStats,
} from '../types';

// ============================================
// QUERY KEYS
// ============================================
const TICKETS_KEY = 'tickets';
const TICKETS_STATS_KEY = 'tickets-stats';

// ============================================
// TYPES
// ============================================
export interface TicketsFilters {
  status?: 'open' | 'assigned' | 'in_progress' | 'resolved' | 'closed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  client_id?: number;
  assigned_to?: number;
  open_only?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface CreateTicketData {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  client?: number | null;  // For create, backend uses 'client'
  call?: number;
  notes?: string;
}

export interface UpdateTicketData {
  title?: string;
  description?: string;
  status?: 'open' | 'assigned' | 'in_progress' | 'resolved' | 'closed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  notes?: string;
  client_id?: number | null;
  assigned_to?: number | null;
}

// ============================================
// HOOKS
// ============================================

/**
 * Fetch tickets list with filters and pagination
 */
export function useTickets(filters: TicketsFilters = {}) {
  return useQuery({
    queryKey: [TICKETS_KEY, filters],
    queryFn: async () => {
      const params: Record<string, string | number | boolean | undefined> = {};

      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.client_id) params.client_id = filters.client_id;
      if (filters.assigned_to) params.assigned_to = filters.assigned_to;
      if (filters.open_only) params.open_only = 'true';
      if (filters.search) params.search = filters.search;
      if (filters.page) params.page = filters.page;
      if (filters.page_size) params.page_size = filters.page_size;

      const response = await apiClient.get<TicketsListResponse>('api/v1/tickets/', {
        params,
      });
      return response.data;
    },
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Fetch single ticket detail
 */
export function useTicket(id: number) {
  return useQuery({
    queryKey: [TICKETS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<TicketFull>(`api/v1/tickets/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Fetch tickets statistics
 */
export function useTicketsStats() {
  return useQuery({
    queryKey: [TICKETS_STATS_KEY],
    queryFn: async () => {
      const response = await apiClient.get<TicketsStats>('api/v1/tickets/stats/');
      return response.data;
    },
    staleTime: 60000, // 1 minute
  });
}

/**
 * Create a new ticket
 */
export function useCreateTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateTicketData) => {
      const response = await apiClient.post('api/v1/tickets/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_STATS_KEY] });
    },
  });
}

/**
 * Update a ticket
 */
export function useUpdateTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdateTicketData }) => {
      const response = await apiClient.patch(`api/v1/tickets/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY, variables.id] });
    },
  });
}

/**
 * Delete a ticket
 */
export function useDeleteTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.delete(`api/v1/tickets/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_STATS_KEY] });
    },
  });
}

/**
 * Change ticket status
 */
export function useChangeTicketStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      status,
    }: {
      id: number;
      status: 'open' | 'assigned' | 'in_progress' | 'resolved' | 'closed';
    }) => {
      const response = await apiClient.post(`api/v1/tickets/${id}/change_status/`, {
        status,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_STATS_KEY] });
    },
  });
}

/**
 * Assign ticket to a user
 */
export function useAssignTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, userId }: { id: number; userId?: number }) => {
      const response = await apiClient.post(`api/v1/tickets/${id}/assign/`, {
        user_id: userId,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY] });
      queryClient.invalidateQueries({ queryKey: [TICKETS_KEY, variables.id] });
    },
  });
}
