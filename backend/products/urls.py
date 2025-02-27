from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, version_requirements, sprint_requirements, LocalProjectViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'products_localproject', LocalProjectViewSet, basename='localproject')

urlpatterns = [
    path('', include(router.urls)),
    path('api/requirements/version/<str:version_name>/', version_requirements, name='version-requirements'),
    path('api/requirements/sprint/<str:sprint_name>/', sprint_requirements, name='sprint-requirements'),

] 