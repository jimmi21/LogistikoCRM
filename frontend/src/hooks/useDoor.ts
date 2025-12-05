import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

const DOOR_KEY = 'door-status';

interface DoorStatusResponse {
  success: boolean;
  status: 'open' | 'closed' | 'error';
  raw_power?: string;
  online: boolean;
  message?: string;
}

interface DoorActionResponse {
  success: boolean;
  message: string;
  new_status?: 'open' | 'closed';
}

export function useDoorStatus() {
  return useQuery({
    queryKey: [DOOR_KEY],
    queryFn: async (): Promise<DoorStatusResponse> => {
      const response = await apiClient.get<DoorStatusResponse>('/api/v1/door/status/');
      return response.data;
    },
    refetchInterval: 30000, // Check every 30 seconds
    retry: false,
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}

export function useOpenDoor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<DoorActionResponse> => {
      const response = await apiClient.post<DoorActionResponse>('/api/v1/door/open/');
      return response.data;
    },
    onSuccess: () => {
      // Invalidate status to refresh
      queryClient.invalidateQueries({ queryKey: [DOOR_KEY] });
    },
  });
}

export function usePulseDoor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (duration: number = 1): Promise<DoorActionResponse> => {
      const response = await apiClient.post<DoorActionResponse>('/api/v1/door/pulse/', {
        duration,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DOOR_KEY] });
    },
  });
}
