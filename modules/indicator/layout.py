# modules/indicator/layout.py
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

import plotly.graph_objs as go
PRIMARY_COLOR = "#2C3E50"  # 深蓝色作为主色
SECONDARY_COLOR = "#18BC9C"  # 青绿色作为次要色

def create_base_indicator_card():
    """创建基础指标测算卡片"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4('基础指标测算', className="card-title mb-0"),
            html.Span("单项构件估算", className="text-muted small")
        ], className="d-flex justify-content-between align-items-center"),
        dbc.CardBody([
            # 施工模式选择
            html.Div([
                dbc.Label("施工模式", className="mb-2"),
                dbc.RadioItems(
                    id='construction-mode-select',
                    options=[
                        {'label': '钢筋笼', 'value': 'steel_cage'},
                        {'label': '钢衬里', 'value': 'steel_lining'}
                    ],
                    value='steel_cage',
                    inline=True,
                    className="mb-3"
                )
            ], className="mb-3"),
            
            # 指标搜索
            html.Div([
                dbc.Label("搜索指标", className="mb-2"),
                dbc.Input(
                    id='indicator-search',
                    type='text',
                    placeholder='输入关键字搜索指标...',
                    autoComplete='off',
                    debounce=True,
                    className="mb-2"
                ),
                
                # 搜索结果列表
                html.Div(
                    id='search-results',
                    className="border rounded",
                    style={
                        'maxHeight': '200px',
                        'overflowY': 'auto',
                        'display': 'none'
                    }
                )
            ], className="mb-3"),
            
            # 已选指标展示
            html.Div([
                dbc.Label("已选指标", className="mb-2"),
                html.Div(
                    id='selected-indicator',
                    className="p-2 bg-light rounded mb-3",
                    style={'minHeight': '38px'}
                ),
                # 添加单价展示区域
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Div("人工单价:", className="fw-bold mb-1"),
                            html.Div(id="labor-unit-price", className="text-primary")
                        ], width=4),
                        dbc.Col([
                            html.Div("材料单价:", className="fw-bold mb-1"),
                            html.Div(id="material-unit-price", className="text-primary")
                        ], width=4),
                        dbc.Col([
                            html.Div("机械单价:", className="fw-bold mb-1"),
                            html.Div(id="machinery-unit-price", className="text-primary")
                        ], width=4)
                    ], className="mb-2"),
                    html.Div([
                        html.Div("总单价:", className="fw-bold mb-1"),
                        html.Div(id="total-unit-price", className="text-success h5")
                    ], className="text-center")
                ], id="price-details", className="mt-2 p-2 border rounded", 
                   style={'display': 'none'})
            ], className="mb-3"),
            
            # 数量输入
            html.Div([
                dbc.Label("数量", className="mb-2"),
                dbc.InputGroup([
                    dbc.Input(
                        id='input-number',
                        type='number',
                        value=1,
                        min=0.01,
                        step=0.01,
                        style={'borderRadius': '4px'}
                    ),
                    dbc.InputGroupText(id='unit-display', children="-")
                ], className="mb-3")
            ], className="mb-3"),
            
            # 计算按钮
            dbc.Button(
                html.Span([
                    html.I(className="fas fa-calculator me-2"),
                    "计算"
                ]),
                id='btn-base-calculate',
                color="primary",
                className="w-100"
            )
        ])
    ], className="h-100 shadow-sm")

def create_composite_indicator_card():
    """创建复合指标测算卡片"""
    return dbc.Card([
        dbc.CardBody([
            html.H4('复合指标测算', className="card-title"),
            html.P('多项构件组合估算', className="card-subtitle text-muted mb-3"),
            
            # 施工模式选择
            html.Div([
                dbc.Label("施工模式", className="mb-2"),
                dbc.RadioItems(
                    id='composite-construction-mode-select',
                    options=[
                        {'label': '钢筋笼', 'value': 'steel_cage'},
                        {'label': '钢衬里', 'value': 'steel_lining'}
                    ],
                    value='steel_cage',
                    inline=True,
                    className="mb-3"
                )
            ], className="mb-3"),
            
            # 指标搜索部分
            html.Div([
                dbc.Label("搜索材料/构件", className="mb-2"),
                dbc.Input(
                    id='composite-indicator-search',
                    type='text',
                    placeholder='输入关键字搜索...',
                    autoComplete='off',
                    debounce=True,
                    className="mb-2"
                ),
                
                # 搜索结果列表
                html.Div(
                    id='composite-search-results',
                    className="border rounded mb-3",
                    style={
                        'maxHeight': '150px',
                        'overflowY': 'auto',
                        'display': 'none'
                    }
                ),

                # 已选项目列表
                html.Div([
                    html.H6("已选项目", className="mb-2"),
                    dash_table.DataTable(
                        id='composite-selected-items-table',
                        columns=[
                            {'name': '项目', 'id': 'name'},
                            {'name': '材料/构件', 'id': 'category'},
                            {'name': '单位', 'id': 'unit'},
                            {'name': '数量', 'id': 'quantity', 'editable': True},
                            {'name': '单价', 'id': 'unit_price'},
                            {'name': '小计', 'id': 'subtotal'}
                        ],
                        data=[],
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '5px',
                            'whiteSpace': 'normal'
                        },
                        style_data_conditional=[{
                            'if': {'column_id': 'quantity'},
                            'backgroundColor': '#f8f9fa'
                        }],
                        row_deletable=True
                    ),
                    # 合计金额显示
                    html.Div([
                        html.Hr(),
                        html.Div([
                            html.Span("总计：", className="fw-bold"),
                            html.Span(
                                "¥ 0.00",
                                id="composite-total",
                                className="float-end text-primary fw-bold"
                            )
                        ])
                    ], id="composite-total-container", className="mt-3")
                ], className="border rounded p-2 mb-3"),

                # 按钮组
                dbc.Row([
                    dbc.Col(
                        dbc.Button(
                            html.Span([
                                html.I(className="fas fa-calculator me-2"),
                                "计算"
                            ]),
                            id='btn-composite-calculate',
                            color="primary",
                            className="w-100 mb-2"
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Button(
                            html.Span([
                                html.I(className="fas fa-save me-2"),
                                "保存项目"
                            ]),
                            id='btn-save-project',
                            color="success",
                            className="w-100 mb-2"
                        ),
                        width=6
                    )
                ]),
                
                # 保存项目的模态框
                dbc.Modal([
                    dbc.ModalHeader("保存项目信息"),
                    dbc.ModalBody([
                        dbc.Input(
                            id="project-name-input",
                            placeholder="项目名称",
                            type="text",
                            className="mb-3"
                        ),
                        dbc.Select(
                            id="project-type-input",
                            options=[
                                {"label": "类型A", "value": "A"},
                                {"label": "类型B", "value": "B"},
                                {"label": "类型C", "value": "C"}
                            ],
                            placeholder="选择项目类型",
                            className="mb-3"
                        ),
                        dbc.InputGroup([
                            dbc.Input(
                                id="project-quantity-input",
                                placeholder="工程量",
                                type="number",
                                className="mb-3"
                            ),
                            dbc.InputGroupText(id="project-unit-display")
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col(
                                dbc.Input(
                                    id="normal-days-input",
                                    placeholder="常规施工工期(天)",
                                    type="number",
                                    className="mb-3"
                                )
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="modular-days-input",
                                    placeholder="模块化施工工期(天)",
                                    type="number",
                                    className="mb-3"
                                )
                            )
                        ]),
                        dbc.Textarea(
                            id="project-remarks-input",
                            placeholder="备注信息",
                            className="mb-3"
                        ),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("取消", id="btn-cancel-save", className="me-2"),
                        dbc.Button("保存", id="btn-confirm-save", color="primary")
                    ])
                ], id="save-project-modal"),
                
                # 保存结果提示Toast
                dbc.Toast(
                    id="save-result-toast",
                    header="保存结果",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    style={
                        "position": "fixed",
                        "top": 80,
                        "right": 20,
                        "width": 350,
                        "z-index": 9999
                    }
                ),
                
                # 数据存储
                dcc.Store(id='composite-selected-items-store'),
            ])
        ])
    ], className="h-100 shadow-sm")

def create_overall_indicator_card():
    """创建综合指标测算卡片"""
    return dbc.Card([
        dbc.CardBody([
            html.H4('综合指标测算', className="card-title"),
            html.P('整体工程造价估算', className="card-subtitle text-muted mb-3"),
            
            html.Div([
                dbc.Label("工程类型"),
                dcc.Dropdown(
                    id='dropdown-project-type',
                    options=[
                        {'label': '钢筋笼', 'value': 'steel_cage'},
                        {'label': '钢衬里', 'value': 'steel_lining'}
                    ],
                    value='steel_cage',
                    clearable=False,
                    style={'marginBottom': '15px'}
                ),
                
                dbc.Label("工程规模 (m²)"),
                dbc.Input(
                    id="project-size", 
                    type="number", 
                    placeholder="输入建筑面积", 
                    value=1000,
                    className="mb-3",
                    min=100
                ),
                
                # 两个按钮并排显示 - 使用文字
                html.Div([
                    dbc.Button(
                        '计算', 
                        id='btn-overall-calculate', 
                        color="primary", 
                        className="me-2",
                        style={'width': '70%'}
                    ),
                    dbc.Button(
                        '配置',
                        id="btn-overall-config",
                        color="light",
                        className="px-3",
                        style={'width': '30%'}
                    ),
                ], style={"display": "flex", "marginTop": "15px"})
            ])
        ])
    ], className="h-100 shadow-sm")


def create_cost_result_card():
    """创建成本结果卡片"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H4("估算结果", className="mb-4 text-center"),
                
                # 成本项卡片组
                dbc.Row([
                    # 材料成本
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5('材料成本', className="text-center text-muted"),
                                html.H2([
                                    "¥ ", 
                                    html.Span(id="cost-result-material", children="0", style={"color": PRIMARY_COLOR})
                                ], className="text-center mb-2"),
                                html.Div([
                                    dbc.Badge(id="cost-percent-material", children="占比 0%", color="light", className="me-2"),
                                    dbc.Badge("误差 ±6%", color="warning"),
                                ], className="text-center")
                            ])
                        ], className="border-0 bg-light")
                    ], width=12, md=4, className="mb-3 mb-md-0"),
                    
                    # 人工成本
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5('人工成本', className="text-center text-muted"),
                                html.H2([
                                    "¥ ", 
                                    html.Span(id="cost-result-labor", children="0", style={"color": PRIMARY_COLOR})
                                ], className="text-center mb-2"),
                                html.Div([
                                    dbc.Badge(id="cost-percent-labor", children="占比 0%", color="light", className="me-2"),
                                    dbc.Badge("误差 ±6%", color="warning"),
                                ], className="text-center")
                            ])
                        ], className="border-0 bg-light")
                    ], width=12, md=4, className="mb-3 mb-md-0"),
                    
                    # 设备成本
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5('设备成本', className="text-center text-muted"),
                                html.H2([
                                    "¥ ", 
                                    html.Span(id="cost-result-machinery", children="0", style={"color": PRIMARY_COLOR})
                                ], className="text-center mb-2"),
                                html.Div([
                                    dbc.Badge(id="cost-percent-machinery", children="占比 0%", color="light", className="me-2"),
                                    dbc.Badge("误差 ±6%", color="warning"),
                                ], className="text-center")
                            ])
                        ], className="border-0 bg-light")
                    ], width=12, md=4)
                ]),
                
                # 总造价信息
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("总造价", className="mb-0"),
                            html.H2([
                                "¥ ", 
                                html.Span(id="cost-result-total", children="0", style={"color": SECONDARY_COLOR})
                            ], className="mb-0")
                        ], className="d-flex justify-content-between align-items-center")
                    ], width=6)
                ], className="mt-4 border-top pt-3")
            ])
        ])
    ], className="shadow-sm")

def create_cost_chart_card():
    """创建成本图表卡片"""
    return dbc.Card([
        dbc.CardBody([
            html.H4("成本构成", className="mb-3 text-center"),
            dcc.Graph(
                id='cost-breakdown-chart',
                figure=go.Figure(
                    data=[
                        go.Pie(
                            labels=['材料成本', '人工成本', '设备成本', '其他成本'],
                            values=[358674, 358674, 358674, 0],
                            hole=.3,
                            marker=dict(
                                colors=[PRIMARY_COLOR, SECONDARY_COLOR, '#F39C12', '#95A5A6']
                            )
                        )
                    ],
                    layout=go.Layout(
                        margin=dict(l=20, r=20, t=0, b=0),
                        height=300,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.1,
                            xanchor="center",
                            x=0.5
                        )
                    )
                ),
                config={'displayModeBar': False}
            )
        ])
    ], className="shadow-sm h-100")


def create_indicator_layout():
    """创建指标测算模块的布局"""
    return html.Div([
        # 三个测算模块
        dbc.Row([
            # 基础指标测算
            dbc.Col(create_base_indicator_card(), width=12, md=4, className="mb-4"),
            
            # 复合指标测算
            dbc.Col(create_composite_indicator_card(), width=12, md=4, className="mb-4"),
            
            # 综合指标测算
            dbc.Col(create_overall_indicator_card(), width=12, md=4, className="mb-4"),
        ], className="mb-4"),
        
        # 造价预测结果部分
        dbc.Row([
            # 成本卡片
            dbc.Col(create_cost_result_card(), width=12, md=8),
            
            # 图表部分
            dbc.Col(create_cost_chart_card(), width=12, md=4, className="mt-4 mt-md-0")
        ])
    ])