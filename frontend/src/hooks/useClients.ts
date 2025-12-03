import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type { Client, ClientFormData, PaginatedResponse } from '../types';

const CLIENTS_KEY = 'clients';

export function useClients(params?: { page?: number; search?: string }) {
  return useQuery({
    queryKey: [CLIENTS_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedResponse<Client>>('/clients/', {
        params,
      });
      return response.data;
    },
  });
}

export function useClient(id: number) {
  return useQuery({
    queryKey: [CLIENTS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<Client>(`/clients/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ClientFormData) => {
      const response = await apiClient.post<Client>('/clients/', data);
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
      const response = await apiClient.patch<Client>(`/clients/${id}/`, data);
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
      await apiClient.delete(`/clients/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTS_KEY] });
    },
  });
}
