from django_filters import rest_framework as filters
from rest_framework import filters as flt

from ..models import Category, Product

class AttributeFilterBackend(flt.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        attr_values_str = request.query_params.get('attr', '')
        attr_values = [int(value) for value in attr_values_str.split(',') if value.isdigit()]
        filtered_products = []
        for product in queryset:
            found_values = set()
            for product_attr in product.product_attrs.all():
                for attr in product_attr.attrs.all():
                    if attr.attribute_value_id in attr_values:
                        found_values.add(attr.attribute_value_id)
            if set(attr_values).issubset(found_values):
                filtered_products.append(product.id)
        return queryset.filter(id__in=filtered_products)


class CategoryFilter(filters.FilterSet):
    parent_null = filters.BooleanFilter(field_name='parent', lookup_expr='isnull', label='false')

    class Meta:
        model = Category
        fields = '__all__'

class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = '__all__'
        

