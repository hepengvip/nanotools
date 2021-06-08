from nanotools.entry import celery_app


@celery_app.task
def proc(x, y):
    import time
    time.sleep(10)
    return x + y


@celery_app.task
def perid_proc():
    print('perid_proc')
    return 'ok'
