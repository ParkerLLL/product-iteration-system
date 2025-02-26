from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet

# 创建路由器实例
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/', include(router.urls)),
] 

