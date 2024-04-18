from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Product
from .resources import ProductResource

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ['name', 'sku', 'price', 'category', 'brand']