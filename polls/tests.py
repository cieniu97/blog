import datetime
from time import sleep
from tkinter.tix import Tree
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Post, Comment
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from . import urls

import os
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
        for n in range(1, categories[len(categories)-1][1]):
            create_post("title_text", 0, category)
        response = self.client.get(reverse('index'))
        if len(categories)>10:
            self.assertNotContains(response, category)
        else:
            self.assertContains(response, category)

class TestSelenium(TestCase):
    def setUp(self):
        self.CHROMEDRIVER_PATH = 'chromedriver'
        self.WINDOW_SIZE = "1920,1080"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=%s" % self.WINDOW_SIZE)
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')    
        self.driver = webdriver.Chrome(executable_path=self.CHROMEDRIVER_PATH,chrome_options=self.chrome_options)
        self.address = "http://localhost:8000/"
        self.driver.get(self.address)

    def test_is_working(self):
        # sprawdza poprawność tytułu uruchomionej strony
        self.assertEqual(self.driver.title, 'FUN animals')

    def test_pages_urls_working(self):
        # sprawdza działanie odnośników zawartych w urls.py
        self.exceptionList = ['storeUser', 'loginUser', 'storeComment', 'show']
        self.argumentNeedList = ['search', 'categories']
        
        self.work = 0
        for elem in range(len(urls.urlpatterns)):
            self.url = str(urls.urlpatterns[elem])
            self.urlFix = self.url.partition("=")[2][:-2].replace("'","")
            if self.urlFix not in self.exceptionList:
                if self.urlFix not in self.argumentNeedList:
                    if self.urlFix == "index":
                        self.address = "http://localhost:8000/"
                    else:
                        self.address = "http://localhost:8000/" + self.urlFix
                else:
                    self.address = "http://localhost:8000/" + self.urlFix + "/any"
                self.driver.get(self.address)
                self.assertEqual(self.driver.title, 'FUN animals')

    def test_images_show(self):
        # sprawdza czy grafiki zawarte w podglądzie posta są wyświetlane
        self.element = self.driver.find_elements_by_class_name("postimg")
        for elem in self.element:
            elem = elem.is_displayed()
            self.assertEqual(elem, True)

    def test_images_urls(self):
        # sprawdza czy pliki załączone jako tło elementu znajdują się w folderze ze zdjęciami
        self.element = self.driver.find_elements_by_class_name("postimg")
        self.imgpath = "/code/media/photos/"
        self.imgsrcs = os.listdir(self.imgpath)
        self.imgurls = []
        for i in self.imgsrcs:
            self.imgurls.append(f"""url("{self.address}media/photos/{i}")""")
        for elem in self.element:
            elem = elem.value_of_css_property("background-image")
            self.assertIn(elem, self.imgurls)

    def test_post_urls_working(self):
        # sprawdza działanie odnośników do konkretnego posta
        self.element = self.driver.find_elements_by_class_name("postbox")
        self.listLen = len(self.element) + 1
        for elem in range(1, self.listLen):
            self.address = f"""http://localhost:8000/{elem}/"""
            self.driver.get(self.address)
            self.assertEqual(self.driver.title, 'FUN animals')

    def test_post_dates(self):
        # sprawdza czy wyświetlane posty są posortowane według daty
        self.element = self.driver.find_elements_by_class_name("postbox")
        self.listLen = len(self.element) + 1
        self.dateslist = []
        for elem in range(1, self.listLen):
            self.address = f"""http://localhost:8000/{elem}/"""
            self.driver.get(self.address)
            self.dateelement = self.driver.find_element_by_id("publish_date").text
            self.dateslist.append(self.dateelement[12:-1].replace(".",""))
        # self.dateslist.append("May 13, 2022, 3:40 pm")
        self.dateslistsorted = self.dateslist.copy()
        self.dateslistsorted.sort()
        # print(self.dateslist, self.dateslistsorted)
        self.assertListEqual(self.dateslist, self.dateslistsorted)

    def test_post_number(self):
        # sprawdza czy lista postów na stronie głównej odpowiada liczbie postów w kategorii "post"
        self.postElement = self.driver.find_elements_by_class_name("postbox")
        self.postCount = len(self.postElement)
        self.address = "http://localhost:8000/categories/post"
        self.driver.get(self.address)
        self.resultsElement = self.driver.find_elements_by_class_name("list-group-item")
        self.resultCount = len(self.resultsElement)
        # print(self.postCount, self.resultCount)
        self.assertEqual(self.postCount, self.resultCount)

    def test_login_fail(self):
        # sprawdza wyświetlenie informacji w przypadku nieudanej próby logowania
        self.address = "http://localhost:8000/login"
        self.driver.get(self.address)
        self.loginBox = self.driver.find_element(By.NAME, "username")
        self.loginBox.send_keys("wrongusername")
        self.passwordBox = self.driver.find_element(By.NAME, "password")
        self.passwordBox.send_keys("wrongpassword")
        self.form = self.driver.find_element_by_id("submitLogin")
        self.form.click()
        self.info = self.driver.find_element_by_class_name("error").text
        # print(self.info)
        self.assertEqual(self.info, "Wrong credentials")

    def test_login_success(self):
        # sprawdza wyświetlenie informacji w przypadku udanej próby logowania
        self.address = "http://localhost:8000/login"
        self.driver.get(self.address)
        self.loginBox = self.driver.find_element(By.NAME, "username")
        self.loginBox.send_keys("testowyUser")
        self.passwordBox = self.driver.find_element(By.NAME, "password")
        self.passwordBox.send_keys("qwerty")
        self.form = self.driver.find_element_by_id("submitLogin")
        self.form.click()
        self.info = self.driver.find_element_by_class_name("success").text
        # print(self.info)
        self.assertEqual(self.info, "Loged in")

    def test_register_email_fail(self):
        # sprawdza czy formularz zadziała w przypadku nieprawidłowego formatu email
        self.address = "http://localhost:8000/register"
        self.driver.get(self.address)
        self.loginBox = self.driver.find_element(By.NAME, "username")
        self.loginBox.send_keys("wrongusername")
        self.passwordBox = self.driver.find_element(By.NAME, "email")
        self.passwordBox.send_keys("wrongemail")
        self.passwordBox = self.driver.find_element(By.NAME, "password")
        self.passwordBox.send_keys("wrongpassword")
        self.passwordBox = self.driver.find_element(By.NAME, "confirmation_password")
        self.passwordBox.send_keys("wrongpassword")
        self.form = self.driver.find_element_by_id("submitRegister")
        self.form.click()
        # print(self.driver.current_url)
        self.assertEqual(self.driver.current_url, "http://localhost:8000/register")

    def test_register_password_fail(self):
        # sprawdza czy formularz zadziała w przypadku nieprawidłowego formatu email
        self.address = "http://localhost:8000/register"
        self.driver.get(self.address)
        self.loginBox = self.driver.find_element(By.NAME, "username")
        self.loginBox.send_keys("wrongusername")
        self.passwordBox = self.driver.find_element(By.NAME, "email")
        self.passwordBox.send_keys("wrong@ema.il")
        self.passwordBox = self.driver.find_element(By.NAME, "password")
        self.passwordBox.send_keys("wrongpassword")
        self.passwordBox = self.driver.find_element(By.NAME, "confirmation_password")
        self.passwordBox.send_keys("differentpassword")
        self.form = self.driver.find_element_by_id("submitRegister")
        self.form.click()
        self.info = self.driver.find_element_by_class_name("error").text
        # print(self.driver.current_url)
        self.assertEqual(self.info, "Passwords not matching")

    def test_register_success(self):
        # sprawdza czy formularz zadziała w przypadku prawidłowych danych
        self.address = "http://localhost:8000/register"
        self.driver.get(self.address)
        self.loginBox = self.driver.find_element(By.NAME, "username")
        self.loginBox.send_keys("correctusername")
        self.passwordBox = self.driver.find_element(By.NAME, "email")
        self.passwordBox.send_keys("corr@ct.mail")
        self.passwordBox = self.driver.find_element(By.NAME, "password")
        self.passwordBox.send_keys("correctpassword")
        self.passwordBox = self.driver.find_element(By.NAME, "confirmation_password")
        self.passwordBox.send_keys("correctpassword")
        self.form = self.driver.find_element_by_id("submitRegister")
        self.form.click()
        # print(self.driver.current_url)
        self.assertEqual(self.driver.current_url, "http://localhost:8000/user/register")

    def test_search(self):
        # sprawdza czy pole search wyszukuje dany element
        self.value = "ppost1"
        self.search = self.driver.find_element_by_id("searchVal")
        self.search.send_keys(self.value)
        self.form = self.driver.find_element_by_id("searchButton")
        self.form.click()
        # print(self.driver.current_url)
        self.assertEqual(self.driver.current_url, f"http://localhost:8000/search/{self.value}")

    def test_comment_anon(self):
        # sprawdza czy jest możliwość dodania posta będąc niezalogowanym użytkownikiem
        self.driver.delete_all_cookies()
        self.element = self.driver.find_elements_by_class_name("postbox")
        self.listLen = len(self.element) + 1
        self.cookies = self.driver.get_cookies()
        for elem in range(1, self.listLen):
            self.address = f"""http://localhost:8000/{elem}/"""
            self.driver.get(self.address)
            if self.driver.find_elements_by_id("logininfo"):
                self.info = True
            else:
                self.info = False
            self.assertEqual(self.info, True)

    def test_comment_logged(self):
        # sprawdza czy jest możliwość dodania posta będąc zalogowanym użytkownikiem
        self.test_login_success()
        self.element = self.driver.find_elements_by_class_name("postbox")
        self.listLen = len(self.element) + 1
        self.cookies = self.driver.get_cookies()
        for elem in range(1, self.listLen):
            self.address = f"""http://localhost:8000/{elem}/"""
            self.driver.get(self.address)
            if self.driver.find_elements_by_id("logininfo"):
                self.info = True
            else:
                self.info = False
            self.assertEqual(self.info, False)
