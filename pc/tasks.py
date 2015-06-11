import requests
import xml.etree.ElementTree as ET
from .models import Room
from celery import task

@task
def get_data():
    r = requests.get(url='http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML')
    root = ET.fromstring(r.content)

    for child in root:
        if 'location' in child.keys():
            ratio = round(int(child.attrib['free'])/int(child.attrib['seats']), 3)
            r = Room(location=child.attrib['location'], free=int(child.attrib['free']), seats=int(child.attrib['seats']), group=child.attrib['group'], ratio=ratio)
            r.save()
    return 'works!'






