import mimetypes

from .imageManager import image_types, image_mimes, image_mimes_to_ext
from .videoManager import video_types, video_mimes, video_mimes_to_ext
from .musicManager import music_types, music_mimes, music_mimes_to_ext
from .documentManager import document_types, document_mimes, document_mimes_to_ext
from .otherManager import other_types, other_mimes, other_mimes_to_ext

types = image_types + video_types + music_types + document_types + other_types
mimes = image_mimes + video_mimes + music_mimes + document_mimes + other_mimes
mime_ext = dict(dict(dict(dict(image_mimes_to_ext, **video_mimes_to_ext), **music_mimes_to_ext), **document_mimes_to_ext), **other_mimes_to_ext)

priorities = ['Low', 'High']

#validity checkers
def mime_valid(mime):
    return mime.lower() in mimes
    
def extension_valid(ext):
    return ext in types


#mimes, extensions
def extension_from_mime(mime):
    return mime_ext[mime]
    
def get_extension_from_string(string):
    last_dot = string.rfind('.')
    if last_dot < 0:
        return ''
    first_question_after_dot = string.rfind('?', last_dot)
    if first_question_after_dot < 0:
        return string[last_dot+1:]
    return string[last_dot+1:first_question_after_dot]

def get_extension_type(ext):
    if ext in image_types:
        return 'image'
    if ext in video_types:
        return 'video'
    if ext in music_types:
        return 'music'
    if ext in document_types:
        return 'document'
    if ext in other_types:
        return 'other'
    return ''