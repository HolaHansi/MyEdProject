from django.db.models import Q
from django.shortcuts import render
from .models import Tutorial_Room
from .serializer import Bookable_Room_Serializer
from core import utilities
import datetime


def index(request):
    """
    The view that returns the frontpage of the rooms' suggester app.
    """
    return render(request, 'rooms/index.html')


def filter_suggestions(request):
    """
    Takes a GET request and returns a list of suggestions based
    on the parameters of the request.
    :param request:
    :return: JSON object
    """
    if request.method == "GET":
        # get all rooms
        data = Tutorial_Room.objects.all()

        # Exclude all rooms that we KNOW are currently closed.
        data = utilities.excludeClosedLocations(data)

        # if searching for bookable spaces...
        if request.GET['bookable'] == 'true':
            data = data.filter(locally_allocated=0)
        # if searching for pc...
        if request.GET['pc'] == 'true':
            data = data.filter(pc='true')
        # if searching for printer...
        if request.GET['printer'] == 'true':
            data = data.filter(printer='true')
        # if searching for whiteboard...
        if request.GET['whiteboard'] == 'true':
            data = data.filter(whiteboard='true')
        # if searching for blackboard...
        if request.GET['blackboard'] == 'true':
            data = data.filter(blackboard='true')
        # if searching for projector...
        if request.GET['projector'] == 'true':
            data = data.filter(projector='true')





        # remove any campuses they didn't select
        campuses_to_remove = request.GET.getlist('campusesUnselected[]')
        # if 'other' needs removed...
        if 'Other' in campuses_to_remove:
            query = Q(campus_name='')
            # remove anything that isn't one of the four main options,
            # but also remove any of the four main options if they've been selected to be removed
            for campus in ['Central', "King's Buildings", "Lauriston", "Holyrood"]:
                if campus not in campuses_to_remove:
                    query = query | Q(campus_name=campus)
            data = data.filter(query)
        # otherwise, just remove any campuses they've selected to be removed
        else:
            for campus in campuses_to_remove:
                data = data.exclude(campus_name=campus)


        # REMEMBER TO IMPLEMENT THIS IN THE JSON FEED!!
        # available_for_hours = request.GET['availableForHours']


        # THIS IS A DUMMY VARIABLE! Remove after test!
        available_for_hours = 3

        data = utilities.filter_out_busy_rooms(data, available_for_hours)

        #
        # # filter all rooms which have an activity that starts before x hours time and ends after now
        # # currently using test times and dates
        #
        # current_time = datetime.datetime.now()
        # wanted_end_time = current_time + datetime.timedelta(hours=available_for_hours)
        #
        #
        # # if an event starts before end time, and ends after currentTime, then the room is
        # # already booked, and should be added to busy_rooms.
        #
        # busy_rooms = data.filter(activity__startTime__lte=wanted_end_time,
        #                          activity__endTime__gte=current_time)
        #
        #
        #
        #
        # # busy_rooms = data.filter(activity__startTime__lt='2015-08-12 ' + str(hr + 1) + ':00:00+0000',
        # #                          activity__endTime__gt='2015-08-12 ' + str(hr) + ':00:00+0000')
        #
        # # now exclude all rooms that are busy from the room suggestions (data)
        # busy_rooms = [x.locationId for x in busy_rooms]
        # data = data.exclude(locationId__in=busy_rooms)


        # if they're currently searching for a building:
        if request.GET['building'] == '':
            # work out how many rooms are available in each building
            building_details = {}
            for room in data:
                if not (room.abbreviation in building_details):
                    building_details[room.abbreviation] = {
                        'abbreviation': room.abbreviation,
                        'rooms': 1,
                        'building_name': room.building_name,
                        'latitude': room.latitude,
                        'longitude': room.longitude,
                        'campus': room.campus_name
                    }
                else:
                    building_details[room.abbreviation]['rooms'] += 1
            # convert it from a JSON of JSONs to a list of JSONs
            building_details = list(building_details.values())
            # if sorting by location
            if request.GET['nearby'] == 'true':
                # get the user's latitude and longitude
                usr_longitude = float(request.GET['longitude'])
                usr_latitude = float(request.GET['latitude'])

                # sort the buildings based on distance from user, closest first
                building_details = utilities.sortBuildingsByDistance(usr_longitude=usr_longitude,
                                                                    usr_latitude=usr_latitude,
                                                                    building_details=building_details)

            # if not sorting by location, sort by number of suitable rooms available
            else:
                building_details = sorted(building_details, key=lambda x: x['rooms'], reverse=True)

            return utilities.JSONResponse(building_details)

        # if they're searching for a room...

        # get only rooms within that building
        data = data.filter(abbreviation=request.GET['building'])

        # sort the rooms based on a simple heuristic function
        data = sorted(data, key=lambda x: utilities.calculate_heuristic(x), reverse=True)

        # return the rooms
        serializer = Bookable_Room_Serializer(data, many=True)

        # FOR TESTING:
        # print('for testing! \n', data)

        # return sorted suggestions
        return utilities.JSONResponse(serializer.data)


# FOR TESTING ONLY!
def testing(hr):
    data = Tutorial_Room.objects.all()

    # filter all rooms which have an activity that starts before x hours time and ends after now
    busy_rooms = data.filter(activity__startTime__lt='2015-08-12 ' + str(hr + 1) + ':00:00+0000',
                             activity__endTime__gt='2015-08-12 ' + str(hr) + ':00:00+0000')
    print("Busy rooms:", busy_rooms.count())
    busy_rooms = [x.locationId for x in busy_rooms]
    data = data.exclude(locationId__in=busy_rooms)
    print("Inefficiently:", data.count())
    data = Tutorial_Room.objects.all()
    data = data.exclude(activity__startTime__lte='2015-08-12 ' + str(hr + 1) + ':00:00+0000',
                        activity__endTime__gte='2015-08-12 ' + str(hr) + ':00:00+0000')
    print("Basic exclude:", data.count())
    data = Tutorial_Room.objects.all()
    data = data.exclude(activity__startTime__lte='2015-08-12 ' + str(hr + 1) + ':00:00+0000').exclude(
        activity__endTime__gte='2015-08-12 ' + str(hr) + ':00:00+0000')
    print("Double exclude:", data.count())
    data = Tutorial_Room.objects.exclude(Q(activity__startTime__lt='2015-08-12 ' + str(hr + 1) + ':00:00+0000') | Q(
        activity__endTime__gt='2015-08-12 ' + str(hr) + ':00:00+0000'))
    print("Fancy exclude:", data.count())
    data = Tutorial_Room.objects.filter(~Q(activity__startTime__lt='2015-08-12 ' + str(hr + 1) + ':00:00+0000') | ~Q(
        activity__endTime__gt='2015-08-12 ' + str(hr) + ':00:00+0000'))
    print("Fancy filter:", data.count())
    # Only 'Inefficiently' works correctly, all the others don't.  No idea why basic exclude doesn't.
