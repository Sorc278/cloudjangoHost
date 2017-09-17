import os, os.path
from PIL import Image
from subprocess import check_output, call

music_mimes = ['audio/mpeg', 'audio/mp4a-latm', 'audio/flac']
music_types = ['mp3', 'm4a', 'flac']
music_mimes_to_ext = { 'audio/mpeg': 'mp3', 'audio/flac': 'flac', 'audio/mp4a-latm': 'm4a' }
maxsize = 300

def process_upload(upload):
	if not os.path.isfile(upload.get_temp_main()):
		raise OSError('Failed to process audio, main file is missing.')
	if 'mp3' == upload.extension or 'flac' == upload.extension or 'm4a' == upload.extension:
		return #mp3, flac file do not require any processing
	
	return

def create_thumb(upl):
	#TODO: if it has embeded picture, use it as thumb
	return