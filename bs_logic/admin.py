from django.contrib import admin
from .models import Category, Order, OrderItem, Product, Profile


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'phone', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    inlines = [OrderItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_kg', 'in_stock')
    list_editable = ('price_per_kg', 'in_stock')


admin.site.register(Category)
admin.site.register(Profile)