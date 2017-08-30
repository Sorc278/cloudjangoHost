import os
import os.path
from PIL import Image

from storage.operations import get_tempfile, get_tempthumb

image_mimes = ['image/jpeg', 'image/png', 'image/gif']
image_types = ['jpg', 'jpeg', 'png', 'gif']
image_mimes_to_ext = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif' }
maxsize = 300

def process_image(upl):
    if 'jpeg' == upl.extension:
        oldpath = get_tempfile(upl)
        upl.extension = 'jpg'
        upl.save()
        os.rename(oldpath, get_tempfile(upl))
        
    if not os.path.isfile(get_tempfile(upl)):
        raise OSError('Failed to process file, resulting file is missing.')
        
    return

def create_thumb(upl):
    im = get_thumb_in_memory(get_tempfile(upl))
    im.save(get_tempthumb(upl), "JPEG", quality=90)
    
    if not os.path.isfile(get_tempthumb(upl)):
        raise OSError('Failed to process file, resulting thumbnail is missing.')
        
def get_thumb_in_memory(path):
    im = Image.open(path)
    width = float(im.size[0])
    height = float(im.size[1])
    if width>height:
        height = int(height * (maxsize / width))
        width = 300
    else:
        width = int(width * (maxsize / height))
        height = 300
    im = im.convert("RGB")
    im=im.resize((width, height), Image.ANTIALIAS)
    return im