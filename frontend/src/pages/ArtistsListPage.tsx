import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchArtists } from '@/api/artists'; // Use path alias
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton"; // Import Skeleton for loading state

const ArtistsListPage: React.FC = () => {
  const { data: artists, isLoading, error } = useQuery({
    queryKey: ['artists'],
    queryFn: fetchArtists,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Artists</h1>
        <Button>Add New Artist</Button> {/* Placeholder */}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(4)].map((_, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center gap-4">
                <Skeleton className="h-12 w-12 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
                <Skeleton className="h-6 w-16" />
              </CardHeader>
              <CardContent className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </CardContent>
              <CardFooter>
                <Skeleton className="h-10 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-red-500">
          Error fetching artists: {error.message}
        </div>
      )}

      {/* Artist Grid - Success State */}
      {!isLoading && !error && artists && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {artists.map((artist) => (
            <Card key={artist.id}>
              <CardHeader className="flex flex-row items-center gap-4">
                <Avatar className="h-12 w-12">
                  {/* Use optional chaining for image_url */}
                  <AvatarImage src={artist.image_url || undefined} alt={artist.name} />
                  <AvatarFallback>{artist.name.substring(0, 2).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <CardTitle>{artist.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{artist.genre}</p>
                </div>
                <Badge variant={artist.active ? 'default' : 'outline'}>
                  {artist.active ? 'Active' : 'Inactive'}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Releases:</span>
                  <span>{artist.release_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Errors:</span>
                  <span className={artist.error_count > 0 ? 'text-red-500' : ''}>{artist.error_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Autopilot:</span>
                  <Badge variant={artist.autopilot ? 'secondary' : 'outline'}>
                    {artist.autopilot ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild variant="outline" className="w-full">
                  <Link to={`/artists/${artist.id}`}>View Details</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtistsListPage;

