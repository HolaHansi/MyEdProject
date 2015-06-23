import xml.etree.ElementTree as ET
from .models import PC_Space, Building_PC
import requests


def get_building_data():
    """
    This function makes a call to the building feed and updates the values of the Building_Feed table.
    :return: void
    """
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php" #smaller lat/long
    buildings = requests.get(url)


    for building in buildings.json()["locations"]:
        if 'name' in building.keys():
            longitude = float(building["longitude"])
            latitude = float(building["latitude"])
            name = building["name"]

            #create object and save to database
            obj = Building_PC(longitude=longitude,
                                 latitude=latitude,
                                 name=name)
            obj.save()
    return 'success'


def get_pc_data():
    r = requests.get(url='http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML')
    root = ET.fromstring(r.content)

    for child in root:
        if 'location' in child.keys():

            location = child.attrib['location']
            free = int(child.attrib['free'])
            seats = int(child.attrib['seats'])
            ratio = round(free/seats, 3)

            # if object already exists, then update the ratio value.
            if PC_Space.objects.filter(location = child.attrib['location']):
                PC_Space.objects.filter(location=child.attrib['location']).update(free=free)
                PC_Space.objects.filter(location=child.attrib['location']).update(seats=seats)
                PC_Space.objects.filter(location=child.attrib['location']).update(ratio=ratio)

            else:
                group = child.attrib['group']
                longitude = 0.0
                latitude = 0.0

                # get building :
                for building in Building_PC.objects.all():
                    print('location PC: ',location)
                    print('building NAME: ', building.name)
                    if building.name in location:
                        longitude = building.longitude
                        latitude = building.latitude
                        continue

                obj = PC_Space(location=location,
                    free=free,
                    seats=seats,
                    group=group,
                    ratio=ratio,
                    longitude=longitude,
                    latitude=latitude)

                obj.save()

    return 'successfully updated database'
