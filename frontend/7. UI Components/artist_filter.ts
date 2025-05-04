import React from 'react';
import { ArtistGenre, ArtistStatus } from '../../types';

interface ArtistFilterProps {
  onSearch: (query: string) => void;
  onGenreFilter: (genre: string) => void;
  onStatusFilter: (status: string) => void;
  searchQuery: string;
  genreFilter: string;
  statusFilter: string;
}

/**
 * ArtistFilter component for filtering the artist list
 * @param props ArtistFilter properties
 * @returns ArtistFilter component
 */
const ArtistFilter: React.FC<ArtistFilterProps> = ({
  onSearch,
  onGenreFilter,
  onStatusFilter,
  searchQuery,
  genreFilter,
  statusFilter,
}) => {
  // Genres (in a real app, these might come from the API)
  const genres = [
    { value: 'all', label: 'All Genres' },
    { value: 'electronic', label: 'Electronic' },
    { value: 'pop', label: 'Pop' },
    { value: 'rock', label: 'Rock' },
    { value: 'hip-hop', label: 'Hip Hop' },
    { value: 'ambient', label: 'Ambient' },
    { value: 'other', label: 'Other' },
  ];

  // Statuses
  const statuses = [
    { value: 'all', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'paused', label: 'Paused' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'error', label: 'Error' },
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            id="search"
            placeholder="Search by artist name..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            value={searchQuery}
            onChange={(e) => onSearch(e.target.value)}
          />
        </div>

        <div className="w-full md:w-48">
          <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-1">
            Genre
          </label>
          <select
            id="genre"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            value={genreFilter}
            onChange={(e) => onGenreFilter(e.target.value)}
          >
            {genres.map((genre) => (
              <option key={genre.value} value={genre.value}>
                {genre.label}
              </option>
            ))}
          </select>
        </div>

        <div className="w-full md:w-48">
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            value={statusFilter}
            onChange={(e) => onStatusFilter(e.target.value)}
          >
            {statuses.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default ArtistFilter;