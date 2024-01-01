from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field

from ..serializers import UserSerializer, CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer, TransactionSerializer, PostSerializer, FieldSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics, viewsets
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from supabase import create_client, Client
import os
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
    def post(self, request, format=None):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase : Client = create_client(url, key)
        bucket_name = 'images'
        file_path_in_bucket = 'products/test.png'
        local_image_path = 'media/attachments/thoikhoabieu_1.png'
        with open(local_image_path, 'rb') as file_content:
            response = supabase.storage.from_(bucket_name).upload(file_path_in_bucket, file_content)
        # Check the response
        if response['error']:
            Response(f"Error uploading image: {response['error']['message']}", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            Response("Image uploaded successfully!", status=status.HTTP_200_OK)

class CreatePost(APIView):
    def post(self, request, format=None):

        pass

@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CATEGORY REQUEST


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# PRODUCT REQUESTS


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
