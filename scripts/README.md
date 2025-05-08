### 4. Fetch assets before teaser generation

Run asset fetching script to download required visuals:

```bash
python scripts/fetch_assets.py
```

- First attempts to fetch from Pixabay.
- If missing, tries Pexels.
- If still missing, uses MixKit fallback links.

Requires setting up a .env file with:

```
PIXABAY_KEY=your_pixabay_api_key
PEXELS_KEY=your_pexels_api_key
```

Assets are saved under:

```
/assets/raw_sources/{visual_keyword}/
```
