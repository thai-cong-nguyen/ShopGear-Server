from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post

from ..serializers import LoginSerializer, UserSerializer, RegistrationSerializer, ResetTokenSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import serializers 

class LoginView(APIView):
    def post(self, request):
        try:
            data = request.data
            if not data.get('username_or_email'):
                raise Exception("Invalid username or email")
            if not data.get('password'):
                raise Exception("Password is required")
            
            serializer = LoginSerializer(data = data)
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data['token']
            return Response({"status": status.HTTP_200_OK, "message": "Login Successfully", "data": token})
        except serializers.ValidationError as e:
            error_message = e.detail.get('non_field_errors', [])[0]
            print(error_message)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(error_message), "data": {}},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
            
class RegistrationView(APIView):
    serializer_class = RegistrationSerializer
    def post(self, request):
        try:
            serializer = self.serializer_class(data = request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
            return Response({"status": status.HTTP_200_OK, "message": "Register Successfully", "data": {}}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            error_message = e.detail.get('non_field_errors', [])[0]
            print(error_message)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(error_message), "data": {}},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
    
class ResetTokenView(APIView):
    serializer_class = ResetTokenSerializer
    def post(self, request):
        try:
            serializer = self.serializer_class(data = request.data)
            serializer.is_valid(raise_exception=True)
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']
            return Response({"status": status.HTTP_200_OK, "message": "Token reset successfully", "data": {"access_token": str(access_token), "refresh_token": str(refresh_token)}}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            error_message = e.detail.get('non_field_errors', [])[0]
            print(error_message)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(error_message), "data": {}},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
        