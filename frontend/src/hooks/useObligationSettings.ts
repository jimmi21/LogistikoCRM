import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import type {
  ObligationTypeFull,
  ObligationTypeFormData,
  ObligationProfileFull,
  ObligationProfileFormData,
  ObligationGroupFull,
  ObligationGroupFormData,
} from '../types';

// Query keys
const SETTINGS_TYPES_KEY = 'settings-obligation-types';
const SETTINGS_PROFILES_KEY = 'settings-obligation-profiles';
const SETTINGS_GROUPS_KEY = 'settings-obligation-groups';

// Base URL for settings API
const SETTINGS_BASE = '/accounting/api/v1/settings';

// ============================================
// OBLIGATION TYPES HOOKS
// ============================================

interface ObligationTypeParams {
  is_active?: boolean;
  frequency?: string;
  profile?: number;
  exclusion_group?: number;
  search?: string;
}

/**
 * Get all obligation types for settings management
 */
export function useObligationTypesList(params?: ObligationTypeParams) {
  return useQuery({
    queryKey: [SETTINGS_TYPES_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<ObligationTypeFull[]>(
        `${SETTINGS_BASE}/obligation-types/`,
        { params }
      );
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Get a single obligation type
 */
export function useObligationType(id: number) {
  return useQuery({
    queryKey: [SETTINGS_TYPES_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ObligationTypeFull>(
        `${SETTINGS_BASE}/obligation-types/${id}/`
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Create a new obligation type
 */
export function useCreateObligationType() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ObligationTypeFormData) => {
      const response = await apiClient.post<ObligationTypeFull>(
        `${SETTINGS_BASE}/obligation-types/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
      // Also invalidate the grouped types used in client profile
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types'] });
    },
  });
}

/**
 * Update an existing obligation type
 */
export function useUpdateObligationType() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ObligationTypeFormData> }) => {
      const response = await apiClient.put<ObligationTypeFull>(
        `${SETTINGS_BASE}/obligation-types/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types'] });
    },
  });
}

/**
 * Delete an obligation type (soft delete by default)
 */
export function useDeleteObligationType() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, force = false }: { id: number; force?: boolean }) => {
      await apiClient.delete(`${SETTINGS_BASE}/obligation-types/${id}/`, {
        params: { force },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types'] });
    },
  });
}

// ============================================
// OBLIGATION PROFILES HOOKS
// ============================================

interface ObligationProfileParams {
  search?: string;
}

/**
 * Get all obligation profiles for settings management
 */
export function useObligationProfilesList(params?: ObligationProfileParams) {
  return useQuery({
    queryKey: [SETTINGS_PROFILES_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<ObligationProfileFull[]>(
        `${SETTINGS_BASE}/obligation-profiles/`,
        { params }
      );
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Get a single obligation profile
 */
export function useObligationProfile(id: number) {
  return useQuery({
    queryKey: [SETTINGS_PROFILES_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ObligationProfileFull>(
        `${SETTINGS_BASE}/obligation-profiles/${id}/`
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Create a new obligation profile
 */
export function useCreateObligationProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ObligationProfileFormData) => {
      const response = await apiClient.post<ObligationProfileFull>(
        `${SETTINGS_BASE}/obligation-profiles/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_PROFILES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-profiles'] });
    },
  });
}

/**
 * Update an existing obligation profile
 */
export function useUpdateObligationProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ObligationProfileFormData> }) => {
      const response = await apiClient.put<ObligationProfileFull>(
        `${SETTINGS_BASE}/obligation-profiles/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_PROFILES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-profiles'] });
    },
  });
}

/**
 * Delete an obligation profile
 */
export function useDeleteObligationProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, force = false }: { id: number; force?: boolean }) => {
      await apiClient.delete(`${SETTINGS_BASE}/obligation-profiles/${id}/`, {
        params: { force },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_PROFILES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-profiles'] });
    },
  });
}

/**
 * Add obligation types to a profile
 */
export function useAddTypesToProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ profileId, typeIds }: { profileId: number; typeIds: number[] }) => {
      const response = await apiClient.post(
        `${SETTINGS_BASE}/obligation-profiles/${profileId}/add_types/`,
        { obligation_type_ids: typeIds }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_PROFILES_KEY] });
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
    },
  });
}

/**
 * Remove obligation types from a profile
 */
export function useRemoveTypesFromProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ profileId, typeIds }: { profileId: number; typeIds: number[] }) => {
      const response = await apiClient.post(
        `${SETTINGS_BASE}/obligation-profiles/${profileId}/remove_types/`,
        { obligation_type_ids: typeIds }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_PROFILES_KEY] });
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
    },
  });
}

// ============================================
// OBLIGATION GROUPS HOOKS
// ============================================

interface ObligationGroupParams {
  search?: string;
}

/**
 * Get all obligation groups for settings management
 */
export function useObligationGroupsList(params?: ObligationGroupParams) {
  return useQuery({
    queryKey: [SETTINGS_GROUPS_KEY, params],
    queryFn: async () => {
      const response = await apiClient.get<ObligationGroupFull[]>(
        `${SETTINGS_BASE}/obligation-groups/`,
        { params }
      );
      return response.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Get a single obligation group
 */
export function useObligationGroup(id: number) {
  return useQuery({
    queryKey: [SETTINGS_GROUPS_KEY, id],
    queryFn: async () => {
      const response = await apiClient.get<ObligationGroupFull>(
        `${SETTINGS_BASE}/obligation-groups/${id}/`
      );
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Create a new obligation group
 */
export function useCreateObligationGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ObligationGroupFormData) => {
      const response = await apiClient.post<ObligationGroupFull>(
        `${SETTINGS_BASE}/obligation-groups/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_GROUPS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
    },
  });
}

/**
 * Update an existing obligation group
 */
export function useUpdateObligationGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ObligationGroupFormData> }) => {
      const response = await apiClient.put<ObligationGroupFull>(
        `${SETTINGS_BASE}/obligation-groups/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_GROUPS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
    },
  });
}

/**
 * Delete an obligation group
 */
export function useDeleteObligationGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`${SETTINGS_BASE}/obligation-groups/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_GROUPS_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
    },
  });
}

/**
 * Set which obligation types belong to a group
 */
export function useSetGroupTypes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ groupId, typeIds }: { groupId: number; typeIds: number[] }) => {
      const response = await apiClient.post(
        `${SETTINGS_BASE}/obligation-groups/${groupId}/set_types/`,
        { obligation_type_ids: typeIds }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SETTINGS_GROUPS_KEY] });
      queryClient.invalidateQueries({ queryKey: [SETTINGS_TYPES_KEY] });
      queryClient.invalidateQueries({ queryKey: ['obligation-types-grouped'] });
    },
  });
}
