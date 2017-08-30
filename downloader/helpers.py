import requests, mimetypes

from django.shortcuts import render

from managers.imageManager import image_types, image_mimes, image_mimes_to_ext

boards = [1, 2, 3, 4]
allowed_submit_types = ['url', 'youtube', 'upload']
priorities = ['Low', 'High']

#utility
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
def send_head(url):
    response = requests.head(url, headers=headers)
    return response
    
def send_get(url):
    response = requests.get(url, stream=True, headers=headers)
    return response

#validity checkers
def board_is_valid(board):
    return board in boards
    
def url_is_valid(url):#more like url exists...
    return len(url) > 0
    
def submit_type_is_valid(submit_type):
    return submit_type in allowed_submit_types
    
def priority_is_valid(priority):
    return priority in priorities

#mimes, extensions
def get_mime_from_url(url):
    return send_head(url).headers['content-type']

#other
def get_size_from_url(url):
    size = send_get(url).headers['Content-length']
    if not isinstance( size, int ):
        return 0
    return size
    
def get_priority(size):
    priority = 'Low' if 64000000 < size else 'High' #64MB
    return priority
    
#errors
def err(request, msg): 
    return render(request, 'submit/index.html', { 'err': msg })