from ast import literal_eval
import socket

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Q

from posts.models import Post
from .models import Tag, PostTag, TagDeclination
from .objects import TaggablePost

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
	TaggablePost(request.POST.get('filename'), request.user.pk).add_tag(request.POST.get('tag'))
	return redirect('posts:post', board=request.POST.get('board'), filename=request.POST.get('filename'))
	
@login_required
def add_suggested_tag(request):
	TaggablePost(request.POST.get('filename'), request.user.pk).add_tag(request.POST.get('tag'))
	return HttpResponse()

@login_required
def add_tag_declination(request):
	TaggablePost(request.POST.get('filename'), request.user.pk).add_tag_declination(request.POST.get('tag'))
	return HttpResponse()

@login_required
def get_suggested_tags_json(request):
	post = get_object_or_404(Post, filename=request.POST.get('filename'))
	tPost = TaggablePost(request.POST.get('filename'), None)

	tags = tPost.get_tag_list()
	tags_to_predict = tPost.get_possible_tag_list()
	
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
	
def get_tag_lists(request):
	#Used to get a list of lists, where each list are all tags of a post
	#Will be used to parse neural network data on another machine
	from cloudjangohost.settings import TAG_API_KEY
	key = request.GET.get('key')
	if not key == TAG_API_KEY:
		return JsonResponse({})
	posts = Post.objects.all()
	all_tags = set(list(Tag.objects.all().values_list('id', flat=True)))
	p = []
	p2 = []
	p3 = []
	for post in posts:
		tPost = TaggablePost(post, None)
		if post.tag_set.exists():
			p.append(tPost.get_tag_list())
			p2.append(tPost.get_tag_declination_list())
			p3.append(tPost.get_possible_tag_list())
	ret = {
		'lists': p,
		'lists_dec': p2,
		'list_pos': p3,
		'count': Tag.objects.count()
	}
	return JsonResponse(ret)