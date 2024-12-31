# PodBriefing Backend

Backend service for analyzing podcasts using Gemini AI and generating briefings.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
# Create .env file
cp .env.example .env
# Add your Gemini API key
```

3. Run development server:
```bash
poetry run uvicorn src.main:app --reload
```

4. Run Celery worker:
```bash
poetry run celery -A src.tasks.celery_app worker --loglevel=info
```

## Project Structure

```
src/
├── api/          # FastAPI routes
├── core/         # Core business logic
├── db/           # Database models and config
└── tasks/        # Celery tasks
```

## Requirements

- Python 3.11+
- Redis (for Celery)
- PostgreSQL
- FFmpeg (for audio processing) 