
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.add_post, name="add_post"),
    path("posts/<str:post_owner>/<str:page>", views.load_posts, name="load_posts"),
    path("profiles/<str:post_owner>", views.load_profile, name="load_profile"),
    path("follow/<str:profile_id>", views.follow_profile, name="follow_profile"),
    path("like/<str:post_id>", views.like_post, name="like_post"),
    path("edit/<str:post_id>", views.edit_post, name="edit_post"),
    path("update_image/<str:profile_id>", views.update_image, name="update_image")
]
