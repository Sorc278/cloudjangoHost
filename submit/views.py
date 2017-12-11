import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from downloader.helpers import submit_type_is_valid, get_youtube_formats, get_imgur_images
from downloader.operations import submit_url, submit_upload, submit_youtube, submit_imgur
from home.views import get_user_by_api_key

# Create your views here.
@login_required
def submit(request):
	if request.method == "POST":
		submit_type = request.POST.get('submit_type')
		if not submit_type_is_valid(submit_type):
			return render(request, 'submit/index.html', { 'err': 'Invalid submission type selected. Are you hacking?' })
		
		try:
			if 'url' == submit_type:
				submit_url(request)
				return redirect('downloader:queue')
			elif 'youtube' == submit_type:
				submit_youtube(request)
				return redirect('downloader:queue')
			elif 'imgur' == submit_type:
				submit_imgur(request)
				return redirect('downloader:queue')
		except Warning as w:
			logging.warning(w, exc_info=True)
			return render(request, 'submit/index.html', { 'err': 'Failed: '+str(w) })
		except Exception as e:
			logging.exception(e)
			return render(request, 'submit/index.html', { 'err': 'Failed: internal server error occured' })
			
		if 'upload' == submit_type:
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
	
	return render(request, 'submit/index.html', None)

@csrf_exempt
def submit_api(request):
	user = get_user_by_api_key(request.POST.get("key"))
	if user:
		request.user = user
		ret = submit(request)
		if isinstance(ret, HttpResponseRedirect):
			return HttpResponse("Success")
		else:
			return HttpResponse("", status=400)
	else:
		return HttpResponse("", status=403)

@csrf_exempt
def query_youtube(request):
	url = request.POST.get('url')
	return JsonResponse(get_youtube_formats(url))
	
@csrf_exempt
def query_imgur(request):
	url = request.POST.get('url')
	return JsonResponse({ 'images': get_imgur_images(url) })