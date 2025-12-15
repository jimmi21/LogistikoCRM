import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Client, ClientFormData, PaginatedResponse } from '../types';

const CLIENTS_KEY = 'clients';

interface ClientParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export function useClients(params?: ClientParams) {
  return useQuery({
    queryKey: [CLIENTS_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<Client>>('/api/v1/clients/', {
        params,
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useClient(id: number) {
  return useQuery({
    queryKey: [CLIENTS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<Client>(`api/v1/clients/${id}/`);
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ClientFormData) => {
      const response = await apiClient.post<Client>('/api/v1/clients/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTS_KEY] });
    },
  });
}

export function useUpdateClient(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ClientFormData>) => {
      const response = await apiClient.patch<Client>(`api/v1/clients/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTS_KEY] });
    },
  });
}

export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`api/v1/clients/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTS_KEY] });
    },
  });
}
