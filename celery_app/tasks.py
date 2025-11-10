"""
Common Celery tasks for SEW-TRACK project.
"""

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, name='celery_app.tasks.example_task')
def example_task(self, param: str) -> dict:
    """
    Example task to demonstrate Celery functionality.
    
    Args:
        param: Example parameter
        
    Returns:
        Dictionary with task results
    """
    logger.info(f'Starting example_task with param: {param}')
    
    try:
        # Simulate some work
        result = {'status': 'success', 'param': param}
        logger.info(f'Completed example_task: {result}')
        return result
    except Exception as exc:
        logger.error(f'Task failed: {exc}')
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(name='celery_app.tasks.cleanup_old_records')
def cleanup_old_records() -> dict:
    """
    Periodic task to cleanup old records.
    
    This task can be scheduled using django-celery-beat.
    """
    logger.info('Starting cleanup_old_records task')
    
    # Add cleanup logic here
    deleted_count = 0
    
    logger.info(f'Cleanup completed. Deleted {deleted_count} records')
    return {'status': 'success', 'deleted_count': deleted_count}


@shared_task(name='celery_app.tasks.send_notification')
def send_notification(user_id: str, message: str) -> dict:
    """
    Task to send notifications to users.
    
    Args:
        user_id: User ID to send notification to
        message: Notification message
        
    Returns:
        Dictionary with task results
    """
    logger.info(f'Sending notification to user {user_id}')
    
    # Add notification logic here
    
    return {'status': 'success', 'user_id': user_id}

