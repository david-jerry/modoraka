from apps.analytics.models import AnalysisData
from config import celery_app
from celery.schedules import crontab

from utils.logger import LOGGER


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Executes every first day of the month in the morning at 7:30 a.m.
    """
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_month=1),
        create_performance_analytics.s(),
    )

@celery_app.task()
def create_performance_analytics():
    try:
        # Your task logic here
        result = AnalysisData.update_analysis_data()
        LOGGER.info('Task executed successfully: %s', result)
    except Exception as e:
        LOGGER.error('Task failed: %s', e, exc_info=True)
