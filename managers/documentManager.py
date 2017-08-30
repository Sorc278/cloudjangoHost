import os, os.path
from PIL import Image
from subprocess import check_output, call

from storage.operations import get_tempfile, get_tempthumb

document_mimes = ['application/pdf']
document_types = ['pdf']
document_mimes_to_ext = { 'application/pdf': 'pdf' }
maxsize = 300

def process_document(upl):
	if not os.path.isfile(get_tempfile(upl)):
		raise OSError('Failed to process file, resulting file is missing.')
		
	if 'pdf' == upl.extension:
		return #pdf files do not require any processing

def create_thumb(upl):
	#TODO: find how to create good pdf thumb from first page only
	return