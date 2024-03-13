from rest_framework import routers
from .views import CategoryViewSet, ProductViewSet, BrandViewSet, FavoriteProductsViewSet, OrderViewSet,CurrencyViewSet

router = routers.DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'currency', CurrencyViewSet)
router.register(r'user/favorites', FavoriteProductsViewSet, basename='user-favorites')
router.register(r'user/orders', OrderViewSet, basename='user-orders')

