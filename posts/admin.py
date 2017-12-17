from django.contrib import admin

from .models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'body', 'image',)
    list_display = ('id', 'user', 'title', 'body', 'image',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ('post', 'user', 'body',)
    list_display = ('id', 'post', 'user', 'body',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    fields = ('post', 'user',)
    list_display = ('id', 'post', 'user',)