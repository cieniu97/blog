from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
# import numpy as np

from .models import Post, Comment

def index(request):
    latest_post_list = Post.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

    categories = {}
    for post in Post.objects.all():
        if post.category_text not in categories:
            categories[post.category_text] = 1
        else:
            categories[post.category_text] += 1
    
    categories = sorted(categories.items(), key=lambda item: item[1], reverse=True)
    categories = categories[0:10]
    context = {'latest_post_list': latest_post_list, 'categories': categories}

    return render(request, 'polls/index.html', context)
    
    

class ShowView(generic.DetailView):
    model = Post
    template_name = 'polls/show.html'
    
    def get_queryset(self):
        """
        Excludes any posts that aren't published yet.
        """
        return Post.objects.filter(pub_date__lte=timezone.now())


def photos(request):
    photos = []
    for post in Post.objects.all():
        photos.append(post.image_file.url)
    context = {'photos': photos}
    return render(request, 'polls/photos.html', context)

def info(request):
    return render(request, 'polls/info.html')

def search(request, title):
    results = Post.objects.filter(title_text__icontains=title)
    context = {'results': results}
    return render(request, 'polls/search.html', context)

def categories(request, category):
    results = Post.objects.filter(category_text__icontains=category)
    context = {'results': results}
    return render(request, 'polls/categories.html', context)

def register(request):
    return render(request, 'polls/register.html')

def login(request):
    return render(request, 'polls/login.html')

def storeUser(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    confirmation_password = request.POST['confirmation_password']
    if(password == confirmation_password):
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registered in')

        return render(request, 'polls/login.html')
    else:
        messages.error(request, 'Passwords not matching')
        return render(request, 'polls/register.html')
    

def loginUser(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        django_login(request, user)
        messages.success(request, 'Loged in')
        return redirect('index')
    else:
        messages.error(request, 'Wrong credentials')
        return render(request, 'polls/login.html')

def logout(request):
    django_logout(request)
    return redirect('index')

def storeComment(request, post_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Commenting is restricted for authenticated users')
        return redirect('show', pk=post_id)
    else:
        comment = Comment(body_text=request.POST['body'], name=request.user.id, post = get_object_or_404(Post, pk=post_id))
        comment.save()
        return redirect('show', pk=post_id)    