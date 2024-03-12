from django_filters import rest_framework as filters
from ..models import Category, Product


class CategoryFilter(filters.FilterSet):
    parent_null = filters.BooleanFilter(field_name='parent', lookup_expr='isnull', label='false')

    class Meta:
        model = Category
        fields = '__all__'

class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = '__all__'
        

