import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/accounting';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If 401 error and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh: refreshToken,
          }, {
            headers: { 'Content-Type': 'application/json' }
          });

          const { access } = response.data;
          localStorage.setItem('accessToken', access);

          // Retry the original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API functions
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/api/auth/login/', { username, password });
    return response.data;
  },

  refreshToken: async (refresh: string) => {
    const response = await apiClient.post('/api/auth/refresh/', { refresh });
    return response.data;
  },

  verifyToken: async (token: string) => {
    const response = await apiClient.post('/api/auth/verify/', { token });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/api/auth/me/');
    return response.data;
  },

  updateProfile: async (data: { first_name?: string; last_name?: string; email?: string }) => {
    const response = await apiClient.patch('/api/auth/me/', data);
    return response.data;
  },
};

// Clients API functions
export const clientsApi = {
  getAll: async (params?: { search?: string; page?: number; page_size?: number }) => {
    const response = await apiClient.get('/api/v1/clients/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await apiClient.get(`/api/v1/clients/${id}/`);
    return response.data;
  },
};

// Obligations API functions
export const obligationsApi = {
  getAll: async (params?: { search?: string; page?: number; page_size?: number; status?: string }) => {
    const response = await apiClient.get('/api/v1/obligations/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await apiClient.get(`/api/v1/obligations/${id}/`);
    return response.data;
  },
};

// Global Search API
export interface SearchResultItem {
  id: number;
  title: string;
  subtitle: string;
  url: string;
  type: 'client' | 'obligation' | 'ticket' | 'call';
  extra?: Record<string, unknown>;
}

export interface GlobalSearchResponse {
  query: string;
  results: {
    clients: SearchResultItem[];
    obligations: SearchResultItem[];
    tickets: SearchResultItem[];
    calls: SearchResultItem[];
  };
  total: number;
  error?: string;
}

export const searchApi = {
  globalSearch: async (query: string): Promise<GlobalSearchResponse> => {
    const response = await apiClient.get('/api/v1/search/', { params: { q: query } });
    return response.data;
  },
};

// GSIS API (Αναζήτηση στοιχείων με ΑΦΜ)
export interface AFMData {
  afm: string;
  onomasia: string;
  doy: string;
  doy_descr: string;
  legal_form: string;
  legal_form_descr: string;
  postal_address: string;
  postal_address_no: string;
  postal_zip_code: string;
  postal_area: string;
  registration_date: string | null;
  stop_date: string | null;
  deactivation_flag: boolean;
  firm_flag: boolean;
  activities: Array<{
    firm_act_descr?: string;
    firm_act_kind?: string;
    firm_act_kind_descr?: string;
  }>;
}

export interface AFMLookupResponse {
  success: boolean;
  data?: AFMData;
  error?: string;
}

export interface GSISStatusResponse {
  configured: boolean;
  active: boolean;
  username?: string;
}

export const gsisApi = {
  // Αναζήτηση στοιχείων με ΑΦΜ
  lookupAfm: async (afm: string): Promise<AFMLookupResponse> => {
    try {
      const response = await apiClient.post('/api/v1/afm-lookup/', { afm });
      return response.data;
    } catch (error: unknown) {
      // Extract error message from axios error response
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { error?: string } } };
        if (axiosError.response?.data?.error) {
          return { success: false, error: axiosError.response.data.error };
        }
      }
      return { success: false, error: 'Σφάλμα επικοινωνίας με τον server' };
    }
  },

  // Κατάσταση ρυθμίσεων GSIS
  getStatus: async (): Promise<GSISStatusResponse> => {
    const response = await apiClient.get('/api/v1/gsis/status/');
    return response.data;
  },

  // Ενημέρωση ρυθμίσεων GSIS
  updateSettings: async (data: { username: string; password?: string; is_active?: boolean }) => {
    const response = await apiClient.post('/api/v1/gsis/settings/', data);
    return response.data;
  },

  // Δοκιμή σύνδεσης
  testConnection: async () => {
    const response = await apiClient.post('/api/v1/gsis/test/');
    return response.data;
  },
};

export default apiClient;
