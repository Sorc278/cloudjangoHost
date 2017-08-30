from random import getrandbits

from storage.operations import get_tempfile, get_file_size

from .models import Post

# Create your functions here.
def create_post(upload):
    post = Post()
    
    post.user = upload.user
    post.title = upload.title
    post.store = upload.store
    post.filename = get_filename(16)
    post.extension = upload.extension
    post.private = upload.private
    post.board = upload.board
    post.source = upload.url if upload.url else 'Uploaded by user as '+upload.filename
    post.size = get_file_size(get_tempfile(upload))
    
    post.save()
    return post

def get_filename(length):
    if not isinstance( length, int ):
        raise ValueError('Value of length is invalid, should be a number')
    
    while True:
        post = '%0x' % getrandbits(length * 4)
        if not Post.objects.filter(filename=post).exists():
            break
        
    return post