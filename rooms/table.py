import requests
from rooms.models import Room_Feed, Building_Feed, Bookable_Room

def get_names(listOfDicts):
    names = ""

def update_room_table():
    """
    The function makes a request to the bookablerooms feeds and updates the fields in
    the Room_Feed table.
    :return: void
    """

    rooms = requests.get("http://nightside.is.ed.ac.uk:8080/locations").json()
    zones = requests.get('http://nightside.is.ed.ac.uk:8080/zones/').json()
    # save each bookable room:
    for room in rooms:
        if 'locationId' in room.keys():
            # save the basic details
            locationId = room['locationId']
            abbreviation = room['host_key'][:4]
            room_name = room['name']
            description = room['description']
            capacity = int(room['capacity'])
            zoneId = room['zoneId']

            # initialize suitability values
            whiteboard = False
            pc = False
            projector = False
            blackboard = False
            locally_allocated = False
            printer = False
            # save the suitabilities
            for dict in room['suitabilities']:
                suit = ""
                for x in list(dict.values()):
                    suit += str(x)

                if 'Printing' in suit:
                    printer = True
                if 'Whiteboard' in suit:
                    whiteboard = True
                if 'Locally Allocated' in suit:
                    locally_allocated = True
                if 'PC' in suit or 'Computer Lab' in description:
                    pc = True
                if 'Projector' in suit:
                    projector = True
                if 'Blackboard' in suit:
                    blackboard = True

            # look up what campus the room is on:
            #initialize variables
            campus_id=''
            campus_name=''
            zoneSearchId=zoneId
            # search through all the zones until you find the root
            while campus_id=='':
                for zone in zones:
                    # if this is the zone you're searching for
                    if zone['zoneId'] == zoneSearchId :
                        # if this zone is a campus, not just a building, save this as the room's campus
                        if zone['parentZoneId'] is None:
                            campus_id=zone['zoneId']
                            campus_name=zone['name'][1:]
                        else:
                        # if this zone is the parent but not a campus, find out which campus the parent is on
                            zoneSearchId=zone['parentZoneId']

            # save the object
            obj = Room_Feed(locationId=locationId,
                        abbreviation = abbreviation,
                        room_name = room_name,
                        description = description,
                        capacity = capacity,
                        pc = pc,
                        whiteboard = whiteboard,
                        blackboard = blackboard,
                        projector = projector,
                        locally_allocated = locally_allocated,
                        printer = printer,
                        zoneId = zoneId,
                        campus_id = campus_id,
                        campus_name = campus_name)

            obj.save()

    return 'success'


    # for room in rooms.json()["locations"]:
    #     #declare attributes
    #     field_building_name = room["room"]["field_building_name"]
    #     title = room["room"]["title"]
    #     capacity = int(room["room"]["Capacity"].replace(" ", ""))
    #     building_host_key = room["room"]["BuildingHostKey"]
    #
    #     #boolean attributes - Checks in room Attributes string
    #     whiteboard = "Whiteboard" in room["room"]["Room Attributes"]
    #     blackboard = "Blackboard" in room["room"]["Room Attributes"]
    #     projector = "Projector" in room["room"]["Room Attributes"]
    #     pc = "PC" in room["room"]["Room Attributes"]
    #
    #     #create object and save to database
    #     obj = Room_Feed(abbreviation=building_host_key,
    #                         field_building_name = field_building_name,
    #                         title = title,
    #                         capacity = capacity,
    #                         pc = pc,
    #                         whiteboard = whiteboard,
    #                         blackboard = blackboard,
    #                         projector = projector)
    #     obj.save()
    # return 'success'


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
            abbreviation = building["abbreviation"][:4]
            longitude = float(building["longitude"])
            latitude = float(building["latitude"])
            building_name = building["name"]

            #create object and save to database
            obj = Building_Feed(abbreviation=abbreviation,
                                 longitude=longitude,
                                 latitude=latitude,
                                 building_name=building_name)
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
                            locationId = results.locationId,
                            room_name = results.room_name,
                            description = results.description,
                            capacity = results.capacity,
                            pc = results.pc,
                            printer = results.printer,
                            whiteboard = results.whiteboard,
                            blackboard = results.blackboard,
                            projector = results.projector,
                            locally_allocated = results.locally_allocated,
                            zoneId = results.zoneId,
                            longitude = results.longitude,
                            latitude = results.latitude,
                            building_name = results.building_name,
                            campus_id = results.campus_id,
                            campus_name = results.campus_name)

        obj.save()
    return 'success'