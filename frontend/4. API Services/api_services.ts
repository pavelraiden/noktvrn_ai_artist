import axios from 'axios';
import { Artist, Stats } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches dashboard statistics
 * @returns Promise with stats data
 */
export const fetchStats = async (): Promise<Stats> => {
  const { data } = await api.get('/stats');
  return data;
};

/**
 * Fetches the list of artists
 * @param params Optional query parameters
 * @returns Promise with artists array
 */
export const fetchArtists = async (params?: { 
  genre?: string; 
  status?: string; 
  search?: string;
}): Promise<Artist[]> => {
  const { data } = await api.get('/artists', { params });
  return data;
};

/**
 * Fetches a single artist by ID
 * @param id Artist ID
 * @returns Promise with artist data
 */
export const fetchArtistById = async (id: string): Promise<Artist> => {
  const { data } = await api.get(`/artists/${id}`);
  return data;
};

/**
 * Fetches logs for an artist
 * @param id Artist ID
 * @param params Optional query parameters
 * @returns Promise with logs array
 */
export const fetchArtistLogs = async (id: string, params?: {
  level?: string;
  limit?: number;
}): Promise<any[]> => {
  const { data } = await api.get(`/artists/${id}/logs`, { params });
  return data;
};

/**
 * Generates new content for an artist
 * @param id Artist ID
 * @param params Generation parameters
 * @returns Promise with generation result
 */
export const generateArtistContent = async (
  id: string, 
  params: {
    genre: string;
    style: string;
    length: string;
  }
): Promise<any> => {
  const { data } = await api.post(`/artists/${id}/generate`, params);
  return data;
};