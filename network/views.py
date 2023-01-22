import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator   

from .models import User, Post, Profile


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:

            # Save user
            user = User.objects.create_user(username, email, password)
            user.save()

            # Create user profile
            person = User.objects.get(username=username)
            new_user_profile = Profile(
                owner = person,  
                name = person.username,         
                image = None,
            )
            new_user_profile.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def add_post(request):

    # If request method is POST
    if request.method == "POST":

        # Get post data
        data = json.loads(request.body)
        owner = User.objects.get(username=request.user)
        content = data.get("content")
        timestamp = data.get("timestamp")

        # Save post to database
        new_post = Post(
            owner = owner,           
            content = content,
            timestamp = timestamp            
        )
        new_post.save()

        # Confirm submission
        return JsonResponse({"message": "Post submitted successfully."}, status=201)

    # If request method is not POST, return an error message
    elif request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)


def load_posts(request, post_owner, page):

    # If post_owner specified as "all", get all posts from database
    if post_owner == "all":
        posts = Post.objects.all()

     # If posts specified as "following", get followed posts       ( Combining and ordering multiple lists: https://stackoverflow.com/questions/64985718/attributeerror-list-object-has-no-attribute-order-by and https://stackoverflow.com/questions/1058135/django-convert-a-list-back-to-a-queryset)
    elif post_owner == "following":
        followed_profiles = request.user.user_following.all()
        followed_user_ids = []
        for profile in followed_profiles:
            followed_user_id = profile.owner_id
            followed_user_ids.append(followed_user_id)
        posts = Post.objects.filter(owner_id__in=followed_user_ids)

    # Otherwise get specified posts
    else:
        posts = Post.objects.filter(owner_id=post_owner)

    # Sort posts newest item first
    posts = posts.order_by("-timestamp").all()

    # Paginate posts
    paginator = Paginator(posts, 10)
    current_page = page
    pages = paginator.num_pages
    page_object = paginator.get_page(current_page)
    has_previous = page_object.has_previous()
    has_next = page_object.has_next()

    # Return paginated posts  
    posts = list(posts)
    return JsonResponse({"posts": [post.serialize() for post in page_object], "pages": pages, "current_page": current_page, "has_previous": has_previous, "has_next": has_next, "user_authenticated": request.user.is_authenticated, "user_id": request.user.id}, safe=False)


def load_profile(request, post_owner):

    # Query for requested profile
    try:
        profile = Profile.objects.get(owner=post_owner)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    # If user is profile owner, confirm in JSON response to remove follow button at front end
    if profile.owner == request.user:
        profile.is_user = True
    else: 
        profile.is_user = False

    # Check if user already following profile
    if request.user in profile.followers.all():
        profile.is_followed_by_user = True
    else:
        profile.is_followed_by_user = False

    # Count profiles followed 
    profile.following = profile.owner.user_following.count()

    # Return profile
    if request.method == "GET":
        return JsonResponse({"profile": profile.serialize(), "user_authenticated": request.user.is_authenticated}, safe=False)   # ( Safe:true/false https://dev.to/chryzcode/django-json-response-safe-false-4f9i )


@login_required
def follow_profile(request, profile_id):

     # Check request method is GET
    if request.method == "GET":
        
        # Get profile object
        profile = Profile.objects.get(id=profile_id)

        # If user is not already following profile
        if request.user not in profile.followers.all():

            # Add user to followers
            profile.followers.add(request.user)

            # Redirect user to followed posts
            return JsonResponse({"message": "Now following this profile.", "profile_owner": profile.owner_id}, status=200)

        else:
            # If user is already a follower, remove from list
            profile.followers.remove(request.user)
            return JsonResponse({"message": "No longer following this profile.", "profile_owner": profile.owner_id}, status=200)


@login_required
def like_post(request, post_id):
    
    # Check request method is GET
    if request.method == "GET":
        
        # Retrieve post
        try: 
            post = Post.objects.get(id=post_id)
        except AttributeError:
            return JsonResponse({"error": "Not logged in."}, status=404)

        # If user has not already liked the post, mark post as liked
        if post not in request.user.liked_posts.all():
            post.is_liked_by_user = True
            post.likes.add(request.user)

        # If user has already liked the post, update flag to false 
        else:
            post.is_liked_by_user = False
            post.likes.remove(request.user)

        # Return liked status and count
        return JsonResponse({"post_id": post_id, "is_liked_by_user": post.is_liked_by_user, "likes": post.likes.count()}, status=200)
            

@login_required
def edit_post(request, post_id):
    
    # Check user is post owner
    post = Post.objects.get(id=post_id)
    if request.user == post.owner:

        # If request method is PUT
        if request.method == "PUT":

            # Get edited post data
            data = json.loads(request.body)
            content = data.get("content")

            # Save edited content
            post.content = content
            post.save()

            # Confirm update
            return JsonResponse({"message": "Edits saved.", "content": post.content}, status=200)

    # If user is not the post owner, display error message
    else: 
        return JsonResponse({"message": "Not authorised."}, status=403)


@login_required
def update_image(request, profile_id):

    # If request method is PUT
    if request.method == "PUT":

        # Get request data
        data = json.loads(request.body)
        image = data.get("image")
    
        # Retrieve profile
        profile = Profile.objects.get(id=profile_id)

        # Save new image
        profile.image = image
        profile.save()

        # Confirm udpate
        return JsonResponse({"message": "Profile image updated."}, status=200)
