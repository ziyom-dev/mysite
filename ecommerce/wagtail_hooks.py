# ecommerce.wagtail_hooks.py
from django.urls import re_path

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import Category, Product, Brand, Order, Currency, Reviews
from .models import AttributeGroup, Attribute, AttributeValue, ProductAttribute, ProductAttributeAttrs, Otp
from Customer.models import User

class OtpSnippetViewSet(SnippetViewSet):
    model = Otp
    inspect_view_enabled = True
    base_url_path = "otp"
    
register_snippet(OtpSnippetViewSet)


    
class CurrencySnippetViewSet(SnippetViewSet):
    model = Currency
    icon = "dollar-sign"
    inspect_view_enabled = True
    base_url_path = "ecommerce/currency"
    
class ReviewsSnippetViewSet(SnippetViewSet):
    model = Reviews
    icon = "list-ul"
    inspect_view_enabled = True
    base_url_path = "ecommerce/reviews"


class CustomerSnippetViewSet(SnippetViewSet):
    model = User
    icon = "group"
    inspect_view_enabled = True
    base_url_path = "ecommerce/customers"
    
    search_fields = ('phone_number','first_name','last_name')

    
    def get_queryset(self, *args, **kwargs):
        # Возвращаем всех пользователей, являющихся клиентами
        return User.objects.filter(is_superuser=False)

    
class OrderSnippetViewSet(SnippetViewSet):
    model = Order
    icon = "orders"
    inspect_view_enabled = True
    base_url_path = "ecommerce/orders"
    list_filter = ('status',)
    list_display = ('__str__', 'user', 'created_at', 'updated_at', 'total_price', 'status')

class EcommerceGroup(SnippetViewSetGroup):
    menu_label = "Ecommerce"
    base_url_path = "ecommerce"
    menu_icon = "cart"  # change as required
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
    icon = "layer-group"
    inspect_view_enabled = True
    base_url_path = "shop/categories"
    list_filter = ('parent',)
    list_display = ('__list_str__', 'description', 'slug', 'parent')
    list_export = ('name', 'description', 'slug', 'parent', 'image')

class ProductSnippetViewSet(SnippetViewSet):
    model = Product
    ordering = ("name",)
    icon = "pick"
    inspect_view_enabled = True
    list_display = ('name','image','category', 'price', 'live')
    list_filter = ('category', 'brand', 'live')
    search_fields = ('name',)
    base_url_path = "shop/products"
    
class BrandSnippetViewSet(SnippetViewSet):    
    model = Brand
    icon = "wagtail-icon"
    ordering = ("name",)
    search_fields = ("name",)
    list_display = ('image','name','slug')
    inspect_view_enabled = True
    base_url_path = "shop/brands"

class ShopMenuGroup(SnippetViewSetGroup):
    menu_label = "Shop"
    base_url_path = "shop"
    menu_icon = "store"  # change as required
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
from .views import user_chooser_viewset,attribute_value_chooser_viewset, attribute_chooser_viewset, attribute_group_chooser_viewset, category_chooser_viewset, address_chooser_viewset

@hooks.register("register_icons")
def register_icons(icons):
    return icons + ['mysite/store.svg', 'mysite/cart.svg', 'mysite/layer-group.svg', 'mysite/dollar-sign.svg', 'mysite/orders.svg']

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

@hooks.register('register_admin_viewset')
def register_category_chooser_viewset():
    return category_chooser_viewset

@hooks.register('register_admin_viewset')
def register_address_chooser_viewset():
    return address_chooser_viewset




@hooks.register('construct_snippet_action_menu')
def make_publish_default_action_for_snippets(menu_items, request, context):
    for (index, item) in enumerate(menu_items):
        if item.name == 'action-publish':
            # Вынимаем элемент из списка
            menu_items.pop(index)
            # Вставляем его в начало списка, делая основным
            menu_items.insert(0, item)
            break
from django.utils.html import format_html

@hooks.register('insert_global_admin_js', order=100)
def global_admin_js():
    return format_html('<script src="{}"></script>', '/static/js/mysite.js')