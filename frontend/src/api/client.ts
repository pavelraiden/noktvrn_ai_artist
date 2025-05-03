import axios from 'axios';

// TODO: Get API base URL from environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Add authorization headers if needed, e.g.:
    // 'Authorization': `Bearer ${getToken()}`
  },
});

// Add interceptors for request/response handling if needed
// apiClient.interceptors.response.use(...);

export default apiClient;

