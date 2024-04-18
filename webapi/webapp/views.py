from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_dj
from datetime import datetime
from django.utils.timezone import make_aware
import json

from .models import Author, NewsStory


# Create your views here.
def index(request):
    return HttpResponse("Index Page.")


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            author = Author.objects.get(username=username, password=password)
            request.session['author_id'] = author.id
            # user = authenticate(request, username=username, password=password)
            # if user is not None:
            #     login_dj(request, user)  # 使用 Django 提供的 login 函数登录用户
            #     return HttpResponse('Login successful', status=200, content_type='text/plain')
            # else:
            #     return HttpResponse("Username or password incorrect", status=401)
            return HttpResponse('Login successful', status=200, content_type='text/plain')
        except Author.DoesNotExist:
            return HttpResponse('Invalid username or password', status=401, content_type='text/plain')
    else:
        return HttpResponse('Invalid request method', status=405, content_type='text/plain')

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        if 'author_id' in request.session:
            del request.session['author_id']
            logout(request)
        return HttpResponse('Logout successful', status=200, content_type='text/plain')
    else:
        return HttpResponse('Invalid request method', status=405, content_type='text/plain')

@csrf_exempt
def post_story(request):
    if request.method == 'POST':
        author_id = request.session.get('author_id')
        print(author_id)
        if author_id:
            author = get_object_or_404(Author, pk=author_id)
            json_data = json.loads(request.body.decode('utf-8'))
            headline = json_data.get('headline')
            category = json_data.get('category')
            region = json_data.get('region')
            details = json_data.get('details')

            story = NewsStory.objects.create(
                headline=headline,
                category=category,
                region=region,
                author=author,
                details=details,
                date=datetime.now()
            )
            return HttpResponse(status=201, content_type='text/plain')
        else:
            return HttpResponse('User not logged in', status=401, content_type='text/plain')
    else:
        # Extract query parameters
        story_cat = request.GET.get('story_cat', '*')
        story_region = request.GET.get('story_region', '*')
        story_date = request.GET.get('story_date', '*')
        print(request.GET.get('author_id', '*'))
        # Parse the date string if it's not '*'
        if story_date != '*':
            try:
                # 尝试解析日期字符串为YYYY-MM-DD格式
                story_date = datetime.strptime(story_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                # 如果日期格式不正确，则返回错误响应
                return HttpResponse('Invalid date format. Date must be in DD/MM/YYYY format.', status=400)

        # Filter NewsStory objects based on query parameters
        if story_cat == '*':
            story_cat_filter = {}
        else:
            story_cat_filter = {'category': story_cat}

        if story_region == '*':
            story_region_filter = {}
        else:
            story_region_filter = {'region': story_region}

        if story_date == '*':
            story_date_filter = {}
        else:
            story_date_filter = {'date__gte': story_date}

        print(story_cat,story_region,story_date)
        stories = NewsStory.objects.filter(**story_cat_filter, **story_region_filter, **story_date_filter)

        # If stories are found, prepare JSON response
        if stories:
            story_list = []
            for story in stories:
                story_data = {
                    'key': str(story.pk),
                    'headline': story.headline,
                    'story_cat': story.category,
                    'story_region': story.region,
                    'author': story.author.name,
                    'story_date': story.date.strftime('%Y-%m-%d'),
                    'story_details': story.details
                }
                story_list.append(story_data)

            return JsonResponse({'stories': story_list})
        else:
            # If no stories are found, return 404 status code with a message
            return HttpResponse('No stories found', status=404, content_type='text/plain')

@csrf_exempt
def get_stories(request):
    if request.method == 'GET':
        # Extract query parameters
        story_cat = request.GET.get('story_cat', '*')
        story_region = request.GET.get('story_region', '*')
        story_date = request.GET.get('story_date', '*')

        # Filter NewsStory objects based on query parameters
        stories = NewsStory.objects.filter(
            category=story_cat,
            region=story_region,
            date__gte=story_date
        )

        # If stories are found, prepare JSON response
        if stories:
            story_list = []
            for story in stories:
                story_data = {
                    'key': str(story.pk),
                    'headline': story.headline,
                    'story_cat': story.category,
                    'story_region': story.region,
                    'author': story.author.name,
                    'story_date': story.date.strftime('%Y-%m-%d'),
                    'story_details': story.details
                }
                story_list.append(story_data)

            return JsonResponse({'stories': story_list})
        else:
            # If no stories are found, return 404 status code with a message
            return HttpResponse('No stories found', status=404, content_type='text/plain')
    else:
        # If the request method is not GET, return 405 status code with a message
        return HttpResponse('Invalid request method', status=405, content_type='text/plain')

@csrf_exempt
def delete_story(request, key):
    if request.method == 'DELETE':
        author_id = request.session.get('author_id')
        print(author_id)
        if author_id:
            try:
                story = NewsStory.objects.get(pk=key, author_id=author_id)
                story.delete()
                return HttpResponse(status=200, content_type='text/plain')
            except NewsStory.DoesNotExist:
                return HttpResponse('Story not found', status=404, content_type='text/plain')
            except Exception as e:
                return HttpResponse(str(e), status=503, content_type='text/plain')
        else:
            return HttpResponse('User not logged in', status=401, content_type='text/plain')
    else:
        return HttpResponse('Invalid request method', status=405, content_type='text/plain')
