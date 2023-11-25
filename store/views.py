from django.shortcuts import render
from . models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post

from .serializers import UserSerializer, CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer, TransactionSerializer, PostSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics


def index(request):
    obj = Category.objects.all()
    context = {
        'obj': obj
    }
    # hehehe
    return render(request, 'index.html', context)

# USER REQUEST


@api_view(['GET'])
def user(request):
    if request == 'GET':
        return Response(status=status.HTTP_100_CONTINUE)


@api_view(['GET', 'POST'])
def user_list(request):
    # request == GET
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # hihiihi
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request:
        return Response('hffh')
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




# PRODUCT REQUESTS


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
