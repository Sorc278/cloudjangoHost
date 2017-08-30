from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import InvitationKey

import re

# Create your views here.

def login_page(request):
    #redirect logged in users
    if request.user.is_authenticated():
        return redirect('home:homepage')
    
    #check for redirect after logging in
    next_page = request.GET.get('next')
    if not request.method == "POST":
        return render(request, 'welcome/login.html',
            {
                'next': next_page,
                'err': 'You are not logged in.' if next_page else ''
            })
    
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        if not next_page == None:
            return redirect(next_page)
        return redirect('home:homepage')
    else:
        return render(request, 'welcome/login.html',
            {
                'err': "Invalid username and/or password"
            })
        
def logout_page(request):
    logout(request)
    return redirect('welcome:login')
    
def register(request):
    #if using POST, then try to create new user, else just registration page
    if not request.method == "POST":
        return render(request, 'welcome/register.html', None)
        
    key = request.POST['key']
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password_conf']
    err = []
    
    #invitation key
    if not InvitationKey.objects.filter(key_value=key).exists():
        err.append('No such invitation key.')
    #username
    if len(username) < 4:
        err.append('Username too short.')
    if User.objects.filter(username=username).exists():
        err.append('Username is taken.')
    #password
    hasLower = re.compile("^.*[a-z]+.*$")
    hasUpper = re.compile("^.*[A-Z]+.*$")
    hasNumber = re.compile("^.*[0-9]+.*$")
    if len(password) < 10:
        err.append('Password too short.')
    if not password == password2:
        err.append('Passwords do not match.')
    if not hasLower.match(password):
        err.append('Password has no lowercase letter.')
    if not hasUpper.match(password):
        err.append('Password has no uppercase letter.')
    if not hasNumber.match(password):
        err.append('Password has no number.')
    
    if err:
        return render(request, 'welcome/register.html',
            {
                'err': ' '.join(x.encode('utf-8') for x in err)
            })
    else:
        #try:
        user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
        #except Exception as e:
            #TODO: change to return internal server error 500
            #return render(request, 'welcome/register.html', {'err': e})
        
        InvitationKey.objects.filter(key_value=key).delete()
        return redirect('welcome:login')