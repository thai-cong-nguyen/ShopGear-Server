from . models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field
from rest_framework import serializers, routers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from .utils.generate_token import get_tokens_for_user
from django.contrib.auth import authenticate
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'is_admin', 'products', 'posts']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'fields']
        depth = 1


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'user_id', 'category_id', 'name',
                  'description', 'price', 'is_available', 'attachments', 'field_values']
        depth = 4
        read_only_fields = ['user_id']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_price', 'addresses', 'phone', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order_id', 'product_id', 'quantiy']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user_id']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart_id', 'product_id', 'quantiy']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'buyer_id', 'seller_id', 'total_price', 'status']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user_id', 'product_id', 'description', 'price', 'zone', ]
        depth = 2

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field 
        fields = ['id', 'name', 'options']
        depth = 1


class LoginSerializer(serializers.ModelSerializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        # Check if the provided value is a valid email address
        is_email = '@' in username_or_email
        # Choose the correct lookup field based on whether it's an email or username
        lookup_field = 'email' if is_email else 'username'
        try:
            user = User.objects.get(**{lookup_field: username_or_email})
        except User.DoesNotExist:
            raise serializers.ValidationError("Username or Email does not exist")
        if not password == user.password:
                raise serializers.ValidationError("Password is incorrect")
        token = get_tokens_for_user(user)
        if not token:
                raise Exception("Invalid refresh token")
        data['token'] = token
        return data
    class Meta:
        model = User
        fields = ['username_or_email', 'password']
        
class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    address = serializers.CharField()
    def validate(self, data):
        username = data.get('username')
        phone = data.get('phone')
        email = data.get('email')
        
        if not all([username, phone, email, data.get('password'), data.get('address')]):
            raise serializers.ValidationError("Invalid information")
        existing_user = User.objects.filter(Q(username=username) | Q(phone=phone) | Q(email=email)).first()
        if existing_user:
            raise serializers.ValidationError("User with this username, phone, or email already exists")
        return data
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email', 'password', 'address']
        extra_kwargs = {'password': {'write_only': True}}
        
class ResetTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    def validate(self, data):
        token = data.get('token')
        if not token:
            raise serializers.ValidationError("Invalid Refresh Token")
        try:
            decoded_token = UntypedToken(token)
            user_id = decoded_token.payload.get('user_id')
            if user_id is None or not isinstance(user_id, int):
                raise serializers.ValidationError("Invalid user ID in token payload")
            user = User.objects.get(pk=user_id)
            new_token = RefreshToken.for_user(user)
            data['access_token'] = new_token.access_token
            data['refresh_token'] = new_token
        except TokenError as e:
            raise serializers.ValidationError(str(e))
        return data
    class Meta: 
        fields = ["token"]