# modules/integration/integration_layout.py
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG

def create_integration_layout():
    """创建对接一体化平台的布局"""
    return html.Div(
        # id="tab-9-content",
        # style={"display": "none"},
        children=[
            dbc.Row([
                dbc.Col([
                    # 页面标题
                    html.H2("对接一体化平台", className="mb-4", style={'color': PRIMARY_COLOR}),
                    
                    # 连接状态卡片
                    dbc.Card([
                        dbc.CardHeader(html.H4("平台连接状态", className="mb-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-circle text-success me-2"),
                                        html.Span("连接状态: ", style={'fontWeight': 'bold'}),
                                        html.Span("已连接", id="connection-status", style={'color': 'green'})
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("平台地址: ", style={'fontWeight': 'bold'}),
                                        html.Span("http://platform.example.com", id="platform-url")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("最后同步时间: ", style={'fontWeight': 'bold'}),
                                        html.Span("2024-01-15 14:30:25", id="last-sync-time")
                                    ])
                                ], width=8),
                                dbc.Col([
                                    dbc.Button("测试连接", id="btn-test-connection", color="primary", className="me-2"),
                                    dbc.Button("重新连接", id="btn-reconnect", color="warning")
                                ], width=4, className="text-end")
                            ])
                        ])
                    ], className="mb-4", style={'backgroundColor': CARD_BG}),
                    
                    # 数据同步配置
                    dbc.Card([
                        dbc.CardHeader(html.H4("数据同步配置", className="mb-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("同步频率"),
                                    dcc.Dropdown(
                                        id="sync-frequency",
                                        options=[
                                            {"label": "实时同步", "value": "realtime"},
                                            {"label": "每小时", "value": "hourly"},
                                            {"label": "每日", "value": "daily"},
                                            {"label": "手动同步", "value": "manual"}
                                        ],
                                        value="hourly",
                                        className="mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("数据类型"),
                                    dbc.Checklist(
                                        id="sync-data-types",
                                        options=[
                                            {"label": "工程数据", "value": "engineering"},
                                            {"label": "造价数据", "value": "cost"},
                                            {"label": "进度数据", "value": "progress"},
                                            {"label": "质量数据", "value": "quality"}
                                        ],
                                        value=["engineering", "cost"],
                                        className="mb-3"
                                    )
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("保存配置", id="btn-save-sync-config", color="success", className="me-2"),
                                    dbc.Button("立即同步", id="btn-sync-now", color="primary")
                                ])
                            ])
                        ])
                    ], className="mb-4", style={'backgroundColor': CARD_BG}),
                    
                    # API接口管理
                    dbc.Card([
                        dbc.CardHeader(html.H4("API接口管理", className="mb-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("API密钥"),
                                    dbc.Input(
                                        id="api-key",
                                        type="password",
                                        placeholder="请输入API密钥",
                                        className="mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("API版本"),
                                    dcc.Dropdown(
                                        id="api-version",
                                        options=[
                                            {"label": "v1.0", "value": "v1.0"},
                                            {"label": "v2.0", "value": "v2.0"},
                                            {"label": "v3.0", "value": "v3.0"}
                                        ],
                                        value="v2.0",
                                        className="mb-3"
                                    )
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("超时设置（秒）"),
                                    dbc.Input(
                                        id="api-timeout",
                                        type="number",
                                        value=30,
                                        min=5,
                                        max=300,
                                        className="mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("重试次数"),
                                    dbc.Input(
                                        id="api-retry",
                                        type="number",
                                        value=3,
                                        min=1,
                                        max=10,
                                        className="mb-3"
                                    )
                                ], width=6)
                            ]),
                            dbc.Button("更新API配置", id="btn-update-api-config", color="info")
                        ])
                    ], className="mb-4", style={'backgroundColor': CARD_BG}),
                    
                    # 同步日志
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H4("同步日志", className="mb-0", style={'display': 'inline-block'}),
                                dbc.Button("刷新", id="btn-refresh-logs", color="light", size="sm", className="float-end")
                            ])
                        ]),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id="sync-logs-table",
                                columns=[
                                    {"name": "时间", "id": "timestamp"},
                                    {"name": "操作", "id": "operation"},
                                    {"name": "状态", "id": "status"},
                                    {"name": "数据量", "id": "data_count"},
                                    {"name": "描述", "id": "description"}
                                ],
                                data=[
                                    {
                                        "timestamp": "2024-01-15 14:30:25",
                                        "operation": "数据同步",
                                        "status": "成功",
                                        "data_count": "150条",
                                        "description": "工程数据同步完成"
                                    },
                                    {
                                        "timestamp": "2024-01-15 13:30:25",
                                        "operation": "数据推送",
                                        "status": "成功",
                                        "data_count": "85条",
                                        "description": "造价数据推送完成"
                                    },
                                    {
                                        "timestamp": "2024-01-15 12:30:25",
                                        "operation": "连接测试",
                                        "status": "失败",
                                        "data_count": "-",
                                        "description": "网络连接超时"
                                    }
                                ],
                                style_cell={'textAlign': 'left'},
                                style_data_conditional=[
                                    {
                                        'if': {'filter_query': '{status} = 成功'},
                                        'backgroundColor': '#d4edda',
                                        'color': 'black',
                                    },
                                    {
                                        'if': {'filter_query': '{status} = 失败'},
                                        'backgroundColor': '#f8d7da',
                                        'color': 'black',
                                    }
                                ],
                                page_size=5
                            )
                        ])
                    ], className="mb-4", style={'backgroundColor': CARD_BG})
                    
                ], width=12)
            ]),
            
            # 消息提示
            dbc.Toast(
                id="integration-toast",
                header="系统提示",
                is_open=False,
                dismissable=True,
                icon="info",
                duration=4000,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
            )
        ]
    )
