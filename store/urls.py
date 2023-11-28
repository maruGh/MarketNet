from django.urls import path
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter, DefaultRouter

from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', views.CartViewSet, basename='carts')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')

product_route = NestedSimpleRouter(router, 'products', lookup='product')
product_route.register('reviews', views.ReviewViewSet,
                       basename='product-review')
product_route.register('images', views.ProductImageViewSet,
                       basename='product-images')

cart_route = NestedSimpleRouter(router, 'carts', lookup='cart')
cart_route.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + product_route.urls + cart_route.urls

[
    # path('products/', views.ProductViewSet),
    # # path('products/<int:pk>/', views.ProductsDetailViewSet.as_view()),
    # path('collections/', views.CollectionViewSet.as_view())
]
