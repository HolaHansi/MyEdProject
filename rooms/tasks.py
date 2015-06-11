from celery import task
from .table import main, merge

@task
def get_data():
    main()
    merge()
    return 'successfully updated database'

