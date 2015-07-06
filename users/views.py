from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pc.models import PC_Space
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from pc.models import PC_Space
from rooms.models import Bookable_Room
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import login, authenticate


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



def like(request):
    if request.method == 'POST':
        # check if the like request pertains to a pc:
        try:
            # get the id of liked pc space
            pc_id = request.POST['pc_id']
            # get the user from session
            user = request.user


            # get pcLikedByUser variable (boolean)
            pcLikedByUser = request.POST['pcLikedByUser']

            # get PC that was liked
            pc = PC_Space.objects.get(id=pc_id)

            # if the pc has not been liked before, add it to likes, otherwise, remove it.
            if pcLikedByUser == 'false':
                user.pc_favourites.add(pc)
            else:
                user.pc_favourites.remove(pc)

            return HttpResponse(status=200)
        except:
            locationId = request.POST['locationId']

            # get the user from session
            user = request.user

            # get pcLikedByUser variable (boolean)
            roomLikedByUser = request.POST['roomLikedByUser']

            # get room that was liked
            room = Bookable_Room.objects.get(locationId=locationId)
            # if the room has not been liked before, add it to likes, otherwise, remove it.
            if roomLikedByUser == 'false':
                user.room_favourites.add(room)
            else:
                user.room_favourites.remove(room)

            return HttpResponse(status=200)


    # the GET branch is for obtaining the likedByUser variable for a particular room or pc.
    if request.method == 'GET':
        # for PC request try:
        try:
            # get the pc in question
            pc_id = request.GET['pc_id']

            #get user
            user = request.user

            # if the pc is already liked by user, then assign true to pcLikedByUser
            try:
                user.pc_favourites.get(id=pc_id)
                pcLikedByUser = 'true'
            except:
                pcLikedByUser = 'false'

            return JSONResponse(pcLikedByUser)

        # for Room requests
        except:
            # get the room in question
            locationId = request.GET['locationId']

            print('reached')
            #get userprofile
            user = request.user

            # if the room is already liked by user, then assign true to pcLikedByUser
            print('reached')
            try:
                user.room_favourites.get(locationId=locationId)
                roomLikedByUser = 'true'
            except:
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





def register(request):

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
             'registered': registered} )

#
# @login_required
# def entry(request):
#     if request.method == 'POST':
#         form = EntryForm(request.POST)
#         if form.is_valid():
#             entry = form.save(commit=False)
#             entry.moderator = request.user
#             print(entry.moderator)
#             entry.save()
#             return HttpResponseRedirect('/')
#     else:
#         form = EntryForm()
#     return render(request, 'users/entry.html', {'form': form, 'user': request.user})