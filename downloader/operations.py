from random import getrandbits

from celery import shared_task#temp test
import youtube_dl as ydl

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from cloudjangohost.settings import FILE_UPLOAD_STORE

from managers.extHelpers import get_extension_from_string, extension_valid, mime_valid, extension_from_mime

from .models import Upload
from .helpers import board_is_valid, url_is_valid, priority_is_valid, submit_type_is_valid
from .helpers import get_mime_from_url, get_size_from_url, get_priority, get_youtube_format
from .prep import prepare_upload
from .tasks import process_upload

def submit_url(request):
	if not board_is_valid(int(request.POST.get('board'))):
		raise Warning('Board is not valid')
	if not url_is_valid(request.POST.get('url_url')):
		raise Warning('URL is not valid')
	
	url = request.POST.get('url_url')
	try:
		mime = get_mime_from_url(url)
	except:
		#TODO: Could this exception indicate bigger problems present, warrant more than a warning?
		raise Warning('Could not retrieve the MIME type of file')
	if not (mime_valid(mime)):
		raise Warning('File type is not yet supported. MIME determined: ' + mime)
	
	filesize = get_size_from_url(url)
	priority = get_priority(filesize)
	private = True if request.POST.get('private') else False
	extension = extension_from_mime(mime)
	
	upload = prepare_upload(request.user, '',  private,  int(request.POST.get('board')),  request.POST.get('url_url'), extension, request.POST.get('title'), 'url', priority, filesize)
	upload.waiting()
	process_upload.delay(priority)
	return
	
def submit_upload(request):
	chunkNum = request.POST.get('chunkNum')
	if not chunkNum:
		raise Warning('Chunk number is missing. Are you hacking?')
	try:
		chunkNum = int(chunkNum)
	except:
		raise Warning('Non-integer chunk number received')
	
	#set up the download slot
	if -1 == chunkNum:
		if not board_is_valid(int(request.POST.get('board'))):
			raise Warning('Board is not valid')
		
		extension = get_extension_from_string(request.POST.get('filename'))
		if not extension_valid(extension):
			raise Warning('File type is not yet supported. Extension determined: ' + extension)
		
		filesize = int(request.POST.get('filesize'))
		priority = get_priority(filesize)
		private = True if request.POST.get('private') and request.user.is_staff else False
		upload = prepare_upload(request.user, request.POST.get('filename'),  private,  int(request.POST.get('board')),  '', extension, request.POST.get('title'), 'upload', priority, filesize)
		upload.downloading(0)
		return upload.uploadID
	
	#process sent chunk
	uploadID = request.POST.get('uploadID')
	if not uploadID:
		raise Warning('No upload ID supplied')
	upload = Upload.objects.get(uploadID=uploadID)
	if not upload:
		raise Warning('ID supplied by upload does not exist')
	if not upload.expectedChunk == chunkNum:
		raise Warning('Wrong chunk sent to server')
	if not request.FILES['chunk']:
		raise Warning('Chunk contained no data')
	
	try:
		upload.write_chunk_from_memory(request.FILES['chunk'].read())
		upload.downloading(upload.expectedChunk*64*1024)
	except Exception as e:
		upload.fatal_error('Internal server error')
		raise e
	
	if not request.POST.get('lastChunk'):
		return ''
	#last chunk was received, start procesing
	upload.waiting()
	process_upload.delay(upload.priority)
	return 'Done'
	
def submit_youtube(request):
	if not board_is_valid(int(request.POST.get('board'))):
		raise Warning('Board is not valid')
	if not url_is_valid(request.POST.get('youtube_url')):
		raise Warning('URL is not valid')
	
	videoID = request.POST.get('video')
	audioID = request.POST.get('audio')
	if (not videoID) or (not audioID):
		raise Warning('Please select audio/video formats')
	
	url = request.POST.get('youtube_url')
	ret = get_youtube_format({'video': videoID, 'audio': audioID}, url)
	if not ret:
		raise Warning('Selected audio/video format is not valid')
	
	filesize = 0
	priority = get_priority(filesize)
	private = True if request.POST.get('private') else False
	extension = ret
	
	upload = prepare_upload(request.user, '',  private,  int(request.POST.get('board')),  url, extension, request.POST.get('title'), 'youtube', priority, filesize)
	upload.store_options({'videoID': videoID, 'audioID': audioID})
	upload.waiting()
	process_upload.delay(priority)
	return