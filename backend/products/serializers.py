from rest_framework import serializers
from .models import Product, Version, Requirement

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class VersionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Version
        fields = ['id', 'product', 'product_name', 'version_number', 
                 'release_date', 'status', 'description']

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__' 