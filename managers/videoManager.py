import os, os.path
from PIL import Image
import subprocess
from ffmpy import FFprobe, FFmpeg
import re

from cloudjangohost.settings import FFMPEG_PATH, FFPROBE_PATH

video_mimes = ['video/mp4', 'video/webm', 'video/x-matroska']
video_types = ['mp4', 'webm', 'mkv']
video_mimes_to_ext = { 'video/mp4': 'mp4', 'video/webm': 'webm', 'video/x-matroska': 'mkv' }
maxsize = 300

def process_upload(upload):
	if not os.path.isfile(upload.get_temp_main()):
		raise OSError('Failed to process video, main file is missing.')

	video_formats = get_video_formats(upload.get_temp_main())
	audio_formats = get_audio_formats(upload.get_temp_main())
	
	valid_codecs_num = 0
	video_format = None
	for format_item in video_formats:
		if 'h264' == format_item['codec_name'] or 'vp9' == format_item['codec_name']:
			video_format = format_item
			valid_codecs_num += 1
			if valid_codecs_num > 1:
				raise Warning('Videos with two valid video streams are not yet supported')
	if video_format is None:
		stream_str = ''
		for format_item in video_formats:
			stream_str += format_item['codec_name']+','
		stream_str = stream_str[:-1]
		raise Warning("No supported video stream found. "+video_format+" found in video.")
	
	if not 'webm' == upload.extension:
		#webms do not require any processing
		if 'h264' == video_format['codec_name']:
			if 'mp4' == upload.extension:
				if not all_audio_in_list(audio_formats, ['aac']):
					toMP4VideoCopyAudioConvert(upload, video_format, audio_formats)
			elif 'mkv' == upload.extension:
				if all_audio_in_list(audio_formats, []):
					toMP4VideoCopy(upload, video_format)
				elif all_audio_in_list(audio_formats, ['aac']):
					toMP4VideoCopyAudioCopy(upload, video_format, audio_formats)
				else:
					toMP4VideoCopyAudioConvert(upload, video_format, audio_formats)
			else:
				raise Warning("Video container of "+upload.extension+" is not yet supported")
	
	if not os.path.isfile(upload.get_temp_main()):
		raise OSError('Failed to process video, resulting file is missing.')
        
	try:
		create_thumb(upload.get_temp_main(), upload.get_temp_thumb(), video_format)
	except Exception as e:
		raise
	
	return

def create_thumb(video_path, thumb_path, video_format):
	probe = FFprobe(
		executable=FFPROBE_PATH,
		global_options='-v error -select_streams '+video_format['index']+' -show_entries stream=width,height -of default=noprint_wrappers=1',
		inputs={ video_path: None }
	)
	dim_raw = probe.run(stdout=subprocess.PIPE)[0].decode("utf-8").rstrip().replace('\n', ',')[:-1]
	dim = dict(item.split("=") for item in dim_raw.split(","))
	
	mid = '300:-1' if dim['width']>dim['height'] else '-1:300'
	ff = FFmpeg(
		executable=FFMPEG_PATH,
		inputs={video_path: None},
		outputs={thumb_path: '-vf "select=gte(n\,20), scale={0!s}" -frames:v 1'.format(mid)}
	)
	ff.run()
	if not os.path.isfile(thumb_path):
		raise OSError('Failed to create thumb, resulting thumb is missing.')

def toMP4VideoCopyAudioConvert(upl, video_format, audio_formats):
	convertToMP4(upl, get_map_string(video_format, audio_formats)+" -c:v copy -c:a libfdk_aac -vbr 5")
	
def toMP4VideoCopy(upl, video_format):
	convertToMP4(upl, get_map_string(video_format, [])+" -c:v copy")
	
def toMP4VideoCopyAudioCopy(upl, video_format, audio_formats):
	convertToMP4(upl, get_map_string(video_format, audio_formats)+" -c:v copy -c:a copy")
	
def convertToMP4(upl, convert_string):
	convertPath = upl.get_temp_main()+'.mp4'
	ff = FFmpeg(
		executable=FFMPEG_PATH,
		inputs={upl.get_temp_main(): None},
		outputs={convertPath: convert_string}
	)
	ff.run()
	os.remove(upl.get_temp_main())
	upl.extension = 'mp4'
	upl.save()
	os.rename(convertPath, upl.get_temp_main())
	
def get_video_formats(path):
	return get_formats_complex('v', 'index,codec_name', path)
	
def get_audio_formats(path):
	return get_formats_complex('a', 'index,codec_name', path)
	
def get_formats_complex(stream_type, entries, path):
	probe = FFprobe(
		executable=FFPROBE_PATH,
		global_options='-v error -select_streams '+stream_type+' -show_entries stream='+entries,
		inputs={ path: None }
	)
	format_raw = probe.run(stdout=subprocess.PIPE)[0].decode("utf-8").rstrip().replace('\n', ',')
	r = re.compile(r'(?<=\[STREAM\]\,).*?(?=\,\[/STREAM\])', re.MULTILINE | re.DOTALL)
	format_ret = []
	for matched in re.findall(r, format_raw):
		d = dict(item.split("=") for item in matched.split(","))
		format_ret.append(d)
	return format_ret
	
def all_audio_in_list(audio_formats, valid_format_list):
	for format_item in audio_formats:
		if not format_item['codec_name'] in valid_format_list:
			return False
	return True
	
def get_map_string(video_format, audio_formats):
	ret = ''
	ret += '-map 0:'+video_format['index']
	for item in audio_formats:
		ret += ' -map 0:'+item['index']
	return ret