from random import getrandbits

from celery import shared_task#temp test

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from cloudjangohost.settings import FILE_UPLOAD_STORE

from storage.operations import write_chunk_from_filepath
from managers.extHelpers import get_extension_from_string, extension_valid, mime_valid, extension_from_mime

from .models import Upload
from .helpers import board_is_valid, url_is_valid, priority_is_valid, submit_type_is_valid
from .helpers import get_mime_from_url, get_size_from_url, get_priority, err
from .prep import prepare_upload
from .tasks import process_upload, update_upload, err_upload

def submit_url(request):
    if not board_is_valid(int(request.POST.get('board'))):
        return err(request, "Board is not valid")
    if not url_is_valid(request.POST.get('url_url')):
        return err(request, "URL is not valid")
    
    url = request.POST.get('url_url')
    try:
        mime = get_mime_from_url(url)
    except:
        return err(request, "Could not retrieve the MIME type of file")
    if not (mime_valid(mime)):
        return err(request, 'File type is not yet supported. MIME determined: ' + mime)
    
    filesize = get_size_from_url(url)
    priority = get_priority(filesize)
    private = True if request.POST.get('private') else False
    extension = extension_from_mime(mime)
    
    prepare_upload(request.user, '',  private,  int(request.POST.get('board')),  request.POST.get('url_url'), extension, request.POST.get('title'), 'url', priority, filesize)
    process_upload.delay(priority)
    
    return render(request, 'submit/index.html', None)
    
def submit_upload(request):
    chunkNum = request.POST.get('chunkNum')
    if not chunkNum:
        return HttpResponse(content='Chunk number is missing. Are you hacking?', status=400)
    try:
        chunkNum = int(chunkNum)
    except:
        return HttpResponse(content='Chunk number should be an integer', status=400)
    
    #set up the download slot
    if -1 == chunkNum:
        if not board_is_valid(int(request.POST.get('board'))):
            return HttpResponse(content='Board is not valid', status=400)
        
        extension = get_extension_from_string(request.POST.get('filename'))
        if not extension_valid(extension):
            return HttpResponse(content='File type is not yet supported. Extension determined: ' + extension, status=501)
        
        filesize = int(request.POST.get('filesize'))
        priority = get_priority(filesize)
        private = True if request.POST.get('private') else False
        upload = prepare_upload(request.user, request.POST.get('filename'),  private,  int(request.POST.get('board')),  '', extension, request.POST.get('title'), 'upload', priority, filesize)
        update_upload(upload, 'Being uploaded', '')
        return HttpResponse(upload.uploadID)
    
    #process sent chunk
    uploadID = request.POST.get('uploadID')
    if not uploadID:
        return HttpResponse(content='No ID supplied', status=400)
    upload = Upload.objects.get(uploadID=uploadID)
    if not upload:
        return HttpResponse(content='ID supplied by upload does not exist.', status=400)
    if not upload.expectedChunk == chunkNum:
        err_upload(upload, 'Wrong chunk sent to server')
        return HttpResponse(content='Wrong chunk sent to server', status=400)
    if not request.FILES['chunk']:
        err_upload(upload, 'Chunk contained no data')
        return HttpResponse(content='Chunk contained no data', status=400)
    
    try:
        write_chunk_from_filepath(upload, request.FILES['chunk'].temporary_file_path())
        upload.expectedChunk += 1
        upload.save()
    except:
        err_upload(upload, 'Failed to write chunk')
        return HttpResponse(content='Failed to write chunk', status=400)
    
    if not request.POST.get('lastChunk'):
        return HttpResponse()
    #last chunk was received, start procesing
    update_upload(upload, 'Waiting', '')
    process_upload.delay(upload.priority)
    
    return HttpResponse("Done")