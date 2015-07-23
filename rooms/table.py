import re
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import requests
import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials
from rooms.models import Room_Feed, Building_Feed, Tutorial_Room, Activity, Open_Hours
import datetime


def update_room_table():
    """
    The function makes a request to the bookable rooms feeds and uses that data to populate the Room_Feed table.
    :return: void
    """

    buildings_to_save = []
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
            buildings_to_save.append(obj)
    # clear the database
    Room_Feed.objects.all().delete()
    # store all the the rooms in the database
    Room_Feed.objects.bulk_create(buildings_to_save)
    return 'success'



def update_building_table():
    """
    Makes a call to the building feed and populates the Building_Feed table with the relevant data received.
    :return: void
    """

    # get the JSON from the feed
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php"
    buildings = requests.get(url).json()

    # extra keys for some of the buildings which are in the buildings database but don't have their key included
    # yeah, the buildings database is kind of rubbish
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

    # initialize variables
    custom_abbreviation_counter = 0
    buildings_to_save = []

    # for each building in the feed,
    for building in buildings["locations"]:
        # only save it if it has a name, otherwise it's useless to us
        # we're also not interested in buses, car parks, or 'information' (whatever that is)
        if 'name' in building.keys() and (len(building['categories']) == 0 or not
        ('Buses' in building['categories'][0]
         or 'Parking' in building['categories'][0]
         or 'Information' in building['categories'][0])):
            # get the longitude, latitude and building name
            longitude = float(building["longitude"])
            latitude = float(building["latitude"])
            building_name = building["name"]

            # if it's one of the rare entries that actually includes the building's abbreviation, then use that
            if 'abbreviation' in building.keys():
                abbreviation = building["abbreviation"][:4]

            # if it's one of the entries which doesn't have an abbreviation in the database,
            # but does in our hard-coded list, then use that
            elif building['name'] in extra_keys:
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

                # Two George Square buildings both use the same building from the buildings feed, so save both of them
                # (yes, the feed is kind of naff)
                elif (building['name']) == 'George Square (16-27)':
                    # save second object
                    obj = Building_Feed(abbreviation='0219',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='21 George Square')
                    buildings_to_save.append(obj)
                    # continue with first object
                    building_name = '16-20 George Square'
                # Think that's bad?  There's loads of Buccleuch Place ones all using the same building from the feed...
                elif (building['name']) == 'Buccleuch Place':
                    # save second object
                    obj = Building_Feed(abbreviation='0244',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='14 Buccleuch Place')
                    buildings_to_save.append(obj)
                    # save third object
                    obj = Building_Feed(abbreviation='0252',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='22 Buccleuch Place')
                    buildings_to_save.append(obj)
                    # save fourth object
                    obj = Building_Feed(abbreviation='0254',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='24 Buccleuch Place')
                    buildings_to_save.append(obj)
                    # save fifth object
                    obj = Building_Feed(abbreviation='0245',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='15 Buccleuch Place')
                    buildings_to_save.append(obj)
                    # save sixth object
                    obj = Building_Feed(abbreviation='0247',
                                        longitude=longitude,
                                        latitude=latitude,
                                        building_name='17 Buccleuch Place')
                    buildings_to_save.append(obj)
                    # continue with first object
                    building_name = '31 Buccleuch Place'

            # if the building doesn't have an id in either the feed or our hard coded list, just give it a custom id
            # only so it can be in our database, it won't be able to be used to link anything
            else:
                # give it a custom id
                abbreviation = 'z' + str(custom_abbreviation_counter)
                custom_abbreviation_counter += 1

            # save the building
            obj = Building_Feed(abbreviation=abbreviation,
                                longitude=longitude,
                                latitude=latitude,
                                building_name=building_name)
            buildings_to_save.append(obj)



    # Remove any duplicates from the database, such as the Noreen and Kenneth Murray Library which is in the feed twice
    # WARNING: O(n^2) efficiency!  For now, the constants are small enough that it's not a problem though.

    new_buildings_to_save = []
    for obj in buildings_to_save:
        if obj not in new_buildings_to_save:
            new_buildings_to_save.append(obj)

    # clear the database
    Building_Feed.objects.all().delete()
    # store all the buildings in the database
    Building_Feed.objects.bulk_create(new_buildings_to_save)
    return 'success'


def update_building_hours():
    """
    updates/populates the open_hours model in the database.
    :return:
    """
    # get all the opening hour records from spreadsheet and save in dict records.
    records = get_building_hours()
    # loop through records, if a record has an abbreviation, save it to the database
    for record in records:
        abbreviation = record['Building Abbreviation'].replace('"', '')
        if abbreviation != 'n/a':
            try:
                building = Building_Feed.objects.get(abbreviation__exact = abbreviation)
                zoneId = record['Zone_ID']

                # get times as strings, and convert to time objects.

                # weekday times:
                weekdayString = record['Monday_friday_Open']

                # if the place is closed, then set open and closing times to the same value.
                if weekdayString == "Closed":
                    weekdayOpen = datetime.time(0)
                    weekdayClosed = datetime.time(0)

                else:
                    weekdayOpen = datetime.time(int(weekdayString[0:2]), int(weekdayString[2:4]))
                    weekdayClosed = datetime.time(int(weekdayString[5:7]), int(weekdayString[7:9]))

                # saturday times - the same approach as before.
                saturdayString = record['Saturday_Open']

                if saturdayString == "Closed":
                    saturdayOpen = datetime.time(0)
                    saturdayClosed = datetime.time(0)

                else:
                    saturdayOpen = datetime.time(int(weekdayString[0:2]), int(weekdayString[2:4]))
                    saturdayClosed = datetime.time(int(weekdayString[5:7]), int(weekdayString[7:9]))

                # sunday times - the same approach as before.
                sundayString = record['Sunday_Open']

                if sundayString == "Closed":
                    sundayOpen = datetime.time(0)
                    sundayClosed = datetime.time(0)

                else:
                    sundayOpen = datetime.time(int(weekdayString[0:2]), int(weekdayString[2:4]))
                    sundayClosed = datetime.time(int(weekdayString[5:7]), int(weekdayString[7:9]))

                building_name = record['Building Name']

                # make an object for the database.
                obj = Open_Hours(building = building,
                                 abbreviation=abbreviation,
                                 zoneId = zoneId,
                                 weekdayOpen=weekdayOpen,
                                 weekdayClosed=weekdayClosed,
                                 saturdayOpen = saturdayOpen,
                                 saturdayClosed = saturdayClosed,
                                 sundayOpen = sundayOpen,
                                 sundayClosed = sundayClosed,
                                 building_name=building_name)

                obj.save()
            except Exception:
                pass

    return 'success'





def merge_room_building():
    """
    The function merges the two tables Room_Feed and Building_Feed into a single table: Tutorial_Room
    :return: void
    """
    rooms_to_save = {}
    for results in Room_Feed.objects.raw("SELECT * FROM rooms_room_feed R,rooms_building_feed B"
                                         " WHERE R.abbreviation=B.abbreviation"):
        # don't include rooms from the feed which aren't suitable study spaces
        if not ("Theatre style" in results.description or "Lecture Theatre" in results.room_name
                or "Gym" in results.description or 'Games Hall' in results.description
                or 'Gallery' in results.description or 'Function Area' == results.description
                or 'Exhibition Space' == results.description or 'Dance Studio' == results.description
                or 'unavailable' in results.room_name.lower()):
            # TODO: Are these suitable study spaces?
            # and results.description!="Foyer Area"
            # and results.description == "Laboratory: Technical"
            # and "COMPUTER LAB" not in results.description.upper()
            room_name = re.sub(r'^z*', '', results.room_name)



            obj = Tutorial_Room(abbreviation=results.abbreviation,
                                locationId=results.locationId,
                                room_name=room_name,
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
                                campus_name=results.campus_name,
                                capacity = results.capacity
                                )

            # try getting appending opening hours to the room if they exist.
            try:
                openHour = Open_Hours.objects.get(abbreviation__exact=results.abbreviation)
                obj.weekdayOpen = openHour.weekdayOpen
                obj.weekdayClosed = openHour.weekdayClosed
                obj.saturdayOpen = openHour.saturdayOpen
                obj.saturdayClosed = openHour.saturdayClosed
                obj.sundayOpen = openHour.sundayOpen
                obj.sundayClosed = openHour.sundayClosed

            except Exception:
                pass

            rooms_to_save[results.locationId] = obj

    # delete all rooms no longer in the data feed
    Tutorial_Room.objects.exclude(locationId__in=rooms_to_save.keys()).delete()
    # if the database has been reset, save all the data in batch
    data = Tutorial_Room.objects.all()
    if len(data) == 0:
        Tutorial_Room.objects.bulk_create(rooms_to_save.values())
    else:
        # for each room
        for room in rooms_to_save.values():
            # if this room wasn't in the database or has changed, add/update it
            if room not in data:
                room.save()

    return 'success'


def get_activities():
    # get the date in a format usable by the API
    now = datetime.datetime.utcnow()
    current_date = str(now)[:-7].replace(' ', 'T') + '%2B0000'
    tomorrow = str(now + datetime.timedelta(days=1))[:-7].replace(' ', 'T') + '%2B0000'

    # for testing - these dates have activities: SHOULD BE COMMENTED OUT!
    current_date = "2015-08-12T08:00:00%2B0000"
    tomorrow = "2015-08-13T08:00:00%2B0000"

    # get the activities data from the feed
    activities = requests.get(
        "http://nightside.is.ed.ac.uk:8080/activities?start-date-time=" + current_date + '&end-date-time=' + tomorrow
    ).json()
    for activity in activities:
        activity_id = activity['activityId']
        name = activity['name']
        i = 0
        for date in activity['Dates']:
            start_time = date['activityDateTimeId']['startDateTime']
            end_time = date['activityDateTimeId']['endDateTime']
            # the feed uses midnight to mean the midnight at the end of the day,
            # whereas django uses midnight to mean the midnight at the start of the day,
            # so convert it if necessary
            if end_time[11:16] == '00:00':
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S%z')
                end_time = end_time + datetime.timedelta(days=1)
            obj = Activity(activityId=activity_id + '-' + str(i),
                           name=name,
                           startTime=start_time,
                           endTime=end_time)
            obj.save()
            i += 1
            # try to add any tutorial rooms to the database
            for location in activity['locations']:
                try:
                    tut_room = Tutorial_Room.objects.get(locationId=location['locationId'])
                    obj.tutorialRooms.add(tut_room)
                except ObjectDoesNotExist:
                    pass


''' For testing:
def printTime(message):
    from time import clock

    global timer
    print(message + ': ' + str(float(int((clock() - timer) * 1000)) / 1000) + 's')
    timer = clock()
'''


def get_building_hours():
    """
    This function retrieves the opening hours for every building when available
    by calling our google-spreadsheet containing this information.
    :return: a list of dictionaries for each building containing its opening hours.
    """
    # first authenticate with google using oAuth2
    # the credentials are stored in googleCredentialsSecrets.json and are kept out of version control.

    json_key = json.load(open('googleCredentialsSecrets.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], 'utf-8'),
                                                scope)
    gc = gspread.authorize(credentials)

    # open the google spreadsheet containing opening hours
    spreadsheet = gc.open_by_key('173BpkRwPyRXR6fWgKQZ53qUgBSkyUlVWCqklT7K701Y')

    # get a worksheet from the spreadsheet.
    ws = spreadsheet.get_worksheet(0)

    # get all entries (buildings) as python dictionaries
    records = ws.get_all_records()

    return records


