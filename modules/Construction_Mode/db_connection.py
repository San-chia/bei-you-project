import mysql.connector
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import uuid
# 在现有导入语句后添加
import sys
import os

# 添加翻译模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dataManagement'))

try:
    from translation import (
        translate_field_name, 
        translate_table_name, 
        reverse_translate_field_name, 
        reverse_translate_table_name,
        translate_dataframe_columns
    )
except ImportError as e:
    print(f"警告：无法导入翻译模块: {e}")
    # 提供备用函数
    def translate_dataframe_columns(df):
        return df
    
# MySQL数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名
    'charset': 'utf8mb4',
    'autocommit': True  # 默认启用自动提交
}

def get_connection():
    """获取MySQL数据库连接"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        raise

def get_connection_diy():
    """获取MySQL数据库连接（DIY版本）"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        raise

def get_price_data(mode, param_category=None):
    """
    获取特定模式和参数类别的价格数据
    
    Args:
        mode (str): 施工模式
        param_category (str, optional): 参数类别，可选
        
    Returns:
        pandas.DataFrame: 价格数据（列名已翻译为中文显示）
    """
    conn = get_connection()
    
    if param_category:
        query = """
        SELECT * FROM `construction_parameter_table` 
        WHERE `mode` = %s AND `parameter_category` = %s
        ORDER BY `sequence_number`
        """
        df = pd.read_sql(query, conn, params=(mode, param_category))
    else:
        query = """
        SELECT * FROM `construction_parameter_table` 
        WHERE `mode` = %s
        ORDER BY `sequence_number`
        """
        df = pd.read_sql(query, conn, params=(mode,))
    
    conn.close()
    
    # 翻译列名为中文显示
    return translate_dataframe_columns(df)

def calculate_cost(mode, params_dict, others):
    """
    计算特定模式和参数的成本
    
    Args:
        mode (str): 施工模式
        params_dict (dict): 参数值字典，格式为 {工程参数: 数量}
        others (dict): 其他费用
        
    Returns:
        dict: 包含直接施工和模块化施工成本明细的字典
    """
    conn = get_connection()
    
    # 模式名称映射 - 将传入的带空格的中文模式名映射为数据库中的实际值
    mode_mapping = {
        " 钢筋笼施工模式 ": "钢筋笼施工模式",
        " 钢筋笼+钢覆面施工模式 ": "钢筋笼+钢覆面施工模式", 
        " 叠合板模块化施工(设备室顶板) ": "叠合板模块化施工(设备室顶板)",
        " 叠合板模块化施工(C403、C409) ": "叠合板模块化施工(C403、C409)",
        " 叠合板模块化施工(C404) ": "叠合板模块化施工(C404)",
        " 叠合板模块化施工(共用) ": "叠合板模块化施工(共用)",
        "钢衬里施工模式": "钢衬里施工模式"
    }
    
    # 去除首尾空格并转换模式名称
    clean_mode = mode.strip()
    actual_mode = mode_mapping.get(mode, clean_mode)
    
    print(f"原始模式: '{mode}' -> 清理后: '{clean_mode}' -> 实际模式: '{actual_mode}'")
    
    # 初始化结果
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
        "明细": []
    }
    
    # 逐个处理每个参数
    for param, quantity in params_dict.items():
        # 清理参数名称：去除首尾空格
        clean_param = param.strip()
        print(f"查找参数: '{clean_param}' 在模式: '{actual_mode}' 中")
        
        # 查找该参数的价格数据 - 使用英文表名和字段名
        query = """
        SELECT * FROM `construction_parameter_table`
        WHERE `mode` = %s AND TRIM(`engineering_parameter`) = %s
        """
        
        try:
            param_df = pd.read_sql(query, conn, params=(actual_mode, clean_param))
            
            if param_df.empty:
                print(f"精确匹配失败，尝试模糊匹配参数: '{clean_param}'")
                # 尝试模糊匹配 - 标准处理方式
                fuzzy_query = """
                SELECT * FROM `construction_parameter_table`
                WHERE `mode` = %s AND TRIM(`engineering_parameter`) LIKE %s
                """
                param_df = pd.read_sql(fuzzy_query, conn, params=(actual_mode, f'%{clean_param}%'))
                
                if param_df.empty:
                    # 最后尝试只通过参数名匹配（忽略模式）
                    param_only_query = """
                    SELECT * FROM `construction_parameter_table`
                    WHERE TRIM(`engineering_parameter`) = %s
                    LIMIT 1
                    """
                    param_df = pd.read_sql(param_only_query, conn, params=(clean_param,))
                    
                    if param_df.empty:
                        print(f"警告: 未找到参数 '{clean_param}' 的价格数据")
                        continue
                    else:
                        print(f"通过参数名匹配找到: '{clean_param}'")
                else:
                    print(f"通过模糊匹配找到: '{clean_param}'")
            else:
                print(f"精确匹配成功: '{clean_param}'")
        
        except Exception as e:
            print(f"查询参数 '{param}' 时出错: {e}")
            continue
        
        if not param_df.empty:
            row = param_df.iloc[0]
            
            try:
                # 确保数量是有效数值
                # 移除字符串两端的空白，并将空字符串转换为0
                quantity_str = str(quantity).strip() if quantity is not None else ""
                quantity = float(quantity_str) if quantity_str else 0
                
                # 安全地获取单价，确保它们是数值
                def safe_float(value):
                    """安全地将值转换为浮点数"""
                    if pd.isna(value) or value is None:
                        return 0.0
                    try:
                        # 如果是字符串，先去除空白
                        if isinstance(value, str):
                            value = value.strip()
                            if not value:  # 如果是空字符串
                                return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        print(f"警告: 无法转换值 '{value}' 为浮点数，使用0代替")
                        return 0.0
                
                # 获取并转换单价 - 使用英文字段名
                direct_labor_unit = safe_float(row["direct_labor_unit_price"])
                direct_material_unit = safe_float(row["direct_material_unit_price"])
                direct_machine_unit = safe_float(row["direct_machinery_unit_price"])
                direct_others_unit = safe_float(others.get("直接施工间接费", 0))
                
                modular_labor_unit = safe_float(row["modular_labor_unit_price"])
                modular_material_unit = safe_float(row["modular_material_unit_price"])
                modular_machine_unit = safe_float(row["modular_machinery_unit_price"])
                modular_others_unit = safe_float(others.get("模块化施工间接费", 0))
                
                # 计算直接施工成本
                direct_labor = direct_labor_unit * quantity
                direct_material = direct_material_unit * quantity
                direct_machine = direct_machine_unit * quantity
                direct_others = direct_others_unit
                direct_total = direct_labor + direct_material + direct_machine + direct_others_unit
                
                # 计算模块化施工成本
                modular_labor = modular_labor_unit * quantity
                modular_material = modular_material_unit * quantity
                modular_machine = modular_machine_unit * quantity
                modular_others = modular_others_unit
                modular_total = modular_labor + modular_material + modular_machine + modular_others_unit
                
                # 添加到总计
                result["直接施工"]["人工费"] += direct_labor
                result["直接施工"]["材料费"] += direct_material
                result["直接施工"]["机械费"] += direct_machine
                result["直接施工"]["间接费用"] = direct_others
                result["直接施工"]["总计"] += direct_total
                
                result["模块化施工"]["人工费"] += modular_labor
                result["模块化施工"]["材料费"] += modular_material
                result["模块化施工"]["机械费"] += modular_machine
                result["模块化施工"]["间接费用"] = modular_others
                result["模块化施工"]["总计"] += modular_total
                
                # 添加明细 - 使用英文字段名获取参数类别
                result["明细"].append({
                    "参数": param,
                    "数量": quantity,
                    "参数类别": row["parameter_category"] if "parameter_category" in row else "",
                    "直接施工": {
                        "人工费": round(direct_labor, 2),
                        "材料费": round(direct_material, 2),
                        "机械费": round(direct_machine, 2),
                        "间接费用": round(direct_others,2),
                        "总计": round(direct_total, 2)
                    },
                    "模块化施工": {
                        "人工费": round(modular_labor, 2),
                        "材料费": round(modular_material, 2),
                        "机械费": round(modular_machine, 2),
                        "间接费用": round(modular_others,2),
                        "总计": round(modular_total, 2)
                    }
                })
                
            except Exception as e:
                print(f"计算参数 '{param}' 成本时出错: {e}")
                # 记录错误但继续处理其他参数
        else:
            print(f"警告: 未找到参数 '{param}' 的价格数据")
    
    # 四舍五入总计结果
    for method in ["直接施工", "模块化施工"]:
        for cost_type in ["人工费", "材料费", "机械费", "总计"]:
            result[method][cost_type] = round(result[method][cost_type], 2)
    
    conn.close()
    return result

def init_db():
    """初始化MySQL数据库，如果不存在则创建必要的表（英文表结构）"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # 修改：只在表不存在时创建，不删除现有表
        if 'project_info' not in tables:
            # 创建项目基本信息表 - 使用英文字段名
            cursor.execute('''
            CREATE TABLE `project_info` (
                `project_id` INT NOT NULL AUTO_INCREMENT,
                `project_name` VARCHAR(255) NOT NULL,
                `project_type` VARCHAR(100) NOT NULL,
                `project_quantity` DECIMAL(15,2) DEFAULT 0,
                `unit` VARCHAR(50) DEFAULT '',
                `normal_construction_days` INT DEFAULT 0,
                `modular_construction_days` INT DEFAULT 0,
                `remarks` TEXT,
                `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`project_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1
            ''')
            print("已成功创建project_info表")
        else:
            print("project_info表已存在，跳过创建")
        
        # 创建参数表（如果不存在）- 使用英文字段名
        if 'parameter_info' not in tables:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS `parameter_info` (
                `parameter_id` INT AUTO_INCREMENT PRIMARY KEY,
                `project_id` INT NOT NULL,
                `project_name` VARCHAR(255) NOT NULL,
                `parameter_unique_id` VARCHAR(255) NOT NULL,
                `parameter_name` VARCHAR(255) NOT NULL,
                `parameter_type` VARCHAR(100) NOT NULL,
                `parameter_value` DECIMAL(15,2),
                `unit` VARCHAR(50),
                `remarks` TEXT,
                `direct_labor_unit_price` DECIMAL(15,2),
                `direct_material_unit_price` DECIMAL(15,2),
                `direct_machinery_unit_price` DECIMAL(15,2),
                `modular_labor_unit_price` DECIMAL(15,2),
                `modular_material_unit_price` DECIMAL(15,2),
                `modular_machinery_unit_price` DECIMAL(15,2),
                FOREIGN KEY (`project_id`) REFERENCES `project_info`(`project_id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            print("已成功创建parameter_info表")
        else:
            print("parameter_info表已存在，跳过创建")
        
    except Exception as e:
        print(f"初始化MySQL数据库时出错: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

def save_project(project_data):
    """保存项目基本信息并返回项目ID - 确保唯一性"""
    conn = None
    try:
        mysql_config = MYSQL_CONFIG.copy()
        mysql_config['autocommit'] = False
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        project_name = project_data.get('project_name', '')
        print(f"准备保存项目: {project_name}")
        
        # 检查项目名称是否已存在
        cursor.execute("SELECT `project_id` FROM `project_info` WHERE `project_name` = %s", (project_name,))
        existing_project = cursor.fetchone()
        
        if existing_project:
            project_id = existing_project['project_id']
            print(f"项目 '{project_name}' 已存在，使用现有project_id: {project_id}")
            conn.close()
            return project_id
        
        # 插入新项目
        insert_query = '''
        INSERT INTO `project_info` (
            `project_name`, `project_type`, `project_quantity`, `unit`, 
            `normal_construction_days`, `modular_construction_days`, `remarks`
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        
        insert_values = (
            project_data.get('project_name', ''),
            project_data.get('project_type', ''),
            project_data.get('project_value', 0),
            project_data.get('project_unit', ''),
            project_data.get('regular_days', 0),
            project_data.get('modular_days', 0),
            project_data.get('description', '')
        )
        
        cursor.execute(insert_query, insert_values)
        project_id = cursor.lastrowid
        
        if not project_id:
            # 备用方案
            cursor.execute("SELECT `project_id` FROM `project_info` WHERE `project_name` = %s", (project_name,))
            result = cursor.fetchone()
            if result:
                project_id = result['project_id']
        
        if not project_id:
            raise Exception("无法获取项目ID")
        
        conn.commit()
        print(f"新项目 '{project_name}' 保存成功，project_id: {project_id}")
        
        return project_id
        
    except Exception as e:
        print(f"保存项目时出错: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def save_custom_parameters(project_id, custom_params, replace_existing=True):
    """保存自定义参数 - 确保正确的project_id关联
    
    Args:
        project_id: 项目ID
        custom_params: 参数列表
        replace_existing: 是否替换现有参数，默认True。如果False则添加参数
    """
    conn = None
    try:
        mysql_config = MYSQL_CONFIG.copy()
        mysql_config['autocommit'] = False
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        if not project_id:
            raise Exception("project_id 不能为空")
        
        print(f"开始保存参数到project_id: {project_id}, 参数数量: {len(custom_params)}")
        
        # 验证project_id存在
        cursor.execute("SELECT `project_name` FROM `project_info` WHERE `project_id` = %s", (project_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception(f"project_id {project_id} 在project_info表中不存在")
        
        project_name = result['project_name']
        print(f"确认项目名称: {project_name}")
        
        # 只有在 replace_existing=True 时才删除现有参数
        if replace_existing:
            cursor.execute("DELETE FROM `parameter_info` WHERE `project_id` = %s", (project_id,))
            deleted_count = cursor.rowcount
            print(f"替换模式：删除了 {deleted_count} 个旧参数记录")
        else:
            print("添加模式：保留现有参数，只添加新参数")
        
        # 保存新参数
        success_count = 0
        for i, param in enumerate(custom_params):
            try:
                param_id = param.get('id', f'param_{i}')
                param_name = param.get('name', '')
                param_type = param.get('type', '')
                
                try:
                    param_value = float(param.get('value', 0))
                except (ValueError, TypeError):
                    param_value = 0.0
                    
                param_unit = param.get('unit', '')
                param_description = param.get('description', '')
                
                # 价格信息
                direct_labor_price = param.get('direct_labor_price', 0)
                direct_material_price = param.get('direct_material_price', 0)
                direct_machine_price = param.get('direct_machine_price', 0)
                modular_labor_price = param.get('modular_labor_price', 0)
                modular_material_price = param.get('modular_material_price', 0)
                modular_machine_price = param.get('modular_machine_price', 0)
                
                cursor.execute('''
                INSERT INTO `parameter_info` (
                    `project_id`, `project_name`, `parameter_unique_id`, `parameter_name`, `parameter_type`, 
                    `parameter_value`, `unit`, `remarks`,
                    `direct_labor_unit_price`, `direct_material_unit_price`, `direct_machinery_unit_price`,
                    `modular_labor_unit_price`, `modular_material_unit_price`, `modular_machinery_unit_price`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    project_id,  # 确保使用正确的project_id
                    project_name,
                    param_id,
                    param_name,
                    param_type,
                    param_value,
                    param_unit,
                    param_description,
                    direct_labor_price,
                    direct_material_price,
                    direct_machine_price,
                    modular_labor_price,
                    modular_material_price,
                    modular_machine_price
                ))
                
                success_count += 1
                print(f"参数 {i+1}/{len(custom_params)} 保存成功: {param_name}")
                
            except Exception as e:
                print(f"保存参数 {i+1} 时出错: {e}")
                raise
        
        conn.commit()
        action_type = "替换" if replace_existing else "添加"
        print(f"✅ 成功{action_type} {success_count}/{len(custom_params)} 个参数到project_id: {project_id}")
        
        # 验证保存结果
        cursor.execute("SELECT COUNT(*) as count FROM `parameter_info` WHERE `project_id` = %s", (project_id,))
        count_result = cursor.fetchone()
        actual_count = count_result['count'] if count_result else 0
        print(f"验证: project_id={project_id} 现有参数数量: {actual_count}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"保存参数失败: {e}")
        raise
        
    finally:
        if conn:
            conn.close()


def get_parameter_suggestions(param_name, param_type=None):
    """
    根据部分参数名称和类型获取建议及完整价格数据
    
    Args:
        param_name (str): 部分参数名称
        param_type (str, optional): 参数类型
        
    Returns:
        list: 参数建议及价格信息列表
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if param_type:
            query = """
            SELECT DISTINCT `engineering_parameter`, `parameter_category`, `mode`, 
                   `direct_labor_unit_price`, `direct_material_unit_price`, `direct_machinery_unit_price`,
                   `modular_labor_unit_price`, `modular_material_unit_price`, `modular_machinery_unit_price`
            FROM `construction_parameter_table`
            WHERE `engineering_parameter` LIKE %s AND `parameter_category` LIKE %s
            """
            cursor.execute(query, (f'%{param_name}%', f'%{param_type}%'))
        else:
            query = """
            SELECT DISTINCT `engineering_parameter`, `parameter_category`, `mode`, 
                   `direct_labor_unit_price`, `direct_material_unit_price`, `direct_machinery_unit_price`,
                   `modular_labor_unit_price`, `modular_material_unit_price`, `modular_machinery_unit_price`
            FROM `construction_parameter_table`
            WHERE `engineering_parameter` LIKE %s
            """
            cursor.execute(query, (f'%{param_name}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        suggestions = []
        for row in results:
            try:
                # 安全转换函数
                def safe_float(value):
                    if value is None:
                        return 0.0
                    if isinstance(value, str) and (value.strip() == "" or not value.strip()):
                        return 0.0
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return 0.0
                
                # 确保参数名不为空 - 使用英文字段名
                param_name = row['engineering_parameter'].strip() if row['engineering_parameter'] else ""
                if not param_name:
                    continue
                
                # 处理价格数据 - 使用英文字段名
                direct_labor_price = safe_float(row['direct_labor_unit_price'])
                direct_material_price = safe_float(row['direct_material_unit_price'])
                direct_machine_price = safe_float(row['direct_machinery_unit_price'])
                modular_labor_price = safe_float(row['modular_labor_unit_price'])
                modular_material_price = safe_float(row['modular_material_unit_price'])
                modular_machine_price = safe_float(row['modular_machinery_unit_price'])
                
                # 计算总价
                direct_total = direct_labor_price + direct_material_price + direct_machine_price
                modular_total = modular_labor_price + modular_material_price + modular_machine_price
                total_price = (direct_total + modular_total) / 2 if (direct_total + modular_total) > 0 else 0
                
                # 添加建议项 - 使用英文字段名获取数据
                suggestions.append({
                    "name": param_name,
                    "category": row['parameter_category'].strip() if row['parameter_category'] else "",
                    "mode": row['mode'].strip() if row['mode'] else "",
                    "price": round(total_price, 2),
                    "direct_labor_price": round(direct_labor_price, 2),
                    "direct_material_price": round(direct_material_price, 2),
                    "direct_machine_price": round(direct_machine_price, 2),
                    "modular_labor_price": round(modular_labor_price, 2),
                    "modular_material_price": round(modular_material_price, 2),
                    "modular_machine_price": round(modular_machine_price, 2)
                })
            except Exception as e:
                print(f"处理参数建议时出错: {e}")
                continue
        
        return suggestions
    except Exception as e:
        print(f"获取参数建议时发生错误: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def get_mode_details_from_database(mode_id):
    """从MySQL数据库获取指定ID的自定义模式详细信息"""
    try:
        # 连接到数据库
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取项目基本信息 - 使用英文表名和字段名
        cursor.execute('''
        SELECT * FROM `project_info` 
        WHERE `project_id` = %s
        ''', (mode_id,))
        
        project_row = cursor.fetchone()
        if not project_row:
            conn.close()
            return None  # 如果找不到项目，返回None
        
        # 获取项目名称用于后续查询
        project_name = project_row['project_name']
        
        # 确保项目数据包含所有必要的字段 - 使用英文字段名
        project_dict = {
            "id": project_row['project_id'],
            "project_name": project_name,
            "project_type": project_row['project_type'],
            "project_value": project_row['project_quantity'],
            "project_unit": project_row['unit'],
            "regular_days": project_row['normal_construction_days'],
            "modular_days": project_row['modular_construction_days'],
            "created_at": project_row['create_time'],
            "description": project_row['remarks'] if project_row['remarks'] else "",
            "parameters": []  # 初始化参数列表
        }
        
        # 修改参数查询逻辑 - 根据project_name筛选，并只获取必要字段
        cursor.execute('''
        SELECT 
            `parameter_name`,
            `parameter_type`, 
            `parameter_value`,
            `unit`,
            `remarks`,
            `direct_labor_unit_price`,
            `direct_material_unit_price`,
            `direct_machinery_unit_price`,
            `modular_labor_unit_price`,
            `modular_material_unit_price`,
            `modular_machinery_unit_price`
        FROM `parameter_info` 
        WHERE `project_name` = %s AND `project_id` = %s
        ORDER BY `parameter_id`
        ''', (project_name, mode_id))
        
        params = cursor.fetchall()
        
        # 将参数添加到结果字典中 - 使用英文字段名，简化数据结构
        for param in params:
            try:
                # 计算平均价格作为参考价格
                direct_total = (param.get('direct_labor_unit_price', 0) or 0) + \
                              (param.get('direct_material_unit_price', 0) or 0) + \
                              (param.get('direct_machinery_unit_price', 0) or 0)
                
                modular_total = (param.get('modular_labor_unit_price', 0) or 0) + \
                               (param.get('modular_material_unit_price', 0) or 0) + \
                               (param.get('modular_machinery_unit_price', 0) or 0)
                
                param_dict = {
                    "id": f"param_{len(project_dict['parameters'])}",  # 生成简单ID
                    "name": param['parameter_name'],
                    "type": param['parameter_type'],
                    "value": param['parameter_value'] if param['parameter_value'] else 0,
                    "unit": param['unit'] if param['unit'] else "",
                    "description": param['remarks'] if param['remarks'] else "",
                    "direct_total_price": round(direct_total, 2),
                    "modular_total_price": round(modular_total, 2),
                    # 只保留总价，不显示详细的人工、材料、机械费分解
                    #"price_difference": round(modular_total - direct_total, 2)
                }
                
                project_dict["parameters"].append(param_dict)
            except Exception as e:
                print(f"处理参数时出错: {e}")
                continue  # 跳过当前参数，继续处理下一个
        
        # 尝试获取计算结果（如果存在）- 使用英文表名
        try:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'calculation_results'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute('''
                SELECT * FROM `calculation_results` 
                WHERE `project_id` = %s 
                ORDER BY `calculation_time` DESC 
                LIMIT 1
                ''', (mode_id,))
                
                result_row = cursor.fetchone()
                if result_row:
                    try:
                        # 尝试解析JSON结果 - 使用英文字段名
                        result_json = json.loads(result_row['result_data'])
                        project_dict["calculation_results"] = result_json
                    except (json.JSONDecodeError, TypeError):
                        # 如果JSON解析失败，使用原始字符串
                        project_dict["calculation_results"] = result_row['result_data'] if result_row['result_data'] else {}
                else:
                    project_dict["calculation_results"] = {}
            else:
                project_dict["calculation_results"] = {}
        except Exception as e:
            print(f"获取计算结果时出错: {e}")
            project_dict["calculation_results"] = {}
        
        conn.close()
        return project_dict
        
    except Exception as e:
        print(f"加载自定义模式时出错: {e}")
        return {
            "id": mode_id,
            "project_name": "数据加载错误",
            "project_type": "",
            "description": f"加载数据时发生错误: {str(e)}",
            "parameters": []
        }

def safe_float(value):
    """
    安全地将值转换为浮点数
    
    Args:
        value: 需要转换的值
        
    Returns:
        float: 转换后的浮点数，如果转换失败则返回0.0
    """
    if value is None:
        return 0.0
    
    if isinstance(value, str) and (value.strip() == "" or not value.strip()):
        return 0.0
    
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"警告: 无法转换值 '{value}' 为浮点数，使用0代替")
        return 0.0

def save_selected_parameters(project_id, selected_parameters):
    """
    保存用户从价格数据表中选择的参数到MySQL数据库 - 修正版本
    
    Args:
        project_id (int): 项目ID
        selected_parameters (list): 包含选中参数的列表，每个参数是一个字典
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    conn = None
    try:
        # 创建连接时关闭自动提交以支持事务
        mysql_config = MYSQL_CONFIG.copy()
        mysql_config['autocommit'] = False
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        print(f"开始保存选中参数，project_id: {project_id}, 参数数量: {len(selected_parameters)}")
        
        # 获取项目名称 - 使用英文表名和字段名
        cursor.execute("SELECT `project_name` FROM `project_info` WHERE `project_id` = %s", (project_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception(f"找不到project_id为{project_id}的项目")
        
        project_name = result['project_name']
        print(f"项目名称: {project_name}")
        
        # 为每个选中的参数创建记录
        for i, param in enumerate(selected_parameters):
            # 生成唯一ID
            param_unique_id = str(uuid.uuid4())
            
            # 确保所有必要的字段都有值
            param_name = param.get('name', '')
            param_type = param.get('category', '')
            param_value = param.get('value', 0)  # 默认值为0
            param_unit = param.get('unit', '')  # 单位可能为空
            param_description = param.get('description', '')  # 描述可能为空
            
            # 价格信息
            direct_labor_price = param.get('direct_labor_price', 0)
            direct_material_price = param.get('direct_material_price', 0)
            direct_machine_price = param.get('direct_machine_price', 0)
            modular_labor_price = param.get('modular_labor_price', 0)
            modular_material_price = param.get('modular_material_price', 0)
            modular_machine_price = param.get('modular_machine_price', 0)
            
            print(f"保存选中参数 {i+1}: {param_name}, project_id: {project_id}")
            
            # 插入参数记录 - 使用英文表名和字段名
            cursor.execute('''
            INSERT INTO `parameter_info` (
                `project_id`, `project_name`, `parameter_unique_id`, `parameter_name`, `parameter_type`, 
                `parameter_value`, `unit`, `remarks`,
                `direct_labor_unit_price`, `direct_material_unit_price`, `direct_machinery_unit_price`,
                `modular_labor_unit_price`, `modular_material_unit_price`, `modular_machinery_unit_price`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                project_id,  # 确保使用正确的project_id
                project_name,
                param_unique_id,
                param_name,
                param_type,
                param_value,
                param_unit,
                param_description,
                direct_labor_price,
                direct_material_price,
                direct_machine_price,
                modular_labor_price,
                modular_material_price,
                modular_machine_price
            ))
        
        # 提交事务
        conn.commit()
        print(f"成功保存 {len(selected_parameters)} 个选中参数到project_id: {project_id}")
        
        # 验证保存结果
        cursor.execute("SELECT COUNT(*) as count FROM `parameter_info` WHERE `project_id` = %s", (project_id,))
        count_result = cursor.fetchone()
        actual_count = count_result['count'] if count_result else 0
        print(f"验证：数据库中project_id={project_id}的参数总数量: {actual_count}")
        
        return True
    
    except Exception as e:
        print(f"保存选中参数时出错: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def calculate_cost_diy(mode, params_dict, others):
    """
    计算特定模式和参数的成本（DIY版本）
    
    Args:
        mode (str): 施工模式
        params_dict (dict): 参数值字典，格式为 {工程参数: 数量}
        others (dict): 其他费用
        
    Returns:
        dict: 包含直接施工和模块化施工成本明细的字典
    """
    conn = get_connection_diy()
    
    # 初始化结果
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
        "明细": []
    }
    
    # 逐个处理每个参数
    for param, quantity in params_dict.items():
        # 查找该参数的价格数据 - 使用英文表名和字段名
        query = """
        SELECT * FROM `parameter_info`
        WHERE `parameter_name` = %s
        """
        param_df = pd.read_sql(query, conn, params=(param,))
        print(param)
        
        if not param_df.empty:
            row = param_df.iloc[0]
            
            try:
                # 确保数量是有效数值
                quantity_str = str(quantity).strip() if quantity is not None else ""
                quantity = float(quantity_str) if quantity_str else 0
                
                # 安全地获取单价，确保它们是数值
                def safe_float(value):
                    """安全地将值转换为浮点数"""
                    if pd.isna(value) or value is None:
                        return 0.0
                    try:
                        if isinstance(value, str):
                            value = value.strip()
                            if not value:
                                return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        print(f"警告: 无法转换值 '{value}' 为浮点数，使用0代替")
                        return 0.0
                
                # 获取并转换单价 - 使用英文字段名
                direct_labor_unit = safe_float(row["direct_labor_unit_price"])
                direct_material_unit = safe_float(row["direct_material_unit_price"])
                direct_machine_unit = safe_float(row["direct_machinery_unit_price"])
                direct_others_unit = safe_float(others.get("直接施工间接费", 0))
                
                modular_labor_unit = safe_float(row["modular_labor_unit_price"])
                modular_material_unit = safe_float(row["modular_material_unit_price"])
                modular_machine_unit = safe_float(row["modular_machinery_unit_price"])
                modular_others_unit = safe_float(others.get("模块化施工间接费", 0))
                
                # 计算直接施工成本
                direct_labor = direct_labor_unit * quantity
                direct_material = direct_material_unit * quantity
                direct_machine = direct_machine_unit * quantity
                direct_others = direct_others_unit
                direct_total = direct_labor + direct_material + direct_machine + direct_others_unit
                
                # 计算模块化施工成本
                modular_labor = modular_labor_unit * quantity
                modular_material = modular_material_unit * quantity
                modular_machine = modular_machine_unit * quantity
                modular_others = modular_others_unit
                modular_total = modular_labor + modular_material + modular_machine + modular_others_unit
                
                # 添加到总计
                result["直接施工"]["人工费"] += direct_labor
                result["直接施工"]["材料费"] += direct_material
                result["直接施工"]["机械费"] += direct_machine
                result["直接施工"]["间接费用"] = direct_others
                result["直接施工"]["总计"] += direct_total
                
                result["模块化施工"]["人工费"] += modular_labor
                result["模块化施工"]["材料费"] += modular_material
                result["模块化施工"]["机械费"] += modular_machine
                result["模块化施工"]["间接费用"] = modular_others
                result["模块化施工"]["总计"] += modular_total
                
                # 添加明细 - 使用英文字段名获取参数类别
                result["明细"].append({
                    "参数": param,
                    "数量": quantity,
                    "参数类别": row["parameter_type"] if "parameter_type" in row else "",
                    "直接施工": {
                        "人工费": round(direct_labor, 2),
                        "材料费": round(direct_material, 2),
                        "机械费": round(direct_machine, 2),
                        "间接费用": round(direct_others,2),
                        "总计": round(direct_total, 2)
                    },
                    "模块化施工": {
                        "人工费": round(modular_labor, 2),
                        "材料费": round(modular_material, 2),
                        "机械费": round(modular_machine, 2),
                        "间接费用": round(modular_others,2),
                        "总计": round(modular_total, 2)
                    }
                })
                
            except Exception as e:
                print(f"计算参数 '{param}' 成本时出错: {e}")
        else:
            print(f"警告: 未找到参数 '{param}' 的价格数据")
    
    # 四舍五入总计结果
    for method in ["直接施工", "模块化施工"]:
        for cost_type in ["人工费", "材料费", "机械费", "总计"]:
            result[method][cost_type] = round(result[method][cost_type], 2)
    
    conn.close()
    return result

def save_calculation_result(project_id, construction_mode, cost_data, cost_json):
    """
    保存计算结果到MySQL数据库 - 完全无result_id版本
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print(f"开始保存计算结果到数据库...")
        print(f"项目ID: {project_id} (类型: {type(project_id)})")
        print(f"施工模式: {construction_mode}")
        
        # 处理项目ID映射
        if isinstance(project_id, str):
            mode_id_mapping = {
                "steel-cage-mode": 1001,
                "steel-cage-cover-mode": 1002, 
                "equipment-room-composite-mode": 1003,
                "utility-tunnel-composite-mode": 1004,
                "utility-tunnel-c404-mode": 1005,
                "steel-lining-mode": 1006
            }
            if project_id in mode_id_mapping:
                actual_project_id = mode_id_mapping[project_id]
                print(f"映射项目ID: {project_id} -> {actual_project_id}")
            else:
                try:
                    actual_project_id = int(project_id)
                except ValueError:
                    actual_project_id = 1001
        else:
            actual_project_id = project_id
        
        print(f"实际使用的项目ID: {actual_project_id}")
        
        # 提取各项费用数据
        direct_labor = cost_data["直接施工"]["人工费"]
        direct_material = cost_data["直接施工"]["材料费"]
        direct_machine = cost_data["直接施工"]["机械费"]
        direct_indirect = cost_data["直接施工"]["间接费用"]
        direct_total = cost_data["直接施工"]["总计"]
        
        modular_labor = cost_data["模块化施工"]["人工费"]
        modular_material = cost_data["模块化施工"]["材料费"]
        modular_machine = cost_data["模块化施工"]["机械费"]
        modular_indirect = cost_data["模块化施工"]["间接费用"]
        modular_total = cost_data["模块化施工"]["总计"]
        
        # 计算差异
        cost_diff = modular_total - direct_total
        cost_diff_percent = (cost_diff / direct_total * 100) if direct_total > 0 else 0
        
        # 检查是否已有记录 - 不使用result_id
        cursor.execute(
            "SELECT COUNT(*) as count FROM `calculation_results` WHERE `project_id`=%s AND `construction_mode`=%s", 
            (actual_project_id, construction_mode)
        )
        count_result = cursor.fetchone()
        record_exists = count_result['count'] > 0
        
        print(f"记录是否存在: {record_exists}")
        
        if record_exists:
            # 更新现有记录 - WHERE条件不使用result_id
            print("更新现有记录")
            cursor.execute('''
            UPDATE `calculation_results` SET
                `result_data`=%s,
                `direct_labor_cost`=%s,
                `direct_material_cost`=%s,
                `direct_machinery_cost`=%s,
                `direct_indirect_cost`=%s,
                `direct_total`=%s,
                `modular_labor_cost`=%s,
                `modular_material_cost`=%s,
                `modular_machinery_cost`=%s,
                `modular_indirect_cost`=%s,
                `modular_total`=%s,
                `cost_difference`=%s,
                `cost_difference_percentage`=%s,
                `calculation_time`=CURRENT_TIMESTAMP
            WHERE `project_id`=%s AND `construction_mode`=%s
            ''', (
                cost_json,
                direct_labor,
                direct_material,
                direct_machine,
                direct_indirect,
                direct_total,
                modular_labor,
                modular_material,
                modular_machine,
                modular_indirect,
                modular_total,
                cost_diff,
                cost_diff_percent,
                actual_project_id,
                construction_mode
            ))
            print("✅ 成功更新计算结果记录")
        else:
            # 插入新记录 - 不包含result_id字段
            print("插入新的计算结果记录")
            cursor.execute('''
            INSERT INTO `calculation_results` (
                `project_id`, 
                `construction_mode`, 
                `result_data`,
                `direct_labor_cost`, 
                `direct_material_cost`, 
                `direct_machinery_cost`, 
                `direct_indirect_cost`, 
                `direct_total`,
                `modular_labor_cost`, 
                `modular_material_cost`, 
                `modular_machinery_cost`, 
                `modular_indirect_cost`, 
                `modular_total`,
                `cost_difference`, 
                `cost_difference_percentage`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                actual_project_id,
                construction_mode,
                cost_json,
                direct_labor,
                direct_material,
                direct_machine,
                direct_indirect,
                direct_total,
                modular_labor,
                modular_material,
                modular_machine,
                modular_indirect,
                modular_total,
                cost_diff,
                cost_diff_percent
            ))
            print("✅ 成功插入新的计算结果记录")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 保存计算结果时出错: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False
    

def debug_steel_lining_database():
    """调试钢衬里MySQL数据库，检查表结构和数据"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== 钢衬里MySQL数据库诊断 ===")
        
        # 1. 检查数据库中的所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]
        print(f"数据库中的表: {table_names}")
        
        # 2. 如果有表，检查表结构和数据
        for table_dict in tables:
            table_name = list(table_dict.values())[0]
            print(f"\n--- 表 '{table_name}' 的信息 ---")
            
            # 检查表结构
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            print("字段信息:")
            for col in columns:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # 检查数据数量
            cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            count = cursor.fetchone()['count']
            print(f"数据行数: {count}")
            
            # 查看前几行数据
            if count > 0:
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                rows = cursor.fetchall()
                print("前5行数据:")
                for row in rows:
                    print(f"  {dict(row)}")
        
        conn.close()
        
    except Exception as e:
        print(f"调试时出错: {e}")

def calculate_steel_lining_cost_fixed(mode, params_dict, others):
    """
    钢衬里施工模式标准计算方式 - 完全移植标准计算逻辑
    
    Args:
        mode (str): 施工模式
        params_dict (dict): 参数值字典，格式为 {工程参数: 数量}
        others (dict): 其他费用
        
    Returns:
        dict: 包含直接施工和模块化施工成本明细的字典
    """
    try:
        # 连接数据库
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print(f"开始计算钢衬里成本，模式: {mode}")
        print(f"传入参数: {params_dict}")
        
        # 钢衬里模式使用专门的steel_lining表
        table_name = "steel_lining"
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]
        
        if table_name not in table_names:
            print(f"警告: 表 '{table_name}' 不存在")
            conn.close()
            return create_empty_steel_lining_result()
        
        # 检查表结构
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        print(f"表 '{table_name}' 的字段: {column_names}")
        
    except Exception as e:
        print(f"数据库连接出错: {e}")
        if 'conn' in locals():
            conn.close()
        return create_empty_steel_lining_result()
    
    # 初始化结果 - 完全按照标准格式
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0, "总计": 0},
        "明细": []
    }
    
    # 逐个处理每个参数 - 完全按照标准方式
    for param, quantity in params_dict.items():
        print(f"正在查询参数: {param}")
        
        # 查找该参数的价格数据 - 使用标准查询方式
        query = f"""
        SELECT * FROM `{table_name}`
        WHERE `name` = %s
        """
        
        try:
            param_df = pd.read_sql(query, conn, params=(param,))
            
            if param_df.empty:
                print(f"精确匹配失败，尝试模糊匹配参数: '{param}'")
                # 尝试模糊匹配 - 标准处理方式
                fuzzy_query = f"""
                SELECT * FROM `{table_name}`
                WHERE `name` LIKE %s
                """
                param_df = pd.read_sql(fuzzy_query, conn, params=(f'%{param}%',))
                
                if param_df.empty:
                    print(f"警告: 未找到参数 '{param}' 的价格数据")
                    continue
                else:
                    print(f"通过模糊匹配找到: '{param}'")
        
        except Exception as e:
            print(f"查询参数 '{param}' 时出错: {e}")
            continue
        
        if not param_df.empty:
            row = param_df.iloc[0]
            
            try:
                # 确保数量是有效数值 - 标准处理方式
                quantity_str = str(quantity).strip() if quantity is not None else ""
                quantity = float(quantity_str) if quantity_str else 0
                
                # 安全地获取单价，确保它们是数值 - 完全按照标准方式
                def safe_float_local(value):
                    """安全地将值转换为浮点数 - 标准函数"""
                    if pd.isna(value) or value is None:
                        return 0.0
                    try:
                        if isinstance(value, str):
                            value = value.strip()
                            if not value:
                                return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        print(f"警告: 无法转换值 '{value}' 为浮点数，使用0代替")
                        return 0.0
                
                # 获取直接施工单价 - 钢衬里表字段映射
                direct_labor_unit = safe_float_local(row.get("labor_cost", 0))
                direct_material_unit = safe_float_local(row.get("material_cost", 0))
                direct_machine_unit = safe_float_local(row.get("machinery_cost", 0))
                direct_others_unit = safe_float_local(others.get("直接施工间接费", 0))
                
                # 获取模块化施工单价 - 检查是否有模块化字段
                if "modular_labor_cost" in row:
                    # 如果表中有模块化字段，直接使用
                    modular_labor_unit = safe_float_local(row.get("modular_labor_cost", 0))
                    modular_material_unit = safe_float_local(row.get("modular_material_cost", 0))
                    modular_machine_unit = safe_float_local(row.get("modular_machinery_cost", 0))
                    print(f"使用数据库中的模块化施工单价")
                else:
                    # 如果表中没有模块化字段，使用比例计算
                    print(f"数据库中无模块化字段，使用比例计算模块化单价")
                    modular_labor_unit = direct_labor_unit * 0.8      # 人工费降低20%
                    modular_material_unit = direct_material_unit * 1.1 # 材料费增加10%  
                    modular_machine_unit = direct_machine_unit * 0.9   # 机械费降低10%
                
                modular_others_unit = safe_float_local(others.get("模块化施工间接费", 0))
                
                # ====== 标准计算公式 - 完全按照其他模式的计算方式 ======
                # 计算直接施工成本 - 标准公式：单价 × 数量
                direct_labor = direct_labor_unit * quantity
                direct_material = direct_material_unit * quantity  
                direct_machine = direct_machine_unit * quantity
                direct_others = direct_others_unit  # 间接费用不乘数量
                direct_total = direct_labor + direct_material + direct_machine + direct_others_unit
                
                # 计算模块化施工成本 - 标准公式：单价 × 数量  
                modular_labor = modular_labor_unit * quantity
                modular_material = modular_material_unit * quantity
                modular_machine = modular_machine_unit * quantity
                modular_others = modular_others_unit  # 间接费用不乘数量
                modular_total = modular_labor + modular_material + modular_machine + modular_others_unit
                
                # 添加到总计 - 完全按照标准方式
                result["直接施工"]["人工费"] += direct_labor
                result["直接施工"]["材料费"] += direct_material
                result["直接施工"]["机械费"] += direct_machine
                result["直接施工"]["间接费用"] = direct_others
                result["直接施工"]["总计"] += direct_total
                
                result["模块化施工"]["人工费"] += modular_labor
                result["模块化施工"]["材料费"] += modular_material
                result["模块化施工"]["机械费"] += modular_machine
                result["模块化施工"]["间接费用"] = modular_others
                result["模块化施工"]["总计"] += modular_total
                
                # 添加明细 - 完全按照标准格式
                result["明细"].append({
                    "参数": param,
                    "数量": quantity,
                    "参数类别": "钢衬里",  # 钢衬里固定类别
                    "直接施工": {
                        "人工费": round(direct_labor, 2),
                        "材料费": round(direct_material, 2),
                        "机械费": round(direct_machine, 2),
                        "间接费用": round(direct_others, 2),
                        "总计": round(direct_total, 2)
                    },
                    "模块化施工": {
                        "人工费": round(modular_labor, 2),
                        "材料费": round(modular_material, 2),
                        "机械费": round(modular_machine, 2),
                        "间接费用": round(modular_others, 2),
                        "总计": round(modular_total, 2)
                    }
                })
                
                print(f"参数 '{param}' 计算完成:")
                print(f"  - 直接施工: 人工{direct_labor:.2f}, 材料{direct_material:.2f}, 机械{direct_machine:.2f}, 总计{direct_total:.2f}")
                print(f"  - 模块化施工: 人工{modular_labor:.2f}, 材料{modular_material:.2f}, 机械{modular_machine:.2f}, 总计{modular_total:.2f}")
                
            except Exception as e:
                print(f"计算参数 '{param}' 成本时出错: {e}")
                continue
        else:
            print(f"警告: 未找到参数 '{param}' 的价格数据")
    
    # 四舍五入总计结果 - 完全按照标准方式
    for method in ["直接施工", "模块化施工"]:
        for cost_type in ["人工费", "材料费", "机械费", "总计"]:
            result[method][cost_type] = round(result[method][cost_type], 2)
    
    conn.close()
    
    # 打印最终结果用于调试
    print("=== 钢衬里成本计算结果 ===")
    print(f"直接施工总计: {result['直接施工']['总计']:.2f}")
    print(f"模块化施工总计: {result['模块化施工']['总计']:.2f}")
    print(f"成本差异: {result['模块化施工']['总计'] - result['直接施工']['总计']:.2f}")
    
    return result


# 在文件末尾添加新的辅助函数
def create_empty_steel_lining_result():
    """创建钢衬里空结果 - 标准格式"""
    return {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0, "总计": 0},
        "明细": []
    }


def delete_custom_project(project_id):
    """
    删除指定的自定义项目及其所有相关数据
    
    Args:
        project_id (int): 要删除的项目ID
        
    Returns:
        dict: 包含删除结果的字典 {"success": bool, "message": str, "deleted_params": int}
    """
    conn = None
    try:
        # 使用事务确保数据一致性
        mysql_config = MYSQL_CONFIG.copy()
        mysql_config['autocommit'] = False
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        print(f"开始删除project_id: {project_id}")
        
        # 1. 首先检查项目是否存在
        cursor.execute("SELECT `project_name` FROM `project_info` WHERE `project_id` = %s", (project_id,))
        project = cursor.fetchone()
        
        if not project:
            return {
                "success": False,
                "message": f"项目ID {project_id} 不存在",
                "deleted_params": 0
            }
        
        project_name = project['project_name']
        print(f"找到项目: {project_name}")
        
        # 2. 统计要删除的参数数量
        cursor.execute("SELECT COUNT(*) as count FROM `parameter_info` WHERE `project_id` = %s", (project_id,))
        param_count_result = cursor.fetchone()
        param_count = param_count_result['count'] if param_count_result else 0
        
        print(f"项目 '{project_name}' 包含 {param_count} 个参数")
        
        # 3. 删除参数信息（由于外键约束，必须先删除子表数据）
        cursor.execute("DELETE FROM `parameter_info` WHERE `project_id` = %s", (project_id,))
        deleted_params = cursor.rowcount
        print(f"删除了 {deleted_params} 个参数")
        
        # 4. 删除计算结果（如果存在calculation_results表）
        try:
            cursor.execute("DELETE FROM `calculation_results` WHERE `project_id` = %s", (project_id,))
            deleted_results = cursor.rowcount
            print(f"删除了 {deleted_results} 个计算结果")
        except Exception as e:
            print(f"删除计算结果时出错（可能表不存在）: {e}")
        
        # 5. 最后删除项目基本信息
        cursor.execute("DELETE FROM `project_info` WHERE `project_id` = %s", (project_id,))
        deleted_project = cursor.rowcount
        
        if deleted_project == 0:
            conn.rollback()
            return {
                "success": False,
                "message": f"删除项目失败，project_id: {project_id}",
                "deleted_params": 0
            }
        
        # 6. 提交事务
        conn.commit()
        
        print(f"✅ 成功删除项目 '{project_name}' (ID: {project_id})")
        print(f"   - 删除了 {deleted_params} 个参数")
        print(f"   - 删除了项目基本信息")
        
        return {
            "success": True,
            "message": f"成功删除项目 '{project_name}' 及其 {deleted_params} 个参数",
            "deleted_params": deleted_params,
            "project_name": project_name
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        
        error_msg = f"删除项目时出错: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        
        return {
            "success": False,
            "message": error_msg,
            "deleted_params": 0
        }
        
    finally:
        if conn:
            conn.close()


def get_project_basic_info(project_id):
    """
    获取项目的基本信息（用于删除确认）
    
    Args:
        project_id (int): 项目ID
        
    Returns:
        dict: 项目基本信息，如果不存在返回None
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取项目基本信息和参数统计
        cursor.execute('''
        SELECT 
            pi.project_id,
            pi.project_name,
            pi.project_type,
            pi.project_quantity,
            pi.unit,
            pi.create_time,
            COUNT(pa.parameter_id) as parameter_count
        FROM project_info pi
        LEFT JOIN parameter_info pa ON pi.project_id = pa.project_id
        WHERE pi.project_id = %s
        GROUP BY pi.project_id
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "project_id": result['project_id'],
                "project_name": result['project_name'],
                "project_type": result['project_type'],
                "project_quantity": result['project_quantity'],
                "unit": result['unit'],
                "create_time": result['create_time'],
                "parameter_count": result['parameter_count']
            }
        else:
            return None
            
    except Exception as e:
        print(f"获取项目基本信息时出错: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return None


# 添加一个调试函数来检查数据库状态
def debug_project_parameter_relationship():
    """调试函数：检查项目和参数的关联关系"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== 项目和参数关联关系调试 ===")
        
        # 检查project_info表
        cursor.execute("SELECT `project_id`, `project_name`, `create_time` FROM `project_info` ORDER BY `create_time` DESC")
        projects = cursor.fetchall()
        print(f"\nproject_info表中的项目:")
        for project in projects:
            print(f"  ID: {project['project_id']}, 名称: {project['project_name']}, 创建时间: {project['create_time']}")
        
        # 检查parameter_info表
        cursor.execute("SELECT `project_id`, `project_name`, COUNT(*) as param_count FROM `parameter_info` GROUP BY `project_id`, `project_name`")
        param_stats = cursor.fetchall()
        print(f"\nparameter_info表中的统计:")
        for stat in param_stats:
            print(f"  project_id: {stat['project_id']}, project_name: {stat['project_name']}, 参数数量: {stat['param_count']}")
        
        # 检查是否有孤立的参数（project_id不存在于project_info中）
        cursor.execute('''
        SELECT DISTINCT p.project_id, p.project_name 
        FROM parameter_info p 
        LEFT JOIN project_info pr ON p.project_id = pr.project_id 
        WHERE pr.project_id IS NULL
        ''')
        orphaned = cursor.fetchall()
        if orphaned:
            print(f"\n发现孤立参数（project_id不存在于project_info中）:")
            for orphan in orphaned:
                print(f"  project_id: {orphan['project_id']}, project_name: {orphan['project_name']}")
        else:
            print(f"\n没有发现孤立参数")
        
        conn.close()
        
    except Exception as e:
        print(f"调试时出错: {e}")

def fix_existing_project_ids():
    """
    修复现有数据库中的项目ID分配问题
    为不同的project_name分配不同的project_id，保留所有现有数据
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== 开始修复项目ID分配问题 ===")
        
        # 1. 获取parameter_info表中所有不同的project_name
        cursor.execute('''
        SELECT DISTINCT project_name 
        FROM parameter_info 
        WHERE project_name IS NOT NULL AND project_name != ''
        ORDER BY project_name
        ''')
        
        distinct_project_names = cursor.fetchall()
        print(f"发现 {len(distinct_project_names)} 个不同的项目名称:")
        for item in distinct_project_names:
            print(f"  - {item['project_name']}")
        
        # 2. 为每个project_name检查或创建对应的project_info记录
        project_id_mapping = {}  # project_name -> project_id 的映射
        
        for item in distinct_project_names:
            project_name = item['project_name']
            
            # 检查project_info表中是否已有此项目
            cursor.execute('''
            SELECT project_id FROM project_info 
            WHERE project_name = %s
            ''', (project_name,))
            
            existing_project = cursor.fetchone()
            
            if existing_project:
                # 如果已存在，使用现有的project_id
                project_id = existing_project['project_id']
                print(f"项目 '{project_name}' 已存在，使用project_id: {project_id}")
            else:
                # 如果不存在，创建新的project_info记录
                cursor.execute('''
                INSERT INTO project_info (
                    project_name, project_type, project_quantity, unit,
                    normal_construction_days, modular_construction_days, remarks
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    project_name,
                    "自定义",  # 默认类型
                    0,         # 默认工程量
                    "",        # 默认单位
                    0,         # 默认正常施工天数
                    0,         # 默认模块化施工天数
                    f"数据修复时创建的项目记录 - {project_name}"
                ))
                
                project_id = cursor.lastrowid
                print(f"为项目 '{project_name}' 创建新记录，project_id: {project_id}")
            
            project_id_mapping[project_name] = project_id
        
        # 3. 更新parameter_info表中的project_id
        print("\n开始更新parameter_info表中的project_id...")
        
        for project_name, correct_project_id in project_id_mapping.items():
            cursor.execute('''
            UPDATE parameter_info 
            SET project_id = %s 
            WHERE project_name = %s
            ''', (correct_project_id, project_name))
            
            updated_count = cursor.rowcount
            print(f"项目 '{project_name}' 的 {updated_count} 个参数已更新为project_id: {correct_project_id}")
        
        # 4. 提交所有更改
        conn.commit()
        print("\n所有更改已提交到数据库")
        
        # 5. 验证修复结果
        print("\n=== 验证修复结果 ===")
        cursor.execute('''
        SELECT project_id, project_name, COUNT(*) as param_count
        FROM parameter_info 
        GROUP BY project_id, project_name
        ORDER BY project_id
        ''')
        
        results = cursor.fetchall()
        print("修复后的项目ID分配:")
        for result in results:
            print(f"  project_id: {result['project_id']}, project_name: '{result['project_name']}', 参数数量: {result['param_count']}")
        
        # 6. 检查是否还有project_id为1且project_name不同的情况
        cursor.execute('''
        SELECT DISTINCT project_name 
        FROM parameter_info 
        WHERE project_id = 1
        ''')
        
        id_1_projects = cursor.fetchall()
        if len(id_1_projects) > 1:
            print(f"\n警告: project_id=1 仍然对应多个项目名称: {[p['project_name'] for p in id_1_projects]}")
        else:
            print(f"\n✅ 修复成功！每个project_id现在都对应唯一的project_name")
        
        conn.close()
        
        return {
            "success": True,
            "project_count": len(distinct_project_names),
            "mapping": project_id_mapping
        }
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        if conn:
            conn.rollback()
            conn.close()
        return {"success": False, "error": str(e)}
    
# 添加一个运行修复的便捷函数
def run_project_id_fix():
    """运行项目ID修复 - 可以在Python控制台中调用"""
    print("开始修复项目ID分配问题...")
    result = fix_existing_project_ids()
    
    if result["success"]:
        print(f"\n🎉 修复完成！")
        print(f"处理了 {result['project_count']} 个不同的项目")
        print(f"项目ID映射:")
        for name, id in result["mapping"].items():
            print(f"  '{name}' -> project_id: {id}")
    else:
        print(f"\n❌ 修复失败: {result['error']}")
    
    return result


def fix_calculation_result_table():
    """修复 calculation_result 表的字段长度问题"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        print("开始检查和修复 calculation_result 表...")
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'calculation_result'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("calculation_result 表已存在，检查字段结构...")
            
            # 查看当前表结构
            cursor.execute("DESCRIBE calculation_result")
            columns = cursor.fetchall()
            
            print("当前表结构：")
            for col in columns:
                print(f"  {col}")
            
            # 修改 result_data 字段为 LONGTEXT
            print("修改 result_data 字段为 LONGTEXT...")
            cursor.execute("ALTER TABLE calculation_result MODIFY COLUMN result_data LONGTEXT")
            
            # 验证修改结果
            cursor.execute("DESCRIBE calculation_result")
            columns = cursor.fetchall()
            result_data_col = [col for col in columns if col[0] == 'result_data']
            if result_data_col:
                print(f"result_data 字段修改后的类型: {result_data_col[0][1]}")
            
            conn.commit()
            print("✅ calculation_result 表修复成功")
        else:
            print("calculation_result 表不存在，将创建新表...")
            # 创建表（使用修改后的init_db函数）
            init_db()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"修复 calculation_result 表时出错: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        if conn:
            conn.close()
        return False
    

