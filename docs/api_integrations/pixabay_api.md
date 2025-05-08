# Pixabay API Integration

## Official API Link
[Pixabay API Documentation](https://pixabay.com/api/docs/)

## Overview
Pixabay provides a RESTful API that allows developers to search and download royalty-free images, videos, and music. The API is free to use and requires an API key for authentication.

## Main Endpoints Used

### Video Search
```
GET https://pixabay.com/api/videos/
```
Used to search for videos based on keywords and filter by various parameters.

## Authentication Method
Authentication is done via an API key provided as a query parameter:

```
https://pixabay.com/api/videos/?key=YOUR_API_KEY
```

The API key should be stored in the `.env` file as `PIXABAY_KEY`.

## Usage Limitations
- 5,000 requests per hour
- No daily or monthly limit specified
- Commercial use allowed
- No attribution required (but appreciated)
- No redistribution of original files as standalone files

## Example Basic Request

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PIXABAY_KEY')

params = {
    'key': api_key,
    'q': 'electronic music',
    'video_type': 'all',
    'category': 'music',
    'min_width': 1280,
    'min_height': 720,
    'per_page': 10
}

response = requests.get('https://pixabay.com/api/videos/', params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Total hits: {data['totalHits']}")
    
    for video in data['hits']:
        print(f"Video ID: {video['id']}")
        print(f"Tags: {video['tags']}")
        print(f"Duration: {video['duration']} seconds")
        print(f"User: {video['user']}")
        
        # Get the video file with the highest quality
        video_files = [
            video['videos']['large'],
            video['videos']['medium'],
            video['videos']['small'],
            video['videos']['tiny']
        ]
        
        # Sort by resolution (width * height)
        video_files = sorted(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
        
        if video_files:
            print(f"Download URL: {video_files[0]['url']}")
            print(f"Resolution: {video_files[0]['width']}x{video_files[0]['height']}")
        
        print("---")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Integration Notes for Our Project

### Implementation Location
The Pixabay API integration is primarily implemented in:
- `/scripts/video_gen/fetch_assets.py`

### Usage in Our System
In our AI Artist Creation and Management System, the Pixabay API is used to:

1. Fetch video assets for music video generation based on artist profile keywords
2. Create visual content that matches the artist's style and genre
3. Serve as the primary source for video assets, with Pexels as a fallback

### Best Practices
- Use specific, targeted keywords based on artist profile
- Filter by category and video_type for more relevant results
- Implement caching to reduce API calls
- Store downloaded assets in the artist's directory structure

### Error Handling
Our implementation includes handling for:
- Rate limiting
- Authentication failures
- Network issues
- Empty search results

### Testing
The API integration can be tested using:
```bash
python -m scripts.api_test --api pixabay
```

## Important Considerations
- Pixabay has more lenient usage terms than Pexels (no attribution required)
- API keys should never be committed to the repository
- Consider implementing a caching layer to reduce API calls
- Monitor usage to avoid hitting rate limits
- Pixabay offers higher resolution videos than some other free services
