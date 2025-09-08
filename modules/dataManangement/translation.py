# 新建文件：modules/dataManagement/translation.py
"""数据库字段和表名的中英文映射模块"""

# 表名映射字典（英文到中文显示）
TABLE_TRANSLATIONS = {
    'price_baseline_1': '价格基准1',
    'price_baseline_2': '价格基准2',
    'key_factors_1': '关键因素1',
    'key_factors_2': '关键因素2',
    'parameter_info': '参数信息',
    'project_info': '工程信息',
    'construction_parameter_table': '施工参数整理表',
    'calculation_results': '计算结果',
    'steel_lining': '钢衬里',
    'project_one': '项目一',
    'project_three': '项目三',
    'project_two_sub_one': '项目二（子项目一）',
    'project_two_sub_two': '项目二（子项目二）',
    'project_two_sub_three': '项目二（子项目三）',
    'project_two_shared_params': '项目二（子项目二、三、四共用参数）',
    'project_five': '项目五',
    'project_four': '项目四',
    'final_project_summary1': '最终项目汇总表1',
    'final_project_summary2': '最终项目汇总表2',
    'price_custom_calculation_results': '自定义价格计算结果表',
    'price_custom_parameters': '自定义价格参数表',
    'users': '用户表'
}

# 字段名映射字典（英文到中文显示）
FIELD_TRANSLATIONS = {
    # 项目相关字段
    'project_id': '项目ID',
    'project_name': '项目名称',
    'project_total_price': '项目总价',
    'project_type': '工程类型',
    'project_quantity': '工程量',
    'project': '项目',
    'project_code': '项目编码',
    'category': '分类',
    'description': '说明',
    'action': '操作',
    
    # 费用相关字段
    'tower_crane_rental_fee': '塔吊租赁费',
    'rebar_production_cost': '钢筋生产线费用',
    'lifting_equipment_cost': '吊索具费用',
    'coupling_cost': '套筒费用',
    'assembly_site_cost': '拼装场地费用',
    'mold_making_cost': '制作胎具费用',
    'steel_support_embedded_cost': '钢支墩、埋件费用',
    'buttress_column_cost': '扶壁柱费用',
    'walkway_platform_cost': '走道板及操作平台费用',
    'steel_grid_cost': '钢网架费用',
    
    # 数量相关字段
    'total_rebar_tonnage': '钢筋总吨数',
    'coupling_quantity': '套筒数量',
    'lifting_equipment_quantity': '吊索具数量',
    'tower_crane_rental_quantity': '塔吊租赁工程量',
    'total_assembly_site_quantity': '拼装场地总工程量',
    'total_mold_making_quantity': '制作胎具总工程量',
    'total_steel_support_embedded_quantity': '钢支墩埋件总工程量',
    'total_buttress_column_quantity': '扶壁柱总工程量',
    'total_walkway_platform_quantity': '走道板操作平台总工程量',
    'total_steel_grid_beam_quantity': '钢网梁总工程量',
    
    # 价格相关字段
    'direct_labor_unit_price': '直接施工人工单价',
    'direct_material_unit_price': '直接施工材料单价',
    'direct_machinery_unit_price': '直接施工机械单价',
    'modular_labor_unit_price': '模块化施工人工单价',
    'modular_material_unit_price': '模块化施工材料单价',
    'modular_machinery_unit_price': '模块化施工机械单价',
    'modular_labor_quantity': '模块化施工人工工程量',
    'modular_material_quantity': '模块化施工材料工程量',
    'modular_machinery_quantity': '模块化施工机械工程量',
    'modular_labor_total': '模块化施工人工合价',
    'modular_material_total': '模块化施工材料合价',
    'modular_machinery_total': '模块化施工机械合价',
    
    # 参数相关字段
    'parameter_id': '参数ID',
    'parameter_unique_id': '参数唯一ID',
    'parameter_name': '参数名称',
    'parameter_type': '参数类型',
    'parameter_value': '参数值',
    'parameter_category': '参数类别',
    
    # 计算结果相关字段
    'result_id': '结果ID',
    'construction_mode': '施工模式',
    'result_data': '结果数据',
    'direct_labor_cost': '直接施工人工费',
    'direct_material_cost': '直接施工材料费',
    'direct_machinery_cost': '直接施工机械费',
    'direct_indirect_cost': '直接施工间接费用',
    'direct_total': '直接施工总计',
    'modular_labor_cost': '模块化施工人工费',
    'modular_material_cost': '模块化施工材料费',
    'modular_machinery_cost': '模块化施工机械费',
    'modular_indirect_cost': '模块化施工间接费用',
    'modular_total': '模块化施工总计',
    'cost_difference': '成本差异',
    'cost_difference_percentage': '成本差异百分比',
    
    # 基础字段
    'sequence_number': '序号',
    'unit': '单位',
    'total_price': '总价',
    'quantity': '数量',
    'remarks': '备注说明',
    'create_time': '创建时间',
    'update_time': '更新时间',
    'status': '状态',
    'user_id': '用户ID',
    'name': '名称',
    'labor_cost': '人工费',
    'material_cost': '材料费',
    'machinery_cost': '机械费',
    'unit_price': '单价',
    'total_price_ten_thousand': '合价（万元）',
    
    # 施工相关字段
    'normal_construction_days': '正常施工工日数',
    'modular_construction_days': '模块化施工工日数',
    'mode': '模式',
    'engineering_parameter': '工程参数',
    'timestamp': '时间戳',
    'calculation_time': '计算时间',
    'data_source': '数据来源',
    'original_table_name': '原始表名',
    
    # 用户相关字段
    'username': '用户名',
    'email': '邮箱',
    'password_hash': '密码哈希',
    'created_at': '创建时间',
    'is_active': '是否激活'
}

# 反向映射：中文到英文（用于前端参数转换）
REVERSE_TABLE_TRANSLATIONS = {v: k for k, v in TABLE_TRANSLATIONS.items()}
REVERSE_FIELD_TRANSLATIONS = {v: k for k, v in FIELD_TRANSLATIONS.items()}

def translate_table_name(english_name):
    """将英文表名翻译为中文显示名"""
    return TABLE_TRANSLATIONS.get(english_name, english_name)

def translate_field_name(english_field):
    """将英文字段名翻译为中文显示名"""
    return FIELD_TRANSLATIONS.get(english_field, english_field)

def reverse_translate_table_name(chinese_name):
    """将中文表名翻译为英文数据库表名"""
    return REVERSE_TABLE_TRANSLATIONS.get(chinese_name, chinese_name)

def reverse_translate_field_name(chinese_field):
    """将中文字段名翻译为英文数据库字段名"""
    return REVERSE_FIELD_TRANSLATIONS.get(chinese_field, chinese_field)

def translate_dataframe_columns(df):
    """翻译DataFrame的列名为中文"""
    chinese_columns = {}
    for col in df.columns:
        chinese_columns[col] = translate_field_name(col)
    return df.rename(columns=chinese_columns)

def translate_table_options(table_list):
    """翻译表选项列表为中文显示"""
    translated_options = []
    for table in table_list:
        if isinstance(table, dict):
            # 如果是字典格式 {'label': xx, 'value': xx}
            chinese_label = translate_table_name(table['value'])
            translated_options.append({
                'label': chinese_label,
                'value': table['value']  # 保持英文值用于数据库操作
            })
        else:
            # 如果是字符串格式
            translated_options.append({
                'label': translate_table_name(table),
                'value': table
            })
    return translated_options
