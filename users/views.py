from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pc.models import PC_Space
from .forms import EntryForm
from django.contrib.auth.decorators import login_required



def index(request):
    return render(request, 'users/index.html')


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