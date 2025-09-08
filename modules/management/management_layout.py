# modules/management/management_layout.py
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# 配置颜色常量
PRIMARY_COLOR = "#007bff"
SECONDARY_COLOR = "#6c757d"
ACCENT_COLOR = "#28a745"
BG_COLOR = "#f8f9fa"
CARD_BG = "#ffffff"

def create_management_layout():
    """创建管理模块的主布局"""
    return html.Div(
        children=[
            # 管理功能导航区域
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("管理功能导航", className="mb-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-users fa-3x text-primary mb-3"),
                                            html.H5("用户管理", className="card-title"),
                                            html.P("管理系统用户信息和账户", className="card-text"),
                                            dbc.Button("进入", id="btn-user-mgmt", color="primary", size="sm")
                                        ], className="text-center")
                                    ], className="h-100")
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-shield-alt fa-3x text-success mb-3"),
                                            html.H5("权限管理", className="card-title"),
                                            html.P("管理用户权限和访问控制", className="card-text"),
                                            dbc.Button("进入", id="btn-permission-mgmt", color="success", size="sm")
                                        ], className="text-center")
                                    ], className="h-100")
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-tasks fa-3x text-warning mb-3"),
                                            html.H5("任务管理", className="card-title"),
                                            html.P("管理系统任务和工作流程", className="card-text"),
                                            dbc.Button("进入", id="btn-task-mgmt", color="warning", size="sm")
                                        ], className="text-center")
                                    ], className="h-100")
                                ], width=3),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-clipboard-list fa-3x text-info mb-3"),
                                            html.H5("日志管理", className="card-title"),
                                            html.P("查看和管理系统操作日志", className="card-text"),
                                            dbc.Button("进入", id="btn-log-mgmt", color="info", size="sm")
                                        ], className="text-center")
                                    ], className="h-100")
                                ], width=3)
                            ])
                        ])
                    ], className="mb-4", style={'backgroundColor': CARD_BG})
                ])
            ]),
            
            # 具体管理内容区域
            dbc.Row([
                dbc.Col([
                    html.Div(id="management-content-area", children=create_user_management_content())
                ])
            ])
        ]
    )

def create_user_management_content():
    """创建用户管理内容"""
    return html.Div([
        # 添加用户模态框
        create_user_modal(),
        # 添加角色分配模态框
        create_role_assignment_modal(),
        # 添加新建角色模态框
        create_role_modal(),
        
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("用户管理", className="mb-0", style={'color': PRIMARY_COLOR}),
                    html.Small("管理系统用户信息和账户", className="text-muted")
                ])
            ]),
            dbc.CardBody([
                # 顶部操作栏
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="user-search-input",
                                placeholder="搜索用户名、邮箱...",
                                style={'borderRadius': '5px 0 0 5px'}
                            ),
                            dbc.Button(
                                html.I(className="fas fa-search"),
                                id="user-search-btn",
                                color="primary",
                                style={'borderRadius': '0 5px 5px 0'}
                            )
                        ])
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-plus me-2"), "添加"],
                                id="user-add-btn",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-edit me-2"), "编辑"],
                                id="user-edit-btn",
                                color="warning",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-user-tag me-2"), "分配角色"],
                                id="user-role-assign-btn",
                                color="info",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "更新"],
                                id="user-refresh-btn",
                                color="primary",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "导出"],
                                id="user-export-btn",
                                color="secondary"
                            )
                        ], className="text-end")
                    ], width=8)
                ], className="mb-3"),
                
                # 用户列表表格
                html.Div(id="user-table-container", children=[
                    get_user_datatable()
                ]),
                
                # 操作提示区域
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "操作说明：点击表格中的行来选择用户，然后点击相应的操作按钮。编辑功能会自动填充用户现有信息。"
                        ], color="info", className="mb-2", style={'fontSize': '14px'})
                    ])
                ]),
                
                # 操作结果提示区域
                html.Div(id="user-alert-area", className="mt-3")
            ])
        ], style={'backgroundColor': CARD_BG})
    ])

def get_user_datatable(users_data=None):
    """获取用户数据表格"""
    # 如果没有传入数据，使用默认数据
    if users_data is None:
        users_data = []
    
    return dash_table.DataTable(
        id='users-datatable',
        data=users_data,
        columns=[
            {"name": "ID", "id": "id", "type": "numeric", "editable": False},
            {"name": "账号", "id": "username", "editable": False},
            {"name": "真实姓名", "id": "real_name", "editable": False},
            {"name": "邮箱", "id": "email", "editable": False},
            {"name": "电话", "id": "phone", "editable": False},
            {"name": "部门", "id": "department", "editable": False},
            {"name": "职位", "id": "position", "editable": False},
            {"name": "角色", "id": "roles", "editable": False},  # 新增角色列
            {"name": "创建时间", "id": "created_at", "editable": False},
            {"name": "状态", "id": "is_active", "editable": False},
        ],
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{is_active} = true'},
                'backgroundColor': '#d4edda',
            },
            {
                'if': {'filter_query': '{is_active} = false'},
                'backgroundColor': '#f8d7da',
            }
        ],
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_deletable=True
    )

def create_permission_management_content():
    """创建权限管理内容"""
    return html.Div([
        # 添加权限模态框
        create_permission_modal(),
        
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("权限管理", className="mb-0", style={'color': ACCENT_COLOR}),
                    html.Small("管理系统权限和访问控制", className="text-muted")
                ])
            ]),
            dbc.CardBody([
                # 顶部操作栏
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="permission-search-input",
                                placeholder="搜索权限名称、代码...",
                                style={'borderRadius': '5px 0 0 5px'}
                            ),
                            dbc.Button(
                                html.I(className="fas fa-search"),
                                id="permission-search-btn",
                                color="success",
                                style={'borderRadius': '0 5px 5px 0'}
                            )
                        ])
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-plus me-2"), "添加权限"],
                                id="permission-add-btn",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-edit me-2"), "编辑"],
                                id="permission-edit-btn",
                                color="warning",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "更新"],
                                id="permission-refresh-btn",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "导出"],
                                id="permission-export-btn",
                                color="secondary"
                            )
                        ], className="text-end")
                    ], width=8)
                ], className="mb-3"),
                
                # 权限列表表格
                html.Div(id="permission-table-container", children=[
                    get_permission_datatable()
                ]),
                
                # 操作提示区域
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "操作说明：点击表格中的行来选择权限，然后点击相应的操作按钮。系统内置权限不能删除，但可以编辑描述。"
                        ], color="info", className="mb-2", style={'fontSize': '14px'})
                    ])
                ]),
                
                # 操作结果提示区域
                html.Div(id="permission-alert-area", className="mt-3")
            ])
        ], style={'backgroundColor': CARD_BG})
    ])

def get_permission_datatable(permissions_data=None):
    """获取权限数据表格"""
    # 如果没有传入数据，使用默认数据
    if permissions_data is None:
        permissions_data = []
    
    return dash_table.DataTable(
        id='permissions-datatable',
        data=permissions_data,
        columns=[
            {"name": "ID", "id": "id", "type": "numeric", "editable": False},
            {"name": "权限名称", "id": "name", "editable": False},
            {"name": "权限代码", "id": "code", "editable": False},
            {"name": "所属模块", "id": "module", "editable": False},
            {"name": "描述", "id": "description", "editable": False},
            {"name": "关联角色数", "id": "role_count", "type": "numeric", "editable": False},
            {"name": "创建时间", "id": "created_at", "editable": False},
            {"name": "状态", "id": "is_active", "editable": False},
        ],
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{is_active} = 激活'},
                'backgroundColor': '#d4edda',
            },
            {
                'if': {'filter_query': '{is_active} = 禁用'},
                'backgroundColor': '#f8d7da',
            }
        ],
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_deletable=True
    )

def create_permission_modal():
    """创建权限添加/编辑模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="permission-modal-title")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("权限名称 *"),
                        dbc.Input(
                            id="permission-modal-name",
                            type="text",
                            placeholder="请输入权限名称"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("权限代码 *"),
                        dbc.Input(
                            id="permission-modal-code",
                            type="text",
                            placeholder="请输入权限代码"
                        ),
                        dbc.FormText("权限代码必须唯一，建议使用英文下划线格式", color="muted")
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("所属模块 *"),
                        dbc.Select(
                            id="permission-modal-module",
                            options=[
                                {"label": "数据管理", "value": "data"},
                                {"label": "用户管理", "value": "user"},
                                {"label": "系统管理", "value": "system"},
                                {"label": "报表管理", "value": "report"},
                                {"label": "权限管理", "value": "permission"},
                                {"label": "任务管理", "value": "task"},
                                {"label": "日志管理", "value": "log"},
                                {"label": "审计管理", "value": "audit"},
                                {"label": "指标管理", "value": "indicator"},
                                {"label": "预测管理", "value": "prediction"},
                                {"label": "施工管理", "value": "construction"},
                                {"label": "平台对接", "value": "integration"}
                            ],
                            placeholder="请选择权限所属模块"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("权限状态"),
                        dbc.Select(
                            id="permission-modal-status",
                            options=[
                                {"label": "激活", "value": "true"},
                                {"label": "禁用", "value": "false"}
                            ],
                            value="true"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("权限描述"),
                        dbc.Textarea(
                            id="permission-modal-description",
                            placeholder="请输入权限描述",
                            rows=3
                        )
                    ])
                ], className="mb-3"),
                
                # 隐藏字段用于存储编辑时的权限ID
                dcc.Store(id="permission-modal-permission-id", data=None)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="permission-modal-cancel", color="secondary", className="me-2"),
            dbc.Button("保存", id="permission-modal-save", color="success")
        ])
    ], id="permission-modal", size="lg", is_open=False)

def create_user_modal():
    """创建用户添加/编辑模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="user-modal-title")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("用户名 *"),
                        dbc.Input(
                            id="user-modal-username",
                            type="text",
                            placeholder="请输入用户名"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("真实姓名"),
                        dbc.Input(
                            id="user-modal-realname",
                            type="text",
                            placeholder="请输入真实姓名"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("邮箱 *"),
                        dbc.Input(
                            id="user-modal-email",
                            type="email",
                            placeholder="请输入邮箱地址"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("电话"),
                        dbc.Input(
                            id="user-modal-phone",
                            type="tel",
                            placeholder="请输入电话号码"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("部门"),
                        dbc.Input(
                            id="user-modal-department",
                            type="text",
                            placeholder="请输入所属部门"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("职位"),
                        dbc.Input(
                            id="user-modal-position",
                            type="text",
                            placeholder="请输入职位"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("密码 *"),
                        dbc.Input(
                            id="user-modal-password",
                            type="password",
                            placeholder="请输入密码（至少6位）"
                        ),
                        dbc.FormText("编辑时留空表示不修改密码", color="muted")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("确认密码"),
                        dbc.Input(
                            id="user-modal-confirm-password",
                            type="password",
                            placeholder="请再次输入密码"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("用户状态"),
                        dbc.Select(
                            id="user-modal-status",
                            options=[
                                {"label": "激活", "value": "true"},
                                {"label": "禁用", "value": "false"}
                            ],
                            value="true"
                        )
                    ], width=6)
                ]),
                
                # 隐藏字段用于存储编辑时的用户ID
                dcc.Store(id="user-modal-user-id", data=None)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="user-modal-cancel", color="secondary", className="me-2"),
            dbc.Button("保存", id="user-modal-save", color="primary")
        ]),
        html.Div(id="user-modal-alerts")
    ], id="user-modal", size="lg", is_open=False)

def create_role_assignment_modal():
    """创建角色分配模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("分配用户角色")),
        dbc.ModalBody([
            # 用户信息显示
            dbc.Card([
                dbc.CardHeader("选中的用户"),
                dbc.CardBody([
                    html.Div(id="selected-user-info", children="请先选择用户")
                ])
            ], className="mb-3"),
            
            # 角色分配区域
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.H5("角色管理", className="mb-0"),
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "新建角色"],
                            id="create-role-btn",
                            color="success",
                            size="sm"
                        )
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
                ]),
                dbc.CardBody([
                    # 角色选择列表
                    html.Div([
                        dbc.Label("可分配角色："),
                        dbc.Checklist(
                            id="role-assignment-checklist",
                            options=[],
                            value=[],
                            inline=False,
                            style={'maxHeight': '300px', 'overflowY': 'auto'}
                        )
                    ])
                ])
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="role-assignment-cancel", color="secondary", className="me-2"),
            dbc.Button("保存分配", id="role-assignment-save", color="primary")
        ]),
        
        # 存储选中用户的ID
        dcc.Store(id="role-assignment-user-id", data=None)
    ], id="role-assignment-modal", size="lg", is_open=False)

def create_role_modal():
    """创建新建/编辑角色模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="role-modal-title")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("角色名称 *"),
                        dbc.Input(
                            id="role-modal-name",
                            type="text",
                            placeholder="请输入角色名称"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("角色代码 *"),
                        dbc.Input(
                            id="role-modal-code",
                            type="text",
                            placeholder="请输入角色代码"
                        ),
                        dbc.FormText("角色代码必须唯一，建议使用英文", color="muted")
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("角色描述"),
                        dbc.Textarea(
                            id="role-modal-description",
                            placeholder="请输入角色描述",
                            rows=3
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("权限分配"),
                        html.Div([
                            dbc.Checklist(
                                id="role-modal-permissions",
                                options=[],
                                value=[],
                                inline=False,
                                style={'maxHeight': '200px', 'overflowY': 'auto', 'border': '1px solid #ced4da', 'padding': '10px', 'borderRadius': '5px'}
                            )
                        ])
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("角色状态"),
                        dbc.Select(
                            id="role-modal-status",
                            options=[
                                {"label": "激活", "value": "true"},
                                {"label": "禁用", "value": "false"}
                            ],
                            value="true"
                        )
                    ], width=6)
                ]),
                
                # 隐藏字段用于存储编辑时的角色ID
                dcc.Store(id="role-modal-role-id", data=None)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="role-modal-cancel", color="secondary", className="me-2"),
            dbc.Button("保存", id="role-modal-save", color="primary")
        ])
    ], id="role-modal", size="lg", is_open=False)

def create_task_management_content():
    """创建任务管理内容"""
    return html.Div([
        # 添加任务模态框
        create_task_modal(),
        
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("任务管理", className="mb-0", style={'color': PRIMARY_COLOR}),
                    html.Small("管理系统任务和工作流程", className="text-muted")
                ])
            ]),
            dbc.CardBody([
                # 顶部操作栏
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="task-search-input",
                                placeholder="搜索任务名称、类型...",
                                style={'borderRadius': '5px 0 0 5px'}
                            ),
                            dbc.Button(
                                html.I(className="fas fa-search"),
                                id="task-search-btn",
                                color="primary",
                                style={'borderRadius': '0 5px 5px 0'}
                            )
                        ])
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-plus me-2"), "添加任务"],
                                id="task-add-btn",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-edit me-2"), "编辑"],
                                id="task-edit-btn",
                                color="warning",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "更新"],
                                id="task-refresh-btn",
                                color="primary",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "导出"],
                                id="task-export-btn",
                                color="secondary"
                            )
                        ], className="text-end")
                    ], width=8)
                ], className="mb-3"),
                
                # 任务列表表格
                html.Div(id="task-table-container", children=[
                    get_task_datatable()
                ]),
                
                # 操作提示区域
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "操作说明：点击表格中的行来选择任务，然后点击相应的操作按钮。可以通过状态筛选和搜索功能快速找到目标任务。"
                        ], color="info", className="mb-2", style={'fontSize': '14px'})
                    ])
                ]),
                
                # 操作结果提示区域
                html.Div(id="task-alert-area", className="mt-3")
            ])
        ], style={'backgroundColor': CARD_BG})
    ])

def get_task_datatable(tasks_data=None):
    """获取任务数据表格"""
    # 如果没有传入数据，使用默认数据
    if tasks_data is None:
        tasks_data = [
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
            },
            {
                'id': 3,
                'name': '月度报表生成',
                'type': '报表任务',
                'priority': '中',
                'status': '已完成',
                'creator': '报表管理员',
                'created_at': '2024-01-10',
                'due_date': '2024-01-15',
                'progress': '100%',
                'description': '生成月度业务报表'
            }
        ]
    
    return dash_table.DataTable(
        id='tasks-datatable',
        data=tasks_data,
        columns=[
            {"name": "ID", "id": "id", "type": "numeric", "editable": False},
            {"name": "任务名称", "id": "name", "editable": False},
            {"name": "任务类型", "id": "type", "editable": False},
            {"name": "优先级", "id": "priority", "editable": False},
            {"name": "状态", "id": "status", "editable": False},
            {"name": "进度", "id": "progress", "editable": False},
            {"name": "创建人", "id": "creator", "editable": False},
            {"name": "创建时间", "id": "created_at", "editable": False},
            {"name": "截止时间", "id": "due_date", "editable": False},
            {"name": "描述", "id": "description", "editable": False},
        ],
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px',
            'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{status} = 已完成'},
                'backgroundColor': '#d4edda',
            },
            {
                'if': {'filter_query': '{status} = 执行中'},
                'backgroundColor': '#fff3cd',
            },
            {
                'if': {'filter_query': '{status} = 待处理'},
                'backgroundColor': '#f8d7da',
            },
            {
                'if': {'filter_query': '{priority} = 高'},
                'fontWeight': 'bold'
            }
        ],
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_deletable=True,
        tooltip_data=[
            {
                column: {'value': str(row[column]), 'type': 'markdown'}
                for column in ['description']
            } for row in tasks_data
        ],
        tooltip_duration=None
    )

def create_task_modal():
    """创建任务添加/编辑模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="task-modal-title")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("任务名称 *"),
                        dbc.Input(
                            id="task-modal-name",
                            type="text",
                            placeholder="请输入任务名称"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("任务类型 *"),
                        dbc.Select(
                            id="task-modal-type",
                            options=[
                                {"label": "维护任务", "value": "维护任务"},
                                {"label": "审核任务", "value": "审核任务"},
                                {"label": "报表任务", "value": "报表任务"},
                                {"label": "数据处理", "value": "数据处理"},
                                {"label": "系统监控", "value": "系统监控"},
                                {"label": "用户支持", "value": "用户支持"},
                                {"label": "其他", "value": "其他"}
                            ],
                            placeholder="请选择任务类型"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("优先级"),
                        dbc.Select(
                            id="task-modal-priority",
                            options=[
                                {"label": "低", "value": "低"},
                                {"label": "中", "value": "中"},
                                {"label": "高", "value": "高"},
                                {"label": "紧急", "value": "紧急"}
                            ],
                            value="中"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("任务状态"),
                        dbc.Select(
                            id="task-modal-status",
                            options=[
                                {"label": "待处理", "value": "待处理"},
                                {"label": "执行中", "value": "执行中"},
                                {"label": "已暂停", "value": "已暂停"},
                                {"label": "已完成", "value": "已完成"},
                                {"label": "已取消", "value": "已取消"}
                            ],
                            value="待处理"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("截止时间"),
                        dbc.Input(
                            id="task-modal-due-date",
                            type="date",
                            placeholder="请选择截止时间"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("执行进度 (%)"),
                        dbc.Input(
                            id="task-modal-progress",
                            type="number",
                            min=0,
                            max=100,
                            step=5,
                            value=0,
                            placeholder="请输入完成进度"
                        )
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("任务描述"),
                        dbc.Textarea(
                            id="task-modal-description",
                            placeholder="请输入任务描述和相关说明",
                            rows=4
                        )
                    ])
                ], className="mb-3"),
                
                # 隐藏字段用于存储编辑时的任务ID
                dcc.Store(id="task-modal-task-id", data=None)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="task-modal-cancel", color="secondary", className="me-2"),
            dbc.Button("保存", id="task-modal-save", color="primary")
        ])
    ], id="task-modal", size="lg", is_open=False)

def create_log_management_content():
    """创建日志管理内容"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("日志管理", className="mb-0", style={'color': PRIMARY_COLOR})
        ]),
        dbc.CardBody([
            html.P("日志管理功能正在开发中...", className="text-muted text-center py-5")
        ])
    ])


def create_log_management_content():
    """创建日志管理内容"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H4("日志管理", className="mb-0", style={'color': PRIMARY_COLOR}),
                    html.Small("查看和管理系统操作日志", className="text-muted")
                ])
            ]),
            dbc.CardBody([
                # 日志类型选择标签页
                dbc.Tabs([
                    dbc.Tab(label='操作日志', tab_id='operation-logs', label_style={"fontWeight": "bold"}),
                    dbc.Tab(label='登录日志', tab_id='login-logs'),
                ], id="log-tabs", active_tab="operation-logs", className="mb-3"),
                
                # 操作日志内容
                html.Div(id="operation-logs-content", children=[
                    # 顶部操作栏
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id="operation-log-search-input",
                                    placeholder="搜索操作描述、模块...",
                                    style={'borderRadius': '5px 0 0 5px'}
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-search"),
                                    id="operation-log-search-btn",
                                    color="primary",
                                    style={'borderRadius': '0 5px 5px 0'}
                                )
                            ])
                        ], width=4),
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Select(
                                        id="operation-log-level-filter",
                                        options=[
                                            {"label": "所有级别", "value": "all"},
                                            {"label": "调试", "value": "debug"},
                                            {"label": "信息", "value": "info"},
                                            {"label": "警告", "value": "warning"},
                                            {"label": "错误", "value": "error"},
                                            {"label": "严重", "value": "critical"}
                                        ],
                                        value="all",
                                        placeholder="日志级别"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Select(
                                        id="operation-log-module-filter",
                                        options=[
                                            {"label": "所有模块", "value": "all"},
                                            {"label": "用户管理", "value": "user"},
                                            {"label": "权限管理", "value": "permission"},
                                            {"label": "任务管理", "value": "task"},
                                            {"label": "数据管理", "value": "data"},
                                            {"label": "系统管理", "value": "system"},
                                            {"label": "报表管理", "value": "report"}
                                        ],
                                        value="all",
                                        placeholder="所属模块"
                                    )
                                ], width=6)
                            ])
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Button(
                                    [html.I(className="fas fa-sync-alt me-2"), "刷新"],
                                    id="operation-log-refresh-btn",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-download me-2"), "导出"],
                                    id="operation-log-export-btn",
                                    color="secondary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-trash me-2"), "清理"],
                                    id="operation-log-clear-btn",
                                    color="danger"
                                )
                            ], className="text-end")
                        ], width=4)
                    ], className="mb-3"),
                    
                    # 操作日志表格
                    html.Div(id="operation-log-table-container", children=[
                        get_operation_log_datatable()
                    ]),
                    
                    # 操作结果提示区域
                    html.Div(id="operation-log-alert-area", className="mt-3")
                ], style={"display": "block"}),
                
                # 登录日志内容
                html.Div(id="login-logs-content", children=[
                    # 顶部操作栏
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id="login-log-search-input",
                                    placeholder="搜索用户名、IP地址...",
                                    style={'borderRadius': '5px 0 0 5px'}
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-search"),
                                    id="login-log-search-btn",
                                    color="info",
                                    style={'borderRadius': '0 5px 5px 0'}
                                )
                            ])
                        ], width=4),
                        dbc.Col([
                            dbc.Select(
                                id="login-log-status-filter",
                                options=[
                                    {"label": "所有状态", "value": "all"},
                                    {"label": "成功", "value": "success"},
                                    {"label": "失败", "value": "failed"}
                                ],
                                value="all",
                                placeholder="登录状态"
                            )
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Button(
                                    [html.I(className="fas fa-sync-alt me-2"), "刷新"],
                                    id="login-log-refresh-btn",
                                    color="info",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-download me-2"), "导出"],
                                    id="login-log-export-btn",
                                    color="secondary"
                                )
                            ], className="text-end")
                        ], width=4)
                    ], className="mb-3"),
                    
                    # 登录日志表格
                    html.Div(id="login-log-table-container", children=[
                        get_login_log_datatable()
                    ]),
                    
                    # 操作结果提示区域
                    html.Div(id="login-log-alert-area", className="mt-3")
                ], style={"display": "none"}),
                
                # 操作提示区域
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "日志说明：系统自动记录用户操作和登录行为，支持按时间、级别、模块等条件进行筛选和查询。"
                        ], color="info", className="mb-2", style={'fontSize': '14px'})
                    ])
                ])
            ])
        ], style={'backgroundColor': CARD_BG})
    ])

def get_operation_log_datatable(logs_data=None):
    """获取操作日志数据表格"""
    if logs_data is None:
        logs_data = []
    
    return dash_table.DataTable(
        id='operation-logs-datatable',
        data=logs_data,
        columns=[
            {"name": "ID", "id": "id", "type": "numeric", "editable": False},
            {"name": "日志名称", "id": "operation_desc", "editable": False},
            {"name": "用户名称", "id": "username", "editable": False},
            {"name": "服务名称", "id": "module", "editable": False},
            {"name": "方法名", "id": "operation_type", "editable": False},
            {"name": "时间", "id": "created_at", "editable": False},
            {"name": "级别", "id": "level", "editable": False},
            {"name": "状态", "id": "status", "editable": False},
            {"name": "IP地址", "id": "ip_address", "editable": False},
            {"name": "具体信息", "id": "target_info", "editable": False},
        ],
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px',
            'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{level} = error'},
                'backgroundColor': '#f8d7da',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{level} = warning'},
                'backgroundColor': '#fff3cd',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{level} = critical'},
                'backgroundColor': '#f5c6cb',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{status} = success'},
                'color': '#28a745',
            },
            {
                'if': {'filter_query': '{status} = failed'},
                'color': '#dc3545',
            }
        ],
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_deletable=False,  # 日志不允许删除
        tooltip_data=[
            {
                column: {'value': str(row[column]), 'type': 'markdown'}
                for column in ['operation_desc', 'target_info']
            } for row in logs_data
        ],
        tooltip_duration=None
    )

def get_login_log_datatable(logs_data=None):
    """获取登录日志数据表格"""
    if logs_data is None:
        logs_data = []
    
    return dash_table.DataTable(
        id='login-logs-datatable',
        data=logs_data,
        columns=[
            {"name": "ID", "id": "id", "type": "numeric", "editable": False},
            {"name": "日志名称", "id": "operation_desc", "editable": False},
            {"name": "用户名称", "id": "username", "editable": False},
            {"name": "登录方式", "id": "operation_type", "editable": False},
            {"name": "时间", "id": "created_at", "editable": False},
            {"name": "IP地址", "id": "ip_address", "editable": False},
            {"name": "状态", "id": "status", "editable": False},
            {"name": "用户代理", "id": "user_agent", "editable": False},
            {"name": "具体信息", "id": "target_info", "editable": False},
        ],
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px',
            'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{status} = success'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{status} = failed'},
                'backgroundColor': '#f8d7da',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{operation_type} = LOGIN'},
                'fontWeight': 'bold'
            }
        ],
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_deletable=False,  # 日志不允许删除
        tooltip_data=[
            {
                column: {'value': str(row[column]), 'type': 'markdown'}
                for column in ['user_agent', 'target_info']
            } for row in logs_data
        ],
        tooltip_duration=None
    )