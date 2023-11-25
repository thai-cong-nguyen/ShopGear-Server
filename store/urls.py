from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.user_list, name='all users'),
    path('users/<int:id>', views.user_detail, name='a detail user')
]
