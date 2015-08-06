from celery import task
from pc.table import get_pc_data
from rooms.table import update_room_table, update_building_hours, update_building_table, merge_room_building, \
    get_activities
from core.utilities import update_status_rooms

# rebuild the database, including checking for any new rooms or labs
@task
def repopulate_all_tables():
    update_building_table()
    print('Buildings saved')
    update_building_hours()
    print('building hours updated')
    update_room_table()
    print('Rooms saved')
    merge_room_building()
    print('Rooms merged')
    get_activities()
    print('Activities merged')
    get_pc_data()
    print('PC labs saved')


# refresh the availability of all the rooms
@task
def refresh_availability():
    get_pc_data()
    print('PC availability refreshed')
    get_activities()
    print('Activities merged')
    update_status_rooms()
    print('Room Status Updated')