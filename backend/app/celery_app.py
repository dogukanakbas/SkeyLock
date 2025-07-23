from celery import Celery
from celery.schedules import crontab
import os

from .core.config import settings

# Create Celery instance
celery_app = Celery(
    "iot_security",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.scanning_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.billing_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    # Run network discovery every hour
    "network-discovery": {
        "task": "app.tasks.scanning_tasks.discover_network_devices",
        "schedule": crontab(minute=0),  # Every hour
    },
    
    # Generate daily reports
    "daily-reports": {
        "task": "app.tasks.notification_tasks.send_daily_reports",
        "schedule": crontab(hour=8, minute=0),  # 8 AM daily
    },
    
    # Process billing monthly
    "monthly-billing": {
        "task": "app.tasks.billing_tasks.process_monthly_billing",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # 1st of month
    },
    
    # Cleanup old data weekly
    "cleanup-old-data": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_data",
        "schedule": crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
    },
    
    # Health check every 5 minutes
    "health-check": {
        "task": "app.tasks.maintenance_tasks.health_check",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.scanning_tasks.*": {"queue": "scanning"},
    "app.tasks.notification_tasks.*": {"queue": "notifications"},
    "app.tasks.billing_tasks.*": {"queue": "billing"},
    "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
}