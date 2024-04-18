# ecommerce.models.py
from django.db import models

from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import *
from wagtail.fields import RichTextField
from django.core.exceptions import ValidationError
from wagtail.models import Orderable, ClusterableModel, DraftStateMixin, RevisionMixin, PreviewableMixin
from modelcluster.models import ParentalKey
from autoslug import AutoSlugField
from django.db import transaction
from Customer.models import User, Address
from .widgets import UserChooserWidget, AttributeValueChooserWidget, AttributeChooserWidget, AttributeGroupChooserWidget,CategoryChooserWidget,AddressChooserWidget
from wagtail.search import index
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.html import format_html
from phonenumber_field.modelfields import PhoneNumberField


        
class Category(MPTTModel):
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True)
    slug = AutoSlugField(populate_from='name', editable=True, unique=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', limit_choices_to={'level': 0})
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    
    def clean(self):
        super().clean()
        if self.parent and self.parent.id == self.id:
            raise ValidationError("Категория не может быть родителем для самой себя.")

    def __list_str__(self):
        return format_html("<span style='padding-left:{}px'>{}</span>", self.level * 20, self.name)
    
    def __str__(self):
        return self.name
    
    class MPTTMeta:
        order_insertion_by = ['name']
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
              
class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', editable=True, unique=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+', null=True
    )
    
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

class AttributeGroup(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
        InlinePanel("attributes", label="Attributes"),
    ]
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Attribute Group")
        verbose_name_plural = _("Attribute Groups")

class Attribute(Orderable, ClusterableModel):
    name = models.CharField(max_length=255)
    group = ParentalKey(AttributeGroup, on_delete=models.CASCADE, related_name="attributes")


    panels = [
        FieldPanel('name'),
        InlinePanel("values", label="Values"),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")

class AttributeValue(Orderable):
    value = models.CharField(max_length=255)
    attribute = ParentalKey(Attribute, on_delete=models.CASCADE, related_name="values")

    panels = [
        FieldPanel('attribute'),
        FieldPanel('value'),
    ]
    
    def __str__(self):
        return self.value
    
    class Meta:
        verbose_name = _("Attribute value")
        verbose_name_plural = _("Attribute values")

class Availability(models.TextChoices):
    OUTOFSTOCK = 'OutOfStock', 'Нет в наличии'
    INSTOCK = 'InStock', 'Есть в наличии'
    SOON = 'Soon', 'Скоро'
    
class Product(index.Indexed, DraftStateMixin, RevisionMixin, ClusterableModel):
    # Components 
    name = models.CharField(max_length=255)
    sku = models.CharField(blank=True, null=True, max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    parent_category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='parent_category')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='category')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    availability = models.CharField(max_length=20, choices=Availability.choices, default=Availability.SOON)
    description = RichTextField(blank=True)
    short_description = models.TextField(blank=True, max_length=160)
    slug = AutoSlugField(populate_from='name', editable=True, unique=True, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    views = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    purchases = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    site_id = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    
    category_root_level = models.IntegerField(default=0)
    # Main
    main_panels = [
        FieldPanel("name"),
        FieldPanel("sku"),
        FieldPanel("price"),
        FieldPanel("sale_price"),
        FieldRowPanel([
            FieldPanel("parent_category", widget=CategoryChooserWidget(linked_fields={'level': '#id_category_root_level'})),
            FieldPanel("category", widget=CategoryChooserWidget(linked_fields={'parent': '#id_parent_category'})),
        ]),
        FieldPanel("brand"),
    ]
    
    # Content
    content_panels = [
        FieldPanel("description"),
        FieldPanel("short_description"),
    ]
    
    # Attributes
    attributes_panels = [
        InlinePanel('product_attrs', label='Атрибут', heading='Атрибуты'),
    ]
    
    # Gellery
    gallery_panels = [
        FieldPanel('image'),
        InlinePanel('gallery', label='Галерея')
    ]
    
    # Reviews
    reviews_panels = [
        InlinePanel('product_reviews', label="Отзывы"),
    ]
    
    # Counters
    counters_panels = [
        FieldPanel("views", read_only=True),
        FieldPanel("purchases", read_only=True),
    ]
    
    # Settings
    settings_panels = [
        FieldPanel("slug"),
        FieldPanel("availability"),
        FieldPanel("category_root_level", attrs = {
            'hidden': 'true'
        }),
    ]
    
    # Handler
    edit_handler = TabbedInterface(
        [
            ObjectList(main_panels, heading='Main'),
            ObjectList(content_panels, heading='Content'),
            ObjectList(attributes_panels, heading='Attributes'),
            ObjectList(gallery_panels, heading='Gallery'),
            ObjectList(reviews_panels, heading='Reviews'),
            ObjectList(counters_panels, heading='Counters'),
            ObjectList(settings_panels, heading='Settings'),
        ]
    )
    
    def get_prices_in_all_currencies(self):
        prices = {}
        for currency in Currency.objects.all():
            prices[currency.code] = {
                "symbol": currency.symbol,
                "price": self.price * currency.exchange_rate
            }
        return prices

    def __str__(self):
        return f"{self.name}"
    
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        
class ProductImage(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('image'),
    ]
    
class ProductAttribute(ClusterableModel, Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='product_attrs')
    attribute_group = models.ForeignKey(AttributeGroup, on_delete=models.CASCADE)
    
    
    panels = [
       FieldPanel('attribute_group',widget=AttributeGroupChooserWidget()),
       InlinePanel('attrs')
    ]
    
    class Meta:
        unique_together = ('product', 'attribute_group',)
    
class ProductAttributeAttrs(Orderable):
    product_attribute = ParentalKey(ProductAttribute, on_delete=models.CASCADE, related_name='attrs')
    attribute       = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    panels = [
        FieldRowPanel(
            [
                FieldPanel('attribute', widget=AttributeChooserWidget(linked_fields={
                    'group': {'match': r'^id_product_attrs-\d+-', 'append': 'attribute_group'}
                })),
                FieldPanel('attribute_value', widget=AttributeValueChooserWidget(linked_fields={
                    'attribute': {'match': r'^id_product_attrs-\d+-attrs-\d+-', 'append': 'attribute'}
                }))
            ]
        )
    ]
 
class UserFavoriteProduct(Orderable):
    user = ParentalKey(User, on_delete=models.CASCADE, related_name='favorite_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s favorite {self.product.name}"

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'В ожидании'
    PROCESSING = 'processing', 'Обработка'
    SHIPPED = 'shipped', 'Отправлено'
    DELIVERED = 'delivered', 'Доставлено'
    CANCELED = 'canceled', 'Отменено'
    
class OrderDeliveryType(models.TextChoices):
    DELIVERY = 'delivery', 'Доставка'
    SELF_DELIVERY = 'self-delivery', 'Самовывоз'
    
class PaymentType(models.TextChoices):
    CASH = 'cash', 'Наличные'
    CARD = 'card', 'Карта'

class Order(ClusterableModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    user_name = models.CharField(max_length=255, null=True)
    user_phone = PhoneNumberField(region="UZ", null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    delivery_type = models.CharField(max_length=20, choices=OrderDeliveryType.choices, default=OrderDeliveryType.DELIVERY)
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, default=PaymentType.CASH)
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total = sum(item.product_price * item.quantity for item in self.items.all())
        self.total_price = total
        super().save(update_fields=['total_price'])

    main_panels = [
        FieldPanel("user", widget=UserChooserWidget),
        FieldPanel("user_name"),
        FieldPanel("user_phone"),
        FieldPanel('delivery_address', widget=AddressChooserWidget(linked_fields={'user': '#id_user'})),
        InlinePanel("items", label="Order Items"),
        FieldPanel("total_price", read_only=True),
        FieldPanel("status"),
        FieldPanel("delivery_type"),
        FieldPanel("payment_type"),
        FieldPanel("comment"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(main_panels, heading='Order Details'),
        ]
    )
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

class OrderItem(Orderable):
    order = ParentalKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    panels = [
        FieldPanel('product'),
        FieldPanel('quantity'),
        FieldRowPanel(
            [
                FieldPanel('product_price' , read_only=True),
                FieldPanel('total_price' , read_only=True),
            ]
        )
    ]
    
        
    def save(self, *args, **kwargs):
        creating = not self.pk  # Проверяем, создается ли новый объект

        if creating and self.product_id:  # Если это новый объект и продукт задан
            # Записываем текущую цену продукта в момент создания OrderItem
            self.product_price = self.product.price

        # Обновляем total_price на основе сохраненной цены и количества
        self.total_price = self.product_price * self.quantity

        super(OrderItem, self).save(*args, **kwargs)

        # Обновляем total_price в Order
        self._update_order_total_price()

    def _update_order_total_price(self):
        with transaction.atomic():
            total = sum(item.product_price * item.quantity for item in OrderItem.objects.filter(order=self.order))
            self.order.total_price = total
            self.order.save(update_fields=['total_price'])

    def __str__(self):
        return f"{self.quantity} x {self.product.name} = {self.total_price}"

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
              
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # Код валюты (например, "USD" для доллара)
    name = models.CharField(max_length=100)  # Название валюты (например, "US Dollar")
    symbol = models.CharField(max_length=5)  # Символ валюты (например, "$")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)  # Курс обмена к базовой валюте
    # is_base_currency = models.BooleanField(default=False)  # Является ли валюта базовой
    
    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencys")
        
    def __str__(self):
        return self.code  # Вернем код валюты как строковое представление

class Reviews(models.Model):
    user = ParentalKey(User, on_delete=models.CASCADE, related_name='user_reviews')
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    stars = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])  # Оценка от 1 до 5
    review_text = models.TextField(blank=True, null=True)  # Текст отзыва, необязательный
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания отзыва
    is_visible = models.BooleanField(default=True)
    
    main_panels = [
        FieldPanel("user", widget=UserChooserWidget),
        FieldRowPanel(
            [
                FieldPanel("stars"),
                FieldPanel("is_visible"),
            ]
        ),
        FieldPanel("review_text"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(main_panels, heading='Review Details'),
        ]
    )
    
    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

class Otp(models.Model):
    phone_number = PhoneNumberField(region="UZ", unique=True, primary_key=True)
    otp = models.IntegerField(null=True)
    time = models.DateTimeField(auto_now=True)
    attempts = models.IntegerField(default=3)