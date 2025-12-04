import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Obligation, ObligationFormData, ObligationStatus, PaginatedResponse } from '../types';

const OBLIGATIONS_KEY = 'obligations';

interface ObligationParams {
  page?: number;
  search?: string;
  status?: ObligationStatus;
  client?: number;
}

export function useObligations(params?: ObligationParams) {
  return useQuery({
    queryKey: [OBLIGATIONS_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<Obligation>>('/obligations/', {
        params,
      });
      return response.data;
    },
  });
}

export function useObligation(id: number) {
  return useQuery({
    queryKey: [OBLIGATIONS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<Obligation>(`/obligations/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateObligation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ObligationFormData) => {
      const response = await apiClient.post<Obligation>('/obligations/', data);
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
      const response = await apiClient.patch<Obligation>(`/obligations/${id}/`, data);
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
      await apiClient.delete(`/obligations/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [OBLIGATIONS_KEY] });
    },
  });
}
