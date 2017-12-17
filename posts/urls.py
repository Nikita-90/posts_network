from django.conf.urls import url

from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^main_page/(?P<page>\d+)/$', views.main_page, name='main_page'),
    url(r'^create_post/$', views.create_post, name='create_post'),
    url(r'^do_like/$', views.do_like, name='do_like'),
    url(r'^post_detail/(?P<post_id>\d+)/(?P<page>\d+)/$', views.post_detail, name='post_detail'),
]