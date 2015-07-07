import requests
from rooms.models import Room_Feed, Building_Feed, Bookable_Room
from time import clock


def update_room_table():
    """
    The function makes a request to the bookable rooms feeds and uses that data to populate the Room_Feed table.
    :return: void
    """

    objectsToSave=[]
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
            for suitability in room['suitabilities']:
                suit = ""
                for x in list(suitability.values()):
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
            # initialize variables
            campus_id = ''
            campus_name = ''
            zone_search_id = zoneId
            # search through all the zones until you find the root
            while campus_id == '':
                for zone in zones:
                    # if this is the zone you're searching for
                    if zone['zoneId'] == zone_search_id:
                        # if this zone is a campus, not just a building, save this as the room's campus
                        if zone['parentZoneId'] is None:
                            campus_id = zone['zoneId']
                            campus_name = zone['name'][1:]
                        else:
                            # if this zone is the parent but not a campus, find out which campus the parent is on
                            zone_search_id = zone['parentZoneId']

            # save the object
            obj = Room_Feed(locationId=locationId,
                            abbreviation=abbreviation,
                            room_name=room_name,
                            description=description,
                            capacity=capacity,
                            pc=pc,
                            whiteboard=whiteboard,
                            blackboard=blackboard,
                            projector=projector,
                            locally_allocated=locally_allocated,
                            printer=printer,
                            zoneId=zoneId,
                            campus_id=campus_id,
                            campus_name=campus_name)
            objectsToSave.append(obj)
    # clear the database
    Room_Feed.objects.all().delete()
    # store all the the rooms in the database
    Room_Feed.objects.bulk_create(objectsToSave)
    return 'success'


def update_building_table():
    """
    This function makes a call to the building feed and updates the values of the Building_Feed table.
    :return: void
    """

    objectsToSave=[]
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php"
    buildings = requests.get(url)

    # extra keys which aren't in the lat/long database, despite the fact their buildings are
    # yeah, the database is kind of rubbish
    # I had to look these ones up manually, so it's not a complete list,
    # nor obviously will it update, but it's a wee help at least
    extra_keys = {
        'Main University Library': '0224',
        'Business School': '0226',
        'Grant Institute': '0633',
        'Sanderson Building': '0601',
        'Michael Swann Building': '0612',
        'Dugald Stewart Building': '0283',
        "Chancellor's Building": '2701',
        'Chrystal MacMillan Building': '0112',
        'Buccleuch Place': '0261',  # 31 Buccleuch Place
        # 'Buccleuch Place':'0244', # 14 Buccleuch Place
        # 'Buccleuch Place':'0252', # 22 Buccleuch Place
        # 'Buccleuch Place':'0254', # 24 Buccleuch Place
        # 'Buccleuch Place':'0245', # 15 Buccleuch Place
        # 'Buccleuch Place':'0247', # 17 Buccleuch Place
        # 'Buccleuch Place':'0260', # 30 Buccleuch Place
        'William Rankine Building': '0668',
        'C.H. Waddington Building': '0670',
        'Hospital for Small Animals': '0719',
        "Old Surgeons' Hall": '0313',
        'Old Infirmary (Geography)': '0311',
        'Evolution House': '0424',
        'Hunter Building': '0423',
        'ECA Main Building': '0421',
        'ECA Architecture Building': '0422',
        'Economics, School of': '0260',
        'Noreen and Kenneth Murray Library': '0636',
        'Darwin Learning & Teaching Cluster': '0611',
        'George Square (1)': '0208',  # 1 George Square
        'George Square (2-15)': '0209',  # 7 George Square
        'George Square (16-27)': '0214',  # 16-20 George Square
        # 'George Square (16-27)':'0219', # 21 George Square
        'Medical Education Centre': '2305',
        "St Leonard's Land": '0564'
    }

    for building in buildings.json()["locations"]:
        # we're not interested in buildings without an abbreviation
        # as this is the only way we can link the tables with Room_Feed.
        if 'abbreviation' in building.keys() or ('name' in building.keys() and building['name'] in extra_keys):
            longitude = float(building["longitude"])
            latitude = float(building["latitude"])
            building_name = building["name"]
            if 'abbreviation' in building.keys():
                abbreviation = building["abbreviation"][:4]
            else:
                abbreviation = extra_keys[building['name']]

                # Rename any buildings called strange things in the lat/long database
                if (building['name']) == 'George Square (2-15)':
                    building_name = '7 George Square (Psychology Building)'
                elif (building['name']) == 'Main University Library':
                    building_name = 'Main Library'
                elif (building['name']) == 'George Square (1)':
                    building_name = '1 George Square'
                elif (building['name']) == 'Economics, School of':
                    building_name = '30 Buccleuch Place (School of Economics)'
                # Two George Square buildings both use the same 'building' name, the lat/long database is kinda rubbish.
                elif (building['name']) == 'George Square (16-27)':
                    # save second object
                    obj = Building_Feed(abbreviation='0219',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='21 George Square')
                    objectsToSave.append(obj)
                    # continue with first object
                    building_name = '16-20 George Square'
                # Think that's bad?  There's loads of Buccleuch Place ones all using the same lat/long...
                elif (building['name']) == 'Buccleuch Place':
                    # save second object
                    obj = Building_Feed(abbreviation='0244',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='14 Buccleuch Place')
                    objectsToSave.append(obj)
                    # save third object
                    obj = Building_Feed(abbreviation='0252',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='22 Buccleuch Place')
                    objectsToSave.append(obj)
                    # save fourth object
                    obj = Building_Feed(abbreviation='0254',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='24 Buccleuch Place')
                    objectsToSave.append(obj)
                    # save fifth object
                    obj = Building_Feed(abbreviation='0245',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='15 Buccleuch Place')
                    objectsToSave.append(obj)
                    # save sixth object
                    obj = Building_Feed(abbreviation='0247',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='17 Buccleuch Place')
                    objectsToSave.append(obj)
                    # continue with first object
                    building_name = '31 Buccleuch Place'

            # save object
            obj = Building_Feed(abbreviation=abbreviation,
                                longitude=longitude,
                                latitude=latitude,
                                building_name=building_name)
            objectsToSave.append(obj)

    # Remove any duplicates from the database, such as the Noreen and Kenneth Murray Library which is in the feed twice
    # WARNING: O(n^2) efficiency!  For now, the constants are small enough that it's not a problem though.
    seen=[]
    for obj in objectsToSave:
        if obj.abbreviation in seen:
            objectsToSave.remove(obj)
        else:
            seen.append(obj.abbreviation)

    # clear the database
    Building_Feed.objects.all().delete()
    # store all the buildings in the database
    Building_Feed.objects.bulk_create(objectsToSave)
    return 'success'


def merge_room_building():
    """
    The function merges the two tables Room_Feed and Building_Feed into a single table: Bookable_Room
    :return: void
    """
    objectsToSave=[]
    for results in Room_Feed.objects.raw("SELECT * FROM rooms_room_feed R,rooms_building_feed B"
                                         " WHERE R.abbreviation=B.abbreviation"):
        obj = Bookable_Room(abbreviation=results.abbreviation,
                            locationId=results.locationId,
                            room_name=results.room_name,
                            description=results.description,
                            capacity=results.capacity,
                            pc=results.pc,
                            printer=results.printer,
                            whiteboard=results.whiteboard,
                            blackboard=results.blackboard,
                            projector=results.projector,
                            locally_allocated=results.locally_allocated,
                            zoneId=results.zoneId,
                            longitude=results.longitude,
                            latitude=results.latitude,
                            building_name=results.building_name,
                            campus_id=results.campus_id,
                            campus_name=results.campus_name)
        objectsToSave.append(obj)

    # clear the database
    Bookable_Room.objects.all().delete()
    # store all the rooms in the database
    Bookable_Room.objects.bulk_create(objectsToSave)
    return 'success'

''' For testing:
def printTime(message):
    global timer
    print(message + ': ' + str(float(int((clock() - timer) * 1000)) / 1000) + 's')
    timer = clock()
'''