from random import getrandbits

import youtube_dl as ydl

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from cloudjangohost.settings import FILE_UPLOAD_STORE

from .managers.extHelpers import ext_from_string, ext_valid, mime_valid, ext_from_mime, get_extension_type

from .models import Upload
from .helpers import basic_validation, board_is_valid, url_is_valid, priority_is_valid, submit_type_is_valid, is_private
from .helpers import get_meta_from_url, get_priority, get_youtube_format, get_imgur_images, get_imgur_title
from .prep import prepare_upload

def submit_url(request):
    try:
        url, board = basic_validation(request)
        meta = get_meta_from_url(url)
    except Warning:
        raise
    if not (mime_valid(meta["mime"])):
        raise Warning('File type is not yet supported. MIME determined: ' + meta["mime"])
    ext = ext_from_mime(meta["mime"])
    prepare_upload(request.user, '', is_private(request), board, url, ext_from_mime(meta["mime"]), request.POST.get('title'), 'url', get_priority(meta["size"]), meta["size"]).waiting()
    
def submit_upload(request):
    chunkNum = request.POST.get('chunkNum')
    if not chunkNum:
        raise Warning('Chunk number is missing. Are you hacking?')
    try:
        chunkNum = int(chunkNum)
    except:
        raise Warning('Non-integer chunk number received')
    
    #set up the download slot
    if -1 == chunkNum:
        if not board_is_valid(int(request.POST.get('board'))):
            raise Warning('Board is not valid')
        
        extension = ext_from_string(request.POST.get('filename'))
        if not ext_valid(extension):
            raise Warning('File type is not yet supported. Extension determined: ' + extension)
        
        filesize = int(request.POST.get('filesize'))
        priority = get_priority(filesize)
        upload = prepare_upload(request.user, request.POST.get('filename'),  is_private(request),  int(request.POST.get('board')),  '', extension, request.POST.get('title'), 'upload', priority, filesize)
        upload.downloading(0)
        return upload.uploadID
    
    #process sent chunk
    uploadID = request.POST.get('uploadID')
    if not uploadID:
        raise Warning('No upload ID supplied')
    upload = Upload.objects.get(uploadID=uploadID)
    if not upload:
        raise Warning('ID supplied by upload does not exist')
    if not upload.expectedChunk == chunkNum:
        raise Warning('Wrong chunk sent to server')
    if not request.FILES['chunk']:
        raise Warning('Chunk contained no data')
    
    try:
        upload.write_chunk_from_memory(request.FILES['chunk'].read())
        upload.downloading(upload.expectedChunk*64*1024)
    except Exception as e:
        upload.fatal_error('Internal server error')
        raise e
    
    if not request.POST.get('lastChunk'):
        return ''
    #last chunk was received, start procesing
    upload.waiting()
    return 'Done'
    
def submit_youtube(request):
    try:
        url, board = basic_validation(request)
    except Warning:
        raise
    youtube_type = request.POST.get('youtube_type')
    if youtube_type == 'video':
        videoID = request.POST.get('video')
        audioID = request.POST.get('audio')
        if (not videoID) or (not audioID):
            raise Warning('Please select audio/video formats')
        ret = get_youtube_format({'video': videoID, 'audio': audioID}, url)
        if not ret:
            raise Warning('Selected audio/video format is not valid')
        extension = ret
        options = {'videoID': videoID, 'audioID': audioID}
    else:
        extension = 'm4a'
        options = {}
    
    filesize = 0
    priority = get_priority(filesize)
    
    upload = prepare_upload(request.user, '',  is_private(request),  board,  url, extension, request.POST.get('title'), 'youtube', priority, filesize)
    upload.store_options(options)
    upload.waiting()
    return

def submit_imgur(request):
    try:
        url, board = basic_validation(request)
    except Warning:
        raise
    
    try:
        images = get_imgur_images(url)
    except:
        raise Warning("Could not get images. Is URL correct?")
    image_items = []
    for item in images:
        if item['id'] in request.POST:
            if not 'image' == get_extension_type(item['ext']):
                raise Warning("Album includes non-image or invalid file(s)")
            image_items.append(item)
    
    if request.POST.get('imgur_type') == 'separate':
        for item in image_items:
            url = item['full_url']
            extension = item['ext']
            filesize = int(round(item['size']/1024))
            priority = get_priority(filesize)
            prepare_upload(request.user, '',  is_private(request),  board,  url, extension, request.POST.get('title'), 'url', priority, filesize).waiting()
    else:
        if len(image_items)<2:
            raise Warning("Album should include at least two images.")
        extension = 'album'
        filesize = 0
        for item in image_items:
            filesize += item['size']
        filesize = int(round(filesize/1024))
        priority = get_priority(filesize)
        title = request.POST.get('title') if request.POST.get('title') else get_imgur_title(url)
        upload = prepare_upload(request.user, '',  is_private(request),  board,  url, extension, title, 'imgur', priority, filesize)
        upload.store_options({'image_items': image_items})
        upload.waiting()
    return