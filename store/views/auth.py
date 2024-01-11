
from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post

from django.conf import settings
from ..serializers import LoginSerializer, UserSerializer, RegistrationSerializer, ResetTokenSerializer, PasswordResetSerializer
from ..utils.reset_password import sendResetPasswordEmail, get_token_generator
from django_rest_passwordreset.models import ResetPasswordToken
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
import json
import datetime

HTTP_USER_AGENT_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_HTTP_USER_AGENT_HEADER', 'HTTP_USER_AGENT')
HTTP_IP_ADDRESS_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_IP_ADDRESS_HEADER', 'REMOTE_ADDR')

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
            user = serializer.validated_data['user']
            return Response({"status": status.HTTP_200_OK, "message": "Login Successfully", "data": { **token, "user": user}})
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
        
class ResetPasswordSendOTPView(APIView):
    serializer = PasswordResetSerializer
    def post(self, request):
        try:
            user_email = request.data.get('email')
            user = User.objects.get(email=user_email)
            user_serializer = UserSerializer(instance=user)
            get_token = get_token_generator()
            print('Line 87: ', user_serializer.data)
            reset_password_data = {
                "key": get_token,
                "username": user_serializer.data['username'],
                "email": user_email
            }
            # print(ResetPasswordToken.objects.filter(user_id=user_serializer).exists())
            sendResetPasswordEmail(reset_password_data)
            # If not Exist => Create
            if not ResetPasswordToken.objects.filter(user_id=user_serializer.data.get('id')).exists():
                validated_data = {
                    "key": get_token,
                    "ip_address": request.META.get(HTTP_IP_ADDRESS_HEADER,''),
                    "user_agent": request.META.get(HTTP_USER_AGENT_HEADER, ''),
                    "user_id": user_serializer.data.get('id'),
                }
                rpt_serializer = self.serializer(data=validated_data)
                rpt_serializer.is_valid(raise_exception=True)
                rpt_serializer.save()
                rpt = rpt_serializer.data
                print('Line 105: ', rpt)
            # If Exist => Update
            instance = ResetPasswordToken.objects.filter(user_id=user_serializer.data.get('id')).first()
            validated_data = {
                "key": get_token,
                "ip_address": request.META.get(HTTP_IP_ADDRESS_HEADER,''),
                "user_agent": request.META.get(HTTP_USER_AGENT_HEADER, '')
            }
            rpt_serializer = self.serializer(data=validated_data)
            rpt_serializer.is_valid(raise_exception=True)
            rpt_serializer.save(instance=instance)
            rpt = rpt_serializer.data
            return Response({"status": status.HTTP_200_OK, "message": "Send OTP Successfully", "data": {rpt}}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            error_message = e.detail.get('email', [])[0]
            print(error_message)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(error_message), "data": {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something Went Wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)
            
class ResetPasswordConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("Reset Password Confirmation")
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": {}}, status=status.HTTP_400_BAD_REQUEST)