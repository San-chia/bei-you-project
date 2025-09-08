# utils/permission_utils.py
from flask_login import current_user

# 模块权限映射
MODULE_PERMISSIONS = {
    'tab-1': 'indicator_calculation',    # 指标测算
    'tab-2': 'data_management',         # 数据管理  
    'tab-3': 'system_config',           # 软件管理（需要系统配置权限）
    'tab-4': 'report_generation',       # 报表管理
    'tab-5': 'modular_construction',    # 模块化施工
    'tab-6': 'construction_management',         # 施工数据
    'tab-7': 'price_prediction',        # 价格预测
    'tab-8': 'platform_integration',    # 对接一体化平台
}

# 模块显示名称
MODULE_NAMES = {
    'tab-1': '指标测算',
    'tab-2': '指标与算法管理',
    'tab-3': '系统管理', 
    'tab-4': '报表管理',
    'tab-5': '模块化施工',
    'tab-6': '施工数据',
    'tab-7': '价格预测',
    'tab-8': '对接一体化平台',
}

def check_module_permission(tab_id):
    """检查当前用户是否有访问指定模块的权限"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        
        # 获取模块需要的权限
        required_permission = MODULE_PERMISSIONS.get(tab_id)
        if not required_permission:
            return True  # 如果没有定义权限要求，默认允许访问
        
        # 检查用户是否拥有该权限
        return current_user.has_permission(required_permission)
    except Exception as e:
        print(f"权限检查失败: {e}")
        return False

def get_user_accessible_tabs():
    """获取当前用户可访问的所有标签页"""
    # 定义希望的显示顺序
    desired_order = ['tab-1', 'tab-7', 'tab-5', 'tab-6', 'tab-2', 'tab-3', 'tab-4', 'tab-8']
    
    accessible_tabs = []
    
    # 按照指定顺序检查权限
    for tab_id in desired_order:
        tab_name = MODULE_NAMES.get(tab_id)
        if tab_name and check_module_permission(tab_id):
            accessible_tabs.append({
                'tab_id': tab_id,
                'tab_name': tab_name,
                'permission': MODULE_PERMISSIONS.get(tab_id)
            })
    
    return accessible_tabs

def get_user_permissions():
    """获取当前用户的所有权限"""
    try:
        if not current_user or not current_user.is_authenticated:
            return []
        return current_user.get_all_permissions()
    except Exception as e:
        print(f"获取用户权限失败: {e}")
        return []