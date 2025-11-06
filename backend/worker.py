"""RQ Worker for processing background jobs"""
import os
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

from rq import Worker, Queue, Connection
from services.redis_service import RedisService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start RQ worker"""
    redis_service = RedisService()
    redis_conn = redis_service.client
    
    # Listen to multiple queues
    queues = [
        Queue('email', connection=redis_conn),
        Queue('resume', connection=redis_conn),
        Queue('calendar', connection=redis_conn),
        Queue('report', connection=redis_conn),
        Queue('default', connection=redis_conn)
    ]
    
    logger.info("Starting RQ worker...")
    logger.info(f"Listening to queues: {[q.name for q in queues]}")
    
    with Connection(redis_conn):
        worker = Worker(queues, name='hireflow-worker')
        worker.work()

if __name__ == '__main__':
    main()
