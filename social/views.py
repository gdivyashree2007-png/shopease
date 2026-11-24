from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .forms import PostForm, ProfileForm, RegistrationForm
from .models import Comment, Follow, Like, Post


def _posts_for_page(request, queryset, title, subtitle=""):
    queryset = queryset.select_related("author", "author__profile").annotate(
        likes_total=Count("likes", distinct=True), comments_total=Count("comments", distinct=True)
    ).prefetch_related("comments__author__profile").order_by("-created_at", "-id")
    page = Paginator(queryset, 12).get_page(request.GET.get("page"))
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(Like.objects.filter(user=request.user, post__in=page.object_list).values_list("post_id", flat=True))
    return render(request, "social/feed.html", {
        "posts": page.object_list, "page_obj": page, "title": title, "subtitle": subtitle,
        "liked_post_ids": liked_post_ids,
    })


def home(request):
    if request.user.is_authenticated:
        followed_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
        posts = Post.objects.filter(Q(author=request.user) | Q(author_id__in=followed_ids))
        return _posts_for_page(request, posts, "Your feed", "Notes from people you follow, plus your own.")
    return _posts_for_page(request, Post.objects.all(), "A little more social", "Find your people. Share what matters.")


def explore(request):
    return _posts_for_page(request, Post.objects.all(), "Explore", "Good ideas have a way of finding you.")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to SocialHub, {user.username}.")
        return redirect("home")
    return render(request, "social/register.html", {"form": form})


def profile(request, username):
    person = get_object_or_404(User.objects.select_related("profile"), username=username)
    posts = person.posts.select_related("author", "author__profile").annotate(
        likes_total=Count("likes", distinct=True), comments_total=Count("comments", distinct=True)
    ).prefetch_related("comments__author__profile").order_by("-created_at", "-id")
    followed = request.user.is_authenticated and Follow.objects.filter(follower=request.user, following=person).exists()
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(Like.objects.filter(user=request.user, post__in=posts).values_list("post_id", flat=True))
    context = {
        "person": person, "posts": posts, "followed": followed,
        "follower_count": person.follower_links.count(), "following_count": person.following_links.count(),
        "liked_post_ids": liked_post_ids,
    }
    return render(request, "social/profile.html", context)


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        messages.error(request, "You can only edit your own profile.")
        return redirect("profile", username=username)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile", username=request.user.username)
    return render(request, "social/profile_edit.html", {"form": form})


def follow_list(request, username, kind):
    person = get_object_or_404(User, username=username)
    if kind == "followers":
        links = person.follower_links.select_related("follower", "follower__profile")
        people = [link.follower for link in links]
        heading = f"People following {person.username}"
    else:
        links = person.following_links.select_related("following", "following__profile")
        people = [link.following for link in links]
        heading = f"People {person.username} follows"
    return render(request, "social/user_list.html", {"people": people, "person": person, "heading": heading})


def search(request):
    query = request.GET.get("q", "").strip()[:80]
    people = User.objects.none()
    if query:
        people = User.objects.filter(username__icontains=query).select_related("profile").order_by("username")[:40]
    return render(request, "social/search.html", {"query": query, "people": people})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post is live.")
        return redirect(post.get_absolute_url())
    return render(request, "social/post_form.html", {"form": form, "heading": "Create a post"})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        messages.error(request, "You can only edit your own posts.")
        return redirect(post.get_absolute_url())
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your post has been updated.")
        return redirect(post.get_absolute_url())
    return render(request, "social/post_form.html", {"form": form, "heading": "Edit your post", "post": post})


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author_id != request.user.id:
        return JsonResponse({"error": "You can only delete your own posts."}, status=403)
    post.delete()
    messages.success(request, "Your post has been deleted.")
    return redirect("profile", username=request.user.username)


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author", "author__profile").annotate(
        likes_total=Count("likes", distinct=True), comments_total=Count("comments", distinct=True)
    ).prefetch_related("comments__author__profile"), pk=pk)
    liked_post_ids = set()
    if request.user.is_authenticated and Like.objects.filter(post=post, user=request.user).exists():
        liked_post_ids.add(post.pk)
    return render(request, "social/post_detail.html", {"post": post, "liked_post_ids": liked_post_ids})


@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({"liked": created, "count": post.likes.count()})


@login_required
@require_POST
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Write a comment before posting."}, status=400)
    if len(text) > 500:
        return JsonResponse({"error": "Comments must be 500 characters or fewer."}, status=400)
    comment = Comment.objects.create(post=post, author=request.user, text=text)
    html = render_to_string("social/partials/comment.html", {"comment": comment, "request": request})
    return JsonResponse({"html": html, "count": post.comments.count(), "id": comment.pk})


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)
    if comment.author_id != request.user.id:
        return JsonResponse({"error": "You can only delete your own comments."}, status=403)
    post = comment.post
    comment.delete()
    return JsonResponse({"deleted": pk, "count": post.comments.count()})


@login_required
@require_POST
def follow_toggle(request, username):
    person = get_object_or_404(User, username=username)
    if person.pk == request.user.pk:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)
    relation, created = Follow.objects.get_or_create(follower=request.user, following=person)
    if not created:
        relation.delete()
    return JsonResponse({"following": created, "count": person.follower_links.count()})
