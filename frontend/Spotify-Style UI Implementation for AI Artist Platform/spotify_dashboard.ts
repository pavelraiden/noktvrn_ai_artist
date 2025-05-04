import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStats, fetchArtists } from '../services/api';
import { Link } from 'react-router-dom';
import { formatCurrency, formatNumber } from '../utils/formatters';
import SpotifyArtistCard from '../components/artist/SpotifyArtistCard';
import { BarLineChart, PieChart } from '../components/charts';
import LoadingSpinner from '../components/ui/LoadingSpinner';

/**
 * Spotify-styled dashboard page component
 * Displays summary metrics, charts, and artist highlights
 */
const SpotifyDashboard: React.FC = () => {
  // Fetch stats and artists data
  const { data: stats, isLoading: isLoadingStats } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
  });

  const { data: artists, isLoading: isLoadingArtists } = useQuery({
    queryKey: ['artists'],
    queryFn: fetchArtists,
  });

  // Show loading state when data is being fetched
  if (isLoadingStats || isLoadingArtists) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner size="lg" label="Loading dashboard..." />
      </div>
    );
  }

  // Get top artists (most played/popular)
  const topArtists = artists?.slice(0, 6).sort((a, b) => b.playCount - a.playCount) || [];

  // Get recently updated artists
  const recentArtists = artists?.slice(0, 6).sort((a, b) => {
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  }) || [];

  return (
    <div className="space-y-8 pb-8 animate-fade-in">
      {/* Welcome/stats header */}
      <div className="bg-gradient-to-b from-spotify-purple/30 to-background-base p-8 -m-8 mb-0">
        <h1 className="text-3xl font-bold mb-6">Welcome to AI Artist Platform</h1>
        
        {/* Stats grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard 
            title="Total Revenue" 
            value={formatCurrency(stats?.totalRevenue || 0)} 
            icon={<CurrencyIcon />}
          />
          <StatCard 
            title="Artist Count" 
            value={stats?.artistCount.toString() || '0'} 
            icon={<ArtistIcon />}
          />
          <StatCard 
            title="Active Runs" 
            value={stats?.activeRuns.toString() || '0'} 
            icon={<RunningIcon />}
          />
          <StatCard 
            title="Total Plays" 
            value={formatNumber(
              artists?.reduce((total, artist) => total + artist.playCount, 0) || 0
            )} 
            icon={<PlayCountIcon />}
          />
        </div>
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-background-elevated p-4 rounded-spotify">
          <h2 className="font-bold text-xl mb-4">Revenue & Subscriptions</h2>
          <BarLineChart 
            data={stats?.revenueSubscriptionsData || []} 
            height={250}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="bg-background-elevated p-4 rounded-spotify">
            <h2 className="font-bold text-xl mb-4">Genre Distribution</h2>
            <PieChart 
              data={stats?.genreDistribution || []} 
              height={200}
              colors={['#1DB954', '#7358FF', '#2E77D0', '#E8115B', '#F59B23']}
            />
          </div>

          <div className="bg-background-elevated p-4 rounded-spotify">
            <h2 className="font-bold text-xl mb-4">Conversion Rates</h2>
            <PieChart 
              data={stats?.conversionRates || []} 
              height={200}
              colors={['#1DB954', '#E8115B']}
            />
          </div>
        </div>
      </div>

      {/* Top Artists section */}
      <div>
        <SectionHeader title="Top Artists" linkTo="/artists" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
          {topArtists.map(artist => (
            <SpotifyArtistCard key={artist.id} artist={artist} />
          ))}
        </div>
      </div>

      {/* Recently Updated section */}
      <div>
        <SectionHeader title="Recently Updated" linkTo="/artists" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
          {recentArtists.map(artist => (
            <SpotifyArtistCard key={artist.id} artist={artist} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper components
const SectionHeader: React.FC<{title: string; linkTo: string}> = ({ title, linkTo }) => (
  <div className="flex justify-between items-center mb-4">
    <h2 className="font-bold text-2xl">{title}</h2>
    <Link to={linkTo} className="text-text-subdued hover:text-white text-sm font-bold uppercase tracking-wider">
      See All
    </Link>
  </div>
);

const StatCard: React.FC<{title: string; value: string; icon: React.ReactNode}> = ({ title, value, icon }) => (
  <div className="bg-background-elevated p-4 rounded-spotify">
    <div className="flex items-center gap-3 mb-2">
      <div className="w-10 h-10 bg-spotify-green/20 rounded-full flex items-center justify-center text-spotify-green">
        {icon}
      </div>
      <h3 className="text-text-subdued font-medium">{title}</h3>
    </div>
    <p className="text-2xl font-bold">{value}</p>
  </div>
);

// Icons
const CurrencyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="16" />
    <line x1="8" y1="12" x2="16" y2="12" />
  </svg>
);

const ArtistIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

const RunningIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
    <polygon points="5 3 19 12 5 21 5 3" />
  </svg>
);

const PlayCountIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
    <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
    <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
  </svg>
);

export default SpotifyDashboard;