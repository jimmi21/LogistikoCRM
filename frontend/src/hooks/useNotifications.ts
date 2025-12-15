import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';

// Notification types
export interface Notification {
  id: number;
  type: 'overdue' | 'due_today' | 'upcoming';
  priority: 'low' | 'medium' | 'high';
  title: string;
  message: string;
  deadline: string;
  client_id: number;
  client_name: string;
  icon: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  count: number;
  overdue_count: number;
  today_count: number;
}

/**
 * Hook to fetch dashboard notifications
 * Polls every 2 minutes for updates
 */
export function useNotifications() {
  return useQuery<NotificationsResponse>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await apiClient.get('api/notifications/');
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 1000 * 60 * 2, // Poll every 2 minutes
    refetchOnWindowFocus: true,
  });
}

export default useNotifications;
