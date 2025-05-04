export type ArtistStatus = 'active' | 'paused' | 'inactive' | 'error';
export type ArtistGenre = 'electronic' | 'pop' | 'rock' | 'hip-hop' | 'ambient' | 'other';

export interface ArtistMetrics {
  ecpa: number;
  ecpt: number;
  plays: number;
  conversionRate: number;
  retentionRate: number;
  completionRate: number;
}

export interface ArtistRelease {
  id: string;
  title: string;
  date: string;
  imageUrl?: string;
  plays: number;
  duration?: number;
  trackUrl?: string;
}

export interface Artist {
  id: string;
  name: string;
  genre: ArtistGenre;
  status: ArtistStatus;
  avatarUrl?: string;
  lastReleaseDate?: string;
  releaseCount: number;
  playCount: number;
  metrics?: ArtistMetrics;
  releases?: ArtistRelease[];
  createdAt: string;
  updatedAt: string;
}