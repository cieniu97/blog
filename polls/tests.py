import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Post, Comment
from django.contrib.auth.models import User

import lorem
import random
import string

def create_post(title_text, days, category = "test category"):
    """
    Create a post with the given `title_text` and published the
    given number of `days` offset to now (negative for posts published
    in the past, positive for posts that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    body = lorem.text()
    return Post.objects.create(title_text=title_text, pub_date=time, body_text = body, category_text=category)

def get_categories():
    categories = {}
    for post in Post.objects.all():
        if post.category_text not in categories:
            categories[post.category_text] = 1
        else:
            categories[post.category_text] += 1
    
    categories = sorted(categories.items(), key=lambda item: item[1], reverse=True)
    categories = categories[0:10]
    return categories

class PostModelTests(TestCase):
    def test_no_posts(self):
        """
        If no posts exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])
        
    def test_past_post(self):
        """
        Posts with a pub_date in the past are displayed on the
        index page.
        """
        post = create_post(title_text="Past post.", days=-30)
        response = self.client.get(reverse('index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            [post],
        )

    def test_future_post(self):
        """
        Posts with a pub_date in the future aren't displayed on
        the index page.
        """
        create_post(title_text="Future post.", days=30)
        response = self.client.get(reverse('index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])

    def test_future_post_and_past_post(self):
        """
        Even if both past and future posts exist, only past posts
        are displayed.
        """
        post = create_post(title_text="Past post.", days=-30)
        create_post(title_text="Future post.", days=30)
        response = self.client.get(reverse('index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            [post],
        )

    def test_two_past_posts(self):
        """
        The posts index page may display multiple posts.
        """
        post1 = create_post(title_text="Past post 1.", days=-30)
        post2 = create_post(title_text="Past post 2.", days=-5)
        response = self.client.get(reverse('index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            [post2, post1],
        )

    def test_was_published_recently_with_future_post(self):
        """
        was_published_recently() returns False for post whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_post = Post(pub_date=time)
        self.assertIs(future_post.was_published_recently(), False)

    def test_was_published_recently_with_old_post(self):
        """
        was_published_recently() returns False for posts whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_post = Post(pub_date=time)
        self.assertIs(old_post.was_published_recently(), False)

    def test_was_published_recently_with_recent_post(self):
        """
        was_published_recently() returns True for posts whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_post = Post(pub_date=time)
        self.assertIs(recent_post.was_published_recently(), True)

class PostDetailViewTests(TestCase):
    def test_future_post(self):
        """
        The detail view of a post with a pub_date in the future
        returns a 404 not found.
        """
        future_post = create_post(title_text='Future post.', days=5)
        url = reverse('show', args=(future_post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_post(self):
        """
        The detail view of a post with a pub_date in the past
        displays the post's text.
        """
        past_post = create_post(title_text='Past Question.', days=-5)
        url = reverse('show', args=(past_post.id,))
        response = self.client.get(url)
        self.assertContains(response, past_post.title_text)

    def test_comment(self):
        """
        The detail view of a post contains added comment
        """
        past_post = create_post(title_text='Past Question.', days=-5)
        body = lorem.text()
        user = User.objects.create_user(username="testUser", email="testEmail@email.com", password="password")
        post_comment = Comment.objects.create(post = past_post, user = user, body_text = body)
        response = self.client.get(reverse('show', args=(past_post.id,)))
        self.assertContains(response, post_comment.body_text)

class PagesStatusTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_photos(self):
        response = self.client.get(reverse('photos'))
        self.assertEqual(response.status_code, 200)
    
    def test_info(self):
        response = self.client.get(reverse('info'))
        self.assertEqual(response.status_code, 200)
    
    def test_search(self):
        response = self.client.get(reverse('search',kwargs={'title':"".join(random.choices(string.ascii_lowercase, k=5))}))
        self.assertEqual(response.status_code, 200)
    
    def test_register(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

class CategoriesTests(TestCase):
    def test_trending_category(self):
        """
        Create 50 new posts with the random category from ten listed.
        Create more than top trending category new posts to see if it will show up in
        index view on trending categories
        """
        past_categories=[
            'category1',
            'category2',
            'category3',
            'category4',
            'category5',
            'category6',
            'category7',
            'category8',
            'category9',
            'category10',
            ]
        for m in range(50):
            create_post("title_text", 0, random.choice(past_categories))
        categories = get_categories()
        category = "tredning category"
        for n in range(0, categories[0][1]):
            create_post("title_text", 0, category)
        response = self.client.get(reverse('index'))
        self.assertContains(response, category)
    
    def test_not_trending_category(self):
        """
        Create 50 new posts with the random category from ten listed.
        Create more than top trending category new posts to see if it will show up in
        index view on trending categories
        """
        past_categories=[
            'category1',
            'category2',
            'category3',
            'category4',
            'category5',
            'category6',
            'category7',
            'category8',
            'category9',
            'category10',
            ]
        for m in range(50):
            create_post("title_text", 0, random.choice(past_categories))
        categories = get_categories()
        category = "tredning category"
        for n in range(1, categories[9][1]):
            create_post("title_text", 0, category)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, category)
