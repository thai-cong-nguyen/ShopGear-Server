from django.urls import path, include
from .views import crud
from rest_framework import routers
urlpatterns = [
    path('', crud.index),
    path('users/', crud.user_list, name='all users'),
    path('users/<int:pk>', crud.user_detail, name='a detail user'),
    path('categories/', crud.category_list, name='all categories'),
    path('categories/<int:pk>', crud.category_detail, name='a detail category'),
    path('products/', crud.ProductList.as_view(), name='all products'),
    path('products/<int:pk>', crud.ProductDetail.as_view(),
         name='a detail product'),
]
