from django.urls import path, include
from . import views
from rest_framework import routers
urlpatterns = [
    path('', views.index),
    path('users/', views.user_list, name='all users'),
    path('users/<int:pk>', views.user_detail, name='a detail user'),
    path('categories/', views.category_list, name='all categories'),
    path('categories/<int:pk>', views.category_detail, name='a detail category'),
    path('products/', views.ProductList.as_view(), name='all products'),
    path('products/<int:pk>', views.ProductDetail.as_view(),
         name='a detail product'),
]
