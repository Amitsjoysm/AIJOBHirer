"""Queue service using RQ for background job processing"""
from rq import Queue
from rq.job import Job
from services.redis_service import RedisService
from typing import Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)

class QueueService:
    """Service for managing background job queues"""
    
    def __init__(self):
        redis_service = RedisService()
        self.redis_client = redis_service.client
        
        # Create different queues for different job types
        self.email_queue = Queue('email', connection=self.redis_client)
        self.resume_queue = Queue('resume', connection=self.redis_client)
        self.calendar_queue = Queue('calendar', connection=self.redis_client)
        self.report_queue = Queue('report', connection=self.redis_client)
        self.default_queue = Queue('default', connection=self.redis_client)
        
        logger.info("Queue service initialized with multiple queues")
    
    def enqueue_email_job(self, func: Callable, *args, **kwargs) -> Optional[Job]:
        """Enqueue an email job"""
        try:
            job = self.email_queue.enqueue(func, *args, **kwargs, job_timeout='5m')
            logger.info(f"Email job enqueued: {job.id}")
            return job
        except Exception as e:
            logger.error(f"Failed to enqueue email job: {str(e)}")
            return None
    
    def enqueue_resume_job(self, func: Callable, *args, **kwargs) -> Optional[Job]:
        """Enqueue a resume processing job"""
        try:
            job = self.resume_queue.enqueue(func, *args, **kwargs, job_timeout='10m')
            logger.info(f"Resume job enqueued: {job.id}")
            return job
        except Exception as e:
            logger.error(f"Failed to enqueue resume job: {str(e)}")
            return None
    
    def enqueue_calendar_job(self, func: Callable, *args, **kwargs) -> Optional[Job]:
        """Enqueue a calendar operation job"""
        try:
            job = self.calendar_queue.enqueue(func, *args, **kwargs, job_timeout='5m')
            logger.info(f"Calendar job enqueued: {job.id}")
            return job
        except Exception as e:
            logger.error(f"Failed to enqueue calendar job: {str(e)}")
            return None
    
    def enqueue_report_job(self, func: Callable, *args, **kwargs) -> Optional[Job]:
        """Enqueue a report generation job"""
        try:
            job = self.report_queue.enqueue(func, *args, **kwargs, job_timeout='15m')
            logger.info(f"Report job enqueued: {job.id}")
            return job
        except Exception as e:
            logger.error(f"Failed to enqueue report job: {str(e)}")
            return None
    
    def enqueue_job(self, func: Callable, *args, **kwargs) -> Optional[Job]:
        """Enqueue a job to default queue"""
        try:
            job = self.default_queue.enqueue(func, *args, **kwargs, job_timeout='10m')
            logger.info(f"Default job enqueued: {job.id}")
            return job
        except Exception as e:
            logger.error(f"Failed to enqueue job: {str(e)}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get status of a job"""
        try:
            job = Job.fetch(job_id, connection=self.redis_client)
            return job.get_status()
        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            return None
    
    def get_job_result(self, job_id: str) -> Any:
        """Get result of a completed job"""
        try:
            job = Job.fetch(job_id, connection=self.redis_client)
            return job.result if job.is_finished else None
        except Exception as e:
            logger.error(f"Failed to get job result: {str(e)}")
            return None
