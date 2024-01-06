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
    
class CreateOrderView(APIView):
    def post(self, request):
        data = request.data
        try:
            print("Create payment order")
            with transaction.atomic():
                # create Order 
                print("Transaction")
                orderdata = {
                    "user": data.get("user"),
                    "total_price": data.get("total_price"),
                    "ward": data.get("ward"),
                    "district": data.get("district"),
                    "province": data.get("province"),
                    "discount_code": data.get("discount_code") if data.get("discount_code") else "",
                    "phone_number": data.get("phone_number"),
                    "full_name": data.get("full_name"),
                    "items": data.get("items")
                }
                serializer = OrderSerializer(data=orderdata)
                serializer.is_valid(raise_exception=True)
                createOrder = serializer.create(validated_data=serializer.validated_data, items=data.get("items"))
                config = {
                "app_id": 2553,
                "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
                "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
                "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
                }
                transID = random.randrange(1000000)
                app_trans_id = "{:%y%m%d}_{}".format(datetime.today(), transID)
                order = {
                    "app_id": config["app_id"],
                    "app_trans_id": app_trans_id, # mã giao dich có định dạng yyMMdd_xxxx
                    "app_user": "user123",
                    "app_time": int(round(time() * 1000)), # miliseconds
                    "embed_data": json.dumps({"order": createOrder.id, "redirecturl": f"http://localhost:5173/order/result/{app_trans_id}"}),
                    "item": json.dumps([{}]),
                    "amount": data.get("total_price"),
                    "description": "ShopGear - Payment for the order #"+str(transID),
                    "bank_code": "zalopayapp",
                    "callback_url": "https://api-shopgear.onrender.com/api/payment/callback"
                }

                # app_id|app_trans_id|app_user|amount|apptime|embed_data|item
                data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"],  order["amount"], order["app_time"], order["embed_data"], order["item"])
                order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()
                response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
                result = json.loads(response.read())
                result["app_trans_id"] = order['app_trans_id']
                result["order_id"] = createOrder.id
                if (result['return_code'] != 1):
                    return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Create Payment Order Failed", "data": result}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": status.HTTP_200_OK, "message": "Create Payment Order Successfully", "data": result}, status=status.HTTP_200_OK)
        
class CallbackView(APIView):
    def post(self, request):
        result = {}
        data = request.data
        try:
            print("Call back when payment success")
            
            config = {
                'key2': 'eG4r0GcoNtRGbO8'
            }
            cbdata = request.data
            # {key: value for key, value in data.items() if key != "order"}
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
                if dataJson.get('embeddata'):
                    orderdata = {"status": 3}
                    instance = Order.objects.get(pk=dataJson['embeddata'].get('order'))
                    serializer = OrderSerializer(instance=instance, data=orderdata)
                    serializer.is_valid(raise_exception=True)
                    serializer.update(instance=instance,validated_data=serializer.validated_data)
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
            order_id = data.get('order_id')
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
            instance = Order.objects.get(pk=order_id)
            order_serializer = OrderSerializer(instance=instance)
            result['items'] = order_serializer.data.get('items')
            if result['return_code'] == 2:
                return Response({"status": status.HTTP_200_OK, "message": "Order is Failed", "data":result},status=status.HTTP_400_BAD_REQUEST)
            elif result['return_code'] == 3:
                return Response({"status": status.HTTP_200_OK, "message": "Order is Pending", "data":result},status=status.HTTP_200_OK)
            return Response({"status": status.HTTP_200_OK, "message": "Order is Successful", "data":result},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "data": e},status=status.HTTP_400_BAD_REQUEST)

class CancelOrderView(APIView):
    def delete(self, request):
        data = request.data
        try:
            instance = Order.objects.get(pk=data.get('order'))
            instance.delete()
        except Exception as e:
            print(str(e))
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": status.HTTP_200_OK, "message": "Cancel Order Successfully", "data": ""}, status=status.HTTP_200_OK)