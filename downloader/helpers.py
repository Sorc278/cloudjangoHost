import logging

import requests, mimetypes, math
import youtube_dl as ydl
from imgurpython import ImgurClient

from django.shortcuts import render

from managers.imageManager import image_types, image_mimes, image_mimes_to_ext
from managers.extHelpers import ext_from_mime

from cloudjangohost.settings import IMGUR_ID, IMGUR_SECRET

boards = [1, 2, 3, 4]
allowed_submit_types = ['url', 'youtube', 'upload', 'imgur']
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
def basic_validation(request):
    board = int(request.POST.get('board'))
    url = request.POST.get('url')
    if not board_is_valid(board):
        raise Warning('Board is not valid')
    if not url_is_valid(url):
        raise Warning('URL is not valid')
    return url, board

def board_is_valid(board):
    return board in boards
    
def url_is_valid(url):#more like url exists...
    return len(url) > 0
    
def submit_type_is_valid(submit_type):
    return submit_type in allowed_submit_types
    
def priority_is_valid(priority):
    return priority in priorities

#other
def is_private(request):
    private = True if request.POST.get('private') and request.user.is_staff else False
    return private

def get_meta_from_url(url):
    try:
        headers = send_head(url).headers
        mime = headers.get('content-type')
        size = headers.get('content-length')
    except Exception as e:
        logging.exception(e)
        raise Warning('Could not retrieve the meta info from URL')
    mime = mime if mime else ""
    size = int(math.ceil(float(size)/1024)) if size and size.isdigit() else 0
    return {"mime": mime, "size": size}
    
def get_priority(size):
    priority = 'Low' if 64000000 < size else 'High' #64MB
    return priority

def get_youtube_format(format_dict, url):
    formats = get_youtube_formats(url)
    if 'video' in format_dict:
        for item in formats['video']:
            if item['format_id'] == format_dict['video']:
                video_item = item
                break
        if not video_item:
            return False
    if 'audio' in format_dict:
        for item in formats['audio']:
            if item['format_id'] == format_dict['audio']:
                audio_item = item
                break
        if not audio_item:
            return False
    if video_item and audio_item:
        if video_item['ext'] == audio_item['ext'] and video_item['ext'] == 'webm':
            return 'webm'
        elif video_item['ext'] == 'mp4' and audio_item['ext'] == 'm4a':
            return 'mp4'
        else:
            return False
    return False

def get_youtube_meta(url):
    options = {
        'noplaylist' : True,
    }
    audio_list = []
    video_list = []
    with ydl.YoutubeDL(options) as r:
        info = r.extract_info(url, download=False)
        ret = {
            'title': info.get('title'),
            'thumb_url': info.get('thumbnail'),
        }
    return ret
    
def get_youtube_formats(url):
    options = {
        'noplaylist' : True,
    }
    audio_list = []
    video_list = []
    with ydl.YoutubeDL(options) as r:
        info = r.extract_info(url, download=False)
        for item in info['formats']:
            if (not item['acodec']=='none') and (not item['vcodec']=='none'):
                continue
            e = item['ext']
            if not e in ['webm', 'mp4', 'm4a']:
                continue
            #print(item)
            item_dict = {
                'ext': item['ext'],
                'format_id': item['format_id'],
            }
            item_dict['filesize'] = human_size(item['filesize']) if 'filesize' in item and not item['filesize'] is None else 'Unknown'
            if not item['vcodec']=='none':
                item_dict['fps'] = item['fps'] if 'fps' in item else 'Unknown'
                item_dict['codec'] = item['vcodec'] if 'vcodec' in item else 'Unknown'
                if 'vbr' in item:
                    item_dict['bitrate'] = item['vbr']
                elif 'tbr' in item:
                    item_dict['bitrate'] = item['tbr']
                else:
                    item_dict['bitrate'] = 'Unknown'
                if 'height' in item and 'width' in item:
                    item_dict['resolution'] = '{0!s}x{1!s}'.format(item['width'], item['height'])
                # 'format': item['format'],
                video_list.append(item_dict)
            elif not item['acodec']=='none':
                item_dict['sampling'] = item['asr'] if 'asr' in item else 'Unknown'
                item_dict['codec'] = item['acodec'] if 'acodec' in item else 'Unknown'
                item_dict['bitrate'] = item['abr'] if 'abr' in item else 'Unknown'
                audio_list.append(item_dict)
        return {'audio': audio_list, 'video': video_list}
    
def human_size(size_in_b):
    size = size_in_b
    for x in ['B','KB','MB','GB','TB']:
        if size < 1024.0:
            return "%3.1f%s" % (size, x)
        size /= 1024.0
        #by Fred Cirera, slighlty modified to convert from KB
        #https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
        
def get_imgur_images(url):
    images = ImgurClient(IMGUR_ID, IMGUR_SECRET).get_album_images(get_imgur_album_id(url))
    ret = []
    for item in images:
        char_index = item.link.rindex('.')
        link = '{0!s}t{1!s}'.format(item.link[:char_index], item.link[char_index:])
        ret.append({
            'id': item.id,
            'url': link,
            'full_url': item.link,
            'mime': item.type,
            'ext': ext_from_mime(item.type),
            'size': item.size,
        })
    return ret
    
def get_imgur_title(url):
    return ImgurClient(IMGUR_ID, IMGUR_SECRET).get_album(get_imgur_album_id(url)).title
    
def get_imgur_album_id(url):
    return url[url.rindex('/')+1:]