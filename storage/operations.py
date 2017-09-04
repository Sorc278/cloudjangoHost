from random import getrandbits
from subprocess import call, check_output
import os, os.path, shutil

from django.utils import timezone

from cloudjangohost.settings import MEDIA_ROOT

# Writing chunks
def write_chunk_from_memory(upload, chunk):
    #TODO add exceptions
    chunkTemppath = get_temp_path(upload, 'chunk')
    
    chunk_file = open(chunkTemppath, 'wb')
    chunk_file.write(chunk)
    chunk_file.close()
    write_chunk_from_filepath(upload, chunkTemppath)
    os.remove(chunkTemppath)

def write_chunk_from_filepath(upload, filepath):
    a = open(get_tempfile(upload), 'ab')
    b = open(filepath, 'rb')
    a.write(b.read())
    #call("cat "+filepath+" >> "+get_tempfile(upload), shell=True)

# Dir creation
def prepare_for_upload(upload):
    os.makedirs(get_temp_path_folder(upload))
    
#finalising uplods
def move_to_storage(upload, name):
    os.rename(get_tempfile(upload), get_post_path(upload, name))
    if not os.path.isfile(get_post_path(upload, name)):
        raise OSError('Failed to move file, destination file is missing.')
    os.rename(get_tempthumb(upload), get_thumb_path(upload, name))
    if not os.path.isfile(get_thumb_path(upload, name)):
        raise OSError('Failed to move thumbnail, destination thumbnail is missing.')
    
def cleanup_upload(upload):
    shutil.rmtree(get_temp_path_folder(upload))

#misc path gets
def get_store_path(obj):
    if not obj.store:
        raise ValueError('Object does not possess a store attribute')
    return '{0!s}{1!s}/'.format(MEDIA_ROOT, obj.store)

#get temp paths
def get_temp_path_folder(upload):
    return '{0!s}temp/{1!s}/'.format(get_store_path(upload), upload.tempname)
    
def get_temp_path(upload, name):
    return '{0!s}{1!s}.{2!s}'.format(get_temp_path_folder(upload), name, upload.extension)
    
def get_temp_path_with_addition(upload, name, addition):
    return '{0!s}.{1!s}'.format(get_temp_path(upload, name), addition)

def get_tempfile(upload):
    return get_temp_path(upload, 'main')
    
def get_tempthumb(upload):
    return '{0!s}thumb.jpg'.format(get_temp_path_folder(upload))
    
#get full paths
def get_post_path(obj, name):
    return '{0!s}post/{1!s}.{2!s}'.format(get_store_path(obj), name, obj.extension)
    
def get_thumb_path(obj, name):
    return '{0!s}thumb/{1!s}.jpg'.format(get_store_path(obj), name)
    
def get_post_path_by_post(obj):
    if not obj.filename or not obj.extension:
        raise ValueError('Object needs to possess filename and extension attributes')
    return '{0!s}post/{1!s}.{2!s}'.format(get_store_path(obj), obj.filename , obj.extension)
    
def get_thumb_path_by_post(obj):
    if not obj.filename:
        raise ValueError('Object needs to possess filename attribute')
    return '{0!s}thumb/{1!s}.jpg'.format(get_store_path(obj), obj.filename)

#other gets
def get_file_size(path):
    return int(check_output("expr $(stat -c '%s' "+path+") / 1024", shell=True))