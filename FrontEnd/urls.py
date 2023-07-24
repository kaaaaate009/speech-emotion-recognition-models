from django.urls import path
from . import views

urlpatterns = [
    path('', views.uploadform, name='uploadform'),
    path('uploadaction', views.uploadaction, name='uploadaction'),
    path('ListView', views.ListView, name='ListView')
]
