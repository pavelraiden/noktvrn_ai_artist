import apiClient from './client';

// Define interfaces for Dashboard data
export interface QuickStats {
  artists: number;
  active: number;
  autopilot: number;
  errors: number; // Assuming errors today or similar metric
}

export interface SystemStatus {
  [service: string]: 'Online' | 'Degraded' | 'Offline';
}

// TODO: Define interfaces for Recent Activity and Performance Data if needed

// API function to fetch quick stats
export const fetchQuickStats = async (): Promise<QuickStats> => {
  try {
    // TODO: Update endpoint when backend API is ready
    // const response = await apiClient.get<QuickStats>("/dashboard/stats");
    // return response.data;

    // Returning mock data for now
    console.warn("Using mock data for fetchQuickStats");
    await new Promise(resolve => setTimeout(resolve, 300)); // Simulate network delay
    return {
      artists: 15,
      active: 10,
      autopilot: 8,
      errors: 2,
    };
  } catch (error) {
    console.error("Error fetching quick stats:", error);
    throw error;
  }
};

// API function to fetch system status
export const fetchSystemStatus = async (): Promise<SystemStatus> => {
  try {
    // TODO: Update endpoint when backend API is ready
    // const response = await apiClient.get<SystemStatus>("/dashboard/status");
    // return response.data;

    // Returning mock data for now
    console.warn("Using mock data for fetchSystemStatus");
    await new Promise(resolve => setTimeout(resolve, 400)); // Simulate network delay
    return {
      'Music Gen API': 'Online',
      'Voice Clone API': 'Degraded',
      'Video API': 'Online',
      'Database': 'Online',
      'Queue': 'Offline',
    };
  } catch (error) {
    console.error("Error fetching system status:", error);
    throw error;
  }
};

// TODO: Add API functions for Recent Activity and Performance Data

