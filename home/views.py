import random

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token

from storage.sizes import get_sizes_list_human
from .models import Quote
# Create your views here.

@login_required
def homepage(request):
    return render(request, 'home/main.html', {
        'quote': random.choice(Quote.objects.all())
    })

@login_required
def profile(request):
    context = {
        'g_sizes': get_sizes_list_human()
    }
    return render(request, 'home/profile.html', context)
    
def get_CSRF(request):
    if request.user.is_authenticated():
        return HttpResponse(get_token(request))
    else:
        return HttpResponse("False", status=403)