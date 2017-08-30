import os, os.path
from PIL import Image
from subprocess import check_output, call

from storage.operations import get_tempfile, get_tempthumb

music_mimes = ['audio/mpeg', 'audio/flac']
music_types = ['mp3', 'flac']
music_mimes_to_ext = { 'audio/mpeg': 'mp3', 'audio/flac': 'flac' }
maxsize = 300

def process_audio(upl):
	if not os.path.isfile(get_tempfile(upl)):
		raise OSError('Failed to process file, resulting file is missing.')
		
	if 'mp3' == upl.extension or 'flac' == upl.extension:
		return #mp3, flac file do not require any processing

def create_thumb(upl):
	#TODO: if it has embeded picture, use it as thumb
	return