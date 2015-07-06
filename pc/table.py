import xml.etree.ElementTree as ET
from .models import PC_Space, Building_PC
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

def get_building_data():
    """
    This function makes a call to the building feed and updates the values of the Building_Feed table.
    :return: void
    """
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php"
    buildings = requests.get(url)

    # for each building in the feed:
    for building in buildings.json()["locations"]:
        # if it has a name:
        if 'name' in building.keys():
            # get the useful fields
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
                location_name = convertBuildingName(location)
                # for each building,
                for building in Building_PC.objects.all():
                    # merge the two databases as best we can based on building name
                    if building.name in location_name:
                        longitude = building.longitude
                        latitude = building.latitude
                        continue
                # if you didn't manage to find a building associated with this room, try what we've hard coded instead
                if latitude==0.0:
                    if 'Holland House' in location:
                        latitude=55.938027
                        longitude=-3.169087
                    elif 'High School Yards Lab' in location:
                        latitude=55.948633
                        longitude=-3.184002
                    else:
                        print('ERROR: Unable to get coordinates of '+location)
                        sendMail(location)

                obj = PC_Space(location=location,
                    free=free,
                    seats=seats,
                    group=group,
                    ratio=ratio,
                    longitude=longitude,
                    latitude=latitude)

                obj.save()

    return 'successfully updated database'

# takes the building name as used in the open access feed and converts it to the format used in the locations feed
# input: name (string) - the name of the building as used by the open access feed
# output: string - the name of the building as used by the locations feed
def convertBuildingName(location):
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

# sends an email alert to bring the error to the attention of the admins so that it can be fixed
# input: location (string): the location which couldn't be loaded
def sendMail(location):
    fromaddr = "book.ed.alerts@gmail.com"
    toaddr = "s1337523@sms.ed.ac.uk" #TODO: send to someone appropriate
    # load the password from the secret json file
    with open('secrets.json') as f:
        secrets = json.load(f)
    password=secrets["GMAIL_PASSWORD"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Alert"

    body = ("Error in book.ed app: new location added which couldn't be matched to a building from the location database at http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php.  \n\nUnknown location: "+location+"\n\nTo fix this, first check if this location is in fact in the buildings database, under a different name.  If so, add this case to convertBuildingName (in /pc/table.py), matching its name from the PC usage database (http://labmonitor.ucs.ed.ac.uk/myed/index.cfm?fuseaction=XML) and returning the name as it's stored in the buildings database.  If the building is not present in the buildings database at all, look up the building on Google Maps or similar to get its coordinates, then enter them manually in get_pc_data() (in /pc/table.py).  \n\nThis is an automated message.  To turn off alerts, go to /pc/table.py and remove the line 'sendMail(location)' from get_pc_data().")
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
