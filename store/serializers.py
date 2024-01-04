from . models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field, FieldOption, FieldValue
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

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'addresses', 'phone', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantiy']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantiy']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'buyer', 'seller', 'total_price', 'status']


# Field & Category
class FieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOption
        fields = ['name']


class FieldSerializer(serializers.ModelSerializer):
    options = FieldOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Field 
        fields = '__all__'
        
class FieldForFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name']

class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldForFieldValueSerializer(read_only=True)
    class Meta:
        model = FieldValue
        fields = ['field', 'value']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        field_representation = representation['field']
        field_name = field_representation['name']
        return { 'tag': field_name, 'value': representation['value'] }
        
    def to_internal_value(self, data):
        field_name = data.get('field')
        category_id = data.get('product').get('category')
        if category_id and field_name:
            try:
                category = Category.objects.get(pk=category_id)
                field = Field.objects.get(name=field_name, category=category)
                data['field'] = field.pk
            except Category.DoesNotExist:
                raise serializers.ValidationError(f'Category with name "{category_id}" does not exist.')
            
        return super().to_internal_value(data)
    
class FieldCategorySerializer(serializers.ModelSerializer):
    options = FieldOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Field
        fields = ['name', 'options', 'field_type']

class CategorySerializer(serializers.ModelSerializer):
    fields = FieldCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['name', 'fields']


class ProductSerializer(serializers.ModelSerializer):
    field_values = FieldValueSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = '__all__'
    def to_internal_value(self, data):
        # Convert category name to its corresponding primary key
        category_name = data.get('category')
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                data['category'] = category.pk
            except Category.DoesNotExist:
                raise serializers.ValidationError(f'Category with name "{category_name}" does not exist.')

        return super().to_internal_value(data)

class PostSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    zone = serializers.CharField(source='get_zone_display')
    class Meta:
        model = Post
        fields = '__all__'

class PostAndProductSerializer(serializers.Serializer):
    # all fields of a product 
    product = ProductSerializer()
    fields = FieldValueSerializer(many=True)

    # user-defined fields
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # post fields
    post_description = serializers.CharField()
    post_zone = serializers.CharField()

    def create(self, validated_data):
        user = validated_data.pop('user')
        # Xử lý dữ liệu và tạo Product
        product_data = validated_data['product']
        product_data['user'] = user
        category_name = product_data['category']
        category = Category.objects.get(name=category_name)
        product_data['category'] = category
        product = Product.objects.create(**product_data)

        # Thêm fields liên kết với product 
        fields_data = validated_data['fields']
        for field_data in fields_data:
            # Convert field names to primary keys
            field = Field.objects.get(pk=field_data['field'])
            field_data['field'] = field
            field_data['product'] = product

            # Tạo FieldValue với primary keys đã được chuyển đổi
            FieldValue.objects.create(**field_data)

        # Tạo Post
        post_data = {
            'user': user,
            'product': product,
            'description': validated_data['post_description'],
            'zone': validated_data['post_zone'],
        }
        post = Post.objects.create(**post_data)
        post_serializer = PostSerializer(post)
        return post_serializer.data
    
    def update(self, instance, validated_data):
        # Logic cập nhật bài đăng
        instance.product.name = validated_data['product']['name']
        instance.product.description = validated_data['product']['description']
        instance.product.price = validated_data['product']['price']
        instance.product.is_available = validated_data['product']['is_available']
        
        category_name = validated_data['product']['category']
        category = Category.objects.get(name=category_name)
        instance.product.category = category
        # Lưu lại đối tượng đã cập nhật
        instance.product.save()

        # Cập nhật các trường liên quan
        for field_data in validated_data['fields']:
            field_instance = instance.product.field_values.get(field=field_data['field'])
            field_instance.value = field_data['value']
            field_instance.save()

        # Cập nhật các trường khác tùy theo nhu cầu của bạn
        instance.description = validated_data['post_description']
        instance.zone = validated_data['post_zone']
        instance.save()
        serializer = PostSerializer(instance)

        return serializer.data


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
            user = decoded_token.payload.get('user')
            if user is None or not isinstance(user, int):
                raise serializers.ValidationError("Invalid user ID in token payload")
            user = User.objects.get(pk=user)
            new_token = RefreshToken.for_user(user)
            data['access_token'] = new_token.access_token
            data['refresh_token'] = new_token
        except TokenError as e:
            raise serializers.ValidationError(str(e))
        return data
    class Meta: 
        fields = ["token"]