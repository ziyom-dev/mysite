# views.py

from .serializers import UserSerializer, BrandSerializer, CategorySerializer, ProductSerializer, FavoriteSerializer, OrderSerializer, CurrencySerializer, ReviewsSerializer, CreateReviewSerializer, AddressSerializer
from ..models import *
from Customer.models import Address
from .pagination import *
from .filters import *

from rest_framework import viewsets, status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView
from django.db.models import Case, When, Q, F, FloatField


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
    
class CurrentUserView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
class ShopBaseViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = BrandsPagination
    search_fields = ['name']
    lookup_field = 'slug'
    
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    search_fields = ['code']
    lookup_field = 'code'
    
class ProductReviewsView(views.APIView):
    # Установим разрешение AllowAny как базовое, чтобы все могли видеть отзывы
    permission_classes = [AllowAny]

    def get_permissions(self):
        """
        Инстанцируем и возвращаем список разрешений, которые этот представление требует.
        """
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        return super(ProductReviewsView, self).get_permissions()

    def get(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        reviews = Reviews.objects.filter(product=product)
        serializer = ReviewsSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Сохраняем отзыв, передавая user как дополнительный аргумент в save()
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ShopBaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name']
    filterset_class = CategoryFilter
    pagination_class = CategoriesPagination
    lookup_field = 'slug'
    def get_queryset(self):
        queryset = Category.objects.all()
        parent_slug = self.request.query_params.get('parent_slug', None)

        if parent_slug is not None:
            parent_category = get_object_or_404(Category, slug=parent_slug)
            queryset = queryset.filter(parent=parent_category)

        return queryset
    
class ProductViewSet(ShopBaseViewSet):

    queryset = Product.objects.filter(live=True)
    serializer_class = ProductSerializer
    search_fields = ['$name']
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ['name', 'price', 'views']
    lookup_field = 'slug'

        # Применяем декораторы кеширования к методу list
    # @method_decorator(cache_page(60*60))  # Кеширует на 2 минуты
    # @method_decorator(vary_on_headers("Authorization", "Accept-Language"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Применяем декораторы кеширования к методу retrieve
    # @method_decorator(cache_page(60*60))  # Кеширует на 5 минут
    # @method_decorator(vary_on_headers("Authorization", "Accept-Language"))
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # Получаем объект продукта из базы данных
        product = self.get_object()
        # Увеличиваем счетчик просмотров на 1
        # Используем F() для предотвращения гонки условий при параллельных запросах
        Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
        return response

    def get_queryset(self):
        queryset = Product.objects.filter(live=True).annotate(
            actual_price=Case(
                When(sale_price__isnull=False, then=F('sale_price')),
                default=F('price'),
                output_field=FloatField()
            )
        )
        
        attr_values = self.request.query_params.get('attr', None)
        
        if attr_values:
            attr_values_list = attr_values.split(',')
            attrs_query = Q(product_attrs__attrs__attribute_value__id__in=attr_values_list)
            queryset = queryset.filter(attrs_query).distinct()
        
        brand_slug = self.request.query_params.get('brand_slug', None)
        if brand_slug is not None:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        price_from = self.request.query_params.get('price_from', None)
        price_to = self.request.query_params.get('price_to', None)

        if price_from is not None:
            queryset = queryset.filter(actual_price__gte=float(price_from))

        if price_to is not None:
            queryset = queryset.filter(actual_price__lte=float(price_to))
            
        return queryset
    
class FavoriteProductsViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем список, чтобы показать только избранные продукты текущего пользователя
        return UserFavoriteProduct.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')

        product = get_object_or_404(Product, id=product_id)

        # Проверяем, существует ли уже такая запись
        favorite_product, created = UserFavoriteProduct.objects.get_or_create(user=user, product=product)

        if created:
            return Response({'message': 'Продукт добавлен в избранные'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Продукт уже в избранных'}, status=status.HTTP_409_CONFLICT)

    def destroy(self, request, *args, **kwargs):
        favorite_product_id = kwargs.get('pk')
        favorite_product = get_object_or_404(UserFavoriteProduct, id=favorite_product_id, user=request.user)
        
        favorite_product.delete()
        return Response({'message': 'Продукт удален из избранных'}, status=status.HTTP_204_NO_CONTENT)
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        # Фильтруем список заказов, чтобы показать только заказы текущего пользователя
        return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        with transaction.atomic():  # Используем транзакцию для обеспечения целостности данных
            # Создаем объект Order
            order = Order.objects.create(user=user)

            # Обработка элементов заказа, если они есть
            if 'items' in data:
                for item_data in data['items']:
                    # Создаем каждый OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity']
                    )
            
            # Вызываем метод save для обновления total_price
            order.save()

        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)
    
    
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем список, чтобы показать только адреса текущего пользователя
        return Address.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        address_id = kwargs.get('pk')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        address.delete()
        return Response({'message': 'Адрес удален'}, status=status.HTTP_204_NO_CONTENT)