import os, os.path
from PIL import Image
from subprocess import check_output, call
import managers.imageManager as im_manager

document_mimes = ['application/pdf']
document_types = ['pdf']
document_mimes_to_ext = { 'application/pdf': 'pdf' }
maxsize = 300

def process_document(upload):
	if not os.path.isfile(upload.get_temp_main()):
		raise OSError('Failed to process file, given file is missing.')
		
	if 'pdf' == upload.extension:
		pass #pdf files do not require any processing
	
	create_thumb(upload)

def create_thumb(upload):
	if 'pdf' == upload.extension:
		call(['convert', '-density', '200', '{0!s}[0]'.format(upload.get_temp_main()), upload.get_temp_thumb()])
		im_manager.create_thumb(upload.get_temp_thumb(), upload.get_temp_thumb())
	return