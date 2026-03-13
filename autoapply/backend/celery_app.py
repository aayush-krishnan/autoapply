import os
import logging
from celery import Celery
from celery.schedules import crontab
from config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "autoapply",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
)

# Auto-discover tasks in specific modules
celery_app.autodiscover_tasks(["tasks"])

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "hourly-scrape": {
        "task": "tasks.scrape_jobs_task",
        "schedule": crontab(minute=0), # Every hour
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
