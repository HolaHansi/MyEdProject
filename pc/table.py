import xml.etree.ElementTree as ET
from .models import PC_Space
from rooms.models import Building_Feed
import requests


def get_data():
    r = requests.get(url='http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML')
    root = ET.fromstring(r.content)

    for child in root:
        if 'location' in child.keys():
            ratio = round(int(child.attrib['free'])/int(child.attrib['seats']), 3)
            location = child.attrib['location']
            free = int(child.attrib['free'])
            seats = int(child.attrib['seats'])
            group = child.attrib['group']
            longitude = 0.0
            latitude = 0.0

            # get building :
            for building in Building_Feed.objects.all():
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

