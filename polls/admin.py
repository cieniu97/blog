from django.contrib import admin

# Register your models here.
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 3


class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Title',               {'fields': ['title_text']}),
        ('Category', {'fields': ['category_text']}),
        ('Publication date', {'fields': ['pub_date'], 'classes': ['collapse']}),
        ('Wrtie a blog post', {'fields': ['body_text']}),
        ('Upload image', {'fields': ['image_file']}),
    ]
    inlines = [CommentInline]
    list_display = ('title_text', 'category_text')
    search_fields = ['title_text', 'category_text']

admin.site.register(Post, PostAdmin)
