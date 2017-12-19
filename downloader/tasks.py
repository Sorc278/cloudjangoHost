import requests
import sys
if sys.version_info[0] < 3:
	from urllib import urlretrieve
else:
	from urllib.request import urlretrieve
import logging
import youtube_dl as ydl
from celery import shared_task

from managers.extHelpers import get_extension_type
import managers.imageManager as imageManager
import managers.videoManager as videoManager
import managers.musicManager as musicManager
import managers.documentManager as documentManager
import managers.otherManager as otherManager
from posts.operations import create_post

from .helpers import send_get, get_youtube_meta


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
	try:
		if 'url' == upload.downloadType:
			prepare_file_url(upload)
		if 'upload' == upload.downloadType:
			prepare_file_upload(upload)
		if 'youtube' == upload.downloadType:
			prepare_file_youtube(upload)
		if 'imgur' == upload.downloadType:
			prepare_file_imgur(upload)
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
	chunk_size_in_kb = 512
	chunk_size=chunk_size_in_kb*1024
	response = send_get(upload.url)
	for chunk in response.iter_content(chunk_size):
		if chunk:
			try:
				upload.write_chunk_from_memory(chunk)
				chunk_num += 1
				upload.downloading(chunk_num*chunk_size_in_kb)
			except Exception as e:
				raise
	return
	
def prepare_file_upload(upload):
	return

def prepare_file_youtube(upload):
	upload.working('Downloading')
	options = upload.get_options()
	ydl_opts = {
		'outtmpl': upload.get_temp_main(),
		'progress_hooks': [],
	}
	if options:
		ydl_opts['format'] = '{0!s}+{1!s}'.format(options['videoID'], options['audioID'])
	else:
		ydl_opts['format'] = 'bestaudio/best'
		ydl_opts['postprocessors'] = [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'm4a',
			'preferredquality': '160',
		}]
	
	try:
		with ydl.YoutubeDL(ydl_opts) as y:
			y.download([upload.url])
	except Exception as e:
		raise
	
	meta = get_youtube_meta(upload.url)
	if not upload.title:
		upload.title = meta['title']
		upload.save()
	#TODO: add exception checks
	if options:
		urlretrieve(meta['thumb_url'], upload.get_temp_thumb())
	return

def prepare_file_imgur(upload):
	upload.downloading(0)
	pages = 0
	downloaded = 0
	image_items = upload.get_options()['image_items']
	for item in image_items:
		urlretrieve(item['full_url'], '{0!s}{1!s}.{2!s}'.format(upload.get_temp_folder(), pages, item['ext']))
		downloaded += item['size']
		upload.downloading(downloaded/1024)
		pages += 1
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
		try:
			videoManager.process_upload(upload)
		except Exception as e:
			raise
	elif 'music' == extType:
		try:
			musicManager.process_upload(upload)
		except Exception as e:
			raise
	elif 'document' == extType:
		try:
			documentManager.process_document(upload)
		except Exception as e:
			raise
	elif 'other' == extType:
		try:
			otherManager.process_upload(upload)
		except Exception as e:
			raise
	
	try:
		post = create_post(upload)
	except Exception as e:
		if 'post' in locals():
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