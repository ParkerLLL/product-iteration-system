from django.core.management.base import BaseCommand
from django.db import connection
from products.models import ProcessedData
import logging
import json
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '处理数据并存储到ProcessedData表中'

    def handle(self, *args, **options):
        total_start_time = time.time()
        try:
            self.stdout.write(self.style.HTTP_INFO('开始数据处理任务...'))
            
            # 处理产品列表数据
            products_start_time = time.time()
            self.stdout.write('开始处理产品列表数据...')
            self.process_products()
            products_time = time.time() - products_start_time
            self.stdout.write(self.style.SUCCESS(f'产品列表数据处理完成，耗时: {products_time:.2f}秒'))
            
            # 处理日历事件数据
            calendar_start_time = time.time()
            self.stdout.write('开始处理日历事件数据...')
            self.process_calendar_events()
            calendar_time = time.time() - calendar_start_time
            self.stdout.write(self.style.SUCCESS(f'日历事件数据处理完成，耗时: {calendar_time:.2f}秒'))
            
            total_time = time.time() - total_start_time
            self.stdout.write(self.style.SUCCESS(f'所有数据处理完成！总耗时: {total_time:.2f}秒'))
            
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            self.stdout.write(self.style.ERROR(f'数据处理失败: {str(e)}'))

    def process_products(self):
        """处理产品列表数据"""
        with connection.cursor() as cursor:
            # SQL查询开始时间
            query_start_time = time.time()
            self.stdout.write('执行产品列表SQL查询...')
            
            sql = """
            SELECT 
                i.ID as issue_id,
                i.TITLE as issue_title,
                i.NUMBER as issue_number,
                i.PROJECT_ID as project_code,
                i.PRIORITY as priority,
                i.PRIORITY_CN as priority_cn,
                i.TYPE_CLASSIFY as issue_type,
                i.STATE as issue_state,
                i.STATE_CN as issue_state_cn,
                i.`DESC` as description,
                i.CREATED_USER as created_user,
                i.CREATED_TIME as created_time,
                project.project_name as project_name,
                CASE 
                    WHEN iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' THEN '版本'
                    WHEN iv.field_id = 'b2bd30c072504b569c76970d564e0715' THEN '迭代'
                    ELSE '未知'
                END as release_type,
                COALESCE(v.NAME, s.TITLE) as version_name,
                COALESCE(v.STATE, s.STATE) as version_status,
                COALESCE(v.PLAN_RELEASE_DATE, s.END_TIME) as release_date,
                COALESCE(v.`DESC`, s.PURPOSE) as version_desc,
                COALESCE(v.PROJECT_ID, s.PROJECT_ID) as version_project_id,
                COALESCE(v.CREATED_USER, s.CREATED_USER) as version_created_user,
                COALESCE(v.START_DATE, s.START_TIME) as start_time,
                COALESCE(v.ACTUAL_RELEASE_DATE, s.ACTUAL_RELEASE_DATE) as actual_release_date
            FROM 
                t_issue i
            LEFT JOIN 
                t_issue_instance_value iv ON i.ID = iv.issue_id
            LEFT JOIN 
                t_issue_version v ON iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' AND iv.value = v.ID
            LEFT JOIN 
                t_issue_sprint s ON iv.field_id = 'b2bd30c072504b569c76970d564e0715' AND iv.value = s.ID
            LEFT JOIN 
                devops_ci_projectmanager.t_project as project ON i.project_id = project.english_name
            WHERE 
                i.TYPE_CLASSIFY IN ('DEMAND', 'BUG')
                AND iv.field_id IN ('672b5f7d003842e6b8e4141cea6fe139', 'b2bd30c072504b569c76970d564e0715')
            ORDER BY 
                project.project_name, release_date DESC
            """
            
            cursor.execute(sql)
            query_time = time.time() - query_start_time
            self.stdout.write(f'SQL查询执行完成，耗时: {query_time:.2f}秒')
            
            # 获取结果开始时间
            fetch_start_time = time.time()
            self.stdout.write('开始获取查询结果...')
            
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            fetch_time = time.time() - fetch_start_time
            self.stdout.write(f'获取查询结果完成，获取到 {len(results)} 条记录，耗时: {fetch_time:.2f}秒')
            
            # 数据处理开始时间
            process_start_time = time.time()
            self.stdout.write('开始处理数据结构...')
            
            organized_data = self.organize_data(results)
            
            process_time = time.time() - process_start_time
            self.stdout.write(f'数据结构处理完成，耗时: {process_time:.2f}秒')
            
            # 保存数据开始时间
            save_start_time = time.time()
            self.stdout.write('开始保存处理后的数据...')
            
            ProcessedData.objects.update_or_create(
                data_type='products',
                defaults={'data': organized_data}
            )
            
            save_time = time.time() - save_start_time
            self.stdout.write(f'数据保存完成，耗时: {save_time:.2f}秒')

    def process_calendar_events(self):
        """处理日历事件数据"""
        with connection.cursor() as cursor:
            # SQL查询开始时间
            query_start_time = time.time()
            self.stdout.write('执行日历事件SQL查询...')
            
            sql = """
            SELECT DISTINCT
                COALESCE(v.ID, s.ID) as id,
                COALESCE(v.NAME, s.TITLE) as title,
                COALESCE(v.PLAN_RELEASE_DATE, s.END_TIME) as release_date,
                COALESCE(v.STATE, s.STATE) as status,
                p.NAME as project_space,
                p.ID as project_space_id,
                CASE 
                    WHEN iv.field_id = '672b5f7d003842e6b8e4141cea6fe139' THEN 'version'
                    WHEN iv.field_id = 'b2bd30c072504b569c76970d564e0715' THEN 'iteration'
                    ELSE 'unknown'
                END as type
            FROM 
                t_issue i
            LEFT JOIN 
                t_issue_instance_value iv ON i.ID = iv.issue_id
            LEFT JOIN 
                t_issue_version v ON iv.value = v.ID AND iv.field_id = '672b5f7d003842e6b8e4141cea6fe139'
            LEFT JOIN 
                t_issue_sprint s ON iv.value = s.ID AND iv.field_id = 'b2bd30c072504b569c76970d564e0715'
            LEFT JOIN
                t_project p ON i.PROJECT_ID = p.ID
            WHERE 
                i.TYPE_CLASSIFY IN ('DEMAND', 'BUG')
                AND iv.field_id IN ('672b5f7d003842e6b8e4141cea6fe139', 'b2bd30c072504b569c76970d564e0715')
                AND COALESCE(v.PLAN_RELEASE_DATE, s.END_TIME) IS NOT NULL
            ORDER BY 
                release_date DESC
            """
            
            cursor.execute(sql)
            query_time = time.time() - query_start_time
            self.stdout.write(f'SQL查询执行完成，耗时: {query_time:.2f}秒')
            
            # 数据处理开始时间
            process_start_time = time.time()
            self.stdout.write('开始处理日历事件数据...')
            
            events = []
            for row in cursor.fetchall():
                if row[2]:  # 只添加有日期的事件
                    events.append({
                        'id': row[0],
                        'title': f"{row[4]} - {row[1]}",
                        'date': row[2].strftime('%Y-%m-%d') if row[2] else None,
                        'extendedProps': {
                            'status': row[3],
                            'projectSpaceId': row[5],
                            'projectSpace': row[4],
                            'type': row[6]
                        }
                    })
            
            process_time = time.time() - process_start_time
            self.stdout.write(f'日历事件数据处理完成，处理了 {len(events)} 条记录，耗时: {process_time:.2f}秒')
            
            # 保存数据开始时间
            save_start_time = time.time()
            self.stdout.write('开始保存日历事件数据...')
            
            ProcessedData.objects.update_or_create(
                data_type='calendar_events',
                defaults={'data': events}
            )
            
            save_time = time.time() - save_start_time
            self.stdout.write(f'日历事件数据保存完成，耗时: {save_time:.2f}秒')

    def organize_data(self, results):
        """组织数据的辅助方法"""
        organized_data = {}
        for result in results:
            project_name = result['project_name'] or ''
            project_parts = project_name.split('-')
            
            # 解析部门信息
            department = project_parts[0].strip() if len(project_parts) > 0 else '未知部门'
            sub_department = project_parts[1].strip() if len(project_parts) > 1 else None
            
            # 创建部门键
            dept_key = department
            
            if dept_key not in organized_data:
                organized_data[dept_key] = {
                    'name': department,
                    'sub_departments': {},
                    'projects': {}
                }
            
            # 确定项目应该放在哪里
            if sub_department:
                if sub_department not in organized_data[dept_key]['sub_departments']:
                    organized_data[dept_key]['sub_departments'][sub_department] = {
                        'name': sub_department,
                        'projects': {}
                    }
                target_projects = organized_data[dept_key]['sub_departments'][sub_department]['projects']
            else:
                target_projects = organized_data[dept_key]['projects']
            
            # 处理项目和版本信息
            project_code = result['project_code']
            if not project_code:
                continue
                
            if project_code not in target_projects:
                target_projects[project_code] = {
                    'code': project_code,
                    'name': project_name,
                    'versions': {}
                }
            
            version_name = result['version_name']
            if not version_name:
                continue
                
            version_key = f"{result['release_type']}_{result['release_date']}_{version_name}"
            
            if version_key not in target_projects[project_code]['versions']:
                target_projects[project_code]['versions'][version_key] = {
                    'name': version_name,
                    'type': result['release_type'],
                    'status': result['version_status'],
                    'release_date': result['release_date'],
                    'description': result['version_desc'],
                    'start_time': result['start_time'],
                    'actual_release_date': result['actual_release_date'],
                    'created_user': result['version_created_user'],
                    'requirements': []
                }
            
            target_projects[project_code]['versions'][version_key]['requirements'].append({
                'id': result['issue_id'],
                'title': result['issue_title'],
                'number': result['issue_number'],
                'state': result['issue_state'],
                'state_cn': result['issue_state_cn'],
                'type': result['issue_type'],
                'priority': result['priority'],
                'priority_cn': result['priority_cn'],
                'description': result['description'],
                'created_user': result['created_user'],
                'created_time': result['created_time']
            })

        # 转换为列表格式
        final_data = []
        for dept_name, dept_data in organized_data.items():
            department_info = {
                'name': dept_name,
                'projects': [],
                'sub_departments': []
            }
            
            for project in dept_data['projects'].values():
                project['versions'] = list(project['versions'].values())
                department_info['projects'].append(project)
            
            for sub_dept_name, sub_dept_data in dept_data['sub_departments'].items():
                sub_dept_info = {
                    'name': sub_dept_name,
                    'projects': []
                }
                for project in sub_dept_data['projects'].values():
                    project['versions'] = list(project['versions'].values())
                    sub_dept_info['projects'].append(project)
                department_info['sub_departments'].append(sub_dept_info)
            
            final_data.append(department_info)
            
        return final_data 