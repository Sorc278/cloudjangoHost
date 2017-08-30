import json

from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

#from cloudjangohost.lastSeenMiddleware.models import LastSeen
from .models import ChatMessage

# Create your views here.
@login_required
def get_users_online(request):
    # lastSeens = LastSeen.objects.filter(when__gte=timezone.now() - timezone.timedelta(minutes=1))
    json_dict = {}
    # i = 0
    # for lastSeen in lastSeens:
    #     json_dict[i] = lastSeen.user.username
    #     i += 1
    return JsonResponse(json_dict)

@login_required
def get_chat(request):
    lastID = int(request.POST.get('lastID'))
    if lastID == None:
        return redirect('home:homepage')
    
    if lastID == -1:
        messages = ChatMessage.objects.filter(when__gte=timezone.now() - timezone.timedelta(minutes=30)).order_by('when')
    else:
        lastMessageSent = ChatMessage.objects.get(pk=lastID)
        if lastMessageSent == None:
            return redirect('home:homepage')
        messages = ChatMessage.objects.filter(when__gt=lastMessageSent.when).order_by('when')

    returnID = messages.last().id if messages.last() else lastID
    
    msg_dict = {}
    i = 0
    for message in messages:
        msg_dict[i] = {
            'username': message.user.username,
            'time': message.when.strftime("%m-%d %H:%M:%S"),
            'message': message.message,
        }
        i += 1
    
    json_dict = {'lastID': returnID, 'msg': msg_dict}
    return JsonResponse(json_dict)
    
@login_required
def post_message(request):
    message = request.POST.get('message')
    
    if message:
        ChatMessage(user=request.user, message=message).save()
    return HttpResponse()