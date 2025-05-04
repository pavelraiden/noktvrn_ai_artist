import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchArtists } from '../services/api';
import { ArtistCard, ArtistFilter } from '../components/artist';
import { Artist } from '../types';

/**
 * ArtistsList page component
 * @returns ArtistsList page with filtering and grid of artist cards
 */
const ArtistsList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [genreFilter, setGenreFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const { data: artists, isLoading, error } = useQuery({
    queryKey: ['artists'],
    queryFn: fetchArtists,
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleGenreFilter = (genre: string) => {
    setGenreFilter(genre);
  };

  const handleStatusFilter = (status: string) => {
    setStatusFilter(status);
  };

  // Filter artists based on search and filter criteria
  const filteredArtists = artists?.filter((artist: Artist) => {
    // Search by name
    const matchesSearch = artist.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Filter by genre
    const matchesGenre = genreFilter === 'all' || artist.genre === genreFilter;
    
    // Filter by status
    const matchesStatus = statusFilter === 'all' || artist.status === statusFilter;
    
    return matchesSearch && matchesGenre && matchesStatus;
  });

  if (isLoading) {
    return <div className="flex justify-center items-center h-full">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Error loading artists. Please try again later.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Artists</h1>
      </div>

      <ArtistFilter
        onSearch={handleSearch}
        onGenreFilter={handleGenreFilter}
        onStatusFilter={handleStatusFilter}
        searchQuery={searchQuery}
        genreFilter={genreFilter}
        statusFilter={statusFilter}
      />

      {filteredArtists?.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 text-gray-700 p-8 rounded-lg text-center">
          <p className="text-lg font-medium">No artists found</p>
          <p className="text-gray-500 mt-2">Try changing your search or filter criteria</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredArtists?.map((artist: Artist) => (
            <ArtistCard key={artist.id} artist={artist} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtistsList;