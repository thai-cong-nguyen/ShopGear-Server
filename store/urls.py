from django.urls import path, include
from .views import crud
from rest_framework import routers
urlpatterns = [
    path('', crud.ApiRoot.as_view(), name='api-root'),
    path('users/', crud.user_list, name='user-list'),
    path('users/<int:pk>/', crud.user_detail, name='user-detail'),
    path('categories/', crud.category_list, name='category-list'),
    path('categories/<int:pk>/', crud.category_detail, name='category-detail'),
    path('products/', crud.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', crud.ProductDetail.as_view(),
         name='product-detail'),
]
