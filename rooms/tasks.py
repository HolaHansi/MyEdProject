from celery import task
from .table import update_room_table, update_building_table, merge_room_building, add_building_attributes

@task
def get_data():
    update_room_table()
    print('rooms updated')
    update_building_table()
    print('basic buildings updated')
    merge_room_building()
    print('rooms have building properties')
    add_building_attributes()
    print('buildings have room properties')
    return 'successfully updated database'

