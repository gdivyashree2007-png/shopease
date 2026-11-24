from django.contrib.auth import views as auth_views
from django.urls import path
from .forms import LoginForm
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("explore/", views.explore, name="explore"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="social/login.html", authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search/", views.search, name="search"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/edit/", views.edit_profile, name="edit_profile"),
    path("u/<str:username>/followers/", views.follow_list, {"kind": "followers"}, name="followers"),
    path("u/<str:username>/following/", views.follow_list, {"kind": "following"}, name="following"),
    path("posts/new/", views.post_create, name="post_create"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("posts/<int:pk>/comments/", views.comment_create, name="comment_create"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
]
