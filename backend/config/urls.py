from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet, VersionViewSet, RequirementViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'versions', VersionViewSet)
router.register(r'requirements', RequirementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
] 