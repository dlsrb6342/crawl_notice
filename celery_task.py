from celery import Celery
from datetime import timedelta
from celery.task import periodic_task
from crawl_notice import crawl_notice


app = Celery('celery_tasks', broker='redis://:password@hostname/dbnumber')

@periodic_task(run_every=timedelta(hours=4))
def start_crawl():
    crawl_notice()
    return
