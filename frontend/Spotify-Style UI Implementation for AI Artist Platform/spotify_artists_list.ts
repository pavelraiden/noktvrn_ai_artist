import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchArtists } from '../services/api';
import SpotifyArtistCard from '../components/artist/SpotifyArtistCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Artist } from '../types';

/**
 * Spotify-styled artists list page
 * Displays a grid of artist cards with filtering options
 */
const SpotifyArtistsList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [genreFilter, setGenreFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');

  // Fetch artists data
  const { 
    data: artists, 
    isLoading, 
    error 
  } = useQuery({
    queryKey: ['artists'],
    queryFn: fetchArtists,
  });

  // Filter and sort artists
  const filteredArtists = React.useMemo(() => {
    if (!artists) return [];

    let result = [...artists];

    // Apply search filter
    if (searchQuery) {
      result = result.filter(artist => 
        artist.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply genre filter
    if (genreFilter !== 'all') {
      result = result.filter(artist => artist.genre === genreFilter);
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      result = result.filter(artist => artist.status === statusFilter);
    }

    // Apply sorting
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'plays':
        result.sort((a, b) => b.playCount - a.playCount);
        break;
      case 'releases':
        result.sort((a, b) => b.releaseCount - a.releaseCount);
        break;
      case 'recent':
        result.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
        break;
      default:
        break;
    }

    return result;
  }, [artists, searchQuery, genreFilter, statusFilter, sortBy]);

  // Get unique genres for the filter
  const genres = React.useMemo(() => {
    if (!artists) return [];
    
    const genreSet = new Set(artists.map(artist => artist.genre));
    return ['all', ...Array.from(genreSet)];
  }, [artists]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner size="lg" label="Loading artists..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-background-elevated p-6 rounded-spotify">
        <h3 className="text-xl font-bold mb-4 text-essential-negative">Error Loading Artists</h3>
        <p className="text-text-subdued">Unable to load artists. Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Hero header */}
      <div className="flex flex-col -mx-8 -mt-8 mb-8 px-8 pt-32 pb-8 bg-gradient-to-b from-spotify-green/30 to-background-base">
        <h1 className="text-4xl font-bold mb-4">Artists</h1>
        <p className="text-text-subdued">Browse and manage your AI artists</p>
      </div>

      {/* Filter tools */}
      <div className="bg-background-elevated p-4 rounded-spotify mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search artists..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 pl-10 rounded-pill bg-background-highlight text-white placeholder-text-subdued focus:outline-none focus:ring-2 focus:ring-spotify-green"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-subdued">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </div>
          </div>

          {/* Genre filter */}
          <div className="md:w-48">
            <select
              value={genreFilter}
              onChange={(e) => setGenreFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-background-highlight text-white border border-background-press focus:outline-none focus:ring-2 focus:ring-spotify-green"
            >
              <option value="all">All genres</option>
              {genres.filter(g => g !== 'all').map(genre => (
                <option key={genre} value={genre}>
                  {genre.charAt(0).toUpperCase() + genre.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Status filter */}
          <div className="md:w-48">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-background-highlight text-white border border-background-press focus:outline-none focus:ring-2 focus:ring-spotify-green"
            >
              <option value="all">All statuses</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="inactive">Inactive</option>
              <option value="error">Error</option>
            </select>
          </div>

          {/* Sort by */}
          <div className="md:w-48">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-background-highlight text-white border border-background-press focus:outline-none focus:ring-2 focus:ring-spotify-green"
            >
              <option value="name">Sort by name</option>
              <option value="plays">Sort by plays</option>
              <option value="releases">Sort by releases</option>
              <option value="recent">Sort by recent</option>
            </select>
          </div>
        </div>
      </div>

      {/* Artist grid */}
      {filteredArtists.length === 0 ? (
        <div className="bg-background-elevated p-12 rounded-spotify flex flex-col items-center justify-center">
          <p className="text-text-subdued text-center text-lg mb-2">No artists found</p>
          <p className="text-text-subdued text-center text-sm">Try adjusting your filters or create a new artist</p>
          <button className="mt-6 px-6 py-3 rounded-pill bg-spotify-green hover:bg-spotify-brightgreen text-black font-bold">
            Create New Artist
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {filteredArtists.map(artist => (
            <SpotifyArtistCard key={artist.id} artist={artist} />
          ))}
        </div>
      )}
    </div>
  );
};

export default SpotifyArtistsList;