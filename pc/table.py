import xml.etree.ElementTree as ElTree
from .models import Computer_Labs
from rooms.models import Building_Feed
import requests
import re


def get_pc_data():
    r = requests.get(url='http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML')
    root = ElTree.fromstring(r.content)

    for child in root:
        if 'location' in child.keys():
            name = child.attrib['location']
            group = child.attrib['group']
            # remove group from name
            name = process_pc_name(name, group)
            free = int(child.attrib['free'])
            seats = int(child.attrib['seats'])
            id = child.attrib['rid']
            ratio = round(free / seats, 3)
            longitude = 0.0
            latitude = 0.0
            # convert group to campus:
            if group == 'Business School':
                campus = 'Central'
            elif group == 'KB Labs':
                campus = "King's Buildings"
            elif group == 'ECA':
                campus = 'Lauriston'
            elif 'Holyrood' in group:
                campus = 'Holyrood'
            else:
                campus = group

            # the variable opening_hours_available is false by default, and is set to true if opening hours are found.
            opening_hours_available = False

            # for each building,
            for building in Building_Feed.objects.all():
                # get building coordinates and opening-hours.
                if building.building_name in convert_building_name(name):

                    # coordinates:
                    longitude = building.longitude
                    latitude = building.latitude

                    # Opening Hours:
                    try:
                        weekdayOpen = building.open_hours.weekdayOpen
                        weekdayClosed = building.open_hours.weekdayClosed
                        saturdayOpen = building.open_hours.saturdayOpen
                        saturdayClosed = building.open_hours.saturdayClosed
                        sundayOpen = building.open_hours.sundayOpen
                        sundayClosed = building.open_hours.sundayClosed
                        opening_hours_available = True
                    except:
                        opening_hours_available = False

                    # a building was matched, hence no need to continue for-loop.
                    break

            # if you didn't manage to find a building associated with this room, try what we've hard coded instead
            if latitude == 0.0:
                if 'Holland House' in name:
                    latitude = 55.938027
                    longitude = -3.169087
                elif 'High School Yards Lab' in name:
                    latitude = 55.948633
                    longitude = -3.184002
                elif 'Mary Bruck' in name:
                    latitude = 55.923024
                    longitude = -3.171045
                    # TODO: update with appropriate coordinates (as of time of writing, it's not on Google Maps)
                else:
                    print('ERROR: Unable to get coordinates of ' + name)
                    send_mail(name)

            obj = Computer_Labs(name=name,
                                free=free,
                                seats=seats,
                                campus=campus,
                                ratio=ratio,
                                longitude=longitude,
                                latitude=latitude,
                                id=id)

            if opening_hours_available:
                obj.weekdayOpen = weekdayOpen
                obj.weekdayClosed = weekdayClosed
                obj.saturdayOpen = saturdayOpen
                obj.saturdayClosed = saturdayClosed
                obj.sundayOpen = sundayOpen
                obj.sundayClosed = sundayClosed

            obj.save()

    return 'successfully updated database'


# takes the building name as used in the open access feed and converts it to the format used in the locations feed
# input: name (string) - the name of the building as used by the open access feed
# output: string - the name of the building as used by the locations feed
def convert_building_name(location):
    # Hugh Robson Bldg -> Hugh Robson Building
    if 'Hugh' in location:
        return 'Hugh Robson Building'
    # Teviot House -> Teviot Row House
    if 'Teviot' in location:
        return 'Teviot Row House'
    # ECA Evolution -> Evolution House
    if 'Evolution' in location:
        return 'Evolution House'
    # JCMB -> James Clerk Maxwell Building
    if 'JCMB' in location:
        return 'James Clerk Maxwell Building'
    # KB Centre -> King's Buildings Centre
    if 'KB Centre' in location:
        return "King's Buildings Centre"
    # Murray Library -> Noreen and Kenneth Murray Library
    if 'Murray' in location:
        return 'Noreen and Kenneth Murray Library'
    return location


def process_pc_name(name, campus):
    # Processes the name of the open access study space to make it more human readable
    regex = re.compile(campus + '( - )? ?', re.IGNORECASE)
    to_return = re.sub(regex, '', name)
    if campus == 'Business School':
        to_return = 'Business School - ' + to_return
    return to_return


# sends an alert to bring the error to the attention of the admins so that it can be fixed
# input: location (string): the location which couldn't be loaded
def send_mail(location):
    message = (
        "Error in book.ed app: new location added which couldn't be matched to a building from the location database "
        "at http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php.  \n\n"
        "Unknown location: " + location +
        "\n\nTo fix this, first check if this location is in fact in the buildings database, under a different name.  "
        "If so, add this case to convert_building_name() (in /pc/table.py), matching its name from the PC usage "
        "database (http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML) and returning the name as it's stored "
        "in the buildings database.  If the building is not present in the buildings database at all, look up the "
        "building on Google Maps or similar to get its coordinates, then enter them manually in get_pc_data() "
        "(in /pc/table.py).  "
        "\n\nThis is an automated message.  To turn off alerts, go to /pc/table.py and remove the line "
        "'sendMail(location)' from get_pc_data().")
    # TODO: send message to admin
    return message
