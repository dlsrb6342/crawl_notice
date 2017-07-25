from celery import Celery
from datetime import timedelta
from celery.task import periodic_task
from crawl_notice import crawl_notice
import json


with open('config.json') as json_data_file:
    config = json.load(json_data_file)
redis = config['redis']
redis_url = redis['password'] + '@' + redis['host'] + ':' + redis['port'] + '/' + redis['db']
app = Celery('celery_tasks', broker='redis://:' + redis_url)

@periodic_task(run_every=timedelta(hours=4))
def start_crawl():
    crawl_notice()
    return
