import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from downloader.helpers import submit_type_is_valid, get_youtube_formats
from downloader.operations import submit_url, submit_upload, submit_youtube

# Create your views here.
@login_required
def submit(request):
	if request.method == "POST":
		submit_type = request.POST.get('submit_type')
		if not submit_type_is_valid(submit_type):
			return render(request, 'submit/index.html', { 'err': 'Invalid submission type selected. Are you hacking?' })
		
		if 'url' == submit_type:
			try:
				submit_url(request)
			except Warning as w:
				logging.warning(w, exc_info=True)
				return render(request, 'submit/index.html', { 'err': 'Failed: '+str(w) })
			except Exception as e:
				logging.exception(e)
				return render(request, 'submit/index.html', { 'err': 'Failed: internal server error occured' })
			return redirect('downloader:queue')
		elif 'upload' == submit_type:
			#Upload is done with AJAX, so HttpResponses are returned
			try:
				response = submit_upload(request)
			except Warning as w:
				logging.warning(w, exc_info=True)
				return HttpResponse(content='Failed: '+str(w), status=400)
			except Exception as e:
				logging.exception(e)
				return HttpResponse(content='Failed: internal server error occured', status=500)
			return HttpResponse(content=response)
		elif 'youtube' == submit_type:
			try:
				submit_youtube(request)
			except Warning as w:
				logging.warning(w, exc_info=True)
				return render(request, 'submit/index.html', { 'err': 'Failed: '+str(w) })
			except Exception as e:
				logging.exception(e)
				return render(request, 'submit/index.html', { 'err': 'Failed: internal server error occured' })
			return redirect('downloader:queue')
	
	return render(request, 'submit/index.html', None)

@login_required
def query_youtube(request):
	url = request.POST.get('url')
	return JsonResponse(get_youtube_formats(url))