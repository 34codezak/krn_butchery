from django.db import models
from decimal import Decimal
from django.conf import settings 

# Category model
class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} (KES {self.price_per_kg}/kg)'

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        READY = 'ready', 'Ready'
        COMPLETED = 'completed', 'Completed'
        CANCELLED ='cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    phone = models.CharField(max_length=20)
    delivery_address = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def total(self):
        return sum((i.subtotal for i in self.items.all()), Decimal('0'))

    def __str__(self):
        return f'Order #{self.pk} - {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product =  models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_kg =  models.DecimalField(max_digits=6, decimal_places=2)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity_kg * self.unit_price
