import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    title_text = models.CharField(max_length=40)
    category_text = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published')
    body_text = models.TextField()
    image_file = models.ImageField(upload_to = 'photos')
    def __str__(self):
        return self.title_text
    
    def was_published_recently(self):
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= timezone.now()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name=models.CharField(max_length=20)
    body_text = models.TextField(max_length=200)
    def __str__(self):
        return self.body_text
