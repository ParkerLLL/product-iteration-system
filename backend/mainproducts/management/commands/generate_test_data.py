from django.core.management.base import BaseCommand
from mainproducts.models import Product, Version, Requirement
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = '生成测试数据'

    def handle(self, *args, **options):
        # 清空现有数据
        self.stdout.write('清空现有数据...')
        Product.objects.all().delete()

        # 产品数据
        products = [
            {
                'name': '智能家居系统',
                'description': '面向家庭用户的智能家居控制系统'
            },
            {
                'name': '企业协作平台',
                'description': '提供团队协作、文档管理、项目追踪等功能的企业级平台'
            },
            {
                'name': '数据分析平台',
                'description': '大数据分析和可视化平台，支持多种数据源和自定义报表'
            }
        ]

        # 需求标题模板
        requirement_templates = [
            '实现{feature}功能',
            '优化{feature}性能',
            '添加{feature}模块',
            '重构{feature}组件',
            '集成{feature}服务'
        ]

        # 功能特性
        features = [
            '用户认证', '数据同步', '消息推送', '报表生成',
            '权限管理', '系统监控', '数据备份', '自动部署',
            '多语言支持', '主题定制', 'API网关', '缓存机制'
        ]

        for product_data in products:
            # 创建产品
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description']
            )
            self.stdout.write(f'创建产品: {product.name}')

            # 为每个产品创建迭代和版本
            current_date = datetime.now()
            
            # 创建迭代
            for i in range(1, 4):
                iteration = Version.objects.create(
                    product=product,
                    type='iteration',
                    iteration_number=f'Sprint {current_date.strftime("%Y%m")}-{i}',
                    version_number=f'v1.{i}.0',
                    release_date=current_date + timedelta(days=i*14),
                    status=random.choice(['规划中', '开发中', '测试中', '已发布']),
                    description=f'第{i}个迭代，专注于{random.choice(features)}相关功能的开发'
                )
                
                # 为迭代创建需求
                for j in range(4 + random.randint(0, 3)):
                    feature = random.choice(features)
                    title = random.choice(requirement_templates).format(feature=feature)
                    Requirement.objects.create(
                        version=iteration,
                        title=title,
                        description=f'详细说明：{title}',
                        priority=random.choice(['高', '中', '低']),
                        status=random.choice(['待处理', '进行中', '已完成'])
                    )

            # 创建版本
            version = Version.objects.create(
                product=product,
                type='version',
                version_number=f'v{current_date.year}.{current_date.month}.0',
                release_date=current_date + timedelta(days=90),
                status='规划中',
                description=f'{current_date.year}年第{current_date.month}季度版本发布'
            )

            # 为版本创建核心需求
            for j in range(3):
                feature = random.choice(features)
                title = random.choice(requirement_templates).format(feature=feature)
                Requirement.objects.create(
                    version=version,
                    title=title,
                    description=f'详细说明：{title}',
                    priority='高',  # 版本需求都是高优先级
                    status='待处理'
                )

        self.stdout.write(self.style.SUCCESS('测试数据生成完成！')) 