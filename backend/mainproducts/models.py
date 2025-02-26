from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="产品名称")
    description = models.TextField(verbose_name="产品描述", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

class Version(models.Model):
    STATUS_CHOICES = [
        ('规划中', '规划中'),
        ('开发中', '开发中'),
        ('测试中', '测试中'),
        ('已发布', '已发布'),
    ]

    TYPE_CHOICES = [
        ('iteration', '迭代'),
        ('version', '版本'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='versions', verbose_name="产品")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='iteration', verbose_name="发布类型")
    iteration_number = models.CharField(max_length=50, verbose_name="迭代号", blank=True, null=True)
    version_number = models.CharField(max_length=50, verbose_name="版本号")
    release_date = models.DateField(verbose_name="发布日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='规划中', verbose_name="状态")
    description = models.TextField(verbose_name="版本描述", blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_type_display()} - {self.version_number}"

class Requirement(models.Model):
    PRIORITY_CHOICES = [
        ('高', '高'),
        ('中', '中'),
        ('低', '低'),
    ]
    
    STATUS_CHOICES = [
        ('待处理', '待处理'),
        ('进行中', '进行中'),
        ('已完成', '已完成'),
    ]

    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='requirements', verbose_name="版本")
    title = models.CharField(max_length=200, verbose_name="需求标题")
    description = models.TextField(verbose_name="需求描述", blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='中', verbose_name="优先级")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='待处理', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.title
