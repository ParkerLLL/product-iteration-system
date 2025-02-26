from django.contrib import admin
from .models import Product, Version, Requirement

# Register your models here.

# 注册模型
admin.site.register(Product)
admin.site.register(Version)
admin.site.register(Requirement)
