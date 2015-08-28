from .table import update_room_table, update_building_table, merge_room_building, update_building_hours, get_activities


def get_data():
    update_room_table()
    print('Rooms saved')
    update_building_table()
    print('Buildings saved')
    merge_room_building()
    print('Tutorial Rooms made')
    get_activities()
    print('Activities merged')
    update_building_hours()
    print('building hours updated')
    return 'successfully updated database'
