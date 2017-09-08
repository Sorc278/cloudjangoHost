import logging

import youtube_dl as ydl

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from downloader.helpers import submit_type_is_valid
from downloader.operations import submit_url, submit_upload

# Create your views here.
@login_required
def submit(request):
	if request.method == "POST":
		submit_type = request.POST.get('submit_type')
		if not submit_type_is_valid(submit_type):
			return err(request, 'Invalid submit type selected.')
		
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
				
		if 'upload' == submit_type:
			return submit_upload(request)
	
	return render(request, 'submit/index.html', None)

@login_required
def query_youtube(request):
	url = request.POST.get('url')
	
	options = {
		'noplaylist' : True,
	}
	audio_list = []
	video_list = []
	with ydl.YoutubeDL(options) as r:
		info = r.extract_info(url, download=False)
		for item in info['formats']:
			if (not item['acodec']=='none') and (not item['vcodec']=='none'):
				continue
			e = item['ext']
			#print(item)
			if e in ['webm', 'mp4'] and not item['vcodec']=='none':
				vid_it = {
					'format': item['format'],
					'fps': item['fps'],
					'ext': item['ext'],
					'codec':item['vcodec'],
				}
				vid_it['bitrate'] = item['vbr'] if 'vbr' in item else 'Unknown'
				vid_it['filesize'] = item['filesize'] if 'filesize' in item else 'Unknown'
				video_list.append(vid_it)
			elif e in ['m4a', 'webm'] and not item['acodec']=='none':
				aud_it = {
					'format': item['format'],
					'bitrate': item['abr'],
					#'sampling': item['asr'],
					'ext': item['ext'],
					'codec':item['acodec'],
				}
				aud_it['filesize'] = item['filesize'] if 'filesize' in item else 'Unknown'
				audio_list.append(aud_it)
		print(audio_list)
		print(video_list)
		return JsonResponse({'audio': audio_list, 'video': video_list})