"""数据库查询模块"""
import mysql.connector
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(
            host='localhost',      # 直接使用字面值或从环境变量获取
            user='dash',          # 数据库用户名
            password='123456',    # 数据库密码
            database='dash_project'# 数据库名
        )
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        raise

def search_indicators(mode: str, search_term: str) -> List[Dict]:
    """
    搜索指标
    Args:
        mode: 施工模式 ('steel_cage' 或 'steel_lining')
        search_term: 搜索关键词
    Returns:
        匹配的指标列表
    """
    table = 'price_baseline_1' if mode == 'steel_cage' else 'price_baseline_2'
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = f"""
        SELECT 
            parameter_category as name,
            sequence_number as code,
            project as project_name,
            unit,
            modular_labor_unit_price as labor_price,
            modular_material_unit_price as material_price,
            modular_machinery_unit_price as machinery_price,
            total_price
        FROM {table}
        WHERE parameter_category LIKE %s
        LIMIT 10
        """
        # OR sequence_number LIKE %s OR project LIKE %s
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern,))
        results = cursor.fetchall()
        
        # 处理结果，确保所有价格字段都是浮点数
        processed_results = []
        for row in results:
            processed_row = {
                'id': row['code'],  # 使用sequence_number作为ID
                'name': row['name'],
                'code': row['code'],
                'project_name': row['project_name'],
                'unit': row['unit'],
                'unit_prices': {
                    'labor': float(row['labor_price'] or 0),
                    'material': float(row['material_price'] or 0),
                    'machinery': float(row['machinery_price'] or 0)
                },
                'total_price': float(row['total_price'] or 0)
            }
            processed_results.append(processed_row)
        
        cursor.close()
        conn.close()
        
        return processed_results
        
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return []

def save_parameters(project_id: int, project_name: str, parameters_data: List[Dict[str, Any]]) -> bool:
    """
    保存参数信息到parameter_info表
    Args:
        project_id: 项目ID
        project_name: 项目名称
        parameters_data: 参数列表，每个参数是一个字典，包含以下字段：
            - name: 参数名称
            - category: 参数类型
            - unit: 单位
            - quantity: 数量
            - unit_prices: 包含各种单价的字典
    Returns:
        bool: 保存是否成功
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取最大的parameter_id
        cursor.execute("SELECT MAX(parameter_id) FROM parameter_info")
        result = cursor.fetchone()
        next_param_id = 1 if result[0] is None else result[0] + 1

        for param in parameters_data:
            # 生成唯一参数ID（可以根据需要修改生成规则）
            param_unique_id = f"P{next_param_id:04d}"
            
            query = """
            INSERT INTO parameter_info (
                parameter_id, project_id, project_name, parameter_unique_id,
                parameter_name, parameter_type, parameter_value, unit,
                remarks, direct_labor_unit_price, direct_material_unit_price,
                direct_machinery_unit_price, modular_labor_unit_price,
                modular_material_unit_price, modular_machinery_unit_price
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                next_param_id,
                project_id,
                project_name,
                param_unique_id,
                param['name'],
                param.get('category', ''),  # 参数类型
                float(param.get('quantity', 0)),  # 参数值（数量）
                param.get('unit', ''),
                '',  # remarks，可以根据需要添加
                param['unit_prices'].get('direct_labor', 0),
                param['unit_prices'].get('direct_material', 0),
                param['unit_prices'].get('direct_machinery', 0),
                param['unit_prices'].get('labor', 0),
                param['unit_prices'].get('material', 0),
                param['unit_prices'].get('machinery', 0)
            )
            
            cursor.execute(query, values)
            next_param_id += 1

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if conn:
            conn.rollback()
        raise Exception(f"参数保存失败，数据库错误: {err}")
    except Exception as e:
        print(f"保存参数信息失败: {str(e)}")
        if conn:
            conn.rollback()
        raise Exception(f"参数保存失败: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

def save_project(project_data: Dict[str, Any]) -> Optional[int]:
    """
    保存项目信息到project_info表
    Args:
        project_data: 包含项目信息的字典，需要包含以下字段：
            - project_name: 项目名称
            - project_type: 项目类型
            - project_quantity: 工程量
            - unit: 单位
            - normal_construction_days: 常规施工工期
            - modular_construction_days: 模块化施工工期
            - remarks: 备注
    Returns:
        Optional[int]: 成功时返回新创建的project_id，失败时返回None
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查找最大的project_id
        cursor.execute("SELECT MAX(project_id) FROM project_info")
        result = cursor.fetchone()
        next_id = 701 if result[0] is None else max(701, result[0] + 1)

        query = """
        INSERT INTO project_info (
            project_id, project_name, project_type, project_quantity,
            unit, normal_construction_days, modular_construction_days,
            remarks, create_time
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        values = (
            next_id,
            project_data['project_name'],
            project_data['project_type'],
            project_data['project_quantity'],
            project_data['unit'],
            project_data['normal_construction_days'],
            project_data['modular_construction_days'],
            project_data['remarks'],
            datetime.now()
        )
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        return next_id
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if conn:
            conn.rollback()
        raise Exception(f"数据库操作失败: {err}")
    except Exception as e:
        print(f"保存项目信息失败: {str(e)}")
        if conn:
            conn.rollback()
        raise Exception(f"保存项目信息失败: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_indicator_details(mode: str, indicator_id: int) -> Optional[Dict]:
    """
    获取指标详细信息
    Args:
        mode: 施工模式
        indicator_id: 指标ID
    Returns:
        指标详细信息
    """
    table = 'price_baseline_1' if mode == 'steel_cage' else 'price_baseline_2'
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = f"""
        SELECT 
            project as name,
            sequence_number as code,
            parameter_category as category,
            unit,
            modular_labor_unit_price as labor_unit_price,
            modular_labor_quantity as labor_quantity,
            modular_labor_total as labor_cost,
            modular_material_unit_price as material_unit_price,
            modular_material_quantity as material_quantity,
            modular_material_total as material_cost,
            modular_machinery_unit_price as equipment_unit_price,
            modular_machinery_quantity as equipment_quantity,
            modular_machinery_total as equipment_cost,
            total_price
        FROM {table}
        WHERE sequence_number = %s
        """
        
        cursor.execute(query, (indicator_id,))
        row = cursor.fetchone()
        
        if row:
            # 处理结果，转换为适当的格式
            result = {
                'id': row['code'],
                'name': row['name'],  # project name
                'parameter_category': row['category'],  # parameter_category
                'code': row['code'],
                'unit': row['unit'],
                'unit_prices': {
                    'labor': float(row['labor_unit_price'] or 0),
                    'material': float(row['material_unit_price'] or 0),
                    'machinery': float(row['equipment_unit_price'] or 0)
                },
                'quantities': {
                    'labor': float(row['labor_quantity'] or 0),
                    'material': float(row['material_quantity'] or 0),
                    'machinery': float(row['equipment_quantity'] or 0)
                },
                'totals': {
                    'labor': float(row['labor_cost'] or 0),
                    'material': float(row['material_cost'] or 0),
                    'machinery': float(row['equipment_cost'] or 0),
                    'total': float(row['total_price'] or 0)
                }
            }
        else:
            result = None
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return None
