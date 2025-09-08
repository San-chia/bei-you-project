# utils/decorators.py
from functools import wraps
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask_login import current_user

def require_permission(permission_code):
    """权限检查装饰器，用于保护回调函数"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 检查用户是否已认证
                if not current_user or not current_user.is_authenticated:
                    return dbc.Alert("请先登录", color="warning")
                
                # 检查用户是否有相应权限
                if not current_user.has_permission(permission_code):
                    return dbc.Alert(
                        [
                            html.H5("权限不足", className="alert-heading"),
                            html.P(f"您需要'{permission_code}'权限才能执行此操作。"),
                            html.P("请联系管理员申请相应权限。")
                        ],
                        color="danger"
                    )
                
                # 执行原函数
                return func(*args, **kwargs)
                
            except Exception as e:
                print(f"权限检查装饰器错误: {e}")
                return dbc.Alert("权限检查失败", color="danger")
        
        return wrapper
    return decorator

def require_any_permission(permission_codes):
    """需要任意一个权限的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if not current_user or not current_user.is_authenticated:
                    return dbc.Alert("请先登录", color="warning")
                
                if not current_user.has_any_permission(permission_codes):
                    permissions_str = "', '".join(permission_codes)
                    return dbc.Alert(
                        [
                            html.H5("权限不足", className="alert-heading"),
                            html.P(f"您需要以下任意一个权限：'{permissions_str}'"),
                            html.P("请联系管理员申请相应权限。")
                        ],
                        color="danger"
                    )
                
                return func(*args, **kwargs)
                
            except Exception as e:
                print(f"权限检查装饰器错误: {e}")
                return dbc.Alert("权限检查失败", color="danger")
        
        return wrapper
    return decorator

def require_role(role_code):
    """角色检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if not current_user or not current_user.is_authenticated:
                    return dbc.Alert("请先登录", color="warning")
                
                if not current_user.has_role(role_code):
                    return dbc.Alert(
                        [
                            html.H5("权限不足", className="alert-heading"),
                            html.P(f"您需要'{role_code}'角色才能访问此功能。"),
                            html.P("请联系管理员申请相应角色。")
                        ],
                        color="danger"
                    )
                
                return func(*args, **kwargs)
                
            except Exception as e:
                print(f"角色检查装饰器错误: {e}")
                return dbc.Alert("角色检查失败", color="danger")
        
        return wrapper
    return decorator

# 示例：如何在回调函数中使用装饰器
"""
@app.callback(
    Output('management-content', 'children'),
    [Input('management-btn', 'n_clicks')]
)
@require_permission('system_config')
def show_management_content(n_clicks):
    if not n_clicks:
        return dash.no_update
    
    return create_management_layout()
"""