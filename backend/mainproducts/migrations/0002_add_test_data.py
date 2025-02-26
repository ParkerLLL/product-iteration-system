from django.db import migrations
from django.utils import timezone
import datetime

def create_test_data(apps, schema_editor):
    Product = apps.get_model('mainproducts', 'Product')
    Version = apps.get_model('mainproducts', 'Version')
    Requirement = apps.get_model('mainproducts', 'Requirement')

    # 创建产品1：移动应用
    mobile_app = Product.objects.create(
        name='智慧城市移动应用',
        description='面向市民的智慧城市移动应用平台'
    )

    # 创建产品2：管理后台
    admin_system = Product.objects.create(
        name='智慧城市管理后台',
        description='智慧城市后台管理系统'
    )

    # 为移动应用创建版本
    mobile_v1 = Version.objects.create(
        product=mobile_app,
        version_number='v1.0.0',
        release_date=datetime.date(2024, 3, 1),
        status='已发布',
        description='首次发布版本'
    )

    mobile_v2 = Version.objects.create(
        product=mobile_app,
        version_number='v1.1.0',
        release_date=datetime.date(2024, 4, 1),
        status='开发中',
        description='第二次迭代版本'
    )

    mobile_v3 = Version.objects.create(
        product=mobile_app,
        version_number='v2.0.0',
        release_date=datetime.date(2024, 5, 1),
        status='规划中',
        description='重大版本更新'
    )

    # 为管理后台创建版本
    admin_v1 = Version.objects.create(
        product=admin_system,
        version_number='v1.0.0',
        release_date=datetime.date(2024, 3, 15),
        status='测试中',
        description='首次发布版本'
    )

    admin_v2 = Version.objects.create(
        product=admin_system,
        version_number='v1.1.0',
        release_date=datetime.date(2024, 4, 15),
        status='规划中',
        description='功能优化版本'
    )

    # 为移动应用v1.0.0添加需求
    Requirement.objects.create(
        version=mobile_v1,
        title='用户注册登录功能',
        description='实现用户的注册、登录、找回密码等基础功能',
        priority='P0',
        status='已完成'
    )

    Requirement.objects.create(
        version=mobile_v1,
        title='首页信息展示',
        description='展示城市最新资讯、服务入口等信息',
        priority='P1',
        status='已完成'
    )

    # 为移动应用v1.1.0添加需求
    Requirement.objects.create(
        version=mobile_v2,
        title='在线办事功能',
        description='支持市民在线办理各类政务服务',
        priority='P0',
        status='开发中'
    )

    Requirement.objects.create(
        version=mobile_v2,
        title='消息推送系统',
        description='实现个性化消息推送功能',
        priority='P1',
        status='待开发'
    )

    # 为移动应用v2.0.0添加需求
    Requirement.objects.create(
        version=mobile_v3,
        title='AI智能客服',
        description='引入AI助手，提供7*24小时智能客服服务',
        priority='P0',
        status='规划中'
    )

    # 为管理后台v1.0.0添加需求
    Requirement.objects.create(
        version=admin_v1,
        title='数据统计分析',
        description='提供各类数据的统计分析功能',
        priority='P0',
        status='测试中'
    )

    Requirement.objects.create(
        version=admin_v1,
        title='权限管理系统',
        description='实现细粒度的权限控制',
        priority='P1',
        status='测试中'
    )

def remove_test_data(apps, schema_editor):
    Product = apps.get_model('mainproducts', 'Product')
    Product.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('mainproducts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_test_data, remove_test_data),
    ] 