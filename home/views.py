import random

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def get_CSRF(request):
    api_key = request.GET.get("key");
    user = get_user_by_api_key(api_key)
    if user:
        request.user = user
        return HttpResponse(get_token(request))
    else:
        return HttpResponse("False", status=403)
    
def get_user_by_api_key(key):
    try:
        return ApiKey.objects.get(key=key).user
    except:
        return None