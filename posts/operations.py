import random

from storage.operations import get_file_size

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
	post.size = upload.get_size()
	
	if upload.extension == 'album':
		image_items = upload.get_options()['image_items']
		images = []
		pages = 0
		for item in image_items:
			images.append({'path': '{0!s}.{1!s}'.format(pages, item['ext'])})
			pages += 1
		post.store_options({'images': images})
	
	post.save()
	return post

def get_filename(length):
	if not isinstance( length, int ):
		raise ValueError('Value of length is invalid, should be a number')
	
	while True:
		post = ''.join(random.choice('0123456789abcdef') for n in range(length))
		#rand bits may sometimes create names of length 15 instead
		
		#extra safeguard
		if not len(post) == 16:
			continue
		
		if not Post.objects.filter(filename=post).exists():
			break
		
	return post