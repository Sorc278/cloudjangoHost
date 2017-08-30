# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from .models import Upload

from managers.extHelpers import get_extension_from_string
from posts.models import Post, Extra

# Create your views here.
def queue(request):
	context = {
		'uploads': Upload.objects.order_by('-date'),
	}
	return render(request, 'downloader/queue.html', context)
	
def extra(request, board, filename):
	get_object_or_404(Post, filename=filename)
	return render(request, 'downloader/extra.html', { 'filename': filename, 'board': board })
	
def submit_extra(request, board, filename):
	post = get_object_or_404(Post, filename=filename)
	extra_type = request.POST.get('extra_type')
	if 'thumb' == extra_type:
		post.thumb_from_image(request.FILES['file'].temporary_file_path())
	elif 'subtitles' == extra_type:
		ext = get_extension_from_string(request.FILES['file'].name)
		if 'ass' == ext:
			e = Extra()
			e.post = post
			e.user = request.user
			e.description = request.POST.get('description')
			e.extra_type = 'subtitles'
			e.extension = 'ass'
			e.save()
			e.save_from_file(request.FILES['file'].temporary_file_path())
	return redirect('posts:post', filename=filename, board=board)