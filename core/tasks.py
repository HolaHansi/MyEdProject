from pc.table import get_pc_data
from rooms.table import update_room_table, update_building_hours, update_building_table, merge_room_building, \
    get_activities


# rebuild the whole database
def repopulate_all_tables():
    refresh_locations()
    refresh_availability()


# Check for any new rooms or labs
def refresh_locations():
    update_building_table()
    print('Buildings saved')
    update_building_hours()
    print('Building hours updated')
    update_room_table()
    print('Rooms saved')
    merge_room_building()
    print('Rooms merged')


# refresh the availability of all the rooms
def refresh_availability():
    get_pc_data()
    print('PC availability refreshed')
    get_activities()
    print('Activities merged')
