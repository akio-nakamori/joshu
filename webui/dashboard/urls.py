from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /dashboard/
    url(r'^$', views.index, name='index'),
    # ex: /dashboard/5/
    url(r'^(?P<anime_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /dashboard/graph/5
    url(r'^(?P<anime_id>[0-9]+)/(graph\/)$', views.graph, name='graph'),
]

