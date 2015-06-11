import requests
from rooms.models import Room_Feed
from rooms.models import Building_Feed
from rooms.models import Bookable_Room


def update_room_table():
    """
    The function makes a request to the bookablerooms feed and updates the fields in
    the Room_Feed table.
    :return: void
    """
    url = "http://www-test.bookablerooms.is.ed.ac.uk/json_feed" #larger bookables
    rooms = requests.get(url)


    for room in rooms.json()["locations"]:
        #declare attributes
        field_building_name = room["room"]["field_building_name"]
        title = room["room"]["title"]
        capacity = int(room["room"]["Capacity"].replace(" ", ""))
        building_host_key = room["room"]["BuildingHostKey"]

        #boolean attributes - Checks in room Attributes string
        whiteboard = "Whiteboard" in room["room"]["Room Attributes"]
        blackboard = "Blackboard" in room["room"]["Room Attributes"]
        projector = "Projector" in room["room"]["Room Attributes"]
        pc = "PC" in room["room"]["Room Attributes"]

        #create object and save to database
        obj = Room_Feed(abbreviation=building_host_key,
                            field_building_name = field_building_name,
                            title = title,
                            capacity = capacity,
                            pc = pc,
                            whiteboard = whiteboard,
                            blackboard = blackboard,
                            projector = projector)
        obj.save()
    return 'success'


def update_building_table():
    """
    This function makes a call to the building feed and updates the values of the Building_Feed table.
    :return: void
    """
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php" #smaller lat/long
    buildings = requests.get(url)


    for building in buildings.json()["locations"]:
        # we're not interested in buildings without an abbreviation, as this is a critical component for linking
        # the this tables with Room_Feed.
        if 'abbreviation' in building.keys():
            abbreviation = building["abbreviation"]
            longitude = float(building["longitude"])
            latitude = float(building["latitude"])
            name = building["name"]

            #create object and save to database
            obj = Building_Feed(abbreviation=abbreviation,
                                 longitude=longitude,
                                 latitude=latitude,
                                 name=name)
            obj.save()
    return 'success'

def merge_room_building():
    """
    The function merges the two tables Room_Feed and Building_Feed into a single table: Bookable_Room
    :return: void
    """
    for results in Room_Feed.objects.raw("SELECT * FROM rooms_room_feed R,rooms_building_feed B WHERE R.abbreviation=B.abbreviation"):
        # print(results)
        # print(results.longitude, results.latitude)
        # print()

        obj = Bookable_Room(abbreviation=results.abbreviation,
                             field_building_name = results.field_building_name,
                             title = results.title,
                             capacity = results.capacity,
                             pc = results.pc,
                             whiteboard = results.whiteboard,
                             blackboard = results.blackboard,
                             projector = results.projector,
                             longitude = results.longitude,
                             latitude = results.latitude)
        obj.save()
    return 'success'