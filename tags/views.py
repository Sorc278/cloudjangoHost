from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Q

from posts.models import Post
from .models import Tag, PostTag, TagChance, TagSuggestion

from .tasks import process_tag_add, process_tag_remove

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
	context = {
		'tag': tag,
		'chancesFrom': sort_chances(TagChance.objects.select_related().filter(child=tag), 'p'),
		'chancesTo': sort_chances(TagChance.objects.select_related().filter(parent=tag), 'c'),
	}
	print(context)
	return render(request, 'tags/tag.html', context)

@login_required
def add_tag(request):
	add_tag_func(request.POST.get('filename'), request.POST.get('tag'), request.user)
	return redirect('posts:post', board=request.POST.get('board'), filename=request.POST.get('filename'))

@login_required
def get_suggested_tags_json(request):
	post = get_object_or_404(Post, filename=request.POST.get('filename'))
	sugs = TagSuggestion.objects.filter(post=post)
	
	if not sugs.exists():
		return JsonResponse({})
	
	sug_list = sort_suggests(sugs)
	
	sug_dict = {k: sug_list[k] for k in range(len(sug_list))}
	return JsonResponse(sug_dict)

@login_required
def add_suggested_tag(request):
	process_tag_add.delay(request.POST.get('filename'), request.POST.get('tag'), request.user.pk)
	return HttpResponse()

@login_required
def remove_suggested_tag(request):
	process_tag_remove.delay(request.POST.get('filename'), request.POST.get('tag'), request.user.pk)
	return HttpResponse()

def remove_suggested_tag_func(filename, tagname, user):
	post = get_object_or_404(Post, filename=filename)
	tag = get_object_or_404(Tag, name=tagname)
	TagSuggestion.objects.get(post=post, tag=tag).delete()

def add_tag_func(filename, tagname, user):
	post = get_object_or_404(Post, filename=filename)
	tag = get_object_or_404(Tag, name=tagname)
	
	if tag.staff_only and not user.is_staff:
		#TODO: add message that tag can be used only by admin and make it a security exception. Make using funcs change response code depending on this
		raise ValueError("User is not set as staff")
		
	if not PostTag.objects.filter(post=post, tag=tag).exists():
		tag.increment_occurences()
		tags_list = post.tag_set.all()
		TagChance.objects.filter(Q(parent__in=tags_list, child=tag) | Q(parent=tag, child__in=tags_list)).update(child_num=F('child_num')+1)
		PostTag.objects.create(tag=tag, post=post, added_by=user)
		tag.posts.add(post)
		TagSuggestion.objects.filter(post=post, tag=tag).delete()
		
def sort_suggests(suggests):
	tag_set = suggests.first().post.tag_set.values_list('id', flat=True)
	print(tag_set)
	sug_list = []
	i = 0
	for sug in suggests:
		sug_list.append({
			'name': sug.tag.name,
			'percent': sug.percent_with_tag_set(tag_set)
		})
	sug_list.sort(key=lambda tup: tup['percent'], reverse=True)
	return sug_list
	
def sort_chances(suggests, t):
	sug_list = []
	i = 0
	for sug in suggests:
		sug_list.append({
			'name': sug.parent.name if t == 'p' else sug.child.name,
			'percent': sug.percent()
		})
	sug_list.sort(key=lambda tup: tup['percent'], reverse=True)
	return sug_list
	
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
			p.append(list(post.tag_set.values_list('id', flat=True).order_by('id')))
	ret = {
		'lists': p,
		'count': Tag.objects.count()
	}
	return JsonResponse(ret)