from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='产品名称')
    description = models.TextField(verbose_name='产品描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'

    def __str__(self):
        return self.name

class Iteration(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='iterations', verbose_name='所属产品')
    version = models.CharField(max_length=50, verbose_name='版本号')
    status_choices = [
        ('planning', '规划中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='planning', verbose_name='状态')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    description = models.TextField(verbose_name='迭代描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '迭代'
        verbose_name_plural = '迭代'

    def __str__(self):
        return f"{self.product.name} - {self.version}"

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
    summary = models.TextField(verbose_name="版本概述", blank=True, null=True)

    class Meta:
        verbose_name = "版本"
        verbose_name_plural = "版本"
        ordering = ['-release_date']

    def __str__(self):
        return f"{self.product.name} - {self.get_type_display()} - {self.version_number}"

class Requirement(models.Model):
    PRIORITY_CHOICES = [
        (1, 'P1'),
        (2, 'P2'),
        (3, 'P3'),
    ]
    
    STATUS_CHOICES = [
        ('待开发', '待开发'),
        ('开发中', '开发中'),
        ('开发完成', '开发完成'),
    ]

    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='requirements', verbose_name="版本")
    issue_id = models.CharField(max_length=50, verbose_name="需求ID")
    title = models.CharField(max_length=200, verbose_name="需求标题")
    description = models.TextField(verbose_name="需求描述", blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name="优先级")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='待开发', verbose_name="状态")
    is_key_feature = models.BooleanField(default=False, verbose_name="是否核心功能")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "需求"
        verbose_name_plural = "需求"
        ordering = ['priority', 'status']

    def __str__(self):
        return self.title

class RemovedRequirement(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('移除', '移除'),
        ('推迟', '推迟'),
        ('变更', '变更'),
    ]

    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='removed_requirements', verbose_name="版本")
    issue_id = models.CharField(max_length=50, verbose_name="需求ID")
    title = models.CharField(max_length=200, verbose_name="需求标题")
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES, verbose_name="变更类型")
    change_reason = models.TextField(verbose_name="变更原因")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "移除/变更需求"
        verbose_name_plural = "移除/变更需求"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.change_type})"

class ProcessedData(models.Model):
    """存储预处理的数据"""
    data_type = models.CharField(max_length=50, help_text='数据类型，如products, calendar_events等')
    data = models.JSONField(help_text='预处理后的JSON数据')
    last_updated = models.DateTimeField(auto_now=True, help_text='最后更新时间')

    class Meta:
        verbose_name = '预处理数据'
        verbose_name_plural = '预处理数据'
        indexes = [
            models.Index(fields=['data_type']),
        ]

    def __str__(self):
        return f"{self.data_type} - {self.last_updated}"

class LocalProject(models.Model):
    """本地项目数据"""
    project_code = models.CharField(max_length=100, unique=True, verbose_name="项目代码")
    project_name = models.CharField(max_length=200, verbose_name="项目名称")
    department = models.CharField(max_length=100, verbose_name="部门")
    sub_department = models.CharField(max_length=100, null=True, blank=True, verbose_name="子部门")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "本地项目"
        verbose_name_plural = "本地项目"
        indexes = [
            models.Index(fields=['project_code']),
            models.Index(fields=['department', 'sub_department']),
        ]

    def __str__(self):
        return f"{self.project_name} ({self.project_code})"

class LocalVersion(models.Model):
    """本地版本数据"""
    project = models.ForeignKey(LocalProject, on_delete=models.CASCADE, related_name='versions')
    version_name = models.CharField(max_length=100, verbose_name="版本名称")
    release_type = models.CharField(max_length=20, verbose_name="发布类型")  # 版本/迭代
    status = models.CharField(max_length=50, verbose_name="状态")
    release_date = models.DateField(verbose_name="发布日期", null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    actual_release_date = models.DateTimeField(null=True, blank=True, verbose_name="实际发布时间")
    created_user = models.CharField(max_length=100, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "本地版本"
        verbose_name_plural = "本地版本"
        indexes = [
            models.Index(fields=['release_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.version_name}"

class LocalSprint(models.Model):
    """本地迭代数据"""
    project = models.ForeignKey(LocalProject, on_delete=models.CASCADE, related_name='sprints')
    sprint_name = models.CharField(max_length=100, verbose_name="迭代名称")
    sprint_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="迭代编号")
    status = models.CharField(max_length=50, verbose_name="状态")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    actual_release_date = models.DateTimeField(null=True, blank=True, verbose_name="实际发布时间")
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    created_user = models.CharField(max_length=100, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "本地迭代"
        verbose_name_plural = "本地迭代"
        indexes = [
            models.Index(fields=['sprint_name']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.sprint_name}"

class LocalRequirement(models.Model):
    """本地需求数据"""
    version = models.ForeignKey(LocalVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='requirements')
    sprint = models.ForeignKey(LocalSprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='requirements')
    issue_id = models.CharField(max_length=100, unique=True, verbose_name="需求ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    number = models.CharField(max_length=100, verbose_name="编号")
    priority = models.CharField(max_length=50, verbose_name="优先级")
    priority_cn = models.CharField(max_length=50, verbose_name="优先级中文")
    issue_type = models.CharField(max_length=50, verbose_name="类型")
    status = models.CharField(max_length=50, verbose_name="状态")
    status_cn = models.CharField(max_length=50, verbose_name="状态中文")
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    created_user = models.CharField(max_length=100, verbose_name="创建人")
    created_time = models.DateTimeField(verbose_name="创建时间")
    created_user_display_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="创建人显示名")
    created_user_email = models.CharField(max_length=200, null=True, blank=True, verbose_name="创建人邮箱")
    
    # 版本相关字段
    previous_version = models.CharField(max_length=100, null=True, blank=True, verbose_name="上一版本")
    current_version = models.CharField(max_length=100, null=True, blank=True, verbose_name="当前版本")
    latest_version = models.CharField(max_length=100, null=True, blank=True, verbose_name="最新版本")
    
    # 迭代相关字段
    original_sprint_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="原始迭代ID")
    original_version_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="原始版本ID")
    previous_sprint = models.CharField(max_length=100, null=True, blank=True, verbose_name="上一迭代")
    current_sprint = models.CharField(max_length=100, null=True, blank=True, verbose_name="当前迭代")
    latest_sprint = models.CharField(max_length=100, null=True, blank=True, verbose_name="最新迭代")
    
    change_status = models.CharField(
        max_length=20, 
        choices=[
            ('存在版本中', '存在版本中'),
            ('存在迭代中', '存在迭代中'),
            ('存在版本和迭代中', '存在版本和迭代中'),
            ('移出版本', '移出版本'),
            ('移出迭代', '移出迭代'),
            ('切换版本', '切换版本'),
            ('切换迭代', '切换迭代'),
            ('不在版本和迭代中', '不在版本和迭代中')
        ],
        default='不在版本和迭代中',
        verbose_name="变更状态"
    )

    class Meta:
        verbose_name = "本地需求"
        verbose_name_plural = "本地需求"
        indexes = [
            models.Index(fields=['issue_id']),
            models.Index(fields=['status']),
            models.Index(fields=['change_status']),
        ]

    def __str__(self):
        return f"{self.issue_id} - {self.title}" 