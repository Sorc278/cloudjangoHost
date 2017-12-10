import random

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

from storage.sizes import get_sizes_list_human
from .models import Quote, ApiKey
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
    
def get_user_by_api_key(key):
    try:
        return ApiKey.objects.get(key=key).user
    except:
        return None