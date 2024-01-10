from ast import Or
from itertools import product
from h11 import Response
from . models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post, Field, FieldOption, FieldValue, Attachment
from rest_framework import serializers, routers, status
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from .utils.generate_token import get_tokens_for_user
from django.contrib.auth import authenticate
from django.db.models import Q
from datetime import datetime
from django.utils.text import slugify
from django.db import transaction
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'is_admin', 'products', 'posts', 'phone', 'email']
class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep['first_name'] + ' ' + rep['last_name']

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
        fields = '__all__'

class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldForFieldValueSerializer(read_only=True)
    class Meta:
        model = FieldValue
        fields = ['field', 'value']
        
    def to_internal_value(self, data):
        field_name = data.get('field')
        category_id = data.get('product').get('category')
        if category_id and field_name:
            try:
                category = Category.objects.get(pk=category_id)
                field = Field.objects.get(name=field_name, category=category)
                data['field'] = field.pk
            except Category.DoesNotExist:
                return Response({"error": (f'Category with name "{category_id}" does not exist.'), "status": 400}) 
            
        return super().to_internal_value(data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        field_representation = representation['field']
        field_name = field_representation['name']
        return { 'tag': field_name, 'value': representation['value'] }

    
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

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    field_values = FieldValueSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
    def to_representation(self, instance):
        # Override this method to customize the representation during GET requests
        representation = super().to_representation(instance)
        representation['category'] = Category.objects.get(pk=representation['category']).name
        return representation
    
    def to_internal_value(self, data):
        # Convert category name to its corresponding primary key
        category_name = data.get('category')
        data['name_without_accent'] = data.get('name')
        print(data)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                data['category'] = category.pk
            except Category.DoesNotExist:
                return Response({"status": (f'Category with name "{category_name}" does not exist.'), "error": 400}) 

        return super().to_internal_value(data)
    def create(self, validated_data):
        validated_data['name_without_accent'] = slugify(validated_data['name']).replace('-', ' ')
        return super().create(validated_data)
    def update(self, instance, validated_data):
        validated_data['name_without_accent'] = slugify(validated_data['name']).replace('-', ' ')
        return super().update(instance, validated_data)
    

class PostSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    zone = serializers.CharField(source='get_zone_display')
    user = UsernameSerializer(read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True, source='product.attachments')
    class Meta:
        model = Post
        fields = '__all__'
    def to_representation(self, instance):
        representaion = super().to_representation(instance)
        created_at = datetime.strptime(representaion['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        updated_at = datetime.strptime(representaion['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at = created_at.date()
        updated_at = updated_at.date()
        representaion['created_at'] = created_at.isoformat()
        representaion['updated_at'] = updated_at.isoformat()
        return representaion

class PostAndProductSerializer(serializers.Serializer):
    # all fields of a product 
    product = ProductSerializer()
    fields = FieldValueSerializer(many=True, write_only=True)

    # user-defined fields
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # post fields
    post_description = serializers.CharField(write_only=True)
    post_zone = serializers.CharField(write_only=True)
    attachments = AttachmentSerializer(required=False, many=True)
    def create(self, validated_data):
        try:
            print('create post')
            with transaction.atomic():
                user = validated_data.pop('user')
                # Xử lý dữ liệu và tạo Product
                product_data = validated_data['product']
                product_data['user'] = user
                category_name = product_data['category']
                category = Category.objects.get(name=category_name)
                product_data['category'] = category
                product_data['name_without_accent'] = slugify(product_data['name']).replace('-', ' ')
                product = Product.objects.create(**product_data)

                # Thêm fields liên kết với product 
                fields_data = validated_data['fields']
                
                # attachment data 
                attachments_data = validated_data['attachments']
                
                for field_data in fields_data:
                    # Convert field names to primary keys
                    field = Field.objects.get(pk=field_data['field'])
                    field_data['field'] = field
                    field_data['product'] = product

                    # Tạo FieldValue với primary keys đã được chuyển đổi
                    try: 
                        FieldValue.objects.create(**field_data)
                    except FieldValue.DoesNotExist:
                        return Response({'status': 400, 'message': 'FieldValue does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Lưu attachment 
                for attachment in attachments_data:
                    try:
                        attachment['publication'] = product 
                        Attachment.objects.create(**attachment)
                    except Exception as e:
                        raise serializers.ValidationError(e)
                    
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
        
        except KeyError as e:
            raise serializers.ValidationError({"status": 400, "error": f"The field {e} is missing."})
        except Category.DoesNotExist:
            raise serializers.ValidationError({"status": 400, "error": "The specified category does not exist."})
        except Exception as e:
            raise serializers.ValidationError({'status': 400, 'error': str(e)})
    
    def update(self, instance, validated_data):
        # Logic cập nhật bài đăng
        instance.product.name = validated_data['product']['name']
        instance.product.description = validated_data['product']['description']
        instance.product.price = validated_data['product']['price']
        instance.product.is_available = validated_data['product']['is_available']
        
        category = validated_data['product']['category']
        instance.product.category = category
        # Lưu lại đối tượng đã cập nhật
        instance.product.save()
        # Cập nhật các trường liên quan
        for field_data in validated_data['fields']:
            field = Field.objects.get(pk=field_data['field'])
            field_value = FieldValue.objects.get(field=field, product=instance.product)
            field_value.value = field_data['value']
            field_value.save()
            
        # Update or create attachments
        for attachment_data in validated_data['attachments']:
            attachment_data['publication'] = instance.product
            attachment, created = Attachment.objects.get_or_create(file=attachment_data['file'], defaults={'file_type': attachment_data['file_type']}, publication=instance.product)
            if not created:
                attachment.file_type = attachment_data['file_type']
                attachment.file = attachment_data['file']
                attachment.save()
            
        # Cập nhật các trường khác 
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
        user_serializer = UserSerializer(instance=user)
        data['user'] = user_serializer.data
        
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
class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = OrderItem   
        fields = '__all__'
    def to_internal_value(self, data):
        data['product'] = data.pop('product_id', None)
        return super().to_internal_value(data)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance=instance.product).data
        representation['product']['user'] = UserSerializer(instance=instance.product.user).data
        representation['order'] = OrderDetailSerializer(instance=instance.order).data
        return representation
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'
    def create(self, validated_data):
        items_data = validated_data['items']
        data_without_items = {key: value for key, value in validated_data.items() if key != 'items'}
        order = Order.objects.create(**data_without_items)
        for item_data in items_data:
            product = item_data['product']
            user = User.objects.get(pk=product.user.id)
            OrderItem.objects.create(order=order, product=product, seller=user)
        return order
    def update(self, instance, validated_data):
        instance.status = validated_data.pop('status')
        instance.save()
        return instance
