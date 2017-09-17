from django.urls import reverse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from tags.models import Tag, TagSuggestion

from cloudjangohost.settings import TAG_DICT_URL

from .models import Post, Extra

# Create your views here.
@login_required
def show_post(request, board, filename):
    #TODO: use get or 404 later, or something similar
    post = Post.objects.get(filename=filename)
    tags = post.tag_set.order_by('tag_type', 'name')
    
    cont = {
        'post': post,
        'extras': Extra.objects.filter(post=post),
        'board': board,
        'tags': tags,
        'TAG_DICT_URL': TAG_DICT_URL,
    }
    return render(request, "posts/post.html", cont)

@login_required
def show_posts(request, board, page):
    tags = request.GET.get('tags')
    options = {
        'board': board
    }
    posts = get_posts(tags, options)
    paginator = Paginator(posts, 88)
    #TODO: add exceptions
    posts_c = paginator.page(page).object_list
    
    cont = {
        'board': board,
        'posts': posts_c,
        'pages': paginator.page_range,
        'TAG_DICT_URL': TAG_DICT_URL,
    }
    return render(request, "posts/posts.html", cont)

def get_posts(tags_string, options):
    if not tags_string:
        post_objs = get_filtered_query(Post.objects, options)
    else:
        tags = tags_string.split()
        pos_tags = []
        neg_tags = []
        for tag in tags:
            if '-' == tag[0]:
                neg_tags.append(tag[1:])
            else:
                pos_tags.append(tag)
        
        if not pos_tags:
            post_objs = get_filtered_query(Post.objects, options).exclude(id__in=get_excluded_ids(neg_tags, options))
        else:
            posts = {}
            count = 1
            for post in get_post_id_list(pos_tags.pop(), options):
                posts[post] = 1
                
            for tag in pos_tags:
                tag_posts = get_post_id_list(tag, options)
                for tag_post in tag_posts:
                    try:
                        if posts[tag_post] == count:
                            posts[tag_post] += 1
                    except:
                        pass
                count += 1
            
            if neg_tags:
                for id in get_excluded_ids(neg_tags, options):
                    if id in posts:
                        del posts[id]
            
            post_list = []
            for k, v in posts.items():
                if v == count:
                    post_list.append(k)

            post_objs = Post.objects.filter(id__in=post_list)
    return post_objs.order_by('-date')

def get_post_id_list(tag, options):
    return get_filtered_query(Tag.objects.select_related().get(name=tag).posts, options).values_list('id', flat=True)
    
def get_excluded_ids(tag_list, options):
    return get_filtered_query(Post.objects.select_related().filter(tag__name__in=tag_list), options).distinct().values_list('id', flat=True)
    
def get_filtered_query(query, options):
    return query.filter(board__lte=options['board'])