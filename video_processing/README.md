# Video Processing Module

This module contains components related to analyzing audio tracks and selecting appropriate video content.

## Components

*   `audio_analyzer.py`: Implements the `analyze_audio` function which uses the `librosa` library to extract features like tempo (BPM), overall energy (RMS), and duration from an audio file. These features are intended to inform video selection.
*   `video_selector.py`: Implements the `select_stock_videos` function. This function takes audio features (tempo, energy) and descriptive keywords as input. It uses the `pexels_client` (from `api_clients`) to search for relevant stock videos on Pexels based on the keywords. It then applies a basic filtering logic based on video duration (aiming for videos slightly longer than the audio duration) and potentially other factors (though current implementation is simple). It returns a list of selected video URLs.

## Usage

1.  Ensure `ffmpeg` and `librosa` are installed.
2.  Call `analyze_audio(audio_path)` to get features.
3.  Instantiate `PexelsClient` with an API key.
4.  Instantiate `VideoSelector` with the `PexelsClient` instance.
5.  Call `video_selector.select_stock_videos(audio_features, keywords)` to get a list of suitable video URLs.

## Dependencies

*   `librosa`
*   `numpy`
*   `ffmpeg` (system dependency)
*   `../api_clients/pexels_client.py`

## Future Enhancements

*   More sophisticated audio analysis (e.g., mood detection, genre classification, beat tracking).
*   More advanced video selection logic (e.g., matching video mood/pace to audio features, scene detection).
*   Integration with other stock video providers.

