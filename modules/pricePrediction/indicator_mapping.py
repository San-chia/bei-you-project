# modules/pricePrediction/indicator_mapping.py

"""
基础指标库与价格预测模块字段映射配置
用于控制基础指标库的启用/停用状态对价格预测模块输入字段的影响
"""

# 钢筋笼模式的映射关系
STEEL_CAGE_INDICATOR_MAPPING = {
    # 基础指标库中的指标名称: 对应的价格预测模块字段配置
    "塔吊租赁单价": {
        "modal_section": "塔吊租赁费",
        "section_title": "1. 塔吊租赁费",
        "fields": [
            "tower-crane-category-param",  # 主输入框
            "tower-crane-1500",           # 自升式塔式起重机(1500KNm)
            "heavy-tower-crane"           # 重型塔吊
        ]
    },
    
    "钢筋生产线单价": {
        "modal_section": "钢筋生产线费用",
        "section_title": "2. 钢筋生产线费用", 
        "fields": [
            "steel-production-category-param"  # 主输入框
        ]
    },
    
    "吊索具综合单价": {
        "modal_section": "吊索具数量",
        "section_title": "3. 吊索具数量",
        "fields": [
            "lifting-equipment-category-param",  # 主输入框
            "steel-wire-a36-1500",              # 压制钢丝绳
            "shackle-55t",                      # 卸扣
            "basket-bolt-3128"                  # 花篮螺栓
        ]
    },
    
    "套筒综合单价": {
        "modal_section": "套筒数量", 
        "section_title": "4. 套筒数量",
        "fields": [
            "sleeve-category-param",          # 主输入框
            "straight-threaded-sleeve",       # 直螺纹钢筋套筒
            "cone-steel-sleeve",             # 锥套锁紧套筒
            "module-vertical-connection"      # 模块竖向钢筋锥套连接
        ]
    },
    
    "钢筋综合单价": {
        "modal_section": "钢筋吨数",
        "section_title": "5. 钢筋吨数", 
        "fields": [
            "steel-tonnage-category-param"    # 主输入框
        ]
    },
    
    "措施费率": {
        "modal_section": "措施费",
        "section_title": "6. 措施费",
        "fields": [
            "steel-price-category-param"      # 主输入框
        ]
    }
}

# 钢衬里模式的映射关系
STEEL_LINING_INDICATOR_MAPPING = {
    "拼装场地综合单价": {
        "modal_section": "拼装场地工程量",
        "section_title": "1. 拼装场地工程量",
        "fields": [
            "assembly-site-category-param"    # 主输入框
        ]
    },
    
    "制作胎具综合单价": {
        "modal_section": "制作胎具",
        "section_title": "2. 制作胎具", 
        "fields": [
            "fixture-making-category-param"   # 主输入框
        ]
    },
    
    "钢支墩及埋件综合单价": {
        "modal_section": "钢支墩、埋件",
        "section_title": "3. 钢支墩、埋件",
        "fields": [
            "steel-support-embedded-category-param",  # 主输入框
            "steel-support-concrete-chiseling",       # 混凝土剔凿
            "steel-support-concrete-backfill",        # 混凝土回填
            "steel-support-installation",             # 安装
            "steel-support-depreciation"              # 折旧
        ]
    },
    
    "扶壁柱综合单价": {
        "modal_section": "扶壁柱",
        "section_title": "4. 扶壁柱",
        "fields": [
            "buttress-category-param",        # 主输入框
            "buttress-installation",          # 扶壁柱安装
            "buttress-removal",              # 扶壁柱拆除
            "buttress-component-depreciation" # 扶壁柱构件使用折旧
        ]
    },
    
    "走道板及平台综合单价": {
        "modal_section": "走道板及操作平台",
        "section_title": "5. 走道板及操作平台",
        "fields": [
            "walkway-platform-category-param",    # 主输入框
            "walkway-platform-manufacturing",     # 制作
            "walkway-platform-erection",         # 搭设
            "walkway-platform-removal"           # 拆除
        ]
    },
    
    "钢网梁综合单价": {
        "modal_section": "钢网梁",
        "section_title": "6. 钢网梁",
        "fields": [
            "steel-grid-beam-category-param",  # 主输入框
            "steel-grid-manufacturing",        # 钢网架制作
            "steel-grid-installation",         # 钢网架安装
            "steel-grid-removal"              # 钢网架拆除
        ]
    },
    
    "措施费率": {
        "modal_section": "措施费",
        "section_title": "7. 措施费",
        "fields": [
            "steel-lining-measures-category-param"  # 主输入框
        ]
    }
}

# 统一的映射配置
INDICATOR_FIELD_MAPPING = {
    "steel_cage": STEEL_CAGE_INDICATOR_MAPPING,
    "steel_lining": STEEL_LINING_INDICATOR_MAPPING
}

# 反向映射：从字段ID找到对应的基础指标
def get_indicator_by_field_id(field_id, mode="steel_cage"):
    """
    根据字段ID查找对应的基础指标名称
    
    Args:
        field_id (str): 价格预测模块中的字段ID
        mode (str): 模式 ('steel_cage' 或 'steel_lining')
    
    Returns:
        str or None: 对应的基础指标名称，如果未找到返回None
    """
    mapping = INDICATOR_FIELD_MAPPING.get(mode, {})
    
    for indicator_name, config in mapping.items():
        if field_id in config["fields"]:
            return indicator_name
    
    return None

# 获取指定模式下的所有基础指标名称
def get_all_indicators_for_mode(mode="steel_cage"):
    """
    获取指定模式下的所有基础指标名称
    
    Args:
        mode (str): 模式 ('steel_cage' 或 'steel_lining')
    
    Returns:
        list: 基础指标名称列表
    """
    mapping = INDICATOR_FIELD_MAPPING.get(mode, {})
    return list(mapping.keys())

# 获取指定基础指标对应的所有字段ID
def get_fields_by_indicator(indicator_name, mode="steel_cage"):
    """
    获取指定基础指标对应的所有字段ID
    
    Args:
        indicator_name (str): 基础指标名称
        mode (str): 模式 ('steel_cage' 或 'steel_lining')
    
    Returns:
        list: 字段ID列表，如果未找到返回空列表
    """
    mapping = INDICATOR_FIELD_MAPPING.get(mode, {})
    config = mapping.get(indicator_name, {})
    return config.get("fields", [])

# 获取指定基础指标的配置信息
def get_indicator_config(indicator_name, mode="steel_cage"):
    """
    获取指定基础指标的完整配置信息
    
    Args:
        indicator_name (str): 基础指标名称
        mode (str): 模式 ('steel_cage' 或 'steel_lining')
    
    Returns:
        dict: 配置信息，如果未找到返回空字典
    """
    mapping = INDICATOR_FIELD_MAPPING.get(mode, {})
    return mapping.get(indicator_name, {})

# 验证映射配置的完整性
def validate_mapping():
    """
    验证映射配置是否完整
    
    Returns:
        dict: 验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    for mode, mapping in INDICATOR_FIELD_MAPPING.items():
        for indicator_name, config in mapping.items():
            # 检查必要的配置项
            required_keys = ["modal_section", "section_title", "fields"]
            for key in required_keys:
                if key not in config:
                    result["valid"] = False
                    result["errors"].append(f"模式 {mode} 的指标 '{indicator_name}' 缺少配置项: {key}")
            
            # 检查字段列表是否为空
            if not config.get("fields"):
                result["warnings"].append(f"模式 {mode} 的指标 '{indicator_name}' 没有配置任何字段")
    
    return result

# 可选：添加一些统计信息
def get_mapping_statistics():
    """
    获取映射关系的统计信息
    
    Returns:
        dict: 统计信息
    """
    stats = {}
    
    for mode, mapping in INDICATOR_FIELD_MAPPING.items():
        total_indicators = len(mapping)
        total_fields = sum(len(config.get("fields", [])) for config in mapping.values())
        
        stats[mode] = {
            "total_indicators": total_indicators,
            "total_fields": total_fields,
            "indicators": list(mapping.keys())
        }
    
    return stats
