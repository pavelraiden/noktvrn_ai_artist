# Pexels API Integration

## Official API Link
[Pexels API Documentation](https://www.pexels.com/api/documentation/)

## Overview
Pexels provides a RESTful API that allows developers to search and download high-quality stock photos and videos. The API is free to use with attribution and requires an API key for authentication.

## Main Endpoints Used

### Video Search
```
GET https://api.pexels.com/videos/search
```
Used to search for videos based on keywords and filter by various parameters.

### Video Details
```
GET https://api.pexels.com/videos/videos/{id}
```
Used to retrieve detailed information about a specific video.

## Authentication Method
Authentication is done via an API key provided in the request headers:

```
Authorization: YOUR_API_KEY
```

The API key should be stored in the `.env` file as `PEXELS_KEY`.

## Usage Limitations
- 200 requests per hour
- 20,000 requests per month
- Commercial use allowed with attribution
- No redistribution of original files
- No selling of Pexels content

## Example Basic Request

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    'Authorization': os.getenv('PEXELS_KEY')
}

params = {
    'query': 'electronic music',
    'orientation': 'landscape',
    'size': 'medium',
    'per_page': 10
}

response = requests.get('https://api.pexels.com/videos/search', headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    for video in data['videos']:
        print(f"Video ID: {video['id']}")
        print(f"Video URL: {video['url']}")
        print(f"Duration: {video['duration']} seconds")
        
        # Get the video file with the highest quality
        video_files = sorted(video['video_files'], key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
        if video_files:
            print(f"Download URL: {video_files[0]['link']}")
        print("---")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Integration Notes for Our Project

### Implementation Location
The Pexels API integration is primarily implemented in:
- `/scripts/video_gen/fetch_assets.py`

### Usage in Our System
In our AI Artist Creation and Management System, the Pexels API is used to:

1. Fetch video assets for music video generation based on artist profile keywords
2. Create visual content that matches the artist's style and genre
3. Provide fallback video sources when Pixabay doesn't have suitable content

### Best Practices
- Always include proper attribution as required by Pexels
- Implement caching to reduce API calls
- Use specific, targeted keywords based on artist profile
- Implement fallback mechanisms for rate limiting
- Store downloaded assets in the artist's directory structure

### Error Handling
Our implementation includes handling for:
- Rate limiting (429 responses)
- Authentication failures
- Network issues
- Empty search results

### Testing
The API integration can be tested using:
```bash
python -m scripts.api_test --api pexels
```

## Important Considerations
- Pexels content requires attribution in the final videos
- API keys should never be committed to the repository
- Consider implementing a caching layer to reduce API calls
- Monitor usage to avoid hitting rate limits
