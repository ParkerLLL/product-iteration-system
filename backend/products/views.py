from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from .models import LocalProject, LocalVersion, LocalRequirement, LocalSprint
from django.core.exceptions import ValidationError
import logging
import time
from rest_framework.decorators import action, api_view
from django.db.models import Prefetch, Q
from rest_framework import serializers
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

# 添加序列化器类
class LocalRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalRequirement
        fields = [
            'id', 'issue_id', 'title', 'number', 'status', 'status_cn', 
            'priority', 'priority_cn', 'description', 'previous_version',
            'current_version', 'change_status', 'latest_version'
        ]

class LocalVersionSerializer(serializers.ModelSerializer):
    requirements = LocalRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = LocalVersion
        fields = ['id', 'version_name', 'release_type', 'status', 'release_date', 'description', 'requirements']

class LocalProjectSerializer(serializers.ModelSerializer):
    versions = LocalVersionSerializer(many=True, read_only=True)

    class Meta:
        model = LocalProject
        fields = ['id', 'project_code', 'project_name', 'department', 'sub_department', 'versions']

class ProductViewSet(ViewSet):
    def list(self, request):
        """获取产品和需求列表"""
        try:
            start_time = time.time()
            logger.info("开始查询本地数据")
            
            # 从本地数据库查询，使用预加载优化查询性能
            projects = LocalProject.objects.prefetch_related(
                Prefetch(
                    'versions',
                    queryset=LocalVersion.objects.prefetch_related(
                        Prefetch(
                            'requirements',
                            queryset=LocalRequirement.objects.all()
                        )
                    )
                )
            ).all()
            
            query_time = time.time() - start_time
            logger.info(f"数据查询完成，耗时: {query_time:.2f}秒")

            # 组织数据结构
            process_start = time.time()
            organized_data = []
            
            # 按部门组织数据
            departments = {}
            for project in projects:
                dept_key = project.department
                if dept_key not in departments:
                    departments[dept_key] = {
                        'name': dept_key,
                        'sub_departments': {},
                        'projects': {}
                    }
                
                # 确定项目应该放在哪里
                if project.sub_department:
                    if project.sub_department not in departments[dept_key]['sub_departments']:
                        departments[dept_key]['sub_departments'][project.sub_department] = {
                            'name': project.sub_department,
                            'projects': {}
                        }
                    target_projects = departments[dept_key]['sub_departments'][project.sub_department]['projects']
                else:
                    target_projects = departments[dept_key]['projects']
                
                # 添加项目信息
                target_projects[project.project_code] = {
                    'code': project.project_code,
                    'name': project.project_name,
                    'versions': [{
                        'name': version.version_name,
                        'type': version.release_type,
                        'status': version.status,
                        'release_date': version.release_date,
                        'description': version.description,
                        'start_time': version.start_time,
                        'actual_release_date': version.actual_release_date,
                        'created_user': version.created_user,
                        'requirements': [{
                            'id': req.issue_id,
                            'title': req.title,
                            'number': req.number,
                            'state': req.status,
                            'state_cn': req.status_cn,
                            'type': req.issue_type,
                            'priority': req.priority,
                            'priority_cn': req.priority_cn,
                            'description': req.description,
                            'created_user': req.created_user,
                            'created_time': req.created_time,
                            'change_status': req.change_status,
                            'previous_version': req.previous_version,
                            'current_version': req.current_version,
                            'latest_version': req.latest_version
                        } for req in version.requirements.all()]
                    } for version in project.versions.all()]
                }
            
            # 转换为列表格式
            for dept_name, dept_data in departments.items():
                department_info = {
                    'name': dept_name,
                    'projects': list(dept_data['projects'].values()),
                    'sub_departments': []
                }
                
                for sub_dept_name, sub_dept_data in dept_data['sub_departments'].items():
                    sub_dept_info = {
                        'name': sub_dept_name,
                        'projects': list(sub_dept_data['projects'].values())
                    }
                    department_info['sub_departments'].append(sub_dept_info)
                
                organized_data.append(department_info)
            
            process_time = time.time() - process_start
            logger.info(f"数据处理完成，耗时: {process_time:.2f}秒")
            
            total_time = time.time() - start_time
            logger.info(f"总耗时: {total_time:.2f}秒")

            return Response({
                'status': 'success',
                'count': len(organized_data),
                'data': organized_data,
                'query_time': query_time,
                'process_time': process_time,
                'total_time': total_time
            })

        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

    @action(detail=False, methods=['get'])
    def calendar_events(self, request):
        """获取日历事件"""
        try:
            start_time = time.time()
            logger.info("开始查询日历事件")
            
            # 从本地数据库查询版本数据
            versions = LocalVersion.objects.select_related('project').prefetch_related('requirements').all()
            sprints = LocalSprint.objects.select_related('project').all()  # 查询迭代数据
            
            query_time = time.time() - start_time
            logger.info(f"数据查询完成，耗时: {query_time:.2f}秒")

            # 处理数据
            process_start = time.time()
            events = []

            # 处理版本数据
            for version in versions:
                requirements_count = version.requirements.filter(issue_type='DEMAND').count()
                bugs_count = version.requirements.filter(issue_type='BUG').count()
                
                events.append({
                    'id': f"{version.project.project_code}_{version.id}",
                    'title': f"{version.project.project_name} - {version.version_name}",
                    'date': version.release_date.strftime('%Y-%m-%d') if version.release_date else None,
                    'extendedProps': {
                        'status': version.status,
                        'projectSpaceId': version.project.project_code,
                        'projectSpace': version.project.project_name,
                        'department': version.project.department,
                        'type': 'version',  # 标记为版本
                        'created_user': version.created_user,
                        'requirements_count': requirements_count,
                        'bugs_count': bugs_count
                    }
                })

            # 处理迭代数据
            for sprint in sprints:
                events.append({
                    'id': f"{sprint.project.project_code}_{sprint.id}",
                    'title': f"{sprint.project.project_name} - {sprint.sprint_name}",
                    'date': sprint.end_time.strftime('%Y-%m-%d') if sprint.end_time else None,
                    'extendedProps': {
                        'status': sprint.status,
                        'projectSpaceId': sprint.project.project_code,
                        'projectSpace': sprint.project.project_name,
                        'type': 'sprint',  # 标记为迭代
                    }
                })
            
            process_time = time.time() - process_start
            logger.info(f"数据处理完成，处理了 {len(events)} 条记录，耗时: {process_time:.2f}秒")
            
            total_time = time.time() - start_time
            logger.info(f"总耗时: {total_time:.2f}秒")

            return Response(events)  # 返回所有事件

        except Exception as e:
            logger.error(f"获取日历事件失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

class VersionViewSet(ReadOnlyModelViewSet):
    """
    只读的版本视图集
    """
    queryset = LocalVersion.objects.all()
    serializer_class = LocalVersionSerializer

    def get_queryset(self):
        queryset = LocalVersion.objects.all()
        product_id = self.request.query_params.get('product', None)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class RequirementViewSet(ReadOnlyModelViewSet):
    """
    只读的需求视图集
    """
    queryset = LocalRequirement.objects.all()
    serializer_class = LocalRequirementSerializer

    def get_queryset(self):
        queryset = LocalRequirement.objects.all()
        version_id = self.request.query_params.get('version', None)
        if version_id is not None:
            queryset = queryset.filter(version_id=version_id)
        return queryset

class IterationViewSet(ReadOnlyModelViewSet):
    """
    只读的迭代视图集
    """
    queryset = LocalVersion.objects.all()
    serializer_class = LocalVersionSerializer

    def get_queryset(self):
        queryset = LocalVersion.objects.all()
        product_id = self.request.query_params.get('product_id', None)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset

@api_view(['GET'])
def version_requirements(request, version_name):
    """获取指定版本的所有相关需求"""
    try:
        # 使用索引优化查询
        requirements = LocalRequirement.objects.filter(
            Q(current_version=version_name) |  # 当前在此版本中的需求
            Q(previous_version=version_name)   # 从此版本移出的需求
        ).select_related('version', 'sprint').only(
            'number', 'title', 'status', 'status_cn',
            'priority', 'priority_cn', 'change_status',
            'current_version', 'current_sprint',
            'previous_version', 'previous_sprint'
        )
        
        # 使用 values() 直接获取需要的字段，减少 ORM 开销
        requirements_data = requirements.values(
            'number', 'title', 'status', 'status_cn',
            'priority', 'priority_cn', 'change_status',
            'current_version', 'current_sprint',
            'previous_version', 'previous_sprint'
        )
        
        return Response(list(requirements_data))
        
    except Exception as e:
        logger.error(f"获取版本需求失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def sprint_requirements(request, sprint_name):
    """获取指定迭代的所有相关需求"""
    # 获取迭代信息
    sprint = get_object_or_404(LocalSprint, sprint_name=sprint_name)
    
    # 获取与该迭代相关的所有需求
    requirements = LocalRequirement.objects.filter(
        Q(current_sprint=sprint_name) |  # 当前在此迭代中的需求
        Q(previous_sprint=sprint_name)   # 从此迭代移出的需求
    ).select_related('version', 'sprint')
    
    # 序列化数据
    requirements_data = [{
        'number': req.number,
        'title': req.title,
        'status': req.status,
        'status_cn': req.status_cn,
        'priority': req.priority,
        'priority_cn': req.priority_cn,
        'change_status': req.change_status,
        'current_version': req.current_version,
        'current_sprint': req.current_sprint,
        'previous_version': req.previous_version,
        'previous_sprint': req.previous_sprint
    } for req in requirements]
    
    return Response(requirements_data) 