from celery.schedules import crontab

from nanotools.common.config import app_config


broker_url = app_config['celery_broker']
timezone = 'Asia/Shanghai'
task_serializer = 'json'
accept_content = ['json']
task_ignore_result = True
result_serializer = 'json'

task_create_missing_queues = True
worker_max_tasks_per_child = 10
task_default_queue = 'default'

beat_schedule = {
    'perid_proc': {
        'task': 'nanotools.tasks.test.perid_proc',
        'schedule': 5,
    },
}

task_routes = {
    'nanotools.tasks.test.perid_proc': {'queue': 'default'},
    'nanotools.tasks.test.proc': {'queue': 'default'},
    'nanotools.tasks.walking.*': {'queue': 'default'},
}

imports = (
    'nanotools.tasks.test',
)
