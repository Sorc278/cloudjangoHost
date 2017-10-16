from random import getrandbits
from subprocess import call, check_output
import os, os.path, shutil

from django.utils import timezone

from cloudjangohost.settings import MEDIA_ROOT

# Writing chunks
def write_chunk_from_memory(path, chunk):
    #TODO: check that it is media folder path
    try:
        with open(path, 'ab') as outfile:
            outfile.write(chunk)
    except Exception as e:
        raise

# def write_chunk_from_filepath(upload, filepath):
#     a = open(get_tempfile(upload), 'ab')
#     b = open(filepath, 'rb')
#     a.write(b.read())

# Dir creation/deletion
def create_folder(path):
    #TODO: check that it is media folder path
    os.makedirs(path)
    
def delete_folder(path):
    #TODO: check that it is media folder path
    shutil.rmtree(path)

#misc path gets
def get_store_path(store):
    if not store:
        raise ValueError('No store specified')
    return '{0!s}{1!s}/'.format(MEDIA_ROOT, store)

#get temp paths
def get_temp_path_folder(store, name):
    return '{0!s}temp/{1!s}/'.format(get_store_path(store), name)
    
#get full paths
def get_post_folder(store):
    return '{0!s}post/'.format(get_store_path(store))

#other gets
def get_file_size(path):
    return int(check_output("expr $(stat -c '%s' "+path+") / 1024", shell=True))