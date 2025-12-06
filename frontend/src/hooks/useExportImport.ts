import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

// ============================================
// TYPES
// ============================================

interface ImportResponse {
  success: boolean;
  created_count: number;
  updated_count: number;
  skipped_count?: number;
  errors: string[];
  message: string;
}

// ============================================
// EXPORT FUNCTIONS (direct download)
// ============================================

/**
 * Download clients CSV
 */
export async function downloadClientsCSV() {
  const response = await apiClient.get('/api/v1/export/clients/csv/', {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;

  // Get filename from Content-Disposition header or use default
  const contentDisposition = response.headers['content-disposition'];
  let filename = 'clients.csv';
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/);
    if (match) filename = match[1];
  }

  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download clients template CSV
 */
export async function downloadClientsTemplate() {
  const response = await apiClient.get('/api/v1/export/clients/template/', {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'clients_template.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download obligation types CSV
 */
export async function downloadObligationTypesCSV() {
  const response = await apiClient.get('/api/v1/export/obligation-types/csv/', {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'obligation_types.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download obligation profiles CSV
 */
export async function downloadObligationProfilesCSV() {
  const response = await apiClient.get('/api/v1/export/obligation-profiles/csv/', {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'obligation_profiles.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download client-obligation assignments CSV
 */
export async function downloadClientObligationsCSV() {
  const response = await apiClient.get('/api/v1/export/client-obligations/csv/', {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'client_obligations.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ============================================
// IMPORT HOOKS
// ============================================

/**
 * Import clients from CSV
 */
export function useImportClients() {
  const queryClient = useQueryClient();

  return useMutation<ImportResponse, Error, { file: File; mode: 'skip' | 'update' }>({
    mutationFn: async ({ file, mode }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode);

      const response = await apiClient.post<ImportResponse>(
        '/api/v1/import/clients/csv/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}

/**
 * Import client-obligation assignments from CSV
 */
export function useImportClientObligations() {
  const queryClient = useQueryClient();

  return useMutation<ImportResponse, Error, { file: File; mode: 'add' | 'replace' }>({
    mutationFn: async ({ file, mode }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode);

      const response = await apiClient.post<ImportResponse>(
        '/api/v1/import/client-obligations/csv/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-obligation-profile'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}
