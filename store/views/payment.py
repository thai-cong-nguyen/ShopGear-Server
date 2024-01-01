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
from time import time
from datetime import datetime
import json, hmac, hashlib, urllib.request, urllib.parse, random
    
class CreateOrderView(APIView):
    def post(self, request):
        try:
            data = request.data
            print("Create payment order")
            config = {
                "app_id": 2553,
                "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
                "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
                "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
            }
            transID = random.randrange(1000000)
            print(random.randrange(1000000))
            order = {
                "app_id": config["app_id"],
                "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID), # mã giao dich có định dạng yyMMdd_xxxx
                "app_user": "user123",
                "app_time": int(round(time() * 1000)), # miliseconds
                "embed_data": json.dumps({}),
                "item": json.dumps([{}]),
                "amount": data.get("amount"),
                "description": "ShopGear - Payment for the order #"+str(transID),
                "bank_code": "zalopayapp",
                "callback_url": "api-shopgear.onrender.com/api/payment/callback"
            }

            # app_id|app_trans_id|app_user|amount|apptime|embed_data|item
            data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"],  order["amount"], order["app_time"], order["embed_data"], order["item"])
            order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()
            response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
            result = json.loads(response.read())
            result["app_trans_id"] = order['app_trans_id']
            if (result['return_code'] != 1):
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Create Payment Order Failed", "data": result}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": status.HTTP_200_OK, "message": "Create Payment Order Successfully", "data": result}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "data": {}},status=status.HTTP_400_BAD_REQUEST)
        
class CallbackView(APIView):
    def post(self, request):
        result = {}
        try:
            print("Call back when payment success")
            config = {
                'key2': 'eG4r0GcoNtRGbO8'
            }
            cbdata = request.data
            mac = hmac.new(config['key2'].encode(), cbdata['data'].encode(), hashlib.sha256).hexdigest()
            # kiểm tra callback hợp lệ (đến từ ZaloPay server)
            if mac != cbdata['mac']:
                # callback không hợp lệ
                result['return_code'] = -1
                result['return_message'] = 'invalid callback'
            else:
                # thanh toán thành công
                # merchant cập nhật trạng thái cho đơn hàng
                dataJson = json.loads(cbdata['data'])
                print("update order's status = success where app_trans_id = " + dataJson['app_trans_id'])

            result['return_code'] = 1
            result['return_message'] = 'success'
        except Exception as e:
            print(e)
            result['return_code'] = 0 # ZaloPay server sẽ callback lại (tối đa 3 lần)
            result['return_message'] = "exception"
            result['e'] = str(e)
        if result['return_code'] == 1:
            result['status_code'] = status.HTTP_200_OK
        else:
            result['status_code'] =  status.HTTP_400_BAD_REQUEST
        # thông báo kết quả cho ZaloPay server
        return Response({"return_code": result['return_code'], "return_message": result['return_message'] or ""}, status=result['status_code'])
    
class QueryOrderView(APIView):
    def post(self, request):
        try:
            data =request.data
            
            config = {
                "app_id": 2553,
                "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
                "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
                "endpoint": "https://sb-openapi.zalopay.vn/v2/query"
            }
            params = {
                "app_id": config["app_id"],
                "app_trans_id": data.get("app_trans_id")  # Input your app_trans_id"
            }

            data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"]) # app_id|app_trans_id|key1
            params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

            response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(params).encode())
            result = json.loads(response.read())
            
            if result['return_code'] == 2:
                return Response({"status": status.HTTP_200_OK, "message": "Order is Failed", "data":result},status=status.HTTP_400_BAD_REQUEST)
            elif result['return_code'] == 3:
                return Response({"status": status.HTTP_200_OK, "message": "Order is Pending", "data":result},status=status.HTTP_200_OK)
            return Response({"status": status.HTTP_200_OK, "message": "Order is Successful", "data":result},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "data": e},status=status.HTTP_400_BAD_REQUEST)

class RefundView(APIView):
    def post(self, request):
        try:
            config = {
                "app_id": 2553,
                "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
                "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
                "refund_url": "https://sb-openapi.zalopay.vn/v2/refund"
            }

            timestamp = int(round(time() * 1000)) # miliseconds
            uid =  "{}{}".format(timestamp, random.randint(111, 999)) # unique id

            order = {
            "app_id": config["app_id"],
            "m_refund_id": "{:%y%m%d}_{}_{}".format(datetime.today(), config["app_id"], uid),
            "timestamp": timestamp,
            "zp_trans_id": 123456789,
            "amount": 1000,
            "description": "ZaloPay Integration Demo",
            }

            # appid|zptransid|amount|description|timestamp
            data = "{}|{}|{}|{}|{}".format(order["m_refund_id"], order["zp_trans_id"], order["amount"], order["description"], order["timestamp"])
            order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

            response = urllib.request.urlopen(url=config["refund_url"], data=urllib.parse.urlencode(order).encode())
            result = json.loads(response.read())

            for k, v in result.items():
                print("{}: {}".format(k, v))
        except Exception as e:
            print(e);