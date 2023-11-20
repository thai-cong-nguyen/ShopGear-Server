from django.contrib import admin
from . models import Category, User, Product, Order, OrderItem, Cart, CartItem, Transaction, Post
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Transaction)
admin.site.register(Post)
