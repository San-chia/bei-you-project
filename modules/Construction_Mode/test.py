import sqlite3
from db_connection import get_connection
import pandas as pd
# ================== 简单调试函数 ==================
def debug_specific_params():
    """调试具体的参数查询问题"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== 参数查询调试 ===")
    
    # 1. 检查表是否存在且有数据
    try:
        cursor.execute('SELECT COUNT(*) FROM "施工参数整理表"')
        total_count = cursor.fetchone()[0]
        print(f"施工参数整理表总记录数: {total_count}")
        
        if total_count == 0:
            print("错误：表中没有数据！")
            conn.close()
            return
    except Exception as e:
        print(f"查询表失败: {e}")
        conn.close()
        return
    
    # 2. 检查有哪些模式
    try:
        cursor.execute('SELECT DISTINCT " 模式 " FROM "施工参数整理表"')
        modes = [row[0] for row in cursor.fetchall()]
        print(f"可用的模式: {modes}")
    except Exception as e:
        print(f"查询模式失败: {e}")
    
    # 3. 检查钢筋笼模式下的参数
    try:
        cursor.execute('SELECT DISTINCT " 工程参数 " FROM "施工参数整理表" WHERE " 模式 " = ? LIMIT 20', ("钢筋笼",))
        params = [row[0] for row in cursor.fetchall()]
        print(f"钢筋笼模式下的参数 (前20个):")
        for i, param in enumerate(params, 1):
            print(f"  {i}. '{param}'")
    except Exception as e:
        print(f"查询钢筋笼参数失败: {e}")
    
    # 4. 搜索包含"钢筋"的参数
    try:
        cursor.execute('SELECT " 工程参数 " FROM "施工参数整理表" WHERE " 工程参数 " LIKE ? LIMIT 10', ("%钢筋%",))
        steel_params = [row[0] for row in cursor.fetchall()]
        print(f"包含'钢筋'的参数:")
        for param in steel_params:
            print(f"  '{param}'")
    except Exception as e:
        print(f"搜索钢筋参数失败: {e}")
    
    # 5. 测试具体参数查询
    test_params = ["Q235B钢筋(现浇构件钢筋)", "水平钢筋绑扎", "竖向钢筋绑扎", "拉筋绑扎"]
    
    for param in test_params:
        print(f"\n--- 测试参数: '{param}' ---")
        
        # 精确匹配
        cursor.execute('SELECT COUNT(*) FROM "施工参数整理表" WHERE " 模式 " = ? AND " 工程参数 " = ?', ("钢筋笼", param))
        exact_count = cursor.fetchone()[0]
        print(f"  精确匹配 (钢筋笼 + {param}): {exact_count} 条")
        
        # 模糊匹配
        param_clean = param.strip()
        cursor.execute('SELECT COUNT(*) FROM "施工参数整理表" WHERE " 工程参数 " LIKE ?', (f"%{param_clean}%",))
        fuzzy_count = cursor.fetchone()[0]
        print(f"  模糊匹配 ({param_clean}): {fuzzy_count} 条")
        
        if fuzzy_count > 0:
            cursor.execute('SELECT " 工程参数 ", " 模式 " FROM "施工参数整理表" WHERE " 工程参数 " LIKE ? LIMIT 3', (f"%{param_clean}%",))
            similar = cursor.fetchall()
            print(f"  相似结果:")
            for sim in similar:
                print(f"    模式:'{sim[1]}' 参数:'{sim[0]}'")
    
    conn.close()

# ================== 修复后的计算函数 ==================
def calculate_cost_robust(mode, params_dict, others):
    """更健壮的成本计算函数"""
    conn = get_connection()
    
    # 初始化结果
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
        "明细": []
    }
    
    print(f"开始计算，模式: {mode}")
    print(f"参数列表: {list(params_dict.keys())}")
    
    # 逐个处理每个参数
    for param, quantity in params_dict.items():
        print(f"\n处理参数: '{param}'")
        
        # 尝试多种查询方式
        queries = [
            # 1. 精确匹配
            ('SELECT * FROM "施工参数整理表" WHERE " 模式 " = ? AND " 工程参数 " = ?', [mode, param]),
            # 2. 去除前后空格后精确匹配
            ('SELECT * FROM "施工参数整理表" WHERE " 模式 " = ? AND " 工程参数 " = ?', [mode, param.strip()]),
            # 3. 模糊匹配（包含模式）
            ('SELECT * FROM "施工参数整理表" WHERE " 模式 " = ? AND " 工程参数 " LIKE ?', [mode, f'%{param.strip()}%']),
            # 4. 仅参数模糊匹配（忽略模式）
            ('SELECT * FROM "施工参数整理表" WHERE " 工程参数 " LIKE ?', [f'%{param.strip()}%']),
            # 5. 更宽松的匹配（去掉括号内容）
            ('SELECT * FROM "施工参数整理表" WHERE " 工程参数 " LIKE ?', [f'%{param.split("(")[0].strip()}%'])
        ]
        
        param_df = pd.DataFrame()
        used_query = None
        
        for i, (query, params_list) in enumerate(queries):
            try:
                param_df = pd.read_sql(query, conn, params=params_list)
                if not param_df.empty:
                    used_query = i + 1
                    print(f"  ✓ 查询方式 {used_query} 成功: {len(param_df)} 条结果")
                    break
            except Exception as e:
                print(f"  ✗ 查询方式 {i+1} 失败: {e}")
        
        if not param_df.empty:
            # 如果有多个结果，选择第一个
            row = param_df.iloc[0]
            found_param = row[" 工程参数 "]
            found_mode = row[" 模式 "]
            print(f"  使用数据: 模式='{found_mode}', 参数='{found_param}'")
            
            try:
                # 确保数量是有效数值
                quantity_str = str(quantity).strip() if quantity is not None else ""
                quantity = float(quantity_str) if quantity_str else 0
                
                # 安全地获取单价
                def safe_float(value):
                    if pd.isna(value) or value is None:
                        return 0.0
                    try:
                        if isinstance(value, str):
                            value = value.strip()
                            if not value:
                                return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        print(f"    警告: 无法转换值 '{value}' 为浮点数，使用0代替")
                        return 0.0
                
                # 获取并转换单价
                direct_labor_unit = safe_float(row[" 直接施工人工单价 "])
                direct_material_unit = safe_float(row[" 直接施工材料单价 "])
                direct_machine_unit = safe_float(row[" 直接施工机械单价 "])
                direct_others_unit = safe_float(others.get("直接施工间接费", 0))
                
                modular_labor_unit = safe_float(row[" 模块化施工人工单价 "])
                modular_material_unit = safe_float(row[" 模块化施工材料单价 "])
                modular_machine_unit = safe_float(row[" 模块化施工机械单价 "])
                modular_others_unit = safe_float(others.get("模块化施工间接费", 0))
                
                print(f"  单价信息: 直接施工(人工:{direct_labor_unit}, 材料:{direct_material_unit}, 机械:{direct_machine_unit})")
                print(f"           模块化施工(人工:{modular_labor_unit}, 材料:{modular_material_unit}, 机械:{modular_machine_unit})")
                
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
                
                # 添加明细
                result["明细"].append({
                    "参数": param,
                    "实际匹配": found_param,
                    "数量": quantity,
                    "参数类别": row.get("参数类别", row.get(" 参数类别 ", "")),
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
                
                print(f"  ✓ 计算完成: 直接施工={direct_total:.2f}, 模块化施工={modular_total:.2f}")
                
            except Exception as e:
                print(f"  ✗ 计算参数 '{param}' 成本时出错: {e}")
        else:
            print(f"  ✗ 警告: 未找到参数 '{param}' 的价格数据")
    
    # 四舍五入总计结果
    for method in ["直接施工", "模块化施工"]:
        for cost_type in ["人工费", "材料费", "机械费", "总计"]:
            result[method][cost_type] = round(result[method][cost_type], 2)
    
    conn.close()
    print(f"\n计算完成，共处理 {len(result['明细'])} 个参数")
    return result

# ================== 使用方法 ==================
# 第一步：运行调试查看具体问题
# debug_specific_params()

# 第二步：使用更健壮的计算函数
# 在您的代码中替换 calculate_cost 为 calculate_cost_robust
def quick_test_fix():
    """快速测试修复"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 查看表的前3行原始数据
    print("=== 原始数据查看 ===")
    cursor.execute('SELECT * FROM "施工参数整理表" LIMIT 3')
    rows = cursor.fetchall()
    
    for i, row in enumerate(rows):
        print(f"行 {i+1}: {row}")
    
    # 2. 查看列名
    print("\n=== 列名查看 ===")
    cursor.execute('PRAGMA table_info("施工参数整理表")')
    columns = cursor.fetchall()
    for col in columns:
        print(f"列: '{col[1]}' (类型: {col[2]})")
    
    # 3. 尝试查询第一列的不同值
    if columns:
        first_col = columns[0][1]  # 第一列的名字
        print(f"\n=== 第一列 '{first_col}' 的值 ===")
        cursor.execute(f'SELECT DISTINCT `{first_col}` FROM "施工参数整理表" LIMIT 5')
        values = cursor.fetchall()
        for val in values:
            print(f"值: '{val[0]}'")
    
    conn.close()

# ================== 深度调试函数 ==================
def deep_debug_database():
    """深度调试数据库结构和数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=== 深度数据库调试 ===")
    
    # 1. 检查表结构
    print("1. 表结构检查:")
    try:
        cursor.execute('PRAGMA table_info("施工参数整理表")')
        columns = cursor.fetchall()
        print("   列信息:")
        for i, col in enumerate(columns):
            print(f"     {i}: {col[1]} ({col[2]}) - NotNull:{col[3]} - Default:{col[4]}")
    except Exception as e:
        print(f"   检查表结构失败: {e}")
        
    # 2. 查看实际数据（前3行）
    print("\n2. 实际数据样例:")
    try:
        cursor.execute('SELECT * FROM "施工参数整理表" LIMIT 3')
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute('PRAGMA table_info("施工参数整理表")')
        columns = [col[1] for col in cursor.fetchall()]
        
        for i, row in enumerate(rows):
            print(f"   行 {i+1}:")
            for j, (col_name, value) in enumerate(zip(columns, row)):
                print(f"     {col_name}: '{value}'")
            print()
    except Exception as e:
        print(f"   查看数据失败: {e}")
    
    # 3. 检查模式列的实际值
    print("3. 模式列分析:")
    try:
        # 尝试不同的列名可能性
        possible_mode_columns = ['" 模式 "', "'模式'", '模式', '[模式]', '`模式`']
        
        for col_name in possible_mode_columns:
            try:
                query = f'SELECT DISTINCT {col_name} FROM "施工参数整理表" LIMIT 5'
                cursor.execute(query)
                modes = cursor.fetchall()
                print(f"   使用列名 {col_name}: {[row[0] for row in modes]}")
                if modes and modes[0][0] not in [' 模式 ', '模式']:
                    print(f"   ✓ 找到有效模式数据!")
                    break
            except Exception as e:
                print(f"   列名 {col_name} 失败: {e}")
    except Exception as e:
        print(f"   模式列分析失败: {e}")
    
    # 4. 检查工程参数列的实际值
    print("\n4. 工程参数列分析:")
    try:
        possible_param_columns = ['" 工程参数 "', "'工程参数'", '工程参数', '[工程参数]', '`工程参数`']
        
        for col_name in possible_param_columns:
            try:
                query = f'SELECT DISTINCT {col_name} FROM "施工参数整理表" LIMIT 10'
                cursor.execute(query)
                params = cursor.fetchall()
                if params:
                    print(f"   使用列名 {col_name}:")
                    for param in params[:5]:  # 只显示前5个
                        print(f"     '{param[0]}'")
                    if len(params) > 5:
                        print(f"     ... 还有 {len(params)-5} 个参数")
                    break
            except Exception as e:
                print(f"   列名 {col_name} 失败: {e}")
    except Exception as e:
        print(f"   工程参数列分析失败: {e}")
    
    # 5. 尝试查找包含"钢筋"的记录
    print("\n5. 搜索包含'钢筋'的记录:")
    try:
        # 查看所有列，寻找包含"钢筋"的数据
        cursor.execute('SELECT * FROM "施工参数整理表"')
        all_rows = cursor.fetchall()
        
        cursor.execute('PRAGMA table_info("施工参数整理表")')
        columns = [col[1] for col in cursor.fetchall()]
        
        found_records = []
        for row in all_rows:
            for col_idx, value in enumerate(row):
                if value and "钢筋" in str(value):
                    found_records.append((columns[col_idx], value, row))
                    if len(found_records) >= 5:  # 限制输出数量
                        break
            if len(found_records) >= 5:
                break
        
        if found_records:
            print("   找到包含'钢筋'的记录:")
            for col_name, value, full_row in found_records:
                print(f"     列'{col_name}': '{value}'")
                print(f"       完整记录: {dict(zip(columns, full_row))}")
        else:
            print("   ❌ 没有找到包含'钢筋'的记录!")
            
    except Exception as e:
        print(f"   搜索钢筋记录失败: {e}")
    
    # 6. 检查所有数据的模式分布
    print("\n6. 数据分布检查:")
    try:
        cursor.execute('SELECT * FROM "施工参数整理表"')
        all_rows = cursor.fetchall()
        
        cursor.execute('PRAGMA table_info("施工参数整理表")')
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"   总记录数: {len(all_rows)}")
        if all_rows:
            print("   前3条完整记录:")
            for i, row in enumerate(all_rows[:3]):
                print(f"     记录{i+1}: {dict(zip(columns, row))}")
                
    except Exception as e:
        print(f"   数据分布检查失败: {e}")
    
    conn.close()

# ================== 基于发现的问题修复函数 ==================
def fix_calculate_cost_with_correct_columns():
    """根据实际的列名修复计算函数"""
    
    # 首先运行深度调试来找出正确的列名
    print("正在分析数据库结构...")
    deep_debug_database()
    
    print("\n" + "="*50)
    print("请根据上面的调试信息，更新以下变量:")
    print("CORRECT_MODE_COLUMN = '正确的模式列名'")
    print("CORRECT_PARAM_COLUMN = '正确的工程参数列名'")
    print("然后使用 calculate_cost_with_custom_columns 函数")

def calculate_cost_with_custom_columns(mode, params_dict, others, mode_col=None, param_col=None):
    """使用自定义列名的计算函数"""
    
    # 如果没有提供列名，尝试自动检测
    if not mode_col or not param_col:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取所有列名
        cursor.execute('PRAGMA table_info("施工参数整理表")')
        all_columns = [col[1] for col in cursor.fetchall()]
        
        # 自动寻找最可能的列名
        if not mode_col:
            for col in all_columns:
                if '模式' in col:
                    mode_col = col
                    break
        
        if not param_col:
            for col in all_columns:
                if '工程参数' in col or '参数' in col:
                    param_col = col
                    break
        
        conn.close()
    
    if not mode_col or not param_col:
        print(f"错误：无法确定列名。模式列：{mode_col}，参数列：{param_col}")
        return {
            "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
            "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
            "明细": []
        }
    
    print(f"使用列名 - 模式列: '{mode_col}', 参数列: '{param_col}'")
    
    conn = get_connection()
    
    # 初始化结果
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
        "明细": []
    }
    
    for param, quantity in params_dict.items():
        print(f"\n查询参数: '{param}'")
        
        # 构建查询
        query = f'SELECT * FROM "施工参数整理表" WHERE {mode_col} = ? AND {param_col} LIKE ?'
        
        try:
            param_df = pd.read_sql(query, conn, params=(mode, f'%{param}%'))
            
            if not param_df.empty:
                row = param_df.iloc[0]
                print(f"找到匹配: {row[param_col]}")
                
                # 计算成本的逻辑保持不变...
                # (这里可以复用之前的计算逻辑)
                
            else:
                print(f"未找到参数: {param}")
                
        except Exception as e:
            print(f"查询失败: {e}")
    
    conn.close()
    return result


# ================== 修复后的函数 ==================

def get_price_data_fixed(mode, param_category=None):
    """修复后的价格数据获取函数"""
    conn = get_connection()
    
    # 使用正确的列名（无空格）和模式名
    actual_mode = f"{mode}施工模式" if not mode.endswith("施工模式") else mode
    
    if param_category:
        query = """
        SELECT * FROM "施工参数整理表" 
        WHERE "模式" = ? AND "参数类别" = ?
        ORDER BY "序号"
        """
        df = pd.read_sql(query, conn, params=(actual_mode, param_category))
    else:
        query = """
        SELECT * FROM "施工参数整理表" 
        WHERE "模式" = ?
        ORDER BY "序号"
        """
        df = pd.read_sql(query, conn, params=(actual_mode,))
    
    conn.close()
    return df

def calculate_cost_fixed(mode, params_dict, others):
    """修复后的成本计算函数"""
    conn = get_connection()
    
    # 使用正确的模式名
    actual_mode = f"{mode}施工模式" if not mode.endswith("施工模式") else mode
    print(f"使用模式: '{actual_mode}'")
    
    # 初始化结果
    result = {
        "直接施工": {"人工费": 0, "材料费": 0, "机械费": 0,"间接费用": 0, "总计": 0},
        "模块化施工": {"人工费": 0, "材料费": 0, "机械费": 0, "间接费用": 0,"总计": 0},
        "明细": []
    }
    
    # 逐个处理每个参数
    for param, quantity in params_dict.items():
        print(f"\n处理参数: '{param}'")
        
        # 使用正确的列名查询
        query = """
        SELECT * FROM "施工参数整理表"
        WHERE "模式" = ? AND "工程参数" = ?
        """
        
        try:
            param_df = pd.read_sql(query, conn, params=(actual_mode, param))
            
            if not param_df.empty:
                row = param_df.iloc[0]
                print(f"  ✓ 找到匹配数据")
                
                # 确保数量是有效数值
                quantity_str = str(quantity).strip() if quantity is not None else ""
                quantity = float(quantity_str) if quantity_str else 0
                print(f"  数量: {quantity}")
                
                # 安全地获取单价，确保它们是数值
                def safe_float(value):
                    if pd.isna(value) or value is None:
                        return 0.0
                    try:
                        if isinstance(value, str):
                            value = value.strip()
                            if not value:
                                return 0.0
                        return float(value)
                    except (ValueError, TypeError):
                        print(f"    警告: 无法转换值 '{value}' 为浮点数，使用0代替")
                        return 0.0
                
                # 获取并转换单价 - 使用正确的列名（无空格）
                direct_labor_unit = safe_float(row["直接施工人工单价"])
                direct_material_unit = safe_float(row["直接施工材料单价"])
                direct_machine_unit = safe_float(row["直接施工机械单价"])
                direct_others_unit = safe_float(others.get("直接施工间接费", 0))
                
                modular_labor_unit = safe_float(row["模块化施工人工单价"])
                modular_material_unit = safe_float(row["模块化施工材料单价"])
                modular_machine_unit = safe_float(row["模块化施工机械单价"])
                modular_others_unit = safe_float(others.get("模块化施工间接费", 0))
                
                print(f"  单价 - 直接施工: 人工={direct_labor_unit}, 材料={direct_material_unit}, 机械={direct_machine_unit}")
                print(f"  单价 - 模块化施工: 人工={modular_labor_unit}, 材料={modular_material_unit}, 机械={modular_machine_unit}")
                
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
                
                # 添加明细
                result["明细"].append({
                    "参数": param,
                    "数量": quantity,
                    "参数类别": row["参数类别"],
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
                
                print(f"  ✓ 计算完成: 直接施工={direct_total:.2f}, 模块化施工={modular_total:.2f}")
                
            else:
                print(f"  ✗ 未找到参数 '{param}' 的数据")
                
        except Exception as e:
            print(f"  ✗ 查询参数 '{param}' 时出错: {e}")
    
    # 四舍五入总计结果
    for method in ["直接施工", "模块化施工"]:
        for cost_type in ["人工费", "材料费", "机械费", "总计"]:
            result[method][cost_type] = round(result[method][cost_type], 2)
    
    conn.close()
    print(f"\n=== 计算完成 ===")
    print(f"成功处理: {len(result['明细'])} 个参数")
    print(f"直接施工总计: {result['直接施工']['总计']}")
    print(f"模块化施工总计: {result['模块化施工']['总计']}")
    
    return result

def get_parameter_suggestions_fixed(param_name, param_type=None):
    """修复后的参数建议函数"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if param_type:
            query = """
            SELECT DISTINCT "工程参数", "参数类别", "模式", "直接施工人工单价", "直接施工材料单价", "直接施工机械单价",
                        "模块化施工人工单价", "模块化施工材料单价", "模块化施工机械单价"
            FROM "施工参数整理表"
            WHERE "工程参数" LIKE ? AND "参数类别" LIKE ?
            """
            cursor.execute(query, (f'%{param_name}%', f'%{param_type}%'))
        else:
            query = """
            SELECT DISTINCT "工程参数", "参数类别", "模式", "直接施工人工单价", "直接施工材料单价", "直接施工机械单价",
                        "模块化施工人工单价", "模块化施工材料单价", "模块化施工机械单价"
            FROM "施工参数整理表"
            WHERE "工程参数" LIKE ?
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
                
                # 确保参数名不为空
                param_name_clean = row[0].strip() if row[0] else ""
                if not param_name_clean:
                    continue
                
                # 处理价格数据
                direct_labor_price = safe_float(row[3])
                direct_material_price = safe_float(row[4])
                direct_machine_price = safe_float(row[5])
                modular_labor_price = safe_float(row[6])
                modular_material_price = safe_float(row[7])
                modular_machine_price = safe_float(row[8])
                
                # 计算总价
                direct_total = direct_labor_price + direct_material_price + direct_machine_price
                modular_total = modular_labor_price + modular_material_price + modular_machine_price
                total_price = (direct_total + modular_total) / 2 if (direct_total + modular_total) > 0 else 0
                
                # 添加建议项
                suggestions.append({
                    "name": param_name_clean,
                    "category": row[1].strip() if row[1] else "",
                    "mode": row[2].strip() if row[2] else "",
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
        return []

# ================== 测试函数 ==================
def test_fixed_functions():
    """测试修复后的函数"""
    print("=== 测试修复后的函数 ===")
    
    # 测试参数
    params_dict = {
        "Q235B钢筋(现浇构件钢筋)": 100,
        "水平钢筋绑扎": 50,
        "竖向钢筋绑扎": 30,
        "拉筋绑扎": 20
    }
    others = {"直接施工间接费": 1000, "模块化施工间接费": 1200}
    
    # 使用修复后的函数
    result = calculate_cost_fixed("钢筋笼", params_dict, others)
    
    print(f"\n=== 最终结果 ===")
    print(f"直接施工总计: {result['直接施工']['总计']}")
    print(f"模块化施工总计: {result['模块化施工']['总计']}")
    print(f"成功处理的参数: {len(result['明细'])}")
    
    return result



if __name__ == '__main__':
    # debug_specific_params()
    # 运行快速测试
    # quick_test_fix()
    # 运行测试
    test_fixed_functions()