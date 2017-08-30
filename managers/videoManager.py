import os, os.path
from PIL import Image
from subprocess import check_output, call

from storage.operations import get_tempfile, get_tempthumb

video_mimes = ['video/mp4', 'video/webm', 'video/x-matroska']
video_types = ['mp4', 'webm', 'mkv']
video_mimes_to_ext = { 'video/mp4': 'mp4', 'video/webm': 'webm', 'video/x-matroska': 'mkv' }
maxsize = 300

def process_video(upl):
	if not os.path.isfile(get_tempfile(upl)):
		raise OSError('Failed to process file, resulting file is missing.')
		
	if 'webm' == upl.extension:
		return #webms do not require any processing
    
	temp_path = get_tempfile(upl)
	video_format = check_output("ffprobe -v error -select_streams v -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "+temp_path, shell=True).decode("utf-8").rstrip()
	audio_format = check_output("ffprobe -v error -select_streams a -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "+temp_path, shell=True).decode("utf-8").rstrip()
	
	if 'h264' == video_format:
		if 'mp4' == upl.extension:
			if not ('' == audio_format or 'aac' == audio_format):
				toMP4VideoCopyAudioConvert(upl)
		elif 'mkv' == upl.extension:
			if '' == audio_format:
				toMP4VideoCopy(upl)
			elif 'aac' == audio_format:
				toMP4VideoCopyAudioCopy(upl)
			else:
				toMP4VideoCopyAudioConvert(upl)
	else:
		raise TypeError("Video encoding of "+video_format+" not supported.")
	
	return

def create_thumb(upl):
	path = get_tempfile(upl)
	width = check_output("ffprobe -v error -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "+path, shell=True).decode("utf-8").rstrip()
	height = check_output("ffprobe -v error -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 "+path, shell=True).decode("utf-8").rstrip()
	mid = '300:-1' if width>height else '-1:300'
	call('ffmpeg -i {0!s} -vf "select=gte(n\,20), scale={1!s}" -frames:v 1 {2!s}'.format(path, mid, get_tempthumb(upl)), shell=True)
	if not os.path.isfile(get_tempthumb(upl)):
		raise OSError('Failed to process file, resulting thumbnail is missing.')

def toMP4VideoCopyAudioConvert(upl):
	convertToMP4(upl, "-c:v copy -c:a libfdk_aac -vbr 5")
	
def toMP4VideoCopy(upl):
	convertToMP4(upl, "-c:v copy")
	
def toMP4VideoCopyAudioCopy(upl):
	convertToMP4(upl, "-c:v copy -c:a copy")
	
def convertToMP4(upl, convert_string):
	convertPath = get_tempfile(upl)+'.mp4'
	call("/srv/ffmpeg/ffmpeg -i "+get_tempfile(upl)+" "+convert_string+" "+convertPath, shell=True)
	os.remove(get_tempfile(upl))
	upl.extension = 'mp4'
	upl.save()
	os.rename(convertPath, get_tempfile(upl))