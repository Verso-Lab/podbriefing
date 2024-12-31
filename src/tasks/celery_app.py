from celery import Celery
import os

# Get Redis URL from environment or use default
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'podbriefing',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'src.tasks.download',
        'src.tasks.analyze'
    ]
)

# Optional configuration
celery_app.conf.update(
    result_expires=3600,  # Results expire in 1 hour
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
