from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="产品名称")
    description = models.TextField(verbose_name="产品描述", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "产品"
        verbose_name_plural = "产品"

    def __str__(self):
        return self.name

class Version(models.Model):
    STATUS_CHOICES = [
        ('planning', '规划中'),
        ('developing', '开发中'),
        ('testing', '测试中'),
        ('released', '已发布'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='versions', verbose_name="产品")
    version_number = models.CharField(max_length=50, verbose_name="版本号")
    release_date = models.DateField(verbose_name="发布日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name="状态")
    description = models.TextField(verbose_name="版本描述", blank=True, null=True)

    class Meta:
        verbose_name = "版本"
        verbose_name_plural = "版本"
        ordering = ['-release_date']

    def __str__(self):
        return f"{self.product.name} - {self.version_number}"

class Requirement(models.Model):
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    ]

    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='requirements', verbose_name="版本")
    title = models.CharField(max_length=200, verbose_name="需求标题")
    description = models.TextField(verbose_name="需求描述", blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="优先级")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "需求"
        verbose_name_plural = "需求"
        ordering = ['-priority', 'status']

    def __str__(self):
        return self.title 