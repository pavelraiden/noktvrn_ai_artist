import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ArtistCard } from '../components/artist';

describe('ArtistCard', () => {
  const mockArtist = {
    id: '1',
    name: 'Test Artist',
    genre: 'electronic',
    status: 'active',
    releaseCount: 10,
    playCount: 100,
    lastReleaseDate: '2025-05-01T12:00:00Z',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2025-04-15T00:00:00Z',
  };

  it('renders artist information correctly', () => {
    render(
      <BrowserRouter>
        <ArtistCard artist={mockArtist} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Test Artist')).toBeInTheDocument();
    expect(screen.getByText('electronic')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Releases: 10')).toBeInTheDocument();
    expect(screen.getByText('Plays: 100')).toBeInTheDocument();
    expect(screen.getByText('Last release')).toBeInTheDocument();
  });

  it('displays placeholder when no lastReleaseDate is provided', () => {
    const artistWithoutRelease = {
      ...mockArtist,
      lastReleaseDate: undefined
    };

    render(
      <BrowserRouter>
        <ArtistCard artist={artistWithoutRelease} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('No releases')).toBeInTheDocument();
  });

  it('applies correct status badge class', () => {
    const artistWithError = {
      ...mockArtist,
      status: 'error'
    };

    render(
      <BrowserRouter>
        <ArtistCard artist={artistWithError} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Error').className).toContain('bg-red-100');
  });
});