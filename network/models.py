from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Profile(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    followers = models.ManyToManyField(User, related_name="user_following")    # ( Guidance: https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_one/ )
    following = models.IntegerField(max_length=3, default=0)
    is_user = models.BooleanField(default=False)
    is_followed_by_user = models.BooleanField(default=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner_id,
            "name": self.name,
            "image": self.image,
            "followers": self.followers.count(),      
            "following": self.following,
            "is_user": self.is_user,
            "is_followed_by_user": self.is_followed_by_user
        }


class Post(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts")
    is_liked_by_user = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "owner_id": self.owner_id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.count(),
            "is_liked_by_user": self.is_liked_by_user
        }


