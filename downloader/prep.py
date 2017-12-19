from random import getrandbits
from celery import shared_task#temp test

from django.utils import timezone

from cloudjangohost.settings import FILE_UPLOAD_STORE

import storage.operations as storage
from managers.extHelpers import extension_valid

from .models import Upload
from .helpers import board_is_valid, priority_is_valid, submit_type_is_valid

def prepare_upload(user, filename, private, board, url, extension, title, downloadType, priority, filesize):
    try:
        upload = create_upload(user, filename, private, board, url, extension, title, downloadType, priority, filesize)
    except Exception as e:
        raise
    try:
        upload.prepare()
    except Exception as e:
        upload.cleanup()
        upload.delete()
        raise
    return upload

# Create your functions here.
def create_upload(user, filename, private, board, url, extension, title, downloadType, priority, filesize):
    upload = Upload()
    
    #TODO: validate user, along with all other variables
    upload.user = user
    upload.uploadID = get_upload_id(32)
    upload.filename = filename if filename else ''
    upload.tempname = user.username + upload.uploadID + ('%0x' % getrandbits(8 * 4)) #name of file in temp directory
    if not extension_valid(extension):
        raise ValueError('Invalid extension specified')
    else:
        upload.extension = extension
    upload.activeTime = timezone.now()
    upload.expectedChunk = 0
    if True == private:
        upload.private = True
    elif False == private:
        upload.private = False
    else:
        raise ValueError('Value of private is invalid, use either of the following: True, False')
    if not board_is_valid(board):
        raise ValueError('Value of board is invalid')
    else:
        upload.board = board
    upload.url = url if url else ''
    upload.title = title if title else ''
    if not submit_type_is_valid(downloadType):
        raise ValueError('Value of downloadType is invalid, as it is not in types currently allowed')
    else:
        upload.downloadType = downloadType
    upload.status = "Initialising"
    upload.description = ''
    upload.store = int(FILE_UPLOAD_STORE)
    if priority_is_valid(priority):
        upload.priority = priority
    else:
        raise ValueError('Value of priority is invalid, use either of the following: Low, High')
    if not isinstance(filesize, int):
        raise ValueError('Filesize must be an integer in KB')
    else:
        upload.filesize = filesize
    
    upload.filesize
    upload.save()
    return upload

def get_upload_id(length):
    if not isinstance( length, int ):
        raise ValueError('Value of length is invalid, should be a number')
    
    while True:
        upload = '%0x' % getrandbits(length * 4)
        if not Upload.objects.filter(uploadID=upload).exists():
            break
        
    return upload