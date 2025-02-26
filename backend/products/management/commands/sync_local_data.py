from django.core.management.base import BaseCommand
from django.db import connections, transaction
from products.models import LocalProject, LocalVersion, LocalRequirement, LocalSprint
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.utils import IntegrityError
import json
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '从远程数据库同步数据到本地数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-cached',
            action='store_true',
            help='使用缓存的数据而不是重新查询'
        )

    def save_to_temp_file(self, data, file_name):
        """保存数据到临时文件"""
        temp_dir = 'temp_data'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str)
        
        self.stdout.write(f'数据已保存到临时文件: {file_path}')

    def load_from_temp_file(self, file_name):
        """从临时文件加载数据"""
        file_path = os.path.join('temp_data', file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def handle(self, *args, **options):
        total_start_time = time.time()
        start_datetime = datetime.now()
        
        # 记录开始时间
        logger.info(f'开始同步时间: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'开始同步时间: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # 设置更高的事务隔离级别
        with transaction.atomic():
            connection = connections['default']
            connection.settings_dict['OPTIONS'] = {
                'isolation_level': 'READ COMMITTED'
            }
            
            try:
                self.stdout.write('开始同步数据...')
                
                # 保存当前数据统计
                requirement_count = LocalRequirement.objects.all().count()
                version_count = LocalVersion.objects.all().count()
                sprint_count = LocalSprint.objects.all().count()
                project_count = LocalProject.objects.all().count()
                
                self.stdout.write(f'''
同步前数据统计：
- 需求数: {requirement_count}
- 版本数: {version_count}
- 迭代数: {sprint_count}
- 项目数: {project_count}
''')
                
                # 创建保存点用于可能的回滚
                sid = transaction.savepoint()
                
                try:
                    # 清空现有数据
                    self.stdout.write('清空本地数据...')
                    LocalRequirement.objects.all().delete()
                    LocalVersion.objects.all().delete()
                    LocalSprint.objects.all().delete()
                    LocalProject.objects.all().delete()
                    
                    # 检查是否使用缓存数据
                    if options['use_cached']:
                        self.stdout.write('使用缓存的数据...')
                        version_sprint_data = self.load_from_temp_file('version_sprint_data.json')
                        change_records = self.load_from_temp_file('change_records.json')
                        issues = self.load_from_temp_file('issues.json')
                        
                        if not all([version_sprint_data, change_records, issues]):
                            self.stdout.write(self.style.ERROR('未找到缓存数据，请先运行一次完整同步'))
                            return
                    else:
                        # 从远程数据库查询数据
                        self.stdout.write('从远程数据库获取数据...')
                        query_start = time.time()
                        
                        # 版本和迭代信息SQL
                        versions_sprints_sql = """
                        -- 获取版本信息
                        SELECT 
                            v.project_id as project_code,
                            project.project_name as project_name,
                            project.dept_name as department,
                            '672b5f7d003842e6b8e4141cea6fe139' as field_id,
                            v.ID as item_id,
                            v.NAME as item_name,
                            v.STATE as item_status,
                            v.PLAN_RELEASE_DATE as release_date,
                            v.START_DATE as start_time,
                            v.ACTUAL_RELEASE_DATE as actual_release_date,
                            v.`DESC` as description,
                            v.CREATED_USER as created_user,
                            NULL as sprint_number
                        FROM t_issue_version v
                        LEFT JOIN devops_ci_projectmanager.t_project as project 
                            ON v.project_id = project.english_name
                        WHERE v.START_DATE >= '2025-01-01'
                        GROUP BY v.ID

                        UNION ALL

                        -- 获取迭代信息
                        SELECT 
                            s.project_id as project_code,
                            project.project_name as project_name,
                            project.dept_name as department,
                            'b2bd30c072504b569c76970d564e0715' as field_id,
                            s.ID as item_id,
                            s.TITLE as item_name,
                            s.STATE as item_status,
                            s.END_TIME as release_date,
                            s.START_TIME as start_time,
                            s.ACTUAL_RELEASE_DATE as actual_release_date,
                            s.PURPOSE as description,
                            s.CREATED_USER as created_user,
                            s.ID as sprint_number
                        FROM t_issue_sprint s
                        LEFT JOIN devops_ci_projectmanager.t_project as project 
                            ON s.project_id = project.english_name
                        WHERE s.START_TIME >= '2025-01-01'
                        GROUP BY s.ID
                        """
                        
                        # 变更记录SQL
                        change_records_sql = """
                        -- 版本变更记录
                        SELECT 
                            i.ID as issue_id,
                            vcr.VERSION_ID as before_value,
                            NULL as after_value,
                            'version' as change_field,
                            vcr.CREATED_TIME as change_time,
                            v.NAME as before_name,
                            NULL as after_name,
                            i.NUMBER as issue_number,
                            i.TITLE as issue_title,
                            i.PROJECT_ID as project_code,
                            i.PRIORITY as priority,
                            i.PRIORITY_CN as priority_cn,
                            i.TYPE_CLASSIFY as issue_type,
                            i.STATE as issue_state,
                            i.STATE_CN as issue_state_cn,
                            i.`DESC` as description,
                            i.CREATED_USER as created_user,
                            CONVERT_TZ(i.CREATED_TIME, '+00:00', '+08:00') as created_time,
                            project.project_name as project_name,
                            project.dept_name as department,
                            vcr.OPERATION as operation_desc,
                            'ISSUE_CHANGE' as change_type
                        FROM t_issue_version_change_record vcr
                        JOIN t_issue_version v ON vcr.VERSION_ID = v.ID
                        JOIN t_issue i ON i.TITLE = SUBSTRING_INDEX(
                            SUBSTRING_INDEX(vcr.OPERATION, '"', 2),
                            '"',
                            -1
                        )
                        LEFT JOIN devops_ci_projectmanager.t_project as project 
                            ON i.project_id = project.english_name
                        WHERE vcr.TYPE = 'ISSUE_CHANGE'
                            AND vcr.OPERATION LIKE '%移出版本%'
                            AND YEAR(vcr.CREATED_TIME) = YEAR(CURDATE())

                        UNION ALL

                        -- 迭代变更记录
                        SELECT 
                            i.ID as issue_id,
                            scr.SPRINT_ID as before_value,
                            NULL as after_value,
                            'iteration' as change_field,
                            scr.CREATED_TIME as change_time,
                            s.TITLE as before_name,
                            NULL as after_name,
                            i.NUMBER as issue_number,
                            i.TITLE as issue_title,
                            i.PROJECT_ID as project_code,
                            i.PRIORITY as priority,
                            i.PRIORITY_CN as priority_cn,
                            i.TYPE_CLASSIFY as issue_type,
                            i.STATE as issue_state,
                            i.STATE_CN as issue_state_cn,
                            i.`DESC` as description,
                            i.CREATED_USER as created_user,
                            CONVERT_TZ(i.CREATED_TIME, '+00:00', '+08:00') as created_time,
                            project.project_name as project_name,
                            project.dept_name as department,
                            scr.OPERATION as operation_desc,
                            'ISSUE_CHANGE' as change_type
                        FROM t_issue_sprint_change_record scr
                        JOIN t_issue_sprint s ON scr.SPRINT_ID = s.ID
                        JOIN t_issue i ON i.TITLE = SUBSTRING_INDEX(
                            SUBSTRING_INDEX(scr.OPERATION, '"', 2),
                            '"',
                            -1
                        )
                        LEFT JOIN devops_ci_projectmanager.t_project as project 
                            ON i.project_id = project.english_name
                        WHERE scr.TYPE = 'ISSUE_CHANGE'
                            AND scr.OPERATION LIKE '%移出迭代%'
                            AND YEAR(scr.CREATED_TIME) = YEAR(CURDATE())
                        ORDER BY issue_id, change_field, change_time DESC
                        """
                        
                        # 主查询SQL
                        issues_sql = """
                        SELECT DISTINCT
                            i.ID AS issue_id,
                            i.TITLE AS issue_title,
                            i.NUMBER AS issue_number,
                            i.PROJECT_ID AS project_code,
                            i.PRIORITY AS priority,
                            i.PRIORITY_CN AS priority_cn,
                            i.TYPE_CLASSIFY AS issue_type,
                            i.STATE AS issue_state,
                            i.STATE_CN AS issue_state_cn,
                            i.`DESC` AS description,
                            i.CREATED_USER AS created_user,
                            CONVERT_TZ(i.CREATED_TIME, '+00:00', '+08:00') as created_time,
                            project.project_name AS project_name,
                            project.dept_name as department,
                            
                            -- 版本信息
                            version_field.VALUE as version_id,
                            v.NAME as version_name,
                            v.STATE as version_status,
                            
                            -- 迭代信息
                            sprint_field.VALUE as sprint_id,
                            s.TITLE as sprint_name,
                            s.STATE as sprint_status,
                            
                            tuser.username as created_user,
                            tuser.display_name as created_user_display_name,
                            tuser.email as created_user_email
                            
                        FROM t_issue i
                        LEFT JOIN devops_ci_projectmanager.t_project as project 
                            ON i.project_id = project.english_name
                        LEFT JOIN bk_user.profiles_profile as tuser 
                            ON i.created_user = tuser.username
                            
                        -- 版本关联
                        LEFT JOIN t_issue_instance_value version_field 
                            ON i.ID = version_field.ISSUE_ID 
                            AND version_field.field_id = '672b5f7d003842e6b8e4141cea6fe139'
                        LEFT JOIN t_issue_version v 
                            ON version_field.value = v.ID
                            
                        -- 迭代关联
                        LEFT JOIN t_issue_instance_value sprint_field 
                            ON i.ID = sprint_field.ISSUE_ID 
                            AND sprint_field.field_id = 'b2bd30c072504b569c76970d564e0715'
                        LEFT JOIN t_issue_sprint s 
                            ON sprint_field.value = s.ID
                            
                        WHERE i.TYPE_CLASSIFY IN ('DEMAND', 'BUG')
                            AND (v.START_DATE >= '2025-01-01' OR s.START_TIME >= '2025-01-01')
                        """
                        
                        try:
                            with connections['remote'].cursor() as cursor:
                                # 获取版本和迭代信息
                                cursor.execute(versions_sprints_sql)
                                columns = [col[0].lower() for col in cursor.description]
                                version_sprint_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                                
                                # 获取变更记录
                                cursor.execute(change_records_sql)
                                columns = [col[0].lower() for col in cursor.description]
                                change_records = [dict(zip(columns, row)) for row in cursor.fetchall()]
                                
                                # 获取所有需求数据
                                cursor.execute(issues_sql)
                                columns = [col[0].lower() for col in cursor.description]
                                issues = [dict(zip(columns, row)) for row in cursor.fetchall()]
                                
                                # 保存查询结果到临时文件
                                self.save_to_temp_file(version_sprint_data, 'version_sprint_data.json')
                                self.save_to_temp_file(change_records, 'change_records.json')
                                self.save_to_temp_file(issues, 'issues.json')
                                
                        except Exception as e:
                            logger.error(f"数据库查询失败: {str(e)}")
                            transaction.savepoint_rollback(sid)
                            raise
                        
                        query_time = time.time() - query_start
                        self.stdout.write(f'数据查询完成，总耗时: {query_time:.2f}秒')
                    
                    # 处理数据
                    try:
                        self.stdout.write('开始处理和保存数据到本地数据库...')
                        save_start = time.time()
                        
                        projects = {}
                        versions = {}
                        sprints = {}
                        no_version_issues = []
                        processed_issues = set()
                        requirements_to_create = []  # 用于存储要创建的需求
                        
                        # 处理项目信息
                        for item in version_sprint_data:
                            if not item['project_code'] or not item['project_name']:
                                continue
                                
                            try:
                                if item['project_code'] not in projects:
                                    project_parts = item['project_name'].split('-')
                                    department = item['department'] or '未知部门'  # 使用数据库中的部门名称
                                    sub_department = project_parts[1].strip() if len(project_parts) > 1 else None
                                    
                                    projects[item['project_code']] = LocalProject.objects.create(
                                        project_code=item['project_code'],
                                        project_name=item['project_name'],
                                        department=department,
                                        sub_department=sub_department
                                    )
                            except IntegrityError as e:
                                logger.warning(f"项目已存在，跳过: {item['project_code']}")
                                continue
                                
                        # 处理版本和迭代信息
                        for item in version_sprint_data:
                            try:
                                if item['field_id'] == '672b5f7d003842e6b8e4141cea6fe139':  # 版本
                                    version_key = f"{item['project_code']}_{item['item_id']}"
                                    if version_key not in versions and item['project_code'] in projects:
                                        release_date = datetime.combine(item['release_date'], datetime.min.time()) if item['release_date'] else None
                                        start_time = datetime.combine(item['start_time'], datetime.min.time()) if item['start_time'] else None
                                        actual_release_date = datetime.combine(item['actual_release_date'], datetime.min.time()) if item['actual_release_date'] else None
                                        
                                        versions[version_key] = LocalVersion.objects.create(
                                            project=projects[item['project_code']],
                                            version_name=item['item_name'],
                                            release_type='版本',
                                            status=item['item_status'] or '未知',
                                            release_date=timezone.make_aware(release_date) if release_date else None,
                                            description=item['description'] or '',
                                            start_time=timezone.make_aware(start_time) if start_time else None,
                                            actual_release_date=timezone.make_aware(actual_release_date) if actual_release_date else None,
                                            created_user=item['created_user'] or ''
                                        )
                                elif item['field_id'] == 'b2bd30c072504b569c76970d564e0715':  # 迭代
                                    sprint_key = f"{item['project_code']}_{item['item_id']}"
                                    if sprint_key not in sprints and item['project_code'] in projects:
                                        release_date = datetime.combine(item['release_date'], datetime.min.time()) if item['release_date'] else None
                                        start_time = datetime.combine(item['start_time'], datetime.min.time()) if item['start_time'] else None
                                        actual_release_date = datetime.combine(item['actual_release_date'], datetime.min.time()) if item['actual_release_date'] else None
                                        
                                        sprints[sprint_key] = LocalSprint.objects.create(
                                            project=projects[item['project_code']],
                                            sprint_name=item['item_name'],
                                            sprint_number=item['sprint_number'],
                                            status=item['item_status'] or '未知',
                                            start_time=timezone.make_aware(start_time) if start_time else None,
                                            end_time=timezone.make_aware(release_date) if release_date else None,
                                            actual_release_date=timezone.make_aware(actual_release_date) if actual_release_date else None,
                                            description=item['description'] or '',
                                            created_user=item['created_user'] or ''
                                        )
                            except Exception as e:
                                logger.error(f"处理版本/迭代数据失败: {str(e)}, item: {item}")
                                continue
                                
                        # 处理变更记录，找出已移除版本和迭代的需求
                        removed_issues = {}
                        version_changes = {}  # 按issue_id存储所有版本变更记录
                        sprint_changes = {}   # 按issue_id存储所有迭代变更记录

                        # 按issue_id分组存储所有变更记录
                        for record in change_records:
                            issue_id = record['issue_id']
                            if record['change_field'] == 'version':
                                if issue_id not in version_changes:
                                    version_changes[issue_id] = []
                                version_changes[issue_id].append(record)
                            else:  # iteration
                                if issue_id not in sprint_changes:
                                    sprint_changes[issue_id] = []
                                sprint_changes[issue_id].append(record)

                        # 处理每个需求的变更记录
                        for issue in issues:
                            issue_id = issue['issue_id']
                            
                            # 获取版本变更历史
                            issue_version_changes = version_changes.get(issue_id, [])
                            issue_sprint_changes = sprint_changes.get(issue_id, [])
                            
                            # 初始化变更状态
                            change_status = '不在版本和迭代中'
                            previous_version = None
                            previous_sprint = None
                            current_version = issue.get('version_name')
                            current_sprint = issue.get('sprint_name')
                            
                            # 处理版本变更
                            if issue_version_changes:
                                latest_change = issue_version_changes[0]  # 最新的变更记录
                                if '移出版本' in latest_change['operation_desc']:
                                    # 从版本中移出
                                    change_status = '移出版本'
                                    previous_version = latest_change['before_name']
                                    current_version = None
                            
                            # 处理迭代变更
                            if issue_sprint_changes:
                                latest_change = issue_sprint_changes[0]  # 最新的迭代变更记录
                                if '移出迭代' in latest_change['operation_desc']:
                                    # 从迭代中移出
                                    if change_status == '移出版本':
                                        change_status = '移出版本和迭代'
                                    else:
                                        change_status = '移出迭代'
                                    previous_sprint = latest_change['before_name']
                                    current_sprint = None
                            
                            # 设置当前状态
                            if current_version and current_sprint:
                                change_status = '存在版本和迭代中'
                            elif current_version:
                                change_status = '存在版本中'
                            elif current_sprint:
                                change_status = '存在迭代中'
                            
                            # 创建或更新需求记录
                            if issue_id not in processed_issues:
                                requirements_to_create.append(
                                    LocalRequirement(
                                        version=versions.get(f"{issue['project_code']}_{issue['version_id']}") if issue.get('version_id') else None,
                                        sprint=sprints.get(f"{issue['project_code']}_{issue['sprint_id']}") if issue.get('sprint_id') else None,
                                        issue_id=issue_id,
                                        title=issue['issue_title'],
                                        number=issue['issue_number'],
                                        priority=issue['priority'],
                                        priority_cn=issue['priority_cn'],
                                        issue_type=issue['issue_type'],
                                        status=issue['issue_state'],
                                        status_cn=issue['issue_state_cn'],
                                        description=issue['description'],
                                        created_user=issue['created_user'],
                                        created_time=timezone.make_aware(issue['created_time']),
                                        current_version=current_version,
                                        current_sprint=current_sprint,
                                        previous_version=previous_version,
                                        previous_sprint=previous_sprint,
                                        change_status=change_status,
                                        latest_version=None,
                                        latest_sprint=None,
                                        created_user_display_name=issue.get('created_user_display_name'),
                                        created_user_email=issue.get('created_user_email')
                                    )
                                )
                                processed_issues.add(issue_id)

                        # 批量创建需求
                        if requirements_to_create:
                            try:
                                LocalRequirement.objects.bulk_create(requirements_to_create, batch_size=1000)
                            except Exception as e:
                                logger.error(f"批量创建需求失败: {str(e)}")
                                transaction.savepoint_rollback(sid)
                                raise
                                
                        # 提交事务
                        transaction.savepoint_commit(sid)
                        
                        save_time = time.time() - save_start
                        total_time = time.time() - total_start_time
                        
                        # 在同步完成后记录结束时间和总耗时
                        end_datetime = datetime.now()
                        minutes = int(total_time // 60)
                        seconds = int(total_time % 60)
                        
                        time_str = ""
                        if minutes > 0:
                            time_str = f"{minutes}分钟"
                        time_str += f"{seconds}秒"
                        
                        logger.info(f'结束同步时间: {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
                        logger.info(f'总耗时: {time_str}')
                        
                        # 输出同步结果
                        self.stdout.write(self.style.SUCCESS(f'''
同步完成！
- 同步开始时间: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}
- 同步结束时间: {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}
- 总耗时: {time_str}
- 同步前数据:
  - 需求数: {requirement_count}
  - 版本数: {version_count}
  - 迭代数: {sprint_count}
  - 项目数: {project_count}
- 同步后数据:
  - 项目数量: {len(projects)}
  - 版本数量: {len(versions)}
  - 迭代数量: {len(sprints)}
  - 需求总数: {len(processed_issues)}
  - 无版本需求数量: {len(no_version_issues)}
'''))
                        
                    except Exception as e:
                        logger.error(f"数据处理失败: {str(e)}")
                        transaction.savepoint_rollback(sid)
                        raise
                        
                except Exception as e:
                    logger.error(f"同步过程失败: {str(e)}")
                    transaction.savepoint_rollback(sid)
                    raise
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'同步失败: {str(e)}'))
                raise 