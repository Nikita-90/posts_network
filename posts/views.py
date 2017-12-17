from django.contrib.auth.decorators import login_required
from django.db.models.query import Prefetch
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from django.db.models import Count

from .forms import PostForm, CommentForm
from .models import Post, Like, Comment
from common.models import CustomUser


def get_page(page, data):
    """
    Pagination
    """
    page_next = (page + 1) if ((page + 1) <= len(data) / 5) else page
    page_prev = (page - 1) if ((page - 1) >= 0) else page
    return page_next, page_prev


@login_required(login_url='/common/authentication_user/')
def do_like(request):
    back_link = '/posts/main_page/'
    if request.method == 'POST':
        post = request.POST.get('like')
        if post:
            user = request.user
            if Like.objects.filter(post_id=post, user_id=user.id).exists():
                Like.objects.filter(post_id=post, user_id=user.id).delete()
            else:
                Like.objects.create(post_id=post, user_id=user.id)
        link = request.META.get('HTTP_REFERER')
        if link:
            back_link = '/' + link.split('/', 3)[-1]
    return redirect(back_link)


@login_required(login_url='/common/authentication_user/')
def post_detail(request, post_id, page=0):
    user = request.user
    posts = Post.objects.annotate(Count('like_post'))
    post = posts.get(id=post_id)
    comments = Comment.objects.filter(post=post)
    page = int(page)
    page_next, page_prev = get_page(page, comments)
    comments = comments[page * 5:page * 5 + 5]
    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.data._mutable = True
        form.data['user'] = user.id
        form.data['post'] = post.id
        if form.is_valid():
            form.save()
        redirect('posts:main_page', 0)
    else:
        form = CommentForm()
    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments,
                                                      'form': form, 'page_next': page_next,
                                                      'page_prev': page_prev})


def get_countries_cities(posts):
    """
    Returns the countries and cities of users who made posts
    """
    users_id = list(set(post.user.id for post in posts))
    users = CustomUser.objects.filter(id__in=users_id)
    countries = users.distinct('country')
    cities = users.distinct('city')
    countries = [user.country for user in countries]
    cities = [user.city for user in cities]
    return countries, cities


def get_filter(request, posts):
    """
    Filter: title or body, country, city
    """
    if request.GET.get('text'):
        posts = posts.filter(Q(body__contains=request.GET.get('text')) | Q(title__contains=request.GET.get('text')))
    if request.GET.get('country') or request.GET.get('city'):
        users = CustomUser.objects.all()
        if request.GET.get('country'):
            posts = posts.filter(user__in=users.filter(country=request.GET.get('country')))
        if request.GET.get('city'):
            posts = posts.filter(user__in=users.filter(city=request.GET.get('city')))
    return posts


@login_required(login_url='/common/authentication_user/')
def main_page(request, page=0):
    posts = Post.objects.annotate(Count('like_post')).order_by('-id')
    if request.method == 'GET':
        posts = get_filter(request, posts)
    countries, cities = get_countries_cities(posts)
    page = int(page)
    page_next, page_prev = get_page(page, posts)
    posts = posts[page * 5:page * 5 + 5]
    return render(request, 'posts/main_page.html', {'posts': posts, 'page_next': page_next,
                                                    'page_prev': page_prev, 'countries': countries,
                                                    'cities': cities})


@login_required(login_url='/common/authentication_user/')
def create_post(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        form.data._mutable = True
        form.data['user'] = user.id
        if form.is_valid():
            form.save()
        return redirect('posts:main_page', 0)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})
