import apiClient from './client';

// Define interfaces for Artist data (can be moved to a types/interfaces file later)
export interface ArtistSummary {
  id: string;
  name: string;
  genre: string;
  active: boolean;
  autopilot: boolean;
  release_count: number;
  error_count: number;
  image_url?: string; // Optional image URL
}

export interface ArtistDetail extends ArtistSummary {
  description?: string;
  created_at: string;
  last_run_at?: string;
  chain_steps: { name: string; role: string; status: string; timestamp?: string }[];
  logs: { timestamp: string; level: string; message: string }[];
  // Add other detailed fields as needed
}

// API function to fetch all artists (summary)
export const fetchArtists = async (): Promise<ArtistSummary[]> => {
  try {
    // TODO: Update endpoint when backend API is ready
    // const response = await apiClient.get<ArtistSummary[]>("/artists");
    // return response.data;

    // Returning mock data for now
    console.warn("Using mock data for fetchArtists");
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    return [
      {
        id: '1',
        name: 'Synthwave Dreamer',
        genre: 'Synthwave',
        active: true,
        autopilot: true,
        release_count: 12,
        error_count: 1,
        image_url: 'https://via.placeholder.com/150/FF5733/FFFFFF?text=SD',
      },
      {
        id: '2',
        name: 'LoFi Beats Bot',
        genre: 'Lo-Fi Hip Hop',
        active: false,
        autopilot: false,
        release_count: 5,
        error_count: 3,
        image_url: 'https://via.placeholder.com/150/33FF57/FFFFFF?text=LBB',
      },
      {
        id: '3',
        name: 'Ambient Explorer',
        genre: 'Ambient',
        active: true,
        autopilot: false,
        release_count: 8,
        error_count: 0,
        image_url: 'https://via.placeholder.com/150/3357FF/FFFFFF?text=AE',
      },
      {
        id: '4',
        name: 'Techno Titan',
        genre: 'Techno',
        active: true,
        autopilot: true,
        release_count: 25,
        error_count: 0,
        image_url: 'https://via.placeholder.com/150/FFFF33/000000?text=TT',
      },
    ];
  } catch (error) {
    console.error("Error fetching artists:", error);
    throw error; // Re-throw error for react-query to handle
  }
};

// API function to fetch a single artist's details
export const fetchArtistById = async (id: string): Promise<ArtistDetail> => {
  try {
    // TODO: Update endpoint when backend API is ready
    // const response = await apiClient.get<ArtistDetail>(`/artists/${id}`);
    // return response.data;

    // Returning mock data for now
    console.warn(`Using mock data for fetchArtistById (ID: ${id})`);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    // Find the artist in the mock list or return a default mock detail
    const artists = await fetchArtists();
    const summary = artists.find(a => a.id === id);
    if (!summary) {
        throw new Error(`Artist with ID ${id} not found`);
    }
    return {
        ...summary,
        description: `An AI artist specializing in ${summary.genre} tracks. (Mock description)`, 
        created_at: '2024-01-15T10:30:00Z',
        last_run_at: '2024-05-03T09:30:00Z',
        chain_steps: [
            { name: 'Generate Lyrics', role: 'LLM', status: 'completed', timestamp: '2024-05-03 09:00:15Z' },
            { name: 'Generate Beat', role: 'MusicGen', status: 'completed', timestamp: '2024-05-03 09:05:30Z' },
            { name: 'Generate Vocals', role: 'VoiceClone', status: 'running', timestamp: '2024-05-03 09:10:45Z' },
            { name: 'Mix & Master', role: 'AudioProc', status: 'pending', timestamp: undefined },
            { name: 'Select Video', role: 'VideoAPI', status: 'pending', timestamp: undefined },
            { name: 'Publish', role: 'Platform', status: 'pending', timestamp: undefined },
        ],
        logs: [
            { timestamp: '2024-05-03 09:10:45Z', level: 'INFO', message: 'Starting voice clone generation...' },
            { timestamp: '2024-05-03 09:05:30Z', level: 'INFO', message: 'Beat generation completed successfully.' },
            { timestamp: '2024-05-03 09:05:00Z', level: 'INFO', message: 'Received beat generation request.' },
            { timestamp: '2024-05-03 09:00:15Z', level: 'INFO', message: 'Lyrics generated: [Verse 1] Neon lights...' },
            { timestamp: '2024-05-02 15:20:00Z', level: 'ERROR', message: 'Failed to connect to Video API (Timeout).' },
        ]
    };

  } catch (error) {
    console.error(`Error fetching artist with ID ${id}:`, error);
    throw error; // Re-throw error for react-query to handle
  }
};

// Add other artist-related API functions here (e.g., create, update, delete)

