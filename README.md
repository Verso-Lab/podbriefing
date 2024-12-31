# PodBriefing Backend

Backend service for analyzing podcasts using Gemini AI and generating briefings.

## Requirements

Before starting, make sure you have the following installed:
- Python 3.13
- [Poetry](https://python-poetry.org/docs/#installation) for Python package management
- PostgreSQL 17 (instructions below)
- Redis (for background tasks)

## Setup

### 1. Install Dependencies

Install Python dependencies using Poetry:
```bash
poetry install
```

### 2. Set up PostgreSQL

#### For macOS:
1. Install PostgreSQL 17 using Homebrew:
   ```bash
   brew install postgresql@17
   ```

2. Start the PostgreSQL service:
   ```bash
   brew services start postgresql@17
   ```

3. Create the postgres superuser (one-time setup):
   ```bash
   createuser-17 -s postgres
   ```

4. Create the application database:
   ```bash
   createdb-17 -U postgres podbriefing
   ```

### 3. Environment Setup

1. Create your environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   The other default settings should work as is.

### 4. Initialize Database

Create and apply the database schema:
```bash
# Create the initial migration
poetry run alembic revision --autogenerate -m "initial"

# Apply the migration
poetry run alembic upgrade head
```

### 5. Start the Application

1. Start the development server:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

2. In a separate terminal, start the Celery worker for background tasks:
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

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify PostgreSQL is running:
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Ubuntu
   sudo service postgresql status
   ```

2. Check if the postgres user exists (macOS only):
   ```bash
   # Create the user if it doesn't exist
   createuser-17 -s postgres
   ```

3. Test database connection:
   ```bash
   # macOS
   psql-17 -U postgres -d podbriefing
   
   # Ubuntu
   sudo -u postgres psql -d podbriefing
   ```

4. Common error messages:
   - "role postgres does not exist": Run `createuser-17 -s postgres`
   - "database podbriefing does not exist": Run `createdb-17 -U postgres podbriefing`
   - "connection refused": Make sure PostgreSQL service is running

### Redis Connection Issues

Make sure Redis is running:
```bash
# macOS
brew services list | grep redis

# Ubuntu
sudo service redis status
```