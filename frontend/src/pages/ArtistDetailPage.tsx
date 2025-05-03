import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchArtistById } from '@/api/artists'; // Use path alias
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton"; // Import Skeleton
import ChatWindow from '@/components/ChatWindow'; // Import ChatWindow
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"; // Import ScrollArea

const getStatusIcon = (status: string) => {
  switch (status?.toLowerCase()) { // Add null check for status
    case 'completed': return '✅';
    case 'running': return '⏳';
    case 'error': return '❌';
    case 'pending':
    default: return '⏸️';
  }
};

const ArtistDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: artist, isLoading, error } = useQuery({
    queryKey: ['artist', id],
    queryFn: () => fetchArtistById(id!),
    enabled: !!id,
  });

  // Loading State
  if (isLoading) {
    return (
      <div className="space-y-6 p-4 md:p-6"> {/* Add padding */}
        {/* Responsive Header Skeleton */}
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
          <Skeleton className="h-10 w-10 flex-shrink-0" /> {/* Back button */}
          <div className="flex items-center gap-4">
            <Skeleton className="h-16 w-16 rounded-full flex-shrink-0" />
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
          <div className="flex gap-2 mt-2 md:mt-0 md:ml-auto">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <Skeleton className="h-10 w-full" /> {/* Tabs List */}
        {/* ... rest of skeleton ... */}
        <Card>
          <CardHeader><Skeleton className="h-6 w-1/3" /></CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-20 w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader><Skeleton className="h-6 w-1/3" /></CardHeader>
          <CardContent>
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error State
  if (error || !artist) {
    return (
      <div className="p-4 md:p-6"> {/* Add padding */}
        <Button variant="outline" size="icon" asChild className="mb-4">
          <Link to="/artists">
            <span>&lt;</span>
          </Link>
        </Button>
        <div className="text-red-500">
          Error fetching artist details: {error?.message || 'Artist not found'}
        </div>
      </div>
    );
  }

  // Success State
  return (
    <div className="space-y-6 p-4 md:p-6"> {/* Add padding */}
      {/* Responsive Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
        <Button variant="outline" size="icon" asChild className="flex-shrink-0">
          <Link to="/artists">
            {/* TODO: Add proper icon like ChevronLeft */}
            <span>&lt;</span>
          </Link>
        </Button>
        <div className="flex items-center gap-4 flex-grow">
          <Avatar className="h-16 w-16 flex-shrink-0">
            <AvatarImage src={artist.image_url || undefined} alt={artist.name} />
            <AvatarFallback>{artist.name.substring(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex-grow">
            <h1 className="text-2xl md:text-3xl font-bold flex flex-wrap items-center gap-2">
              <span>{artist.name}</span>
              <Badge variant={artist.active ? 'default' : 'outline'}>
                {artist.active ? 'Active' : 'Inactive'}
              </Badge>
            </h1>
            <p className="text-muted-foreground">{artist.genre}</p>
          </div>
        </div>
        <div className="flex gap-2 mt-2 md:mt-0 md:ml-auto flex-shrink-0">
          <Button variant="outline" size="sm">{artist.active ? 'Pause' : 'Resume'}</Button>
          <Button variant="outline" size="sm">Refresh</Button>
        </div>
      </div>

      {/* Responsive Tabs */}
      <Tabs defaultValue="overview">
        <ScrollArea className="w-full whitespace-nowrap border-b">
          <TabsList className="inline-flex h-auto p-1">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
            <TabsTrigger value="chat">Chat</TabsTrigger>
          </TabsList>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Artist Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p>{artist.description || 'No description available.'}</p>
              {/* Responsive Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-sm">
                <span>Created:</span><span className="text-muted-foreground">{new Date(artist.created_at).toLocaleString()}</span>
                <span>Last Run:</span><span className="text-muted-foreground">{artist.last_run_at ? new Date(artist.last_run_at).toLocaleString() : 'Never'}</span>
                <span>Releases:</span><span className="text-muted-foreground">{artist.release_count}</span>
                <span>Errors:</span><span className={`font-medium ${artist.error_count > 0 ? 'text-red-500' : ''}`}>{artist.error_count}</span>
                <span>Autopilot:</span>
                <Badge variant={artist.autopilot ? 'secondary' : 'outline'}>
                  {artist.autopilot ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>LLM Chain Status</CardTitle>
            </CardHeader>
            <CardContent>
              <TooltipProvider>
                {/* ScrollArea for Chain Status */}
                <ScrollArea className="w-full whitespace-nowrap">
                  <div className="flex space-x-2 pb-4">
                    {artist.chain_steps?.map((step, index) => (
                      <Tooltip key={index}>
                        <TooltipTrigger asChild>
                          <div className={`flex flex-col items-center p-2 border rounded-md min-w-[100px] ${step.status === 'running' ? 'border-blue-500' : ''}`}>
                            <span className="text-2xl mb-1">{getStatusIcon(step.status)}</span>
                            <span className="text-xs font-medium text-center">{step.name}</span>
                            <span className="text-xs text-muted-foreground">({step.role})</span>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Status: {step.status}</p>
                          {step.timestamp && <p>Time: {new Date(step.timestamp).toLocaleTimeString()}</p>}
                        </TooltipContent>
                      </Tooltip>
                    )) || <p className="text-muted-foreground text-sm">No chain status available.</p>}
                  </div>
                  <ScrollBar orientation="horizontal" />
                </ScrollArea>
              </TooltipProvider>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Logs</CardTitle>
            </CardHeader>
            <CardContent>
              {artist.logs?.length > 0 ? (
                /* ScrollArea for Logs Table */
                <ScrollArea className="w-full whitespace-nowrap">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[180px]">Timestamp</TableHead>
                        <TableHead className="w-[80px]">Level</TableHead>
                        <TableHead>Message</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {artist.logs.map((log, index) => (
                        <TableRow key={index}>
                          <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <Badge variant={log.level === 'ERROR' ? 'destructive' : log.level === 'WARN' ? 'secondary' : 'outline'}>
                              {log.level}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-xs whitespace-normal">{log.message}</TableCell> {/* Allow message wrap */}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <ScrollBar orientation="horizontal" />
                </ScrollArea>
              ) : (
                <p className="text-muted-foreground text-sm">No logs available for this artist.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Artist configuration options will go here (e.g., prompt details, API keys, model choices).</p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Chat Tab */}
        <TabsContent value="chat" className="mt-4">
          <ChatWindow artistId={artist.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ArtistDetailPage;

