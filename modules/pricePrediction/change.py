import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import urllib.parse

# 导入MySQL配置和连接函数
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

def load_table_from_db(table_name: str):
    """
    从 MySQL 数据库的指定表中加载数据到 pandas DataFrame。

    参数:
        table_name (str): 要读取的表的名称。

    返回:
        pandas.DataFrame: 包含表数据的 DataFrame，如果出错则退出程序。
    """
    conn = None
    try:
        conn = get_connection()
        query = f"SELECT * FROM `{table_name}`"
        df = pd.read_sql_query(query, conn)
        return df
    except mysql.connector.Error as e:
        print(f"MySQL数据库错误 (读取表 '{table_name}'): {e}")
        exit()
    except Exception as e:
        print(f"读取表 '{table_name}' 时发生错误: {e}")
        if "doesn't exist" in str(e).lower():
            print(f"请确认表名 '{table_name}' 在MySQL数据库中是正确的。")
        exit()
    finally:
        if conn:
            conn.close()

def get_sqlalchemy_engine():
    """
    创建SQLAlchemy引擎用于pandas的to_sql方法
    """
    try:
        # URL编码密码以处理特殊字符
        password = urllib.parse.quote_plus(MYSQL_CONFIG['password'])
        
        # 构建连接字符串
        connection_string = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{password}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}?charset={MYSQL_CONFIG['charset']}"
        
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"创建SQLAlchemy引擎失败: {e}")
        return None

def process_and_update_databases(
    table1_name: str,
    project_col_db1: str,
    param_category_col_db1: str,
    material_quantity_col_db1: str,
    target_param_category_value: str,
    table2_name: str,
    project_col_db2: str,
    target_sum_col_db2: str,
    output_table_name: str,
    if_exists_behavior: str = 'replace'
) -> bool:
    """
    从MySQL数据库读取数据，处理数据，并将结果写入指定表中。

    参数:
        table1_name (str): 第一个源数据表的名称。
        project_col_db1 (str): table1中表示项目的列名。
        param_category_col_db1 (str): table1中表示参数类别的列名。
        material_quantity_col_db1 (str): table1中表示模块化施工材料工程量的列名。
        target_param_category_value (str): table1中参数类别列要筛选的值 (例如 '钢筋吨数')。
        table2_name (str): 第二个目标数据表的名称。
        project_col_db2 (str): table2中表示项目的列名 (用于匹配)。
        target_sum_col_db2 (str): table2中需要更新的总数/吨数列名。
        output_table_name (str): 保存更新后数据的表名。
        if_exists_behavior (str): 当输出表已存在时的行为 ('fail', 'replace', 'append')。
                                 默认为 'replace'。

    返回:
        bool: 如果成功完成则返回 True，否则返回 False。
    """
    print("--- 开始数据处理 ---")

    # --- 步骤 1: 从表1读取数据并处理 ---
    print(f"正在从MySQL数据库表 '{table1_name}' 读取数据...")
    df1 = load_table_from_db(table1_name)

    required_cols_df1 = [project_col_db1, param_category_col_db1, material_quantity_col_db1]
    for col in required_cols_df1:
        if col not in df1.columns:
            print(f"错误: 列 '{col}' 在表 '{table1_name}' 中未找到。")
            print(f"可用列为: {df1.columns.tolist()}")
            return False

    df1_filtered = df1[df1[param_category_col_db1] == target_param_category_value]
    if df1_filtered.empty:
        print(f"警告: 在表 '{table1_name}' 中未找到参数类别为 '{target_param_category_value}' 的数据。")
    
    df1_extracted = df1_filtered[[project_col_db1, material_quantity_col_db1]].copy()
    df1_extracted[material_quantity_col_db1] = pd.to_numeric(df1_extracted[material_quantity_col_db1], errors='coerce')
    df1_extracted.dropna(subset=[material_quantity_col_db1], inplace=True)

    if df1_extracted.empty:
        print(f"警告: 筛选和转换后，从 '{table1_name}' 中没有有效的 '{material_quantity_col_db1}' 数据用于聚合。")
        project_material_sum = pd.DataFrame(columns=[project_col_db1, 'calculated_sum'])
    else:
        project_material_sum = df1_extracted.groupby(project_col_db1)[material_quantity_col_db1].sum().reset_index()
        project_material_sum.rename(columns={material_quantity_col_db1: 'calculated_sum'}, inplace=True)

    print("--- 从表1计算得到的项目材料总量 ---")
    print(project_material_sum if not project_material_sum.empty else "无数据可聚合。")
    print("\n")

    # --- 步骤 2: 从表2读取数据 ---
    print(f"正在从MySQL数据库表 '{table2_name}' 读取数据...")
    df2 = load_table_from_db(table2_name)

    # 检查项目列和目标更新列是否存在于df2
    if project_col_db2 not in df2.columns:
        print(f"错误: 项目匹配列 '{project_col_db2}' 在表 '{table2_name}' 中未找到。")
        print(f"可用列为: {df2.columns.tolist()}")
        return False
    if target_sum_col_db2 not in df2.columns:
        print(f"警告: 目标更新列 '{target_sum_col_db2}' 在表 '{table2_name}' 中未找到。将创建此列。")
        df2[target_sum_col_db2] = pd.NA

    # --- 步骤 3: 将计算结果合并到表2的数据中 ---
    df2_updated = pd.merge(df2, project_material_sum, left_on=project_col_db2, right_on=project_col_db1, how='left')

    # --- 步骤 4: 更新目标列 ---
    update_mask = df2_updated['calculated_sum'].notna()
    df2_updated.loc[update_mask, target_sum_col_db2] = df2_updated['calculated_sum']

    # 移除合并时产生的辅助列
    if project_col_db1 in df2_updated.columns and project_col_db1 != project_col_db2:
        df2_updated.drop(columns=[project_col_db1], inplace=True)
    if 'calculated_sum' in df2_updated.columns:
        df2_updated.drop(columns=['calculated_sum'], inplace=True)

    print("--- 更新后的数据预览 (准备写入数据库) ---")
    print(df2_updated.head())
    print("\n")

    # --- 步骤 5: 将更新后的数据保存到MySQL数据库的表中 ---
    try:
        engine = get_sqlalchemy_engine()
        if engine is None:
            print("无法创建数据库引擎，保存失败。")
            return False
            
        df2_updated.to_sql(output_table_name, engine, if_exists=if_exists_behavior, index=False, method='multi')
        print(f"处理完成！更新后的数据已保存到MySQL数据库的表 '{output_table_name}' 中。")
        if if_exists_behavior == 'replace' and output_table_name == table2_name:
            print(f"警告: 原有表 '{table2_name}' 在MySQL数据库中已被替换。")
        return True
    except mysql.connector.Error as e:
        print(f"MySQL数据库错误 (写入表 '{output_table_name}'): {e}")
        return False
    except Exception as e:
        print(f"保存到MySQL数据库表 '{output_table_name}' 时出错: {e}")
        return False

def create_sample_tables_for_testing():
    """
    创建示例表用于测试（可选函数）
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 创建示例表1
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `price_baseline_1` (
            `project` VARCHAR(100),
            `parameter_category` VARCHAR(100),
            `modular_material_quantity` DECIMAL(10,2),
            `other_data1` INT
        )
        """)
        
        # 创建示例表2  
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `key_factors_1` (
            `project_id` VARCHAR(100),
            `total_rebar_tonnage` DECIMAL(10,2),
            `other_data2` VARCHAR(100)
        )
        """)
        
        # 插入示例数据到表1
        sample_data1 = [
            ('ProjectA', 'rebar_tonnage', 10.0, 1),
            ('ProjectA', 'concrete_volume', 50.0, 2), 
            ('ProjectB', 'rebar_tonnage', 15.0, 3),
            ('ProjectA', 'rebar_tonnage', 5.0, 4),
            ('ProjectC', 'other', 20.0, 5)
        ]
        
        cursor.execute("DELETE FROM `price_baseline_1`")
        cursor.executemany(
            "INSERT INTO `price_baseline_1` (`project`, `parameter_category`, `modular_material_quantity`, `other_data1`) VALUES (%s, %s, %s, %s)",
            sample_data1
        )
        
        # 插入示例数据到表2
        sample_data2 = [
            ('ProjectA', 15.0, 'infoA'),
            ('ProjectB', 22.0, 'infoB'),
            ('ProjectD', 18.5, 'infoD')
        ]
        
        cursor.execute("DELETE FROM `key_factors_1`")  # 清空表
        cursor.executemany(
            "INSERT INTO `key_factors_1` (`project_id`, `total_rebar_tonnage`, `other_data2`) VALUES (%s, %s, %s)",
            sample_data2
        )
        
        conn.commit()
        print("示例表和数据创建完成。")
        
    except mysql.connector.Error as e:
        print(f"创建示例表时出错: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"创建示例表时发生错误: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- 如何调用这个函数 (示例) ---
if __name__ == '__main__':
    # --- 配置参数 (不再需要数据库文件路径) ---
    
    # 表1 (源数据)
    db1_table = 'price_baseline_1'  # 原来是 '价格基准1'
    db1_proj_col = 'project'  # 原来是 '项目'
    db1_param_col = 'parameter_category'  # 原来是 '参数类别'
    db1_qty_col = 'modular_material_quantity'  # 原来是 '模块化施工材料工程量'
    db1_target_val = 'rebar_tonnage'  # 原来是 '钢筋吨数'

    # 表2 (目标数据)
    db2_table = 'key_factors_1'  # 原来是 '关键因素1'
    db2_proj_col = 'project_id'  # 原来是 '项目ID'
    db2_target_sum_col = 'total_rebar_tonnage'  # 原来是 '钢筋总吨数'

    # 输出配置
    output_target_table = 'final_project_summary1'
    # if_exists_options: 'fail' (如果表存在则失败), 'replace' (删除旧表,创建新表), 'append' (追加到旧表)
    output_if_exists = 'replace'

    # --- 可选：创建示例表和数据用于测试 ---
    print("正在创建示例表和数据 (仅用于测试)...")
    create_sample_tables_for_testing()
    print("示例表和数据创建完成。")

    # 调用主函数
    success = process_and_update_databases(
        table1_name=db1_table,
        project_col_db1=db1_proj_col,
        param_category_col_db1=db1_param_col,
        material_quantity_col_db1=db1_qty_col,
        target_param_category_value=db1_target_val,
        table2_name=db2_table,
        project_col_db2=db2_proj_col,
        target_sum_col_db2=db2_target_sum_col,
        output_table_name=output_target_table,
        if_exists_behavior=output_if_exists
    )

    if success:
        print("函数执行成功。")
        # 你可以在这里添加代码来验证输出表的内容
        try:
            df_check = load_table_from_db(output_target_table)
            print("\n--- 验证输出表内容 ---")
            print(df_check)
        except:
            print("无法验证输出表内容，可能表不存在或读取失败。")
    else:
        print("函数执行失败。")