# Project-REMIX: AI-Powered Music Remixing Platform 🎵

An AI-driven platform that allows users to remix music seamlessly using YouTube tracks and state-of-the-art AI models.

## Features

- Search and extract music from YouTube
- Transform songs into different genres (Rock, Electro, Jazz, Hip-Hop, Lo-Fi)
- AI-powered remix generation using MusicGen
- Stem separation with Spleeter
- Original track generation with multiple inspiration sources

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Unix: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Add your YouTube API key to .env
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
project-remix/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── frontend/
├── tests/
├── .env
└── requirements.txt
```
