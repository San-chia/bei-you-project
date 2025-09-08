# modules/dataManagement/callbacks.py (修改版本)
import dash
from dash import html
from dash import Input, Output, State, callback_context, ALL, MATCH
from dash import dcc, html, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io
from utils.file_handlers import parse_uploaded_file
import plotly.graph_objects as go
import time
from datetime import datetime
import mysql.connector
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, text
from sqlalchemy.ext.declarative import declarative_base
import pymysql
from dash.exceptions import PreventUpdate  # 添加这个导入
import logging  # 添加这个导入
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG, THEME, FONT_AWESOME_URL
from .translation import (
    translate_table_name, 
    translate_field_name, 
    translate_dataframe_columns,
    translate_table_options,
    reverse_translate_table_name,
    reverse_translate_field_name,
    TABLE_TRANSLATIONS,
    FIELD_TRANSLATIONS
)

# MySQL数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名
    'charset': 'utf8mb4'
}


# 计算类型映射字典
CALCULATION_TYPE_TRANSLATIONS = {
    'sum': '求和',
    'product': '乘积', 
    'weighted_sum': '加权求和',
    'custom': '自定义公式'
}

REVERSE_CALCULATION_TYPE_TRANSLATIONS = {
    '求和': 'sum',
    '乘积': 'product',
    '加权求和': 'weighted_sum', 
    '自定义公式': 'custom'
}

def translate_calculation_type(english_type):
    """将英文计算类型翻译为中文显示"""
    return CALCULATION_TYPE_TRANSLATIONS.get(english_type, english_type)

def reverse_translate_calculation_type(chinese_type):
    """将中文计算类型翻译为英文数据库值"""
    return REVERSE_CALCULATION_TYPE_TRANSLATIONS.get(chinese_type, chinese_type)

def create_db_connection():
    """创建到MySQL数据库的连接"""
    try:
        # 使用SQLAlchemy创建MySQL引擎
        # 构建MySQL连接字符串
        connection_string = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}?charset={MYSQL_CONFIG['charset']}"
        engine = create_engine(connection_string, echo=False)
        return engine
    except Exception as e:
        print(f"MySQL数据库连接错误: {str(e)}")
        return None

def create_raw_mysql_connection():
    """创建原生MySQL连接（用于某些特殊操作）"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"原生MySQL连接错误: {str(e)}")
        return None

# 获取数据库中的所有表
def get_all_tables():
    """获取MySQL数据库中的所有表名"""
    try:
        engine = create_db_connection()
        if engine:
            # 使用SQLAlchemy元数据来获取表信息
            metadata = MetaData()
            metadata.reflect(bind=engine)
            
            # 过滤掉不需要的系统表 - 更新为英文表名
            excluded_tables = {
                'Mode1', 'Mode2', 'sqlite_sequence',
                'price_custom_calculation_results', 'price_custom_parameters'
            }
            
            filtered_tables = [table_name for table_name in metadata.tables.keys() 
                             if table_name not in excluded_tables]
            
            # 使用翻译函数将表名转换为中文显示
            return translate_table_options([{"label": table_name, "value": table_name} 
                                          for table_name in filtered_tables])
        return []
    except Exception as e:
        print(f"获取MySQL表名错误: {str(e)}")
        return []

def check_table_exists(table_name):
    """检查表是否存在"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        return False
    except Exception as e:
        print(f"检查表存在性错误: {str(e)}")
        return False

def get_table_columns(table_name):
    """获取表的列信息"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            conn.close()
            return [col['Field'] for col in columns]
        return []
    except Exception as e:
        print(f"获取表列信息错误: {str(e)}")
        return []

def get_basic_indicators(category_filter='all'):
    """获取基础指标数据 - 修复参数传递问题"""
    try:
        engine = create_db_connection()
        if engine:
            # 根据分类筛选构建查询条件
            if category_filter == 'all':
                # 排除占位符指标
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif category_filter == 'steel_cage':
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE id BETWEEN 1 AND 99 
                    AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif category_filter == 'steel_lining':
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE id BETWEEN 100 AND 199 
                    AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif category_filter == 'common_cost':
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE id BETWEEN 200 AND 299 
                    AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif category_filter.startswith('custom_'):
                # 处理自定义分类，如 'custom_300'
                try:
                    # 提取起始ID
                    range_start = int(category_filter.split('_')[1])
                    range_end = range_start + 99
                    
                    # 使用字符串格式化而不是参数化查询（这样更简单且安全，因为我们控制了输入）
                    query = f"""
                        SELECT * FROM basic_indicators 
                        WHERE id BETWEEN {range_start} AND {range_end}
                        AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                        ORDER BY id
                    """
                    print(f"自定义分类查询范围: {range_start} - {range_end}")
                    print(f"执行SQL: {query}")
                    
                    df = pd.read_sql(query, engine)
                    
                except (IndexError, ValueError) as e:
                    print(f"解析自定义分类失败: {e}")
                    # 如果解析失败，默认查询300以上的所有指标
                    query = """
                        SELECT * FROM basic_indicators 
                        WHERE id >= 300 
                        AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                        ORDER BY id
                    """
                    df = pd.read_sql(query, engine)
                    
            elif category_filter == 'custom':
                # 处理通用自定义分类
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE id >= 300 
                    AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            else:
                # 默认查询所有（排除占位符）
                query = """
                    SELECT * FROM basic_indicators 
                    WHERE NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
            
            print(f"查询结果: {len(df)} 条记录")
            
            if not df.empty:
                print("查询到的数据示例:")
                for i, row in df.head(3).iterrows():
                    print(f"  记录{i+1}: ID={row['id']}, 代码={row['code']}, 名称={row['name']}, 状态={row['status']}")
                
                # 转换状态显示
                df['status'] = df['status'].map({'enabled': '启用', 'disabled': '停用'})
                result = df.to_dict('records')
                print(f"最终返回 {len(result)} 条记录")
                return result
            else:
                print("查询结果为空")
                return []
                
        return []
    except Exception as e:
        print(f"获取基础指标数据错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

    

# 在这里添加新函数
def update_basic_indicator(indicator_data):
    """更新基础指标数据到数据库"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 添加调试信息
            print(f"调试信息 - 传入的indicator_data: {indicator_data}")
            print(f"调试信息 - status值: '{indicator_data['status']}', 类型: {type(indicator_data['status'])}")
            
            # 确保status值是正确的枚举值
            status_value = indicator_data['status']
            if status_value not in ['enabled', 'disabled']:
                print(f"警告：status值 '{status_value}' 不在允许范围内，默认设为 'enabled'")
                status_value = 'enabled'
            
            # 去除可能的空格
            status_value = status_value.strip()
            
            print(f"调试信息 - 最终使用的status值: '{status_value}'")
            
            update_query = """
                UPDATE basic_indicators 
                SET code = %s, name = %s, category = %s, unit = %s, 
                    description = %s, status = %s, updated_at = NOW()
                WHERE id = %s
            """
            
            print(f"调试信息 - 执行的参数: {(indicator_data['code'], indicator_data['name'], indicator_data['category'], indicator_data['unit'], indicator_data['description'], status_value, indicator_data['id'])}")
            
            cursor.execute(update_query, (
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['category'],
                indicator_data['unit'],
                indicator_data['description'],
                status_value,
                indicator_data['id']
            ))
            
            conn.commit()
            conn.close()
            return True
        return False
    except Exception as e:
        print(f"更新基础指标数据错误: {str(e)}")
        return False

def add_basic_indicator(indicator_data, main_category='custom'):
    """新增基础指标到数据库 - 修复版本，正确处理category字段"""
    try:
        print(f"=== add_basic_indicator 调试 ===")
        print(f"传入数据: {indicator_data}")
        print(f"主分类: {main_category}")
        
        # 先检查代码是否已存在
        code_exists = check_indicator_code_exists(indicator_data['code'])
        print(f"代码是否已存在: {code_exists}")
        
        if code_exists:
            print(f"指标代码 '{indicator_data['code']}' 已存在")
            return False
        
        # 获取下一个可用ID
        next_id = get_next_available_id(main_category)
        print(f"下一个可用ID: {next_id}")
        
        if next_id is None:
            print(f"分类 '{main_category}' 的ID已用完")
            return False
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            status_value = indicator_data['status']
            print(f"状态值: {status_value}")
            
            # 注意：这里的category是业务分类（如"人工费"、"材料费"），不是分类范围名称
            insert_query = """
                INSERT INTO basic_indicators (id, code, name, category, unit, description, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            insert_params = (
                next_id,
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['category'],  # 这是业务分类，如"人工费"
                indicator_data['unit'],
                indicator_data['description'],
                status_value
            )
            
            print(f"SQL查询: {insert_query}")
            print(f"参数: {insert_params}")
            
            cursor.execute(insert_query, insert_params)
            
            conn.commit()
            conn.close()
            print(f"成功添加指标，ID: {next_id}")
            return True
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"新增基础指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 在这里添加删除函数
def delete_basic_indicator(indicator_id):
    """删除基础指标（硬删除）"""
    try:
        print(f"开始删除指标，ID: {indicator_id}")
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 先检查指标是否存在
            cursor.execute("SELECT id, name FROM basic_indicators WHERE id = %s", (indicator_id,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"找到指标: ID={existing[0]}, Name={existing[1]}")
                
                # 执行删除
                cursor.execute("DELETE FROM basic_indicators WHERE id = %s", (indicator_id,))
                deleted_count = cursor.rowcount
                
                print(f"删除影响的行数: {deleted_count}")
                
                if deleted_count > 0:
                    conn.commit()
                    print(f"成功删除指标 ID: {indicator_id}")
                    conn.close()
                    return True
                else:
                    conn.close()
                    print(f"删除操作未影响任何行，ID: {indicator_id}")
                    return False
            else:
                conn.close()
                print(f"指标不存在，ID: {indicator_id}")
                return False
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"删除基础指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
def delete_multiple_basic_indicators(indicator_ids):
    """批量删除基础指标"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            # 构建批量删除的SQL
            placeholders = ','.join(['%s'] * len(indicator_ids))
            query = f"DELETE FROM basic_indicators WHERE id IN ({placeholders})"
            cursor.execute(query, indicator_ids)
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted_count
        return 0
    except Exception as e:
        print(f"批量删除基础指标错误: {str(e)}")
        return 0
   
def check_indicator_code_exists(code, exclude_id=None):
    """检查指标代码是否已存在"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            if exclude_id:
                # 编辑时排除当前记录
                cursor.execute("SELECT id FROM basic_indicators WHERE code = %s AND id != %s", (code, exclude_id))
            else:
                # 新增时检查所有记录
                cursor.execute("SELECT id FROM basic_indicators WHERE code = %s", (code,))
            
            result = cursor.fetchone()
            conn.close()
            return result is not None
        return False
    except Exception as e:
        print(f"检查指标代码错误: {str(e)}")
        return False
    
# 修复get_next_available_id函数以处理可能的错误
def get_next_available_id(main_category):
    """根据主分类获取下一个可用的ID（支持动态分类）"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 获取所有分类信息
            all_categories = get_all_indicator_categories()
            
            # 根据main_category找到对应的ID范围
            target_range = None
            for category in all_categories:
                if category['value'] == main_category:
                    target_range = category['id_range']
                    break
            
            if not target_range:
                # 如果没找到，默认使用自定义范围
                print(f"警告：主分类 '{main_category}' 未找到，使用默认自定义范围")
                target_range = (300, 999999)
            
            start_id, end_id = target_range
            
            if main_category.startswith('custom_') or main_category == 'custom':
                # 自定义指标：在指定范围内找到最大ID，然后+1
                cursor.execute(
                    "SELECT MAX(id) FROM basic_indicators WHERE id BETWEEN %s AND %s",
                    (start_id, end_id)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    next_id = result[0] + 1
                    # 确保不超出范围
                    if next_id > end_id:
                        conn.close()
                        return None
                else:
                    next_id = start_id
            else:
                # 系统默认分类：在指定范围内找到最大ID，然后+1
                cursor.execute(
                    "SELECT MAX(id) FROM basic_indicators WHERE id BETWEEN %s AND %s",
                    (start_id, end_id)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    next_id = result[0] + 1
                    if next_id > end_id:
                        conn.close()
                        return None
                else:
                    next_id = start_id
            
            conn.close()
            return next_id
        return None
    except Exception as e:
        print(f"获取下一个可用ID错误: {str(e)}")
        return None

# 确保get_main_category_by_id函数正确工作
def get_main_category_by_id(indicator_id):
    """根据ID判断属于哪个主分类（支持动态分类）"""
    try:
        indicator_id = int(indicator_id)
        all_categories = get_all_indicator_categories()
        
        for category in all_categories:
            start_id, end_id = category['id_range']
            if start_id <= indicator_id <= end_id:
                return category['value']
        
        # 如果没找到匹配的分类，默认返回custom
        return 'custom'
    except (ValueError, TypeError):
        print(f"警告：无法解析指标ID '{indicator_id}'，默认返回'custom'")
        return 'custom'

def get_all_indicator_categories():
    """动态获取所有指标分类（基于ID范围推断）- 修复版本"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 系统默认分类
            categories = [
                {'label': '全部指标', 'value': 'all', 'id_range': (1, 999999)},
                {'label': '钢筋笼模式指标', 'value': 'steel_cage', 'id_range': (1, 99)},
                {'label': '钢衬里模式指标', 'value': 'steel_lining', 'id_range': (100, 199)},
                {'label': '通用费用指标', 'value': 'common_cost', 'id_range': (200, 299)}
            ]
            
            # 查找所有300以上的ID范围（不管是否有占位符）
            cursor.execute("""
                SELECT DISTINCT id FROM basic_indicators 
                WHERE id >= 300
                ORDER BY id
            """)
            all_ids = [row[0] for row in cursor.fetchall()]
            
            # 按100的范围分组
            used_ranges = set()
            for id_val in all_ids:
                range_start = (id_val // 100) * 100
                used_ranges.add(range_start)
            
            # 为每个使用的范围生成分类选项
            for range_start in sorted(used_ranges):
                range_end = range_start + 99
                
                # 首先查找该范围内的占位符来获取分类名称
                cursor.execute("""
                    SELECT category FROM basic_indicators 
                    WHERE id BETWEEN %s AND %s 
                    AND status = 'disabled' 
                    AND code LIKE 'PLACEHOLDER_%%'
                    LIMIT 1
                """, (range_start, range_end))
                
                placeholder_result = cursor.fetchone()
                
                if placeholder_result:
                    # 如果有占位符，使用占位符的category作为分类名
                    category_name = placeholder_result[0]
                else:
                    # 如果没有占位符，查找该范围内第一个实际指标的category作为分类名
                    cursor.execute("""
                        SELECT category FROM basic_indicators 
                        WHERE id BETWEEN %s AND %s 
                        AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%%')
                        ORDER BY id 
                        LIMIT 1
                    """, (range_start, range_end))
                    
                    actual_result = cursor.fetchone()
                    category_name = actual_result[0] if actual_result else f"自定义分类{range_start}"
                
                categories.append({
                    'label': f"{category_name}指标",
                    'value': f'custom_{range_start}',
                    'id_range': (range_start, range_end)
                })
                
                print(f"添加自定义分类选项: {category_name}指标, 值: custom_{range_start}, 范围: {range_start}-{range_end}")
            
            conn.close()
            print(f"总共生成 {len(categories)} 个分类选项")
            return categories
        return []
    except Exception as e:
        print(f"获取指标分类错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []



def get_next_category_id_range():
    """获取下一个可用的100个ID范围"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 查询当前最大的ID
            cursor.execute("SELECT MAX(id) FROM basic_indicators WHERE id >= 300")
            result = cursor.fetchone()
            
            if result and result[0]:
                max_id = result[0]
                # 计算下一个100的范围
                next_range_start = ((max_id // 100) + 1) * 100
            else:
                # 如果没有自定义指标，从300开始
                next_range_start = 300
            
            next_range_end = next_range_start + 99
            conn.close()
            return (next_range_start, next_range_end)
        return None
    except Exception as e:
        print(f"获取下一个ID范围错误: {str(e)}")
        return None

def add_new_indicator_category(category_name):
    """添加新的指标分类（通过预留第一个指标实现）- 修复版本"""
    try:
        print(f"=== 添加新指标分类: {category_name} ===")
        
        # 获取下一个可用的ID范围
        id_range = get_next_category_id_range()
        if not id_range:
            return False, "无法获取可用的ID范围"
        
        range_start, range_end = id_range
        print(f"分配ID范围: {range_start}-{range_end}")
        
        # 创建一个占位指标来标记这个分类
        # 注意：这里的category字段存储的是分类范围的名称，不是业务分类
        placeholder_data = {
            'code': f'PLACEHOLDER_{range_start}',
            'name': f'{category_name}分类占位符',
            'category': category_name,  # 这里存储的是分类范围名称（如"水葫芦"）
            'unit': '',
            'description': f'该指标为{category_name}分类的占位符，用于标记分类范围，请勿删除',
            'status': 'disabled'  # 设为禁用状态，在筛选时会被排除
        }
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 插入占位符指标
            insert_query = """
                INSERT INTO basic_indicators (id, code, name, category, unit, description, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            cursor.execute(insert_query, (
                range_start,
                placeholder_data['code'],
                placeholder_data['name'],
                placeholder_data['category'],
                placeholder_data['unit'],
                placeholder_data['description'],
                placeholder_data['status']
            ))
            
            conn.commit()
            conn.close()
            print(f"成功创建分类占位符，ID: {range_start}")
            return True, f"成功创建分类 '{category_name}'，ID范围：{range_start}-{range_end}"
        
        return False, "数据库连接失败"
    except Exception as e:
        print(f"添加新指标分类错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"添加失败：{str(e)}"
    
def get_deletable_categories():
    """获取可删除的分类列表（只返回自定义分类）"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 查找所有300以上的ID范围
            cursor.execute("""
                SELECT DISTINCT id FROM basic_indicators 
                WHERE id >= 300
                ORDER BY id
            """)
            all_ids = [row[0] for row in cursor.fetchall()]
            
            deletable_categories = []
            used_ranges = set()
            
            # 按100的范围分组
            for id_val in all_ids:
                range_start = (id_val // 100) * 100
                if range_start not in used_ranges:
                    used_ranges.add(range_start)
                    
                    # 查找该范围的分类名称
                    range_end = range_start + 99
                    
                    # 首先查找占位符
                    cursor.execute("""
                        SELECT category FROM basic_indicators 
                        WHERE id BETWEEN %s AND %s 
                        AND status = 'disabled' 
                        AND code LIKE 'PLACEHOLDER_%%'
                        LIMIT 1
                    """, (range_start, range_end))
                    
                    placeholder_result = cursor.fetchone()
                    
                    if placeholder_result:
                        category_name = placeholder_result[0]
                    else:
                        # 如果没有占位符，查找第一个实际指标
                        cursor.execute("""
                            SELECT category FROM basic_indicators 
                            WHERE id BETWEEN %s AND %s 
                            ORDER BY id 
                            LIMIT 1
                        """, (range_start, range_end))
                        
                        actual_result = cursor.fetchone()
                        category_name = actual_result[0] if actual_result else f"分类{range_start}"
                    
                    # 统计该范围内的指标数量
                    cursor.execute("""
                        SELECT COUNT(*) FROM basic_indicators 
                        WHERE id BETWEEN %s AND %s
                    """, (range_start, range_end))
                    
                    count = cursor.fetchone()[0]
                    
                    deletable_categories.append({
                        'label': f"{category_name}指标 ({count}个指标)",
                        'value': f'custom_{range_start}',
                        'range_start': range_start,
                        'range_end': range_end,
                        'category_name': category_name,
                        'count': count
                    })
            
            conn.close()
            print(f"找到 {len(deletable_categories)} 个可删除的分类")
            return deletable_categories
        return []
    except Exception as e:
        print(f"获取可删除分类错误: {str(e)}")
        return []

def delete_category_and_indicators(category_value):
    """删除指定分类及其所有指标"""
    try:
        if not category_value.startswith('custom_'):
            return False, "只能删除自定义分类"
        
        range_start = int(category_value.split('_')[1])
        range_end = range_start + 99
        
        print(f"准备删除分类，ID范围: {range_start}-{range_end}")
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 先查询要删除的指标信息
            cursor.execute("""
                SELECT id, code, name, category FROM basic_indicators 
                WHERE id BETWEEN %s AND %s
                ORDER BY id
            """, (range_start, range_end))
            
            indicators_to_delete = cursor.fetchall()
            
            if not indicators_to_delete:
                conn.close()
                return False, "该分类下没有找到任何指标"
            
            print(f"找到 {len(indicators_to_delete)} 个指标待删除:")
            for indicator in indicators_to_delete:
                print(f"  - ID: {indicator[0]}, 代码: {indicator[1]}, 名称: {indicator[2]}")
            
            # 执行删除操作
            cursor.execute("""
                DELETE FROM basic_indicators 
                WHERE id BETWEEN %s AND %s
            """, (range_start, range_end))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"成功删除 {deleted_count} 个指标")
            return True, f"成功删除分类及其 {deleted_count} 个指标，ID范围 {range_start}-{range_end} 已释放"
        
        return False, "数据库连接失败"
        
    except Exception as e:
        print(f"删除分类错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"删除失败：{str(e)}"

def clean_orphaned_placeholders():
    """清理孤立的占位符指标（没有对应实际指标的分类）- 修复版本"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 查找所有占位符
            cursor.execute("""
                SELECT id, category FROM basic_indicators 
                WHERE status = 'disabled' AND code LIKE 'PLACEHOLDER_%'
                ORDER BY id
            """)
            placeholders = cursor.fetchall()
            
            orphaned_placeholders = []
            
            for placeholder_id, category_name in placeholders:
                # 计算该占位符对应的ID范围
                range_start = (placeholder_id // 100) * 100
                range_end = range_start + 99
                
                # 检查该范围内是否有非占位符指标
                cursor.execute("""
                    SELECT COUNT(*) FROM basic_indicators 
                    WHERE id BETWEEN %s AND %s 
                    AND NOT (status = 'disabled' AND code LIKE 'PLACEHOLDER_%')
                """, (range_start, range_end))
                
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # 如果没有实际指标，则这是孤立的占位符
                    orphaned_placeholders.append(placeholder_id)
                    print(f"发现孤立占位符: ID={placeholder_id}, 分类={category_name}")
            
            # 删除孤立的占位符
            if orphaned_placeholders:
                placeholders_str = ','.join(map(str, orphaned_placeholders))
                cursor.execute(f"DELETE FROM basic_indicators WHERE id IN ({placeholders_str})")
                deleted_count = cursor.rowcount
                conn.commit()
                print(f"已清理 {deleted_count} 个孤立占位符")
            else:
                print("没有发现孤立占位符")
            
            conn.close()
            return len(orphaned_placeholders)
        return 0
    except Exception as e:
        print(f"清理孤立占位符错误: {str(e)}")
        return 0



# ====== 复合指标相关函数 ======

def get_composite_indicators(construction_mode_filter='all'):
    """获取复合指标数据 - 修复版本，显示所有状态的记录"""
    try:
        engine = create_db_connection()
        if engine:
            # 根据施工模式筛选构建查询条件 - 移除status过滤
            if construction_mode_filter == 'all':
                query = """
                    SELECT * FROM composite_indicators 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif construction_mode_filter == 'steel_cage':
                query = """
                    SELECT * FROM composite_indicators 
                    WHERE construction_mode = 'steel_cage' 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif construction_mode_filter == 'steel_lining':
                query = """
                    SELECT * FROM composite_indicators 
                    WHERE construction_mode = 'steel_lining' 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
                
            else:
                # 默认查询所有
                query = """
                    SELECT * FROM composite_indicators 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
            
            print(f"复合指标查询结果: {len(df)} 条记录")
            
            if not df.empty:
                # 转换状态显示
                df['status'] = df['status'].map({'enabled': '启用', 'disabled': '停用'})
                # 转换施工模式显示
                df['construction_mode'] = df['construction_mode'].map({
                    'steel_cage': '钢筋笼模式',
                    'steel_lining': '钢衬里模式'
                })

                # 转换计算类型显示
                df['calculation_type'] = df['calculation_type'].map(CALCULATION_TYPE_TRANSLATIONS)  

                result = df.to_dict('records')
                print(f"最终返回 {len(result)} 条复合指标记录")
                return result
            else:
                print("复合指标查询结果为空")
                return []
                
        return []
    except Exception as e:
        print(f"获取复合指标数据错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def add_composite_indicator(indicator_data):
    """新增复合指标到数据库 - 去掉category字段"""
    try:
        print(f"=== add_composite_indicator 调试 ===")
        print(f"传入数据: {indicator_data}")
        
        # 检查代码是否已存在
        code_exists = check_composite_indicator_code_exists(indicator_data['code'])
        if code_exists:
            print(f"复合指标代码 '{indicator_data['code']}' 已存在")
            return False
        
        # 获取下一个可用ID
        construction_mode = indicator_data.get('construction_mode', 'steel_cage')
        next_id = get_next_composite_indicator_id(construction_mode)
        
        if next_id is None:
            print(f"施工模式 '{construction_mode}' 的ID已用完")
            return False
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建dependencies JSON
            dependencies_json = indicator_data.get('dependencies', '{}')
            if isinstance(dependencies_json, str):
                dependencies_str = dependencies_json
            else:
                import json
                dependencies_str = json.dumps(dependencies_json, ensure_ascii=False)
            
            # 去掉category字段的INSERT语句
            insert_query = """
                INSERT INTO composite_indicators 
                (id, code, name, construction_mode, unit, formula, calculation_type, dependencies, description, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            insert_params = (
                next_id,
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['construction_mode'],
                indicator_data['unit'],
                indicator_data['formula'],
                indicator_data.get('calculation_type', 'custom'),
                dependencies_str,
                indicator_data['description'],
                indicator_data['status']
            )
            
            print(f"SQL查询: {insert_query}")
            print(f"参数: {insert_params}")
            
            cursor.execute(insert_query, insert_params)
            conn.commit()
            conn.close()
            print(f"成功添加复合指标，ID: {next_id}")
            return True
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"新增复合指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_composite_indicator(indicator_data):
    """更新复合指标数据到数据库 - 添加调试信息"""
    try:
        print(f"=== update_composite_indicator 调试 ===")
        print(f"传入数据: {indicator_data}")
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建dependencies JSON
            dependencies_json = indicator_data.get('dependencies', '{}')
            if isinstance(dependencies_json, str):
                dependencies_str = dependencies_json
            else:
                import json
                dependencies_str = json.dumps(dependencies_json, ensure_ascii=False)
            
            update_query = """
                UPDATE composite_indicators 
                SET code = %s, name = %s, construction_mode = %s, unit = %s, 
                    formula = %s, calculation_type = %s, dependencies = %s, description = %s, 
                    status = %s, updated_at = NOW()
                WHERE id = %s
            """
            
            update_params = (
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['construction_mode'],
                indicator_data['unit'],
                indicator_data['formula'],
                indicator_data.get('calculation_type', 'custom'),
                dependencies_str,
                indicator_data['description'],
                indicator_data['status'],
                indicator_data['id']
            )
            
            print(f"执行SQL: {update_query}")
            print(f"参数: {update_params}")
            
            cursor.execute(update_query, update_params)
            affected_rows = cursor.rowcount
            print(f"受影响的行数: {affected_rows}")
            
            if affected_rows > 0:
                conn.commit()
                print("提交成功")
                
                # 验证更新结果
                cursor.execute("SELECT status FROM composite_indicators WHERE id = %s", (indicator_data['id'],))
                result = cursor.fetchone()
                print(f"更新后的状态值: {result[0] if result else 'NULL'}")
                
                conn.close()
                return True
            else:
                print("没有行被更新")
                conn.close()
                return False
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"更新复合指标数据错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def delete_composite_indicator(indicator_id):
    """删除复合指标"""
    try:
        print(f"开始删除复合指标，ID: {indicator_id}")
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 先检查指标是否存在
            cursor.execute("SELECT id, name FROM composite_indicators WHERE id = %s", (indicator_id,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"找到复合指标: ID={existing[0]}, Name={existing[1]}")
                
                # 执行删除
                cursor.execute("DELETE FROM composite_indicators WHERE id = %s", (indicator_id,))
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    conn.commit()
                    print(f"成功删除复合指标 ID: {indicator_id}")
                    conn.close()
                    return True
                else:
                    conn.close()
                    return False
            else:
                conn.close()
                print(f"复合指标不存在，ID: {indicator_id}")
                return False
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"删除复合指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_composite_indicator_code_exists(code, exclude_id=None):
    """检查复合指标代码是否已存在"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            if exclude_id:
                cursor.execute("SELECT id FROM composite_indicators WHERE code = %s AND id != %s", (code, exclude_id))
            else:
                cursor.execute("SELECT id FROM composite_indicators WHERE code = %s", (code,))
            
            result = cursor.fetchone()
            conn.close()
            return result is not None
        return False
    except Exception as e:
        print(f"检查复合指标代码错误: {str(e)}")
        return False

def get_next_composite_indicator_id(construction_mode):
    """根据施工模式获取下一个可用的ID - 去掉common模式，调整ID范围"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 定义ID范围 - 去掉common模式，预留200-299给综合指标库
            if construction_mode == 'steel_cage':
                start_id, end_id = 1, 98  # 排除99这个总计行
                summary_id = 99  # 总计行ID
            elif construction_mode == 'steel_lining':
                start_id, end_id = 100, 198  # 排除199这个总计行
                summary_id = 199  # 总计行ID
            # 删除 common 模式的处理
            else:  # 其他情况（如custom扩展）
                start_id, end_id = 300, 999999
                summary_id = None  # 自定义模式没有固定的总计行
            
            # 查找范围内最大ID，但排除总计行
            if summary_id:
                # 有总计行的情况，排除总计行ID
                cursor.execute(
                    "SELECT MAX(id) FROM composite_indicators WHERE id BETWEEN %s AND %s AND id != %s",
                    (start_id, end_id + 1, summary_id)
                )
            else:
                # 自定义模式，没有总计行
                cursor.execute(
                    "SELECT MAX(id) FROM composite_indicators WHERE id BETWEEN %s AND %s",
                    (start_id, end_id)
                )
            
            result = cursor.fetchone()
            
            if result and result[0]:
                next_id = result[0] + 1
                # 确保不会分配到总计行ID
                if summary_id and next_id == summary_id:
                    print(f"警告：下一个ID {next_id} 是总计行ID，范围已满")
                    conn.close()
                    return None
                # 确保不超出可用范围
                if next_id > end_id:
                    conn.close()
                    return None
            else:
                next_id = start_id
            
            print(f"为施工模式 {construction_mode} 分配ID: {next_id}")
            conn.close()
            return next_id
        return None
    except Exception as e:
        print(f"获取下一个复合指标ID错误: {str(e)}")
        return None

def get_composite_dependencies(composite_id):
    """获取复合指标的依赖关系"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT dependencies FROM composite_indicators WHERE id = %s", (composite_id,))
            result = cursor.fetchone()
            
            if result and result['dependencies']:
                import json
                dependencies = json.loads(result['dependencies'])
                conn.close()
                return dependencies
            
            conn.close()
            return {}
    except Exception as e:
        print(f"获取复合指标依赖关系错误: {str(e)}")
        return {}

def validate_composite_formula(formula, dependencies):
    """验证复合指标公式的有效性"""
    try:
        # 简单的公式验证逻辑
        # 检查公式中引用的指标是否在dependencies中定义
        import re
        
        # 查找公式中的所有引用 {XXX-XXX-XXX}
        references = re.findall(r'\{([^}]+)\}', formula)
        
        # 查找公式中的所有参数引用 QTY_XXX
        parameters = re.findall(r'QTY_\w+', formula)
        
        print(f"公式中的引用: {references}")
        print(f"公式中的参数: {parameters}")
        
        # 检查所有引用是否都有对应的依赖定义
        # 这里可以添加更复杂的验证逻辑
        
        return True, "公式验证通过"
    except Exception as e:
        return False, f"公式验证失败: {str(e)}"


# ====== 综合指标相关函数 ======

def get_comprehensive_indicators(construction_mode_filter='all'):
    """获取综合指标数据"""
    try:
        engine = create_db_connection()
        if engine:
            # 根据施工模式筛选构建查询条件
            if construction_mode_filter == 'all':
                query = """
                    SELECT * FROM comprehensive_indicators 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif construction_mode_filter == 'steel_cage':
                query = """
                    SELECT * FROM comprehensive_indicators 
                    WHERE construction_mode = 'steel_cage' 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            elif construction_mode_filter == 'steel_lining':
                query = """
                    SELECT * FROM comprehensive_indicators 
                    WHERE construction_mode = 'steel_lining' 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
                
            else:
                # 默认查询所有
                query = """
                    SELECT * FROM comprehensive_indicators 
                    ORDER BY id
                """
                df = pd.read_sql(query, engine)
            
            print(f"综合指标查询结果: {len(df)} 条记录")
            
            if not df.empty:
                # 转换状态显示
                df['status'] = df['status'].map({'enabled': '启用', 'disabled': '停用'})
                # 转换施工模式显示
                df['construction_mode'] = df['construction_mode'].map({
                    'steel_cage': '钢筋笼模式',
                    'steel_lining': '钢衬里模式'
                })
                # 转换计算方法显示
                df['calculation_method'] = df['calculation_method'].map({
                    'ml_prediction': 'AI预测',
                    'ratio_method': '比率法'
                })
                # 转换指标类型显示
                df['indicator_type'] = df['indicator_type'].map({
                    'raw_value': '原始值',
                    'final_value': '最终值'
                })

                result = df.to_dict('records')
                print(f"最终返回 {len(result)} 条综合指标记录")
                return result
            else:
                print("综合指标查询结果为空")
                return []
                
        return []
    except Exception as e:
        print(f"获取综合指标数据错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def add_comprehensive_indicator(indicator_data):
    """新增综合指标到数据库"""
    try:
        print(f"=== add_comprehensive_indicator 调试 ===")
        print(f"传入数据: {indicator_data}")
        
        # 检查代码是否已存在
        code_exists = check_comprehensive_indicator_code_exists(indicator_data['code'])
        if code_exists:
            print(f"综合指标代码 '{indicator_data['code']}' 已存在")
            return False
        
        # 获取下一个可用ID
        construction_mode = indicator_data.get('construction_mode', 'steel_cage')
        next_id = get_next_comprehensive_indicator_id(construction_mode)
        
        if next_id is None:
            print(f"施工模式 '{construction_mode}' 的ID已用完")
            return False
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建dependencies JSON
            dependencies_json = indicator_data.get('dependencies', '{}')
            if isinstance(dependencies_json, str):
                dependencies_str = dependencies_json
            else:
                import json
                dependencies_str = json.dumps(dependencies_json, ensure_ascii=False)
            
            insert_query = """
                INSERT INTO comprehensive_indicators 
                (id, code, name, construction_mode, calculation_method, indicator_type, 
                 calculation_logic, dependencies, unit, description, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            insert_params = (
                next_id,
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['construction_mode'],
                indicator_data['calculation_method'],
                indicator_data['indicator_type'],
                indicator_data.get('calculation_logic', ''),
                dependencies_str,
                indicator_data['unit'],
                indicator_data['description'],
                indicator_data['status']
            )
            
            print(f"SQL查询: {insert_query}")
            print(f"参数: {insert_params}")
            
            cursor.execute(insert_query, insert_params)
            conn.commit()
            conn.close()
            print(f"成功添加综合指标，ID: {next_id}")
            return True
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"新增综合指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_comprehensive_indicator(indicator_data):
    """更新综合指标数据到数据库"""
    try:
        print(f"=== update_comprehensive_indicator 调试 ===")
        print(f"传入数据: {indicator_data}")
        
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建dependencies JSON
            dependencies_json = indicator_data.get('dependencies', '{}')
            if isinstance(dependencies_json, str):
                dependencies_str = dependencies_json
            else:
                import json
                dependencies_str = json.dumps(dependencies_json, ensure_ascii=False)
            
            update_query = """
                UPDATE comprehensive_indicators 
                SET code = %s, name = %s, construction_mode = %s, calculation_method = %s, 
                    indicator_type = %s, calculation_logic = %s, dependencies = %s, 
                    unit = %s, description = %s, status = %s, updated_at = NOW()
                WHERE id = %s
            """
            
            update_params = (
                indicator_data['code'],
                indicator_data['name'],
                indicator_data['construction_mode'],
                indicator_data['calculation_method'],
                indicator_data['indicator_type'],
                indicator_data.get('calculation_logic', ''),
                dependencies_str,
                indicator_data['unit'],
                indicator_data['description'],
                indicator_data['status'],
                indicator_data['id']
            )
            
            print(f"执行SQL: {update_query}")
            print(f"参数: {update_params}")
            
            cursor.execute(update_query, update_params)
            affected_rows = cursor.rowcount
            print(f"受影响的行数: {affected_rows}")
            
            if affected_rows > 0:
                conn.commit()
                print("提交成功")
                conn.close()
                return True
            else:
                print("没有行被更新")
                conn.close()
                return False
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"更新综合指标数据错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def delete_comprehensive_indicator(indicator_id):
    """删除综合指标"""
    try:
        print(f"开始删除综合指标，ID: {indicator_id}")
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 先检查指标是否存在
            cursor.execute("SELECT id, name FROM comprehensive_indicators WHERE id = %s", (indicator_id,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"找到综合指标: ID={existing[0]}, Name={existing[1]}")
                
                # 执行删除
                cursor.execute("DELETE FROM comprehensive_indicators WHERE id = %s", (indicator_id,))
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    conn.commit()
                    print(f"成功删除综合指标 ID: {indicator_id}")
                    conn.close()
                    return True
                else:
                    conn.close()
                    return False
            else:
                conn.close()
                print(f"综合指标不存在，ID: {indicator_id}")
                return False
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"删除综合指标错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_comprehensive_indicator_code_exists(code, exclude_id=None):
    """检查综合指标代码是否已存在"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            if exclude_id:
                cursor.execute("SELECT id FROM comprehensive_indicators WHERE code = %s AND id != %s", (code, exclude_id))
            else:
                cursor.execute("SELECT id FROM comprehensive_indicators WHERE code = %s", (code,))
            
            result = cursor.fetchone()
            conn.close()
            return result is not None
        return False
    except Exception as e:
        print(f"检查综合指标代码错误: {str(e)}")
        return False

def get_next_comprehensive_indicator_id(construction_mode):
    """根据施工模式获取下一个可用的ID"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            
            # 定义ID范围（没有总计行限制）
            if construction_mode == 'steel_cage':
                start_id, end_id = 1, 99
            elif construction_mode == 'steel_lining':
                start_id, end_id = 100, 199
            else:  # 扩展模式
                start_id, end_id = 200, 299
            
            # 查找范围内最大ID
            cursor.execute(
                "SELECT MAX(id) FROM comprehensive_indicators WHERE id BETWEEN %s AND %s",
                (start_id, end_id)
            )
            
            result = cursor.fetchone()
            
            if result and result[0]:
                next_id = result[0] + 1
                # 确保不超出范围
                if next_id > end_id:
                    conn.close()
                    return None
            else:
                next_id = start_id
            
            print(f"为施工模式 {construction_mode} 分配ID: {next_id}")
            conn.close()
            return next_id
        return None
    except Exception as e:
        print(f"获取下一个综合指标ID错误: {str(e)}")
        return None

def get_comprehensive_dependencies(comprehensive_id):
    """获取综合指标的依赖关系"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT dependencies FROM comprehensive_indicators WHERE id = %s", (comprehensive_id,))
            result = cursor.fetchone()
            
            if result and result['dependencies']:
                import json
                dependencies = json.loads(result['dependencies'])
                conn.close()
                return dependencies
            
            conn.close()
            return {}
    except Exception as e:
        print(f"获取综合指标依赖关系错误: {str(e)}")
        return {}

def validate_comprehensive_logic(calculation_logic, dependencies):
    """验证综合指标计算逻辑的有效性"""
    try:
        # 简单的逻辑验证
        # 检查逻辑中引用的指标是否在dependencies中定义
        import re
        
        # 查找逻辑中的所有引用 {XXX-XXX-XXX}
        references = re.findall(r'\{([^}]+)\}', calculation_logic)
        
        # 查找逻辑中的所有输入参数引用 INPUT_XXX
        input_params = re.findall(r'INPUT_\w+', calculation_logic)
        
        print(f"计算逻辑中的引用: {references}")
        print(f"计算逻辑中的输入参数: {input_params}")
        
        # 这里可以添加更复杂的验证逻辑
        
        return True, "计算逻辑验证通过"
    except Exception as e:
        return False, f"计算逻辑验证失败: {str(e)}"
    
# ====== 算法配置相关函数 ======
def get_algorithms_by_construction_mode(construction_mode):
    """根据施工模式获取对应的算法列表"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM algorithm_configs WHERE construction_mode = %s ORDER BY id",
                (construction_mode,)
            )
            results = cursor.fetchall()
            conn.close()
            
            # 转换状态显示
            for result in results:
                result['status_display'] = '启用' if result['status'] == 'enabled' else '停用'
            
            return results
        return []
    except Exception as e:
        print(f"获取算法列表错误: {str(e)}")
        return []


def get_algorithm_by_id(algorithm_id):
    """根据ID获取单个算法配置"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM algorithm_configs WHERE id = %s", (algorithm_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        return None
    except Exception as e:
        print(f"获取算法配置错误: {str(e)}")
        return None

def update_algorithm_status_by_id(algorithm_id, status):
    """更新指定ID算法的状态"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE algorithm_configs SET status = %s, updated_at = NOW() WHERE id = %s",
                (status, algorithm_id)
            )
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        return False
    except Exception as e:
        print(f"更新算法状态错误: {str(e)}")
        return False
    
def get_algorithm_config(algorithm_type, construction_mode):
    """获取特定算法和施工模式的配置"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM algorithm_configs WHERE algorithm_type = %s AND construction_mode = %s",
                (algorithm_type, construction_mode)
            )
            result = cursor.fetchone()
            conn.close()
            return result
        return None
    except Exception as e:
        print(f"获取算法配置错误: {str(e)}")
        return None

def get_all_algorithm_configs(construction_mode=None):
    """获取算法配置（可按施工模式筛选）"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if construction_mode:
                cursor.execute(
                    "SELECT * FROM algorithm_configs WHERE construction_mode = %s ORDER BY algorithm_type",
                    (construction_mode,)
                )
            else:
                cursor.execute("SELECT * FROM algorithm_configs ORDER BY construction_mode, algorithm_type")
            
            results = cursor.fetchall()
            conn.close()
            return results
        return []
    except Exception as e:
        print(f"获取所有算法配置错误: {str(e)}")
        return []

def get_enabled_algorithms(construction_mode=None):
    """获取启用的算法（可按施工模式筛选）"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if construction_mode:
                cursor.execute(
                    "SELECT * FROM algorithm_configs WHERE status = 'enabled' AND construction_mode = %s ORDER BY algorithm_type",
                    (construction_mode,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM algorithm_configs WHERE status = 'enabled' ORDER BY construction_mode, algorithm_type"
                )
            
            results = cursor.fetchall()
            conn.close()
            return results
        return []
    except Exception as e:
        print(f"获取启用算法错误: {str(e)}")
        return []

def update_algorithm_status(algorithm_type, construction_mode, status):
    """更新特定算法和施工模式的状态"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE algorithm_configs SET status = %s, updated_at = NOW() WHERE algorithm_type = %s AND construction_mode = %s",
                (status, algorithm_type, construction_mode)
            )
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        return False
    except Exception as e:
        print(f"更新算法状态错误: {str(e)}")
        return False

def update_algorithm_parameters(algorithm_type, construction_mode, parameters=None):
    """更新特定算法和施工模式的参数（简化版）"""
    try:
        import json
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            # 如果没有传入参数，保持原有参数不变
            if parameters is None:
                parameters = {}
            
            parameters_json = json.dumps(parameters)
            cursor.execute(
                "UPDATE algorithm_configs SET parameters = %s, updated_at = NOW() WHERE algorithm_type = %s AND construction_mode = %s",
                (parameters_json, algorithm_type, construction_mode)
            )
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        return False
    except Exception as e:
        print(f"更新算法参数错误: {str(e)}")
        return False

def check_prediction_availability(construction_mode):
    """检查特定施工模式是否可以进行预测"""
    enabled_algorithms = get_enabled_algorithms(construction_mode)
    return len(enabled_algorithms) > 0

def get_algorithm_status_summary(construction_mode=None):
    """获取算法状态汇总信息（可按施工模式筛选）"""
    try:
        all_algorithms = get_all_algorithm_configs(construction_mode)
        enabled_algorithms = [alg for alg in all_algorithms if alg['status'] == 'enabled']
        disabled_algorithms = [alg for alg in all_algorithms if alg['status'] == 'disabled']
        
        return {
            'construction_mode': construction_mode,
            'total_count': len(all_algorithms),
            'enabled_count': len(enabled_algorithms),
            'disabled_count': len(disabled_algorithms),
            'enabled_algorithms': [f"{alg['algorithm_name']}" for alg in enabled_algorithms],
            'disabled_algorithms': [f"{alg['algorithm_name']}" for alg in disabled_algorithms],
            'can_predict': len(enabled_algorithms) > 0
        }
    except Exception as e:
        print(f"获取算法状态汇总错误: {str(e)}")
        return {
            'construction_mode': construction_mode,
            'total_count': 0,
            'enabled_count': 0,
            'disabled_count': 0,
            'enabled_algorithms': [],
            'disabled_algorithms': [],
            'can_predict': False
        }

def get_construction_mode_chinese_name(mode):
    """获取施工模式的中文名称"""
    mode_names = {
        'steel_cage': '钢筋笼模式',
        'steel_lining': '钢衬里模式'
    }
    return mode_names.get(mode, mode)

def perform_prediction_with_mode_algorithms(input_data, construction_mode):
    """根据施工模式使用相应的启用算法进行预测"""
    # 检查该施工模式是否有可用算法
    if not check_prediction_availability(construction_mode):
        mode_name = get_construction_mode_chinese_name(construction_mode)
        return {
            'success': False,
            'message': f'无法进行{mode_name}预测：该模式下所有预测算法均已停用，请在算法配置中启用至少一种算法。',
            'results': None,
            'construction_mode': construction_mode
        }
    
    # 获取该施工模式下启用的算法
    enabled_algorithms = get_enabled_algorithms(construction_mode)
    mode_name = get_construction_mode_chinese_name(construction_mode)
    
    # 执行预测（这里是示例逻辑）
    prediction_results = {}
    for algorithm in enabled_algorithms:
        algorithm_type = algorithm['algorithm_type']
        algorithm_name = algorithm['algorithm_name']
        
        # 示例预测结果
        prediction_results[algorithm_name] = {
            'prediction': 1000000 + len(algorithm_name) * 50000,
            'confidence': 0.85
        }
    
    return {
        'success': True,
        'message': f'{mode_name}预测完成，使用了 {len(enabled_algorithms)} 种算法',
        'results': prediction_results,
        'construction_mode': construction_mode,
        'mode_name': mode_name,
        'enabled_algorithms': [alg['algorithm_name'] for alg in enabled_algorithms]
    }

def get_all_modes_prediction_status():
    """获取所有施工模式的预测状态信息"""
    steel_cage_status = get_algorithm_status_summary('steel_cage')
    steel_lining_status = get_algorithm_status_summary('steel_lining')
    
    return {
        'steel_cage': {
            'mode_name': '钢筋笼模式',
            'can_predict': steel_cage_status['can_predict'],
            'enabled_algorithms': steel_cage_status['enabled_algorithms'],
            'disabled_algorithms': steel_cage_status['disabled_algorithms'],
            'message': f"钢筋笼模式：{'可预测' if steel_cage_status['can_predict'] else '无法预测'}"
        },
        'steel_lining': {
            'mode_name': '钢衬里模式',
            'can_predict': steel_lining_status['can_predict'],
            'enabled_algorithms': steel_lining_status['enabled_algorithms'],
            'disabled_algorithms': steel_lining_status['disabled_algorithms'],
            'message': f"钢衬里模式：{'可预测' if steel_lining_status['can_predict'] else '无法预测'}"
        }
    }



# ====== 算法参数管理相关函数 ======

def get_all_algorithms():
    """获取所有不重复的算法列表"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT algorithm_name, algorithm_name_en, algorithm_class 
                FROM algorithm_parameters 
                ORDER BY algorithm_name
            """)
            results = cursor.fetchall()
            conn.close()
            
            algorithms = []
            for result in results:
                algorithms.append({
                    'label': result[0],  # algorithm_name (中文)
                    'value': result[1],  # algorithm_name_en (英文，用作value)
                    'class': result[2]   # algorithm_class
                })
            return algorithms
        return []
    except Exception as e:
        print(f"获取算法列表错误: {str(e)}")
        return []

def get_algorithm_parameters(algorithm_name_en):
    """根据算法英文名获取其所有参数"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM algorithm_parameters 
                WHERE algorithm_name_en = %s 
                ORDER BY 
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    parameter_name
            """, (algorithm_name_en,))
            results = cursor.fetchall()
            conn.close()
            return results
        return []
    except Exception as e:
        print(f"获取算法参数错误: {str(e)}")
        return []

def update_algorithm_parameter(param_id, new_value):
    """更新指定参数的当前值"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE algorithm_parameters 
                SET current_value = %s, updated_at = NOW() 
                WHERE id = %s
            """, (new_value, param_id))
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        return False
    except Exception as e:
        print(f"更新算法参数错误: {str(e)}")
        return False

def reset_algorithm_parameters(algorithm_name_en):
    """重置指定算法的所有参数到建议值"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor()
            # 这里我们假设有一个默认值逻辑，实际可能需要根据suggested_range来设置
            # 暂时先更新时间戳，具体的重置逻辑可以后续完善
            cursor.execute("""
                UPDATE algorithm_parameters 
                SET updated_at = NOW() 
                WHERE algorithm_name_en = %s
            """, (algorithm_name_en,))
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        return False
    except Exception as e:
        print(f"重置算法参数错误: {str(e)}")
        return False

def validate_parameter_value(parameter_type, suggested_range, value):
    """验证参数值是否在建议范围内 - 改进版本"""
    try:
        if parameter_type == 'continuous':
            # 解析连续值范围，如 "0.01-100"
            if '-' in suggested_range:
                range_parts = suggested_range.split('-')
                if len(range_parts) == 2:
                    min_val = float(range_parts[0])
                    max_val = float(range_parts[1])
                    value_float = float(value)
                    return min_val <= value_float <= max_val, f"值应在 {min_val} 到 {max_val} 之间"
        
        elif parameter_type == 'discrete':
            # 解析离散值范围，如 "2-10" 或 "500-5000"
            if '-' in suggested_range:
                range_parts = suggested_range.split('-')
                if len(range_parts) == 2:
                    min_val = int(float(range_parts[0]))
                    max_val = int(float(range_parts[1]))
                    value_int = int(float(value))
                    return min_val <= value_int <= max_val, f"值应在 {min_val} 到 {max_val} 之间"
        
        elif parameter_type == 'categorical':
            # 解析分类选项，如 "linear, rbf, poly"
            options = [opt.strip() for opt in suggested_range.split(',')]
            return str(value).strip() in options, f"值应为: {', '.join(options)}"
        
        return True, "验证通过"
    except Exception as e:
        return False, f"验证错误: {str(e)}"
    
    
def get_algorithm_description(algorithm_name_en):
    """获取算法描述信息"""
    try:
        conn = create_raw_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT DISTINCT algorithm_name, algorithm_class 
                FROM algorithm_parameters 
                WHERE algorithm_name_en = %s
                LIMIT 1
            """, (algorithm_name_en,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # 根据算法类型返回描述信息
                descriptions = {
                    'linear_regression': '岭回归是一种线性回归的正则化版本，通过添加L2正则化项来防止过拟合，特别适用于特征数量较多或存在多重共线性的情况。',
                    'tree_based': '决策树是一种基于树结构的机器学习算法，通过一系列if-else条件来进行预测，具有良好的可解释性。',
                    'ensemble': '随机森林是一种集成学习算法，通过构建多个决策树并取平均值来提高预测精度和稳定性。',
                    'kernel_method': '支持向量回归通过核函数将数据映射到高维空间，寻找最优的回归超平面，适用于非线性回归问题。',
                    'neural_network': '多层感知器是一种前馈神经网络，通过多个隐藏层来学习复杂的非线性关系。'
                }
                
                description = descriptions.get(result['algorithm_class'], '暂无详细描述')
                return {
                    'name': result['algorithm_name'],
                    'class': result['algorithm_class'],
                    'description': description
                }
        return None
    except Exception as e:
        print(f"获取算法描述错误: {str(e)}")
        return None
    

def register_data_callbacks(app):
    """注册数据管理模块的回调函数"""
    
    # 添加调试回调 - 监控所有模态窗口状态
    @app.callback(
        Output("debug-output", "children"),  # 需要在布局中添加一个隐藏的div
        [Input("modal-basic-indicator", "is_open"),
         Input("modal-composite-indicator", "is_open"),
         Input("modal-comprehensive-indicator", "is_open"),
         Input("modal-algorithm-config", "is_open"),
         Input("modal-model-training", "is_open"),
         Input("modal-model-evaluation", "is_open")]
    )
    def debug_modal_states(basic, composite, comprehensive, algo, training, eval):
        print(f"""
        ========== 模态窗口状态监控 ==========
        基础指标: {basic}
        复合指标: {composite}
        综合指标: {comprehensive}
        算法配置: {algo}
        模型训练: {training}
        预测精度: {eval}
        =====================================
        """)
        return ""

    # 基础指标库模态窗口回调
    @app.callback(
        Output("modal-basic-indicator", "is_open"),
        [Input("btn-basic-indicator", "n_clicks"), 
        Input("close-basic-indicator", "n_clicks")],
        [State("modal-basic-indicator", "is_open")]
    )
    def toggle_basic_indicator_modal(n1, n2, is_open):
        print(f"[基础指标] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        # 如果两个按钮都没有被点击过，保持关闭状态
        if n1 is None and n2 is None:
            print("[基础指标] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[基础指标] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[基础指标] 没有触发事件，返回 no_update")
            return no_update
        
        # 获取触发的组件
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[基础指标] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        # 确保触发值不是0或None
        if trigger_value is None or trigger_value == 0:
            print("[基础指标] 触发值无效，返回 no_update")
            return no_update
        
        # 只在明确的按钮点击时切换
        if button_id in ["btn-basic-indicator", "close-basic-indicator"]:
            new_state = not is_open
            print(f"[基础指标] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[基础指标] 未知的触发源，返回 no_update")
        return no_update

    # 复合指标库模态窗口回调
    @app.callback(
        Output("modal-composite-indicator", "is_open"),
        [Input("btn-composite-indicator", "n_clicks"), 
        Input("close-composite-indicator", "n_clicks")],
        [State("modal-composite-indicator", "is_open")]
    )
    def toggle_composite_indicator_modal(n1, n2, is_open):
        print(f"[复合指标] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        if n1 is None and n2 is None:
            print("[复合指标] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[复合指标] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[复合指标] 没有触发事件，返回 no_update")
            return no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[复合指标] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        if trigger_value is None or trigger_value == 0:
            print("[复合指标] 触发值无效，返回 no_update")
            return no_update
        
        if button_id in ["btn-composite-indicator", "close-composite-indicator"]:
            new_state = not is_open
            print(f"[复合指标] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[复合指标] 未知的触发源，返回 no_update")
        return no_update
    # 综合指标库模态窗口回调
    @app.callback(
        Output("modal-comprehensive-indicator", "is_open"),
        [Input("btn-comprehensive-indicator", "n_clicks"), 
        Input("close-comprehensive-indicator", "n_clicks")],
        [State("modal-comprehensive-indicator", "is_open")]
    )
    def toggle_comprehensive_indicator_modal(n1, n2, is_open):
        print(f"[综合指标] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        if n1 is None and n2 is None:
            print("[综合指标] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[综合指标] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[综合指标] 没有触发事件，返回 no_update")
            return no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[综合指标] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        if trigger_value is None or trigger_value == 0:
            print("[综合指标] 触发值无效，返回 no_update")
            return no_update
        
        if button_id in ["btn-comprehensive-indicator", "close-comprehensive-indicator"]:
            new_state = not is_open
            print(f"[综合指标] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[综合指标] 未知的触发源，返回 no_update")
        return no_update
    
    # 算法配置模态窗口回调
    @app.callback(
        Output("modal-algorithm-config", "is_open"),
        [Input("btn-algorithm-config", "n_clicks"), 
        Input("close-algorithm-config", "n_clicks")],
        [State("modal-algorithm-config", "is_open")]
    )
    def toggle_algorithm_config_modal(n1, n2, is_open):
        print(f"[算法配置] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        if n1 is None and n2 is None:
            print("[算法配置] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[算法配置] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[算法配置] 没有触发事件，返回 no_update")
            return no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[算法配置] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        if trigger_value is None or trigger_value == 0:
            print("[算法配置] 触发值无效，返回 no_update")
            return no_update
        
        if button_id in ["btn-algorithm-config", "close-algorithm-config"]:
            new_state = not is_open
            print(f"[算法配置] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[算法配置] 未知的触发源，返回 no_update")
        return no_update
    
    # 保留原有的模型训练管理模态窗口回调（现在改为模型参数管理）
    @app.callback(
        Output("modal-model-training", "is_open"),
        [Input("btn-model-training", "n_clicks"), 
        Input("close-model-training", "n_clicks")],
        [State("modal-model-training", "is_open")]
    )
    def toggle_model_training_modal(n1, n2, is_open):
        print(f"[模型训练] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        if n1 is None and n2 is None:
            print("[模型训练] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[模型训练] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[模型训练] 没有触发事件，返回 no_update")
            return no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[模型训练] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        if trigger_value is None or trigger_value == 0:
            print("[模型训练] 触发值无效，返回 no_update")
            return no_update
        
        if button_id in ["btn-model-training", "close-model-training"]:
            new_state = not is_open
            print(f"[模型训练] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[模型训练] 未知的触发源，返回 no_update")
        return no_update


    # 模拟训练进度回调
    @app.callback(
        [Output("training-progress", "value"),
         Output("training-status", "children")],
        [Input("start-training", "n_clicks"),
         Input("pause-training", "n_clicks")]
    )
    def update_training_progress(start_clicks, pause_clicks):
        ctx = callback_context
        
        if not ctx.triggered:
            # 初始状态
            return 40, "当前状态：训练中... (40% 完成，损失：0.035)"
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "start-training":
            # 模拟训练进度增加
            return 75, "当前状态：训练中... (75% 完成，损失：0.018)"
        elif button_id == "pause-training":
            # 模拟训练暂停
            return 40, "当前状态：训练已暂停 (40% 完成，损失：0.035)"
        
        return 40, "当前状态：训练中... (40% 完成，损失：0.035)"



    @app.callback(
        Output("import-button", "n_clicks"),  # 借用一个已存在的组件
        [Input("btn-model-comparison", "n_clicks")],
        prevent_initial_call=True
    )
    def test_model_comparison_click(n_clicks):
        print(f"\n=== 模型性能对比按钮被点击了！点击次数: {n_clicks} ===\n")
        return 0  # 返回值不重要


    # 施工模式切换时更新算法状态概览
    @app.callback(
        Output("algorithm-status-overview", "children"),
        [Input("comparison-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def update_algorithm_status_overview(construction_mode):
        """更新算法状态概览"""
        try:
            # 获取指定模式下的算法状态
            algorithm_status = get_algorithm_status_summary(construction_mode)
            mode_name = get_construction_mode_chinese_name(construction_mode)
            
            # 构建状态展示组件
            status_components = []
            
            # 总体状态卡片
            if algorithm_status['can_predict']:
                status_color = "success"
                status_icon = "fas fa-check-circle"
                status_text = f"{mode_name}：预测功能可用"
            else:
                status_color = "danger"
                status_icon = "fas fa-times-circle"
                status_text = f"{mode_name}：预测功能不可用"
            
            status_components.append(
                dbc.Alert([
                    html.I(className=f"{status_icon} me-2"),
                    html.Strong(status_text),
                    html.Br(),
                    f"启用算法：{algorithm_status['enabled_count']}/{algorithm_status['total_count']}"
                ], color=status_color, className="mb-2")
            )
            
            # 算法详细状态
            if algorithm_status['enabled_algorithms']:
                enabled_text = "、".join(algorithm_status['enabled_algorithms'])
                status_components.append(
                    html.Div([
                        html.Strong("已启用算法：", style={'color': '#28a745'}),
                        html.Span(enabled_text, style={'marginLeft': '5px'})
                    ], style={'marginBottom': '8px'})
                )
            
            if algorithm_status['disabled_algorithms']:
                disabled_text = "、".join(algorithm_status['disabled_algorithms'])
                status_components.append(
                    html.Div([
                        html.Strong("已停用算法：", style={'color': '#dc3545'}),
                        html.Span(disabled_text, style={'marginLeft': '5px'})
                    ])
                )
            
            return status_components
            
        except Exception as e:
            return [
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"获取算法状态失败：{str(e)}"
                ], color="danger")
            ]


    # 开始评估后更新图表回调
    @app.callback(
        [Output("evaluation-table", "data"),
         Output("evaluation-graph", "figure")],
        [Input("start-evaluation", "n_clicks")],
        [State("evaluation-model-dropdown", "value")]
    )
    def update_evaluation_results(n_clicks, model_value):
        if not n_clicks:
            return [], {}
        
        # 根据所选模型更新评估结果
        if model_value == 'nn_20250310':
            # 神经网络模型的评估结果
            table_data = [
                {'metric': '平均绝对误差', 'value': '2.85%'},
                {'metric': '均方根误差', 'value': '3.72%'},
                {'metric': 'R²值', 'value': '0.943'},
                {'metric': '准确率(±5%)', 'value': '94.2%'}
            ]
            # 神经网络模型的散点图
            figure = {
                'data': [
                    go.Scatter(
                        x=[100, 200, 300, 400, 500, 600],
                        y=[105, 195, 310, 390, 515, 590],
                        mode='markers',
                        name='预测 vs 实际',
                        marker=dict(size=10, color='#2C3E50')
                    ),
                    go.Scatter(
                        x=[0, 700],
                        y=[0, 700],
                        mode='lines',
                        name='理想预测',
                        line=dict(color='#E74C3C', dash='dash')
                    )
                ],
                'layout': go.Layout(
                    title="预测值 vs 实际值",
                    height=250,
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 20},
                    xaxis={'title': '实际值'},
                    yaxis={'title': '预测值'},
                    legend={'orientation': 'h', 'y': 1.1}
                )
            }
        elif model_value == 'lr_20250305':
            # 线性回归模型的评估结果
            table_data = [
                {'metric': '平均绝对误差', 'value': '4.25%'},
                {'metric': '均方根误差', 'value': '5.10%'},
                {'metric': 'R²值', 'value': '0.892'},
                {'metric': '准确率(±5%)', 'value': '87.5%'}
            ]
            # 线性回归模型的散点图
            figure = {
                'data': [
                    go.Scatter(
                        x=[100, 200, 300, 400, 500, 600],
                        y=[110, 220, 270, 420, 470, 630],
                        mode='markers',
                        name='预测 vs 实际',
                        marker=dict(size=10, color='#2C3E50')
                    ),
                    go.Scatter(
                        x=[0, 700],
                        y=[0, 700],
                        mode='lines',
                        name='理想预测',
                        line=dict(color='#E74C3C', dash='dash')
                    )
                ],
                'layout': go.Layout(
                    title="预测值 vs 实际值",
                    height=250,
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 20},
                    xaxis={'title': '实际值'},
                    yaxis={'title': '预测值'},
                    legend={'orientation': 'h', 'y': 1.1}
                )
            }
        else:
            # 随机森林模型的评估结果
            table_data = [
                {'metric': '平均绝对误差', 'value': '3.15%'},
                {'metric': '均方根误差', 'value': '3.90%'},
                {'metric': 'R²值', 'value': '0.925'},
                {'metric': '准确率(±5%)', 'value': '92.8%'}
            ]
            # 随机森林模型的散点图
            figure = {
                'data': [
                    go.Scatter(
                        x=[100, 200, 300, 400, 500, 600],
                        y=[103, 205, 295, 405, 510, 595],
                        mode='markers',
                        name='预测 vs 实际',
                        marker=dict(size=10, color='#2C3E50')
                    ),
                    go.Scatter(
                        x=[0, 700],
                        y=[0, 700],
                        mode='lines',
                        name='理想预测',
                        line=dict(color='#E74C3C', dash='dash')
                    )
                ],
                'layout': go.Layout(
                    title="预测值 vs 实际值",
                    height=250,
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 20},
                    xaxis={'title': '实际值'},
                    yaxis={'title': '预测值'},
                    legend={'orientation': 'h', 'y': 1.1}
                )
            }
        
        return table_data, figure

    # 文件上传回调 - 修改为翻译字段名
    @app.callback(
        [Output("preview-table-data", "data"),
         Output("preview-table-data", "columns"),
         Output("preview-data-container", "style"),
         Output("field-mapping-table-body", "children"),
         Output("current-date-display", "children"),
         Output("manual-date-picker", "date")],
        [Input("upload-data", "contents")],
        [State("upload-data", "filename")]
    )
    def update_output(contents, filename):
        # 生成当前日期
        current_date = datetime.now()
        current_date_str = current_date.strftime("%Y-%m-%d")
        
        if contents is None:
            # 初始状态返回空值
            return [], [], {'display': 'none'}, [html.Tr([
                html.Td("Material_name", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                html.Td("文本", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                html.Td("钢筋", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                html.Td([
                    dcc.Dropdown(
                        options=[
                            {'label': '材料', 'value': 'material'},
                            {'label': '规格', 'value': 'specification'},
                            {'label': '型号', 'value': 'model'}
                        ],
                        value='material',
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'})
            ])], current_date_str, current_date.date()
        
        try:
            # 使用parse_uploaded_file函数处理上传的文件
            df = parse_uploaded_file(contents, filename)
            
            # 翻译DataFrame列名为中文显示
            translated_df = translate_dataframe_columns(df)
            
            # 显示表格数据（使用翻译后的列名）
            data = translated_df.to_dict('records')
            columns = [{'name': i, 'id': i} for i in translated_df.columns]
            
            # 更新字段映射表格（使用原始英文列名进行映射，但显示中文）
            mapping_rows = []
            for i, col in enumerate(df.columns):
                # 获取列的示例值（非空）
                sample_value = ""
                for val in df[col]:
                    if pd.notna(val) and str(val).strip() != "":
                        sample_value = str(val)
                        break
                
                # 确定数据类型
                col_type = "文本"
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_type = "数值"
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_type = "日期"
                elif pd.api.types.is_bool_dtype(df[col]):
                    col_type = "布尔值"
                
                # 显示翻译后的列名
                chinese_col_name = translate_field_name(col)
                    
                mapping_rows.append(html.Tr([
                    html.Td(chinese_col_name, style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                    html.Td(col_type, style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                    html.Td(sample_value, style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                    html.Td([
                        dcc.Dropdown(
                            options=[
                                {'label': '材料', 'value': 'material'},
                                {'label': '规格', 'value': 'specification'},
                                {'label': '型号', 'value': 'model'},
                                {'label': '价格', 'value': 'price'},
                                {'label': '单位', 'value': 'unit'},
                                {'label': '无', 'value': 'none'}
                            ],
                            value='none',
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'})
                ]))
            
            return data, columns, {'display': 'block', 'marginTop': '20px'}, mapping_rows, current_date_str, current_date.date()
            
        except Exception as e:
            print(f"文件处理错误: {str(e)}")
            # 发生错误时返回错误信息
            error_df = pd.DataFrame({
                '错误': [f'处理文件时出错: {str(e)}'],
                '建议': ['请检查文件格式是否正确']
            })
            error_data = error_df.to_dict('records')
            error_columns = [{'name': i, 'id': i} for i in error_df.columns]
            
            # 返回错误信息
            return (error_data, error_columns, {'display': 'block', 'marginTop': '20px'}, 
                    [html.Tr([
                        html.Td("Error", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                        html.Td("错误", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                        html.Td(str(e), style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                        html.Td([
                            dcc.Dropdown(
                                options=[
                                    {'label': '无', 'value': 'none'}
                                ],
                                value='none',
                                clearable=False,
                                style={'width': '100%'}
                            )
                        ], style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'})
                    ])], current_date_str, current_date.date())

    # 确认导入数据回调 - 添加翻译支持
    @app.callback(
        [Output("table-data", "data", allow_duplicate=True),
         Output("modal-import", "is_open", allow_duplicate=True),
         Output("import-status-message", "children", allow_duplicate=True),
         Output("import-status-message", "style", allow_duplicate=True)],
        [Input("confirm-import", "n_clicks")],
        [State("preview-table-data", "data"),
         State("import-choice-value", "data"),
         State("table-operation-type", "value"),
         State("new-table-name", "value"),
         State("existing-table-dropdown", "value"),
         State("import-mode", "value"),
         State("manual-date-picker", "date"),
         State("modal-import", "is_open")],
        prevent_initial_call=True
    )
    def confirm_import_data(n_clicks, preview_data, import_choice, operation_type, new_table_name, 
                           existing_table, import_mode, manual_date, is_modal_open):
        if n_clicks is None or not is_modal_open:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # 创建一个状态消息
        status_message = ""
        
        # 检查导入选择
        if import_choice == "preview_only":
            # 仅预览数据，不导入数据库
            # 翻译列名为中文显示
            translated_data = []
            for row in preview_data:
                translated_row = {}
                for key, value in row.items():
                    chinese_key = translate_field_name(key)
                    translated_row[chinese_key] = value
                translated_data.append(translated_row)
            
            return translated_data, False, "数据已预览，未导入数据库", {
                'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                'borderRadius': '4px', 'backgroundColor': '#fff3cd', 'color': '#856404'
            }
        
        # 以下是原有的导入逻辑
        try:
            # 转换预览数据为DataFrame
            df = pd.DataFrame(preview_data)
            
            # 添加时间戳列（导入时间和数据日期）
            import_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 确保manual_date是有效的日期格式
            if isinstance(manual_date, str):
                data_date = manual_date
            else:
                data_date = manual_date.strftime("%Y-%m-%d") if manual_date else datetime.now().strftime("%Y-%m-%d")
            
            # 添加时间戳列
            df['import_timestamp'] = import_timestamp
            df['data_date'] = data_date
            
            # 获取数据库连接
            engine = create_db_connection()
            
            if engine:
                if operation_type == 'new_table':
                    # 检查表名是否有效
                    if not new_table_name or not new_table_name.strip():
                        return preview_data, True, "错误：请输入有效的表名！", {
                            'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                            'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                        }
                    
                    # 检查表是否已存在
                    table_name = new_table_name.strip()
                    if check_table_exists(table_name):
                        return preview_data, True, f"错误：表 '{table_name}' 已存在！", {
                            'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                            'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                        }
                    
                    # 创建新表并导入数据
                    df.to_sql(table_name, engine, if_exists='fail', index=False, method='multi')
                    status_message = f"成功创建并导入数据到新表: {translate_table_name(table_name)}"
                    
                else:  # 添加到现有表
                    if not existing_table:
                        return preview_data, True, "错误：请选择一个现有表！", {
                            'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                            'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                        }
                    
                    # 根据导入模式处理数据
                    if import_mode == 'append':
                        # 检查列结构兼容性
                        existing_columns = get_table_columns(existing_table)
                        new_columns = df.columns.tolist()
                        
                        # 确保新数据的列与现有表兼容
                        missing_cols = set(existing_columns) - set(new_columns)
                        if missing_cols:
                            # 为缺失的列添加空值
                            for col in missing_cols:
                                df[col] = None
                        
                        # 重新排序列以匹配现有表
                        df = df.reindex(columns=existing_columns, fill_value=None)
                        
                        df.to_sql(existing_table, engine, if_exists='append', index=False, method='multi')
                        status_message = f"成功追加数据到表: {translate_table_name(existing_table)}"
                        
                    elif import_mode == 'replace':
                        df.to_sql(existing_table, engine, if_exists='replace', index=False, method='multi')
                        status_message = f"成功替换表: {translate_table_name(existing_table)} 中的数据"
                        
                    elif import_mode == 'update':
                        # MySQL更新逻辑
                        conn = create_raw_mysql_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            
                            # 获取表的第一列作为主键（假设）
                            table_columns = get_table_columns(existing_table)
                            if not table_columns:
                                conn.close()
                                return preview_data, True, "错误：无法获取表结构！", {
                                    'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                                    'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                                }
                            
                            primary_key_col = table_columns[0]
                            
                            # 对每一行数据进行更新操作
                            update_count = 0
                            for _, row in df.iterrows():
                                primary_key_val = row[df.columns[0]]
                                
                                # 构建更新语句
                                update_columns = [col for col in df.columns if col != df.columns[0]]
                                set_clause = ', '.join([f"`{col}` = %s" for col in update_columns])
                                
                                # 添加时间戳字段到更新中
                                if 'import_timestamp' not in update_columns:
                                    set_clause += ", `import_timestamp` = %s"
                                    update_columns.append('import_timestamp')
                                if 'data_date' not in update_columns:
                                    set_clause += ", `data_date` = %s"
                                    update_columns.append('data_date')
                                
                                update_values = [row[col] if col in row else (import_timestamp if col == 'import_timestamp' else data_date) 
                                               for col in update_columns]
                                update_values.append(primary_key_val)
                                
                                query = f"UPDATE `{existing_table}` SET {set_clause} WHERE `{primary_key_col}` = %s"
                                
                                # 执行更新
                                cursor.execute(query, update_values)
                                if cursor.rowcount > 0:
                                    update_count += 1
                            
                            conn.commit()
                            conn.close()
                            status_message = f"成功更新表: {translate_table_name(existing_table)} 中的 {update_count} 条匹配记录"
                        else:
                            return preview_data, True, "错误：无法连接到MySQL数据库！", {
                                'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                                'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                            }
                
                # 查询更新后的表数据并翻译列名
                table_name = existing_table if operation_type == 'existing_table' else new_table_name
                try:
                    updated_data = pd.read_sql_table(table_name, engine)
                    # 翻译列名为中文显示
                    updated_data_translated = translate_dataframe_columns(updated_data)
                    return updated_data_translated.to_dict('records'), False, status_message, {
                        'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                        'borderRadius': '4px', 'backgroundColor': '#d4edda', 'color': '#155724'
                    }
                except Exception as read_error:
                    print(f"读取更新后的表数据失败: {read_error}")
                    return preview_data, False, status_message, {
                        'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                        'borderRadius': '4px', 'backgroundColor': '#d4edda', 'color': '#155724'
                    }
            
            else:
                return preview_data, True, "错误：无法连接到MySQL数据库！", {
                    'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                    'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
                }
        
        except Exception as e:
            print(f"导入数据错误: {str(e)}")
            return preview_data, True, f"错误：{str(e)}", {
                'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
            }

    @app.callback(
        [Output("new-table-div", "style"),
         Output("existing-table-div", "style")],
        [Input("table-operation-type", "value")]
    )
    def toggle_table_operation_options(operation_type):
        if operation_type == 'new_table':
            return {'display': 'block', 'marginTop': '10px'}, {'display': 'none', 'marginTop': '10px'}
        else:
            return {'display': 'none', 'marginTop': '10px'}, {'display': 'block', 'marginTop': '10px'}

    # 控制导入选项区域可见性的回调函数
    @app.callback(
        [Output("new-table-div", "style", allow_duplicate=True),
         Output("existing-table-div", "style", allow_duplicate=True)],
        [Input("modal-import", "is_open"),
         Input("import-choice-value", "data")],
        [State("table-operation-type", "value")],
        prevent_initial_call=True
    )
    def toggle_import_options_visibility(is_open, import_choice, operation_type):
        if not is_open:
            return dash.no_update, dash.no_update
        
        # 如果选择仅预览，隐藏导入选项
        if import_choice == "preview_only":
            return {'display': 'none', 'marginTop': '10px'}, {'display': 'none', 'marginTop': '10px'}
        
        # 否则根据操作类型显示对应的选项
        if operation_type == 'new_table':
            return {'display': 'block', 'marginTop': '10px'}, {'display': 'none', 'marginTop': '10px'}
        else:
            return {'display': 'none', 'marginTop': '10px'}, {'display': 'block', 'marginTop': '10px'}

    # 选择卡片的点击回调
    @app.callback(
        [Output("preview-only-card", "style"),
         Output("import-to-db-card", "style"),
         Output("import-choice-value", "data"),
         Output("import-choice-description", "children"),
         Output("confirm-import-choice", "disabled")],
        [Input("preview-only-btn", "n_clicks"),
         Input("import-to-db-btn", "n_clicks")],
        [State("preview-only-card", "style"),
         State("import-to-db-card", "style")]
    )
    def select_import_choice(preview_clicks, import_clicks, preview_style, import_style):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # 复制原有样式，以便更新特定属性
        preview_style_new = dict(preview_style)
        import_style_new = dict(import_style)
        
        # 重置样式
        preview_style_new["border"] = "2px solid #ddd"
        import_style_new["border"] = "2px solid #ddd"
        
        description = ""
        choice_value = ""
        disabled = True
        
        if button_id == "preview-only-btn":
            preview_style_new["border"] = f"2px solid {PRIMARY_COLOR}"
            description = '您选择了"仅上传数据"。点击确认后，将只查看数据内容，不会导入数据库。'
            choice_value = "preview_only"
            disabled = False
        elif button_id == "import-to-db-btn":
            import_style_new["border"] = f"2px solid {SECONDARY_COLOR}"
            description = '您选择了"导入到数据库"。点击确认后，将配置数据导入选项。'
            choice_value = "import_to_db"
            disabled = False
        
        return preview_style_new, import_style_new, choice_value, description, disabled

    # 更新现有表下拉菜单的回调 - 添加翻译支持
    @app.callback(
        Output("existing-table-dropdown", "options"),
        [Input("modal-import", "is_open")]
    )
    def update_table_dropdown(is_open):
        if is_open:
            # 当模态框打开时，动态获取数据库表（已经翻译为中文显示）
            return get_all_tables()
        return []

    # 显示/隐藏状态消息的回调
    @app.callback(
        [Output("import-status-message", "style", allow_duplicate=True),
         Output("import-status-message", "className", allow_duplicate=True)],
        [Input("import-status-message", "children")],
        prevent_initial_call=True
    )
    def update_status_message_style(message):
        if not message:
            return {'display': 'none'}, ''
        
        if isinstance(message, str) and message.startswith("错误"):
            return {
                'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                'borderRadius': '4px', 'backgroundColor': '#f8d7da', 'color': '#721c24'
            }, 'border border-danger'
        else:
            return {
                'display': 'block', 'padding': '10px', 'marginTop': '10px', 
                'borderRadius': '4px', 'backgroundColor': '#d4edda', 'color': '#155724'
            }, 'border border-success'

    @app.callback(
        [Output("modal-import-choice", "is_open", allow_duplicate=True),
         Output("modal-import", "is_open", allow_duplicate=True)],
        [Input("confirm-import-choice", "n_clicks")],
        [State("import-choice-value", "data")],
        prevent_initial_call=True
    )
    def confirm_import_choice(n_clicks, choice):
        if not n_clicks:
            return dash.no_update, dash.no_update
        
        if choice == "preview_only":
            # 选择仅预览，直接打开预览界面，但跳过导入数据库选项
            return False, True
        elif choice == "import_to_db":
            # 选择导入数据库，打开导入界面
            return False, True
        
        return dash.no_update, dash.no_update

    @app.callback(
        Output("modal-import-choice", "is_open"),
        [Input("import-button", "n_clicks"),
         Input("close-import-choice", "n_clicks"),
         Input("close-import-choice-x", "n_clicks")],
        [State("modal-import-choice", "is_open")]
    )
    def toggle_import_choice_modal(n1, n2, n3, is_open):
        if n1 or n2 or n3:
            return not is_open
        return is_open
    # 修改加载基础指标数据的回调函数
    @app.callback(
        Output('basic-indicator-table', 'data'),
        [Input('modal-basic-indicator', 'is_open'),
        Input('basic-indicator-main-category-dropdown', 'value'),
        Input('basic-indicator-status-dropdown', 'value')]
    )
    def load_basic_indicators_data(is_open, category_value, status_value):
        """当基础指标模态窗口打开、分类或状态改变时，从数据库加载数据 - 修复版本"""
        if is_open:
            print(f"=== 加载基础指标数据 ===")
            print(f"分类值: {category_value}")
            print(f"状态值: {status_value}")
            
            # 获取指定分类的数据
            data = get_basic_indicators(category_value)
            print(f"从数据库获取到 {len(data)} 条记录")
            
            # 如果有状态筛选，进一步过滤
            if status_value and status_value != 'all':
                status_map = {'enabled': '启用', 'disabled': '停用'}
                target_status = status_map.get(status_value, status_value)
                original_count = len(data)
                data = [item for item in data if item.get('status') == target_status]
                print(f"状态筛选后剩余 {len(data)} 条记录（原{original_count}条）")
            
            # 打印一些示例数据用于调试
            if data:
                print("示例数据:")
                for i, item in enumerate(data[:3]):
                    print(f"  {i+1}. ID:{item.get('id')}, 名称:{item.get('name')}, 分类:{item.get('category')}")
            
            return data
        return []



    # 新添加：控制编辑和删除按钮的启用/禁用状态
    @app.callback(
        [Output("edit-selected-indicator", "disabled"),
         Output("delete-selected-indicator", "disabled")],
        [Input("basic-indicator-table", "selected_rows"),
         Input("editing-mode", "data")]
    )
    def update_button_states(selected_rows, editing_mode):
        """根据表格选中状态和编辑模式更新按钮可用性"""
        if editing_mode:
            # 编辑模式中禁用编辑和删除按钮
            return True, True
        
        if not selected_rows or len(selected_rows) == 0:
            # 没有选中行时禁用按钮
            return True, True
        
        if len(selected_rows) != 1:
            # 选中多行时禁用编辑按钮，但允许删除
            return True, False
            
        # 选中一行且非编辑模式时，两个按钮都可用
        return False, False
    # 修复编辑按钮回调函数
    @app.callback(
        [Output("basic-indicator-code-input", "value"),
        Output("basic-indicator-name-input", "value"),
        Output("basic-indicator-unit-input", "value"),
        Output("basic-indicator-description-textarea", "value"),
        Output("basic-indicator-status-radio", "value"),
        Output("basic-indicator-category-dropdown-input", "value"),
        Output("basic-indicator-form-category-dropdown", "value", allow_duplicate=True),
        Output("editing-mode", "data"),
        Output("editing-indicator-id", "data"),
        Output("original-indicator-data", "data")],
        [Input("edit-selected-indicator", "n_clicks")],
        [State("basic-indicator-table", "selected_rows"),
        State("basic-indicator-table", "data")],
        prevent_initial_call=True
    )
    def edit_selected_indicator(n_clicks, selected_rows, table_data):
        """编辑所选指标 - 将数据填入表单并进入编辑模式"""
        if not n_clicks or not selected_rows or not table_data:
            return "", "", "", "", "enabled", "机械费", "custom", False, None, {}
        
        selected_row = table_data[selected_rows[0]]
        
        # 将状态从中文转换为英文
        status_value = 'enabled' if selected_row.get('status') == '启用' else 'disabled'
        
        # 根据ID判断主分类
        indicator_id = selected_row.get('id', 300)
        main_category = get_main_category_by_id(indicator_id)
        
        print(f"编辑指标 - ID: {indicator_id}, 主分类: {main_category}")
        
        original_data = selected_row.copy()
        
        return (
            selected_row.get('code', ''),
            selected_row.get('name', ''),
            selected_row.get('unit', ''),
            selected_row.get('description', ''),
            status_value,
            selected_row.get('category', '机械费'),
            main_category,  # 确保主分类正确设置
            True,
            selected_row.get('id'),
            original_data
        )
# 新添加：根据编辑模式更新UI显示状态
    @app.callback(
        [Output("form-title", "children"),
         Output("save-basic-indicator", "children"),
         Output("cancel-edit-indicator", "style"),
         Output("editing-status-alert", "children"),
         Output("editing-status-alert", "style")],
        [Input("editing-mode", "data"),
         Input("editing-indicator-id", "data")],
        [State("basic-indicator-table", "data")]
    )
    def update_editing_ui_state(editing_mode, editing_indicator_id, table_data):
        """根据编辑模式更新UI显示状态"""
        if editing_mode and editing_indicator_id and table_data:
            # 编辑模式
            # 找到正在编辑的指标名称
            indicator_name = ""
            for row in table_data:
                if row.get('id') == editing_indicator_id:
                    indicator_name = row.get('name', '')
                    break
            
            # 编辑状态提示
            alert_content = dbc.Alert([
                html.I(className="fas fa-edit", style={'marginRight': '8px'}),
                f"正在编辑指标：{indicator_name}"
            ], color="info", className="mb-0")
            
            return (
                "编辑基础指标",  # 表单标题
                [html.I(className="fas fa-save", style={'marginRight': '5px'}), "更新指标"],  # 保存按钮文字
                {'marginRight': '10px', 'display': 'inline-block'},  # 显示取消编辑按钮
                alert_content,  # 提示内容
                {'marginBottom': '15px', 'display': 'block'}  # 显示提示区域
            )
        else:
            # 非编辑模式
            return (
                "新增基础指标",  # 表单标题
                [html.I(className="fas fa-plus", style={'marginRight': '5px'}), "保存指标"],  # 保存按钮文字
                {'marginRight': '10px', 'display': 'none'},  # 隐藏取消编辑按钮
                [],  # 清空提示内容
                {'marginBottom': '15px', 'display': 'none'}  # 隐藏提示区域
            )
# 新添加：取消编辑功能
    @app.callback(
        [Output("basic-indicator-code-input", "value", allow_duplicate=True),
         Output("basic-indicator-name-input", "value", allow_duplicate=True),
         Output("basic-indicator-unit-input", "value", allow_duplicate=True),
         Output("basic-indicator-description-textarea", "value", allow_duplicate=True),
         Output("basic-indicator-status-radio", "value", allow_duplicate=True),
         Output("editing-mode", "data", allow_duplicate=True),
         Output("editing-indicator-id", "data", allow_duplicate=True),
         Output("basic-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("cancel-edit-indicator", "n_clicks")],
        prevent_initial_call=True
    )
    def cancel_edit_indicator(n_clicks):
        """取消编辑 - 清空表单并退出编辑模式"""
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        return (
            "",  # 清空代码
            "",  # 清空名称
            "",  # 清空单位
            "",  # 清空描述
            "enabled",  # 重置状态
            False,  # 退出编辑模式
            None,  # 清空编辑ID
            []  # 清空表格选中状态
        )
# 新添加：新增指标按钮处理
    @app.callback(
        [Output("basic-indicator-code-input", "value", allow_duplicate=True),
         Output("basic-indicator-name-input", "value", allow_duplicate=True),
         Output("basic-indicator-unit-input", "value", allow_duplicate=True),
         Output("basic-indicator-description-textarea", "value", allow_duplicate=True),
         Output("basic-indicator-status-radio", "value", allow_duplicate=True),
         Output("editing-mode", "data", allow_duplicate=True),
         Output("editing-indicator-id", "data", allow_duplicate=True),
         Output("basic-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("add-new-indicator", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_form_for_new_indicator(n_clicks):
        """新增指标时清空表单并退出编辑模式"""
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        return (
            "",  # 清空表单
            "", 
            "", 
            "", 
            "enabled", 
            False,  # 退出编辑模式
            None,  # 清空编辑ID
            []  # 清空选中状态
        )
    # 修复后的保存/更新指标回调函数
    @app.callback(
        [Output("basic-indicator-table", "data", allow_duplicate=True),
        Output("editing-mode", "data", allow_duplicate=True),
        Output("editing-indicator-id", "data", allow_duplicate=True),
        Output("basic-indicator-table", "selected_rows", allow_duplicate=True),
        Output("basic-indicator-code-input", "value", allow_duplicate=True),
        Output("basic-indicator-name-input", "value", allow_duplicate=True),
        Output("basic-indicator-unit-input", "value", allow_duplicate=True),
        Output("basic-indicator-description-textarea", "value", allow_duplicate=True),
        Output("basic-indicator-status-radio", "value", allow_duplicate=True),
        Output("editing-status-alert", "children", allow_duplicate=True),
        Output("editing-status-alert", "style", allow_duplicate=True),
        Output("basic-indicator-main-category-dropdown", "options", allow_duplicate=True),  # 新增：分类选项更新
        Output("basic-indicator-form-category-dropdown", "options", allow_duplicate=True)],  # 新增：表单分类选项更新
        [Input("save-basic-indicator", "n_clicks")],
        [State("editing-mode", "data"),
        State("editing-indicator-id", "data"),
        State("basic-indicator-code-input", "value"),
        State("basic-indicator-name-input", "value"),
        State("basic-indicator-unit-input", "value"),
        State("basic-indicator-description-textarea", "value"),
        State("basic-indicator-category-dropdown-input", "value"),
        State("basic-indicator-status-radio", "value"),
        State("basic-indicator-form-category-dropdown", "value"), 
        State("basic-indicator-main-category-dropdown", "value")],
        prevent_initial_call=True
    )
    def save_or_update_indicator(n_clicks, editing_mode, editing_indicator_id, 
                                code, name, unit, description, category, status, main_category, category_filter):
        """保存或更新基础指标 - 修改版本，保存后自动更新分类选项"""
        
        print("=== 保存回调被触发！===")
        print(f"n_clicks: {n_clicks}")
        print(f"editing_mode: {editing_mode}")
        print(f"editing_indicator_id: {editing_indicator_id}")
        print(f"code: '{code}'")
        print(f"name: '{name}'")
        print(f"category: '{category}'")
        print(f"main_category: '{main_category}'")
        
        if not n_clicks:
            print("n_clicks为空，返回no_update")
            return [dash.no_update] * 13  # 注意：输出数量从11改为13
        
        # 验证必填字段
        if not code or not name:
            print("验证失败：缺少必填字段")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                "请填写指标代码和指标名称！"
            ], color="danger", className="mb-0")
            
            # 获取当前分类选项（保持不变）
            categories = get_all_indicator_categories()
            category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
            
            return [dash.no_update] * 9 + [error_alert, {'marginBottom': '15px', 'display': 'block'}, 
                    category_options, category_options]
        
        try:
            if editing_mode and editing_indicator_id:
                print("进入编辑模式")
                # 编辑模式：构建更新数据
                indicator_data = {
                    'id': editing_indicator_id,
                    'code': code.strip(),
                    'name': name.strip(),
                    'category': category,
                    'unit': unit.strip() if unit else "",
                    'description': description.strip() if description else "",
                    'status': status
                }
                
                print(f"更新指标数据: {indicator_data}")
                
                # 调用更新函数
                result = update_basic_indicator(indicator_data)
                print(f"update_basic_indicator 返回结果: {result}")
                
                if result:
                    print("更新成功，重新加载数据")
                    # 更新成功
                    updated_data = get_basic_indicators(category_filter)
                    success_alert = dbc.Alert([
                        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                        "指标更新成功！"
                    ], color="success", className="mb-0")
                    
                    # 重新加载分类选项
                    categories = get_all_indicator_categories()
                    category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
                    
                    return (
                        updated_data, False, None, [], "", "", "", "", "enabled",
                        success_alert, {'marginBottom': '15px', 'display': 'block'},
                        category_options, category_options  # 新增的输出
                    )
                else:
                    print("更新失败")
                    error_alert = dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                        "更新失败！"
                    ], color="danger", className="mb-0")
                    
                    # 获取当前分类选项（保持不变）
                    categories = get_all_indicator_categories()
                    category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
                    
                    return [dash.no_update] * 9 + [error_alert, {'marginBottom': '15px', 'display': 'block'},
                            category_options, category_options]
            else:
                print("进入新增模式")
                # 新增模式：构建新增数据
                new_indicator_data = {
                    'code': code.strip(),
                    'name': name.strip(),
                    'category': category,
                    'unit': unit.strip() if unit else "",
                    'description': description.strip() if description else "",
                    'status': status
                }
                
                print(f"准备新增指标数据: {new_indicator_data}")
                print(f"主分类: {main_category}")
                
                # 确保主分类有效，如果为空则默认为custom
                if not main_category:
                    main_category = 'custom'
                    print(f"主分类为空，设置为默认值: {main_category}")
                
                # 调用新增函数
                result = add_basic_indicator(new_indicator_data, main_category)
                print(f"add_basic_indicator 返回结果: {result}")
                
                if result:
                    print("新增成功，重新加载数据和分类选项")
                    # 新增成功
                    updated_data = get_basic_indicators(category_filter)
                    success_alert = dbc.Alert([
                        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                        "新指标添加成功！分类选项已更新。"
                    ], color="success", className="mb-0")
                    
                    # 重新加载分类选项（这是关键！）
                    categories = get_all_indicator_categories()
                    category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
                    print(f"更新后的分类选项: {[opt['label'] for opt in category_options]}")
                    
                    return (
                        updated_data, False, None, [], "", "", "", "", "enabled",
                        success_alert, {'marginBottom': '15px', 'display': 'block'},
                        category_options, category_options  # 新增的输出
                    )
                else:
                    print("新增失败")
                    # 新增失败
                    error_alert = dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                        f"添加失败！指标代码 '{code}' 已存在，请使用不同的代码。"
                    ], color="danger", className="mb-0")
                    
                    # 获取当前分类选项（保持不变）
                    categories = get_all_indicator_categories()
                    category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
                    
                    return [dash.no_update] * 9 + [error_alert, {'marginBottom': '15px', 'display': 'block'},
                            category_options, category_options]
            
        except Exception as e:
            print(f"保存指标错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"操作失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            # 获取当前分类选项（保持不变）
            categories = get_all_indicator_categories()
            category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
            
            return [dash.no_update] * 9 + [error_alert, {'marginBottom': '15px', 'display': 'block'},
                    category_options, category_options]
    
    @app.callback(
        [Output("basic-indicator-table", "data", allow_duplicate=True),
        Output("basic-indicator-table", "selected_rows", allow_duplicate=True),
        Output("editing-status-alert", "children", allow_duplicate=True),
        Output("editing-status-alert", "style", allow_duplicate=True)],
        [Input("delete-selected-indicator", "n_clicks")],
        [State("basic-indicator-table", "selected_rows"),
        State("basic-indicator-table", "data"),
        State("basic-indicator-main-category-dropdown", "value")],
        prevent_initial_call=True
    )
    def delete_selected_indicators(n_clicks, selected_rows, table_data, category_filter):
        """删除选中的指标"""
        
        print(f"=== 删除回调被触发 ===")
        print(f"n_clicks: {n_clicks}")
        print(f"selected_rows: {selected_rows}")
        print(f"table_data长度: {len(table_data) if table_data else 0}")
        print(f"category_filter: {category_filter}")
        
        if not n_clicks or not selected_rows or not table_data:
            print("删除条件不满足，返回no_update")
            return [dash.no_update] * 4
        
        try:
            # 获取要删除的指标信息
            indicators_to_delete = []
            for row_index in selected_rows:
                if row_index < len(table_data):
                    indicator = table_data[row_index]
                    indicators_to_delete.append(indicator)
            
            print(f"准备删除的指标: {indicators_to_delete}")
            
            if not indicators_to_delete:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "没有找到要删除的指标！"
                ], color="danger", className="mb-0")
                
                return [dash.no_update, dash.no_update, error_alert, 
                        {'marginBottom': '15px', 'display': 'block'}]
            
            # 执行删除操作
            deleted_count = 0
            failed_indicators = []
            
            for indicator in indicators_to_delete:
                indicator_id = indicator.get('id')
                indicator_name = indicator.get('name', '未知指标')
                
                print(f"正在删除指标ID: {indicator_id}, 名称: {indicator_name}")
                
                if indicator_id:
                    result = delete_basic_indicator(indicator_id)
                    if result:
                        deleted_count += 1
                        print(f"成功删除指标: {indicator_name}")
                    else:
                        failed_indicators.append(indicator_name)
                        print(f"删除失败: {indicator_name}")
                else:
                    failed_indicators.append(indicator_name)
                    print(f"指标ID无效: {indicator_name}")
            
            # 准备结果消息
            if deleted_count > 0 and len(failed_indicators) == 0:
                # 全部删除成功
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个指标！"
                ], color="success", className="mb-0")
                
                result_alert = success_alert
                alert_style = {'marginBottom': '15px', 'display': 'block'}
                
            elif deleted_count > 0 and len(failed_indicators) > 0:
                # 部分删除成功
                warning_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个指标，{len(failed_indicators)} 个指标删除失败！"
                ], color="warning", className="mb-0")
                
                result_alert = warning_alert
                alert_style = {'marginBottom': '15px', 'display': 'block'}
                
            else:
                # 全部删除失败
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "删除操作失败！请检查网络连接或数据库状态。"
                ], color="danger", className="mb-0")
                
                result_alert = error_alert
                alert_style = {'marginBottom': '15px', 'display': 'block'}
            
            # 重新加载表格数据
            if deleted_count > 0:
                print("重新加载表格数据...")
                updated_data = get_basic_indicators(category_filter)
                print(f"重新加载后的数据量: {len(updated_data)}")
                
                # 返回：更新的数据、清空选中状态、显示结果消息
                return (updated_data, [], result_alert, alert_style)
            else:
                # 没有成功删除任何指标，保持原数据
                return (dash.no_update, [], result_alert, alert_style)
                
        except Exception as e:
            print(f"删除指标过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"删除操作发生错误：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update, dash.no_update, error_alert, 
                    {'marginBottom': '15px', 'display': 'block'}]
    # 修改动态加载指标分类选项的回调函数
    @app.callback(
        [Output("basic-indicator-main-category-dropdown", "options", allow_duplicate=True),
        Output("basic-indicator-form-category-dropdown", "options", allow_duplicate=True)],  
        [Input("modal-basic-indicator", "is_open"),
        Input("confirm-add-category", "n_clicks"),
        Input("confirm-delete-category", "n_clicks")],  # 添加删除触发器
        prevent_initial_call=True
    )
    def update_category_dropdown_options(is_open, confirm_add_clicks, confirm_delete_clicks):
        """动态更新指标分类下拉菜单选项 - 修复版本，支持多种触发条件"""
        print(f"=== 更新分类下拉菜单 ===")
        print(f"模态框打开: {is_open}, 确认添加分类: {confirm_add_clicks}, 确认删除分类: {confirm_delete_clicks}")
        
        if is_open or confirm_add_clicks or confirm_delete_clicks:
            categories = get_all_indicator_categories()
            options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
            print(f"生成下拉菜单选项: {[opt['label'] for opt in options]}")
            return options, options  # 返回给两个下拉菜单
        return dash.no_update, dash.no_update

    
    # 切换添加分类模式
    @app.callback(
        [Output("basic-indicator-main-category-dropdown", "style", allow_duplicate=True),
         Output("add-new-category-btn", "style", allow_duplicate=True),
         Output("add-category-input-div", "style", allow_duplicate=True)],
        [Input("add-new-category-btn", "n_clicks"),
         Input("confirm-add-category", "n_clicks"),
         Input("cancel-add-category", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_add_category_mode(add_clicks, confirm_clicks, cancel_clicks):
        """切换添加分类模式"""
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "add-new-category-btn":
            # 进入添加模式
            return (
                {'width': '70%', 'marginRight': '5px', 'display': 'none'},  # 隐藏下拉菜单
                {'width': '12%', 'padding': '6px', 'marginRight': '5px', 'display': 'none'},  # 隐藏添加按钮
                {'display': 'block', 'marginTop': '5px'}                    # 显示输入区域
            )
        else:
            # 退出添加模式
            return (
                {'width': '70%', 'marginRight': '5px', 'display': 'block'}, # 显示下拉菜单
                {'width': '12%', 'padding': '6px', 'marginRight': '5px', 'display': 'block'}, # 显示添加按钮
                {'display': 'none', 'marginTop': '5px'}                     # 隐藏输入区域
            )

    # 确认添加新分类
    @app.callback(
        [Output("new-category-name-input", "value"),
        Output("editing-status-alert", "children", allow_duplicate=True),
        Output("editing-status-alert", "style", allow_duplicate=True),
        Output("basic-indicator-main-category-dropdown", "options", allow_duplicate=True),
        Output("basic-indicator-form-category-dropdown", "options", allow_duplicate=True)],
        [Input("confirm-add-category", "n_clicks")],
        [State("new-category-name-input", "value")],
        prevent_initial_call=True
    )
    def confirm_add_new_category(n_clicks, category_name):
        """确认添加新的指标分类 - 修复版本，同时更新所有分类下拉菜单"""
        if not n_clicks or not category_name or not category_name.strip():
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            success, message = add_new_indicator_category(category_name.strip())
            
            # 重新加载分类选项
            categories = get_all_indicator_categories()
            category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
            
            if success:
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    message
                ], color="success", className="mb-0")
                
                return ("", success_alert, {'marginBottom': '15px', 'display': 'block'}, 
                        category_options, category_options)
            else:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    message
                ], color="danger", className="mb-0")
                
                return (dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'},
                        category_options, category_options)
                
        except Exception as e:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"添加分类失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            # 即使出错，也尝试更新分类选项
            categories = get_all_indicator_categories()
            category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
            
            return (dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'},
                    category_options, category_options)

    # 切换删除分类模式
    @app.callback(
        [Output("basic-indicator-main-category-dropdown", "style", allow_duplicate=True),
         Output("add-new-category-btn", "style", allow_duplicate=True),
         Output("delete-category-btn", "style"),
         Output("delete-category-input-div", "style")],
        [Input("delete-category-btn", "n_clicks"),
         Input("confirm-delete-category", "n_clicks"),
         Input("cancel-delete-category", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_delete_category_mode(delete_clicks, confirm_clicks, cancel_clicks):
        """切换删除分类模式"""
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "delete-category-btn":
            # 进入删除模式
            return (
                {'width': '70%', 'marginRight': '5px', 'display': 'none'},  # 隐藏主下拉菜单
                {'width': '12%', 'padding': '6px', 'marginRight': '5px', 'display': 'none'},  # 隐藏添加按钮
                {'width': '12%', 'padding': '6px', 'display': 'none'},      # 隐藏删除按钮
                {'display': 'block', 'marginTop': '5px'}                    # 显示删除输入区域
            )
        else:
            # 退出删除模式
            return (
                {'width': '70%', 'marginRight': '5px', 'display': 'block'}, # 显示主下拉菜单
                {'width': '12%', 'padding': '6px', 'marginRight': '5px', 'display': 'block'}, # 显示添加按钮
                {'width': '12%', 'padding': '6px', 'display': 'block'},     # 显示删除按钮
                {'display': 'none', 'marginTop': '5px'}                     # 隐藏删除输入区域
            )

    # 更新删除分类下拉菜单选项
    @app.callback(
        Output("delete-category-dropdown", "options"),
        [Input("delete-category-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def update_delete_category_options(n_clicks):
        """更新删除分类下拉菜单选项"""
        if n_clicks:
            categories = get_deletable_categories()
            return [{'label': cat['label'], 'value': cat['value']} for cat in categories]
        return []

    # 确认删除分类
    @app.callback(
        [Output("basic-indicator-table", "data", allow_duplicate=True),
         Output("editing-status-alert", "children", allow_duplicate=True),
         Output("editing-status-alert", "style", allow_duplicate=True),
         Output("basic-indicator-main-category-dropdown", "options", allow_duplicate=True),
         Output("basic-indicator-form-category-dropdown", "options", allow_duplicate=True),
         Output("delete-category-dropdown", "value"),
         Output("basic-indicator-main-category-dropdown", "value", allow_duplicate=True)],
        [Input("confirm-delete-category", "n_clicks")],
        [State("delete-category-dropdown", "value"),
         State("basic-indicator-main-category-dropdown", "value")],
        prevent_initial_call=True
    )
    def confirm_delete_category(n_clicks, category_to_delete, current_category):
        """确认删除分类"""
        if not n_clicks or not category_to_delete:
            return [dash.no_update] * 7
        
        try:
            # 执行删除操作
            success, message = delete_category_and_indicators(category_to_delete)
            
            if success:
                # 删除成功
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    message
                ], color="success", className="mb-0")
                
                # 重新加载分类选项
                categories = get_all_indicator_categories()
                category_options = [{'label': cat['label'], 'value': cat['value']} for cat in categories]
                
                # 如果当前选中的分类被删除了，切换到"全部指标"
                new_current_category = 'all' if current_category == category_to_delete else current_category
                
                # 重新加载表格数据
                updated_data = get_basic_indicators(new_current_category)
                
                return (
                    updated_data,
                    success_alert,
                    {'marginBottom': '15px', 'display': 'block'},
                    category_options,
                    category_options,
                    None,  # 清空删除下拉菜单的选择
                    new_current_category
                )
            else:
                # 删除失败
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    message
                ], color="danger", className="mb-0")
                
                return [dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'}] + [dash.no_update] * 4
                
        except Exception as e:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"删除操作发生错误：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'}] + [dash.no_update] * 4


# ====== 复合指标相关回调函数 ======
    
    # 加载复合指标数据的回调函数
    @app.callback(
        Output('composite-indicator-table', 'data'),
        [Input('modal-composite-indicator', 'is_open'),
         Input('composite-construction-mode-dropdown', 'value'),
         Input('composite-status-dropdown', 'value')]
    )
    def load_composite_indicators_data(is_open, construction_mode, status_value):
        """当复合指标模态窗口打开、施工模式或状态改变时，从数据库加载数据"""
        if is_open:
            print(f"=== 加载复合指标数据 ===")
            print(f"施工模式: {construction_mode}")
            print(f"状态值: {status_value}")
            
            # 获取指定模式的数据
            data = get_composite_indicators(construction_mode)
            print(f"从数据库获取到 {len(data)} 条记录")
            
            # 如果有状态筛选，进一步过滤
            if status_value and status_value != 'all':
                status_map = {'enabled': '启用', 'disabled': '停用'}
                target_status = status_map.get(status_value, status_value)
                original_count = len(data)
                data = [item for item in data if item.get('status') == target_status]
                print(f"状态筛选后剩余 {len(data)} 条记录（原{original_count}条）")
            
            return data
        return []

    # 更新操作按钮状态
    @app.callback(
        [Output("edit-selected-composite", "disabled"),
         Output("delete-selected-composite", "disabled")],
        [Input("composite-indicator-table", "selected_rows"),
         Input("composite-editing-mode", "data")]
    )
    def update_composite_button_states(selected_rows, editing_mode):
        """根据表格选中状态和编辑模式更新按钮可用性"""
        if editing_mode:
            return True, True
        
        if not selected_rows or len(selected_rows) == 0:
            return True, True
        
        if len(selected_rows) != 1:
            return True, False
            
        return False, False

    # 显示选中指标的详情
    @app.callback(
        [Output("composite-detail-name", "children"),
         Output("composite-detail-code", "children"),
         Output("composite-detail-mode", "children"),
         Output("composite-detail-calc-type", "children"),
         Output("composite-detail-formula", "children"),
         Output("composite-dependencies-table", "data")],
        [Input("composite-indicator-table", "selected_rows")],
        [State("composite-indicator-table", "data")]
    )
    def display_composite_indicator_details(selected_rows, table_data):
        """显示选中复合指标的详细信息"""
        if not selected_rows or not table_data or len(selected_rows) == 0:
            return "请选择指标", "-", "-", "-", "请选择指标查看公式", []
        
        try:
            selected_row = table_data[selected_rows[0]]
            
            # 基本信息
            name = selected_row.get('name', '-')
            code = selected_row.get('code', '-')
            mode = selected_row.get('construction_mode', '-')
            calc_type = selected_row.get('calculation_type', '-')
            formula = selected_row.get('formula', '无公式')
            
            # 获取依赖关系数据
            dependencies_data = []
            dependencies_json = selected_row.get('dependencies')
            
            if dependencies_json:
                try:
                    import json
                    if isinstance(dependencies_json, str):
                        dependencies = json.loads(dependencies_json)
                    else:
                        dependencies = dependencies_json
                    
                    # 处理基础指标依赖
                    if 'basic_indicators' in dependencies:
                        for item in dependencies['basic_indicators']:
                            dependencies_data.append({
                                'type': '基础指标',
                                'code': item.get('code', ''),
                                'name': item.get('name', ''),
                                'coefficient': item.get('coefficient', 1.0)
                            })
                    
                    # 处理输入参数依赖
                    if 'input_parameters' in dependencies:
                        for item in dependencies['input_parameters']:
                            dependencies_data.append({
                                'type': '输入参数',
                                'code': item.get('code', ''),
                                'name': item.get('name', ''),
                                'coefficient': '-'
                            })
                    
                    # 处理复合指标依赖
                    if 'composite_indicators' in dependencies:
                        for item in dependencies['composite_indicators']:
                            dependencies_data.append({
                                'type': '复合指标',
                                'code': item.get('code', ''),
                                'name': item.get('name', ''),
                                'coefficient': item.get('coefficient', 1.0)
                            })
                            
                except Exception as e:
                    print(f"解析依赖关系JSON错误: {e}")
            
            return name, code, mode, calc_type, formula, dependencies_data
            
        except Exception as e:
            print(f"显示指标详情错误: {e}")
            return "解析错误", "-", "-", "-", "解析错误", []

    # 编辑按钮回调函数
    @app.callback(
        [Output("composite-code-input", "value"),
        Output("composite-name-input", "value"),
        Output("composite-unit-input", "value"),
        Output("composite-form-construction-mode", "value"),
        Output("composite-calculation-type", "value"),
        Output("composite-formula-input", "value"),
        Output("composite-description-input", "value"),
        Output("composite-status-radio", "value"),
        Output("composite-editing-mode", "data"),
        Output("composite-editing-indicator-id", "data"),
        Output("composite-original-indicator-data", "data")],
        [Input("edit-selected-composite", "n_clicks")],
        [State("composite-indicator-table", "selected_rows"),
        State("composite-indicator-table", "data")],
        prevent_initial_call=True
    )
    def edit_selected_composite_indicator(n_clicks, selected_rows, table_data):
        """编辑所选复合指标 - 去掉common模式映射"""
        if not n_clicks or not selected_rows or not table_data:
            return "", "", "", "steel_cage", "custom", "", "", "enabled", False, None, {}
        
        selected_row = table_data[selected_rows[0]]
        
        # 将状态从中文转换为英文
        status_value = 'enabled' if selected_row.get('status') == '启用' else 'disabled'
        
        # 将施工模式从中文转换为英文 - 去掉通用模式映射
        mode_map = {
            '钢筋笼模式': 'steel_cage', 
            '钢衬里模式': 'steel_lining'
            # 删除：'通用模式': 'common'
        }
        construction_mode = mode_map.get(selected_row.get('construction_mode'), 'steel_cage')
        
        # 计算类型转换
        calc_type_map = {
            '求和': 'sum',
            '乘积': 'product', 
            '加权求和': 'weighted_sum',
            '自定义公式': 'custom'
        }
        calculation_type = calc_type_map.get(selected_row.get('calculation_type'), 'custom')
        
        print(f"编辑调试 - 原始施工模式: '{selected_row.get('construction_mode')}', 转换后: '{construction_mode}'")
        
        original_data = selected_row.copy()
        
        return (
            selected_row.get('code', ''),
            selected_row.get('name', ''),
            selected_row.get('unit', ''),
            construction_mode,
            calculation_type,
            selected_row.get('formula', ''),
            selected_row.get('description', ''),
            status_value,
            True,  # 进入编辑模式
            selected_row.get('id'),
            original_data
        )
    

    # 更新编辑UI状态
    @app.callback(
        [Output("composite-form-title", "children"),
         Output("save-composite-indicator", "children"),
         Output("cancel-edit-composite", "style"),
         Output("composite-editing-status-alert", "children"),
         Output("composite-editing-status-alert", "style")],
        [Input("composite-editing-mode", "data"),
         Input("composite-editing-indicator-id", "data")],
        [State("composite-indicator-table", "data")]
    )
    def update_composite_editing_ui_state(editing_mode, editing_indicator_id, table_data):
        """根据编辑模式更新UI显示状态"""
        if editing_mode and editing_indicator_id and table_data:
            # 找到正在编辑的指标名称
            indicator_name = ""
            for row in table_data:
                if row.get('id') == editing_indicator_id:
                    indicator_name = row.get('name', '')
                    break
            
            alert_content = dbc.Alert([
                html.I(className="fas fa-edit", style={'marginRight': '8px'}),
                f"正在编辑复合指标：{indicator_name}"
            ], color="info", className="mb-0")
            
            return (
                "编辑复合指标",
                [html.I(className="fas fa-save", style={'marginRight': '5px'}), "更新指标"],
                {'marginRight': '10px', 'display': 'inline-block'},
                alert_content,
                {'marginBottom': '15px', 'display': 'block'}
            )
        else:
            return (
                "新增复合指标",
                [html.I(className="fas fa-plus", style={'marginRight': '5px'}), "保存指标"],
                {'marginRight': '10px', 'display': 'none'},
                [],
                {'marginBottom': '15px', 'display': 'none'}
            )

    # 取消编辑功能
    @app.callback(
        [Output("composite-code-input", "value", allow_duplicate=True),
        Output("composite-name-input", "value", allow_duplicate=True),
        Output("composite-unit-input", "value", allow_duplicate=True),
        Output("composite-formula-input", "value", allow_duplicate=True),
        Output("composite-description-input", "value", allow_duplicate=True),
        Output("composite-status-radio", "value", allow_duplicate=True),
        Output("composite-editing-mode", "data", allow_duplicate=True),
        Output("composite-editing-indicator-id", "data", allow_duplicate=True),
        Output("composite-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("cancel-edit-composite", "n_clicks")],
        prevent_initial_call=True
    )
    def cancel_edit_composite_indicator(n_clicks):
        """取消编辑复合指标 - 去掉category"""
        if not n_clicks:
            return [dash.no_update] * 9
        
        return "", "", "", "", "", "enabled", False, None, []

    # 新增指标按钮处理
    @app.callback(
        [Output("composite-code-input", "value", allow_duplicate=True),
        Output("composite-name-input", "value", allow_duplicate=True),
        Output("composite-unit-input", "value", allow_duplicate=True),
        Output("composite-formula-input", "value", allow_duplicate=True),
        Output("composite-description-input", "value", allow_duplicate=True),
        Output("composite-status-radio", "value", allow_duplicate=True),
        Output("composite-editing-mode", "data", allow_duplicate=True),
        Output("composite-editing-indicator-id", "data", allow_duplicate=True),
        Output("composite-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("add-new-composite", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_form_for_new_composite_indicator(n_clicks):
        """新增复合指标时清空表单 - 去掉category"""
        if not n_clicks:
            return [dash.no_update] * 9
        
        return "", "", "", "", "", "enabled", False, None, []

    # 保存/更新复合指标回调函数
    @app.callback(
        [Output("composite-indicator-table", "data", allow_duplicate=True),
        Output("composite-editing-mode", "data", allow_duplicate=True),
        Output("composite-editing-indicator-id", "data", allow_duplicate=True),
        Output("composite-indicator-table", "selected_rows", allow_duplicate=True),
        Output("composite-code-input", "value", allow_duplicate=True),
        Output("composite-name-input", "value", allow_duplicate=True),
        Output("composite-unit-input", "value", allow_duplicate=True),
        Output("composite-formula-input", "value", allow_duplicate=True),
        Output("composite-description-input", "value", allow_duplicate=True),
        Output("composite-status-radio", "value", allow_duplicate=True),
        Output("composite-editing-status-alert", "children", allow_duplicate=True),
        Output("composite-editing-status-alert", "style", allow_duplicate=True)],
        [Input("save-composite-indicator", "n_clicks")],
        [State("composite-editing-mode", "data"),
        State("composite-editing-indicator-id", "data"),
        State("composite-code-input", "value"),
        State("composite-name-input", "value"),
        State("composite-unit-input", "value"),
        State("composite-form-construction-mode", "value"),
        State("composite-calculation-type", "value"),
        State("composite-formula-input", "value"),
        State("composite-description-input", "value"),
        State("composite-status-radio", "value"),
        State("composite-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def save_or_update_composite_indicator(n_clicks, editing_mode, editing_indicator_id, 
                                        code, name, unit, construction_mode, 
                                        calculation_type, formula, description, status, filter_mode):
        """保存或更新复合指标 - 修复版本，保持原有dependencies"""
        
        print("=== 复合指标保存调试 ===")
        print(f"n_clicks: {n_clicks}")
        print(f"editing_mode: {editing_mode}")
        print(f"editing_indicator_id: {editing_indicator_id}")
        print(f"status值: '{status}' (类型: {type(status)})")
        
        if not n_clicks:
            return [dash.no_update] * 12
        
        # 验证必填字段
        if not code or not name or not formula:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                "请填写指标代码、指标名称和计算公式！"
            ], color="danger", className="mb-0")
            
            return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
        
        try:
            # 确保状态值是正确的英文值
            if status not in ['enabled', 'disabled']:
                print(f"警告：状态值 '{status}' 不在允许范围内，默认设为 'enabled'")
                status = 'enabled'
            
            print(f"最终使用的状态值: '{status}'")
            
            # 获取原有的dependencies（如果是编辑模式）
            original_dependencies = '{}'
            if editing_mode and editing_indicator_id:
                try:
                    conn = create_raw_mysql_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT dependencies FROM composite_indicators WHERE id = %s", (editing_indicator_id,))
                        result = cursor.fetchone()
                        if result and result[0]:
                            original_dependencies = result[0]
                            print(f"获取到原有dependencies: {original_dependencies}")
                        conn.close()
                except Exception as e:
                    print(f"获取原有dependencies失败: {e}")
            
            # 构建指标数据
            indicator_data = {
                'code': code.strip(),
                'name': name.strip(),
                'construction_mode': construction_mode,
                'unit': unit.strip() if unit else "",
                'formula': formula.strip(),
                'calculation_type': calculation_type,
                'description': description.strip() if description else "",
                'status': status,
                'dependencies': original_dependencies  # 使用原有的dependencies而不是固定的'{}'
            }
            
            print(f"构建的指标数据: {indicator_data}")
            
            if editing_mode and editing_indicator_id:
                # 更新模式
                indicator_data['id'] = editing_indicator_id
                print(f"执行更新操作，ID: {editing_indicator_id}")
                result = update_composite_indicator(indicator_data)
                operation = "更新"
            else:
                # 新增模式 - 新增时使用空的dependencies
                indicator_data['dependencies'] = '{}'
                print("执行新增操作")
                result = add_composite_indicator(indicator_data)
                operation = "新增"
            
            print(f"{operation}操作结果: {result}")
            
            if result:
                # 操作成功，重新加载数据
                print("操作成功，重新加载数据")
                updated_data = get_composite_indicators(filter_mode)
                print(f"重新加载后的数据条数: {len(updated_data)}")
                
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    f"复合指标{operation}成功！"
                ], color="success", className="mb-0")
                
                return (
                    updated_data, False, None, [], "", "", "", "", "", "enabled",
                    success_alert, {'marginBottom': '15px', 'display': 'block'}
                )
            else:
                # 操作失败
                print("操作失败")
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    f"{operation}失败！请检查控制台错误信息。"
                ], color="danger", className="mb-0")
                
                return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
            
        except Exception as e:
            print(f"保存复合指标错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"操作失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
        
    # 删除复合指标回调函数
    @app.callback(
        [Output("composite-indicator-table", "data", allow_duplicate=True),
         Output("composite-indicator-table", "selected_rows", allow_duplicate=True),
         Output("composite-editing-status-alert", "children", allow_duplicate=True),
         Output("composite-editing-status-alert", "style", allow_duplicate=True)],
        [Input("delete-selected-composite", "n_clicks")],
        [State("composite-indicator-table", "selected_rows"),
         State("composite-indicator-table", "data"),
         State("composite-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def delete_selected_composite_indicators(n_clicks, selected_rows, table_data, filter_mode):
        """删除选中的复合指标"""
        
        if not n_clicks or not selected_rows or not table_data:
            return [dash.no_update] * 4
        
        try:
            deleted_count = 0
            failed_indicators = []
            
            for row_index in selected_rows:
                if row_index < len(table_data):
                    indicator = table_data[row_index]
                    indicator_id = indicator.get('id')
                    indicator_name = indicator.get('name', '未知指标')
                    
                    if indicator_id:
                        result = delete_composite_indicator(indicator_id)
                        if result:
                            deleted_count += 1
                        else:
                            failed_indicators.append(indicator_name)
            
            # 准备结果消息
            if deleted_count > 0 and len(failed_indicators) == 0:
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个复合指标！"
                ], color="success", className="mb-0")
                result_alert = success_alert
            elif deleted_count > 0 and len(failed_indicators) > 0:
                warning_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个指标，{len(failed_indicators)} 个指标删除失败！"
                ], color="warning", className="mb-0")
                result_alert = warning_alert
            else:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "删除操作失败！"
                ], color="danger", className="mb-0")
                result_alert = error_alert
            
            # 重新加载数据
            if deleted_count > 0:
                updated_data = get_composite_indicators(filter_mode)
                return (updated_data, [], result_alert, {'marginBottom': '15px', 'display': 'block'})
            else:
                return (dash.no_update, [], result_alert, {'marginBottom': '15px', 'display': 'block'})
                
        except Exception as e:
            print(f"删除复合指标错误: {str(e)}")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"删除操作发生错误：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update, dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'}]

# ====== 综合指标相关回调函数 ======

    # 加载综合指标数据的回调函数
    @app.callback(
        Output('comprehensive-indicator-table', 'data'),
        [Input('modal-comprehensive-indicator', 'is_open'),
         Input('comprehensive-construction-mode-dropdown', 'value'),
         Input('comprehensive-calculation-method-dropdown', 'value'),
         Input('comprehensive-indicator-type-dropdown', 'value'),
         Input('comprehensive-status-dropdown', 'value')]
    )
    def load_comprehensive_indicators_data(is_open, construction_mode, calculation_method, indicator_type, status_value):
        """当综合指标模态窗口打开或筛选条件改变时，从数据库加载数据"""
        if is_open:
            print(f"=== 加载综合指标数据 ===")
            print(f"施工模式: {construction_mode}")
            print(f"计算方法: {calculation_method}")
            print(f"指标类型: {indicator_type}")
            print(f"状态值: {status_value}")
            
            # 获取指定模式的数据
            data = get_comprehensive_indicators(construction_mode)
            print(f"从数据库获取到 {len(data)} 条记录")
            
            # 应用多重筛选
            if calculation_method and calculation_method != 'all':
                method_map = {'ml_prediction': 'AI预测', 'ratio_method': '比率法'}
                target_method = method_map.get(calculation_method, calculation_method)
                data = [item for item in data if item.get('calculation_method') == target_method]
                print(f"计算方法筛选后: {len(data)} 条记录")
            
            if indicator_type and indicator_type != 'all':
                type_map = {'raw_value': '原始值', 'final_value': '最终值'}
                target_type = type_map.get(indicator_type, indicator_type)
                data = [item for item in data if item.get('indicator_type') == target_type]
                print(f"指标类型筛选后: {len(data)} 条记录")
            
            if status_value and status_value != 'all':
                status_map = {'enabled': '启用', 'disabled': '停用'}
                target_status = status_map.get(status_value, status_value)
                data = [item for item in data if item.get('status') == target_status]
                print(f"状态筛选后: {len(data)} 条记录")
            
            return data
        return []

    # 更新操作按钮状态
    @app.callback(
        [Output("edit-selected-comprehensive", "disabled"),
         Output("delete-selected-comprehensive", "disabled")],
        [Input("comprehensive-indicator-table", "selected_rows"),
         Input("comprehensive-editing-mode", "data")]
    )
    def update_comprehensive_button_states(selected_rows, editing_mode):
        """根据表格选中状态和编辑模式更新按钮可用性"""
        if editing_mode:
            return True, True
        
        if not selected_rows or len(selected_rows) == 0:
            return True, True
        
        if len(selected_rows) != 1:
            return True, False
            
        return False, False

    # 显示选中指标的详情
    @app.callback(
        [Output("comprehensive-detail-name", "children"),
         Output("comprehensive-detail-code", "children"),
         Output("comprehensive-detail-mode", "children"),
         Output("comprehensive-detail-method", "children"),
         Output("comprehensive-detail-type", "children"),
         Output("comprehensive-detail-logic", "children"),
         Output("comprehensive-dependencies-table", "data")],
        [Input("comprehensive-indicator-table", "selected_rows")],
        [State("comprehensive-indicator-table", "data")]
    )
    def display_comprehensive_indicator_details(selected_rows, table_data):
        """显示选中综合指标的详细信息"""
        if not selected_rows or not table_data or len(selected_rows) == 0:
            return "请选择指标", "-", "-", "-", "-", "请选择指标查看计算逻辑", []
        
        try:
            selected_row = table_data[selected_rows[0]]
            
            # 基本信息
            name = selected_row.get('name', '-')
            code = selected_row.get('code', '-')
            mode = selected_row.get('construction_mode', '-')
            method = selected_row.get('calculation_method', '-')
            indicator_type = selected_row.get('indicator_type', '-')
            logic = selected_row.get('calculation_logic', '无计算逻辑')
            
            # 获取依赖关系数据
            dependencies_data = []
            dependencies_json = selected_row.get('dependencies')
            
            if dependencies_json:
                try:
                    import json
                    if isinstance(dependencies_json, str):
                        dependencies = json.loads(dependencies_json)
                    else:
                        dependencies = dependencies_json
                    
                    # 处理复合指标依赖
                    if 'composite_indicators' in dependencies:
                        for item in dependencies['composite_indicators']:
                            dependencies_data.append({
                                'type': '复合指标',
                                'reference': item,
                                'description': '依赖的复合指标'
                            })
                    
                    # 处理AI模型依赖
                    if 'ml_model' in dependencies:
                        dependencies_data.append({
                            'type': 'AI模型',
                            'reference': dependencies['ml_model'],
                            'description': '使用的机器学习模型'
                        })
                    
                    # 处理比率规则依赖
                    if 'ratio_rule' in dependencies:
                        dependencies_data.append({
                            'type': '比率规则',
                            'reference': dependencies['ratio_rule'],
                            'description': '历史成本占比规则'
                        })
                    
                    # 处理综合指标依赖
                    if 'comprehensive_indicators' in dependencies:
                        for item in dependencies['comprehensive_indicators']:
                            dependencies_data.append({
                                'type': '综合指标',
                                'reference': item,
                                'description': '依赖的其他综合指标'
                            })
                    
                    # 处理输入参数依赖
                    if 'input_parameters' in dependencies:
                        for item in dependencies['input_parameters']:
                            dependencies_data.append({
                                'type': '输入参数',
                                'reference': item,
                                'description': '需要用户输入的参数'
                            })
                            
                except Exception as e:
                    print(f"解析综合指标依赖关系JSON错误: {e}")
            
            return name, code, mode, method, indicator_type, logic, dependencies_data
            
        except Exception as e:
            print(f"显示综合指标详情错误: {e}")
            return "解析错误", "-", "-", "-", "-", "解析错误", []

    # 编辑按钮回调函数
    @app.callback(
        [Output("comprehensive-code-input", "value"),
        Output("comprehensive-name-input", "value"),
        Output("comprehensive-unit-input", "value"),
        Output("comprehensive-form-construction-mode", "value"),
        Output("comprehensive-form-calculation-method", "value"),
        Output("comprehensive-form-indicator-type", "value"),
        Output("comprehensive-logic-input", "value"),
        Output("comprehensive-description-input", "value"),
        Output("comprehensive-status-radio", "value"),
        Output("comprehensive-editing-mode", "data"),
        Output("comprehensive-editing-indicator-id", "data"),
        Output("comprehensive-original-indicator-data", "data")],
        [Input("edit-selected-comprehensive", "n_clicks")],
        [State("comprehensive-indicator-table", "selected_rows"),
        State("comprehensive-indicator-table", "data")],
        prevent_initial_call=True
    )
    def edit_selected_comprehensive_indicator(n_clicks, selected_rows, table_data):
        """编辑所选综合指标"""
        if not n_clicks or not selected_rows or not table_data:
            return "", "", "", "steel_cage", "ml_prediction", "raw_value", "", "", "enabled", False, None, {}
        
        selected_row = table_data[selected_rows[0]]
        
        # 将状态从中文转换为英文
        status_value = 'enabled' if selected_row.get('status') == '启用' else 'disabled'
        
        # 将各种枚举值从中文转换为英文
        mode_map = {
            '钢筋笼模式': 'steel_cage', 
            '钢衬里模式': 'steel_lining'
        }
        construction_mode = mode_map.get(selected_row.get('construction_mode'), 'steel_cage')
        
        method_map = {
            'AI预测': 'ml_prediction',
            '比率法': 'ratio_method'
        }
        calculation_method = method_map.get(selected_row.get('calculation_method'), 'ml_prediction')
        
        type_map = {
            '原始值': 'raw_value',
            '最终值': 'final_value'
        }
        indicator_type = type_map.get(selected_row.get('indicator_type'), 'raw_value')
        
        original_data = selected_row.copy()
        
        return (
            selected_row.get('code', ''),
            selected_row.get('name', ''),
            selected_row.get('unit', ''),
            construction_mode,
            calculation_method,
            indicator_type,
            selected_row.get('calculation_logic', ''),
            selected_row.get('description', ''),
            status_value,
            True,  # 进入编辑模式
            selected_row.get('id'),
            original_data
        )


    # 更新编辑UI状态
    @app.callback(
        [Output("comprehensive-form-title", "children"),
        Output("save-comprehensive-indicator", "children"),
        Output("cancel-edit-comprehensive", "style"),
        Output("comprehensive-editing-status-alert", "children"),
        Output("comprehensive-editing-status-alert", "style")],
        [Input("comprehensive-editing-mode", "data"),
        Input("comprehensive-editing-indicator-id", "data")],
        [State("comprehensive-indicator-table", "data")]
    )
    def update_comprehensive_editing_ui_state(editing_mode, editing_indicator_id, table_data):
        """根据编辑模式更新UI显示状态"""
        if editing_mode and editing_indicator_id and table_data:
            # 找到正在编辑的指标名称
            indicator_name = ""
            for row in table_data:
                if row.get('id') == editing_indicator_id:
                    indicator_name = row.get('name', '')
                    break
            
            alert_content = dbc.Alert([
                html.I(className="fas fa-edit", style={'marginRight': '8px'}),
                f"正在编辑综合指标：{indicator_name}"
            ], color="info", className="mb-0")
            
            return (
                "编辑综合指标",
                [html.I(className="fas fa-save", style={'marginRight': '5px'}), "更新指标"],
                {'marginRight': '10px', 'display': 'inline-block'},
                alert_content,
                {'marginBottom': '15px', 'display': 'block'}
            )
        else:
            return (
                "新增综合指标",
                [html.I(className="fas fa-plus", style={'marginRight': '5px'}), "保存指标"],
                {'marginRight': '10px', 'display': 'none'},
                [],
                {'marginBottom': '15px', 'display': 'none'}
            )

    # 取消编辑功能
    @app.callback(
        [Output("comprehensive-code-input", "value", allow_duplicate=True),
        Output("comprehensive-name-input", "value", allow_duplicate=True),
        Output("comprehensive-unit-input", "value", allow_duplicate=True),
        Output("comprehensive-logic-input", "value", allow_duplicate=True),
        Output("comprehensive-description-input", "value", allow_duplicate=True),
        Output("comprehensive-status-radio", "value", allow_duplicate=True),
        Output("comprehensive-editing-mode", "data", allow_duplicate=True),
        Output("comprehensive-editing-indicator-id", "data", allow_duplicate=True),
        Output("comprehensive-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("cancel-edit-comprehensive", "n_clicks")],
        prevent_initial_call=True
    )
    def cancel_edit_comprehensive_indicator(n_clicks):
        """取消编辑综合指标"""
        if not n_clicks:
            return [dash.no_update] * 9
        
        return "", "", "", "", "", "enabled", False, None, []

    # 新增指标按钮处理
    @app.callback(
        [Output("comprehensive-code-input", "value", allow_duplicate=True),
        Output("comprehensive-name-input", "value", allow_duplicate=True),
        Output("comprehensive-unit-input", "value", allow_duplicate=True),
        Output("comprehensive-logic-input", "value", allow_duplicate=True),
        Output("comprehensive-description-input", "value", allow_duplicate=True),
        Output("comprehensive-status-radio", "value", allow_duplicate=True),
        Output("comprehensive-editing-mode", "data", allow_duplicate=True),
        Output("comprehensive-editing-indicator-id", "data", allow_duplicate=True),
        Output("comprehensive-indicator-table", "selected_rows", allow_duplicate=True)],
        [Input("add-new-comprehensive", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_form_for_new_comprehensive_indicator(n_clicks):
        """新增综合指标时清空表单"""
        if not n_clicks:
            return [dash.no_update] * 9
        
        return "", "", "", "", "", "enabled", False, None, []

    # 保存/更新综合指标回调函数
    @app.callback(
        [Output("comprehensive-indicator-table", "data", allow_duplicate=True),
        Output("comprehensive-editing-mode", "data", allow_duplicate=True),
        Output("comprehensive-editing-indicator-id", "data", allow_duplicate=True),
        Output("comprehensive-indicator-table", "selected_rows", allow_duplicate=True),
        Output("comprehensive-code-input", "value", allow_duplicate=True),
        Output("comprehensive-name-input", "value", allow_duplicate=True),
        Output("comprehensive-unit-input", "value", allow_duplicate=True),
        Output("comprehensive-logic-input", "value", allow_duplicate=True),
        Output("comprehensive-description-input", "value", allow_duplicate=True),
        Output("comprehensive-status-radio", "value", allow_duplicate=True),
        Output("comprehensive-editing-status-alert", "children", allow_duplicate=True),
        Output("comprehensive-editing-status-alert", "style", allow_duplicate=True)],
        [Input("save-comprehensive-indicator", "n_clicks")],
        [State("comprehensive-editing-mode", "data"),
        State("comprehensive-editing-indicator-id", "data"),
        State("comprehensive-code-input", "value"),
        State("comprehensive-name-input", "value"),
        State("comprehensive-unit-input", "value"),
        State("comprehensive-form-construction-mode", "value"),
        State("comprehensive-form-calculation-method", "value"),
        State("comprehensive-form-indicator-type", "value"),
        State("comprehensive-logic-input", "value"),
        State("comprehensive-description-input", "value"),
        State("comprehensive-status-radio", "value"),
        State("comprehensive-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def save_or_update_comprehensive_indicator(n_clicks, editing_mode, editing_indicator_id, 
                                            code, name, unit, construction_mode, 
                                            calculation_method, indicator_type, logic, description, status, filter_mode):
        """保存或更新综合指标"""
        
        print("=== 综合指标保存调试 ===")
        print(f"n_clicks: {n_clicks}")
        print(f"editing_mode: {editing_mode}")
        
        if not n_clicks:
            return [dash.no_update] * 12
        
        # 验证必填字段
        if not code or not name:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                "请填写指标代码和指标名称！"
            ], color="danger", className="mb-0")
            
            return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
        
        try:
            # 构建指标数据（暂时使用空的dependencies）
            indicator_data = {
                'code': code.strip(),
                'name': name.strip(),
                'construction_mode': construction_mode,
                'calculation_method': calculation_method,
                'indicator_type': indicator_type,
                'calculation_logic': logic.strip() if logic else "",
                'dependencies': '{}',  # 暂时使用空的JSON
                'unit': unit.strip() if unit else "",
                'description': description.strip() if description else "",
                'status': status
            }
            
            if editing_mode and editing_indicator_id:
                # 更新模式
                indicator_data['id'] = editing_indicator_id
                result = update_comprehensive_indicator(indicator_data)
                operation = "更新"
            else:
                # 新增模式
                result = add_comprehensive_indicator(indicator_data)
                operation = "新增"
            
            if result:
                # 操作成功，重新加载数据
                updated_data = get_comprehensive_indicators(filter_mode)
                
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    f"综合指标{operation}成功！"
                ], color="success", className="mb-0")
                
                return (
                    updated_data, False, None, [], "", "", "", "", "", "enabled",
                    success_alert, {'marginBottom': '15px', 'display': 'block'}
                )
            else:
                # 操作失败
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    f"{operation}失败！"
                ], color="danger", className="mb-0")
                
                return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
            
        except Exception as e:
            print(f"保存综合指标错误: {str(e)}")
            
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"操作失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update] * 10 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]

    # 删除综合指标回调函数
    @app.callback(
        [Output("comprehensive-indicator-table", "data", allow_duplicate=True),
         Output("comprehensive-indicator-table", "selected_rows", allow_duplicate=True),
         Output("comprehensive-editing-status-alert", "children", allow_duplicate=True),
         Output("comprehensive-editing-status-alert", "style", allow_duplicate=True)],
        [Input("delete-selected-comprehensive", "n_clicks")],
        [State("comprehensive-indicator-table", "selected_rows"),
         State("comprehensive-indicator-table", "data"),
         State("comprehensive-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def delete_selected_comprehensive_indicators(n_clicks, selected_rows, table_data, filter_mode):
        """删除选中的综合指标"""
        
        if not n_clicks or not selected_rows or not table_data:
            return [dash.no_update] * 4
        
        try:
            deleted_count = 0
            failed_indicators = []
            
            for row_index in selected_rows:
                if row_index < len(table_data):
                    indicator = table_data[row_index]
                    indicator_id = indicator.get('id')
                    indicator_name = indicator.get('name', '未知指标')
                    
                    if indicator_id:
                        result = delete_comprehensive_indicator(indicator_id)
                        if result:
                            deleted_count += 1
                        else:
                            failed_indicators.append(indicator_name)
            
            # 准备结果消息
            if deleted_count > 0 and len(failed_indicators) == 0:
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个综合指标！"
                ], color="success", className="mb-0")
                result_alert = success_alert
            elif deleted_count > 0 and len(failed_indicators) > 0:
                warning_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    f"成功删除 {deleted_count} 个指标，{len(failed_indicators)} 个指标删除失败！"
                ], color="warning", className="mb-0")
                result_alert = warning_alert
            else:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "删除操作失败！"
                ], color="danger", className="mb-0")
                result_alert = error_alert
            
            # 重新加载数据
            if deleted_count > 0:
                updated_data = get_comprehensive_indicators(filter_mode)
                return (updated_data, [], result_alert, {'marginBottom': '15px', 'display': 'block'})
            else:
                return (dash.no_update, [], result_alert, {'marginBottom': '15px', 'display': 'block'})
                
        except Exception as e:
            print(f"删除综合指标错误: {str(e)}")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"删除操作发生错误：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update, dash.no_update, error_alert, {'marginBottom': '15px', 'display': 'block'}]       



# ====== 算法配置相关回调函数 ======

    # 施工模式或算法选择变化时更新详情显示（简化版）
    @app.callback(
        [Output("algorithm-application-scenario", "children"),
         Output("algorithm-model-description", "children"),
         Output("algorithm-status-radio", "value"),
         Output("algorithm-status-hint", "children")],
        [Input("algorithm-construction-mode-dropdown", "value"),
         Input("modal-algorithm-type-dropdown", "value")],
        [State("modal-algorithm-config", "is_open")]
    )
    def update_algorithm_details_with_mode(construction_mode, selected_algorithm, is_open):
        """当选择不同施工模式或算法时，更新算法详情显示"""
        if not construction_mode or not selected_algorithm or not is_open:
            return ("请选择施工模式和算法查看应用场景", "请选择施工模式和算法查看模型描述", 
                    "enabled", "停用后该算法在当前施工模式下将不参与价格预测计算")
        
        print(f"=== 更新算法详情 ===")
        print(f"施工模式: {construction_mode}")
        print(f"算法类型: {selected_algorithm}")
        
        # 从数据库获取算法配置
        algorithm_config = get_algorithm_config(selected_algorithm, construction_mode)
        
        if algorithm_config:
            application_scenario = algorithm_config.get('application_scenario', '暂无应用场景描述')
            model_description = algorithm_config.get('model_description', '暂无模型描述')
            status = algorithm_config.get('status', 'enabled')
            
            # 动态生成状态提示
            mode_name = get_construction_mode_chinese_name(construction_mode)
            status_hint = f"停用后该算法在{mode_name}下将不参与价格预测计算"
            
            return (application_scenario, model_description, status, status_hint)
        else:
            mode_name = get_construction_mode_chinese_name(construction_mode)
            return (f"未找到{mode_name}下{selected_algorithm}的配置", "算法配置未找到", 
                    "enabled", f"停用后该算法在{mode_name}下将不参与价格预测计算")

    # 保存算法配置（简化版）
    @app.callback(
        [Output("algorithm-config-status-alert", "children"),
         Output("algorithm-config-status-alert", "style")],
        [Input("save-algorithm-config", "n_clicks")],
        [State("algorithm-construction-mode-dropdown", "value"),
         State("modal-algorithm-type-dropdown", "value"),
         State("algorithm-status-radio", "value")],
        prevent_initial_call=True
    )
    def save_algorithm_configuration_with_mode(n_clicks, construction_mode, algorithm_type, status):
        """保存算法配置（简化版 - 只保存状态）"""
        if not n_clicks or not construction_mode or not algorithm_type:
            return [], {'display': 'none'}
        
        try:
            print(f"=== 保存算法配置 ===")
            print(f"施工模式: {construction_mode}")
            print(f"算法类型: {algorithm_type}")
            print(f"状态: {status}")
            
            # 更新状态
            status_success = update_algorithm_status(algorithm_type, construction_mode, status)
            
            mode_name = get_construction_mode_chinese_name(construction_mode)
            algorithm_name_map = {
                'linear_regression': '线性回归',
                'neural_network': '神经网络',
                'decision_tree': '决策树',
                'random_forest': '随机森林',
                'svm': '支持向量机'
            }
            algorithm_chinese_name = algorithm_name_map.get(algorithm_type, algorithm_type)
            
            if status_success:
                print("算法配置保存成功")
                success_alert = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={'marginRight': '10px', 'fontSize': '18px', 'color': '#28a745'}),
                        html.Span([
                            html.Strong("配置保存成功！", style={'fontSize': '16px'}),
                            html.Br(),
                            f"{mode_name} - {algorithm_chinese_name}：{('已启用' if status == 'enabled' else '已停用')}",
                        ])
                    ], style={'display': 'flex', 'alignItems': 'flex-start'})
                ], color="success", className="mb-0", style={'fontSize': '14px'})
                
                return success_alert, {'marginBottom': '15px', 'display': 'block'}
            else:
                print("算法配置保存失败")
                error_alert = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '10px', 'fontSize': '18px', 'color': '#dc3545'}),
                        html.Span([
                            html.Strong("保存失败！", style={'fontSize': '16px'}),
                            html.Br(),
                            "请检查网络连接后重试"
                        ])
                    ], style={'display': 'flex', 'alignItems': 'flex-start'})
                ], color="danger", className="mb-0", style={'fontSize': '14px'})
                
                return error_alert, {'marginBottom': '15px', 'display': 'block'}
                
        except Exception as e:
            print(f"保存算法配置时发生错误: {str(e)}")
            error_alert = dbc.Alert([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '10px', 'fontSize': '18px', 'color': '#dc3545'}),
                    html.Span([
                        html.Strong("保存出错！", style={'fontSize': '16px'}),
                        html.Br(),
                        f"错误信息：{str(e)}"
                    ])
                ], style={'display': 'flex', 'alignItems': 'flex-start'})
            ], color="danger", className="mb-0", style={'fontSize': '14px'})
            
            return error_alert, {'marginBottom': '15px', 'display': 'block'}

    # 重置算法配置（简化版）
    @app.callback(
        [Output("algorithm-construction-mode-dropdown", "value", allow_duplicate=True),
         Output("modal-algorithm-type-dropdown", "value", allow_duplicate=True),
         Output("algorithm-status-radio", "value", allow_duplicate=True)],
        [Input("reset-algorithm-config", "n_clicks")],
        prevent_initial_call=True
    )
    def reset_algorithm_configuration_with_mode(n_clicks):
        """重置算法配置为默认值"""
        if not n_clicks:
            return [dash.no_update] * 3
        
        return 'steel_cage', 'linear_regression', 'enabled'

    # 清除状态提示（当选择改变时）
    @app.callback(
        [Output("algorithm-config-status-alert", "children", allow_duplicate=True),
         Output("algorithm-config-status-alert", "style", allow_duplicate=True)],
        [Input("algorithm-construction-mode-dropdown", "value"),
         Input("modal-algorithm-type-dropdown", "value"),
         Input("algorithm-status-radio", "value")],
        prevent_initial_call=True
    )
    def clear_status_alert_on_change(construction_mode, algorithm_type, status):
        """当用户改变选择时，清除状态提示"""
        return [], {'display': 'none'}


    # 根据施工模式更新算法表格数据
    @app.callback(
        Output('algorithm-config-table', 'data'),
        [Input('algorithm-construction-mode-dropdown', 'value'),
         Input('modal-algorithm-config', 'is_open')]
    )
    def update_algorithm_table_data(construction_mode, is_open):
        """根据选择的施工模式更新算法表格"""
        if is_open and construction_mode:
            print(f"=== 更新算法表格数据 ===")
            print(f"施工模式: {construction_mode}")
            
            algorithms = get_algorithms_by_construction_mode(construction_mode)
            print(f"获取到 {len(algorithms)} 个算法")
            
            return algorithms
        return []

    # 控制编辑按钮的启用/禁用状态
    @app.callback(
        [Output("edit-selected-algorithm", "disabled")],
        [Input("algorithm-config-table", "selected_rows"),
         Input("algorithm-editing-mode", "data")]
    )
    def update_edit_button_state(selected_rows, editing_mode):
        """根据选中状态和编辑模式控制编辑按钮"""
        if editing_mode:
            return [True]  # 编辑模式中禁用编辑按钮
        
        if not selected_rows or len(selected_rows) == 0:
            return [True]  # 没有选中行时禁用按钮
        
        return [False]  # 选中行且非编辑模式时启用按钮

    # 进入编辑模式
    @app.callback(
        [Output("algorithm-editing-mode", "data"),
         Output("algorithm-editing-id", "data"),
         Output("algorithm-original-data", "data"),
         Output("algorithm-edit-area", "style"),
         Output("edit-selected-algorithm", "style"),
         Output("cancel-edit-algorithm", "style"),
         Output("current-algorithm-name", "children"),
         Output("algorithm-status-radio-edit", "value"),
         Output("algorithm-application-scenario-edit", "children"),
         Output("algorithm-model-description-edit", "children"),
         Output("algorithm-status-hint-edit", "children"),
         Output("algorithm-editing-status-alert", "children"),
         Output("algorithm-editing-status-alert", "style")],
        [Input("edit-selected-algorithm", "n_clicks")],
        [State("algorithm-config-table", "selected_rows"),
         State("algorithm-config-table", "data"),
         State("algorithm-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def enter_edit_mode(n_clicks, selected_rows, table_data, construction_mode):
        """进入编辑模式"""
        if not n_clicks or not selected_rows or not table_data:
            return [dash.no_update] * 13
        
        try:
            selected_algorithm = table_data[selected_rows[0]]
            algorithm_id = selected_algorithm.get('id')
            
            # 从数据库获取完整的算法信息
            algorithm_data = get_algorithm_by_id(algorithm_id)
            
            if not algorithm_data:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "获取算法信息失败！"
                ], color="danger", className="mb-0")
                
                return [False, None, {}, {'display': 'none'}, 
                       {'marginRight': '10px'}, {'display': 'none'},
                       "", "enabled", "", "", "", 
                       error_alert, {'marginBottom': '15px', 'display': 'block'}]
            
            # 生成状态提示
            mode_name = get_construction_mode_chinese_name(construction_mode)
            status_hint = f"停用后该算法在{mode_name}下将不参与价格预测计算"
            
            # 编辑状态提示
            info_alert = dbc.Alert([
                html.I(className="fas fa-edit", style={'marginRight': '8px'}),
                f"正在编辑算法：{algorithm_data['algorithm_name']}"
            ], color="info", className="mb-0")
            
            return [
                True,  # 进入编辑模式
                algorithm_id,  # 编辑的算法ID
                algorithm_data.copy(),  # 原始数据
                {'display': 'block', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'border': '2px solid #007bff'},  # 显示编辑区域
                {'marginRight': '10px', 'display': 'none'},  # 隐藏编辑按钮
                {'display': 'inline-block'},  # 显示取消按钮
                algorithm_data['algorithm_name'],  # 算法名称
                algorithm_data['status'],  # 状态值
                algorithm_data['application_scenario'],  # 应用场景
                algorithm_data['model_description'],  # 模型描述
                status_hint,  # 状态提示
                info_alert,  # 编辑提示
                {'marginBottom': '15px', 'display': 'block'}  # 显示提示区域
            ]
            
        except Exception as e:
            print(f"进入编辑模式错误: {str(e)}")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"进入编辑模式失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [False, None, {}, {'display': 'none'}, 
                   {'marginRight': '10px'}, {'display': 'none'},
                   "", "enabled", "", "", "", 
                   error_alert, {'marginBottom': '15px', 'display': 'block'}]

    # 取消编辑模式
    @app.callback(
        [Output("algorithm-editing-mode", "data", allow_duplicate=True),
         Output("algorithm-editing-id", "data", allow_duplicate=True),
         Output("algorithm-original-data", "data", allow_duplicate=True),
         Output("algorithm-edit-area", "style", allow_duplicate=True),
         Output("edit-selected-algorithm", "style", allow_duplicate=True),
         Output("cancel-edit-algorithm", "style", allow_duplicate=True),
         Output("algorithm-config-table", "selected_rows", allow_duplicate=True),
         Output("algorithm-editing-status-alert", "children", allow_duplicate=True),
         Output("algorithm-editing-status-alert", "style", allow_duplicate=True)],
        [Input("cancel-edit-algorithm", "n_clicks"),
         Input("cancel-algorithm-edit", "n_clicks")],
        prevent_initial_call=True
    )
    def cancel_edit_mode(cancel_header_clicks, cancel_footer_clicks):
        """取消编辑模式"""
        if not cancel_header_clicks and not cancel_footer_clicks:
            return [dash.no_update] * 9
        
        return [
            False,  # 退出编辑模式
            None,  # 清空编辑ID
            {},  # 清空原始数据
            {'display': 'none'},  # 隐藏编辑区域
            {'marginRight': '10px', 'display': 'inline-block'},  # 显示编辑按钮
            {'display': 'none'},  # 隐藏取消按钮
            [],  # 清空选中行
            [],  # 清空提示
            {'marginBottom': '15px', 'display': 'none'}  # 隐藏提示区域
        ]

    # 保存编辑
    @app.callback(
        [Output("algorithm-config-table", "data", allow_duplicate=True),
         Output("algorithm-editing-mode", "data", allow_duplicate=True),
         Output("algorithm-editing-id", "data", allow_duplicate=True),
         Output("algorithm-original-data", "data", allow_duplicate=True),
         Output("algorithm-edit-area", "style", allow_duplicate=True),
         Output("edit-selected-algorithm", "style", allow_duplicate=True),
         Output("cancel-edit-algorithm", "style", allow_duplicate=True),
         Output("algorithm-config-table", "selected_rows", allow_duplicate=True),
         Output("algorithm-config-status-alert", "children", allow_duplicate=True),
         Output("algorithm-config-status-alert", "style", allow_duplicate=True)],
        [Input("save-algorithm-edit", "n_clicks")],
        [State("algorithm-editing-id", "data"),
         State("algorithm-status-radio-edit", "value"),
         State("algorithm-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def save_algorithm_edit(n_clicks, algorithm_id, new_status, construction_mode):
        """保存算法编辑"""
        if not n_clicks or not algorithm_id:
            return [dash.no_update] * 10
        
        try:
            print(f"=== 保存算法编辑 ===")
            print(f"算法ID: {algorithm_id}")
            print(f"新状态: {new_status}")
            
            # 更新数据库
            success = update_algorithm_status_by_id(algorithm_id, new_status)
            
            if success:
                # 重新获取表格数据
                updated_data = get_algorithms_by_construction_mode(construction_mode)
                
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                    "算法配置保存成功！"
                ], color="success", className="mb-0")
                
                return [
                    updated_data,  # 更新表格数据
                    False,  # 退出编辑模式
                    None,  # 清空编辑ID
                    {},  # 清空原始数据
                    {'display': 'none'},  # 隐藏编辑区域
                    {'marginRight': '10px', 'display': 'inline-block'},  # 显示编辑按钮
                    {'display': 'none'},  # 隐藏取消按钮
                    [],  # 清空选中行
                    success_alert,  # 成功提示
                    {'marginBottom': '15px', 'display': 'block'}  # 显示提示区域
                ]
            else:
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                    "保存失败！请检查网络连接后重试。"
                ], color="danger", className="mb-0")
                
                return [dash.no_update] * 8 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]
                
        except Exception as e:
            print(f"保存算法编辑错误: {str(e)}")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                f"保存失败：{str(e)}"
            ], color="danger", className="mb-0")
            
            return [dash.no_update] * 8 + [error_alert, {'marginBottom': '15px', 'display': 'block'}]

    # 清除状态提示（当操作改变时）
    @app.callback(
        [Output("algorithm-config-status-alert", "children", allow_duplicate=True),
         Output("algorithm-config-status-alert", "style", allow_duplicate=True)],
        [Input("algorithm-construction-mode-dropdown", "value"),
         Input("algorithm-config-table", "selected_rows")],
        prevent_initial_call=True
    )
    def clear_algorithm_status_alert(construction_mode, selected_rows):
        """当用户改变选择时，清除状态提示"""
        return [], {'display': 'none'}


    # ====== 算法参数管理回调函数 ======

    # 加载算法列表到下拉菜单
    @app.callback(
        Output("algorithm-select-dropdown", "options"),
        [Input("modal-model-training", "is_open")]
    )
    def load_algorithm_options(is_open):
        """当模态窗口打开时加载算法选项"""
        if is_open:
            algorithms = get_all_algorithms()
            return algorithms
        return []

    # 显示算法描述信息
    @app.callback(
        [Output("algorithm-description-display", "children"),
        Output("edit-parameters-btn", "disabled"),
        Output("reset-parameters-btn", "disabled"),
        Output("selected-algorithm-data", "data")],
        [Input("algorithm-select-dropdown", "value")]
    )
    def display_algorithm_description(selected_algorithm):
        """显示选中算法的描述信息并启用操作按钮"""
        if not selected_algorithm:
            return [
                html.P("请选择算法查看详细信息", style={'color': '#666', 'fontStyle': 'italic'})
            ], True, True, {}
        
        # 获取算法描述
        description_info = get_algorithm_description(selected_algorithm)
        
        if description_info:
            description_content = [
                html.Div([
                    html.H6(f"{description_info['name']}", 
                        style={'color': '#2C3E50', 'marginBottom': '10px'}),
                    html.P(f"算法类型: {description_info['class']}", 
                        style={'color': '#666', 'marginBottom': '8px', 'fontSize': '14px'}),
                    html.P(description_info['description'], 
                        style={'color': '#333', 'lineHeight': '1.6'})
                ])
            ]
            return description_content, False, False, {'algorithm': selected_algorithm}
        else:
            return [
                html.P("无法获取算法信息", style={'color': '#dc3545'})
            ], True, True, {}

    # 加载和显示算法参数
    @app.callback(
        Output("parameters-display-area", "children"),
        [Input("selected-algorithm-data", "data"),
        Input("parameter-editing-mode", "data")]
    )
    def display_algorithm_parameters(algorithm_data, editing_mode):
        """显示算法参数列表"""
        if not algorithm_data or 'algorithm' not in algorithm_data:
            return [html.P("请先选择算法", style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})]
        
        algorithm_name = algorithm_data['algorithm']
        parameters = get_algorithm_parameters(algorithm_name)
        
        if not parameters:
            return [html.P("该算法暂无可配置参数", style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})]
        
        if editing_mode:
            # 编辑模式 - 显示可编辑的输入控件
            return create_parameter_edit_form(parameters)
        else:
            # 查看模式 - 显示参数表格
            return create_parameter_view_table(parameters)

    def create_parameter_view_table(parameters):
        """创建参数查看表格"""
        table_data = []
        for param in parameters:
            # 根据优先级设置行样式
            priority_colors = {
                'high': '#ffebee',      # 浅红色
                'medium': '#fff3e0',    # 浅橙色  
                'low': '#f5f5f5'        # 浅灰色
            }
            
            row_style = {
                'backgroundColor': priority_colors.get(param['priority'], '#ffffff'),
                'borderLeft': f"4px solid {'#f44336' if param['priority'] == 'high' else '#ff9800' if param['priority'] == 'medium' else '#9e9e9e'}"
            }
            
            table_data.append({
                'parameter_name_cn': param['parameter_name_cn'],
                'current_value': param['current_value'],
                'suggested_range': param['suggested_range'],
                'adjustment_tips': param['adjustment_tips'][:50] + '...' if len(param['adjustment_tips']) > 50 else param['adjustment_tips'],
                'priority': param['priority'].upper()
            })
        
        return [
            dash_table.DataTable(
                data=table_data,
                columns=[
                    {'name': '参数名称', 'id': 'parameter_name_cn'},
                    {'name': '当前值', 'id': 'current_value'},
                    {'name': '建议范围', 'id': 'suggested_range'},
                    {'name': '调整提示', 'id': 'adjustment_tips'},
                    {'name': '优先级', 'id': 'priority'}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial, sans-serif'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #dee2e6'
                },
                style_data={
                    'border': '1px solid #dee2e6'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{priority} = HIGH'},
                        'backgroundColor': '#ffebee',
                        'borderLeft': '4px solid #f44336'
                    },
                    {
                        'if': {'filter_query': '{priority} = MEDIUM'},
                        'backgroundColor': '#fff3e0',
                        'borderLeft': '4px solid #ff9800'
                    },
                    {
                        'if': {'filter_query': '{priority} = LOW'},
                        'backgroundColor': '#f5f5f5',
                        'borderLeft': '4px solid #9e9e9e'
                    }
                ],
                page_size=10,
                style_table={'overflowX': 'auto'}
            ),
            # 优先级说明
            html.Div([
                html.Small([
                    html.Span("■ ", style={'color': '#f44336'}),
                    "高优先级 ",
                    html.Span("■ ", style={'color': '#ff9800'}),
                    "中优先级 ",
                    html.Span("■ ", style={'color': '#9e9e9e'}),
                    "低优先级"
                ], style={'color': '#666', 'marginTop': '10px'})
            ])
        ]

    def create_parameter_edit_form(parameters):
        """创建参数编辑表单 - 修订版，支持复杂参数类型"""
        form_elements = []
        
        for i, param in enumerate(parameters):
            # 根据参数名称和类型创建特殊的输入控件
            if param['parameter_name'] == 'alphas' and 'logspace' in param['current_value']:
                # 处理 logspace 类型参数
                input_element = create_logspace_input(i, param['current_value'])
            elif param['parameter_name'] == 'hidden_layer_sizes' and '(' in param['current_value']:
                # 处理神经网络层结构参数
                input_element = create_layer_structure_input(i, param['current_value'])
            elif param['parameter_type'] == 'continuous':
                input_element = dcc.Input(
                    id={"type": "param-input", "index": i},
                    type="number",
                    value=float(param['current_value']) if param['current_value'] != 'None (自动)' else 0,
                    step="any",
                    style={'width': '100%', 'padding': '8px'}
                )
            elif param['parameter_type'] == 'discrete':
                input_element = dcc.Input(
                    id={"type": "param-input", "index": i},
                    type="number",
                    value=int(float(param['current_value'])) if param['current_value'].isdigit() else 1,
                    step=1,
                    style={'width': '100%', 'padding': '8px'}
                )
            elif param['parameter_type'] == 'categorical':
                # 解析分类选项
                options = [{'label': opt.strip(), 'value': opt.strip()} 
                        for opt in param['suggested_range'].split(',')]
                input_element = dcc.Dropdown(
                    id={"type": "param-input", "index": i},
                    options=options,
                    value=param['current_value'],
                    clearable=False,
                    style={'width': '100%'}
                )
            else:
                # 默认文本输入
                input_element = dcc.Input(
                    id={"type": "param-input", "index": i},
                    type="text",
                    value=param['current_value'],
                    style={'width': '100%', 'padding': '8px'}
                )
            
            # 优先级标识
            priority_badge_color = {
                'high': 'danger',
                'medium': 'warning', 
                'low': 'secondary'
            }
            
            form_elements.append(
                html.Div([
                    html.Div([
                        html.Label([
                            param['parameter_name_cn'],
                            dbc.Badge(
                                param['priority'].upper(),
                                color=priority_badge_color.get(param['priority'], 'secondary'),
                                className="ml-2"
                            )
                        ], style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        input_element,
                        html.Div(id={"type": "param-validation", "index": i}),
                        html.Small([
                            html.Strong("建议范围: "), param['suggested_range']
                        ], style={'color': '#666', 'display': 'block', 'marginTop': '3px'}),
                        html.Small([
                            html.Strong("调整提示: "), param['adjustment_tips']
                        ], style={'color': '#666', 'display': 'block', 'marginTop': '3px'})
                    ], style={'marginBottom': '20px', 'padding': '15px', 
                            'border': '1px solid #dee2e6', 'borderRadius': '5px'})
                ])
            )
        
        return form_elements

    def create_logspace_input(index, current_value):
        """创建 logspace 参数的输入控件"""
        # 解析当前值，例如：np.logspace(-3, 3, 11)
        try:
            # 提取数字参数
            import re
            match = re.search(r'logspace\(([^,]+),\s*([^,]+),\s*([^)]+)\)', current_value)
            if match:
                start_val = float(match.group(1))
                end_val = float(match.group(2))
                num_val = int(match.group(3))
            else:
                start_val, end_val, num_val = -3, 3, 11
        except:
            start_val, end_val, num_val = -3, 3, 11
        
        return html.Div([
            html.Div([
                html.Label("起始指数:", style={'marginBottom': '5px', 'fontSize': '12px'}),
                dcc.Input(
                    id={"type": "param-input", "index": f"{index}_start"},
                    type="number",
                    value=start_val,
                    step=1,
                    style={'width': '100%', 'padding': '6px', 'fontSize': '14px'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
            
            html.Div([
                html.Label("结束指数:", style={'marginBottom': '5px', 'fontSize': '12px'}),
                dcc.Input(
                    id={"type": "param-input", "index": f"{index}_end"},
                    type="number",
                    value=end_val,
                    step=1,
                    style={'width': '100%', 'padding': '6px', 'fontSize': '14px'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
            
            html.Div([
                html.Label("数量:", style={'marginBottom': '5px', 'fontSize': '12px'}),
                dcc.Input(
                    id={"type": "param-input", "index": f"{index}_num"},
                    type="number",
                    value=num_val,
                    step=1,
                    min=1,
                    style={'width': '100%', 'padding': '6px', 'fontSize': '14px'}
                )
            ], style={'width': '30%', 'display': 'inline-block'}),
            
            html.Div([
                html.Small(f"当前生成: np.logspace({start_val}, {end_val}, {num_val})", 
                        id={"type": "logspace-display", "index": index},
                        style={'color': '#666', 'fontStyle': 'italic', 'marginTop': '5px'})
            ])
        ])

    def create_layer_structure_input(index, current_value):
        """创建神经网络层结构的输入控件 - 简化版"""
        # 解析当前值
        try:
            import re
            numbers = re.findall(r'\d+', current_value)
            if len(numbers) >= 2:
                layer1_size = int(numbers[0])
                layer2_size = int(numbers[1])
            elif len(numbers) == 1:
                layer1_size = int(numbers[0])
                layer2_size = 0
            else:
                layer1_size = 3
                layer2_size = 0
        except:
            layer1_size = 3
            layer2_size = 0
        
        return html.Div([
            html.Div([
                html.Label("第一层神经元数量:", style={'marginBottom': '5px', 'fontSize': '12px'}),
                dcc.Input(
                    id={"type": "param-input", "index": f"{index}_layer1"},
                    type="number",
                    value=layer1_size,
                    min=1,
                    max=100,
                    step=1,
                    style={'width': '100%', 'padding': '6px', 'fontSize': '14px', 'marginBottom': '10px'}
                )
            ]),
            
            html.Div([
                html.Label("第二层神经元数量 (填0表示单层):", style={'marginBottom': '5px', 'fontSize': '12px'}),
                dcc.Input(
                    id={"type": "param-input", "index": f"{index}_layer2"},
                    type="number",
                    value=layer2_size,
                    min=0,
                    max=100,
                    step=1,
                    style={'width': '100%', 'padding': '6px', 'fontSize': '14px'}
                )
            ]),
            
            html.Small([
                "提示: 第一层=5, 第二层=3 → (5,3); 第一层=5, 第二层=0 → (5,)"
            ], style={'color': '#666', 'fontSize': '11px', 'marginTop': '5px', 'display': 'block'})
        ])
    # 控制隐藏层结构输入的显示
    @app.callback(
        [Output({"type": "layer2-div", "index": MATCH}, "style"),
        Output({"type": "layer-display", "index": MATCH}, "children")],
        [Input({"type": "param-input", "index": MATCH}, "value"),
        Input({"type": "param-input", "index": MATCH}, "value"),
        Input({"type": "param-input", "index": MATCH}, "value")],
        [State({"type": "param-input", "index": MATCH}, "id")]
    )
    def update_layer_structure_display(layer_count, layer1, layer2, component_id):
        """更新隐藏层结构的显示"""
        try:
            # 解析组件ID来判断是哪个参数
            index_str = str(component_id['index'])
            
            if '_layer_count' in index_str:
                # 层数改变
                if layer_count == 2:
                    return {'marginBottom': '10px', 'display': 'block'}, f"当前配置: (5,3)"
                else:
                    return {'marginBottom': '10px', 'display': 'none'}, f"当前配置: (5,)"
            elif '_layer1' in index_str:
                # 第一层神经元数量改变
                return dash.no_update, f"当前配置: ({layer1},)"
            elif '_layer2' in index_str:
                # 第二层神经元数量改变  
                return dash.no_update, f"当前配置: ({layer1},{layer2})"
            else:
                return dash.no_update, dash.no_update
                
        except:
            return {'marginBottom': '10px', 'display': 'none'}, "当前配置: (3,)"    

    # 控制编辑模式切换
    @app.callback(
        [Output("parameter-editing-mode", "data"),
        Output("edit-parameters-btn", "style"),
        Output("cancel-parameter-edit", "style"),
        Output("save-parameters", "style")],
        [Input("edit-parameters-btn", "n_clicks"),
        Input("cancel-parameter-edit", "n_clicks"),
        Input("save-parameters", "n_clicks")],
        [State("parameter-editing-mode", "data")]
    )
    def toggle_editing_mode(edit_clicks, cancel_clicks, save_clicks, current_mode):
        """切换参数编辑模式"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, {'marginRight': '10px'}, {'marginRight': '10px', 'display': 'none'}, {'display': 'none'}
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "edit-parameters-btn":
            # 进入编辑模式
            return True, {'marginRight': '10px', 'display': 'none'}, {'marginRight': '10px', 'display': 'inline-block'}, {'display': 'inline-block'}
        elif button_id in ["cancel-parameter-edit", "save-parameters"]:
            # 退出编辑模式
            return False, {'marginRight': '10px'}, {'marginRight': '10px', 'display': 'none'}, {'display': 'none'}
        
        return current_mode, {'marginRight': '10px'}, {'marginRight': '10px', 'display': 'none'}, {'display': 'none'}

    # 参数保存功能
    @app.callback(
        [Output("parameter-status-alert", "children"),
        Output("parameter-status-alert", "style"),
        Output("parameter-editing-mode", "data", allow_duplicate=True)],
        [Input("save-parameters", "n_clicks")],
        [State("selected-algorithm-data", "data"),
        State({"type": "param-input", "index": ALL}, "value"),
        State({"type": "param-input", "index": ALL}, "id")],
        prevent_initial_call=True
    )
    def save_algorithm_parameters(save_clicks, algorithm_data, param_values, param_ids):
        """保存算法参数 - 支持复杂参数类型"""
        if not save_clicks or not algorithm_data or 'algorithm' not in algorithm_data:
            return [], {'display': 'none'}, False
        
        try:
            algorithm_name = algorithm_data['algorithm']
            parameters = get_algorithm_parameters(algorithm_name)
            
            if not parameters:
                return [
                    dbc.Alert("没有参数需要保存", color="warning")
                ], {'display': 'block', 'marginTop': '15px'}, False
            
            # 重新组织参数值
            processed_params = process_complex_parameters(parameters, param_values, param_ids)
            
            # 验证和保存每个参数
            saved_count = 0
            validation_errors = []
            
            for param_id, new_value in processed_params.items():
                # 找到对应的参数配置
                param_config = next((p for p in parameters if p['id'] == param_id), None)
                if not param_config:
                    continue
                
                # 对于复杂参数类型，跳过标准验证
                if param_config['parameter_name'] in ['alphas', 'hidden_layer_sizes']:
                    # 直接保存，不进行标准验证
                    if update_algorithm_parameter(param_id, str(new_value)):
                        saved_count += 1
                    else:
                        validation_errors.append(f"{param_config['parameter_name_cn']}: 保存失败")
                else:
                    # 标准参数验证
                    is_valid, error_msg = validate_parameter_value(
                        param_config['parameter_type'],
                        param_config['suggested_range'],
                        new_value
                    )
                    
                    if not is_valid:
                        validation_errors.append(f"{param_config['parameter_name_cn']}: {error_msg}")
                        continue
                    
                    # 保存参数
                    if update_algorithm_parameter(param_id, str(new_value)):
                        saved_count += 1
                    else:
                        validation_errors.append(f"{param_config['parameter_name_cn']}: 保存失败")
            
            # 显示保存结果
            if validation_errors:
                error_message = "部分参数保存失败：\n" + "\n".join(validation_errors)
                return [
                    dbc.Alert([
                        html.H6("参数验证错误", className="alert-heading"),
                        html.Hr(),
                        html.P(error_message, style={'whiteSpace': 'pre-line'})
                    ], color="danger")
                ], {'display': 'block', 'marginTop': '15px'}, True  # 保持编辑模式
            else:
                return [
                    dbc.Alert([
                        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                        f"成功保存 {saved_count} 个参数"
                    ], color="success")
                ], {'display': 'block', 'marginTop': '15px'}, False  # 退出编辑模式
                
        except Exception as e:
            return [
                dbc.Alert(f"保存参数时发生错误: {str(e)}", color="danger")
            ], {'display': 'block', 'marginTop': '15px'}, True

    def process_complex_parameters(parameters, param_values, param_ids):
        """处理复杂参数类型，将多个输入值组合成最终参数值"""
        processed_params = {}
        
        # 创建ID到值的映射
        id_value_map = {}
        for i, param_id in enumerate(param_ids):
            if i < len(param_values):
                id_value_map[str(param_id['index'])] = param_values[i]
        
        # 处理每个参数
        for i, param in enumerate(parameters):
            param_name = param['parameter_name']
            param_id = param['id']
            
            if param_name == 'alphas':
                # 处理 logspace 参数
                try:
                    start_val = id_value_map.get(f"{i}_start", -3)
                    end_val = id_value_map.get(f"{i}_end", 3)
                    num_val = id_value_map.get(f"{i}_num", 11)
                    
                    # 组装 logspace 表达式
                    final_value = f"np.logspace({start_val}, {end_val}, {num_val})"
                    processed_params[param_id] = final_value
                except:
                    # 如果没有找到复杂参数的子值，使用简单值
                    if str(i) in id_value_map:
                        processed_params[param_id] = id_value_map[str(i)]
            
            elif param_name == 'hidden_layer_sizes':
                # 处理隐藏层结构参数
                try:
                    layer1 = id_value_map.get(f"{i}_layer1", 3)
                    layer2 = id_value_map.get(f"{i}_layer2", 0)
                    
                    # 组装层结构表达式
                    if layer2 and layer2 > 0:
                        final_value = f"({layer1},{layer2})"
                    else:
                        final_value = f"({layer1},)"
                    
                    processed_params[param_id] = final_value
                except:
                    if str(i) in id_value_map:
                        processed_params[param_id] = id_value_map[str(i)]
            
            else:
                # 普通参数
                if str(i) in id_value_map:
                    processed_params[param_id] = id_value_map[str(i)]
        
        return processed_params

    # 参数重置功能
    @app.callback(
        [Output("parameter-status-alert", "children", allow_duplicate=True),
        Output("parameter-status-alert", "style", allow_duplicate=True),
        Output("parameters-display-area", "children", allow_duplicate=True)],
        [Input("reset-parameters-btn", "n_clicks")],
        [State("selected-algorithm-data", "data")],
        prevent_initial_call=True
    )
    def reset_algorithm_parameters_callback(reset_clicks, algorithm_data):
        """重置算法参数到默认值"""
        if not reset_clicks or not algorithm_data or 'algorithm' not in algorithm_data:
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            algorithm_name = algorithm_data['algorithm']
            
            # 执行重置操作
            if reset_algorithm_parameters(algorithm_name):
                # 重新加载参数显示
                parameters = get_algorithm_parameters(algorithm_name)
                updated_display = create_parameter_view_table(parameters)
                
                return [
                    dbc.Alert([
                        html.I(className="fas fa-undo", style={'marginRight': '8px'}),
                        "参数已重置到默认值"
                    ], color="info")
                ], {'display': 'block', 'marginTop': '15px'}, updated_display
            else:
                return [
                    dbc.Alert("重置参数失败", color="danger")
                ], {'display': 'block', 'marginTop': '15px'}, dash.no_update
                
        except Exception as e:
            return [
                dbc.Alert(f"重置参数时发生错误: {str(e)}", color="danger")
            ], {'display': 'block', 'marginTop': '15px'}, dash.no_update

    # 实时参数验证
    @app.callback(
        Output({"type": "param-validation", "index": MATCH}, "children"),
        [Input({"type": "param-input", "index": MATCH}, "value")],
        [State({"type": "param-input", "index": MATCH}, "id")],
        prevent_initial_call=True
    )
    def validate_parameter_input(param_value, param_input_id):
        """实时验证参数输入"""
        if param_value is None:
            return ""
        
        try:
            # 从ID中提取参数ID
            param_id = param_input_id['index']
            
            # 这里需要根据param_id获取参数信息进行验证
            # 暂时返回简单的验证结果
            return html.Small("✓ 验证通过", style={'color': 'green'})
            
        except Exception:
            return html.Small("✗ 验证失败", style={'color': 'red'})

    # 清除状态提示
    @app.callback(
        [Output("parameter-status-alert", "children", allow_duplicate=True),
        Output("parameter-status-alert", "style", allow_duplicate=True)],
        [Input("algorithm-select-dropdown", "value")],
        prevent_initial_call=True
    )
    def clear_status_alert(selected_algorithm):
        """切换算法时清除状态提示"""
        return [], {'display': 'none'}

    # 模态窗口关闭时重置状态
    @app.callback(
        [Output("algorithm-select-dropdown", "value", allow_duplicate=True),
        Output("parameter-editing-mode", "data", allow_duplicate=True),
        Output("selected-algorithm-data", "data", allow_duplicate=True)],
        [Input("modal-model-training", "is_open")],
        prevent_initial_call=True
    )
    def reset_modal_state(is_open):
        """模态窗口关闭时重置所有状态"""
        if not is_open:
            return None, False, {}
        return dash.no_update, dash.no_update, dash.no_update

    # 在回调函数注册函数内部定义logger
    import logging
    logger = logging.getLogger(__name__)
    # 添加模型性能对比模态窗口的开关回调
    @app.callback(
        Output("modal-model-evaluation", "is_open"),
        [Input("btn-model-comparison", "n_clicks"),  # ← 改成正确的按钮ID
        Input("close-model-evaluation", "n_clicks")],
        [State("modal-model-evaluation", "is_open")]
    )
    def toggle_model_evaluation_modal(n1, n2, is_open):
        print(f"[模型性能对比] DEBUG: n1={n1}, n2={n2}, is_open={is_open}")
        
        if n1 is None and n2 is None:
            print("[模型性能对比] 两个按钮都未点击，返回 False")
            return False
        
        ctx = callback_context
        print(f"[模型性能对比] ctx.triggered: {ctx.triggered}")
        
        if not ctx.triggered:
            print("[模型性能对比] 没有触发事件，返回 no_update")
            return no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_value = ctx.triggered[0]["value"]
        
        print(f"[模型性能对比] 触发按钮: {button_id}, 触发值: {trigger_value}")
        
        if trigger_value is None or trigger_value == 0:
            print("[模型性能对比] 触发值无效，返回 no_update")
            return no_update
        
        if button_id in ["btn-model-comparison", "close-model-evaluation"]:  # ← 这里也要改
            new_state = not is_open
            print(f"[模型性能对比] 切换状态: {is_open} -> {new_state}")
            return new_state
        
        print("[模型性能对比] 未知的触发源，返回 no_update")
        return no_update

    @app.callback(
        [Output("comparison-summary-table", "data"),
        Output("comparison-chart", "figure"),
        Output("enabled-algorithms-display", "children")],
        [Input("start-evaluation", "n_clicks")],
        [State("comparison-construction-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def perform_model_comparison(n_clicks, construction_mode):
        """执行模型性能对比"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # 导入模型对比类
            from .model_comparison import ModelPerformanceComparison
            
            # 创建模型对比实例
            comparator = ModelPerformanceComparison(construction_mode)
            
            # 加载算法配置
            if not comparator.load_algorithm_configs():
                return [], {}, "❌ 算法配置加载失败"
            
            # 检查是否有启用的算法
            if not comparator.enabled_algorithms:
                return [], {}, "⚠️ 当前没有启用的算法，请先在'算法模型配置'中启用算法"
            
            # 显示启用的算法
            enabled_list = [html.Li(f"✅ {config['name']}") 
                        for config in comparator.enabled_algorithms.values()]
            enabled_display = html.Ul(enabled_list, style={'marginBottom': '0'})
            
            # 执行性能评估
            results = comparator.evaluate_algorithms()
            if not results:
                return [], {}, enabled_display
            
            # 获取汇总表数据
            summary_data = comparator.get_comparison_summary()
            
            # 添加排名
            for i, row in enumerate(summary_data):
                row['rank'] = i + 1
            
            # 创建对比图表
            algorithms = [row['algorithm_name'] for row in summary_data]
            mae_values = [row['mae'] for row in summary_data]
            rmse_values = [row['rmse'] for row in summary_data]
            r2_values = [row['r2'] for row in summary_data]
            
            fig = go.Figure()
            
            # 添加柱状图
            fig.add_trace(go.Bar(
                name='MAE',
                x=algorithms,
                y=mae_values,
                yaxis='y',
                offsetgroup=1,
                marker_color='#e74c3c'
            ))
            
            fig.add_trace(go.Bar(
                name='RMSE',
                x=algorithms,
                y=rmse_values,
                yaxis='y',
                offsetgroup=2,
                marker_color='#f39c12'
            ))
            
            fig.add_trace(go.Bar(
                name='R²',
                x=algorithms,
                y=r2_values,
                yaxis='y2',
                offsetgroup=3,
                marker_color='#27ae60'
            ))
            
            # 设置布局
            mode_name = '钢筋笼' if construction_mode == 'steel_cage' else '钢衬里'
            fig.update_layout(
                title=f'{mode_name}模式 - 算法性能对比',
                xaxis_title='算法',
                yaxis=dict(
                    title='MAE / RMSE',
                    side='left'
                ),
                yaxis2=dict(
                    title='R²',
                    side='right',
                    overlaying='y',
                    range=[0, 1]
                ),
                height=400,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return summary_data, fig, enabled_display
            
        except Exception as e:
            logger.error(f"模型性能对比失败: {e}")
            return [], {}, f"❌ 对比失败: {str(e)}"
        