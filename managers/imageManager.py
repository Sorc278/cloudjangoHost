import os
import os.path
from PIL import Image

image_mimes = ['image/jpeg', 'image/png', 'image/gif']
image_types = ['jpg', 'jpeg', 'png', 'gif']
image_mimes_to_ext = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif' }
maxsize = 300

def process_upload(upload):
    if 'jpeg' == upload.extension:
        oldpath = upload.get_temp_main()
        upload.extension = 'jpg'
        upload.save()
        os.rename(oldpath, upload.get_temp_main())
        
    if not os.path.isfile(upload.get_temp_main()):
        raise OSError('Failed to process image, resulting file is missing.')
    
    try:
        create_thumb(upload.get_temp_folder(), upload.get_temp_main(), upload.get_temp_thumb())
    except Exception as e:
        raise e
    
    return

def create_thumb(folder_path, image_path, thumb_path):
    im = get_thumb_in_memory(image_path)
    im.save(thumb_path, "JPEG", quality=90)
    
    if not os.path.isfile(thumb_path):
        raise OSError('Failed to process image, resulting thumbnail is missing.')
        
def get_thumb_in_memory(path):
    im = Image.open(path)
    width = float(im.size[0])
    height = float(im.size[1])
    if width>height:
        height = int(height * (maxsize / width))
        width = maxsize
    else:
        width = int(width * (maxsize / height))
        height = maxsize
    im = im.convert("RGB")
    im=im.resize((width, height), Image.ANTIALIAS)
    return im