from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

POSTS_PER_PAGE = 10


# Main page function definition
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'request': request,
    }
    return render(request, template, context)


# Group post function definition
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'request': request,
    }
    return render(request, template, context)


# User profile function definition
def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if not request.user.is_anonymous:
        authors_ids = Follow.objects.filter(
            user=request.user
        ).values_list('author_id', flat=True)
        if author.id in authors_ids:
            following = True
        else:
            following = False
    context = {
        'author': author,
        'username': username,
        'page_obj': page_obj,
        'post_list': post_list,
        'following': following,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id).all()
    post = get_object_or_404(Post.objects.select_related('group'), id=post_id)
    author_posts = Post.objects.filter(author=post.author)
    context = {
        'post': post,
        'post_id': post_id,
        'author_posts': author_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if request.user.username == post.author.username:
        form = PostForm(instance=post)
        if request.method == 'POST':
            form = PostForm(request.POST,
                            files=request.FILES or None,
                            instance=post
                            )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post.id)
        context = {
            'form': form,
            'is_edit': is_edit,
        }
        return render(request, template, context)
    else:
        return redirect('posts:post_detail', post_id=post.id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    authors_ids = Follow.objects.filter(
        user=request.user
    ).values_list('author_id', flat=True)
    post_list = Post.objects.filter(author_id__in=authors_ids)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'request': request,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    context = {
        'author': author,
    }
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', author)
    return render(request, template, context)


@login_required
def profile_unfollow(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    context = {
        'author': author,
    }
    if request.user != author:
        person = Follow.objects.get(user=request.user, author=author)
        person.delete()
        return redirect('posts:profile', author)
    return render(request, template, context)
