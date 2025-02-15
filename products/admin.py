from django.contrib import admin
from .models import Product, Order

# ثبت مدل Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')  # فیلدهای نمایش داده‌شده در لیست
    search_fields = ('name',)  # جستجو بر اساس نام محصول
    list_filter = ('price',)  # فیلتر بر اساس قیمت

# ثبت مدل Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_price', 'created_at')  # فیلدهای نمایش داده‌شده در لیست
    list_filter = ('created_at',)  # فیلتر بر اساس تاریخ ایجاد
    search_fields = ('product__name',)  # جستجو بر اساس نام محصول

