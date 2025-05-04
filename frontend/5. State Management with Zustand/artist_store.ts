import { create } from 'zustand';
import { Artist } from '../types';

interface ArtistState {
  selectedArtist: Artist | null;
  recentlyViewed: Artist[];
  setSelectedArtist: (artist: Artist | null) => void;
  addToRecentlyViewed: (artist: Artist) => void;
  clearRecentlyViewed: () => void;
}

/**
 * Store for artist-related state management
 */
export const useArtistStore = create<ArtistState>((set) => ({
  selectedArtist: null,
  recentlyViewed: [],
  
  /**
   * Sets the currently selected artist
   */
  setSelectedArtist: (artist) => set({ selectedArtist: artist }),
  
  /**
   * Adds an artist to the recently viewed list
   * Prevents duplicates and limits list to 5 items
   */
  addToRecentlyViewed: (artist) => 
    set((state) => ({
      recentlyViewed: [
        artist,
        ...state.recentlyViewed.filter(a => a.id !== artist.id)
      ].slice(0, 5)
    })),
  
  /**
   * Clears the recently viewed list
   */
  clearRecentlyViewed: () => set({ recentlyViewed: [] }),
}));