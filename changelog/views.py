from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

from .models import ChangelogItem

# Create your views here.
@login_required
def get_changelog(request):
    numToGet = request.POST.get('numToGet')
    if not numToGet:
        return HttpResponse()
    
    items = ChangelogItem.objects.order_by('-priority', '-when')[:int(numToGet)]
    
    json_dict = {}
    i = 0
    for item in items:
        json_dict[i] = {
            'title': '#'+str(item.id)+': '+item.title,
            'time': item.when.strftime("%Y-%m-%d %H:%M:%S"),
            'text': item.text,
        }
        i += 1
    return JsonResponse(json_dict)