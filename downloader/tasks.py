import requests
import logging

from celery import shared_task

from managers.extHelpers import get_extension_type
import managers.imageManager as imageManager
import managers.videoManager as videoManager
import managers.musicManager as musicManager
import managers.documentManager as documentManager
from posts.operations import create_post

from .helpers import send_get


from .models import Upload

import time

@shared_task()
def process_upload(priority):
	upl_pr = Upload.objects.filter(priority=priority)
	while upl_pr.filter(status='Working').exists():
		time.sleep(2)
	upload = upl_pr.filter(status='Waiting').order_by('activeTime').first()
	upload.working('')
	
	#do processing here
	if 'url' == upload.downloadType:
		try:
			prepare_file_url(upload)
		except Warning as w:
			logging.warning(w, exc_info=True)
			upload.fatal_error(str(w))
			return
		except Exception as e:
			logging.exception(e)
			upload.fatal_error('Internal server error')
			return
	if 'upload' == upload.downloadType:
		try:
			prepare_file_upload(upload)
		except Warning as w:
			logging.warning(w, exc_info=True)
			upload.fatal_error(str(w))
			return
		except Exception as e:
			logging.exception(e)
			upload.fatal_error('Internal server error')
			return
	
	try:
		post = finalise_upload(upload)
	except Warning as w:
		logging.warning(w, exc_info=True)
		upload.fatal_error(str(w))
		return
	except Exception as e:
		logging.exception(e)
		upload.fatal_error('Internal server error')
		return
	upload.cleanup()
	upload.complete()
	return post
	
def prepare_file_url(upload):
	upload.working('Downloaded 0 out of '+str(upload.filesize)+" KB")
	chunk_num = 0
	chunk_size_in_kb = 64*1024
	chunk_size=chunk_size_in_kb*1024
	response = send_get(upload.url)
	for chunk in response.iter_content(chunk_size=chunk_size):
		if chunk:
			try:
				upload.write_chunk_from_memory(chunk)
				chunk_num += 1
				upload.downloading(min(chunk_num*chunk_size_in_kb, upload.filesize))
			except Exception as e:
				raise
	return
	
def prepare_file_upload(upload):
	return
	
def finalise_upload(upload):
	if not upload.main_file_present():
		raise OSError('Main file was not found.')
	
	extType = get_extension_type(upload.extension)
	if 'image' == extType:
		try:
			imageManager.process_upload(upload)
		except Exception as e:
			raise
	elif 'video' == extType:
		raise Warning("No video processing yet")
	# 	try:
	# 		videoManager.process_video(upl)
	# 		videoManager.create_thumb(upl)
	# 	except:
	# 		err_upload(upl, 'Failed to process file')
	# 		raise
	# elif 'music' == extType:
	# 	try:
	# 		musicManager.process_audio(upl)
	# 		musicManager.create_thumb(upl)
	# 	except:
	# 		err_upload(upl, 'Failed to process file')
	# 		raise
	# elif 'document' == extType:
	# 	try:
	# 		documentManager.process_document(upl)
	# 		documentManager.create_thumb(upl)
	# 	except:
	# 		err_upload(upl, 'Failed to process file')
	# 		raise
	
	try:
		post = create_post(upload)
	except Exception as e:
		if post:
			post.delete()
		raise
	try:
		post.move_files_from(upload)
	except Exception as e:
		post.delete_files()
		post.delete()
		raise
	
	storage = upload.user.storage
	storage.storage_used += post.size
	storage.save()
	return post