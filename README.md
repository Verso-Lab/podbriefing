# Podcast Newsletter Generator

A Streamlit app that analyzes podcasts and generates sharp, insider-style briefings.

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Install ffmpeg (required for audio processing):
- Mac: `brew install ffmpeg`
- Ubuntu: `sudo apt-get install ffmpeg`
- Windows: Download from https://ffmpeg.org/download.html

## Running Locally

```bash
streamlit run podcast_streamlit.py
```

## Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your GitHub repository
4. Add your `GEMINI_API_KEY` in the Streamlit Cloud secrets management
5. Deploy! 