from celery import task
from pc.table import get_pc_data
from rooms.table import update_room_table, update_building_table, merge_room_building


@task
def repopulate_all_tables():
    update_building_table()
    print('Buildings saved')
    update_room_table()
    print('Rooms saved')
    merge_room_building()
    print('Rooms merged')
    get_pc_data()
    print('PC labs saved')


@task
def refresh_availability():
    get_pc_data()
    print('PC availability refreshed')
