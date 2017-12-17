from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('user', 'title', 'body', 'image',)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = self.fields['user'].hidden_widget()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('post', 'user', 'body',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = self.fields['user'].hidden_widget()
        self.fields['post'].widget = self.fields['post'].hidden_widget()
