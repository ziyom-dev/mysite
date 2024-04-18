# views.py

from .serializers import UserSerializer, BrandSerializer, CategorySerializer, ProductSerializer, FavoriteSerializer, OrderSerializer, CurrencySerializer, ReviewsSerializer, CreateReviewSerializer, AddressSerializer,OtpSerializer
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
from rest_fuzzysearch import search, sort

from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from django.urls import reverse

# otp_views.py


from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.validators import validate_international_phonenumber


from .otp import send_otp, verify_otp
from .utils import send_telegram_message


class OtpAuth(views.APIView):
    def get(self, request):
        otps = Otp.objects.all()
        serializer = OtpSerializer(otps, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        phone_number = request.data.get("phone_number")

        # Проверка на наличие номера телефона
        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Валидация номера телефона
        try:
            validate_international_phonenumber(phone_number)
        except ValidationError:
            return Response({"error": "Invalid phone number format."}, status=status.HTTP_400_BAD_REQUEST)
        
        result = send_otp(phone_number)
        if result["success"]:
            return Response({"message": f"OTP sent to {phone_number}."}, status=status.HTTP_200_OK)
        else:
            if "remaining_time" in result:
                timer = int(result["remaining_time"])
                return Response({"timer": timer}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
        

    def put(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        # Проверка на наличие номера телефона и OTP
        if not phone_number or not otp:
            return Response({"error": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Валидация номера телефона
        try:
            validate_international_phonenumber(phone_number)
        except ValidationError:
            return Response({"error": "Invalid phone number format."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем OTP и формируем ответ
        result = verify_otp(phone_number, otp)
        if result["success"]:
            return Response({"message": result["message"], "refresh": result["refresh"], "access": result["access"], "created": result["created"]}, status=status.HTTP_200_OK)
        else:
            return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)
        


    
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
    
class ProductViewSet(viewsets.ReadOnlyModelViewSet, sort.SortedModelMixin, search.SearchableModelMixin):
    queryset = Product.objects.filter(live=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, search.RankedFuzzySearchFilter, sort.OrderingFilter,AttributeFilterBackend]
    search_fields = ['name']
    filterset_class = ProductFilter
    pagination_class = ProductsPagination
    ordering_fields = ['rank', 'name', 'price', 'views']
    lookup_field = 'slug'
    min_rank = 0.1

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
        product = self.get_object()
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
    
    def get_admin_edit_url(self, order_id):
        return reverse('wagtailsnippets_ecommerce_order:edit', args=[order_id])


    
    def get_queryset(self):
        """
        Фильтрует список заказов, чтобы показать только заказы текущего пользователя,
        и сортирует их по дате создания (новые сверху)
        """
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        with transaction.atomic():  # Используем транзакцию для обеспечения целостности данных
            
            if 'items' not in data or not data['items']:
                return Response({'error': 'Нельзя создать заказ без продуктов'}, status=status.HTTP_400_BAD_REQUEST)
            
            delivery_type = data.get('delivery_type', '')
            if delivery_type not in dict(OrderDeliveryType.choices):
                return Response({'error': 'Неверный тип доставки'}, status=status.HTTP_400_BAD_REQUEST)

            payment_type = data.get('payment_type', '')
            if payment_type not in dict(PaymentType.choices):
                return Response({'error': 'Неверный тип оплаты'}, status=status.HTTP_400_BAD_REQUEST)

            # Создаем объект Order
            order = Order.objects.create(
                user=user,
                user_name=data.get('user_name', ''),  # Используем имя пользователя по умолчанию, если не указано другое
                user_phone=data.get('user_phone', ''),  # Можете задать вашу логику для обработки телефона
                delivery_address_id=data.get('delivery_address'),  # Передаем id адреса доставки
                delivery_type=delivery_type,
                payment_type=payment_type,
                comment=data.get('comment', '')
            )

            # Обработка элементов заказа, если они есть
            if 'items' in data:
                for item_data in data['items']:
                    # Создаем каждый OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity']
                    )

                items_info = []
                for item_data in data['items']:
                    product_id = item_data['product_id']
                    quantity = item_data['quantity']
                    product = Product.objects.get(pk=product_id)
                    price_per_item = product.sale_price if product.sale_price else product.price
                    total_per_item = price_per_item * quantity
                    price_str = f"{price_per_item}$"
                    product_url = settings.FRONTEND_URL + product.parent_category.slug + '/' + product.category.slug + '/' + product.slug
                    if product.sale_price:
                        price_str += " (%)"
                    items_info.append(f"- <a href='{product_url}'>{product.name}</a> ({price_str} * {quantity} = {total_per_item}$)")
                items_str = "\n".join(items_info)
            
            
            
            message = f'New order:\nID: {order.id}\nUser: {user.username}\nDelivery Type: {delivery_type}\nPayment Type: {payment_type}\nItems:\n'
            message += items_str
            
            # Добавляем delivery_address в сообщение, если delivery_type равен 'delivery'
            if delivery_type == OrderDeliveryType.DELIVERY:
                delivery_address = order.delivery_address
                if delivery_address:
                    message += f"\nDelivery Address: <a href='{delivery_address.link}'>{delivery_address}</a>"
                    
            admin_edit_url = settings.WAGTAILADMIN_BASE_URL + self.get_admin_edit_url(order.id)
            admin_edit_link = f"<a href='{admin_edit_url}'>Edit order</a>"
                    
            message += f"\n{admin_edit_link}"

            send_telegram_message(message)
            
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