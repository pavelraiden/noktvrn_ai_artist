# Suno AI API Integration

## Official API Link
[Suno AI API Documentation](https://docs.aimlapi.com/)

## Overview
Suno AI provides an API for generating music tracks using artificial intelligence. The API allows developers to create original songs by providing lyrics, style parameters, and other musical attributes.

## Main Endpoints Used

### Generate Song
```
POST https://api.suno.ai/v1/generate
```
Used to generate a new song based on provided parameters.

### Check Generation Status
```
GET https://api.suno.ai/v1/generations/{generation_id}
```
Used to check the status of a song generation request.

### List Generations
```
GET https://api.suno.ai/v1/generations
```
Used to list all previous generation requests.

## Authentication Method
Authentication is done via an API key provided in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

The API key should be stored in the `.env` file as `SUNO_API_KEY`.

## Usage Limitations
- Rate limits apply based on subscription tier
- Free tier: Limited number of generations per day
- Paid tiers: Higher generation limits and priority processing
- Commercial use allowed for generated content (check latest terms)
- No redistribution of the API or direct API access

## Example Basic Request

```python
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SUNO_API_KEY')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'prompt': 'A futuristic electronic track with pulsing synths',
    'lyrics': 'Neon lights in the digital sky\nWe\'re floating through a world so high\nElectronic dreams in virtual space\nMoving at a different pace',
    'style': 'electronic',
    'tempo': 'medium',
    'mood': 'energetic',
    'title': 'Digital Dreams'
}

# Generate song
response = requests.post('https://api.suno.ai/v1/generate', headers=headers, json=data)

if response.status_code == 202:  # Accepted
    generation_data = response.json()
    generation_id = generation_data['id']
    print(f"Generation started with ID: {generation_id}")
    
    # Poll for completion
    while True:
        status_response = requests.get(
            f'https://api.suno.ai/v1/generations/{generation_id}',
            headers=headers
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data['status']
            
            if status == 'completed':
                print("Song generation completed!")
                download_url = status_data['download_url']
                print(f"Download URL: {download_url}")
                
                # Download the song
                song_response = requests.get(download_url)
                with open('generated_song.mp3', 'wb') as f:
                    f.write(song_response.content)
                print("Song downloaded as 'generated_song.mp3'")
                break
            elif status == 'failed':
                print("Song generation failed")
                print(status_data.get('error', 'Unknown error'))
                break
            else:
                print(f"Status: {status}, progress: {status_data.get('progress', 'unknown')}%")
                time.sleep(10)  # Wait 10 seconds before checking again
        else:
            print(f"Error checking status: {status_response.status_code}")
            print(status_response.text)
            break
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Integration Notes for Our Project

### Implementation Location
The Suno AI integration is primarily implemented in:
- `/scripts/artist_gen/suno_song_generator.py`

### Usage in Our System
In our AI Artist Creation and Management System, the Suno AI API is used to:

1. Generate original music tracks based on artist profiles
2. Create songs that match the artist's style, genre, and lyrical themes
3. Produce high-quality audio content for music videos and releases

### Best Practices
- Generate prompts based on artist profile attributes
- Use consistent style parameters for a cohesive artist sound
- Implement proper error handling and retry logic
- Store generated songs in the artist's directory structure
- Track generation history for each artist

### Error Handling
Our implementation includes handling for:
- Rate limiting
- Authentication failures
- Generation failures
- Network issues
- Timeout handling for long-running generations

### Testing
The API integration can be tested using:
```bash
python -m scripts.api_test --api suno
```

## Important Considerations
- Song generation can take several minutes to complete
- Implement asynchronous processing for production use
- API keys should never be committed to the repository
- Monitor usage to avoid hitting rate limits
- Consider implementing a queue system for multiple generation requests
- Store generated songs with proper metadata for future reference
