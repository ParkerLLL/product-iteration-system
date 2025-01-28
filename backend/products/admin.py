from django.contrib import admin
from .models import Product, Version, Requirement

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('product', 'version_number', 'release_date', 'status')
    list_filter = ('status', 'product', 'release_date')
    search_fields = ('version_number', 'description')
    raw_id_fields = ('product',)

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'version', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('version',)
    readonly_fields = ('created_at', 'updated_at') 