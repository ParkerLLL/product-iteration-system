from django.core.management.base import BaseCommand
from products.models import Product, Version, Requirement, RemovedRequirement
from datetime import datetime, timedelta
import random
from django.db import connection
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

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

        # 变更原因
        change_reasons = [
            '需求优先级调整',
            '技术方案变更',
            '资源配置调整',
            '客户需求变更',
            '合规性要求变更'
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
                    summary=f'第{i}个迭代，专注于{random.choice(features)}相关功能的开发'
                )
                
                # 为迭代创建需求
                for j in range(4 + random.randint(0, 3)):
                    feature = random.choice(features)
                    title = random.choice(requirement_templates).format(feature=feature)
                    Requirement.objects.create(
                        version=iteration,
                        issue_id=f'REQ-{product.id}-{i}-{j+1}',
                        title=title,
                        description=f'详细说明：{title}',
                        priority=random.randint(1, 3),
                        status=random.choice(['待开发', '开发中', '开发完成']),
                        is_key_feature=random.random() > 0.7
                    )

                # 为迭代创建移除/变更的需求
                for j in range(1 + random.randint(0, 2)):
                    feature = random.choice(features)
                    title = random.choice(requirement_templates).format(feature=feature)
                    RemovedRequirement.objects.create(
                        version=iteration,
                        issue_id=f'REM-{product.id}-{i}-{j+1}',
                        title=title,
                        change_type=random.choice(['移除', '推迟', '变更']),
                        change_reason=random.choice(change_reasons)
                    )

            # 创建版本
            version = Version.objects.create(
                product=product,
                type='version',
                version_number=f'v{current_date.year}.{current_date.month}.0',
                release_date=current_date + timedelta(days=90),
                status='规划中',
                summary=f'{current_date.year}年第{current_date.month}季度版本发布'
            )

            # 为版本创建核心需求
            for j in range(3):
                feature = random.choice(features)
                title = random.choice(requirement_templates).format(feature=feature)
                Requirement.objects.create(
                    version=version,
                    issue_id=f'REQ-{product.id}-V-{j+1}',
                    title=title,
                    description=f'详细说明：{title}',
                    priority=1,  # 版本需求都是高优先级
                    status='待开发',
                    is_key_feature=True
                )

        self.stdout.write(self.style.SUCCESS('测试数据生成完成！'))

class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                i.ID AS 需求ID,
                i.TITLE AS 需求标题,
                i.NUMBER AS 需求编号,
                i.PRIORITY AS 需求优先级,
                i.PRIORITY_CN AS 需求优先级_CN,
                i.TYPE_CLASSIFY AS 工单类型,
                i.STATE_CN AS 需求状态_CN,
                i.`DESC` AS 需求描述,
                i.CREATED_USER AS 创建人,
                i.CREATED_TIME AS 创建时间,
                CASE 
                    WHEN iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' THEN '版本'
                    WHEN iv.field_id = 'b2bd30c072504b569c76970d564e0715' THEN '迭代'
                    ELSE '未知'
                END AS 类型,
                COALESCE(v.NAME, s.TITLE) AS 名称,
                COALESCE(v.STATE, s.STATE) AS 状态,
                COALESCE(v.PLAN_RELEASE_DATE, s.END_TIME) AS 计划发布时间,
                COALESCE(v.`DESC`, s.PURPOSE) AS 简述,
                COALESCE(v.PROJECT_ID, s.PROJECT_ID) AS 项目ID,
                COALESCE(v.CREATED_USER, s.CREATED_USER) AS 创建人,
                COALESCE(v.START_DATE, s.START_TIME) AS 开始时间,
                COALESCE(v.ACTUAL_RELEASE_DATE, s.ACTUAL_RELEASE_DATE) AS 实际发布时间
            FROM 
                `t_issue` i
            LEFT JOIN 
                `t_issue_instance_value` iv ON i.ID = iv.issue_id
            LEFT JOIN 
                `t_issue_version` v ON iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' AND iv.value = v.ID
            LEFT JOIN 
                `t_issue_sprint` s ON iv.field_id = 'b2bd30c072504b569c76970d564e0715' AND iv.value = s.ID
            WHERE 
                i.CREATED_TIME >= '2025-01-01 00:00:00'
                AND i.TYPE_CLASSIFY IN ('DEMAND', 'BUG')
                AND (v.CREATED_USER IS NULL OR v.CREATED_TIME >= '2025-01-01 00:00:00')
                AND iv.field_id IN ('672b5f7d003842e6b8e4141cea6fe139', 'b2bd30c072504b569c76970d564e0715')
            """
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 按项目ID分组整理数据
            products = {}
            for result in results:
                project_id = result['项目ID']
                if project_id not in products:
                    products[project_id] = {
                        'id': project_id,
                        'name': result['名称'],
                        'versions': []
                    }
                
                version = {
                    'id': result['需求ID'],
                    'iteration_number': result['需求编号'],
                    'version_number': result['需求编号'],
                    'release_date': result['计划发布时间'],
                    'status': result['状态'],
                    'summary': result['简述'],
                    'type': result['类型'],
                    'requirements': [{
                        'issue_id': result['需求ID'],
                        'title': result['需求标题'],
                        'status': result['需求状态_CN'],
                        'priority': result['需求优先级'],
                        'description': result['需求描述']
                    }]
                }
                
                products[project_id]['versions'].append(version)
            
            return Response(list(products.values()))

    @action(detail=False, methods=['get'])
    def calendar_events(self, request):
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                i.ID,
                i.TITLE,
                COALESCE(v.PLAN_RELEASE_DATE, s.END_TIME) AS release_date,
                COALESCE(v.STATE, s.STATE) AS status,
                COALESCE(v.NAME, s.TITLE) AS name,
                COALESCE(v.PROJECT_ID, s.PROJECT_ID) AS project_id
            FROM 
                `t_issue` i
            LEFT JOIN 
                `t_issue_instance_value` iv ON i.ID = iv.issue_id
            LEFT JOIN 
                `t_issue_version` v ON iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' AND iv.value = v.ID
            LEFT JOIN 
                `t_issue_sprint` s ON iv.field_id = 'b2bd30c072504b569c76970d564e0715' AND iv.value = s.ID
            WHERE 
                i.CREATED_TIME >= '2025-01-01 00:00:00'
                AND i.TYPE_CLASSIFY IN ('DEMAND', 'BUG')
            """
            cursor.execute(sql)
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'date': row[2],
                    'extendedProps': {
                        'productId': row[5],
                        'productName': row[4],
                        'status': row[3]
                    }
                })
            return Response(events) 