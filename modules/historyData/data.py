# modules/historyData/data.py (修改版本)
import mysql.connector
from datetime import datetime
import re
from .translation import (
    translate_history_table_name, 
    translate_history_field_name,
    reverse_translate_table_name,
    reverse_translate_field_name
)

# MySQL数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名 - 使用新的英文数据库
    'charset': 'utf8mb4',
    'autocommit': False
}

def translate_schema_columns(columns):
    """翻译schema中的列定义"""
    translated_columns = []
    for col in columns:
        translated_col = col.copy()
        # 将英文字段名翻译为中文
        if 'id' in col:
            translated_col['name'] = translate_history_field_name(col['id'])
        translated_columns.append(translated_col)
    return translated_columns

def translate_record_data(record_dict):
    """将记录数据的字段名从英文翻译为中文"""
    if not record_dict:
        return record_dict
    
    translated_record = {}
    for key, value in record_dict.items():
        chinese_key = translate_history_field_name(key)
        translated_record[chinese_key] = value
    return translated_record

def reverse_translate_record_data(record_dict):
    """将记录数据的字段名从中文翻译为英文"""
    if not record_dict:
        return record_dict
    
    english_record = {}
    for key, value in record_dict.items():
        english_key = reverse_translate_field_name(key)
        english_record[english_key] = value
    return english_record

# 新增调试函数：列出数据库中的所有表和结构
def debug_database_structure():
    """调试函数：打印数据库中所有表的结构信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("=" * 50)
        print("数据库结构调试信息:")
        print("=" * 50)
        
        for table in tables:
            table_name = list(table.values())[0]  # MySQL的SHOW TABLES返回格式不同
            print(f"\n表名: {table_name} (中文: {translate_history_table_name(table_name)})")
            print("-" * 30)
            
            # 获取表结构
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            for col in columns:
                chinese_name = translate_history_field_name(col['Field'])
                print(f"  列: {col['Field']:<20} (中文: {chinese_name:<15}) 类型: {col['Type']:<15} 非空: {col['Null'] == 'NO'}")
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            count = cursor.fetchone()['count']
            print(f"  记录数: {count}")
            
            # 显示前几条记录的示例
            if count > 0:
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 2")
                samples = cursor.fetchall()
                print("  示例数据:")
                for sample in samples:
                    print(f"    {sample}")
        
        conn.close()
        print("=" * 50)
        
    except Exception as e:
        print(f"调试数据库结构失败: {e}")

# 修改现有的 get_db_connection() 函数，增加模式参数
def get_db_connection(mode=None):
    """连接数据库，支持根据模式选择不同的数据库"""
    try:
        # MySQL不需要根据模式选择不同的数据库文件，所有数据都在同一个数据库中
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print(f"成功连接到MySQL数据库: {MYSQL_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"连接MySQL数据库失败: {e}")
        raise

# 新增：施工模式专用数据库连接
def get_mode_db_connection():
    """
    连接到施工模式专用数据库
    MySQL版本中，所有数据都在同一个数据库中
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print(f"成功连接到施工模式MySQL数据库: {MYSQL_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"连接施工模式MySQL数据库失败: {e}")
        # 如果专用数据库连接失败，回退到主数据库
        print("回退到主数据库")
        return get_db_connection()

# 获取不同模式的表结构定义（修改：使用英文表名和字段名）
def get_table_schema(mode):
    # 使用施工模式专用数据库检查表
    try:
        conn = get_mode_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [list(row.values())[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"施工模式数据库中存在的表: {existing_tables}")
        
    except Exception as e:
        print(f"检查施工模式数据库表失败: {e}")
        existing_tables = []

    if mode == "steel_cage":
        # 尝试多个可能的英文表名
        possible_names = ["construction_parameter_table", "price_baseline_1", "steel_cage"]
        table_name = None
        
        for name in possible_names:
            if name in existing_tables:
                table_name = name
                break
        
        # 如果没有找到，使用第一个可用的表（如果存在）
        if not table_name and existing_tables:
            table_name = existing_tables[0]
            print(f"警告：未找到钢筋笼模式表，使用默认表: {table_name}")
        
        if table_name:
            return {
                "table_name": table_name,
                "display_name": "钢筋笼施工模式",
                "use_mode_db": True,  # 标记使用施工模式数据库
                "columns": translate_schema_columns([
                    {"id": "sequence_number", "name": "序号", "type": "numeric"},
                    {"id": "mode", "name": "施工模式", "type": "text"},
                    {"id": "parameter_category", "name": "参数类别", "type": "text"},
                    {"id": "engineering_parameter", "name": "工程参数", "type": "text"},
                    {"id": "unit", "name": "单位", "type": "text"},
                    {"id": "direct_labor_unit_price", "name": "直接施工人工单价", "type": "numeric"},
                    {"id": "direct_material_unit_price", "name": "直接施工材料单价", "type": "numeric"},
                    {"id": "direct_machinery_unit_price", "name": "直接施工机械单价", "type": "numeric"},
                    {"id": "modular_labor_unit_price", "name": "模块化施工人工单价", "type": "numeric"},
                    {"id": "modular_material_unit_price", "name": "模块化施工材料单价", "type": "numeric"},
                    {"id": "modular_machinery_unit_price", "name": "模块化施工机械单价", "type": "numeric"},
                    {"id": "timestamp", "name": "更新时间", "type": "text"},
                ])
            }
        else:
            print("错误：未找到钢筋笼施工模式对应的表")
            return None
            
    elif mode == "steel_lining":
        # 尝试多个可能的英文表名
        possible_names = ["steel_lining", "钢衬里", "price_baseline_2"]
        table_name = None
        
        for name in possible_names:
            if name in existing_tables:
                table_name = name
                break
        
        # 如果没有找到，使用第二个可用的表（如果存在）
        if not table_name and len(existing_tables) > 1:
            table_name = existing_tables[1]
            print(f"警告：未找到钢衬里模式表，使用默认表: {table_name}")
        elif not table_name and existing_tables:
            table_name = existing_tables[0]
            print(f"警告：未找到钢衬里模式表，使用默认表: {table_name}")
        
        if table_name:
            return {
                "table_name": table_name,
                "display_name": "钢衬里施工模式",
                "use_mode_db": True,  # 标记使用施工模式数据库
                "columns": translate_schema_columns([
                    {"id": "sequence_number", "name": "序号", "type": "numeric"},
                    {"id": "mode", "name": "施工模式", "type": "text"},
                    {"id": "parameter_category", "name": "参数类别", "type": "text"},
                    {"id": "engineering_parameter", "name": "工程参数", "type": "text"},
                    {"id": "unit", "name": "单位", "type": "text"},
                    {"id": "direct_labor_unit_price", "name": "直接施工人工单价", "type": "numeric"},
                    {"id": "direct_material_unit_price", "name": "直接施工材料单价", "type": "numeric"},
                    {"id": "direct_machinery_unit_price", "name": "直接施工机械单价", "type": "numeric"},
                    {"id": "modular_labor_unit_price", "name": "模块化施工人工单价", "type": "numeric"},
                    {"id": "modular_material_unit_price", "name": "模块化施工材料单价", "type": "numeric"},
                    {"id": "modular_machinery_unit_price", "name": "模块化施工机械单价", "type": "numeric"},
                    {"id": "timestamp", "name": "更新时间", "type": "text"},
                ])
            }
        else:
            print("错误：未找到钢衬里施工模式对应的表")
            return None
    
    return None

# 自然排序函数 - 用于项目名称排序
def natural_sort_key(text):
    """
    将项目名称转换为自然排序键
    处理英文表名的排序
    """
    def convert(text):
        # 提取数字部分
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # 处理英文表名的排序逻辑
        if 'one' in text.lower():
            return 1
        elif 'two' in text.lower():
            return 2
        elif 'three' in text.lower():
            return 3
        elif 'four' in text.lower():
            return 4
        elif 'five' in text.lower():
            return 5
        
        return 999
    
    return convert(text)

# 获取所有项目表名，返回给下拉框用（修改：适配英文表名）
def get_all_project_tables(mode=None):
    """获取所有项目表名，支持根据模式选择数据库"""
    try:
        # 定义每个模式应该包含的表
        MODE_TABLES = {
            'steel_cage': [
                'project_one', 
                'project_two_sub_one', 
                'project_two_shared_params', 
                'project_two_sub_three', 
                'project_two_sub_two', 
                'project_three'
            ],
            'steel_lining': [
                'project_four', 
                'project_five'
            ]
        }
        
        # 获取当前模式应该显示的表
        allowed_tables = MODE_TABLES.get(mode, [])
        
        if not allowed_tables:
            print(f"未找到模式 {mode} 对应的表配置")
            return []
        
        # 连接数据库验证表是否存在
        conn = get_db_connection(mode)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        all_existing_tables = cursor.fetchall()
        conn.close()
        
        # 提取现有表名
        existing_table_names = set()
        for table in all_existing_tables:
            table_name = list(table.values())[0] if isinstance(table, dict) else table[0]
            existing_table_names.add(table_name)
        
        # 只保留数据库中实际存在的表
        tables = []
        for table_name in allowed_tables:
            if table_name in existing_table_names:
                tables.append(table_name)
            else:
                print(f"警告：表 {table_name} 在数据库中不存在")
        
        # 构建下拉框选项，包含表名和记录数，显示中文名称
        options = []
        table_list = []
        
        for table_name in tables:
            record_count = get_table_record_count(table_name, mode)  # 传入模式参数
            chinese_name = translate_history_table_name(table_name)
            label = f"{chinese_name} ({record_count}条记录)"
            table_list.append({
                "label": label, 
                "value": table_name,  # 保持英文值用于数据库操作
                "sort_key": natural_sort_key(table_name)
            })
        
        # 按照自然排序键排序
        table_list.sort(key=lambda x: x["sort_key"])
        
        # 转换为最终格式
        for item in table_list:
            options.append({"label": item["label"], "value": item["value"]})
        
        print(f"获取到{mode or '默认'}模式的{len(options)}个项目表: {[t['value'] for t in options]}")
        return options
    except Exception as e:
        print(f"获取项目表列表失败: {e}")
        return []
    
# 获取表的记录数量
def get_table_record_count(table_name, mode=None):
    """获取表的记录数量，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
        result = cursor.fetchone()
        conn.close()
        return result["count"] if result else 0
    except Exception as e:
        print(f"获取表 {table_name} 记录数失败: {e}")
        return 0

# 修改现有的 dynamic_get_schema_from_table() 函数，增加模式参数
def dynamic_get_schema_from_table(table_name, mode=None):
    """动态从表名获取表结构，支持不同模式数据库"""
    try:
        # 首先检查表是否存在
        if not table_exists(table_name, mode):  # 传入模式参数
            print(f"警告：表 {table_name} 不存在")
            return None
            
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        conn.close()

        if not columns_info:
            print(f"警告：表 {table_name} 没有列信息")
            return None

        columns = []
        for col in columns_info:
            # col['Field'] 是列名, col['Type'] 是数据类型
            col_name = col['Field']
            col_type_str = col['Type'].upper()
            
            # 根据数据类型判断列类型
            if any(t in col_type_str for t in ['INT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'NUMERIC']):
                col_type = 'numeric'
            else:
                col_type = 'text'
            
            columns.append({
                "id": col_name, 
                "name": translate_history_field_name(col_name),  # 翻译为中文显示
                "type": col_type
            })
        
        chinese_table_name = translate_history_table_name(table_name)
        return {
            "table_name": table_name, 
            "columns": columns,
            "display_name": f"项目表: {chinese_table_name}",
            "mode": mode  # 记录使用的模式
        }
    except Exception as e:
        print(f"获取表 {table_name} 结构失败: {e}")
        return None

# 获取表数据，支持模糊搜索（改进：支持施工模式数据库和翻译）
def get_table_data(table_name, search_term=None, use_mode_db=False, mode=None):
    """获取表数据，支持模糊搜索和不同模式数据库"""
    try:
        # MySQL版本中所有数据都在同一个数据库中
        conn = get_db_connection(mode)
        print(f"使用MySQL数据库获取表 {table_name} 数据")
        
        # 检查表是否存在
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        
        if not cursor.fetchone():
            print(f"警告：表 {table_name} 不存在")
            conn.close()
            return []
        
        if search_term and search_term.strip():
            # 先获取表的列信息，用于构建搜索条件
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = cursor.fetchall()
            
            # 构建搜索条件 - 对所有文本类型的列进行模糊搜索
            search_conditions = []
            search_params = []
            pattern = f"%{search_term.strip()}%"
            
            for col in columns_info:
                col_name = col['Field']
                col_type = col['Type'].upper()
                
                # 对文本类型和可能包含文本的列进行搜索
                if not any(t in col_type for t in ['DECIMAL', 'FLOAT', 'DOUBLE']) or col_name in ['mode', 'parameter_category', 'engineering_parameter', 'unit']:
                    search_conditions.append(f"`{col_name}` LIKE %s")
                    search_params.append(pattern)
            
            if search_conditions:
                # 使用英文字段名进行查询，但优先使用sequence_number排序
                order_field = "sequence_number" if "sequence_number" in [col['Field'] for col in columns_info] else list(columns_info)[0]['Field']
                query = f"SELECT * FROM `{table_name}` WHERE {' OR '.join(search_conditions)} ORDER BY `{order_field}`"
                cursor.execute(query, search_params)
            else:
                # 如果没有可搜索的列，返回所有数据
                order_field = "sequence_number" if "sequence_number" in [col['Field'] for col in columns_info] else list(columns_info)[0]['Field']
                query = f"SELECT * FROM `{table_name}` ORDER BY `{order_field}`"
                cursor.execute(query)
        else:
            # 获取列信息用于排序
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = cursor.fetchall()
            order_field = "sequence_number" if "sequence_number" in [col['Field'] for col in columns_info] else list(columns_info)[0]['Field']
            query = f"SELECT * FROM `{table_name}` ORDER BY `{order_field}`"
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表，并翻译字段名为中文显示
        result = []
        for row in rows:
            item = {}
            for key, value in row.items():
                # 翻译字段名为中文
                chinese_key = translate_history_field_name(key)
                # 处理空值
                if value is None:
                    item[chinese_key] = ""
                else:
                    item[chinese_key] = value
            result.append(item)
        
        print(f"成功获取表 {table_name} 数据: {len(result)} 条记录")
        return result
    except Exception as e:
        print(f"获取表 {table_name} 数据失败: {e}")
        return []

# 获取下一个可用的ID（改进：处理不存在的表和不同的ID列名）
def get_next_id(table_name, mode=None):
    """获取下一个可用的ID，支持不同模式数据库"""
    try:
        # 首先检查表是否存在
        if not table_exists(table_name, mode):
            print(f"警告：表 {table_name} 不存在，返回默认ID")
            return 1
            
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        
        # 检查是否有"sequence_number"列（英文字段名）
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        column_names = [col['Field'] for col in columns_info]
        
        if "sequence_number" in column_names:
            cursor.execute(f"SELECT MAX(`sequence_number`) as max_id FROM `{table_name}`")
        elif "id" in column_names:
            cursor.execute(f"SELECT MAX(`id`) as max_id FROM `{table_name}`")
        elif "ID" in column_names:
            cursor.execute(f"SELECT MAX(`ID`) as max_id FROM `{table_name}`")
        else:
            # MySQL中没有ROWID概念，使用AUTO_INCREMENT主键
            cursor.execute(f"SELECT MAX(id) as max_id FROM `{table_name}`")
        
        result = cursor.fetchone()
        conn.close()
        
        max_id = result["max_id"] if result and result["max_id"] else 0
        return max_id + 1
    except Exception as e:
        print(f"获取表 {table_name} 下一个ID失败: {e}")
        return 1

# 添加新记录（修改：支持字段名翻译）
def add_record(table_name, record_data, mode=None):
    """添加新记录，支持不同模式数据库"""
    try:
        # 将中文字段名转换为英文字段名
        english_record_data = reverse_translate_record_data(record_data)
        
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor()
        
        # 构建插入语句
        columns = list(english_record_data.keys())
        placeholders = ', '.join(['%s' for _ in columns])  # MySQL使用%s作为占位符
        values = list(english_record_data.values())
        
        # 使用反引号包围表名和列名以防止SQL注入
        column_names = ', '.join([f'`{col}`' for col in columns])
        query = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"添加记录到表 {table_name} 失败: {e}")
        return False

# 更新记录（修改：支持字段名翻译）
def update_record(table_name, record_id, record_data, mode=None):
    """更新记录，支持不同模式数据库"""
    try:
        # 将中文字段名转换为英文字段名
        english_record_data = reverse_translate_record_data(record_data)
        
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor()
        
        # 构建更新语句
        set_clauses = [f"`{col}` = %s" for col in english_record_data.keys()]  # MySQL使用%s
        values = list(english_record_data.values()) + [record_id]
        
        # 使用英文字段名作为WHERE条件
        id_field = "sequence_number"  # 默认使用sequence_number作为主键
        query = f"UPDATE `{table_name}` SET {', '.join(set_clauses)} WHERE `{id_field}` = %s"
        cursor.execute(query, values)
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows > 0
    except Exception as e:
        print(f"更新表 {table_name} 记录失败: {e}")
        return False

# 删除记录（修改2：返回删除的记录数据以支持撤回功能）
def delete_record(table_name, record_id, mode=None):
    """删除记录，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        
        # 使用英文字段名查询
        id_field = "sequence_number"  # 默认使用sequence_number作为主键
        cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{id_field}` = %s", (record_id,))
        deleted_record = cursor.fetchone()
        
        if deleted_record:
            # 执行删除
            cursor.execute(f"DELETE FROM `{table_name}` WHERE `{id_field}` = %s", (record_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            if affected_rows > 0:
                # 翻译删除的记录字段名为中文
                translated_deleted_record = translate_record_data(deleted_record)
                return True, translated_deleted_record
            else:
                return False, None
        else:
            conn.close()
            return False, None
            
    except Exception as e:
        print(f"删除表 {table_name} 记录失败: {e}")
        return False, None

# 恢复删除的记录（修改2：新增撤回功能）
def restore_deleted_record(table_name, deleted_data, mode=None):
    """恢复删除的记录，支持不同模式数据库"""
    try:
        return add_record(table_name, deleted_data, mode)  # 传入模式参数
    except Exception as e:
        print(f"恢复表 {table_name} 记录失败: {e}")
        return False

# 检查表是否存在
def table_exists(table_name, mode=None):
    """检查表是否存在，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"检查表 {table_name} 是否存在失败: {e}")
        return False

# 获取单条记录详情
def get_record_by_id(table_name, record_id, mode=None):
    """获取单条记录详情，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        
        id_field = "sequence_number"  # 默认使用sequence_number作为主键
        cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{id_field}` = %s", (record_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # 翻译字段名为中文
            return translate_record_data(result)
        return None
    except Exception as e:
        print(f"获取表 {table_name} 记录 {record_id} 失败: {e}")
        return None

# 批量删除记录
def delete_multiple_records(table_name, record_ids, mode=None):
    """批量删除记录，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor()
        
        # 构建批量删除语句
        placeholders = ', '.join(['%s' for _ in record_ids])  # MySQL使用%s
        id_field = "sequence_number"  # 默认使用sequence_number作为主键
        query = f"DELETE FROM `{table_name}` WHERE `{id_field}` IN ({placeholders})"
        
        cursor.execute(query, record_ids)
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        return affected_rows
    except Exception as e:
        print(f"批量删除表 {table_name} 记录失败: {e}")
        return 0

# 复制记录
def duplicate_record(table_name, record_id, mode=None):
    """复制记录，支持不同模式数据库"""
    try:
        # 获取原记录
        original_record = get_record_by_id(table_name, record_id, mode)  # 传入模式参数
        if not original_record:
            return False
        
        # 移除序号和时间戳，让系统自动生成
        new_record = original_record.copy()
        chinese_id_field = translate_history_field_name("sequence_number")
        chinese_timestamp_field = translate_history_field_name("timestamp")
        
        if chinese_id_field in new_record:
            del new_record[chinese_id_field]
        new_record[chinese_timestamp_field] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 分配新的序号
        new_record[chinese_id_field] = get_next_id(table_name, mode)  # 传入模式参数
        
        # 添加新记录
        return add_record(table_name, new_record, mode)  # 传入模式参数
    except Exception as e:
        print(f"复制表 {table_name} 记录 {record_id} 失败: {e}")
        return False

# 获取表的所有列名
def get_table_columns(table_name, mode=None):
    """获取表的所有列名，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        conn.close()
        
        # 返回英文列名
        return [col['Field'] for col in columns_info]  # col['Field'] 是列名
    except Exception as e:
        print(f"获取表 {table_name} 列名失败: {e}")
        return []

# 验证记录数据
def validate_record_data(table_name, record_data, mode=None):
    """验证记录数据的有效性，支持不同模式数据库"""
    try:
        # 将中文字段名转换为英文
        english_record_data = reverse_translate_record_data(record_data)
        
        # 获取表的列信息
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        conn.close()
        
        errors = []
        
        for col in columns_info:
            col_name = col['Field']
            col_type = col['Type'].upper()
            not_null = col['Null'] == 'NO'  # MySQL中Null字段表示是否允许NULL
            
            if col_name in english_record_data:
                value = english_record_data[col_name]
                
                # 检查非空约束
                if not_null and (value is None or str(value).strip() == ''):
                    chinese_col_name = translate_history_field_name(col_name)
                    errors.append(f"字段 '{chinese_col_name}' 不能为空")
                
                # 检查数值类型
                if any(t in col_type for t in ['INT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'NUMERIC']) and value:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        chinese_col_name = translate_history_field_name(col_name)
                        errors.append(f"字段 '{chinese_col_name}' 必须为数值类型")
        
        return len(errors) == 0, errors
    except Exception as e:
        return False, [f"验证失败: {str(e)}"]

# 导出表数据为字典格式
def export_table_data(table_name, format='dict', mode=None):
    """导出表数据，支持多种格式和不同模式数据库"""
    try:
        data = get_table_data(table_name, mode=mode)  # 传入模式参数
        
        if format == 'dict':
            return data
        elif format == 'list':
            if not data:
                return []
            # 返回列表格式，第一行为表头
            headers = list(data[0].keys())
            result = [headers]
            for row in data:
                result.append([row.get(header, '') for header in headers])
            return result
        else:
            return data
    except Exception as e:
        print(f"导出表 {table_name} 数据失败: {e}")
        return []

# 统计表数据
def get_table_statistics(table_name, mode=None):
    """获取表的统计信息，支持不同模式数据库"""
    try:
        conn = get_db_connection(mode)  # 传入模式参数
        cursor = conn.cursor(dictionary=True)
        
        # 基本统计
        cursor.execute(f"SELECT COUNT(*) as total_records FROM `{table_name}`")
        total_records = cursor.fetchone()["total_records"]
        
        # 获取数值列的统计信息
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns_info = cursor.fetchall()
        
        numeric_stats = {}
        for col in columns_info:
            col_name = col['Field']
            col_type = col['Type'].upper()
            
            if any(t in col_type for t in ['INT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'NUMERIC']) and 'price' in col_name:
                try:
                    cursor.execute(f"""
                        SELECT 
                            AVG(`{col_name}`) as avg_val,
                            MIN(`{col_name}`) as min_val,
                            MAX(`{col_name}`) as max_val,
                            SUM(`{col_name}`) as sum_val
                        FROM `{table_name}` 
                        WHERE `{col_name}` IS NOT NULL AND `{col_name}` != ''
                    """)
                    stats = cursor.fetchone()
                    if stats:
                        chinese_col_name = translate_history_field_name(col_name)
                        numeric_stats[chinese_col_name] = {
                            'average': round(float(stats['avg_val']) if stats['avg_val'] else 0, 2),
                            'minimum': float(stats['min_val']) if stats['min_val'] else 0,
                            'maximum': float(stats['max_val']) if stats['max_val'] else 0,
                            'total': round(float(stats['sum_val']) if stats['sum_val'] else 0, 2)
                        }
                except Exception as e:
                    print(f"统计列 {col_name} 失败: {e}")
        
        conn.close()
        
        return {
            'total_records': total_records,
            'numeric_statistics': numeric_stats,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"获取表 {table_name} 统计信息失败: {e}")
        return {
            'total_records': 0,
            'numeric_statistics': {},
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    