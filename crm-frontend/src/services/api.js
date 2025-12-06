const API_BASE_URL = 'http://localhost:8000/api';

const apiCall = async (endpoint, options = {}) => {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
      throw new Error('API Error');
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const clientsAPI = {
  getAll: async () => apiCall('/clients/'),
  getStats: async () => apiCall('/clients/stats/'),
};

export const obligationsAPI = {
  getAll: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    return apiCall(`/obligations/?${params}`);
  },
  updateStatus: async (id, status) => {
    return apiCall(`/obligations/${id}/update_status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },
};

// =============================================================================
// myDATA API
// =============================================================================

export const mydataAPI = {
  // Dashboard - overview for all clients
  getDashboard: async (year, month) => {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (month) params.append('month', month);
    return apiCall(`/mydata/dashboard/?${params}`);
  },

  // Trend data for charts
  getTrend: async (afm = null, months = 6) => {
    const params = new URLSearchParams({ months });
    if (afm) params.append('afm', afm);
    return apiCall(`/mydata/trend/?${params}`);
  },

  // Client detail
  getClientVAT: async (afm, year, month, includeRecords = false) => {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (month) params.append('month', month);
    if (includeRecords) params.append('include_records', 'true');
    return apiCall(`/mydata/client/${afm}/?${params}`);
  },

  // VAT Records
  records: {
    getAll: async (filters = {}) => {
      const params = new URLSearchParams(filters);
      return apiCall(`/mydata/records/?${params}`);
    },
    get: async (id) => apiCall(`/mydata/records/${id}/`),
    getSummary: async (afm, year, month) => {
      const params = new URLSearchParams({ afm });
      if (year) params.append('year', year);
      if (month) params.append('month', month);
      return apiCall(`/mydata/records/summary/?${params}`);
    },
    getByCategory: async (afm, year, month, recType = null) => {
      const params = new URLSearchParams({ afm });
      if (year) params.append('year', year);
      if (month) params.append('month', month);
      if (recType) params.append('rec_type', recType);
      return apiCall(`/mydata/records/by_category/?${params}`);
    },
  },

  // Credentials
  credentials: {
    getAll: async (filters = {}) => {
      const params = new URLSearchParams(filters);
      return apiCall(`/mydata/credentials/?${params}`);
    },
    get: async (id) => apiCall(`/mydata/credentials/${id}/`),
    create: async (data) => {
      return apiCall('/mydata/credentials/', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    update: async (id, data) => {
      return apiCall(`/mydata/credentials/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    updateCredentials: async (id, userId, subscriptionKey, isSandbox = false) => {
      return apiCall(`/mydata/credentials/${id}/update_credentials/`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          subscription_key: subscriptionKey,
          is_sandbox: isSandbox,
        }),
      });
    },
    verify: async (id) => {
      return apiCall(`/mydata/credentials/${id}/verify/`, {
        method: 'POST',
      });
    },
    sync: async (id, options = {}) => {
      return apiCall(`/mydata/credentials/${id}/sync/`, {
        method: 'POST',
        body: JSON.stringify(options),
      });
    },
  },

  // Sync logs
  logs: {
    getAll: async (filters = {}) => {
      const params = new URLSearchParams(filters);
      return apiCall(`/mydata/logs/?${params}`);
    },
    get: async (id) => apiCall(`/mydata/logs/${id}/`),
  },
};