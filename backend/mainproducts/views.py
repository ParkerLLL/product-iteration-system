from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Version, Requirement
from .serializers import ProductSerializer, VersionSerializer, RequirementSerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def calendar_events(self, request):
        versions = Version.objects.select_related('product').all()
        events = []
        for version in versions:
            events.append({
                'id': f'{version.product.id}-{version.id}',
                'title': f'{version.product.name} {version.version_number}',
                'date': version.release_date,
                'extendedProps': {
                    'productId': version.product.id,
                    'productName': version.product.name,
                    'versionId': version.id,
                    'version_number': version.version_number,
                    'status': version.status,
                    'type': version.type
                },
                'allDay': True,
                'display': 'block',
                'backgroundColor': 'white',
                'borderColor': '#ddd'
            })
        return Response(events)

class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer

    def get_queryset(self):
        queryset = Version.objects.all()
        product_id = self.request.query_params.get('product', None)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class RequirementViewSet(viewsets.ModelViewSet):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer

    def get_queryset(self):
        queryset = Requirement.objects.all()
        version_id = self.request.query_params.get('version', None)
        if version_id is not None:
            queryset = queryset.filter(version_id=version_id)
        return queryset
