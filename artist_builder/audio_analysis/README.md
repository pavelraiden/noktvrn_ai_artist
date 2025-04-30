# Audio Analysis Module

## Overview

This module provides comprehensive functionality for extracting and analyzing musical features from audio files. It plays a crucial role in the AI Artist Creation and Management System by enabling a deeper understanding of musical content, which informs artist evolution, trend analysis, and content generation.

The module uses the `librosa` library for core audio processing and feature extraction, along with `numpy` and `pandas` for data manipulation.

## Components

1.  **`feature_extractor.py`**: Contains the `FeatureExtractor` class responsible for extracting a wide range of features from audio files, including:
    *   **Temporal Features**: Tempo (BPM), beat tracking, onset detection, rhythm patterns.
    *   **Spectral Features**: Spectral centroid, bandwidth, contrast, rolloff, Mel-frequency cepstral coefficients (MFCCs).
    *   **Harmonic Features**: Key and scale detection, chroma features, tonal centroid, harmonic/percussive separation.
    *   **High-Level Features**: RMS energy, zero-crossing rate, spectral flatness, estimated danceability, mood (valence/arousal).

2.  **`style_analyzer.py`**: Contains the `StyleAnalyzer` class for analyzing musical styles based on extracted features. Its capabilities include:
    *   **Genre Classification**: Simple rule-based classification (placeholder for a more advanced model).
    *   **Similarity Calculation**: Computes a similarity score between two tracks based on their features.
    *   **Style Element Identification**: Identifies descriptive elements like tempo class, energy class, mood, complexity, and instrumentation.
    *   **Trend Compatibility Analysis**: Assesses how well a track aligns with a set of trend features.
    *   **Reference Management**: Allows saving features as references for specific styles.

3.  **`trend_analyzer.py`**: Contains the `TrendAnalyzer` class for analyzing musical trends from collections of features. Its capabilities include:
    *   **Trend Identification**: Calculates aggregate statistics (mean, median, distribution) for key features across a collection of tracks.
    *   **Trend Evolution Tracking**: Monitors changes in trend metrics over time.
    *   **Future Trend Prediction**: Simple linear regression-based prediction of future feature values.
    *   **Data Management**: Loading and saving trend data.

4.  **`utils/`**: Contains utility modules:
    *   **`audio_loader.py`**: Functions for loading, preprocessing (trimming silence, normalization), resampling, and segmenting audio files.

5.  **`tests/`**: Contains unit tests for the module components:
    *   **`test_feature_extractor.py`**: Tests for the `FeatureExtractor` class.
    *   **`test_style_analyzer.py`**: Tests for the `StyleAnalyzer` class.
    *   **`test_trend_analyzer.py`**: Tests for the `TrendAnalyzer` class.

## Usage

### Feature Extraction

```python
from artist_builder.audio_analysis.feature_extractor import FeatureExtractor

# Initialize the extractor
extractor = FeatureExtractor()

# Extract features from an audio file
audio_file = "path/to/your/audio.wav"
features = extractor.extract_features(audio_file)

# Access specific features
tempo = features.get("temporal", {}).get("tempo")
energy_level = features.get("high_level", {}).get("energy_level")

print(f"Tempo: {tempo:.2f} BPM")
print(f"Energy Level: {energy_level:.2f}")
```

### Style Analysis

```python
from artist_builder.audio_analysis.style_analyzer import StyleAnalyzer

# Assume 'features1' and 'features2' are extracted feature dictionaries

analyzer = StyleAnalyzer()

# Classify genre
genre_info = analyzer.classify_genre(features1)
print(f"Primary Genre: {genre_info["primary_genre"]}")

# Calculate similarity
similarity = analyzer.calculate_similarity(features1, features2)
print(f"Similarity: {similarity:.2f}")

# Identify style elements
style_elements = analyzer.identify_style_elements(features1)
print(f"Identified Mood: {style_elements.get("mood")}")
```

### Trend Analysis

```python
from artist_builder.audio_analysis.trend_analyzer import TrendAnalyzer

# Assume 'features_collection' is a list of feature dictionaries

trend_analyzer = TrendAnalyzer()

# Identify current trends
current_trends = trend_analyzer.identify_current_trends(features_collection)
print(f"Average Tempo Trend: {current_trends.get("tempo", {}).get("mean"):.2f}")

# Track evolution (assuming history is loaded or built)
trend_analyzer.trend_history = [...] # Load or build history
evolution = trend_analyzer.track_trend_evolution(current_trends)
print(f"Tempo Change Direction: {evolution.get("evolution_analysis", {}).get("tempo", {}).get("change", {}).get("direction")}")

# Predict future trends
predictions = trend_analyzer.predict_future_trends()
print(f"Predicted Tempo (next period): {predictions.get("predictions", {}).get("tempo", [None])[0]}")
```

## Integration

This module integrates with other parts of the AI Artist System:

*   **Artist Builder**: Provides feature data to inform the creation and evolution of AI artists.
*   **Trend Analyzer (Main)**: Feeds detailed audio feature trends into the broader system trend analysis.
*   **Artist Evolution System**: Uses similarity and compatibility analysis to guide artist development.

## Future Enhancements

*   Implement more sophisticated machine learning models for genre and mood classification.
*   Integrate Essentia library for a wider range of features and potentially better performance.
*   Develop feature map visualization tools.
*   Implement more advanced trend prediction models (e.g., ARIMA, LSTM).
*   Add capabilities for analyzing symbolic music data (MIDI).
*   Improve error handling and robustness for diverse audio inputs.

