from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field

from ..serializers import UserSerializer, CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer, TransactionSerializer, PostSerializer, FieldSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics, viewsets
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from supabase import create_client, Client, SupabaseStorageClient
import os
from datetime import datetime

# USER REQUEST


class ApiRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'products': reverse('product-list', request=request, format=format),
            'product_detail': reverse('product-detail', request=request, args=[5], format=format),
            'users': reverse('user-list', request=request, format=format),
            'fields' : reverse('field-list', request=request, format=format)
            # Add more endpoints as needed
        })

class UploadImage(APIView):
    def post(self, request):
        if 'images' in request.FILES:
            url = os.environ.get("DB_URL")
            key = os.environ.get("DB_API_KEY")
            supabase = create_client(url, key)
            bucket_name = 'Bucket_Images'
            file_urls = []
            # Body of Request is FormData and 'images' is the field for uploading images
            for image in request.FILES.getlist('images'):
                # You can modify the file name as needed
                file_image = image.read()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                original_name, extension = os.path.splitext(image.name)
                file_name = f"{timestamp}_{original_name}{extension}"
                # Upload the image to Supabase storage
                response = supabase.storage.from_(bucket_name).upload(file_name, file_image)
                if response.status_code == 200:
                    file_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
                    file_urls.append(file_url)
                else:
                    return Response({"error": "Failed to upload image", "data": file_urls}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "Images uploaded successfully!", "data": file_urls}, status=status.HTTP_200_OK)
        return Response({"error": "No images provided in the request"}, status=status.HTTP_400_BAD_REQUEST)
    
class CreatePost(APIView):
    def post(self, request, format=None):

        pass

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

class FieldDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer