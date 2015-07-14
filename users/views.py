from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from pc.models import Computer_Labs
from rooms.models import Tutorial_Room
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.views import login as django_login
from django.conf import settings
from django.contrib import messages


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def index(request):
    return render(request, 'users/index.html')


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
                labs.append(
                    {'value': lab.name,
                     'data': {
                         'id': lab.id,
                         'free': lab.free,
                         'seats': lab.seats,
                         'ratio': lab.ratio
                     }
                     }
                )

        # create the list of tutorial rooms in the format needed for the autocompleter
        data = Tutorial_Room.objects.all()
        rooms = []
        already_favourited = user.room_favourites.all()
        for room in data:
            if len(already_favourited.filter(locationId=room.locationId)) == 0:
                rooms.append(
                    {'value': room.room_name + ', ' + room.building_name,
                     'data': {
                         'room_name': room.room_name,
                         'building_name': room.building_name,
                         'id': room.locationId,
                         'pc': room.pc,
                         'printer': room.printer,
                         'projector': room.projector,
                         'whiteboard': room.whiteboard,
                         'blackboard': room.blackboard
                     }
                     }
                )

        return JSONResponse({'labs': labs, 'rooms': rooms})


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

            return JSONResponse(pcLikedByUser)

        # for Room requests
        else:
            # get the room in question
            locationId = request.GET['locationId']

            # get userprofile
            user = request.user

            # if the room is already liked by user, then assign true to pcLikedByUser
            try:
                user.room_favourites.get(locationId=locationId)
                roomLikedByUser = 'true'
            except ObjectDoesNotExist:
                roomLikedByUser = 'false'

            return JSONResponse(roomLikedByUser)


@login_required
def favourites(request):
    user = request.user
    pc_favourites = user.pc_favourites.all()
    room_favourites = user.room_favourites.all()
    context = {'pc_favourites': pc_favourites,
               'room_favourites': room_favourites,
               'user': user}
    return render(request, 'users/favourites.html', context)


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
