from django.db import models
from common.models import CustomUser


class Post(models.Model):
    user = models.ForeignKey(CustomUser)
    title = models.CharField(max_length=32)
    body = models.TextField(max_length=1024, blank=True)
    image = models.ImageField(upload_to='image/post/', blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(CustomUser)
    body = models.TextField(max_length=1024)

    def __str__(self):
        return "Comment {}, post {}".format(self.id, self.post.title)


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='like_post')
    user = models.ForeignKey(CustomUser)

    def __str__(self):
        return "Like {}, post {}".format(self.id, self.post.title)
