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