from ast import literal_eval
import socket

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Q

from posts.models import Post
from .models import Tag, PostTag, TagSuggestion

from .tasks import process_tag_add, process_tag_remove

from cloudjangohost.settings import NEURAL_SUGGEST_SOCKET

# Create your views here.

@login_required
def tag_list(request):
	context = {
		'tags': Tag.objects.order_by('name').values_list('name', flat=True),
	}
	return render(request, 'tags/tag_list.html', context)

@login_required
def tag_description(request, tag):
	tag = get_object_or_404(Tag, name=tag)
	all_tag_ids = list(Tag.objects.values_list('id', flat=True))
	context = {
		'tag': tag,
		'chancesFrom': [],
		'chancesTo': get_tag_set_predictions([tag.id], all_tag_ids),
	}
	return render(request, 'tags/tag.html', context)

@login_required
def add_tag(request):
	process_tag_add.delay(request.POST.get('filename'), request.POST.get('tag'), request.user.pk)
	return redirect('posts:post', board=request.POST.get('board'), filename=request.POST.get('filename'))
	
@login_required
def add_suggested_tag(request):
	process_tag_add.delay(request.POST.get('filename'), request.POST.get('tag'), request.user.pk)
	return HttpResponse()

@login_required
def remove_suggested_tag(request):
	process_tag_remove.delay(request.POST.get('filename'), request.POST.get('tag'), request.user.pk)
	return HttpResponse()

@login_required
def get_suggested_tags_json(request):
	post = get_object_or_404(Post, filename=request.POST.get('filename'))
	sugs = TagSuggestion.objects.filter(post=post)

	if not sugs.exists():
	 	return JsonResponse({})

	tags = list(post.tag_set.values_list('id', flat=True))
	tags_to_predict = list(sugs.values_list('tag__id', flat=True))
	
	sug_list = get_tag_set_predictions(tags, tags_to_predict)
	sug_dict = {k: sug_list[k] for k in range(len(sug_list))}
	return JsonResponse(sug_dict)
	
def get_tag_set_predictions(tag_ids_set, tag_ids_to_predict):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('localhost', NEURAL_SUGGEST_SOCKET))
	s.sendall(str(tag_ids_set).encode('utf-8'))
	s.shutdown(socket.SHUT_WR)
	msg=[]
	while True:
		data = s.recv(8192)
		if not data: break
		msg.append(data.decode('utf-8'))
	predicts = literal_eval(''.join(msg))
	sug_list = []
	for tag in tag_ids_to_predict:
		sug_list.append({
			'name': Tag.objects.get(id=tag).name,
			'percent': predicts[tag]*100
		})
	sug_list = sorted(sug_list, key=lambda k: k['percent'], reverse=True) 
	return sug_list

def remove_suggested_tag_func(filename, tagname, user):
	post = get_object_or_404(Post, filename=filename)
	tag = get_object_or_404(Tag, name=tagname)
	TagSuggestion.objects.get(post=post, tag=tag).delete()
	
def get_tag_lists(request):
	#Used to get a list of lists, where each list are all tags of a post
	#Will be used to parse neural network data on another machine
	from cloudjangohost.settings import TAG_API_KEY
	key = request.GET.get('key')
	if not key == TAG_API_KEY:
		return JsonResponse({'lists': [], 'count': -1})
	posts = Post.objects.all()
	p = []
	for post in posts:
		if post.tag_set.exists():
			p.append(list(post.tag_set.values_list('id', flat=True)))
	ret = {
		'lists': p,
		'count': Tag.objects.count()
	}
	return JsonResponse(ret)