# API Integration Testing Guide

## Overview

This document provides detailed information about the API integrations in the AI Artist Creation and Management System and how to test them. The system integrates with several external APIs to generate music, fetch video assets, and create visual content for AI artists.

## Supported APIs

The system currently integrates with the following external APIs:

1. **Suno AI** - For music generation
2. **Pixabay** - For video asset collection
3. **Pexels** - For video asset collection
4. **OpenAI** - For text generation (not covered in this testing guide)
5. **Leonardo.ai** - For image generation (not covered in this testing guide)

## API Testing Script

The repository includes a comprehensive API testing script located at `scripts/api_test.py`. This script allows you to verify that your API keys are correctly configured and that the system can successfully communicate with the external APIs.

### Usage

```bash
# Test all APIs
python -m scripts.api_test --api all

# Test specific API
python -m scripts.api_test --api suno
python -m scripts.api_test --api pixabay
python -m scripts.api_test --api pexels
```

### Test Results

The script will output detailed results for each API test, including:

- Success/failure status
- Error messages (if any)
- Sample response data
- URLs of fetched assets (for video APIs)

Example successful output:
```
==================================================
API TEST RESULTS: SUCCESS
==================================================
Message: Successfully fetched all 3 videos from Pexels
==================================================
{
  "status": "success",
  "message": "Successfully fetched all 3 videos from Pexels",
  "results": {
    "retro car race": {
      "status": "success",
      "url": "https://videos.pexels.com/video-files/5514241/5514241-hd_1280_720_24fps.mp4"
    },
    "city night lights": {
      "status": "success",
      "url": "https://videos.pexels.com/video-files/31815964/13555630_360_640_30fps.mp4"
    },
    "electronic music concert": {
      "status": "success",
      "url": "https://videos.pexels.com/video-files/1692701/1692701-hd_1280_720_30fps.mp4"
    }
  }
}
```

## API Configuration

All API keys are stored in the `.env` file. You can use the provided `.env.example` file as a template:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your API keys:

```
# External API keys
SUNO_API_KEY=your_suno_api_key
PIXABAY_KEY=your_pixabay_api_key
PEXELS_KEY=your_pexels_api_key
```

## API Integration Details

### Suno AI Integration

The Suno AI integration is used to generate music tracks for AI artists. The integration is implemented in `scripts/artist_gen/suno_song_generator.py`.

Key features:
- Song generation based on artist profile
- Support for genre specification
- Ability to wait for generation completion
- Automatic download of generated songs

### Pixabay Integration

The Pixabay integration is used to fetch video assets for music videos. The integration is implemented in `scripts/video_gen/fetch_assets.py`.

Key features:
- Search for videos based on keywords
- Filter by resolution and duration
- Download videos for use in music video generation

### Pexels Integration

The Pexels integration provides an alternative source for video assets. The integration is implemented in `scripts/video_gen/fetch_assets.py`.

Key features:
- Search for videos based on keywords
- Filter by resolution and duration
- Download videos for use in music video generation

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your API keys are correctly entered in the `.env` file
   - Check that there are no extra spaces or characters in the API keys
   - Verify that your API keys are still valid and have not expired

2. **Rate Limiting**
   - Some APIs have rate limits that may cause temporary failures
   - If you encounter a rate limit error, wait a few minutes before trying again

3. **Network Issues**
   - Ensure your system has internet connectivity
   - Check if your network blocks any of the API endpoints

### Logging

The system uses Python's logging module to provide detailed information about API interactions. Logs are stored in the `logs/` directory:

- `logs/suno_api.log` - Logs for Suno AI interactions
- `logs/video_assets.log` - Logs for Pixabay and Pexels interactions

Examining these logs can provide additional information when troubleshooting API issues.

## Adding New API Integrations

When adding new API integrations to the system, follow these guidelines:

1. Create a dedicated module for the API integration
2. Add the API key to `.env.example` and update documentation
3. Implement proper error handling and logging
4. Add tests for the new API integration
5. Update this documentation with details about the new integration

For more information on contributing to the project, see the [Contribution Guide](../CONTRIBUTION_GUIDE.md).
