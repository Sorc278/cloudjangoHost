import requests
import os.path

from celery import shared_task

from managers.extHelpers import get_extension_type
import managers.imageManager as imageManager
import managers.videoManager as videoManager
import managers.musicManager as musicManager
import managers.documentManager as documentManager
from storage.operations import write_chunk_from_memory,  move_to_storage
from storage.operations import get_temp_path_with_addition, get_temp_path, get_tempfile, get_tempthumb
from posts.operations import create_post

from .prep import cleanup_upload
from .helpers import send_get


from .models import Upload

import time

@shared_task()
def process_upload(priority):
    upl_pr = Upload.objects.filter(priority=priority)
    while upl_pr.filter(status='Working').exists():
        time.sleep(2)
    upl = upl_pr.filter(status='Waiting').order_by('activeTime').first()
    update_upload(upl, 'Working', '')
    
    #do processing here
    if 'url' == upl.downloadType:
        post = process_upload_url(upl)
    if 'upload' == upl.downloadType:
        post = process_upload_upload(upl)
    
    cleanup_upload(upl)
    update_upload(upl, 'Complete', '')
    return post
    
def process_upload_url(upl):
    update_upload(upl, 'Working', 'Downloading: 0 out of '+str(upl.filesize)+" KB")
    chunk_num = 0
    chunk_size_in_kb = 64*1024
    chunk_size=chunk_size_in_kb*1024
    response = send_get(upl.url)
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            try:
                write_chunk_from_memory(upl, chunk)
                chunk_num += 1
                update_upload(upl, 'Working', 'Downloading: '+str(min(chunk_num*chunk_size_in_kb, upl.filesize))+' out of '+str(upl.filesize)+" KB")
            except:
                err_upload(upl, 'Failed to download file')
                raise
    
    return finalise_upload(upl)
    
def process_upload_upload(upl):
    return finalise_upload(upl)
    
def finalise_upload(upl):
    if not os.path.isfile(get_tempfile(upl)):
        err_upload(upl, 'Failed to download/retrieve file')
        raise OSError('File was not found.')
    
    extType = get_extension_type(upl.extension)
    if 'image' == extType:
        try:
            imageManager.process_image(upl)
            imageManager.create_thumb(upl)
        except:
            err_upload(upl, 'Failed to process file')
            raise
    elif 'video' == extType:
        try:
            videoManager.process_video(upl)
            videoManager.create_thumb(upl)
        except:
            err_upload(upl, 'Failed to process file')
            raise
    elif 'music' == extType:
        try:
            musicManager.process_audio(upl)
            musicManager.create_thumb(upl)
        except:
            err_upload(upl, 'Failed to process file')
            raise
    elif 'document' == extType:
        try:
            documentManager.process_document(upl)
            documentManager.create_thumb(upl)
        except:
            err_upload(upl, 'Failed to process file')
            raise
    
    try:
        post = create_post(upl)
        move_to_storage(upl, post.filename)
    except:
        err_upload(upl, 'Failed to move post to storage')
        if post:
            post.delete()
        raise
    storage = upl.user.storage
    storage.storage_used += post.size
    storage.save()
    return post.filename

def err_upload(upload, description):
    update_upload(upload, 'Failed', description)
    cleanup_upload(upload)

def update_upload(upload, status, description):
    upload.status = status
    upload.description = description
    upload.save()