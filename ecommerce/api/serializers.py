from ..models import *
from rest_framework import serializers
from rest_framework.fields import Field
from Customer.models import User


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ["id", "value"]

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = "__all__"

class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer()
    attribute_value = AttributeValueSerializer()
    
    class Meta:
        model = ProductAttribute
        fields = ["attribute", "attribute_value", "sort_order"]

class ImageSerializedField(Field):
    """A custom serializer used in Wagtail's API, now excluding SVG images for WebP conversion."""

    def to_representation(self, value):
        # Проверяем, существует ли изображение и является ли оно SVG
        if not value or value.file.url.lower().endswith('.svg'):
            return {
                "url": value.file.url if value else None,
                "alt": value.title if value else '',
                "width": value.width if value else None,
                "height": value.height if value else None,
            }

        # Возвращаем информацию об изображении, включая URL для разных размеров в формате WebP для не-SVG изображений
        return {
            # "url": value.file.url,  # Оригинальный URL изображения
            # "alt": value.title,
            # "width": value.width,
            # "height": value.height,
            "url": self.get_webp_url(value, 'fill-500x500'),
            # "card": self.get_webp_url(value, 'fill-1000x1000'),
            # "mini-card": self.get_webp_url(value, 'fill-174x174'),
        }

    def get_webp_url(self, image, rendition_filter):
        """Возвращает URL изображения в заданном размере и формате WebP, если изображение не SVG."""
        rendition = image.get_rendition(rendition_filter + "|format-webp")
        return rendition.url
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'first_name', 'last_name', 'email']

class ReviewsSerializer(serializers.ModelSerializer):
    user = UserSerializer()


    class Meta:
        model = Reviews
        fields = ['id', 'user', 'stars', 'review_text', 'created_at']
        
class BrandSerializer(serializers.ModelSerializer):
    image = ImageSerializedField()
    
    class Meta:
        model = Brand
        fields = "__all__"
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        
class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category 
        fields = ('id', 'slug', 'name')

class CategorySerializer(serializers.ModelSerializer):
    image = ImageSerializedField()
    parent = ParentCategorySerializer(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        
class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageSerializedField()
    
    class Meta:
        model = ProductImage
        fields = "__all__"
        
class ProductSerializer(serializers.ModelSerializer):
    image = ImageSerializedField()
    gallery = ProductImageSerializer(many=True, source='product_images')
    category = CategorySerializer()
    brand = BrandSerializer()
    prices_in_currencies = serializers.SerializerMethodField()
    product_attrs = ProductAttributeSerializer(many=True)
    product_reviews = ReviewsSerializer(many=True)

    
    def get_prices_in_currencies(self, obj):
        return obj.get_prices_in_all_currencies()
    
    def get_product_reviews(self, obj):
        reviews = Reviews.objects.filter(product=obj, is_visible=True)
        return ReviewSerializer(reviews, many=True, context=self.context).data
    
    def to_representation(self, instance):
        representation = super(ProductSerializer, self).to_representation(instance)
        if 'list' in self.context.get('view').action:
            representation.pop('gallery', None)
            representation.pop('sku', None)
            representation.pop('brand', None)
            representation.pop('product_attrs', None)
            representation.pop('description', None)
            representation.pop('short_description', None)
        return representation
    
    class Meta:
        model = Product
        exclude = ['live', 'site_id', 'purchases', 'latest_revision', 'live_revision', 'expired', 'expire_at', 'go_live_at', 'last_published_at', 'first_published_at', 'has_unpublished_changes']
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        
class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = UserFavoriteProduct
        fields = ['id', 'sort_order', 'user', 'product',]
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'product_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'updated_at', 'total_price', 'items']
        
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"