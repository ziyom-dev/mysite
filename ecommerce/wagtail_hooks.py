# ecommerce.wagtail_hooks.py
from django.urls import re_path

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import Category, Product, Brand, Order, Currency, Reviews
from .models import AttributeGroup, Attribute, AttributeValue, ProductAttribute, ProductAttributeAttrs
from Customer.models import User


    
class CurrencySnippetViewSet(SnippetViewSet):
    model = Currency
    icon = "list-ul"
    inspect_view_enabled = True
    base_url_path = "ecommerce/currency"
    
class ReviewsSnippetViewSet(SnippetViewSet):
    model = Reviews
    icon = "list-ul"
    inspect_view_enabled = True
    base_url_path = "ecommerce/reviews"


class CustomerSnippetViewSet(SnippetViewSet):
    model = User
    label = "Customers"
    icon = "list-ul"
    inspect_view_enabled = True
    base_url_path = "ecommerce/customers"
    
    search_fields = ('phone_number','first_name','last_name')

    
    def get_queryset(self, *args, **kwargs):
        # Возвращаем всех пользователей, являющихся клиентами
        return User.objects.filter(is_superuser=False)

    
class OrderSnippetViewSet(SnippetViewSet):
    model = Order
    label = "Orders"
    icon = "placeholder"
    inspect_view_enabled = True
    base_url_path = "ecommerce/orders"
    list_filter = ('status',)
    list_display = ('__str__', 'user', 'created_at', 'updated_at', 'total_price', 'status')

class EcommerceGroup(SnippetViewSetGroup):
    menu_label = "Ecommerce"
    base_url_path = "ecommerce"
    menu_icon = "folder"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        CustomerSnippetViewSet,
        OrderSnippetViewSet,
        CurrencySnippetViewSet,
        ReviewsSnippetViewSet,
    )

register_snippet(EcommerceGroup)


class CategorySnippetViewSet(SnippetViewSet):
    model = Category
    ordering = ("name",)
    search_fields = ("name",)
    icon = "tag"
    inspect_view_enabled = True
    base_url_path = "shop/categories"
    list_filter = ('parent',)
    list_display = ('name', 'description', 'slug', 'parent')
    list_export = ('name', 'description', 'slug', 'parent', 'image')

class ProductSnippetViewSet(SnippetViewSet):
    model = Product
    ordering = ("name",)
    icon = "list-ul"
    inspect_view_enabled = True
    list_display = ('name','image','category', 'price', 'live')
    list_filter = ('category', 'brand', 'live')
    search_fields = ('name',)
    base_url_path = "shop/products"
    
class BrandSnippetViewSet(SnippetViewSet):    
    model = Brand
    ordering = ("name",)
    search_fields = ("name",)
    list_display = ('image','name','slug')
    inspect_view_enabled = True
    base_url_path = "shop/brands"

class ShopMenuGroup(SnippetViewSetGroup):
    menu_label = "Shop"
    base_url_path = "shop"
    menu_icon = "folder"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        CategorySnippetViewSet,
        ProductSnippetViewSet,
        BrandSnippetViewSet
    )

register_snippet(ShopMenuGroup)





class AttributeGroupSnippetViewSet(SnippetViewSet):
    model = AttributeGroup
class AttributeSnippetViewSet(SnippetViewSet):
    model = Attribute
class AttributeValueSnippetViewSet(SnippetViewSet):
    model = AttributeValue
class ProductAttributeSnippetViewSet(SnippetViewSet):
    model = ProductAttribute
class ProductAttributeAttrsSnippetViewSet(SnippetViewSet):
    model = ProductAttributeAttrs

    
class AttributeMenuGroup(SnippetViewSetGroup):
    menu_label = "Attribute"
    base_url_path = "attribute"
    menu_icon = "folder"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        AttributeGroupSnippetViewSet,
        AttributeSnippetViewSet,
        AttributeValueSnippetViewSet,
        ProductAttributeSnippetViewSet,
        ProductAttributeAttrsSnippetViewSet,
    )

register_snippet(AttributeMenuGroup)


from wagtail import hooks
from .views import user_chooser_viewset,attribute_value_chooser_viewset, attribute_chooser_viewset, attribute_group_chooser_viewset

@hooks.register('register_admin_viewset')
def register_user_chooser_viewset():
    return user_chooser_viewset

@hooks.register('register_admin_viewset')
def register_attribute_value_chooser_viewset():
    return attribute_value_chooser_viewset

@hooks.register('register_admin_viewset')
def register_attribute_chooser_viewset():
    return attribute_chooser_viewset

@hooks.register('register_admin_viewset')
def register_attribute_group_chooser_viewset():
    return attribute_group_chooser_viewset


