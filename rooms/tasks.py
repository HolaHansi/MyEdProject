from celery import task
from .table import update_room_table, update_building_table, merge_room_building


@task
def get_data():
    update_room_table()
    print('Rooms saved')
    update_building_table()
    print('Buildings saved')
    merge_room_building()
    return 'successfully updated database'
