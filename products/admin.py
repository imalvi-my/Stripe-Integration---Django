from django.contrib import admin
from .models import Product

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('stripe_product_id', 'stripe_price_id', 'created_at', 'updated_at')
