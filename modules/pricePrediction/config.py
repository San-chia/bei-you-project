# ==================== 价格预测模块配置 ====================
#STEEL_CAGE_PRICE_DB = r"E:\1codefiles\python\Dash_app\project_20250703_V9\project_20250524_V5.1\project_20250427_V3\Data.db"
#STEEL_CAGE_KEY_FACTORS_DB = r"E:\1codefiles\python\Dash_app\project_20250703_V9\project_20250524_V5.1\project_20250427_V3\Data.db"

STEEL_CAGE_COL_MAPPING = {
    'tower_crane_rental_cost': '成本_塔吊租赁',
    'rebar_production_cost': '成本_钢筋生产线', 
    'lifting_equipment_cost': '成本_吊索具',
    'coupling_cost': '成本_套筒',
    'total_rebar_tonnage': '钢筋总吨数',
    'coupling_quantity': '套筒数量',
    'lifting_equipment_quantity': '吊索具数量',
    'tower_crane_rental_quantity': '塔吊租赁工程量',
    'project_total_price': '项目总价',
    'project_id': '项目ID',
}
STEEL_CAGE_ML_FEATURES = ['成本_塔吊租赁', '成本_钢筋生产线', '成本_吊索具', '成本_套筒']

# 钢衬里模式数据库路径
#STEEL_LINING_PRICE_DB = r"E:\1codefiles\python\Dash_app\project_20250703_V9\project_20250524_V5.1\project_20250427_V3\Data.db"
#STEEL_LINING_KEY_FACTORS_DB = r"E:\1codefiles\python\Dash_app\project_20250703_V9\project_20250524_V5.1\project_20250427_V3\Data.db"

# 钢衬里模式的关键列名映射
# 根据您提供的“价格基准2”数据结构，并假设这些合价会映射到“关键因素2”中的“费用”列
STEEL_LINING_COL_MAPPING = {
    # 费用相关映射（从英文数据库列名到中文逻辑名）
    'assembly_site_cost': '拼装场地费用',
    'mold_making_cost': '制作胎具费用', 
    'steel_support_embedded_cost': '钢支墩、埋件费用',
    'buttress_column_cost': '扶壁柱费用',
    'walkway_platform_cost': '走道板及操作平台费用',
    'steel_grid_cost': '钢网架费用',
    'project_total_price': '项目总价',
    
    # 工程量相关映射（从英文数据库列名到中文逻辑名）
    'total_assembly_site_quantity': '拼装场地总工程量',
    'total_mold_making_quantity': '制作胎具总工程量',
    'total_steel_support_embedded_quantity': '钢支墩埋件总工程量',
    'total_buttress_column_quantity': '扶壁柱总工程量',
    'total_walkway_platform_quantity': '走道板操作平台总工程量',
    'total_steel_grid_beam_quantity': '钢网梁总工程量',
    
    # 如果还有其他英文列名，请根据实际数据库结构添加
    'project_id': '项目ID',
}
# 钢衬里模式的机器学习特征列 (需要与关键因素2的“费用”列对应)
STEEL_LINING_ML_FEATURES = [
    "拼装场地费用",
    "制作胎具费用",
    "钢支墩、埋件费用",
    "扶壁柱费用",
    "走道板及操作平台费用",
    "钢网架费用"
]