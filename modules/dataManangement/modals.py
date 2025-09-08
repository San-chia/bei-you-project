# modules/data/modals.py
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import plotly.graph_objects as go  # 添加这一行导入
import time
from datetime import datetime

from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG, THEME, FONT_AWESOME_URL

def create_import_modal():
    """创建导入数据模态窗口"""
    return  dbc.Modal(
    [
        dbc.ModalHeader([
            html.Span("导入数据", style={'fontSize': '18px', 'fontWeight': 'bold'}),
            html.Button(
                html.I(className="fas fa-times"),
                id="close-import-x",
                style={
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'float': 'right',
                    'fontSize': '20px',
                    'cursor': 'pointer'
                }
            )
        ], style={'borderBottom': '1px solid #eee', 'padding': '15px 20px'}),
        
        dbc.ModalBody([
            # 文件上传区域
            html.Div([
                dcc.Upload(
                    id="upload-data",
                    children=html.Div([
                        # 垂直布局容器
                        html.Div([
                            # 上传图标
                            html.I(className="fas fa-upload", 
                                style={'fontSize': '40px', 'color': '#ccc', 'marginBottom': '15px'}),
                            
                            # 文字提示
                            html.Div([
                                html.Span("点击上传", style={'color': '#3498db', 'cursor': 'pointer'}),
                                html.Span(" 或将文件拖拽到此处", style={'color': '#666'})
                            ]),
                            
                            # 支持格式说明
                            html.Div(
                                html.Span("支持 Excel、CSV、PDF 格式文件", 
                                        style={'color': '#666', 'fontSize': '12px', 'marginTop': '5px'})
                            )
                        ], style={
                            'display': 'flex',
                            'flexDirection': 'column',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'height': '100%'
                        })
                    ], style={
                        'width': '100%',
                        'height': '150px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'borderColor': '#ccc',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    }),
                    multiple=False,
                    style={
                        'width': '100%',
                        'marginBottom': '20px'
                    }
                ),
                
                # 数据导入方式选择区域
                html.Div([
                    # 材料数据下拉菜单
                    html.Div([
                        dbc.DropdownMenu(
                            label="材料数据",
                            id="material-data-dropdown",
                            children=[
                                dbc.DropdownMenuItem("建筑材料"),
                                dbc.DropdownMenuItem("钢材"),
                                dbc.DropdownMenuItem("混凝土"),
                                dbc.DropdownMenuItem("木材")
                            ],
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'border': '1px solid #ccc',
                                'borderRadius': '4px'
                            }
                        )
                    ], style={'width': '48%'}),
                    
                    # 追加数据下拉菜单
                    html.Div([
                        dbc.DropdownMenu(
                            label="追加数据",
                            id="append-data-dropdown",
                            children=[
                                dbc.DropdownMenuItem("替换现有数据"),
                                dbc.DropdownMenuItem("追加到现有数据"),
                                dbc.DropdownMenuItem("只更新匹配记录")
                            ],
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'border': '1px solid #ccc',
                                'borderRadius': '4px'
                            }
                        )
                    ], style={'width': '48%'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'marginBottom': '20px'
                }),
                
            # 数据库表操作选择区域
            html.Div([
                html.Label("数据导入方式：", style={'marginBottom': '5px', 'fontWeight': 'bold'}),
                dcc.RadioItems(
                    id="table-operation-type",
                    options=[
                        {'label': '创建新表', 'value': 'new_table'},
                        {'label': '添加到现有表', 'value': 'existing_table'}
                    ],
                    value='new_table',
                    labelStyle={'marginRight': '15px'}
                ),
                
                # 新表名称输入框（当选择创建新表时显示）
                html.Div(
                    [
                        html.Label("新表名称：", style={'marginBottom': '5px'}),
                        dbc.Input(
                            id="new-table-name",
                            type="text",
                            placeholder="请输入新表名称",
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ],
                    id="new-table-div",
                    style={'display': 'block', 'marginTop': '10px'}
                ),
                
                # 现有表选择（当选择添加到现有表时显示）
                html.Div(
                    [
                        html.Label("选择现有表：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="existing-table-dropdown",
                            options=[
                                {'label': '材料成本表', 'value': 'material_cost'},
                                {'label': '人工成本表', 'value': 'labor_cost'},
                                {'label': '设备成本表', 'value': 'equipment_cost'},
                                {'label': '综合指标表', 'value': 'comprehensive_indicators'}
                            ],
                            placeholder="请选择表",
                            style={'width': '100%', 'marginBottom': '10px'}
                        ),
                        
                        # 数据导入模式选择
                        html.Label("数据导入模式：", style={'marginBottom': '5px'}),
                        dcc.RadioItems(
                            id="import-mode",
                            options=[
                                {'label': '追加数据', 'value': 'append'},
                                {'label': '替换数据', 'value': 'replace'},
                                {'label': '更新匹配记录', 'value': 'update'}
                            ],
                            value='append',
                            labelStyle={'marginRight': '15px'}
                        ),
                    ],
                    id="existing-table-div",
                    style={'display': 'none', 'marginTop': '10px'}
                )
            ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}), 
                

                # 在字段映射表格之前添加日期选择部分
                html.Div([
                    html.Label("数据时间：", style={'marginBottom': '5px', 'fontWeight': 'bold'}),
                    html.Div([
                        # 当前日期显示
                        html.Div([
                            html.Label("当前日期:", style={'marginBottom': '5px'}),
                            html.Div(
                                id="current-date-display",
                                children=datetime.now().strftime("%Y-%m-%d"),
                                style={
                                    'padding': '6px 12px',
                                    'border': '1px solid #ccc',
                                    'borderRadius': '4px',
                                    'backgroundColor': '#f9f9f9'
                                }
                            )
                        ], style={'width': '48%'}),
                        
                        # 手动选择日期
                        html.Div([
                            html.Label("修改数据日期:", style={'marginBottom': '5px'}),
                            dcc.DatePickerSingle(
                                id='manual-date-picker',
                                date=datetime.now().date(),
                                display_format='YYYY-MM-DD',
                                style={'width': '100%'}
                            )
                        ], style={'width': '48%'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})
                ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),    
                # 字段映射表格
                html.Div([
                    html.Table([
                        # 表头
                        html.Thead(
                            html.Tr([
                                html.Th("字段名", style={'padding': '10px', 'textAlign': 'center', 'fontWeight': 'bold', 'borderBottom': '1px solid #ddd', 'width': '25%'}),
                                html.Th("类型", style={'padding': '10px', 'textAlign': 'center', 'fontWeight': 'bold', 'borderBottom': '1px solid #ddd', 'width': '25%'}),
                                html.Th("示例值", style={'padding': '10px', 'textAlign': 'center', 'fontWeight': 'bold', 'borderBottom': '1px solid #ddd', 'width': '25%'}),
                                html.Th("映射字段", style={'padding': '10px', 'textAlign': 'center', 'fontWeight': 'bold', 'borderBottom': '1px solid #ddd', 'width': '25%'})
                            ])
                        ),
                        
                        # 表身体
                        html.Tbody(id="field-mapping-table-body", children=[
                            html.Tr([
                                html.Td("Material_name", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                                html.Td("文本", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                                html.Td("钢筋", style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'}),
                                html.Td([
                                    dcc.Dropdown(
                                        id='field-mapping-dropdown-1',
                                        options=[
                                            {'label': '材料', 'value': 'material'},
                                            {'label': '规格', 'value': 'specification'},
                                            {'label': '型号', 'value': 'model'}
                                        ],
                                        value='material',
                                        clearable=False,
                                        style={'width': '100%'}
                                    )
                                ], style={'padding': '10px', 'textAlign': 'center', 'borderBottom': '1px solid #eee'})
                            ])
                        ])
                    ], style={
                        'width': '100%',
                        'borderCollapse': 'collapse',
                        'marginBottom': '20px'
                    })
                ], style={
                    'overflowX': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '4px',
                    'marginBottom': '20px'
                }),
                
                # 上传的文件数据表格 (预览)
                html.Div(
                    id="preview-data-container",
                    style={
                        'marginTop': '20px',
                        'display': 'none'  # 初始隐藏，直到上传文件
                    },
                    children=[
                        html.H6("数据预览", style={'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id="preview-table-data",
                            page_size=5,
                            style_table={
                                'overflowX': 'auto'
                            },
                            style_cell={
                                'textAlign': 'left',
                                'padding': '8px'
                            },
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold'
                            }
                        )
                    ]
                )
            ])
        ]),
        # 在ModalBody和ModalFooter之间添加状态消息区域
        html.Div(
            id="import-status-message",
            children="",
            style={
                'padding': '10px',
                'marginTop': '10px',
                'borderRadius': '4px',
                'backgroundColor': '#f8f9fa',
                'display': 'none'  # 初始隐藏
            }
        ),
        dbc.ModalFooter([
            dbc.Button("取消", id="close-import", className="mr-2", color="secondary"),
            dbc.Button("导入", id="confirm-import", color="primary")
        ], style={'borderTop': '1px solid #eee', 'padding': '15px'})
    ],
    id="modal-import",
    is_open=False,
    size="lg",
    style={'maxWidth': '800px'}
)

def create_basic_indicator_modal():
    """创建基础指标库模态窗口"""
    return dbc.Modal([
        dbc.ModalHeader("基础指标库管理"),
        dbc.ModalBody([
            # 指标筛选和搜索区域
            html.Div([
                html.Label("指标筛选：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div([
                    # 分类选择
                    html.Div([
                        html.Label("指标分类：", style={'marginBottom': '5px'}),
                        html.Div([
                            dcc.Dropdown(
                                id="basic-indicator-main-category-dropdown",
                                options=[],  # 初始为空，通过回调动态加载
                                value='custom',
                                clearable=False,
                                style={'width': '70%', 'marginRight': '5px'},
                                disabled=False
                            ),
                            dbc.Button([
                                html.I(className="fas fa-plus", style={'fontSize': '12px'})
                            ], 
                            id="add-new-category-btn", 
                            color="success", 
                            size="sm",
                            style={'width': '12%', 'padding': '6px', 'marginRight': '5px'}
                            ),
                            dbc.Button([
                                html.I(className="fas fa-minus", style={'fontSize': '12px'})
                            ], 
                            id="delete-category-btn", 
                            color="danger", 
                            size="sm",
                            style={'width': '12%', 'padding': '6px'}
                            )
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        
                        # 添加分类模式的输入框（初始隐藏）
                        html.Div([
                            dcc.Input(
                                id="new-category-name-input",
                                type="text",
                                placeholder="请输入新分类名称",
                                style={'width': '60%', 'marginRight': '5px'}
                            ),
                            dbc.Button("确认", id="confirm-add-category", color="primary", size="sm", style={'marginRight': '5px'}),
                            dbc.Button("取消", id="cancel-add-category", color="secondary", size="sm")
                        ], id="add-category-input-div", style={'display': 'none', 'marginTop': '5px'}),
                        
                        # 删除分类模式的下拉菜单（初始隐藏）
                        html.Div([
                            html.Label("选择要删除的分类：", style={'marginBottom': '5px', 'color': '#dc3545', 'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id="delete-category-dropdown",
                                options=[],
                                placeholder="请选择要删除的分类",
                                style={'width': '60%', 'marginRight': '5px'}
                            ),
                            dbc.Button("确认删除", id="confirm-delete-category", color="danger", size="sm", style={'marginRight': '5px'}),
                            dbc.Button("取消", id="cancel-delete-category", color="secondary", size="sm"),
                            html.Div([
                                dbc.Alert([
                                    html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                                    "警告：删除分类将删除该分类下的所有指标，且不可恢复！"
                                ], color="warning", style={'marginTop': '10px', 'fontSize': '12px'})
                            ])
                        ], id="delete-category-input-div", style={'display': 'none', 'marginTop': '5px'})
                    ], style={'width': '22%'}),
                    
                    # 状态筛选
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px', 'display': 'block'}),
                        dcc.Dropdown(
                            id="basic-indicator-status-dropdown",
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '48%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between'}),
                
                # 搜索框
                html.Div([
                    dbc.InputGroup([
                        dbc.Input(id="basic-indicator-search", placeholder="搜索指标名称或代码..."),
                        dbc.Button([html.I(className="fas fa-search")], id="basic-indicator-search-btn"),
                    ], style={'marginBottom': '20px'})
                ])
            ]),
            # 在表格前面添加这个区域
            html.Div([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                        "编辑所选"
                    ], id="edit-selected-indicator", color="primary", size="sm", 
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-trash", style={'marginRight': '5px'}),
                        "删除所选"
                    ], id="delete-selected-indicator", color="danger", size="sm",
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '5px'}),
                        "新增指标"
                    ], id="add-new-indicator", color="success", size="sm")
                ], style={'textAlign': 'right'})
            ], style={'marginBottom': '15px'}),            
            # 指标列表表格
            html.Div([
                dash_table.DataTable(
                    id='basic-indicator-table',
                    columns=[
                        {'name': '指标代码', 'id': 'code', 'editable': False},
                        {'name': '指标名称', 'id': 'name', 'editable': False},
                        {'name': '分类', 'id': 'category', 'editable': False, 'presentation': 'dropdown'},
                        {'name': '单位', 'id': 'unit', 'editable': False},
                        {'name': '说明', 'id': 'description', 'editable': False},
                        {'name': '状态', 'id': 'status', 'editable': False, 'presentation': 'dropdown'},
                        
                    ],
                    data=[],
                    editable=False,# 改为不可编辑，通过按钮操作
                    row_selectable='single',
                    selected_rows=[],# 初始无选中
                    dropdown={
                        'category': {
                            'options': [
                                {'label': '机械费', 'value': '机械费'},
                                {'label': '材料费', 'value': '材料费'},
                                {'label': '措施费', 'value': '措施费'}
                            ]
                        },
                        'status': {
                            'options': [
                                {'label': '启用', 'value': '启用'},
                                {'label': '停用', 'value': '停用'}
                            ]
                        }
                    },
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        },

                    ],
                    page_size=6,
                    style_table={'overflowX': 'auto'}
                )
            ], style={'marginBottom': '20px'}),
            # 状态管理组件（隐藏）
            html.Div([
                dcc.Store(id="editing-mode", data=False),  # 是否处于编辑模式
                dcc.Store(id="editing-indicator-id", data=None),  # 正在编辑的指标ID
                dcc.Store(id="original-indicator-data", data={})  # 原始数据（用于取消编辑）
            ], style={'display': 'none'}),

            # 编辑状态提示区域
            html.Div(
                id="editing-status-alert",
                children=[],
                style={'marginBottom': '15px', 'display': 'none'}
            ),
            # 新增指标表单
            html.Div([
                html.H6(id="form-title", children="新增基础指标", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                
                # 表单第一行 - 修改为四列布局
                html.Div([
                    # 指标分类（新添加）
                    html.Div([
                        html.Label("指标分类：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="basic-indicator-form-category-dropdown",  # 改为新的ID
                            options=[],  # 也改为空，让回调函数动态加载
                            value='custom',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '22%'}),
                                        
                    # 指标代码
                    html.Div([
                        html.Label("指标代码：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="basic-indicator-code-input",
                            type="text",
                            placeholder="请输入指标代码",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '22%'}),
                    
                    # 指标名称
                    html.Div([
                        html.Label("指标名称：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="basic-indicator-name-input",
                            type="text",
                            placeholder="请输入指标名称",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '30%'}),
                    
                    # 单位
                    html.Div([
                        html.Label("单位：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="basic-indicator-unit-input",
                            type="text",
                            placeholder="请输入单位",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '22%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),

                html.Div([
                    html.Small("不同分类对应不同ID范围，用于上方筛选功能", 
                            style={'color': '#666', 'fontStyle': 'italic'})
                ], style={'marginBottom': '10px'}),
                
                # 表单第二行
                html.Div([
                    # 分类
                    html.Div([
                        html.Label("分类：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="basic-indicator-category-dropdown-input",
                            options=[
                                {'label': '机械费', 'value': '机械费'},
                                {'label': '材料费', 'value': '材料费'},
                                {'label': '措施费', 'value': '措施费'},
                                {'label': '人工费', 'value': '人工费'},
                                {'label': '其他费用', 'value': '其他费用'}
                            ],
                            value='机械费',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '40%'}),
                    
                    # 状态
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px'}),
                        dcc.RadioItems(
                            id="basic-indicator-status-radio",
                            options=[
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='enabled',
                            inline=True
                        )
                    ], style={'width': '55%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
                
                    # 说明
                    html.Div([
                        html.Label("说明：", style={'marginBottom': '5px'}),
                        dcc.Textarea(
                            id="basic-indicator-description-textarea",
                            placeholder="请输入指标说明...",
                            style={'width': '100%', 'height': '80px', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ])
            ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'})
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="close-basic-indicator", color="secondary", className="ml-auto", style={'marginRight': '10px'}),
            #dbc.Button("重置", id="reset-basic-indicator", color="info", style={'marginRight': '10px'}),
            dbc.Button("取消编辑", id="cancel-edit-indicator", color="warning", style={'marginRight': '10px', 'display': 'none'}),
            dbc.Button("保存指标", id="save-basic-indicator", color="primary")
        ])
    ], id="modal-basic-indicator", is_open=False, size="xl", style={'maxWidth': '95%', 'width': '95%'})

def import_choice_modal ():
    return dbc.Modal(
    [
        dbc.ModalHeader([
            html.Span("选择导入方式", style={'fontSize': '18px', 'fontWeight': 'bold'}),
            html.Button(
                html.I(className="fas fa-times"),
                id="close-import-choice-x",
                style={
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'float': 'right',
                    'fontSize': '20px',
                    'cursor': 'pointer'
                }
            )
        ], style={'borderBottom': '1px solid #eee', 'padding': '15px 20px'}),
        
        dbc.ModalBody([
            html.Div([
                html.H5("请选择导入方式", style={"marginBottom": "20px", "textAlign": "center"}),
                
                # 选项卡片
                dbc.Row([
                    # 仅预览选项
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-eye", style={'fontSize': '32px', 'color': PRIMARY_COLOR, 'marginBottom': '15px'}),
                                    html.H5("仅上传数据", className="card-title"),
                                    html.P("上传数据内容而不进行数据库操作。上传后，数据将不会保存到数据库中。", 
                                        className="card-text", style={'color': '#666', 'fontSize': '14px'}),
                                    dbc.Button("选择此选项", id="preview-only-btn", color="light", className="mt-3")  # 添加按钮
                                ], style={'textAlign': 'center'})
                            ])
                        ], id="preview-only-card", className="h-100", style={
                            'cursor': 'pointer',
                            'border': '2px solid #ddd',
                            'transition': 'all 0.3s ease'
                        })
                    ], width=12, md=6, className="mb-4 mb-md-0"),

                    # 导入数据库选项
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-database", style={'fontSize': '32px', 'color': SECONDARY_COLOR, 'marginBottom': '15px'}),
                                    html.H5("导入到数据库", className="card-title"),
                                    html.P("将数据导入到数据库中。您需要配置导入选项，包括表名和导入模式。", 
                                        className="card-text", style={'color': '#666', 'fontSize': '14px'}),
                                    dbc.Button("选择此选项", id="import-to-db-btn", color="light", className="mt-3")  # 添加按钮
                                ], style={'textAlign': 'center'})
                            ])
                        ], id="import-to-db-card", className="h-100", style={
                            'cursor': 'pointer',
                            'border': '2px solid #ddd',
                            'transition': 'all 0.3s ease'
                        })
                    ], width=12, md=6)
                ], className="mb-4"),
                
                # 隐藏的选择值
                dcc.Store(id="import-choice-value", data=""),
                
                # 说明文字
                html.Div(id="import-choice-description", 
                        children="请点击上方选项卡片进行选择",
                        style={'textAlign': 'center', 'marginTop': '20px', 'color': '#666'})
            ])
        ]),
        
        dbc.ModalFooter([
            dbc.Button("取消", id="close-import-choice", className="mr-2", color="secondary"),
            dbc.Button("继续", id="confirm-import-choice", color="primary", disabled=True)
        ], style={'borderTop': '1px solid #eee', 'padding': '15px'})
    ],
    id="modal-import-choice",
    is_open=False,
    size="md",
    style={'maxWidth': '600px'}
)

# 其他模态窗口函数...
def create_composite_indicator_modal():
    """创建复合指标库模态窗口 - 重新设计版本"""
    return dbc.Modal([
        dbc.ModalHeader("复合指标库管理"),
        dbc.ModalBody([
            # 指标筛选和搜索区域
            html.Div([
                html.Label("指标筛选：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div([
                    # 施工模式选择
                    html.Div([
                        html.Label("施工模式：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="composite-construction-mode-dropdown",
                            options=[
                                {'label': '全部模式', 'value': 'all'},
                                {'label': '钢筋笼模式', 'value': 'steel_cage'},
                                {'label': '钢衬里模式', 'value': 'steel_lining'}
                                
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '32%'}),
                    
                    # 状态筛选
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="composite-status-dropdown",
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '32%'}),
                    
                    # 搜索框
                    html.Div([
                        html.Label("搜索：", style={'marginBottom': '5px'}),
                        dbc.InputGroup([
                            dbc.Input(id="composite-search", placeholder="指标名称或代码"),
                            dbc.Button([html.I(className="fas fa-search")], id="composite-search-btn"),
                        ])
                    ], style={'width': '32%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})
            ]),
            
            # 操作按钮区域
            html.Div([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                        "编辑所选"
                    ], id="edit-selected-composite", color="primary", size="sm", 
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-trash", style={'marginRight': '5px'}),
                        "删除所选"
                    ], id="delete-selected-composite", color="danger", size="sm",
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '5px'}),
                        "新增指标"
                    ], id="add-new-composite", color="success", size="sm")
                ], style={'textAlign': 'right'})
            ], style={'marginBottom': '15px'}),
            
            # 两列布局：左侧表格，右侧详情
            html.Div([
                # 左侧 - 复合指标列表
                html.Div([
                    html.H6("复合指标列表", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='composite-indicator-table',
                        columns=[
                            {'name': '指标代码', 'id': 'code'},
                            {'name': '指标名称', 'id': 'name'},
                            {'name': '施工模式', 'id': 'construction_mode'},
                            {'name': '单位', 'id': 'unit'},
                            {'name': '状态', 'id': 'status'}
                        ],
                        data=[],
                        style_cell={'textAlign': 'center', 'padding': '10px'},
                        style_header={
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f9f9f9'
                            }
                        ],
                        page_size=6,
                        row_selectable='single',
                        selected_rows=[]
                    )
                ], style={'width': '48%'}),
                
                # 右侧 - 指标详情和公式展示
                html.Div([
                    html.H6("指标详情与计算公式", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    html.Div([
                        # 基本信息展示
                        html.Div([
                            html.Div([
                                html.Label("指标名称：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                                html.Span(id="composite-detail-name", children="请选择指标", style={'display': 'inline-block'})
                            ], style={'marginBottom': '8px'}),
                            
                            html.Div([
                                html.Label("指标代码：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                                html.Span(id="composite-detail-code", children="-", style={'display': 'inline-block'})
                            ], style={'marginBottom': '8px'}),
                            
                            html.Div([
                                html.Label("施工模式：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                                html.Span(id="composite-detail-mode", children="-", style={'display': 'inline-block'})
                            ], style={'marginBottom': '8px'}),
                            
                            html.Div([
                                html.Label("计算类型：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                                html.Span(id="composite-detail-calc-type", children="-", style={'display': 'inline-block'})
                            ], style={'marginBottom': '10px'})
                        ]),
                        
                        # 计算公式展示
                        html.Div([
                            html.Label("计算公式：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                            html.Div(
                                id="composite-detail-formula",
                                children="请选择指标查看公式",
                                style={
                                    'padding': '10px',
                                    'border': '1px solid #ddd',
                                    'borderRadius': '4px',
                                    'backgroundColor': '#f9f9f9',
                                    'fontFamily': 'monospace',
                                    'minHeight': '40px',
                                    'marginBottom': '15px'
                                }
                            )
                        ]),
                        
                        # 依赖关系展示
                        html.Div([
                            html.Label("依赖关系：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                            dash_table.DataTable(
                                id='composite-dependencies-table',
                                columns=[
                                    {'name': '类型', 'id': 'type'},
                                    {'name': '代码', 'id': 'code'},
                                    {'name': '名称', 'id': 'name'},
                                    {'name': '系数', 'id': 'coefficient'}
                                ],
                                data=[],
                                style_cell={'textAlign': 'center', 'padding': '8px'},
                                style_header={
                                    'backgroundColor': '#f8f9fa',
                                    'fontWeight': 'bold'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f9f9f9'
                                    }
                                ],
                                page_size=4
                            )
                        ])
                    ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'height': '100%'})
                ], style={'width': '48%'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
            
            # 状态管理组件（隐藏）
            html.Div([
                dcc.Store(id="composite-editing-mode", data=False),
                dcc.Store(id="composite-editing-indicator-id", data=None),
                dcc.Store(id="composite-original-indicator-data", data={})
            ], style={'display': 'none'}),

            # 编辑状态提示区域
            html.Div(
                id="composite-editing-status-alert",
                children=[],
                style={'marginBottom': '15px', 'display': 'none'}
            ),
            
            # 新增/编辑复合指标表单
            html.Div([
                html.H6(id="composite-form-title", children="新增复合指标", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                
                # 表单第一行 - 基本信息（3列）
                html.Div([
                    # 施工模式
                    html.Div([
                        html.Label("施工模式：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="composite-form-construction-mode",
                            options=[
                                {'label': '钢筋笼模式', 'value': 'steel_cage'},
                                {'label': '钢衬里模式', 'value': 'steel_lining'}
                                
                            ],
                            value='steel_cage',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '30%'}),
                    
                    # 指标代码
                    html.Div([
                        html.Label("指标代码：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="composite-code-input",
                            type="text",
                            placeholder="如: FU-GJL-TDCB",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '30%'}),
                    
                    # 指标名称
                    html.Div([
                        html.Label("指标名称：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="composite-name-input",
                            type="text",
                            placeholder="如: 成本_塔吊租赁",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '35%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
                
                # 表单第二行 - 单位、计算类型、状态（3列）
                html.Div([
                    # 单位
                    html.Div([
                        html.Label("单位：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="composite-unit-input",
                            type="text",
                            placeholder="如: 元",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '30%'}),
                    
                    # 计算类型
                    html.Div([
                        html.Label("计算类型：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="composite-calculation-type",
                            options=[
                                {'label': '求和 (A+B+C)', 'value': 'sum'},
                                {'label': '乘积 (A×B×C)', 'value': 'product'},
                                {'label': '加权求和', 'value': 'weighted_sum'},
                                {'label': '自定义公式', 'value': 'custom'}
                            ],
                            value='custom',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '35%'}),
                    
                    # 状态
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px'}),
                        dcc.RadioItems(
                            id="composite-status-radio",
                            options=[
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='enabled',
                            inline=True
                        )
                    ], style={'width': '30%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
                
                # 计算公式输入
                html.Div([
                    html.Label("计算公式：", style={'marginBottom': '5px'}),
                    dcc.Textarea(
                        id="composite-formula-input",
                        placeholder="请输入计算公式，如: QTY_塔吊 * {GJL-JI-01}\n支持的格式：\n- 基础指标引用: {GJL-JI-01}\n- 输入参数: QTY_塔吊\n- 复合指标引用: {FU-GJL-TDCB}",
                        style={'width': '100%', 'height': '80px', 'padding': '8px', 'marginBottom': '10px'}
                    )
                ]),
                
                # 说明
                html.Div([
                    html.Label("说明：", style={'marginBottom': '5px'}),
                    dcc.Textarea(
                        id="composite-description-input",
                        placeholder="请输入指标说明...",
                        style={'width': '100%', 'height': '60px', 'padding': '8px', 'marginBottom': '10px'}
                    )
                ])
            ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'})
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="close-composite-indicator", color="secondary", className="ml-auto", style={'marginRight': '10px'}),
            dbc.Button("取消编辑", id="cancel-edit-composite", color="warning", style={'marginRight': '10px', 'display': 'none'}),
            dbc.Button("保存指标", id="save-composite-indicator", color="primary")
        ])
    ], id="modal-composite-indicator", is_open=False, size="xl", style={'maxWidth': '95%', 'width': '95%'})

def create_comprehensive_indicator_modal():
    """创建综合指标库模态窗口 - 完整修复版本"""
    return dbc.Modal([
        dbc.ModalHeader("综合指标库管理"),
        dbc.ModalBody([
            # 指标筛选区域
            html.Div([
                html.Label("指标筛选：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Div([
                    # 施工模式筛选
                    html.Div([
                        html.Label("施工模式：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-construction-mode-dropdown",
                            options=[
                                {'label': '全部模式', 'value': 'all'},
                                {'label': '钢筋笼模式', 'value': 'steel_cage'},
                                {'label': '钢衬里模式', 'value': 'steel_lining'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 计算方法筛选
                    html.Div([
                        html.Label("计算方法：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-calculation-method-dropdown",
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': 'AI预测', 'value': 'ml_prediction'},
                                {'label': '比率法', 'value': 'ratio_method'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 指标类型筛选
                    html.Div([
                        html.Label("指标类型：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-indicator-type-dropdown",
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': '原始值', 'value': 'raw_value'},
                                {'label': '最终值', 'value': 'final_value'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 状态筛选
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-status-dropdown",
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})
            ]),
            
            # 操作按钮区域
            html.Div([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                        "编辑所选"
                    ], id="edit-selected-comprehensive", color="primary", size="sm", 
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-trash", style={'marginRight': '5px'}),
                        "删除所选"
                    ], id="delete-selected-comprehensive", color="danger", size="sm",
                    style={'marginRight': '10px'}, disabled=True),
                    
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '5px'}),
                        "新增指标"
                    ], id="add-new-comprehensive", color="success", size="sm")
                ], style={'textAlign': 'right'})
            ], style={'marginBottom': '15px'}),
            
            # 综合指标表格
            html.Div([
                dash_table.DataTable(
                    id='comprehensive-indicator-table',
                    columns=[
                        {'name': '指标编码', 'id': 'code'},
                        {'name': '指标名称', 'id': 'name'},
                        {'name': '施工模式', 'id': 'construction_mode'},
                        {'name': '计算方法', 'id': 'calculation_method'},
                        {'name': '指标类型', 'id': 'indicator_type'},
                        {'name': '状态', 'id': 'status'}
                    ],
                    data=[],
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ],
                    page_size=5,
                    row_selectable='single',
                    selected_rows=[]
                )
            ], style={'marginBottom': '20px'}),

            # 指标详情区域
            html.Div([
                html.H6("指标详情", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                
                # 指标基本信息
                html.Div([
                    # 左侧 - 基本属性
                    html.Div([
                        html.Div([
                            html.Label("指标名称：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-name", children="请选择指标", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("指标编码：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-code", children="-", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("施工模式：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-mode", children="-", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("计算方法：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-method", children="-", style={'display': 'inline-block'})
                        ])
                    ], style={'width': '48%'}),
                    
                    # 右侧 - 附加属性和说明
                    html.Div([
                        html.Div([
                            html.Label("指标类型：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-type", children="-", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("单位：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-unit", children="-", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("数据日期：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span("2025年1月", style={'display': 'inline-block'})
                        ], style={'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Label("状态：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': '100px'}),
                            html.Span(id="comprehensive-detail-status", children="-", style={'display': 'inline-block', 'color': 'green'})
                        ])
                    ], style={'width': '48%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'})
            ]),
            
            # 计算逻辑显示区域
            html.Div([
                html.Label("计算逻辑：", style={'fontWeight': 'bold', 'marginBottom': '5px', 'marginTop': '15px'}),
                html.Div(
                    id="comprehensive-detail-logic",
                    children="请选择指标查看计算逻辑",
                    style={
                        'padding': '10px',
                        'border': '1px solid #ddd',
                        'borderRadius': '4px',
                        'backgroundColor': '#f9f9f9',
                        'fontFamily': 'monospace',
                        'minHeight': '60px',
                        'whiteSpace': 'pre-wrap'
                    }
                )
            ]),
            
            # 依赖关系表格
            html.Div([
                html.Label("依赖关系：", style={'fontWeight': 'bold', 'marginBottom': '5px', 'marginTop': '15px'}),
                dash_table.DataTable(
                    id='comprehensive-dependencies-table',
                    columns=[
                        {'name': '类型', 'id': 'type'},
                        {'name': '引用', 'id': 'reference'},
                        {'name': '说明', 'id': 'description'}
                    ],
                    data=[],
                    style_cell={'textAlign': 'center', 'padding': '8px'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ],
                    page_size=3
                )
            ]),
            
            # 状态管理组件（隐藏）
            html.Div([
                dcc.Store(id="comprehensive-editing-mode", data=False),
                dcc.Store(id="comprehensive-editing-indicator-id", data=None),
                dcc.Store(id="comprehensive-original-indicator-data", data={})
            ], style={'display': 'none'}),

            # 编辑状态提示区域
            html.Div(
                id="comprehensive-editing-status-alert",
                children=[],
                style={'marginBottom': '15px', 'display': 'none'}
            ),
            
            # 新增/编辑综合指标表单
            html.Div([
                html.H6(id="comprehensive-form-title", children="新增综合指标", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                
                # 表单第一行 - 基本信息（4列）
                html.Div([
                    # 施工模式
                    html.Div([
                        html.Label("施工模式：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-form-construction-mode",
                            options=[
                                {'label': '钢筋笼模式', 'value': 'steel_cage'},
                                {'label': '钢衬里模式', 'value': 'steel_lining'}
                            ],
                            value='steel_cage',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 指标代码
                    html.Div([
                        html.Label("指标代码：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="comprehensive-code-input",
                            type="text",
                            placeholder="如: ZH-GJL-COST",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 指标名称
                    html.Div([
                        html.Label("指标名称：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="comprehensive-name-input",
                            type="text",
                            placeholder="如: 综合造价预测",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'}),
                    
                    # 单位
                    html.Div([
                        html.Label("单位：", style={'marginBottom': '5px'}),
                        dcc.Input(
                            id="comprehensive-unit-input",
                            type="text",
                            placeholder="如: 万元",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], style={'width': '24%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
                
                # 表单第二行 - 计算配置（3列）
                html.Div([
                    # 计算方法
                    html.Div([
                        html.Label("计算方法：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-form-calculation-method",
                            options=[
                                {'label': 'AI预测', 'value': 'ml_prediction'},
                                {'label': '比率法', 'value': 'ratio_method'}
                            ],
                            value='ml_prediction',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '32%'}),
                    
                    # 指标类型
                    html.Div([
                        html.Label("指标类型：", style={'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="comprehensive-form-indicator-type",
                            options=[
                                {'label': '原始值', 'value': 'raw_value'},
                                {'label': '最终值', 'value': 'final_value'}
                            ],
                            value='raw_value',
                            clearable=False,
                            style={'width': '100%', 'marginBottom': '10px'}
                        )
                    ], style={'width': '32%'}),
                    
                    # 状态
                    html.Div([
                        html.Label("状态：", style={'marginBottom': '5px'}),
                        dcc.RadioItems(
                            id="comprehensive-status-radio",
                            options=[
                                {'label': '启用', 'value': 'enabled'},
                                {'label': '停用', 'value': 'disabled'}
                            ],
                            value='enabled',
                            inline=True
                        )
                    ], style={'width': '32%'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
                
                # 计算逻辑输入
                html.Div([
                    html.Label("计算逻辑：", style={'marginBottom': '5px'}),
                    dcc.Textarea(
                        id="comprehensive-logic-input",
                        placeholder="请输入计算逻辑，如:\n如果 calculation_method == 'ml_prediction':\n    使用 AI模型 预测总造价\n否则:\n    使用历史项目比率计算\n支持引用：\n- 复合指标: {FU-GJL-TDCB}\n- 输入参数: INPUT_工程面积",
                        style={'width': '100%', 'height': '100px', 'padding': '8px', 'marginBottom': '10px'}
                    )
                ]),
                
                # 说明
                html.Div([
                    html.Label("说明：", style={'marginBottom': '5px'}),
                    dcc.Textarea(
                        id="comprehensive-description-input",
                        placeholder="请输入指标说明...",
                        style={'width': '100%', 'height': '60px', 'padding': '8px', 'marginBottom': '10px'}
                    )
                ])
            ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'marginTop': '20px'})
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="close-comprehensive-indicator", color="secondary", className="ml-auto", style={'marginRight': '10px'}),
            dbc.Button("取消编辑", id="cancel-edit-comprehensive", color="warning", style={'marginRight': '10px', 'display': 'none'}),
            dbc.Button("保存", id="save-comprehensive-indicator", color="primary")
        ])
    ], id="modal-comprehensive-indicator", is_open=False, size="xl")

def create_algorithm_config_modal():
    """创建算法模型配置模态窗口 - 重新设计版本"""
    return dbc.Modal([
        dbc.ModalHeader("算法模型配置"),
        dbc.ModalBody([
            # 施工模式选择区域
            html.Div([
                html.Label("施工模式：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id="algorithm-construction-mode-dropdown",
                    options=[
                        {'label': '钢筋笼模式', 'value': 'steel_cage'},
                        {'label': '钢衬里模式', 'value': 'steel_lining'}
                    ],
                    value='steel_cage',
                    clearable=False,
                    style={'width': '100%', 'marginBottom': '20px'}
                )
            ], style={'padding': '15px', 'backgroundColor': '#e3f2fd', 'borderRadius': '5px', 'marginBottom': '20px', 'border': '1px solid #2196f3'}),
            
            # 操作按钮区域
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                    "编辑选中算法"
                ], id="edit-selected-algorithm", color="primary", size="sm", 
                style={'marginRight': '10px'}, disabled=True),
                
                dbc.Button([
                    html.I(className="fas fa-times", style={'marginRight': '5px'}),
                    "取消编辑"
                ], id="cancel-edit-algorithm", color="secondary", size="sm",
                style={'display': 'none'})
            ], style={'marginBottom': '15px', 'textAlign': 'right'}),
            
            # 算法配置表格
            html.Div([
                dash_table.DataTable(
                    id='algorithm-config-table',
                    columns=[
                        {'name': '算法名称', 'id': 'algorithm_name'},
                        {'name': '状态', 'id': 'status_display'}
                    ],
                    data=[],
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ],
                    row_selectable='single',
                    selected_rows=[],
                    page_size=5,
                    style_table={'marginBottom': '20px'}
                )
            ]),
            
            # 状态管理组件（隐藏）
            html.Div([
                dcc.Store(id="algorithm-editing-mode", data=False),
                dcc.Store(id="algorithm-editing-id", data=None),
                dcc.Store(id="algorithm-original-data", data={})
            ], style={'display': 'none'}),

            # 编辑状态提示区域
            html.Div(
                id="algorithm-editing-status-alert",
                children=[],
                style={'marginBottom': '15px', 'display': 'none'}
            ),
            
            # 编辑区域（初始隐藏）
            html.Div([
                html.H6("编辑算法配置", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                
                # 当前算法显示
                html.Div([
                    html.Label("当前算法：", style={'fontWeight': 'bold', 'display': 'inline-block', 'marginRight': '10px'}),
                    html.Span(id="current-algorithm-name", children="", style={'fontSize': '16px', 'color': '#2C3E50'})
                ], style={'marginBottom': '15px'}),
                
                # 状态选择
                html.Div([
                    html.Label("算法状态：", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.RadioItems(
                        id="algorithm-status-radio-edit",
                        options=[
                            {'label': '启用', 'value': 'enabled'},
                            {'label': '停用', 'value': 'disabled'}
                        ],
                        value='enabled',
                        inline=True,
                        style={'marginBottom': '15px'}
                    ),
                    html.Div([
                        html.I(className="fas fa-info-circle", style={'marginRight': '5px', 'color': '#6c757d'}),
                        html.Small(
                            id="algorithm-status-hint-edit",
                            children="停用后该算法在当前施工模式下将不参与价格预测计算",
                            style={'color': '#6c757d', 'fontStyle': 'italic'}
                        )
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#fff3cd', 'borderRadius': '5px', 'marginBottom': '15px'}),
                
                # 算法详情展示
                html.Div([
                    html.Label("算法详情：", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    
                    # 应用场景展示
                    html.Div([
                        html.H6("应用场景：", style={'fontWeight': 'bold', 'color': '#2C3E50', 'marginBottom': '8px'}),
                        html.P(
                            id="algorithm-application-scenario-edit",
                            children="",
                            style={
                                'padding': '12px',
                                'backgroundColor': '#f8f9fa',
                                'borderRadius': '4px',
                                'border': '1px solid #dee2e6',
                                'marginBottom': '15px',
                                'fontSize': '14px',
                                'lineHeight': '1.6',
                                'minHeight': '60px'
                            }
                        )
                    ]),
                    
                    # 模型描述展示
                    html.Div([
                        html.H6("模型描述：", style={'fontWeight': 'bold', 'color': '#2C3E50', 'marginBottom': '8px'}),
                        html.P(
                            id="algorithm-model-description-edit", 
                            children="",
                            style={
                                'padding': '12px',
                                'backgroundColor': '#f8f9fa',
                                'borderRadius': '4px',
                                'border': '1px solid #dee2e6',
                                'marginBottom': '15px',
                                'fontSize': '14px',
                                'lineHeight': '1.6',
                                'minHeight': '60px'
                            }
                        )
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'marginBottom': '15px'}),
                
                # 保存按钮
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-save", style={'marginRight': '5px'}),
                        "保存编辑"
                    ], id="save-algorithm-edit", color="primary", style={'marginRight': '10px'}),
                    
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '5px'}),
                        "取消编辑"
                    ], id="cancel-algorithm-edit", color="secondary")
                ], style={'textAlign': 'center'})
                
            ], id="algorithm-edit-area", style={'display': 'none', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'border': '2px solid #007bff'}),
            
            # 状态提示信息区域
            html.Div(
                id="algorithm-config-status-alert",
                children=[],
                style={'marginBottom': '15px', 'display': 'none'}
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-algorithm-config", color="secondary")
        ])
    ],id="modal-algorithm-config", is_open=False, size="xl", centered=True, style={'maxWidth': '90%', 'width': '90%'})

def create_model_training_modal():
    """创建模型训练管理模态窗口 - 重新设计为算法参数管理"""
    return dbc.Modal([
        dbc.ModalHeader("算法参数管理"),
        dbc.ModalBody([
            # 算法选择区域
            html.Div([
                html.Label("选择算法：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id="algorithm-select-dropdown",
                    options=[],  # 将通过回调动态加载
                    placeholder="请选择要配置的算法",
                    clearable=False,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                # 算法描述显示区域
                html.Div(
                    id="algorithm-description-display",
                    children=[
                        html.P("请选择算法查看详细信息", style={'color': '#666', 'fontStyle': 'italic'})
                    ],
                    style={
                        'padding': '15px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '5px',
                        'marginBottom': '20px',
                        'border': '1px solid #dee2e6'
                    }
                )
            ]),
            
            # 参数配置区域
            html.Div([
                # 区域标题和操作按钮
                html.Div([
                    html.H6("参数配置", style={'fontWeight': 'bold', 'margin': '0', 'display': 'inline-block'}),
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                            "编辑参数"
                        ], id="edit-parameters-btn", color="primary", size="sm", 
                        style={'marginRight': '10px'}, disabled=True),
                        
                        dbc.Button([
                            html.I(className="fas fa-undo", style={'marginRight': '5px'}),
                            "重置默认"
                        ], id="reset-parameters-btn", color="secondary", size="sm",
                        disabled=True)
                    ], style={'display': 'inline-block', 'float': 'right'})
                ], style={'marginBottom': '15px', 'overflow': 'hidden'}),
                
                # 参数显示/编辑区域
                html.Div(
                    id="parameters-display-area",
                    children=[
                        html.P("请先选择算法", style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})
                    ],
                    style={
                        'minHeight': '300px',
                        'border': '1px solid #dee2e6',
                        'borderRadius': '5px',
                        'padding': '15px',
                        'backgroundColor': '#ffffff'
                    }
                )
            ]),
            
            # 状态管理组件（隐藏）
            html.Div([
                dcc.Store(id="selected-algorithm-data", data={}),
                dcc.Store(id="parameter-editing-mode", data=False),
                dcc.Store(id="original-parameters-data", data={})
            ], style={'display': 'none'}),

            # 操作状态提示区域
            html.Div(
                id="parameter-status-alert",
                children=[],
                style={'marginTop': '15px', 'display': 'none'}
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-model-training", color="secondary", className="ml-auto", style={'marginRight': '10px'}),
            dbc.Button("取消编辑", id="cancel-parameter-edit", color="warning", style={'marginRight': '10px', 'display': 'none'}),
            dbc.Button("保存参数", id="save-parameters", color="primary", style={'display': 'none'})
        ])
    ], id="modal-model-training", size="xl", is_open=False, style={'maxWidth': '90%', 'width': '90%'})

# 同时需要移除或重命名原有的预测精度评估模态窗口
def create_model_evaluation_modal():
    """原预测精度评估模态窗口 - 已弃用，保留以避免引用错误"""
    return create_model_comparison_modal()  # 重定向到新的模型性能对比窗口


def create_model_comparison_modal():
    """创建模型性能对比模态窗口 - 替换原有的预测精度评估"""
    return dbc.Modal([
        dbc.ModalHeader("模型性能对比"),
        dbc.ModalBody([
            # 施工模式选择区域
            html.Div([
                html.Label("施工模式：", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id="comparison-construction-mode-dropdown",
                    options=[
                        {'label': '钢筋笼模式', 'value': 'steel_cage'},
                        {'label': '钢衬里模式', 'value': 'steel_lining'}
                    ],
                    value='steel_cage',
                    clearable=False,
                    style={'width': '100%', 'marginBottom': '20px'}
                )
            ], style={'padding': '15px', 'backgroundColor': '#e3f2fd', 'borderRadius': '5px', 'marginBottom': '20px', 'border': '1px solid #2196f3'}),
            
            # 功能说明区域
            html.Div([
                html.H6("功能说明：", style={'fontWeight': 'bold', 'color': '#2C3E50', 'marginBottom': '10px'}),
                html.P([
                    "本功能将使用留一法交叉验证评估所有",
                    html.Strong("已启用", style={'color': '#e74c3c'}),
                    "的算法在历史数据上的表现，帮助您选择最适合的预测算法。"
                ], style={'marginBottom': '10px', 'fontSize': '14px'}),
                html.Div([
                    html.Strong("评估指标说明：", style={'color': '#34495e'}),
                    html.Ul([
                        html.Li([html.Strong("MAE"), " (平均绝对误差) - 越小越好"]),
                        html.Li([html.Strong("RMSE"), " (均方根误差) - 越小越好"]), 
                        html.Li([html.Strong("R²"), " (决定系数) - 越接近1越好"]),
                        html.Li([html.Strong("MAPE"), " (平均绝对百分比误差) - 越小越好"])
                    ], style={'marginBottom': '0', 'paddingLeft': '20px'})
                ])
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'marginBottom': '20px'}),
            
            # 启用算法状态显示
            html.Div([
                html.H6("当前启用算法：", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.Div(id="enabled-algorithms-display", children="点击'开始对比'查看启用的算法...")
            ], style={'padding': '15px', 'backgroundColor': '#fff3cd', 'borderRadius': '5px', 'marginBottom': '20px'}),
            
            # 对比结果展示区域
            dcc.Loading([
                # 性能指标汇总表
                html.Div([
                    html.H6("性能指标汇总 (按R²排序)", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='comparison-summary-table',
                        columns=[
                            {'name': '排名', 'id': 'rank'},
                            {'name': '算法名称', 'id': 'algorithm_name'},
                            {'name': 'MAE', 'id': 'mae', 'type': 'numeric'},
                            {'name': 'RMSE', 'id': 'rmse', 'type': 'numeric'},
                            {'name': 'R²', 'id': 'r2', 'type': 'numeric'},
                            {'name': 'MAPE (%)', 'id': 'mape', 'type': 'numeric'}
                        ],
                        data=[],
                        style_cell={'textAlign': 'center', 'padding': '10px', 'fontSize': '14px'},
                        style_header={
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold',
                            'border': '1px solid #dee2e6'
                        },
                        style_data={
                            'border': '1px solid #dee2e6'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 0},  # 最佳算法高亮
                                'backgroundColor': '#d4edda',
                                'color': '#155724',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'column_id': 'r2', 'filter_query': '{r2} > 0.9'},
                                'backgroundColor': '#d1ecf1',
                                'color': '#0c5460'
                            }
                        ]
                    )
                ], style={'marginBottom': '20px'}),
                
                # 性能对比图表
                html.Div([
                    html.H6("性能对比图表", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Graph(
                        id='comparison-chart',
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ])
            ], type="default", color=PRIMARY_COLOR)
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-model-evaluation", color="secondary", className="ml-auto", style={'marginRight': '10px'}),
            dbc.Button([
                html.I(className="fas fa-play me-2"),
                "开始对比"
            ], id="start-evaluation", color="primary")
        ])
    ], id="modal-model-evaluation", size="xl",centered=True, style={'maxWidth': '90%', 'width': '90%'})


def create_delete_confirmation_modal():
    """创建删除确认模态窗口"""
    return dbc.Modal([
        dbc.ModalHeader([
            html.I(className="fas fa-exclamation-triangle", 
                  style={'color': '#dc3545', 'marginRight': '10px'}),
            "确认删除指标"
        ]),
        dbc.ModalBody([
            html.Div(id="delete-confirmation-content"),
            dbc.Alert([
                html.I(className="fas fa-warning", style={'marginRight': '8px'}),
                "警告：删除操作不可撤销！请确认您要删除所选指标。"
            ], color="warning", style={'marginTop': '15px'})
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-delete-indicator", color="secondary"),
            dbc.Button("确认删除", id="confirm-delete-indicator", color="danger")
        ])
    ], id="modal-delete-confirmation", size="md")