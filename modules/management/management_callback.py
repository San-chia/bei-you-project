# modules/management/management_callback.py
import dash
from dash import Input, Output, State, html, callback_context, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

from flask_login import current_user
# 导入现有的数据库模型
try:
    from models import db, User, Role, Permission,Task
except ImportError:
    print("无法导入数据库模型")
    db = None
    User = None
    Role = None
    Permission = None

try:
    from models import OperationLog
except ImportError:
    print("无法导入OperationLog模型")
    OperationLog = None

from .management_layout import (
    create_user_management_content,
    create_permission_management_content,
    create_task_management_content,
    create_log_management_content,
    get_user_datatable,
    get_permission_datatable
)

def management_callbacks(app):
    """注册管理模块的回调函数"""
    
    # 1. 页面加载时获取用户数据
    @app.callback(
        Output('users-datatable', 'data'),
        [Input('user-table-container', 'children')]
    )
    def load_users_data(children):
        """加载用户数据"""
        if User and db:
            try:
                users = User.query.all()
                users_data = []
                for user in users:
                    # 获取用户角色信息
                    user_roles = [role.name for role in user.roles] if user.roles else []
                    roles_str = ', '.join(user_roles) if user_roles else '无角色'
                    
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', '') or '',
                        'email': user.email,
                        'phone': getattr(user, 'phone', '') or '',
                        'department': getattr(user, 'department', '') or '',
                        'position': getattr(user, 'position', '') or '',
                        'roles': roles_str,  # 新增角色显示
                        'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                        'is_active': '激活' if user.is_active else '禁用'
                    })
                return users_data
            except Exception as e:
                print(f"获取用户数据失败: {e}")
                return []
        else:
            # 返回示例数据
            return [
                {
                    'id': 1,
                    'username': 'admin',
                    'real_name': '管理员',
                    'email': 'admin@example.com',
                    'phone': '18200000000',
                    'department': '管理部',
                    'position': '系统管理员',
                    'roles': '管理员',
                    'created_at': '2024-01-01',
                    'is_active': '激活'
                },
                {
                    'id': 2,
                    'username': 'user',
                    'real_name': '普通用户',
                    'email': 'user@example.com',
                    'phone': '18200000001',
                    'department': '技术部',
                    'position': '开发工程师',
                    'roles': '操作员',
                    'created_at': '2024-01-02',
                    'is_active': '激活'
                }
            ]

    # 1.1 页面加载时获取权限数据
    @app.callback(
        Output('permissions-datatable', 'data'),
        [Input('permission-table-container', 'children')]
    )
    def load_permissions_data(children):
        """加载权限数据"""
        if Permission and db:
            try:
                permissions = Permission.query.all()
                permissions_data = []
                for permission in permissions:
                    permissions_data.append({
                        'id': permission.id,
                        'name': permission.name,
                        'code': permission.code,
                        'module': permission.module,
                        'description': permission.description or '',
                        'role_count': permission.get_role_count(),
                        'created_at': permission.created_at.strftime('%Y-%m-%d') if permission.created_at else '',
                        'is_active': '激活' if permission.is_active else '禁用'
                    })
                return permissions_data
            except Exception as e:
                print(f"获取权限数据失败: {e}")
                return []
        else:
            # 返回示例数据
            return [
                {
                    'id': 1,
                    'name': '数据管理',
                    'code': 'data_management',
                    'module': 'data',
                    'description': '数据的增删改查权限',
                    'role_count': 2,
                    'created_at': '2024-01-01',
                    'is_active': '激活'
                },
                {
                    'id': 2,
                    'name': '用户管理',
                    'code': 'user_management',
                    'module': 'user',
                    'description': '用户账户管理权限',
                    'role_count': 1,
                    'created_at': '2024-01-01',
                    'is_active': '激活'
                },
                {
                    'id': 3,
                    'name': '报表查看',
                    'code': 'report_view',
                    'module': 'report',
                    'description': '查看报表权限',
                    'role_count': 3,
                    'created_at': '2024-01-01',
                    'is_active': '激活'
                }
            ]

    # 2. 管理模块内容切换
    @app.callback(
        Output('management-content-area', 'children'),
        [Input('btn-user-mgmt', 'n_clicks'),
         Input('btn-permission-mgmt', 'n_clicks'),
         Input('btn-task-mgmt', 'n_clicks'),
         Input('btn-log-mgmt', 'n_clicks')]
    )
    def update_management_content(user_clicks, perm_clicks, task_clicks, log_clicks):
        """切换管理模块内容"""
        ctx = callback_context
        if not ctx.triggered:
            return create_user_management_content()
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        content_mapping = {
            'btn-user-mgmt': create_user_management_content(),
            'btn-permission-mgmt': create_permission_management_content(),
            'btn-task-mgmt': create_task_management_content(),
            'btn-log-mgmt': create_log_management_content()
        }
        
        return content_mapping.get(button_id, create_user_management_content())

    # 3. 用户搜索和更新功能
    @app.callback(
        Output('users-datatable', 'data', allow_duplicate=True),
        [Input('user-search-btn', 'n_clicks'),
         Input('user-refresh-btn', 'n_clicks')],
        [State('user-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_or_refresh_users(search_clicks, refresh_clicks, search_value):
        """搜索用户或刷新数据"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if User and db:
            try:
                if trigger_id == 'user-refresh-btn':
                    # 刷新所有用户数据
                    users = User.query.all()
                elif trigger_id == 'user-search-btn' and search_value:
                    # 搜索用户
                    search_term = f"%{search_value}%"
                    users = User.query.filter(
                        db.or_(
                            User.username.like(search_term),
                            User.email.like(search_term)
                        )
                    ).all()
                else:
                    return no_update
                
                users_data = []
                for user in users:
                    # 获取用户角色信息
                    user_roles = [role.name for role in user.roles] if user.roles else []
                    roles_str = ', '.join(user_roles) if user_roles else '无角色'
                    
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', '') or '',
                        'email': user.email,
                        'phone': getattr(user, 'phone', '') or '',
                        'department': getattr(user, 'department', '') or '',
                        'position': getattr(user, 'position', '') or '',
                        'roles': roles_str,
                        'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                        'is_active': '激活' if user.is_active else '禁用'
                    })
                return users_data
            except Exception as e:
                print(f"操作失败: {e}")
                return no_update
        
        return no_update

    # 3.1 权限搜索和更新功能
    @app.callback(
        Output('permissions-datatable', 'data', allow_duplicate=True),
        [Input('permission-search-btn', 'n_clicks'),
         Input('permission-refresh-btn', 'n_clicks')],
        [State('permission-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_or_refresh_permissions(search_clicks, refresh_clicks, search_value):
        """搜索权限或刷新数据"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if Permission and db:
            try:
                if trigger_id == 'permission-refresh-btn':
                    # 刷新所有权限数据
                    permissions = Permission.query.all()
                elif trigger_id == 'permission-search-btn' and search_value:
                    # 搜索权限
                    search_term = f"%{search_value}%"
                    permissions = Permission.query.filter(
                        db.or_(
                            Permission.name.like(search_term),
                            Permission.code.like(search_term),
                            Permission.module.like(search_term)
                        )
                    ).all()
                else:
                    return no_update
                
                permissions_data = []
                for permission in permissions:
                    permissions_data.append({
                        'id': permission.id,
                        'name': permission.name,
                        'code': permission.code,
                        'module': permission.module,
                        'description': permission.description or '',
                        'role_count': permission.get_role_count(),
                        'created_at': permission.created_at.strftime('%Y-%m-%d') if permission.created_at else '',
                        'is_active': '激活' if permission.is_active else '禁用'
                    })
                return permissions_data
            except Exception as e:
                print(f"操作失败: {e}")
                return no_update
        
        return no_update

    # 4. 添加更新成功提示
    @app.callback(
        Output('user-alert-area', 'children', allow_duplicate=True),
        [Input('user-refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_refresh_message(refresh_clicks):
        """显示刷新成功消息"""
        if refresh_clicks:
            return dbc.Alert("数据已更新", color="success", duration=3000)
        return no_update

    # 4.1 权限更新成功提示
    @app.callback(
        Output('permission-alert-area', 'children', allow_duplicate=True),
        [Input('permission-refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_permission_refresh_message(refresh_clicks):
        """显示权限刷新成功消息"""
        if refresh_clicks:
            return dbc.Alert("权限数据已更新", color="success", duration=3000)
        return no_update

    # 5. 编辑按钮检测选中行
    @app.callback(
        Output('user-alert-area', 'children', allow_duplicate=True),
        [Input('user-edit-btn', 'n_clicks')],
        [State('users-datatable', 'selected_rows'),
         State('users-datatable', 'data')],
        prevent_initial_call=True
    )
    def check_edit_selection(edit_clicks, selected_rows, table_data):
        """检测编辑按钮点击和选中行"""
        if not edit_clicks:
            return no_update
        
        print(f"编辑按钮点击，选中行: {selected_rows}")  # 调试信息
        
        if not selected_rows or len(selected_rows) == 0:
            return dbc.Alert("请先点击表格中的行来选择要编辑的用户", color="warning", duration=4000)
        elif len(selected_rows) > 1:
            return dbc.Alert("请只选择一个用户进行编辑", color="warning", duration=4000)
        
        # 如果选中了一行，显示选中的用户信息
        if table_data and selected_rows:
            try:
                selected_user = table_data[selected_rows[0]]
                print(f"选中的用户数据: {selected_user}")  # 调试信息
                return dbc.Alert(f"已选中用户: {selected_user.get('username', '未知')}", color="info", duration=2000)
            except Exception as e:
                print(f"获取选中用户信息失败: {e}")
                return dbc.Alert("获取用户信息失败", color="danger", duration=4000)
        
        return no_update

    # 5.1 权限编辑按钮检测选中行
    @app.callback(
        Output('permission-alert-area', 'children', allow_duplicate=True),
        [Input('permission-edit-btn', 'n_clicks')],
        [State('permissions-datatable', 'selected_rows'),
         State('permissions-datatable', 'data')],
        prevent_initial_call=True
    )
    def check_permission_edit_selection(edit_clicks, selected_rows, table_data):
        """检测权限编辑按钮点击和选中行"""
        if not edit_clicks:
            return no_update
        
        if not selected_rows or len(selected_rows) == 0:
            return dbc.Alert("请先点击表格中的行来选择要编辑的权限", color="warning", duration=4000)
        elif len(selected_rows) > 1:
            return dbc.Alert("请只选择一个权限进行编辑", color="warning", duration=4000)
        
        # 如果选中了一行，显示选中的权限信息
        if table_data and selected_rows:
            try:
                selected_permission = table_data[selected_rows[0]]
                return dbc.Alert(f"已选中权限: {selected_permission.get('name', '未知')}", color="info", duration=2000)
            except Exception as e:
                print(f"获取选中权限信息失败: {e}")
                return dbc.Alert("获取权限信息失败", color="danger", duration=4000)
        
        return no_update

    # 6. 添加用户模态框控制
    @app.callback(
        [Output('user-modal', 'is_open'),
         Output('user-modal-title', 'children'),
         Output('user-modal-username', 'value'),
         Output('user-modal-realname', 'value'),
         Output('user-modal-email', 'value'),
         Output('user-modal-phone', 'value'),
         Output('user-modal-department', 'value'),
         Output('user-modal-position', 'value'),
         Output('user-modal-password', 'value'),
         Output('user-modal-confirm-password', 'value'),
         Output('user-modal-status', 'value'),
         Output('user-modal-user-id', 'data')],
        [Input('user-add-btn', 'n_clicks'),
         Input('user-edit-btn', 'n_clicks'),
         Input('user-modal-cancel', 'n_clicks'),
         Input('user-modal-save', 'n_clicks')],
        [State('user-modal', 'is_open'),
         State('users-datatable', 'selected_rows'),
         State('users-datatable', 'data')]
    )
    def handle_user_modal(add_clicks, edit_clicks, cancel_clicks, save_clicks, is_open, selected_rows, table_data):
        """处理用户模态框"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'user-add-btn':
            # 添加用户 - 清空所有字段
            return (True, "添加用户", "", "", "", "", "", "", "", "", "true", None)
        
        elif trigger_id == 'user-edit-btn':
            # 编辑用户 - 预填充现有数据
            if not selected_rows or len(selected_rows) != 1:
                # 如果没有选中行或选中多行，不打开模态框
                return no_update
            
            if not table_data:
                return no_update
            
            try:
                # 获取选中行的数据
                selected_user_data = table_data[selected_rows[0]]
                
                # 从数据库获取完整的用户信息（确保数据最新）
                user_id = selected_user_data['id']
                
                if User and db:
                    try:
                        user = User.query.get(user_id)
                        if user:
                            return (
                                True, "编辑用户",
                                user.username,
                                getattr(user, 'real_name', '') or '',
                                user.email,
                                getattr(user, 'phone', '') or '',
                                getattr(user, 'department', '') or '',
                                getattr(user, 'position', '') or '',
                                "",  # 密码字段留空
                                "",  # 确认密码字段留空
                                "true" if user.is_active else "false",
                                user.id
                            )
                    except Exception as e:
                        print(f"获取用户详细信息失败: {e}")
                
                # 如果数据库查询失败，使用表格数据
                return (
                    True, "编辑用户",
                    selected_user_data.get('username', ''),
                    selected_user_data.get('real_name', ''),
                    selected_user_data.get('email', ''),
                    selected_user_data.get('phone', ''),
                    selected_user_data.get('department', ''),
                    selected_user_data.get('position', ''),
                    "",  # 密码字段留空
                    "",  # 确认密码字段留空
                    "true" if selected_user_data.get('is_active') == '激活' else "false",
                    selected_user_data.get('id')
                )
                
            except (IndexError, KeyError) as e:
                print(f"获取选中用户数据失败: {e}")
                return no_update
        
        elif trigger_id in ['user-modal-cancel', 'user-modal-save']:
            # 关闭模态框并清空所有字段
            return (False, "", "", "", "", "", "", "", "", "", "true", None)
        
        return no_update

    # 6.1 权限模态框控制
    @app.callback(
        [Output('permission-modal', 'is_open'),
         Output('permission-modal-title', 'children'),
         Output('permission-modal-name', 'value'),
         Output('permission-modal-code', 'value'),
         Output('permission-modal-module', 'value'),
         Output('permission-modal-description', 'value'),
         Output('permission-modal-status', 'value'),
         Output('permission-modal-permission-id', 'data')],
        [Input('permission-add-btn', 'n_clicks'),
         Input('permission-edit-btn', 'n_clicks'),
         Input('permission-modal-cancel', 'n_clicks'),
         Input('permission-modal-save', 'n_clicks')],
        [State('permission-modal', 'is_open'),
         State('permissions-datatable', 'selected_rows'),
         State('permissions-datatable', 'data')]
    )
    def handle_permission_modal(add_clicks, edit_clicks, cancel_clicks, save_clicks, is_open, selected_rows, table_data):
        """处理权限模态框"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'permission-add-btn':
            # 添加权限 - 清空所有字段
            return (True, "添加权限", "", "", "", "", "true", None)
        
        elif trigger_id == 'permission-edit-btn':
            # 编辑权限 - 预填充现有数据
            if not selected_rows or len(selected_rows) != 1:
                # 如果没有选中行或选中多行，不打开模态框
                return no_update
            
            if not table_data:
                return no_update
            
            try:
                # 获取选中行的数据
                selected_permission_data = table_data[selected_rows[0]]
                
                # 从数据库获取完整的权限信息（确保数据最新）
                permission_id = selected_permission_data['id']
                
                if Permission and db:
                    try:
                        permission = Permission.query.get(permission_id)
                        if permission:
                            return (
                                True, "编辑权限",
                                permission.name,
                                permission.code,
                                permission.module,
                                permission.description or '',
                                "true" if permission.is_active else "false",
                                permission.id
                            )
                    except Exception as e:
                        print(f"获取权限详细信息失败: {e}")
                
                # 如果数据库查询失败，使用表格数据
                return (
                    True, "编辑权限",
                    selected_permission_data.get('name', ''),
                    selected_permission_data.get('code', ''),
                    selected_permission_data.get('module', ''),
                    selected_permission_data.get('description', ''),
                    "true" if selected_permission_data.get('is_active') == '激活' else "false",
                    selected_permission_data.get('id')
                )
                
            except (IndexError, KeyError) as e:
                print(f"获取选中权限数据失败: {e}")
                return no_update
        
        elif trigger_id in ['permission-modal-cancel', 'permission-modal-save']:
            # 关闭模态框并清空所有字段
            return (False, "", "", "", "", "", "true", None)
        
        return no_update

    # 7. 保存用户（修改版）
    @app.callback(
        [Output('user-alert-area', 'children'),
         Output('users-datatable', 'data', allow_duplicate=True)],
        [Input('user-modal-save', 'n_clicks')],
        [State('user-modal-username', 'value'),
         State('user-modal-realname', 'value'),
         State('user-modal-email', 'value'),
         State('user-modal-phone', 'value'),
         State('user-modal-department', 'value'),
         State('user-modal-position', 'value'),
         State('user-modal-password', 'value'),
         State('user-modal-confirm-password', 'value'),
         State('user-modal-status', 'value'),
         State('user-modal-user-id', 'data')],
        prevent_initial_call=True
    )
    def save_user(save_clicks, username, realname, email, phone, department, position, 
                  password, confirm_password, status, user_id):
        """保存用户（支持新建和编辑）"""
        if not save_clicks:
            return no_update
        
        # 基本字段验证
        if not username or not email:
            alert = dbc.Alert("用户名和邮箱为必填字段", color="danger", duration=4000)
            return alert, no_update
        
        # 判断是新建还是编辑
        is_edit_mode = user_id is not None
        
        # 密码验证逻辑
        if not is_edit_mode:
            # 新建用户时，密码为必填
            if not password:
                alert = dbc.Alert("新建用户时密码为必填字段", color="danger", duration=4000)
                return alert, no_update
            
            if len(password) < 6:
                alert = dbc.Alert("密码长度至少6位", color="danger", duration=4000)
                return alert, no_update
                
            if password != confirm_password:
                alert = dbc.Alert("两次输入的密码不一致", color="danger", duration=4000)
                return alert, no_update
        else:
            # 编辑用户时，如果填写了密码才进行验证
            if password:
                if len(password) < 6:
                    alert = dbc.Alert("密码长度至少6位", color="danger", duration=4000)
                    return alert, no_update
                    
                if password != confirm_password:
                    alert = dbc.Alert("两次输入的密码不一致", color="danger", duration=4000)
                    return alert, no_update
        
        if User and db:
            try:
                if is_edit_mode:
                    # 编辑模式
                    # 检查用户名和邮箱是否已被其他用户使用
                    existing_user = User.query.filter(
                        db.and_(
                            User.id != user_id,  # 排除当前用户
                            db.or_(User.username == username, User.email == email)
                        )
                    ).first()
                    
                    if existing_user:
                        if existing_user.username == username:
                            alert = dbc.Alert("用户名已被其他用户使用", color="danger", duration=4000)
                        else:
                            alert = dbc.Alert("邮箱已被其他用户使用", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 获取要编辑的用户
                    user = User.query.get(user_id)
                    if not user:
                        alert = dbc.Alert("用户不存在", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 更新用户信息
                    user.username = username
                    user.email = email
                    user.is_active = (status == "true")
                    
                    # 更新可选字段
                    if hasattr(user, 'real_name'):
                        user.real_name = realname or ''
                    if hasattr(user, 'phone'):
                        user.phone = phone or ''
                    if hasattr(user, 'department'):
                        user.department = department or ''
                    if hasattr(user, 'position'):
                        user.position = position or ''
                    
                    # 如果填写了新密码，则更新密码
                    if password:
                        user.set_password(password)
                    
                    success_message = "用户信息更新成功"
                    
                else:
                    # 新建模式
                    # 检查用户名和邮箱是否已存在
                    existing_user = User.query.filter(
                        db.or_(User.username == username, User.email == email)
                    ).first()
                    
                    if existing_user:
                        if existing_user.username == username:
                            alert = dbc.Alert("用户名已存在", color="danger", duration=4000)
                        else:
                            alert = dbc.Alert("邮箱已存在", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 创建新用户
                    user = User(
                        username=username,
                        email=email,
                        is_active=(status == "true")
                    )
                    user.set_password(password)
                    
                    # 设置可选字段
                    if hasattr(user, 'real_name'):
                        user.real_name = realname or ''
                    if hasattr(user, 'phone'):
                        user.phone = phone or ''
                    if hasattr(user, 'department'):
                        user.department = department or ''
                    if hasattr(user, 'position'):
                        user.position = position or ''
                    
                    db.session.add(user)
                    success_message = "用户添加成功"
                
                db.session.commit()
                
                # 返回成功提示和更新后的用户列表
                alert = dbc.Alert(success_message, color="success", duration=4000)
                
                # 重新获取用户数据
                users = User.query.all()
                users_data = []
                for user in users:
                    # 获取用户角色信息
                    user_roles = [role.name for role in user.roles] if user.roles else []
                    roles_str = ', '.join(user_roles) if user_roles else '无角色'
                    
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', '') or '',
                        'email': user.email,
                        'phone': getattr(user, 'phone', '') or '',
                        'department': getattr(user, 'department', '') or '',
                        'position': getattr(user, 'position', '') or '',
                        'roles': roles_str,
                        'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                        'is_active': '激活' if user.is_active else '禁用'
                    })
                
                return alert, users_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"保存失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 7.1 保存权限
    @app.callback(
        [Output('permission-alert-area', 'children'),
         Output('permissions-datatable', 'data', allow_duplicate=True)],
        [Input('permission-modal-save', 'n_clicks')],
        [State('permission-modal-name', 'value'),
         State('permission-modal-code', 'value'),
         State('permission-modal-module', 'value'),
         State('permission-modal-description', 'value'),
         State('permission-modal-status', 'value'),
         State('permission-modal-permission-id', 'data')],
        prevent_initial_call=True
    )
    def save_permission(save_clicks, name, code, module, description, status, permission_id):
        """保存权限（支持新建和编辑）"""
        if not save_clicks:
            return no_update
        
        # 基本字段验证
        if not name or not code or not module:
            alert = dbc.Alert("权限名称、代码和模块为必填字段", color="danger", duration=4000)
            return alert, no_update
        
        # 判断是新建还是编辑
        is_edit_mode = permission_id is not None
        
        if Permission and db:
            try:
                if is_edit_mode:
                    # 编辑模式
                    # 检查权限代码是否已被其他权限使用
                    existing_permission = Permission.query.filter(
                        db.and_(
                            Permission.id != permission_id,  # 排除当前权限
                            Permission.code == code
                        )
                    ).first()
                    
                    if existing_permission:
                        alert = dbc.Alert("权限代码已被其他权限使用", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 获取要编辑的权限
                    permission = Permission.query.get(permission_id)
                    if not permission:
                        alert = dbc.Alert("权限不存在", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 更新权限信息
                    permission.name = name
                    permission.code = code
                    permission.module = module
                    permission.description = description or ''
                    permission.is_active = (status == "true")
                    
                    success_message = "权限信息更新成功"
                    
                else:
                    # 新建模式
                    # 检查权限代码是否已存在
                    existing_permission = Permission.query.filter_by(code=code).first()
                    
                    if existing_permission:
                        alert = dbc.Alert("权限代码已存在", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 创建新权限
                    permission = Permission(
                        name=name,
                        code=code,
                        module=module,
                        description=description or '',
                        is_active=(status == "true")
                    )
                    
                    db.session.add(permission)
                    success_message = "权限添加成功"
                
                db.session.commit()
                
                # 返回成功提示和更新后的权限列表
                alert = dbc.Alert(success_message, color="success", duration=4000)
                
                # 重新获取权限数据
                permissions = Permission.query.all()
                permissions_data = []
                for permission in permissions:
                    permissions_data.append({
                        'id': permission.id,
                        'name': permission.name,
                        'code': permission.code,
                        'module': permission.module,
                        'description': permission.description or '',
                        'role_count': permission.get_role_count(),
                        'created_at': permission.created_at.strftime('%Y-%m-%d') if permission.created_at else '',
                        'is_active': '激活' if permission.is_active else '禁用'
                    })
                
                return alert, permissions_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"保存失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 8. 角色分配相关回调
    @app.callback(
        [Output('role-assignment-modal', 'is_open'),
         Output('selected-user-info', 'children'),
         Output('role-assignment-checklist', 'options'),
         Output('role-assignment-checklist', 'value'),
         Output('role-assignment-user-id', 'data')],
        [Input('user-role-assign-btn', 'n_clicks'),
         Input('role-assignment-cancel', 'n_clicks'),
         Input('role-assignment-save', 'n_clicks')],
        [State('users-datatable', 'selected_rows'),
         State('users-datatable', 'data'),
         State('role-assignment-modal', 'is_open')]
    )
    def handle_role_assignment_modal(assign_clicks, cancel_clicks, save_clicks, 
                                   selected_rows, table_data, is_open):
        """处理角色分配模态框"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'user-role-assign-btn':
            # 打开角色分配模态框
            if not selected_rows or len(selected_rows) != 1:
                return no_update
            
            if not table_data:
                return no_update
            
            try:
                # 获取选中的用户信息
                selected_user_data = table_data[selected_rows[0]]
                user_id = selected_user_data['id']
                
                # 显示用户信息
                user_info = html.Div([
                    html.P(f"用户名：{selected_user_data.get('username', '未知')}"),
                    html.P(f"真实姓名：{selected_user_data.get('real_name', '未设置')}"),
                    html.P(f"邮箱：{selected_user_data.get('email', '未知')}"),
                    html.P(f"当前角色：{selected_user_data.get('roles', '无角色')}")
                ])
                
                # 获取所有角色选项
                role_options = []
                user_role_ids = []
                
                if Role and db and User:
                    try:
                        # 获取所有角色
                        all_roles = Role.query.filter_by(is_active=True).all()
                        role_options = [
                            {'label': f"{role.name} ({role.description or '无描述'})", 'value': role.id}
                            for role in all_roles
                        ]
                        
                        # 获取用户当前角色
                        user = User.query.get(user_id)
                        if user:
                            user_role_ids = [role.id for role in user.roles]
                        
                    except Exception as e:
                        print(f"获取角色信息失败: {e}")
                
                return True, user_info, role_options, user_role_ids, user_id
                
            except Exception as e:
                print(f"处理角色分配失败: {e}")
                return no_update
        
        elif trigger_id in ['role-assignment-cancel', 'role-assignment-save']:
            # 关闭模态框
            return False, "请先选择用户", [], [], None
        
        return no_update

    # 9. 保存角色分配
    @app.callback(
        [Output('user-alert-area', 'children', allow_duplicate=True),
         Output('users-datatable', 'data', allow_duplicate=True)],
        [Input('role-assignment-save', 'n_clicks')],
        [State('role-assignment-user-id', 'data'),
         State('role-assignment-checklist', 'value')],
        prevent_initial_call=True
    )
    def save_role_assignment(save_clicks, user_id, selected_role_ids):
        """保存用户角色分配"""
        if not save_clicks or not user_id:
            return no_update
        
        if User and Role and db:
            try:
                # 获取用户
                user = User.query.get(user_id)
                if not user:
                    alert = dbc.Alert("用户不存在", color="danger", duration=4000)
                    return alert, no_update
                
                # 清除用户现有角色
                user.roles = []
                
                # 分配新角色
                if selected_role_ids:
                    new_roles = Role.query.filter(Role.id.in_(selected_role_ids)).all()
                    user.roles = new_roles
                
                db.session.commit()
                
                # 返回成功提示和更新后的用户列表
                alert = dbc.Alert("角色分配成功", color="success", duration=4000)
                
                # 重新获取用户数据
                users = User.query.all()
                users_data = []
                for user in users:
                    # 获取用户角色信息
                    user_roles = [role.name for role in user.roles] if user.roles else []
                    roles_str = ', '.join(user_roles) if user_roles else '无角色'
                    
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', '') or '',
                        'email': user.email,
                        'phone': getattr(user, 'phone', '') or '',
                        'department': getattr(user, 'department', '') or '',
                        'position': getattr(user, 'position', '') or '',
                        'roles': roles_str,
                        'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                        'is_active': '激活' if user.is_active else '禁用'
                    })
                
                return alert, users_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"角色分配失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 10. 新建角色相关回调
    @app.callback(
        [Output('role-modal', 'is_open'),
         Output('role-modal-title', 'children'),
         Output('role-modal-name', 'value'),
         Output('role-modal-code', 'value'),
         Output('role-modal-description', 'value'),
         Output('role-modal-permissions', 'options'),
         Output('role-modal-permissions', 'value'),
         Output('role-modal-status', 'value'),
         Output('role-modal-role-id', 'data')],
        [Input('create-role-btn', 'n_clicks'),
         Input('role-modal-cancel', 'n_clicks'),
         Input('role-modal-save', 'n_clicks')],
        [State('role-modal', 'is_open')]
    )
    def handle_role_modal(create_clicks, cancel_clicks, save_clicks, is_open):
        """处理角色模态框"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'create-role-btn':
            # 打开新建角色模态框
            permission_options = []
            
            if Permission and db:
                try:
                    # 获取所有权限
                    all_permissions = Permission.query.filter_by(is_active=True).all()
                    permission_options = [
                        {'label': f"{perm.name} - {perm.description or '无描述'}", 'value': perm.id}
                        for perm in all_permissions
                    ]
                except Exception as e:
                    print(f"获取权限信息失败: {e}")
            
            return True, "新建角色", "", "", "", permission_options, [], "true", None
        
        elif trigger_id in ['role-modal-cancel', 'role-modal-save']:
            # 关闭模态框
            return False, "", "", "", "", [], [], "true", None
        
        return no_update

    # 11. 保存角色
    @app.callback(
        [Output('user-alert-area', 'children', allow_duplicate=True),
         Output('role-assignment-checklist', 'options', allow_duplicate=True)],
        [Input('role-modal-save', 'n_clicks')],
        [State('role-modal-name', 'value'),
         State('role-modal-code', 'value'),
         State('role-modal-description', 'value'),
         State('role-modal-permissions', 'value'),
         State('role-modal-status', 'value')],
        prevent_initial_call=True
    )
    def save_role(save_clicks, name, code, description, permission_ids, status):
        """保存角色"""
        if not save_clicks:
            return no_update
        
        # 基本字段验证
        if not name or not code:
            alert = dbc.Alert("角色名称和代码为必填字段", color="danger", duration=4000)
            return alert, no_update
        
        if Role and Permission and db:
            try:
                # 检查角色代码是否已存在
                existing_role = Role.query.filter_by(code=code).first()
                if existing_role:
                    alert = dbc.Alert("角色代码已存在", color="danger", duration=4000)
                    return alert, no_update
                
                # 创建新角色
                role = Role(
                    name=name,
                    code=code,
                    description=description or '',
                    is_active=(status == "true"),
                    is_system=False  # 用户创建的角色不是系统角色
                )
                
                # 分配权限
                if permission_ids:
                    permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
                    role.permissions = permissions
                
                db.session.add(role)
                db.session.commit()
                
                # 返回成功提示并更新角色选项
                alert = dbc.Alert("角色创建成功", color="success", duration=4000)
                
                # 重新获取角色选项
                role_options = []
                try:
                    all_roles = Role.query.filter_by(is_active=True).all()
                    role_options = [
                        {'label': f"{role.name} ({role.description or '无描述'})", 'value': role.id}
                        for role in all_roles
                    ]
                except Exception as e:
                    print(f"更新角色选项失败: {e}")
                
                return alert, role_options
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"角色创建失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 12. 删除用户
    @app.callback(
        [Output('user-alert-area', 'children', allow_duplicate=True),
         Output('users-datatable', 'data', allow_duplicate=True)],
        [Input('users-datatable', 'data_previous'),
         Input('users-datatable', 'data')],
        prevent_initial_call=True
    )
    def delete_users(previous_data, current_data):
        """处理用户删除"""
        if not previous_data or not current_data:
            return no_update
        
        # 找出被删除的行
        previous_ids = {row['id'] for row in previous_data}
        current_ids = {row['id'] for row in current_data}
        deleted_ids = previous_ids - current_ids
        
        if deleted_ids and User and db:
            try:
                for user_id in deleted_ids:
                    user = User.query.get(user_id)
                    if user:
                        db.session.delete(user)
                
                db.session.commit()
                alert = dbc.Alert(f"成功删除 {len(deleted_ids)} 个用户", color="success", duration=4000)
                
                # 重新获取用户数据
                users = User.query.all()
                users_data = []
                for user in users:
                    # 获取用户角色信息
                    user_roles = [role.name for role in user.roles] if user.roles else []
                    roles_str = ', '.join(user_roles) if user_roles else '无角色'
                    
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', '') or '',
                        'email': user.email,
                        'phone': getattr(user, 'phone', '') or '',
                        'department': getattr(user, 'department', '') or '',
                        'position': getattr(user, 'position', '') or '',
                        'roles': roles_str,
                        'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                        'is_active': '激活' if user.is_active else '禁用'
                    })
                
                return alert, users_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"删除失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        
        return no_update

    # 12.1 删除权限
    @app.callback(
        [Output('permission-alert-area', 'children', allow_duplicate=True),
         Output('permissions-datatable', 'data', allow_duplicate=True)],
        [Input('permissions-datatable', 'data_previous'),
         Input('permissions-datatable', 'data')],
        prevent_initial_call=True
    )
    def delete_permissions(previous_data, current_data):
        """处理权限删除"""
        if not previous_data or not current_data:
            return no_update
        
        # 找出被删除的行
        previous_ids = {row['id'] for row in previous_data}
        current_ids = {row['id'] for row in current_data}
        deleted_ids = previous_ids - current_ids
        
        if deleted_ids and Permission and db:
            try:
                deleted_count = 0
                skipped_count = 0
                
                for permission_id in deleted_ids:
                    permission = Permission.query.get(permission_id)
                    if permission:
                        # 检查权限是否被角色使用
                        if permission.roles:
                            skipped_count += 1
                            continue
                        
                        db.session.delete(permission)
                        deleted_count += 1
                
                db.session.commit()
                
                if deleted_count > 0 and skipped_count > 0:
                    alert = dbc.Alert(f"成功删除 {deleted_count} 个权限，跳过 {skipped_count} 个正在使用的权限", color="warning", duration=4000)
                elif deleted_count > 0:
                    alert = dbc.Alert(f"成功删除 {deleted_count} 个权限", color="success", duration=4000)
                else:
                    alert = dbc.Alert("所选权限正在被角色使用，无法删除", color="warning", duration=4000)
                
                # 重新获取权限数据
                permissions = Permission.query.all()
                permissions_data = []
                for permission in permissions:
                    permissions_data.append({
                        'id': permission.id,
                        'name': permission.name,
                        'code': permission.code,
                        'module': permission.module,
                        'description': permission.description or '',
                        'role_count': permission.get_role_count(),
                        'created_at': permission.created_at.strftime('%Y-%m-%d') if permission.created_at else '',
                        'is_active': '激活' if permission.is_active else '禁用'
                    })
                
                return alert, permissions_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"删除失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        
        return no_update

    # 13. 导出用户数据
    @app.callback(
        Output('user-export-btn', 'n_clicks'),
        [Input('user-export-btn', 'n_clicks')],
        [State('users-datatable', 'data')]
    )
    def export_users(export_clicks, table_data):
        """导出用户数据"""
        if export_clicks and table_data:
            try:
                # 这里可以实现CSV导出功能
                df = pd.DataFrame(table_data)
                # df.to_csv('users_export.csv', index=False)
                print("用户数据导出功能待实现")
            except Exception as e:
                print(f"导出失败: {e}")
        
        return 0

    # 13.1 导出权限数据
    @app.callback(
        Output('permission-export-btn', 'n_clicks'),
        [Input('permission-export-btn', 'n_clicks')],
        [State('permissions-datatable', 'data')]
    )
    def export_permissions(export_clicks, table_data):
        """导出权限数据"""
        if export_clicks and table_data:
            try:
                # 这里可以实现CSV导出功能
                df = pd.DataFrame(table_data)
                # df.to_csv('permissions_export.csv', index=False)
                print("权限数据导出功能待实现")
            except Exception as e:
                print(f"导出失败: {e}")
        
        return 0
    
    # 在 management_callbacks.py 文件中的 management_callbacks(app) 函数内添加以下回调函数：

    # 1.2 页面加载时获取任务数据
    @app.callback(
        Output('tasks-datatable', 'data'),
        [Input('task-table-container', 'children')]
    )
    def load_tasks_data(children):
        """加载任务数据"""
        if Task and db:
            try:
                tasks = Task.query.all()
                tasks_data = []
                for task in tasks:
                    tasks_data.append({
                        'id': task.id,
                        'name': task.title,
                        'type': task.task_type,
                        'priority': task.priority,
                        'status': task.status,
                        'progress': f"{task.progress}%",
                        'creator': task.creator.username if task.creator else '',
                        'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else '',
                        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                        'description': task.description or ''
                    })
                return tasks_data
            except Exception as e:
                print(f"获取任务数据失败: {e}")
                return []
        else:
            # 返回示例数据（当数据库不可用时）
            return [
                {
                    'id': 1,
                    'name': '系统数据备份',
                    'type': '维护任务',
                    'priority': '高',
                    'status': '执行中',
                    'creator': '管理员',
                    'created_at': '2024-01-15',
                    'due_date': '2024-01-20',
                    'progress': '60%',
                    'description': '定期系统数据备份任务'
                },
                {
                    'id': 2,
                    'name': '用户权限审核',
                    'type': '审核任务',
                    'priority': '中',
                    'status': '待处理',
                    'creator': '超级管理员',
                    'created_at': '2024-01-18',
                    'due_date': '2024-01-25',
                    'progress': '0%',
                    'description': '定期用户权限审核'
                }
            ]

    # 3.2 任务搜索和更新功能
    @app.callback(
        Output('tasks-datatable', 'data', allow_duplicate=True),
        [Input('task-search-btn', 'n_clicks'),
         Input('task-refresh-btn', 'n_clicks')],
        [State('task-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_or_refresh_tasks(search_clicks, refresh_clicks, search_value):
        """搜索任务或刷新数据"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if Task and db:
            try:
                if trigger_id == 'task-refresh-btn':
                    # 刷新所有任务数据
                    tasks = Task.query.all()
                elif trigger_id == 'task-search-btn' and search_value:
                    # 搜索任务
                    search_term = f"%{search_value}%"
                    tasks = Task.query.filter(
                        db.or_(
                            Task.title.like(search_term),
                            Task.task_type.like(search_term),
                            Task.description.like(search_term)
                        )
                    ).all()
                else:
                    return no_update
                
                tasks_data = []
                for task in tasks:
                    tasks_data.append({
                        'id': task.id,
                        'name': task.title,
                        'type': task.task_type,
                        'priority': task.priority,
                        'status': task.status,
                        'progress': f"{task.progress}%",
                        'creator': task.creator.username if task.creator else '',
                        'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else '',
                        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                        'description': task.description or ''
                    })
                return tasks_data
            except Exception as e:
                print(f"操作失败: {e}")
                return no_update
        
        return no_update

    # 4.2 任务更新成功提示
    @app.callback(
        Output('task-alert-area', 'children', allow_duplicate=True),
        [Input('task-refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_task_refresh_message(refresh_clicks):
        """显示任务刷新成功消息"""
        if refresh_clicks:
            return dbc.Alert("任务数据已更新", color="success", duration=3000)
        return no_update

    # 5.2 任务编辑按钮检测选中行
    @app.callback(
        Output('task-alert-area', 'children', allow_duplicate=True),
        [Input('task-edit-btn', 'n_clicks')],
        [State('tasks-datatable', 'selected_rows'),
         State('tasks-datatable', 'data')],
        prevent_initial_call=True
    )
    def check_task_edit_selection(edit_clicks, selected_rows, table_data):
        """检测任务编辑按钮点击和选中行"""
        if not edit_clicks:
            return no_update
        
        if not selected_rows or len(selected_rows) == 0:
            return dbc.Alert("请先点击表格中的行来选择要编辑的任务", color="warning", duration=4000)
        elif len(selected_rows) > 1:
            return dbc.Alert("请只选择一个任务进行编辑", color="warning", duration=4000)
        
        # 如果选中了一行，显示选中的任务信息
        if table_data and selected_rows:
            try:
                selected_task = table_data[selected_rows[0]]
                return dbc.Alert(f"已选中任务: {selected_task.get('name', '未知')}", color="info", duration=2000)
            except Exception as e:
                print(f"获取选中任务信息失败: {e}")
                return dbc.Alert("获取任务信息失败", color="danger", duration=4000)
        
        return no_update

    # 6.2 任务模态框控制
    @app.callback(
        [Output('task-modal', 'is_open'),
         Output('task-modal-title', 'children'),
         Output('task-modal-name', 'value'),
         Output('task-modal-type', 'value'),
         Output('task-modal-priority', 'value'),
         Output('task-modal-status', 'value'),
         Output('task-modal-due-date', 'value'),
         Output('task-modal-progress', 'value'),
         Output('task-modal-description', 'value'),
         Output('task-modal-task-id', 'data')],
        [Input('task-add-btn', 'n_clicks'),
         Input('task-edit-btn', 'n_clicks'),
         Input('task-modal-cancel', 'n_clicks'),
         Input('task-modal-save', 'n_clicks')],
        [State('task-modal', 'is_open'),
         State('tasks-datatable', 'selected_rows'),
         State('tasks-datatable', 'data')]
    )
    def handle_task_modal(add_clicks, edit_clicks, cancel_clicks, save_clicks, is_open, selected_rows, table_data):
        """处理任务模态框"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'task-add-btn':
            # 添加任务 - 清空所有字段
            return (True, "添加任务", "", "", "中", "待处理", "", 0, "", None)
        
        elif trigger_id == 'task-edit-btn':
            # 编辑任务 - 预填充现有数据
            if not selected_rows or len(selected_rows) != 1:
                return no_update
            
            if not table_data:
                return no_update
            
            try:
                # 获取选中行的数据
                selected_task_data = table_data[selected_rows[0]]
                task_id = selected_task_data['id']
                
                if Task and db:
                    try:
                        task = Task.query.get(task_id)
                        if task:
                            return (
                                True, "编辑任务",
                                task.title,
                                task.task_type,
                                task.priority,
                                task.status,
                                task.due_date.strftime('%Y-%m-%d') if task.due_date else "",
                                task.progress,
                                task.description or '',
                                task.id
                            )
                    except Exception as e:
                        print(f"获取任务详细信息失败: {e}")
                
                # 如果数据库查询失败，使用表格数据
                return (
                    True, "编辑任务",
                    selected_task_data.get('name', ''),
                    selected_task_data.get('type', ''),
                    selected_task_data.get('priority', '中'),
                    selected_task_data.get('status', '待处理'),
                    selected_task_data.get('due_date', ''),
                    int(selected_task_data.get('progress', '0%').rstrip('%')),
                    selected_task_data.get('description', ''),
                    selected_task_data.get('id')
                )
                
            except (IndexError, KeyError) as e:
                print(f"获取选中任务数据失败: {e}")
                return no_update
        
        elif trigger_id in ['task-modal-cancel', 'task-modal-save']:
            # 关闭模态框并清空所有字段
            return (False, "", "", "", "中", "待处理", "", 0, "", None)
        
        return no_update

    # 7.2 保存任务
    @app.callback(
        [Output('task-alert-area', 'children'),
         Output('tasks-datatable', 'data', allow_duplicate=True)],
        [Input('task-modal-save', 'n_clicks')],
        [State('task-modal-name', 'value'),
         State('task-modal-type', 'value'),
         State('task-modal-priority', 'value'),
         State('task-modal-status', 'value'),
         State('task-modal-due-date', 'value'),
         State('task-modal-progress', 'value'),
         State('task-modal-description', 'value'),
         State('task-modal-task-id', 'data')],
        prevent_initial_call=True
    )
    def save_task(save_clicks, name, task_type, priority, status, due_date, progress, description, task_id):
        """保存任务（支持新建和编辑）"""
        if not save_clicks:
            return no_update
        
        # 基本字段验证
        if not name or not task_type:
            alert = dbc.Alert("任务名称和类型为必填字段", color="danger", duration=4000)
            return alert, no_update
        
        # 判断是新建还是编辑
        is_edit_mode = task_id is not None
        
        if Task and db:
            try:
                # 导入datetime模块用于日期处理
                from datetime import datetime
                
                if is_edit_mode:
                    # 编辑模式
                    task = Task.query.get(task_id)
                    if not task:
                        alert = dbc.Alert("任务不存在", color="danger", duration=4000)
                        return alert, no_update
                    
                    # 更新任务信息
                    task.title = name
                    task.task_type = task_type
                    task.priority = priority
                    task.status = status
                    task.progress = progress or 0
                    task.description = description
                    
                    # 处理截止日期
                    if due_date:
                        task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
                    else:
                        task.due_date = None
                    
                    # 如果状态变为已完成，自动设置完成时间和进度
                    if status == '已完成':
                        task.progress = 100
                        task.completed_at = datetime.utcnow()
                    
                    success_message = "任务信息更新成功"
                    
                else:
                    # 新建模式
                    # 创建新任务
                    task = Task(
                        title=name,
                        task_type=task_type,
                        priority=priority,
                        status=status,
                        progress=progress or 0,
                        description=description,
                        creator_id=current_user.id if current_user and current_user.is_authenticated else 1
                    )
                    
                    # 处理截止日期
                    if due_date:
                        task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
                    
                    db.session.add(task)
                    success_message = "任务添加成功"
                
                db.session.commit()
                
                # 返回成功提示和更新后的任务列表
                alert = dbc.Alert(success_message, color="success", duration=4000)
                
                # 重新获取任务数据
                tasks = Task.query.all()
                tasks_data = []
                for task in tasks:
                    tasks_data.append({
                        'id': task.id,
                        'name': task.title,
                        'type': task.task_type,
                        'priority': task.priority,
                        'status': task.status,
                        'progress': f"{task.progress}%",
                        'creator': task.creator.username if task.creator else '',
                        'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else '',
                        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                        'description': task.description or ''
                    })
                
                return alert, tasks_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"保存失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 12.2 删除任务
    @app.callback(
        [Output('task-alert-area', 'children', allow_duplicate=True),
         Output('tasks-datatable', 'data', allow_duplicate=True)],
        [Input('tasks-datatable', 'data_previous'),
         Input('tasks-datatable', 'data')],
        prevent_initial_call=True
    )
    def delete_tasks(previous_data, current_data):
        """处理任务删除"""
        if not previous_data or not current_data:
            return no_update
        
        # 找出被删除的行
        previous_ids = {row['id'] for row in previous_data}
        current_ids = {row['id'] for row in current_data}
        deleted_ids = previous_ids - current_ids
        
        if deleted_ids and Task and db:
            try:
                for task_id in deleted_ids:
                    task = Task.query.get(task_id)
                    if task:
                        db.session.delete(task)
                
                db.session.commit()
                alert = dbc.Alert(f"成功删除 {len(deleted_ids)} 个任务", color="success", duration=4000)
                
                # 重新获取任务数据
                tasks = Task.query.all()
                tasks_data = []
                for task in tasks:
                    tasks_data.append({
                        'id': task.id,
                        'name': task.title,
                        'type': task.task_type,
                        'priority': task.priority,
                        'status': task.status,
                        'progress': f"{task.progress}%",
                        'creator': task.creator.username if task.creator else '',
                        'created_at': task.created_at.strftime('%Y-%m-%d') if task.created_at else '',
                        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                        'description': task.description or ''
                    })
                
                return alert, tasks_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"删除失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        
        return no_update

    # 13.2 导出任务数据
    @app.callback(
        Output('task-export-btn', 'n_clicks'),
        [Input('task-export-btn', 'n_clicks')],
        [State('tasks-datatable', 'data')]
    )
    def export_tasks(export_clicks, table_data):
        """导出任务数据"""
        if export_clicks and table_data:
            try:
                # 这里可以实现CSV导出功能
                df = pd.DataFrame(table_data)
                # df.to_csv('tasks_export.csv', index=False)
                print("任务数据导出功能待实现")
            except Exception as e:
                print(f"导出失败: {e}")
        
        return 0
    
# 1.3 日志标签页切换
    @app.callback(
        [Output("operation-logs-content", "style"),
         Output("login-logs-content", "style")],
        [Input("log-tabs", "active_tab")]
    )
    def switch_log_tabs(active_tab):
        """切换日志标签页"""
        if active_tab == "operation-logs":
            return {"display": "block"}, {"display": "none"}
        else:
            return {"display": "none"}, {"display": "block"}

    # 1.4 页面加载时获取操作日志数据
    @app.callback(
        Output('operation-logs-datatable', 'data'),
        [Input('operation-log-table-container', 'children')]
    )
    def load_operation_logs_data(children):
        """加载操作日志数据"""
        if OperationLog and db:
            try:
                # 获取除登录日志外的所有操作日志
                logs = OperationLog.query.filter(
                    ~OperationLog.operation_type.in_(['LOGIN', 'LOGOUT'])
                ).order_by(OperationLog.created_at.desc()).limit(1000).all()
                
                logs_data = []
                for log in logs:
                    # 构建目标信息
                    target_info = ""
                    if log.target_type and log.target_id:
                        target_info = f"{log.target_type}:{log.target_id}"
                    elif log.error_message:
                        target_info = log.error_message[:50] + "..." if len(log.error_message) > 50 else log.error_message
                    
                    logs_data.append({
                        'id': log.id,
                        'operation_desc': log.operation_desc,
                        'username': log.user.username if log.user else 'System',
                        'module': log.module,
                        'operation_type': log.operation_type,
                        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                        'level': log.level,
                        'status': log.status,
                        'ip_address': log.ip_address or '',
                        'target_info': target_info
                    })
                return logs_data
            except Exception as e:
                print(f"获取操作日志数据失败: {e}")
                return []
        else:
            # 返回示例数据
            return [
                {
                    'id': 1,
                    'operation_desc': 'API调用日志记录',
                    'username': '超级管理员',
                    'module': 'user',
                    'operation_type': 'CREATE',
                    'created_at': '2025-07-20 15:18:55',
                    'level': 'info',
                    'status': 'success',
                    'ip_address': '192.168.1.100',
                    'target_info': '用户创建成功'
                }
            ]

    # 1.5 页面加载时获取登录日志数据
    @app.callback(
        Output('login-logs-datatable', 'data'),
        [Input('login-log-table-container', 'children')]
    )
    def load_login_logs_data(children):
        """加载登录日志数据"""
        if OperationLog and db:
            try:
                # 只获取登录相关的日志
                logs = OperationLog.query.filter(
                    OperationLog.operation_type.in_(['LOGIN', 'LOGOUT', 'LOGIN_FAILED'])
                ).order_by(OperationLog.created_at.desc()).limit(1000).all()
                
                logs_data = []
                for log in logs:
                    # 构建目标信息
                    target_info = ""
                    if log.error_message:
                        target_info = log.error_message
                    elif log.status == 'success':
                        target_info = "登录成功" if log.operation_type == 'LOGIN' else "退出成功"
                    else:
                        target_info = "登录失败"
                    
                    logs_data.append({
                        'id': log.id,
                        'operation_desc': log.operation_desc,
                        'username': log.user.username if log.user else 'Unknown',
                        'operation_type': log.operation_type,
                        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                        'ip_address': log.ip_address or '',
                        'status': log.status,
                        'user_agent': (log.user_agent[:50] + "...") if log.user_agent and len(log.user_agent) > 50 else (log.user_agent or ''),
                        'target_info': target_info
                    })
                return logs_data
            except Exception as e:
                print(f"获取登录日志数据失败: {e}")
                return []
        else:
            # 返回示例数据
            return [
                {
                    'id': 1,
                    'operation_desc': 'API调用日志记录',
                    'username': '超级管理员',
                    'operation_type': 'LOGIN',
                    'created_at': '2025-07-20 15:18:55',
                    'ip_address': '192.168.1.100',
                    'status': 'success',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'target_info': '登录成功'
                }
            ]

    # 3.3 操作日志搜索和筛选
    @app.callback(
        Output('operation-logs-datatable', 'data', allow_duplicate=True),
        [Input('operation-log-search-btn', 'n_clicks'),
         Input('operation-log-refresh-btn', 'n_clicks'),
         Input('operation-log-level-filter', 'value'),
         Input('operation-log-module-filter', 'value')],
        [State('operation-log-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_or_filter_operation_logs(search_clicks, refresh_clicks, level_filter, module_filter, search_value):
        """搜索和筛选操作日志"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        if OperationLog and db:
            try:
                # 构建查询条件
                query = OperationLog.query.filter(
                    ~OperationLog.operation_type.in_(['LOGIN', 'LOGOUT'])
                )
                
                # 添加搜索条件
                if search_value:
                    search_term = f"%{search_value}%"
                    query = query.filter(
                        db.or_(
                            OperationLog.operation_desc.like(search_term),
                            OperationLog.module.like(search_term),
                            OperationLog.operation_type.like(search_term)
                        )
                    )
                
                # 添加级别筛选
                if level_filter and level_filter != 'all':
                    query = query.filter(OperationLog.level == level_filter)
                
                # 添加模块筛选
                if module_filter and module_filter != 'all':
                    query = query.filter(OperationLog.module == module_filter)
                
                logs = query.order_by(OperationLog.created_at.desc()).limit(1000).all()
                
                logs_data = []
                for log in logs:
                    target_info = ""
                    if log.target_type and log.target_id:
                        target_info = f"{log.target_type}:{log.target_id}"
                    elif log.error_message:
                        target_info = log.error_message[:50] + "..." if len(log.error_message) > 50 else log.error_message
                    
                    logs_data.append({
                        'id': log.id,
                        'operation_desc': log.operation_desc,
                        'username': log.user.username if log.user else 'System',
                        'module': log.module,
                        'operation_type': log.operation_type,
                        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                        'level': log.level,
                        'status': log.status,
                        'ip_address': log.ip_address or '',
                        'target_info': target_info
                    })
                return logs_data
            except Exception as e:
                print(f"操作日志查询失败: {e}")
                return no_update
        
        return no_update

    # 3.4 登录日志搜索和筛选
    @app.callback(
        Output('login-logs-datatable', 'data', allow_duplicate=True),
        [Input('login-log-search-btn', 'n_clicks'),
         Input('login-log-refresh-btn', 'n_clicks'),
         Input('login-log-status-filter', 'value')],
        [State('login-log-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_or_filter_login_logs(search_clicks, refresh_clicks, status_filter, search_value):
        """搜索和筛选登录日志"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        if OperationLog and db:
            try:
                # 构建查询条件
                query = OperationLog.query.filter(
                    OperationLog.operation_type.in_(['LOGIN', 'LOGOUT', 'LOGIN_FAILED'])
                )
                
                # 添加搜索条件
                if search_value:
                    search_term = f"%{search_value}%"
                    query = query.join(User, OperationLog.user_id == User.id, isouter=True).filter(
                        db.or_(
                            User.username.like(search_term),
                            OperationLog.ip_address.like(search_term),
                            OperationLog.operation_desc.like(search_term)
                        )
                    )
                
                # 添加状态筛选
                if status_filter and status_filter != 'all':
                    query = query.filter(OperationLog.status == status_filter)
                
                logs = query.order_by(OperationLog.created_at.desc()).limit(1000).all()
                
                logs_data = []
                for log in logs:
                    target_info = ""
                    if log.error_message:
                        target_info = log.error_message
                    elif log.status == 'success':
                        target_info = "登录成功" if log.operation_type == 'LOGIN' else "退出成功"
                    else:
                        target_info = "登录失败"
                    
                    logs_data.append({
                        'id': log.id,
                        'operation_desc': log.operation_desc,
                        'username': log.user.username if log.user else 'Unknown',
                        'operation_type': log.operation_type,
                        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                        'ip_address': log.ip_address or '',
                        'status': log.status,
                        'user_agent': (log.user_agent[:50] + "...") if log.user_agent and len(log.user_agent) > 50 else (log.user_agent or ''),
                        'target_info': target_info
                    })
                return logs_data
            except Exception as e:
                print(f"登录日志查询失败: {e}")
                return no_update
        
        return no_update

    # 4.3 操作日志刷新成功提示
    @app.callback(
        Output('operation-log-alert-area', 'children', allow_duplicate=True),
        [Input('operation-log-refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_operation_log_refresh_message(refresh_clicks):
        """显示操作日志刷新成功消息"""
        if refresh_clicks:
            return dbc.Alert("操作日志已更新", color="success", duration=3000)
        return no_update

    # 4.4 登录日志刷新成功提示
    @app.callback(
        Output('login-log-alert-area', 'children', allow_duplicate=True),
        [Input('login-log-refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_login_log_refresh_message(refresh_clicks):
        """显示登录日志刷新成功消息"""
        if refresh_clicks:
            return dbc.Alert("登录日志已更新", color="info", duration=3000)
        return no_update

    # 清理操作日志
    @app.callback(
        [Output('operation-log-alert-area', 'children'),
         Output('operation-logs-datatable', 'data', allow_duplicate=True)],
        [Input('operation-log-clear-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_operation_logs(clear_clicks):
        """清理操作日志（保留最近30天）"""
        if not clear_clicks:
            return no_update
        
        if OperationLog and db:
            try:
                from datetime import datetime, timedelta
                
                # 计算30天前的日期
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                
                # 删除30天前的非关键日志
                deleted_count = OperationLog.query.filter(
                    db.and_(
                        OperationLog.created_at < thirty_days_ago,
                        ~OperationLog.operation_type.in_(['LOGIN', 'LOGOUT']),
                        OperationLog.level.in_(['debug', 'info'])  # 只删除非重要日志
                    )
                ).delete()
                
                db.session.commit()
                
                # 重新获取日志数据
                logs = OperationLog.query.filter(
                    ~OperationLog.operation_type.in_(['LOGIN', 'LOGOUT'])
                ).order_by(OperationLog.created_at.desc()).limit(1000).all()
                
                logs_data = []
                for log in logs:
                    target_info = ""
                    if log.target_type and log.target_id:
                        target_info = f"{log.target_type}:{log.target_id}"
                    elif log.error_message:
                        target_info = log.error_message[:50] + "..." if len(log.error_message) > 50 else log.error_message
                    
                    logs_data.append({
                        'id': log.id,
                        'operation_desc': log.operation_desc,
                        'username': log.user.username if log.user else 'System',
                        'module': log.module,
                        'operation_type': log.operation_type,
                        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                        'level': log.level,
                        'status': log.status,
                        'ip_address': log.ip_address or '',
                        'target_info': target_info
                    })
                
                alert = dbc.Alert(f"已清理 {deleted_count} 条历史日志", color="success", duration=4000)
                return alert, logs_data
                
            except Exception as e:
                db.session.rollback()
                alert = dbc.Alert(f"清理日志失败: {str(e)}", color="danger", duration=4000)
                return alert, no_update
        else:
            alert = dbc.Alert("数据库连接失败", color="danger", duration=4000)
            return alert, no_update

    # 13.3 导出操作日志数据
    @app.callback(
        Output('operation-log-export-btn', 'n_clicks'),
        [Input('operation-log-export-btn', 'n_clicks')],
        [State('operation-logs-datatable', 'data')]
    )
    def export_operation_logs(export_clicks, table_data):
        """导出操作日志数据"""
        if export_clicks and table_data:
            try:
                # 这里可以实现CSV导出功能
                df = pd.DataFrame(table_data)
                # df.to_csv('operation_logs_export.csv', index=False)
                print("操作日志数据导出功能待实现")
            except Exception as e:
                print(f"导出失败: {e}")
        
        return 0

    # 13.4 导出登录日志数据
    @app.callback(
        Output('login-log-export-btn', 'n_clicks'),
        [Input('login-log-export-btn', 'n_clicks')],
        [State('login-logs-datatable', 'data')]
    )
    def export_login_logs(export_clicks, table_data):
        """导出登录日志数据"""
        if export_clicks and table_data:
            try:
                # 这里可以实现CSV导出功能
                df = pd.DataFrame(table_data)
                # df.to_csv('login_logs_export.csv', index=False)
                print("登录日志数据导出功能待实现")
            except Exception as e:
                print(f"导出失败: {e}")
        
        return 0