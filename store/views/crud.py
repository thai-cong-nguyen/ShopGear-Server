from multiprocessing import Value
from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field, FieldValue, FieldOption, Attachment

from ..serializers import  UserSerializer, CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer, TransactionSerializer, PostSerializer, FieldSerializer, PostAndProductSerializer, FieldValueSerializer, FieldOptionSerializer, AttachmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics, viewsets, serializers
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from supabase import create_client, Client, SupabaseStorageClient
import os
from datetime import datetime
from django.shortcuts import get_object_or_404
# USER REQUEST
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import jwt

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
    # tìm kiếm theo query
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name_without_accent', 'description', 'user__username', 'name']
    ordering_fields = ['price']


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['category']

class FieldDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['$product__name', 'product__name_without_accent', 'description']
    ordering_fields = ['product__price']

class PostCreate(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostAndProductSerializer
    
    def create(self, request, *args, **kwargs):
        # pre-process the data
        fields_data = request.data.get('fields')
        product_data = request.data.get('product')
        fields_data = [{'product': product_data, **field_data} for field_data in fields_data]
        request.data['fields'] = fields_data 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.validate_user(request)

        response_data = serializer.save(user=user, fields=fields_data)
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def validate_user(self, request, *args, **kwargs):
        access_token = request.data.get('user')

        if access_token is None: 
            raise serializers.ValidationError({'error': 'Access token is missing'})

        try: 
            decoded_token = jwt.decode(access_token, os.environ.get("SECRET_KEY"), algorithms=['HS256'])
            user_id = decoded_token['user']
            user = User.objects.get(pk=user_id)
            return user

        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({'error': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise serializers.ValidationError({'error': 'Invalid token'})
        

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        return PostAndProductSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # pre-process the data
        fields_data = request.data.get('fields')
        product_data = request.data.get('product')
        fields_data = [{'product': product_data, **field_data} for field_data in fields_data]
        request.data['fields'] = fields_data 
        
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.validate_user(request)
        response_data = serializer.save(instance=instance,user=user, fields=fields_data)
        return Response(response_data, status=status.HTTP_200_OK)
    
    def validate_user(self, request, *args, **kwargs):
        access_token = request.data.get('user')

        if access_token is None: 
            raise serializers.ValidationError({'error': 'Access token is missing'})

        try: 
            decoded_token = jwt.decode(access_token, os.environ.get("SECRET_KEY"), algorithms=['HS256'])
            user_id = decoded_token['user']
            user = User.objects.get(pk=user_id)
            return user

        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({'error': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise serializers.ValidationError({'error': 'Invalid token'})
        
        
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

class FieldValueList(generics.ListCreateAPIView):
    queryset = FieldValue.objects.all()
    serializer_class = FieldValueSerializer

class FieldValueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FieldValue.objects.all()
    serializer_class = FieldValueSerializer

class FieldOptionList(generics.ListCreateAPIView):
    queryset = FieldOption.objects.all()
    serializer_class = FieldOptionSerializer

class FieldOptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FieldOption.objects.all()
    serializer_class = FieldOptionSerializer

class FieldsInCategoryView(APIView):
    def get(self, request, category_name, format=None):
        # Get the Category instance based on the name
        category = get_object_or_404(Category, name=category_name)

        # Search for fields related to the specified category
        fields_in_category = Field.objects.filter(category=category)

        # Serialize the fields
        serializer = FieldSerializer(fields_in_category, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class AttachmentList(generics.ListCreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    pagination_class = None

class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderUser(APIView):
    def get(self, *args, **kwargs):
        try:
            user_id = self.kwargs.get('pk')
            user = User.objects.get(pk=user_id)
            orders = Order.objects.filter(user=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)

class PostFromProduct(APIView):
    def get(self, *args, **kwargs):
        try:
            product_id = self.kwargs.get('pk')
            product = Product.objects.get(pk=product_id)
            post = Post.objects.get(product=product)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
# class SellOrderList(generics.ListCreateAPIView):
#     queryset = SellOrder.objects.all()
#     serializer_class = SellOrderSerializer
#     # def get_queryset(self):
#     #     return Order.objects.filter(status=2)
    
# class SellOrderDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = SellOrder.objects.all()
#     serializer_class = SellOrderSerializer
    
# class SellerOrder(APIView):
#     def get(self, *args, **kwargs):
#         try:
#             user_id = self.kwargs.get('pk')
#             user = User.objects.get(pk=user_id)
#             sell_orders = SellOrder.objects.filter(user=user)
#             serializer = SellOrderSerializer(sell_orders, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
#     def put(self, request, pk, *args, **kwargs):
#         try:
#             user_id = self.kwargs.get('pk')
#             user = User.objects.get(pk=user_id)
#             sell_order = get_object_or_404(SellOrder, order=request.data['order'], user=user)
#             serializer = SellOrderSerializer(sell_order, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             print(e)
#             return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
