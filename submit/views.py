from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from downloader.helpers import submit_type_is_valid, err
from downloader.operations import submit_url, submit_upload

# Create your views here.
@login_required
def submit(request):
    if request.method == "POST":
        submit_type = request.POST.get('submit_type')
        if not submit_type_is_valid(submit_type):
            return err(request, 'Invalid submit type selected.')
        
        if 'url' == submit_type:
            return submit_url(request)
        if 'upload' == submit_type:
            return submit_upload(request)
    
    return render(request, 'submit/index.html', None)