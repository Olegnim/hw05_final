from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'group': group,
        'posts': posts,
        'paginator': paginator,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new.html', {'form': form})
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    user_id = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('author').filter(
        author=user_id).order_by('-pub_date')
    count = Post.objects.select_related(
        'author').filter(author=user_id).count()
    countfollowing = Follow.objects.filter(
        user=user_id).count()
    countfollower = Follow.objects.filter(
        author=user_id).count()
    if request.user.is_authenticated:
        following = False
        if Follow.objects.filter(author=user_id, user=request.user).exists():
            following = True
    else:
        following = False
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': user_id,
        'count': count,
        'paginator': paginator,
        'profile': user_id,
        'countfollower': countfollower,
        'countfollowing': countfollowing,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=username)
    countfollowing = Follow.objects.filter(
        user=username).count()
    countfollower = Follow.objects.filter(
        author=username).count()
    count = Post.objects.select_related(
        'author').filter(author=username).count()
    all_comments = Comment.objects.filter(post_id=post_id)
    if request.method != 'POST':
        form = CommentForm()
        context = {
            'post': post,
            'author': username,
            'count': count,
            'username': username,
            'post_id': post_id,
            'comments': all_comments,
            'form': form,
            'countfollower': countfollower,
            'countfollowing': countfollowing,
        }
        return render(request, 'post.html', context)
    form = CommentForm(request.POST)
    if form.is_valid():
        comments = form.save(commit=False)
        comments.author = request.user
        comments.post_id = post_id
        form.save()
        return redirect('post', username=username, post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'author': username,
        'count': count,
        'username': username,
        'post_id': post_id,
        'comments': all_comments,
        'form': form,
    }
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=username)
    countfollowing = Follow.objects.filter(
        user=username).count()
    countfollower = Follow.objects.filter(
        author=username).count()
    count = Post.objects.select_related(
        'author').filter(author=username).count()
    all_comments = Comment.objects.filter(post_id=post_id)
    if request.method != 'POST':
        form = CommentForm()
        context = {
            'post': post,
            'author': username,
            'count': count,
            'username': username,
            'post_id': post_id,
            'comments': all_comments,
            'form': form,
            'countfollower': countfollower,
            'countfollowing': countfollowing,
        }
        return render(request, 'post.html', context)
    form = CommentForm(request.POST)
    if form.is_valid():
        comments = form.save(commit=False)
        comments.author = request.user
        comments.post_id = post_id
        form.save()
        return redirect('post', username=username, post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'author': username,
        'count': count,
        'username': username,
        'post_id': post_id,
        'comments': all_comments,
        'form': form,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=username)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    if request.method != 'POST':
        form = PostForm(instance=post)
        return render(request,
                      'post_new.html',
                      {
                          'form': form,
                          'post': post,
                      }
                      )
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        form.save()
        return redirect('post', username=username, post_id=post_id)
    form = PostForm()
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'post_new.html', context)


@login_required
def follow_index(request):
    follow_list = []
    follow_list_id = Follow.objects.filter(user=request.user).in_bulk()
    for i in follow_list_id:
        follow_list.append(follow_list_id[i].author)
    post_list = Post.objects.filter(author__in=follow_list)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return follow_index(request)
    Follow.objects.get_or_create(user=request.user, author=author)
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return profile(request, username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return profile(request, username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
