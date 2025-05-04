import React from 'react';
import { Link } from 'react-router-dom';
import { Artist } from '../../types';
import { formatDate } from '../../utils/formatters';

interface ArtistCardProps {
  artist: Artist;
}

/**
 * ArtistCard component for displaying artist information in a grid
 * @param props ArtistCard properties
 * @returns ArtistCard component
 */
const ArtistCard: React.FC<ArtistCardProps> = ({ artist }) => {
  /**
   * Get CSS class for status badge based on artist status
   * @returns CSS class string
   */
  const getStatusBadgeClass = () => {
    switch (artist.status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  /**
   * Get display text for artist status
   * @returns Status text
   */
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
    <Link to={`/artists/${artist.id}`}>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
        <div className="relative">
          <img
            src={artist.avatarUrl || `https://via.placeholder.com/300x200/0ea5e9/FFFFFF?text=${encodeURIComponent(artist.name)}`}
            alt={artist.name}
            className="w-full h-40 object-cover"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
            <h3 className="text-white text-lg font-medium truncate">{artist.name}</h3>
            <p className="text-white/80 text-sm">{artist.genre}</p>
          </div>
        </div>
        <div className="p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-500">Last release</p>
              <p className="text-sm font-medium">{artist.lastReleaseDate ? formatDate(artist.lastReleaseDate) : 'No releases'}</p>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass()}`}>
              {getStatusText()}
            </span>
          </div>
          <div className="mt-4 flex justify-between text-xs text-gray-500">
            <span>Releases: {artist.releaseCount}</span>
            <span>Plays: {artist.playCount}</span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ArtistCard;