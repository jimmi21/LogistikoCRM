import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

// ============================================
// TYPES
// ============================================

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface UserCreate {
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  password: string;
  password_confirm: string;
  is_staff?: boolean;
  is_active?: boolean;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  password?: string;
  is_staff?: boolean;
  is_active?: boolean;
}

interface UsersResponse {
  success: boolean;
  count: number;
  users: User[];
}

interface UserResponse {
  success: boolean;
  message?: string;
  user: User;
}

// ============================================
// HOOKS
// ============================================

const USERS_KEY = 'users';

/**
 * Get all users (admin only)
 */
export function useUsers() {
  return useQuery<UsersResponse>({
    queryKey: [USERS_KEY],
    queryFn: async () => {
      const response = await apiClient.get<UsersResponse>('/api/v1/users/');
      return response.data;
    },
  });
}

/**
 * Get single user details
 */
export function useUser(userId: number) {
  return useQuery<UserResponse>({
    queryKey: [USERS_KEY, userId],
    queryFn: async () => {
      const response = await apiClient.get<UserResponse>(`/api/v1/users/${userId}/`);
      return response.data;
    },
    enabled: !!userId,
  });
}

/**
 * Create a new user
 */
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation<UserResponse, Error, UserCreate>({
    mutationFn: async (data) => {
      const response = await apiClient.post<UserResponse>('/api/v1/users/create/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_KEY] });
    },
  });
}

/**
 * Update a user
 */
export function useUpdateUser(userId: number) {
  const queryClient = useQueryClient();

  return useMutation<UserResponse, Error, UserUpdate>({
    mutationFn: async (data) => {
      const response = await apiClient.put<UserResponse>(`/api/v1/users/${userId}/update/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_KEY] });
      queryClient.invalidateQueries({ queryKey: [USERS_KEY, userId] });
    },
  });
}

/**
 * Delete a user
 */
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation<{ success: boolean; message: string }, Error, number>({
    mutationFn: async (userId) => {
      const response = await apiClient.delete(`/api/v1/users/${userId}/delete/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_KEY] });
    },
  });
}

/**
 * Toggle user active status
 */
export function useToggleUserActive() {
  const queryClient = useQueryClient();

  return useMutation<UserResponse, Error, number>({
    mutationFn: async (userId) => {
      const response = await apiClient.post<UserResponse>(`/api/v1/users/${userId}/toggle-active/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USERS_KEY] });
    },
  });
}
