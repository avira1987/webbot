from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} for {self.product.name}"
    
# هر سفارش شامل اطلاعات زیر است:

# product: محصولی که سفارش داده شده است (ارتباط به مدل Product).
# quantity: تعداد محصول سفارش‌داده‌شده.
# total_price: قیمت کل سفارش (محاسبه‌شده از طریق ضرب قیمت محصول در تعداد).
# created_at: تاریخ و زمان ثبت سفارش (به صورت خودکار تنظیم می‌شود).
    