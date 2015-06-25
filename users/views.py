from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pc.models import PC_Space
from .forms import EntryForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from pc.models import PC_Space
from rest_framework.renderers import JSONRenderer


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
        # get the id of liked pc space
        pc_id = request.POST['pc_id']
        #get the user from session
        user = request.user


        userprofile = UserProfile.objects.get(user=user)

        # get PC that was liked
        pc = PC_Space.objects.get(id=pc_id)

        # add this pc to the favourites list
        userprofile.pc_favourites.add(pc)

    return HttpResponse(status=200)

@login_required
def favourites(request):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    query = userprofile.pc_favourites.all()
    context = {'list_of_favourites': query,
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
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
            'auth/registration.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


@login_required
def entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.moderator = request.user
            print(entry.moderator)
            entry.save()
            return HttpResponseRedirect('/')
    else:
        form = EntryForm()
    return render(request, 'users/entry.html', {'form': form, 'user': request.user})