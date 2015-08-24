from django.forms import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from pc.models import Computer_Labs
from rooms.models import Tutorial_Room, Activity
from rooms.serializer import Activity_Serializer
from django.utils.timezone import utc
import datetime
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.conf import settings
from django.contrib import messages
from core import utilities
from users.models import RoomHistory
from itertools import chain


def index(request):
    return render(request, 'core/index.html')


def autocompleteAPI(request):
    if request.method == 'GET':
        # get the user from session
        user = request.user

        # create the list of computer labs in the format needed for the autocompleter
        data = Computer_Labs.objects.all()
        labs = []
        already_favourited = user.pc_favourites.all()

        for lab in data:
            if len(already_favourited.filter(id=lab.id)) == 0:
                # check if lab is open
                is_open = utilities.isOpen(lab)

                # get opening hours
                open_hours = utilities.getOpenHours(lab)
                open_hour = open_hours['openHour']
                closing_hour = open_hours['closingHour']

                # if no opening hours, then set them to 'n/a'
                if open_hour is None:
                    open_hour = 'n/a'
                    closing_hour = 'n/a'

                labs.append(
                    {
                        'value': lab.name,
                        'data': {
                            'id': lab.id,
                            'free': lab.free,
                            'seats': lab.seats,
                            'ratio': lab.ratio,
                            'openHour': open_hour,
                            'closingHour': closing_hour,
                            'isOpen': is_open,
                            'longitude': lab.longitude,
                            'latitude': lab.latitude
                        }
                    }
                )

        # create the list of tutorial rooms in the format needed for the autocompleter
        data = Tutorial_Room.objects.all()
        rooms = []
        already_favourited = user.room_favourites.all()

        # ROOMS AVAILABLE NOW (OPEN AND NOT BOOKED):

        rooms_available_now = data.filter(availability='availableNow')

        # ROOMS NOT AVAILABLE NOW (CLOSED OR BOOKED):

        rooms_not_available_now = data.filter(availability='notAvailable')

        # LOCALLY ALLOCATED OPEN ROOMS:

        rooms_open_locally_allocated = data.filter(availability='localAvailable')

        # ADD to rooms : list of dictionaries.
        for room in rooms_available_now:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                # get opening hours
                open_hours = utilities.getOpenHours(room)
                open_hour = open_hours['openHour']
                closing_hour = open_hours['closingHour']

                if open_hour is None:
                    open_hour = 'n/a'
                    closing_hour = 'n/a'

                rooms.append(
                    {'value': room.room_name + ', ' + room.building_name,
                     'data': {
                         'room_name': room.room_name,
                         'building_name': room.building_name,
                         'locationId': room.locationId,
                         'capacity': room.capacity,
                         'pc': room.pc,
                         'printer': room.printer,
                         'projector': room.projector,
                         'whiteboard': room.whiteboard,
                         'blackboard': room.blackboard,
                         'isOpen': True,
                         'openHour': open_hour,
                         'closingHour': closing_hour,
                         'locally_allocated': False,
                         'availability': 'availableNow',
                         'availableFor': room.availableFor
                     }
                     }
                )

        for room in rooms_not_available_now:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                # get isOpen variable
                is_open = utilities.isOpen(room)

                # get opening hours
                open_hours = utilities.getOpenHours(room)
                open_hour = open_hours['openHour']
                closing_hour = open_hours['closingHour']

                if open_hour is None:
                    open_hour = 'n/a'
                    closing_hour = 'n/a'

                rooms.append(
                    {'value': room.room_name + ', ' + room.building_name,
                     'data': {
                         'room_name': room.room_name,
                         'building_name': room.building_name,
                         'locationId': room.locationId,
                         'capacity': room.capacity,
                         'pc': room.pc,
                         'printer': room.printer,
                         'projector': room.projector,
                         'whiteboard': room.whiteboard,
                         'blackboard': room.blackboard,
                         'isOpen': is_open,
                         'openHour': open_hour,
                         'closingHour': closing_hour,
                         'locally_allocated': room.locally_allocated,
                         'availability': 'notAvailable',
                         'unavailableFor': room.unavailableFor
                     }
                     }
                )

        for room in rooms_open_locally_allocated:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                # get opening hours
                open_hours = utilities.getOpenHours(room)
                open_hour = open_hours['openHour']
                closing_hour = open_hours['closingHour']

                if open_hour is None:
                    open_hour = 'n/a'
                    closing_hour = 'n/a'

                rooms.append(
                    {'value': room.room_name + ', ' + room.building_name,
                     'data': {
                         'room_name': room.room_name,
                         'building_name': room.building_name,
                         'locationId': room.locationId,
                         'capacity': room.capacity,
                         'pc': room.pc,
                         'printer': room.printer,
                         'projector': room.projector,
                         'whiteboard': room.whiteboard,
                         'blackboard': room.blackboard,
                         'openHour': open_hour,
                         'closingHour': closing_hour,
                         'locally_allocated': room.locally_allocated,
                         'availability': 'localAvailable'
                     }
                     }
                )

        return utilities.JSONResponse({'labs': labs, 'rooms': rooms})


def like(request):
    if request.method == 'POST':
        # if the user liked a computer lab:
        if 'pc_id' in request.POST.keys():
            # get the id of the liked computer lab
            pc_id = request.POST['pc_id']
            # get the user from session
            user = request.user

            # get whether the user was liking or unliking the lab
            pcLikedByUser = request.POST['pcLikedByUser']

            # get PC that was liked
            pc = Computer_Labs.objects.get(id=pc_id)

            # if the pc has not been liked before, add it to likes, otherwise, remove it.
            if pcLikedByUser == 'false':
                user.pc_favourites.add(pc)
            else:
                user.pc_favourites.remove(pc)

            return HttpResponse(status=200)
        # if the user liked a tutorial room
        else:
            locationId = request.POST['locationId']

            # get the user from session
            user = request.user

            # get whether the user was liking or unliking the room
            roomLikedByUser = request.POST['roomLikedByUser']

            # get room that was liked
            room = Tutorial_Room.objects.get(locationId=locationId)
            # if the room has not been liked before, add it to likes, otherwise, remove it.
            if roomLikedByUser == 'false':
                user.room_favourites.add(room)
            else:
                user.room_favourites.remove(room)

            return HttpResponse(status=200)


# get the list of all this users favourites
@login_required
def get_all_favourites(request):
    if request.method == 'GET':

        # get user
        user = request.user

        # if getting favourite labs:
        if request.GET['type'] == 'labs':
            # make a list of all this users favourite labs' ids
            users_favourites = user.pc_favourites.all().values_list('id', flat=True)

            # return this list as a JSON response
            return utilities.JSONResponse(users_favourites)

        # if getting favourite rooms
        else:
            # make a list of all this users favourite rooms' ids
            users_favourites = user.room_favourites.all().values_list('locationId', flat=True)

            # return this list as a JSON response
            return utilities.JSONResponse(users_favourites)


def get_panel(request):
    if request.method == 'POST':
        # if getting a lab
        if 'pc_id' in request.POST:
            lab_id = escape(request.POST['pc_id'])
            lab = Computer_Labs.objects.filter(id=lab_id)[0]
            if utilities.isOpen(lab):
                lab.openInfo = 'open'
            else:
                lab.openInfo = 'closed'
            return render(request, 'users/labPanel.html', {'fav': lab})
        else:
            room_id = escape(request.POST['locationId'])
            room = Tutorial_Room.objects.filter(locationId=room_id)[0]
            return render(request, 'users/roomPanel.html', {'fav': room})




@login_required
def favourites(request):
    """
    The view for the favourites page. It renders a template that displays
    all the favourites of current user in the following categories:
    PC: currently open, currently closed
    Rooms: 1) Rooms Available Now (currently open and not booked),
           2) Rooms not available (Either closed or currently booked of both locally and globally allocated rooms),
           3) locally allocated and currently open.
    """
    # get the user from the request
    user = request.user

    # ==== FOR PCs ====

    # get all PCs liked by the user.
    pc_favourites = user.pc_favourites.all()
    # get all currently open PC-labs and sort according to ratio
    pc_favourites_open = utilities.excludeClosedLocations(pc_favourites)
    pc_favourites_open = utilities.sortPCLabByEmptiness(pc_favourites_open)
    for lab in pc_favourites_open:
        lab.openInfo = 'open'
    # get all currently closed PC-labs
    pc_favourites_closed = utilities.get_currently_closed_locations(pc_favourites)
    for lab in pc_favourites_closed:
        lab.openInfo = 'closed'

    all_labs = chain(pc_favourites_open, pc_favourites_closed)

    # ==== FOR ROOMs ====

    # get all rooms liked by the user.
    room_favourites = user.room_favourites.all()

    # ROOMS AVAILABLE NOW (OPEN AND NOT BOOKED):

    rooms_available_now = room_favourites.filter(availability='availableNow')

    # ROOMS NOT AVAILABLE NOW (CLOSED OR BOOKED):

    rooms_not_available_now = room_favourites.filter(availability='notAvailable')

    # ROOMS UNKNOWN AVAILABILITY (OPEN AND LOCALLY ALLOCATED)

    rooms_open_locally_allocated = room_favourites.filter(availability='localAvailable')

    all_rooms = chain(rooms_available_now, rooms_open_locally_allocated)
    all_rooms = chain(all_rooms, rooms_not_available_now)
    context = {'pc_favourites': all_labs,
               'room_favourites': all_rooms,
               'user': user}

    return render(request, 'users/favourites.html', context)


@login_required
def history(request):
    """
    Returns a template with all rooms the user has booked.
    :param request:
    :return:
    """
    # get user
    user = request.user

    # for the ajax post requests from the room suggester.
    if request.method == 'POST':

        clearAll = request.POST['clearAll']

        # if clearing the user's history
        if clearAll == 'true':
            # get history for user
            room_history = RoomHistory.objects.filter(user=user)
            # delete them all
            room_history.delete()

        # otherwise, the request is about adding a room to history
        else:
            # get the locationId of the room in question.
            locationId = request.POST['locationId']

            # look up room
            room = Tutorial_Room.objects.get(locationId=locationId)

            # get time now
            now = datetime.datetime.now().replace(tzinfo=utc)

            # create new RoomHistory obj
            room_history = RoomHistory(room=room, user=user, booked_at_time=now)
            room_history.save()

        return HttpResponse(status=200)

    # Otherwise, the request is get, return a template that displays history
    else:
        # get history for user
        historical_bookings = RoomHistory.objects.filter(user=user)
        to_return = []
        for historicalBooking in historical_bookings:
            print(model_to_dict(historicalBooking.room))
            this_room = model_to_dict(historicalBooking.room)
            this_room['booked_at_time'] = historicalBooking.booked_at_time
            this_room['his_id'] = historicalBooking.id
            to_return = [this_room] + to_return

        # make context for template
        context = {'roomHis': to_return}

        return render(request, 'users/history.html', context)


def calendar(request):
    """
    Returns json of all the activities of a particular room (given by locationId).
    This is the view for the calendar function.
    :param request:
    :return:
    """
    if request.method == 'GET':
        # get the location id
        locationId = request.GET['locationId']

        # get the room in question
        room = Tutorial_Room.objects.get(locationId=locationId)

        # get the activities for this room
        activities = Activity.objects.filter(tutorialRooms=room)

        # Serialize all the activities
        serializer = Activity_Serializer(activities, many=True)

        # TODO Could add opening hours to fade out the areas that are closed in FullCalendar.

        # return sorted suggestions
        return utilities.JSONResponse(serializer.data)


def logout(request):
    """
    Function to log-out the current user. In production, this means also resetting the CoSign cookie.
    """
    if request.user.is_authenticated():

        # in production logging requires logging out of EASE as well as the application session.
        if settings.ENV_TYPE == 'production':

            ease_url = "http://www-test.ease.ed.ac.uk/logout.cgi"
            response = django_logout(request,
                                     next_page=ease_url)

            # overwrite the cosign-cookie and set it to an expired date.
            response.set_cookie('cosign-eucsCosigntest-www-test.book.is.ed.ac.uk',
                                expires="Thu, 01 Jan 2000 00:00:00 GMT",
                                path="/")

        # in development things are more simple - just logout and redirect to frontpage.
        elif settings.ENV_TYPE == 'development':
            response = django_logout(request, next_page='/')

        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Unknown environment")
            response = HttpResponseRedirect('/')
        return response

    # the user was not already logged in. This case is common to both ENVIRONMENTS.
    else:
        messages.add_message(request,
                             messages.ERROR,
                             "Cannot logout when user is not logged in")
        return HttpResponseRedirect('/')


def register(request):
    """
    A view that allow users to register with a username and a password. As we do not
    allow this service in production, we initially check if the settings environment is development or not.
    """

    if settings.ENV_TYPE == 'development':

        # A boolean value for telling the template whether the registration was successful.
        # Set to False initially. Code changes value to True when registration succeeds.
        registered = False

        # If it's a HTTP POST, we're interested in processing form data.
        if request.method == 'POST':
            # Attempt to grab information from the raw form information.
            # Note that we make use of both UserForm and UserProfileForm.
            user_form = UserForm(data=request.POST)

            # If the two forms are valid...
            if user_form.is_valid():
                # Save the user's form data to the database.
                user = user_form.save()

                # Now we hash the password with the set_password method.
                # Once hashed, we can update the user object.
                user.set_password(user.password)
                user.save()

                # # Now sort out the UserProfile instance.
                # # Since we need to set the user attribute ourselves, we set commit=False.
                # # This delays saving the model until we're ready to avoid integrity problems.
                # profile = profile_form.save(commit=False)
                # profile.user = user
                #
                # # Now we save the UserProfile model instance.
                # profile.save()

                # Update our variable to tell the template registration was successful.
                registered = True

            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            # They'll also be shown to the user.
            else:
                print(user_form.errors)

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        else:
            user_form = UserForm()

        # Render the template depending on the context.
        return render(request,
                      'auth/registration.html',
                      {'user_form': user_form,
                       'registered': registered})
    # if settings are production settings, then no registration is allowed.
    else:
        messages.add_message(request,
                             messages.ERROR,
                             "No registration allowed outside of EASE")
        return HttpResponseRedirect('/')


def login(request):
    if settings.ENV_TYPE == 'development':
        if request.user.is_authenticated():
            messages.add_message(request,
                                 messages.ERROR,
                                 "Can't login more than one user at the same time")
            return HttpResponseRedirect('/')

        # user is not authenticated and should be logged in
        else:
            response = django_login(request, template_name='auth/login.html')
            return response

    # the view is called in production - this is now allowed!
    else:
        messages.add_message(request,
                             messages.ERROR,
                             "Not possible to circumvent EASE!")
        return HttpResponseRedirect('/')
