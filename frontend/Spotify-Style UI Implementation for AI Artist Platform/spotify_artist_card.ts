import React from 'react';
import { Link } from 'react-router-dom';
import { Artist } from '../../types';
import { formatDate } from '../../utils/formatters';

interface SpotifyArtistCardProps {
  artist: Artist;
}

/**
 * Spotify-style artist card component
 * Used in grid layouts for displaying artists
 * @param props Component properties
 */
const SpotifyArtistCard: React.FC<SpotifyArtistCardProps> = ({ artist }) => {
  // Get status badge color based on artist status
  const getStatusColor = () => {
    switch (artist.status) {
      case 'active':
        return 'bg-spotify-green';
      case 'paused':
        return 'bg-spotify-blue';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  // Get readable status text
  const getStatusText = () => {
    switch (artist.status) {
      case 'active':
        return 'Active';
      case 'paused':
        return 'Paused';
      case 'inactive':
        return 'Inactive';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  return (
    <Link 
      to={`/artists/${artist.id}`}
      className="group bg-background-elevated p-4 rounded-spotify hover:bg-background-highlight transition-colors duration-300 block"
    >
      <div className="relative mb-4 aspect-square overflow-hidden rounded-spotify bg-background-elevated shadow-spotify-light group-hover:shadow-spotify transition-all duration-300">
        {/* Artist image */}
        <img
          src={artist.avatarUrl || `https://via.placeholder.com/300/1DB954/ffffff?text=${encodeURIComponent(artist.name.charAt(0))}`}
          alt={artist.name}
          className="w-full h-full object-cover"
        />
        
        {/* Play button overlay (appears on hover) */}
        <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-y-2 group-hover:translate-y-0">
          <button 
            className="w-10 h-10 rounded-full bg-spotify-green shadow-spotify-light flex items-center justify-center text-black hover:scale-105 transition-transform"
            aria-label="Play"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </button>
        </div>
        
        {/* Status indicator */}
        <div className={`absolute top-2 left-2 ${getStatusColor()} rounded-pill px-2 py-0.5`}>
          <span className="text-xs font-medium text-black">{getStatusText()}</span>
        </div>
      </div>
      
      {/* Artist info */}
      <h3 className="font-bold text-white truncate mb-1">{artist.name}</h3>
      <p className="text-text-subdued text-sm truncate mb-1">{artist.genre}</p>
      <p className="text-text-subdued text-xs truncate">
        {artist.releaseCount} {artist.releaseCount === 1 ? 'release' : 'releases'} • 
        {artist.lastReleaseDate ? ` Last: ${formatDate(artist.lastReleaseDate).split(',')[0]}` : ' No releases yet'}
      </p>
    </Link>
  );
};

export default SpotifyArtistCard;