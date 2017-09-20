import os, os.path
import managers.imageManager as imageManager
from subprocess import check_output, call

other_mimes = []
other_types = ['album']
other_mimes_to_ext = {}
maxsize = 300

def process_upload(upl):
	if upl.extension == 'album':
		create_thumb(upl)
	elif 'pdf' == upl.extension:
		return #pdf files do not require any processing

def create_thumb(upl):
	#TODO: find how to create good pdf thumb from first page only
	if upl.extension == 'album':
		imageManager.create_thumb('{0!s}0.{1!s}'.format(upl.get_temp_folder(), upl.get_options()['image_items'][0]['ext']) ,upl.get_temp_thumb())
	return