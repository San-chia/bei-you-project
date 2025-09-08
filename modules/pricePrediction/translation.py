# modules/pricePrediction/translation.py

# 价格预测模块专用的表名映射
PRICE_PREDICTION_TABLE_TRANSLATIONS = {
    '关键因素1': 'key_factors_1',
    '关键因素2': 'key_factors_2', 
    '价格基准1': 'price_baseline_1',
    '价格基准2': 'price_baseline_2',
    'key_factors_1': '关键因素1',
    'key_factors_2': '关键因素2',
    'price_baseline_1': '价格基准1', 
    'price_baseline_2': '价格基准2'
}

# 字段名映射（继承基础映射）
PRICE_PREDICTION_FIELD_TRANSLATIONS = {
    'project_id': '项目ID',
    'project_total_price': '项目总价',
    'tower_crane_rental_fee': '塔吊租赁费',
    'rebar_production_cost': '钢筋生产线费用',
    'lifting_equipment_cost': '吊索具费用',
    'coupling_cost': '套筒费用',
    'total_rebar_tonnage': '钢筋总吨数',
    'coupling_quantity': '套筒数量',
    'lifting_equipment_quantity': '吊索具数量',
    'tower_crane_rental_quantity': '塔吊租赁工程量',
    # 钢衬里相关字段
    'assembly_site_cost': '拼装场地费用',
    'mold_making_cost': '制作胎具费用',
    'steel_support_embedded_cost': '钢支墩、埋件费用',
    'buttress_column_cost': '扶壁柱费用',
    'walkway_platform_cost': '走道板及操作平台费用',
    'steel_grid_cost': '钢网架费用',
}

def translate_table_name(english_name):
    """将英文表名翻译为中文"""
    return PRICE_PREDICTION_TABLE_TRANSLATIONS.get(english_name, english_name)

def translate_field_name(english_field):
    """将英文字段名翻译为中文"""
    return PRICE_PREDICTION_FIELD_TRANSLATIONS.get(english_field, english_field)

def reverse_translate_table_name(chinese_name):
    """将中文表名翻译为英文"""
    reverse_mapping = {v: k for k, v in PRICE_PREDICTION_TABLE_TRANSLATIONS.items()}
    return reverse_mapping.get(chinese_name, chinese_name)
