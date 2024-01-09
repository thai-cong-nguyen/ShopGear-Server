from collections.abc import Iterable
from email.policy import default
from django.db import models
import datetime
# Categories of Products
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

# Customers


class User(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    address = models.CharField(
        max_length=250, default='', blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Field(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, default=None, related_name='fields')
    name = models.CharField(max_length=255, blank=True)
    class FieldType(models.IntegerChoices):
        INPUT = 1, 'INPUT'
        SELECT = 2, ' SELECT'
        MULTISELECT = 3, 'MULTISELECT'

    field_type = models.IntegerField(choices=FieldType.choices, default=FieldType.INPUT)
    
    def __str__(self):
        return self.name


class FieldOption(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=False, default=None, related_name='options')
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None, related_name='products')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=False, default=None)
    name = models.CharField(max_length=None)
    name_without_accent = models.CharField(max_length=None, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    price = models.DecimalField(default=0, decimal_places=0, max_digits=9)
    # True: còn hàng; False: đã bán
    is_available = models.BooleanField(default=False)
    amount = models.PositiveIntegerField(default=1)
    class Status(models.IntegerChoices):
        USED = 0, 'Đã qua sử dụng'
        NEW = 1, ' Mới'
    status = models.IntegerField(choices=Status.choices, default=Status.USED)
    def __str__(self):
        return self.name
    
    
class FieldValue(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='field_values')
    def __str__(self) -> str:
        return self.field.name + ' - ' + self.value

class Attachment(models.Model):
    class AttachmentType(models.TextChoices):
        PHOTO = "Photo", _("Photo")
        VIDEO = "Video", _("Video")

    file = models.CharField(max_length=None, verbose_name="Attachment URL")
    file_type = models.CharField('File type', choices=AttachmentType.choices, max_length=10)

    publication = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Model that uses the image field', related_name='attachments', null=False, default=None)
    
    def __str__(self):
        return self.publication.name
    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        
class Status(models.IntegerChoices):
        PENDING = 1, 'Đang chờ xác nhận'
        UNPAID = 2, ' Chưa thanh toán'
        PAID = 3, 'Đã thanh toán'
        IN_TRANSIT = 4, 'Đang vận chuyển'
        DELIVERED = 5, 'Đã giao hàng',
        CANCEL_PENDING = 6, 'Chờ huỷ',
        CANCELLED = 0, 'Đã huỷ'
        
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=None, related_name='orders')
    total_price = models.IntegerField(default=0)
    ward = models.CharField(max_length=255, default='', blank=True)
    district = models.CharField(max_length=255, default='', blank=True)
    province = models.CharField(max_length=255, default='', blank=True)
    discount_code = models.CharField(max_length=255, default='', blank=True)
    phone_number = models.CharField(max_length=20, default='', blank=True)
    full_name = models.CharField(max_length=255, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING)
    def __str__(self):
        return self.full_name + ' - ' + self.phone_number + ' - ' + self.ward + ' - ' + self.district + ' - ' + self.province
    
class OrderItem(models.Model):
    order= models.ForeignKey(
        Order, on_delete=models.CASCADE, null=False, default=None, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, default=None, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=None, related_name='seller')
    confirmation_status = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return self.product.name + ' - ' + str(self.quantity)


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None)

    def __str__(self):
        return 'Cart of' + self.user


class CartItem(models.Model):
    cart= models.ForeignKey(
        Cart, on_delete=models.CASCADE, null=False, default=None)
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return self.product

class Transaction(models.Model):
    buyer = models.ForeignKey(
        User, related_name='buyer_transactions', on_delete=models.CASCADE, null=False, default=None)
    seller = models.ForeignKey(
        User, related_name='seller_transactions', on_delete=models.CASCADE, null=False, default=None)
    total_price = models.IntegerField(default=0)

    status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING)


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None, related_name='posts')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, default=None, related_name='products')
    description = models.TextField()

    HO_CHI_MINH = 'HCM'
    DA_NANG = 'DN'
    HA_NOI = 'HN'
    CAN_THO = 'CT'
    HAI_PHONG = 'HP'

    ZONE_CHOICES = [    
        (HO_CHI_MINH, 'TP. Hồ Chí Minh'),
        (DA_NANG, 'Đà Nẵng'),
        (HA_NOI, 'Hà Nội'),
        (CAN_THO, 'Cần Thơ'),
        (HAI_PHONG, 'Hải Phòng')
    ]
    zone = models.CharField(choices=ZONE_CHOICES,
                            max_length=4, default=HO_CHI_MINH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts')
    likes_count = models.IntegerField(default=0)
    
    def save(self, *args, **kw):
        self.updated_at = datetime.time()
        super().save(*args, **kw)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - '  + self.product.name

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    