from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from pc.models import Computer_Labs
from rooms.models import Tutorial_Room
from django.utils import timezone
import datetime
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.conf import settings
from django.contrib import messages
from core import utilities



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

        now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
        currentTime = now.time().isoformat()
        weekday = now.weekday()


        for lab in data:
            if len(already_favourited.filter(id=lab.id)) == 0:
                # check if lab is open
                isOpen = utilities.isOpen(lab)

                # get opening hours
                openHours = utilities.getOpenHours(lab)
                openHour = openHours['openHour']
                closingHour = openHours['closingHour']

                # if no opening hours, then set them to 'n/a'
                if openHour is None:
                    openHour = 'n/a'
                    closingHour = 'n/a'

                labs.append(
                    {'value': lab.name,
                     'data': {
                         'id': lab.id,
                         'free': lab.free,
                         'seats': lab.seats,
                         'ratio': lab.ratio,
                         'openHour': openHour,
                         'closingHour': closingHour,
                         'isOpen': isOpen,
                         'longitude': lab.longitude,
                         'latitude': lab.latitude
                        }
                     }
                )

        # create the list of tutorial rooms in the format needed for the autocompleter
        data = Tutorial_Room.objects.all()
        rooms = []

        already_favourited = user.room_favourites.all()


        # from users favourites, get all rooms that are locally allocated: we don't know the availability of these.
        rooms_locally_allocated = data.filter(locally_allocated=True)

        # do the same thing for rooms that we know the availability of.
        rooms_globally_allocated = data.filter(locally_allocated=False)

        # rooms currently closed of both globally and locally allocated rooms.
        closed_rooms = utilities.get_currently_closed_locations(data, typeOfSpace='Room')


        # ROOMS AVAILABLE NOW (OPEN AND NOT BOOKED):

        # get all the favourite rooms that we KNOW are available
        # now both in terms of opening hours and activities.
        rooms_not_currently_booked = utilities.filter_out_busy_rooms(data=rooms_globally_allocated, available_for_hours=1)

        # filter out rooms that are also currently closed
        rooms_available_now = utilities.excludeClosedLocations(rooms_not_currently_booked)

        # Now update the available_for field in each of these rooms:
        utilities.available_for_hours(rooms_available_now)


        #ROOMS NOT AVAILABLE NOW (CLOSED OR BOOKED):

        # get all favourite rooms KNOWN to be currently booked
        rooms_currently_booked = utilities.filter_out_avail_rooms(data=rooms_globally_allocated, available_for_hours=1)

        # if a room is either booked or currently closed, then it is not available:
        rooms_not_available_now = closed_rooms | rooms_currently_booked

        utilities.unavailable_till_hours(rooms_not_available_now)


        # LOCALLY ALLOCATED OPEN ROOMS:
        rooms_open_locally_allocated = utilities.excludeClosedLocations(rooms_locally_allocated)



        for room in rooms_available_now:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                # get opening hours
                openHours = utilities.getOpenHours(lab)
                openHour = openHours['openHour']
                closingHour = openHours['closingHour']

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
                         'openHour': openHour,
                         'closingHour': closingHour,
                         'locally_allocated': False,
                         'availability': 'availableNow',
                         'availableFor': room.availableFor
                        }
                     }
                )

        for room in rooms_not_available_now:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                #get isOpen variable
                isOpen = utilities.isOpen(room)

                # get opening hours
                openHours = utilities.getOpenHours(lab)
                openHour = openHours['openHour']
                closingHour = openHours['closingHour']

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
                         'isOpen': isOpen,
                         'openHour': openHour,
                         'closingHour': closingHour,
                         'locally_allocated': room.locally_allocated,
                         'availability': 'notAvailable',
                         'unavailableFor': room.unavailableFor
                        }
                     }
                )

        for room in rooms_open_locally_allocated:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:

                # get opening hours
                openHours = utilities.getOpenHours(lab)
                openHour = openHours['openHour']
                closingHour = openHours['closingHour']

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
                         'openHour': openHour,
                         'closingHour': closingHour,
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

    # the GET branch is for obtaining the likedByUser variable for a particular room or pc.
    if request.method == 'GET':
        # for PC request try:
        if 'pc_id' in request.GET.keys():
            # get the pc in question
            pc_id = request.GET['pc_id']

            # get user
            user = request.user

            # if the pc is already liked by user, then assign true to pcLikedByUser
            try:
                user.pc_favourites.get(id=pc_id)
                pcLikedByUser = 'true'
            except ObjectDoesNotExist:
                pcLikedByUser = 'false'

            return utilities.JSONResponse(pcLikedByUser)

        # for Room requests
        else:
            # get the room in question
            locationId = request.GET['locationId']

            # get user from request
            user = request.user

            # if the room is already liked by user, then assign true to pcLikedByUser
            try:
                user.room_favourites.get(locationId=locationId)
                roomLikedByUser = 'true'
            except ObjectDoesNotExist:
                roomLikedByUser = 'false'

            return utilities.JSONResponse(roomLikedByUser)


@login_required
def favourites(request):
    """
    The view for the favourites page. It renders a template that displays
    all the favourites of current user in the following categories:
    PC: currently open, currently closed
    Rooms: 1) Rooms Available Now (currently open and not booked), 2) Rooms not available (Either closed or currently booked
    of both locally and globally allocated rooms), 3) locally allocated and currently open.
    """
    # get the user from the request
    user = request.user

    # ==== FOR PCs ====

    # get all PCs liked by the user.
    pc_favourites = user.pc_favourites.all()
    # get all currently open PC-labs and sort according to ratio
    pc_favourites_open = utilities.excludeClosedLocations(pc_favourites)
    pc_favourites_open = utilities.sortPCLabByEmptiness(pc_favourites_open)

    # get all currently closed PC-labs and sort according to ratio
    pc_favourites_closed = utilities.get_currently_closed_locations(pc_favourites)
    pc_favourites_closed = utilities.sortPCLabByEmptiness(pc_favourites_closed)

    # ==== FOR ROOMs ====

    # get all rooms liked by the user.
    room_favourites = user.room_favourites.all()

    # from users favourites, get all rooms that are locally allocated: we don't know the availability of these.
    rooms_locally_allocated = room_favourites.filter(locally_allocated=True)

    # do the same thing for rooms that we know the availability of.
    rooms_globally_allocated = room_favourites.filter(locally_allocated=False)

    # rooms currently closed of both globally and locally allocated rooms.
    closed_rooms = utilities.get_currently_closed_locations(room_favourites, typeOfSpace='Room')


    # ROOMS AVAILABLE NOW (OPEN AND NOT BOOKED):

    # get all the favourite rooms that we KNOW are available
    # now both in terms of opening hours and activities.
    rooms_not_currently_booked = utilities.filter_out_busy_rooms(data=rooms_globally_allocated, available_for_hours=1)

    # filter out rooms that are also currently closed
    rooms_available_now = utilities.excludeClosedLocations(rooms_not_currently_booked)

    # Now update the available_for field in each of these rooms:
    utilities.available_for_hours(rooms_available_now)

    #ROOMS NOT AVAILABLE NOW (CLOSED OR BOOKED):

    # get all favourite rooms KNOWN to be currently booked
    rooms_currently_booked = utilities.filter_out_avail_rooms(data=rooms_globally_allocated, available_for_hours=1)

    # if a room is either booked or currently closed, then it is not available:
    rooms_not_available_now = closed_rooms | rooms_currently_booked

    utilities.unavailable_till_hours(rooms_not_available_now)


    #ROOMS UNKNOWN AVAILABILITY (OPEN AND LOCALLY ALLOCATED)

    rooms_open_locally_allocated = utilities.excludeClosedLocations(rooms_locally_allocated)


    context = {'pc_favourites_open': pc_favourites_open,
               'pc_favourites_closed': pc_favourites_closed,
               'rooms_open_locally_allocated': rooms_open_locally_allocated,
               'rooms_available_now': rooms_available_now,
               'rooms_not_available_now': rooms_not_available_now,
               'user': user}

    return render(request, 'users/favourites.html', context)


@login_required
def history(request):
    user = request.user
    pc_history = user.pc_history.all()
    room_history = user.room_history.all()
    context = {'pc_favourites': pc_history,
               'room_favourites': room_history,
               'user': user}
    return render(request, 'users/history.html', context)


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
