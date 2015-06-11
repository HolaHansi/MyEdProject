import requests
from rooms.models import Room_Feed
from rooms.models import Building_Feed
from rooms.models import Bookable_Room


def main():
	url = "http://www-test.bookablerooms.is.ed.ac.uk/json_feed" #larger bookables
	geo = "http://webproxy.is.ed.ac.uk/web-proxy/maps/portal.php" #smaller lat/long

	r = requests.get(url)
	r2 = requests.get(geo)

	count = 0
	for room in r2.json()["locations"]:
		try:
			abbreviation = room["abbreviation"]
			longitude = float(room["longitude"])
			latitude = float(room["latitude"])
			obj1 = Building_Feed(key=abbreviation, longitude=longitude, latitude=latitude)
			obj1.save()
			count += 1
		except:
			continue

	count = 0
	for dict in r.json()["locations"]:

		field_building_name = dict["room"]["field_building_name"]
		title = dict["room"]["title"]
		capacity = int(dict["room"]["Capacity"].replace(" ", ""))
		building_host_key = int(dict["room"]["BuildingHostKey"])

		whiteboard = "Whiteboard" in dict["room"]["Room Attributes"]
		blackboard = "Blackboard" in dict["room"]["Room Attributes"]
		projector = "Projector" in dict["room"]["Room Attributes"]
		pc = "PC" in dict["room"]["Room Attributes"]

		obj2 = Room_Feed(abbreviation=building_host_key,
							field_building_name = field_building_name,
							title = title,
							capacity = capacity,
							pc = pc,
							whiteboard = whiteboard,
							blackboard = blackboard,
							projector = projector)
		obj2.save()
		count += 1

###no primary key


def merge():

	count = 0
	for results in Room_Feed.objects.raw("SELECT * FROM rooms_room_feed R,rooms_building_feed B WHERE R.abbreviation=B.abbreviation"):
		# print(results)
		# print(results.longitude, results.latitude)
		# print()

		obj3 = Bookable_Room(abbreviation=results.abbreviation,
							 field_building_name = results.field_building_name,
							 title = results.title,
							 capacity = results.capacity,
							 pc = results.pc,
							 whiteboard = results.whiteboard,
							 blackboard = results.blackboard,
							 projector = results.projector,
							 longitude = results.longitude,
							 latitude = results.latitude)
		obj3.save()
		count += 1
