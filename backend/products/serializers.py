from rest_framework import serializers
from .models import Product, Version, Requirement, RemovedRequirement, Iteration

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ['id', 'issue_id', 'title', 'status', 'priority', 'is_key_feature']

class RemovedRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemovedRequirement
        fields = ['id', 'issue_id', 'title', 'change_type', 'change_reason']

class VersionSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)
    removed_requirements = RemovedRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Version
        fields = ['id', 'iteration_number', 'version_number', 'release_date', 'status', 'summary', 'type', 'requirements', 'removed_requirements']

class ProductSerializer(serializers.ModelSerializer):
    versions = VersionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'versions']

class IterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Iteration
        fields = ['id', 'product', 'version', 'status', 'start_date', 'end_date', 
                 'description', 'created_at', 'updated_at'] 