from locale import atoi
from venv import create
from django.shortcuts import render
from ..models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post
from django.db import transaction
from ..serializers import OrderSerializer, OrderItemSerializer
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
from time import time
from datetime import datetime
import json, hmac, hashlib, urllib.request, urllib.parse, random

class CancelOrderView(APIView):
    def patch(self, request):
        try:
            print("Cancelling order")
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": status.HTTP_200_OK, "message": "Cancel Order Successfully", "data": ""}, status=status.HTTP_200_OK)
        
    
class AcceptCancelOrderView(APIView):
    def post(self, request):
        try:
            print("Accepting Order")
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": status.HTTP_200_OK, "message": "Accept Order Successfully", "data": ""}, status=status.HTTP_200_OK)
    
class RejectCancelOrderView(APIView):
    def post(self, request):
        try:
            print("Rejecting Order")
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": status.HTTP_200_OK, "message": "Reject Order Successfully", "data": ""}, status=status.HTTP_200_OK)