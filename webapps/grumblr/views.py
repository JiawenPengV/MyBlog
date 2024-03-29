# Create your views here.
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from grumblr.models import *
from grumblr.forms import *

from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.core.mail import send_mail
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse


@login_required
@transaction.atomic
def get_changes(request, time="1970-01-01T00:00+00:00"):
    try:

        max_time = Post.get_max_time()
        posts = Post.get_changes(time)
    except ObjectDoesNotExist:
        raise Http404

    context = {"max_time":max_time, "posts":posts,"username":request.user.username}
    return render(request, 'grumblr/posts.json', context, content_type='application/json')

@login_required
@transaction.atomic
def get_comments_changes(request, post_id, time="1970-01-01T00:00+00:00"):
    if time == 'undefined':
        time="1970-01-01T00:00+00:00"
    try:
        max_time = Comment.get_max_time()

        comments = Comment.get_changes(post_id, time)

    except ObjectDoesNotExist:
        raise Http404

    context = {"max_time":max_time, "comments":comments}
    return render(request, 'grumblr/comments.json', context, content_type='application/json')


@login_required
@transaction.atomic
def add_comment(request, post_id):
    context = {}

    if request.method == 'GET':
        context['form'] = CommentForm()
        return render(request, 'grumblr/global_stream.html', context)

    form = CommentForm(request.POST)
    context['form'] = form


    if not form.is_valid():
        return render(request, 'grumblr/global_stream.html', context)

    try:
        post = Post.objects.get(id=post_id)
    except ObjectDoesNotExist:
        return HttpResponse("The post did not exist")

    new_comment = Comment(content=form.cleaned_data['comment'], user=request.user, post=post)
    new_comment.save()

    comments = Comment.objects.filter(post=post).order_by("-time")
    context['comments'] = comments

    return render(request, 'grumblr/comments.json', context, content_type='application/json')

# Returns all recent changes to the database, as JSON
@login_required
@transaction.atomic
def get_changes_follower(request, time="1970-01-01T00:00+00:00"):
    try:
        max_time = Post.get_max_time_follower(request.user)
        posts = Post.get_changes_follower(request.user, time)

    except ObjectDoesNotExist:
        raise Http404

    context = {"max_time":max_time, "posts":posts, "username":request.user.username}
    return render(request, 'grumblr/posts.json', context, content_type='application/json')


@login_required
@transaction.atomic
def get_comments_changes_for_post(request, post_id, time="1970-01-01T00:00+00:00"):
    if time == 'undefined' or time == '':
        time="1970-01-01T00:00+00:00"
    try:
        max_time = Comment.get_max_time_follower(post_id)

        comments = Comment.get_changes(post_id, time)

    except ObjectDoesNotExist:
        raise Http404
    
    context = {"max_time":max_time, "comments":comments}
    return render(request, 'grumblr/comments.json', context, content_type='application/json')


@login_required
@transaction.atomic
def get_changes_profile(request, username, time="1970-01-01T00:00+00:00"):
    try:
        profile_user = User.objects.get(username=username)
        max_time = Post.get_max_time_profile(profile_user)
        posts = Post.get_changes_profile(profile_user, time)
    
    except ObjectDoesNotExist:
        raise Http404


    
    context = {"max_time":max_time, "posts":posts,"username":request.user.username}
    return render(request, 'grumblr/posts.json', context, content_type='application/json')



@login_required
def home(request):
    
    posts = Post.objects.all().order_by("-time")
    try:
        profile = Profile.objects.





        get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404


    followees = profile.followees.all()
    request_user_profile = Profile.objects.get(user=request.user)
    return render(request, 'grumblr/global_stream.html', {'request_user_profile':request_user_profile,'posts' : posts, 'user' : request.user, 'followees' : followees})


@login_required
def post(request):
    context = {}
    if request.method == 'GET':
        context['form'] = PostForm()
        return render(request, 'grumblr/global_stream.html', context)

    form = PostForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'grumblr/global_stream.html', context)

    new_post = Post(content=form.cleaned_data['post'], user=request.user)
    new_post.save()

    request_user_profile = Profile.objects.filter(user=request.user)
    
    posts = Post.objects.all().order_by("-time")
    context['request_user_profile']=request_user_profile
    context['posts'] = posts
    context['username'] = request.user.username;
    return render(request, 'grumblr/posts.json', context, content_type='application/json')

@login_required
def delete(request, id):
    errors = []

    try:
        item_to_delete = Post.objects.get(id=id, user=request.user)
        item_to_delete.delete()
    except ObjectDoesNotExist:
        raise Http404


    try:
        user_profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404
    request_user_profile = Profile.objects.filter(user=request.user)
    
    posts = Post.objects.filter(user=request.user).order_by('-time')
    context = {'posts' : posts, 'errors' : errors, 'profile' : user_profile,'request_user_profile':request_user_profile}
    return redirect('/')


@login_required
def profile(request, username):
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

   
    posts_of_user = Post.objects.filter(user=post_user).order_by("-time")
   
    try:
        post_user_profile = Profile.objects.get(user=post_user)
    except ObjectDoesNotExist:
        raise Http404

    followees = request.user.profile.followees.all()

    request_user_profile = Profile.objects.get(user=request.user)
    context = {'posts' : posts_of_user, 'user' : post_user, 'profile' : post_user_profile, 'followees' : followees,'request_user_profile': request_user_profile}
    return render(request, 'grumblr/profile.html', context)

@login_required
def follow(request, username):
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    try:
        request_user_profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404

    request_user_profile.followees.add(post_user);
    request_user_profile.save()

    request_user_followees=request_user_profile.followees.all()

    post_user_profile=Profile.objects.get(user=post_user)
    followees = post_user_profile.followees.all()
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    request_user_profile = Profile.objects.filter(user=request.user)
 
    context = {'posts' : posts, 'user' : post_user, 'profile' : post_user_profile, 'followees' : request_user_followees,'request_user_profile': request_user_profile}
    return redirect('/grumblr/profile/' + username)

@login_required
def unfollow(request, username):
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404

    profile.followees.remove(post_user);
    profile.save()
    post_user_profile=Profile.objects.get(user=post_user)
    
    request_user_followees = profile.followees.all();
    followees = post_user_profile.followees.all()
    
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    request_user_profile = Profile.objects.get(user=request.user)
    
    context = {'posts' : posts, 'user' : post_user, 'profile' : post_user_profile, 'followees' : request_user_followees,'request_user_profile': request_user_profile}
    return redirect('/grumblr/profile/' + username)

@login_required
def follower_stream(request):
    
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404

    followees = profile.followees.all()
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    request_user_profile = Profile.objects.get(user=request.user)
    return render(request, 'grumblr/follower_stream.html', {'posts' : posts, 'user' : request.user, 'followees' : followees,'request_user_profile': request_user_profile})


@login_required()
def change_password(request):
    errors = []
    context = {}
    try:
        profile = Profile.objects.get(user=request.user)
        request_user_profile = Profile.objects.filter(user=request.user)
    
    except ObjectDoesNotExist:
        raise Http404


    if request.method == 'GET':
        context['form'] = ChangePasswordForm()
        context['profile'] = profile
        context['request_user_profile'] =request_user_profile
        return render(request, 'grumblr/edit_profile.html', context)

    form = ChangePasswordForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        context['profile'] = profile
        context['request_user_profile'] =request_user_profile
        
        return render(request, 'grumblr/edit_profile.html', context)

    user = request.user
    user.set_password(form.cleaned_data['password'])
    user.save()


    posts = Post.objects.filter(user=request.user).order_by("-time")

    user = authenticate(username=user.username, \
                            password=user.password)
    login(request, user)
    request_user_profile = Profile.objects.filter(user=request.user)
    
    context = {'posts' : posts, 'errors' : errors, 'user' : request.user, 'profile' : profile,'request_user_profile':request_user_profile}
    return redirect('/grumblr/profile/' + request.user.username)


@login_required
def edit_profile(request):
    context = {}
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'GET':
        context['form'] = EditProfileForm()
        context['profile'] = profile
        return render(request, 'grumblr/edit_profile.html', context)
   

  
    form = EditProfileForm(request.POST, request.FILES)
    context['form'] = form

    if not form.is_valid():
        context['profile'] = profile
      
        return render(request, 'grumblr/edit_profile.html', context)

   
    posts_of_user = Post.objects.filter(user=request.user).order_by("-time")

    profile.age=form.cleaned_data['age']
    profile.bio=form.cleaned_data['bio']

    user = request.user
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    
    if form.cleaned_data['picture']:
        profile.picture=form.cleaned_data['picture']

    profile.save()
    request.user.save()
    
    request_user_profile = Profile.objects.filter(user=request.user)
    
    context = {'posts' : posts_of_user, 'user' : request.user, 'profile' : profile,'request_user_profile':request_user_profile}
    return redirect('/grumblr/profile/' + request.user.username)

# get the user profile photos
@login_required
def get_profile_photo(request, username):
    
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    try:
        profile = Profile.objects.get(user=user)
    except ObjectDoesNotExist:
        raise Http404

    if not profile.picture:
        raise Http404
    content_type = guess_type(profile.picture.name)
   

    return HttpResponse(profile.picture, content_type=content_type)

@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'grumblr/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    
    if not form.is_valid():
        return render(request, 'grumblr/register.html', context)


    new_user = User.objects.create_user(username=form.cleaned_data['username'], \
                                        password=form.cleaned_data['password'], \
                                        first_name=form.cleaned_data['first_name'], \
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'],
                                        is_active=False)
    new_user.save()


    token = default_token_generator.make_token(new_user)

    email_body="""
    Welcome to Grumblr! Please click the link below to verify your email
    http://%s%s
    """ % (request.get_host(),
           reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Grumblr - Verify your email address",
              message=email_body,
              from_email="jiawenpeng07@gmail.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'grumblr/email_confirmation.html', context)

@transaction.atomic
def reset_pass(request):
    return render(request, 'grumblr/password_reset.html')


@transaction.atomic
def reset_password(request):
    context = {}
    if request.method == 'GET':
        context['form'] = EmailResetForm()
        return render(request, 'grumblr/password_reset.html', context)

    form = EmailResetForm(request.POST)
    context['form'] = form

  
    if not form.is_valid():
        return render(request, 'grumblr/password_reset.html', context)
    try:
        user= User.objects.get(email=form.cleaned_data['email'])
    except ObjectDoesNotExist:
        raise Http404

    token = default_token_generator.make_token(user)

    email_body="""
    Please click the link below to verify your email address
    and complete the password resetting of your account:
    http://%s%s
    """ % (request.get_host(),
           reverse('password_confirm', args=(user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="jiawenpeng07@gmail.com",
              recipient_list=[user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'grumblr/password_reset_confirmation.html', context)


@transaction.atomic
def password_reset_confirmation(request, username, token):
    context = {}
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    if not default_token_generator.check_token(user, token):

        return render(request, 'grumblr/error_page.html', context)

    context['user'] = user
    return render(request, 'grumblr/password_reset_form.html', context)

@transaction.atomic
def password_reset_form(request, username):
    context = {}
    if request.method == 'GET':
        context['form'] = ChangePasswordForm()
        return render(request, 'grumblr/password_reset_form.html', context)

    form = ChangePasswordForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/password_reset_form.html', context)

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    user.set_password(form.cleaned_data['password'])
    user.save()

    return redirect('/grumblr/global_stream')


@transaction.atomic
def registration_confirmation(request, username, token):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    if not default_token_generator.check_token(user, token):
        
        return render(request, 'grumblr/error_page.html', {})

    user.is_active=True
    user.save()

    new_profile = Profile(age=0, user=user, bio='Introduction is here')
    new_profile.save()

    
    login(request, user)

    return redirect('/grumblr/global_stream')
