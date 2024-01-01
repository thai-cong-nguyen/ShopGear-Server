from django.urls import path, include
from .views import crud, auth, payment
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/', crud.ApiRoot.as_view()),
    # path('users/', crud.user_list, name='all users'),
    # path('users/<int:pk>', crud.user_detail, name='a detail user'),
    # path('categories/', crud.category_list, name='all categories'),
    # path('categories/<int:pk>', crud.category_detail, name='a detail category'),
    # path('products/', crud.ProductList.as_view(), name='all products'),
    # path('products/<int:pk>', crud.ProductDetail.as_view(),
    #      name='a detail product'),
    path('api/login', auth.LoginView.as_view(), name='login'),
    path('api/register', auth.RegistrationView.as_view(), name='register'),
    path('api/token', auth.ResetTokenView.as_view(), name='token'),
    path('', crud.ApiRoot.as_view(), name='api-root'),
    path('api/users/', crud.user_list, name='user-list'),
    path('api/users/<int:pk>/', crud.user_detail, name='user-detail'),
    path('api/categories/', crud.category_list, name='category-list'),
    path('api/categories/<int:pk>/', crud.category_detail, name='category-detail'),
    path('api/products/', crud.ProductList.as_view(), name='product-list'),
    path('api/products/<int:pk>/', crud.ProductDetail.as_view(),
         name='product-detail'),
    path('api/fields/', crud.FieldList.as_view(), name='field-list'),
    path('api/fields/<int:pk>', crud.FieldDetail.as_view(), name='field-detail'),
    path('api/posts', crud.PostList.as_view(), name='post-list' ),
    path('api/posts/<int:pk>', crud.PostDetail.as_view(), name='post-detail' ),
    path('api/upload_images', crud.UploadImage.as_view(), name='upload-image'),
    path('api/create_post', crud.CreatePost.as_view(), name='create-post'),
    path('api/payment/create-order', payment.CreateOrderView.as_view(), name='create-payment-order'),
    path('api/payment/callback', payment.CallbackView.as_view(), name='callback-order'),
    path('api/payment/query', payment.QueryOrderView.as_view(), name='query-order'),
]