import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}`, error.response.data);
    } else if (error.request) {
      console.error('[API Error] No response received', error.request);
    } else {
      console.error('[API Error]', error.message);
    }
    return Promise.reject(error);
  }
);

// ==================== RESOURCE ENDPOINTS ====================

export const resourcesAPI = {
  // Get available resources
  getResources: () => api.get('/resources/'),
  
  // Update available resources
  updateResources: (resources) => api.post('/resources/', resources),
  
  // Assign resources to a district
  assignResources: (assignment) => api.post('/resources/assign', assignment),
  
  // Get all assignments or filter by district
  getAssignments: (district = null) => {
    const params = district ? { district } : {};
    return api.get('/resources/assignments', { params });
  },
  
  // Get total allocated resources
  getTotalAllocated: () => api.get('/resources/total-allocated'),
};

// ==================== PREDICTION ENDPOINTS ====================

export const predictionsAPI = {
  // Generate new predictions
  generatePredictions: () => api.post('/predictions/generate'),
  
  // Get all district predictions
  getDistricts: () => api.get('/predictions/districts'),
  
  // Get specific district prediction
  getDistrict: (districtName) => api.get(`/predictions/districts/${districtName}`),
  
  // Get hotspots (high-risk districts)
  getHotspots: () => api.get('/predictions/hotspots'),
  
  // Get resource recommendations
  getRecommendations: () => api.get('/predictions/recommendations'),
};

// ==================== ADMIN ENDPOINTS ====================

export const adminAPI = {
  // Get complete system overview
  getOverview: () => api.get('/admin/overview'),
  
  // Get statistics
  getStatistics: () => api.get('/admin/statistics'),
  
  // Get resource gap analysis
  getResourceGap: () => api.get('/admin/resource-gap'),
  
  // Compare districts
  compareDistricts: (districts) => {
    const params = { districts: districts.join(',') };
    return api.get('/admin/district-comparison', { params });
  },
};

// ==================== HEALTH CHECK ====================

export const healthAPI = {
  check: () => api.get('/'),
};

// Export the axios instance for custom requests
export default api;