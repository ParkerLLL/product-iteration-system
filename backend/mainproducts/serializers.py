from rest_framework import serializers
from .models import Product, Version, Requirement

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ['id', 'title', 'status', 'priority']

class VersionSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Version
        fields = ['id', 'type', 'iteration_number', 'version_number', 'release_date', 'status', 'description', 'requirements']

class ProductSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    versions = VersionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'latest_version', 'versions']

    def get_latest_version(self, obj):
        latest_version = obj.versions.order_by('-release_date').first()
        if latest_version:
            return {
                'iteration_number': latest_version.iteration_number,
                'version_number': latest_version.version_number,
                'release_date': latest_version.release_date,
                'status': latest_version.status
            }
        return None 