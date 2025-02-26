from django.contrib import admin
from .models import Product, Version, Requirement, RemovedRequirement

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('product', 'iteration_number', 'version_number', 'release_date', 'status', 'type')
    list_filter = ('status', 'type', 'product', 'release_date')
    search_fields = ('version_number', 'iteration_number', 'summary')
    raw_id_fields = ('product',)

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'title', 'version', 'priority', 'status', 'is_key_feature')
    list_filter = ('status', 'priority', 'is_key_feature', 'version', 'created_at')
    search_fields = ('issue_id', 'title', 'description')
    raw_id_fields = ('version',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RemovedRequirement)
class RemovedRequirementAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'title', 'version', 'change_type', 'created_at')
    list_filter = ('change_type', 'version', 'created_at')
    search_fields = ('issue_id', 'title', 'change_reason')
    raw_id_fields = ('version',)
    readonly_fields = ('created_at',) 