from celery_worker import celery
from celery.schedules import crontab

from tasks import send_daily_reminders, send_monthly_report  

celery.conf.beat_schedule = {

    'daily-deadline-reminder': {
        'task':     'tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),    
    },

    'monthly-placement-report': {
        'task':     'tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    },
}

celery.conf.timezone = 'Asia/Kolkata'
