from django.urls import path, include
from .views import crud, auth, payment
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/', crud.ApiRoot.as_view()),
    path('api/login', auth.LoginView.as_view(), name='login'),
    path('api/register', auth.RegistrationView.as_view(), name='register'),
    path('api/password_reset', auth.ResetPasswordSendOTPView.as_view(), name='password_reset'),
    path('api/token', auth.ResetTokenView.as_view(), name='token'),
    path('', crud.ApiRoot.as_view(), name='api-root'),
    path('api/users/', crud.UserList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', crud.UserDetail.as_view(), name='user-detail'),
    path('api/categories/', crud.CategoryList.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', crud.CategoryDetail.as_view(), name='category-detail'),
    path('api/products/', crud.ProductList.as_view(), name='product-list'),
    path('api/products/<int:pk>/', crud.ProductDetail.as_view(),
         name='product-detail'),
    path('api/fields/', crud.FieldList.as_view(), name='field-list'),
    path('api/fields/<int:pk>', crud.FieldDetail.as_view(), name='field-detail'),
    path('api/fields/<str:category_name>/', crud.FieldsInCategoryView.as_view(), name='fields-in-category'),   
    path('api/posts/', crud.PostList.as_view(), name='post-list' ),
    path('api/posts/create', crud.PostCreate.as_view(), name='post-create' ),
    path('api/posts/<int:pk>', crud.PostDetail.as_view(), name='post-detail' ),
    path('api/upload_images', crud.UploadImage.as_view(), name='upload-image'),
    path('api/payment/create-order', payment.CreateOrderView.as_view(), name='create-payment-order'),
    path('api/payment/callback', payment.CallbackView.as_view(), name='callback-order'),
    path('api/payment/query', payment.QueryOrderView.as_view(), name='query-order'),
    path('api/payment/cancel', payment.CancelOrderView.as_view(), name='cancel-order'),
    path('api/fieldvalues', crud.FieldValueList.as_view(), name='field-values'),
    path('api/fieldvalues/<int:pk>', crud.FieldValueDetail.as_view(), name='field-values-detail'),
    path('api/fieldoptions', crud.FieldOptionList.as_view(), name='field-options'),
    path('api/fieldoptions/<int:pk>', crud.FieldOptionDetail.as_view(), name='field-options-detail'),
    path("api/attachments/", crud.AttachmentList.as_view(), name='attachments'),
    path('api/orders/', crud.OrderList.as_view(), name='order-list'),
    path('api/orders/<int:pk>', crud.OrderDetail.as_view(), name='order-list'),
    path('api/get/posts/<int:pk>', crud.PostFromProduct.as_view(), name='post-from-product'),
    # path('api/order-items/<int:buyer>', crud.OrderItemListView.as_view(), name='order-items'),
    path('api/buyer/orders/<int:pk>', crud.OrderUser.as_view(), name='order-user'),
    path('api/seller/orders/<int:seller>', crud.OrderItemView.as_view(), name='order-seller'),
]