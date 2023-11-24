from django.db import models
import datetime
# Categories of Products


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

# Customers


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    address = models.CharField(
        max_length=250, default='', blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Product(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None)
    category_id = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=False, default=None)
    name = models.CharField(max_length=100)
    description = models.CharField(
        max_length=250, default='', blank=True, null=True)
    price = models.DecimalField(default=0, decimal_places=0, max_digits=9)
    image = models.ImageField(upload_to='uploads/product')
    # True: còn hàng; False: đã bán
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None)
    total_price = models.IntegerField(default=0)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)

    def __str__(self):
        return self.product


class OrderItem(models.Model):
    order_id = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=False, default=None)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, default=None)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product_id


class Cart(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None)

    def __str__(self):
        return 'Cart of' + self.user_id


class CartItem(models.Model):
    cart_id = models.ForeignKey(
        Cart, on_delete=models.CASCADE, null=False, default=None)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return self.product_id


class Transaction(models.Model):
    buyer_id = models.ForeignKey(
        User, related_name='buyer_transactions', on_delete=models.CASCADE, null=False, default=None)
    seller_id = models.ForeignKey(
        User, related_name='seller_transactions', on_delete=models.CASCADE, null=False, default=None)
    total_price = models.IntegerField(default=0)

    class Status(models.IntegerChoices):
        PENDING = 1, 'PENDING'
        UNPAID = 2, ' UNPAID'
        PAID = 3, 'PAID'
        IN_TRANSIT = 4, 'IN_TRANSIT'
        DELIVERED = 5, 'DELIVERED'
        CANCELLED = 0, 'CANCELLED'

    status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING)


class Post(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, default=None)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, default=None)
    image_urls = models.ImageField(upload_to='uploads/post')
    description = models.TextField()
    price = models.IntegerField(default=0)

    HO_CHI_MINH = 'HCM'
    DA_NANG = 'DN'
    HA_NOI = 'HN'
    ZONE_CHOICES = [
        (HO_CHI_MINH, 'Hồ Chí Minh'),
        (DA_NANG, 'Đà Nẵng'),
        (HA_NOI, 'Hà Nội'),
    ]
    zone = models.CharField(choices=ZONE_CHOICES,
                            max_length=4, default=HO_CHI_MINH)
