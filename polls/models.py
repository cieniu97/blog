import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title_text = models.CharField(max_length=40)
    category_text = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published')
    body_text = models.TextField()
    image_file = models.ImageField(upload_to = 'photos', default='/media/photos/Tiger_shark.jpg')
    def __str__(self):
        return self.title_text
    
    def was_published_recently(self):
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= timezone.now()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body_text = models.TextField(max_length=200)
    def __str__(self):
        return self.body_text
