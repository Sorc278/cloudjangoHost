from random import getrandbits
from subprocess import call, check_output
import os, os.path, shutil

from django.db.models import Sum
from django.utils import timezone

from cloudjangohost.settings import MEDIA_ROOT

from welcome.models import Storage

def get_sizes_list_human():
    ret = get_sizes_list()
    for row in ret:
        row['size'] = human_size(row['size'])
    return ret

def get_sizes_list():
    ret = []
    s_all = get_size_all()
    s_users = get_size_used_users()
    s_used = get_size_used()
    s_misc = s_used - s_users
    s_alloc = get_size_allocated()
    s_alloc_left = s_alloc - s_users
    s_free = s_all - s_alloc
    ret.append({'name': 'All space', 'size': s_all, 'percent': 100})
    ret.append({'name': 'Free to share', 'size': s_free, 'percent': int((float(100)*s_free)/s_all)})
    ret.append({'name': 'Used by users', 'size': s_users, 'percent': int((float(100)*s_users)/s_all) })
    ret.append({'name': 'Used by misc', 'size': s_misc, 'percent': int((float(100)*s_misc)/s_all) })
    ret.append({'name': 'Allocated to users', 'size': s_alloc, 'percent': int((float(100)*s_alloc)/s_all) })
    ret.append({'name': 'Left to users', 'size': s_alloc_left, 'percent': int((float(100)*s_alloc_left)/s_all) })
    
    return ret

def get_size_all():
    return float(3000000)
    
def get_size_used():
    return float(50000)
    
def get_size_used_users():
    all_used = Storage.objects.aggregate(Sum('storage_used'))['storage_used__sum']
    if all_used is None:
        return float(0)
    return float(all_used)
    
def get_size_allocated():
    allowed = Storage.objects.aggregate(Sum('storage_allowed'))['storage_allowed__sum']
    if allowed is None:
        return float(0)
    return float(allowed)
    
def human_size(size):
    for x in ['KB','MB','GB','TB']:
        if size < 1024.0:
            return "%3.1f%s" % (size, x)
        size /= 1024.0