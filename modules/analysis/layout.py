# modules/analysis/layout.py
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import plotly.graph_objects as go
from config import PRIMARY_COLOR, SECONDARY_COLOR

def create_analysis_layout():
    """创建数据分析模块的布局"""
    return html.Div([
        # 顶部控制栏
        html.Div([
            # 左侧选择器
            html.Div([
                html.Div([
                    html.I(className="fas fa-database", style={'color': PRIMARY_COLOR, 'fontSize': '18px', 'marginRight': '10px'}),
                    html.Span("专用模块分析表"),
                    html.I(className="fas fa-caret-down", style={'marginLeft': '5px'})
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '10px 15px',
                    'cursor': 'pointer',
                    'borderRadius': '3px',
                    'border': '1px solid #ccc'
                })
            ], style={'display': 'inline-block'}),
            
            # 右侧工具 - 使用下拉列表
            html.Div([
                dcc.Dropdown(
                    id="algorithm-type-dropdown",
                    options=[
                        {'label': '线性回归', 'value': 'linear_regression'},
                        {'label': '神经网络', 'value': 'neural_network'},
                        {'label': '决策树', 'value': 'decision_tree'},
                        {'label': '随机森林', 'value': 'random_forest'},
                        {'label': '支持向量机', 'value': 'svm'}
                    ],
                    value='linear_regression',
                    clearable=False,
                    style={'width': '180px'}
                )
            ], style={'display': 'inline-block', 'float': 'right'})
        ], style={'padding': '10px 0px', 'backgroundColor': 'white', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'borderRadius': '5px', 'margin': '10px 0'}),
        
        # 中间部分 - 左侧数据库与右侧图表
        html.Div([
            # 左侧数据库部分
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-table", style={'marginRight': '10px'}),
                        html.H5("数据库表", style={'display': 'inline-block', 'margin': '0'})
                    ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderBottom': '1px solid #ddd'})
                ]),
                
                html.Div([
                    dbc.Button([
                        html.Span("工装及吊装费用表"),
                        html.I(className="fas fa-chevron-down", style={'float': 'right'})
                    ], color="light", className="w-100 text-left", style={'textAlign': 'left', 'borderRadius': '0'}),
                    
                    dbc.Button([
                        html.Span("拼装场地费用表"),
                        html.I(className="fas fa-chevron-down", style={'float': 'right'})
                    ], color="light", className="w-100 text-left", style={'textAlign': 'left', 'borderRadius': '0'}),
                    
                    dbc.Button([
                        html.Span("机械费用"),
                        html.I(className="fas fa-chevron-down", style={'float': 'right'})
                    ], color="light", className="w-100 text-left", style={'textAlign': 'left', 'borderRadius': '0'})
                ])
            ], style={'width': '25%', 'padding': '0', 'boxSizing': 'border-box', 'backgroundColor': 'white', 'borderRadius': '5px', 'border': '1px solid #ddd', 'overflow': 'hidden', 'marginRight': '15px'}),
            
            # 右侧图表部分
            html.Div([
                # 搜索和上传文件部分
                html.Div([
                    dbc.Input(
                        id="search-input",
                        placeholder="输入影响因素...", 
                        style={'width': '50%', 'display': 'inline-block', 'marginRight': '10px'}
                    ),
                    
                    # 装饰材料下拉列表
                    html.Div([
                        dcc.Dropdown(
                            id="material-category-dropdown",
                            options=[
                                {'label': '装饰材料', 'value': 'decoration'},
                                {'label': '钢材', 'value': 'steel'},
                                {'label': '混凝土', 'value': 'concrete'},
                                {'label': '木材', 'value': 'wood'}
                            ],
                            value='decoration',
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], style={'width': '50%', 'display': 'inline-block', 'marginRight': '10px'}),
                ], style={'margin': '10px 0', 'padding': '0 10px', 'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
                
                # 按钮区域 - 将两个按钮分开放置
                html.Div([
                    html.Button('预测', 
                        id='predict-button', 
                        style={
                            'width': '120px',
                            'height': '38px',
                            'lineHeight': '40px',
                            'backgroundColor': '#4CAF50',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'textAlign': 'center',
                            'cursor': 'pointer',
                            'fontSize': '16px',
                            'marginRight': '15px'
                        }
                    ),
                    html.Button('保存价格', 
                        id='save-button', 
                        style={
                            'width': '120px',
                            'height': '38px',
                            'lineHeight': '40px',
                            'backgroundColor': PRIMARY_COLOR, 
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'textAlign': 'center',
                            'cursor': 'pointer',
                            'fontSize': '16px'
                        }
                    ),
                ], style={'margin': '10px 0', 'padding': '0 10px', 'display': 'flex', 'alignItems': 'center'}),
                
                # 数据存储组件
                dcc.Store(id='file-uploaded-flag', data=False),
                dcc.Store(id='uploaded-data-store'),
                
                # 图表部分（初始状态隐藏）
                html.Div(
                    id="prediction-results-container",
                    style={"display": "none"},
                    children=[
                        dcc.Graph(
                            id='prediction-graph',
                            style={'borderRadius': '5px', 'border': '1px solid #ddd', 'backgroundColor': 'white', 'height': '400px'}
                        )
                    ]
                ),
                
                # 分析状态提示
                html.Div(
                    id="analysis-status",
                    children=html.Div([
                        html.I(className="fas fa-info-circle", style={'marginRight': '10px', 'color': PRIMARY_COLOR}),
                        html.Span("请导入数据并点击预测按钮查看分析结果")
                    ], style={
                        'textAlign': 'center',
                        'padding': '100px 20px',
                        'color': '#666',
                        'fontSize': '18px'
                    }),
                    style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                        'height': '400px',
                        'border': '1px dashed #ccc',
                        'borderRadius': '5px',
                        'backgroundColor': '#f9f9f9'
                    }
                )
            ], style={'width': '75%', 'padding': '0', 'boxSizing': 'border-box'})
        ], style={'display': 'flex', 'padding': '10px 0', 'marginBottom': '20px'}),
        
        # 添加一个用于显示当前数据库名称的隐藏元素
        html.Div(id="current-db-name", style={"display": "none"}, children="附件1: 土建专业模块化费用分析表")
    ])