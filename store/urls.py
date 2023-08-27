from django.urls import path
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

from . import views

router = SimpleRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet, basename='collections')

product_route = NestedSimpleRouter(router, 'products', lookup='product')
product_route.register('reviews', views.ReviewViewSet,
                       basename='product-review')

urlpatterns = router.urls + product_route.urls

[
    # path('products/', views.ProductViewSet),
    # # path('products/<int:pk>/', views.ProductsDetailViewSet.as_view()),
    # path('collections/', views.CollectionViewSet.as_view())
]
