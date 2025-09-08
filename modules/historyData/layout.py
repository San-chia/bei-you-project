from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc

def history_data_layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("施工历史数据", className="mb-2"),
                html.P("点击表格单元格直接编辑，点击操作列删除记录，在最后一行添加新记录", className="text-muted small"),
            ], width=12, className="mb-3")
        ]),
        
        dbc.Card([
            dbc.CardBody([
                # 施工模式选择区域（简化版）
                dbc.Row([
                    dbc.Col([
                        html.Label("选择施工模式：", className="fw-bold mb-2"),
                        dbc.RadioItems(
                            options=[
                                {"label": "钢筋笼施工模式", "value": "steel_cage"},
                                {"label": "钢衬里施工模式", "value": "steel_lining"},
                            ],
                            value="steel_cage",
                            id="construction-mode-radio",
                            inline=True,
                            className="mb-0"
                        ),
                        html.Small("选择施工模式，系统将自动连接到对应的数据库", className="text-muted d-block mt-1")
                    ], width=12, md=6, className="mb-3"),

                    dbc.Col([
                        html.Label("选择项目：", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='project-select',
                            options=[],  # 由回调动态填充
                            placeholder="请选择项目（可选）",
                            clearable=True,
                            style={"width": "100%"}
                        ),
                        html.Small("选择具体项目查看项目数据，留空则显示施工模式数据", className="text-muted d-block mt-1")
                    ], width=12, md=6, className="mb-3"),
                ]),
                
                # 控制按钮和搜索区域（修改2：添加撤回按钮）
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button(
                                html.Span([html.I(className="fas fa-sync-alt me-1"), "刷新数据"]), 
                                id="btn-refresh", 
                                color="secondary",
                                size="sm"
                            ),
                            dbc.Button(
                                html.Span([html.I(className="fas fa-undo me-1"), "撤回"]), 
                                id="btn-undo-delete", 
                                color="warning",
                                size="sm",
                                disabled=True
                            ),
                        ])
                    ], width=12, md=4, className="mb-3"),
                    
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(id="search-input2", placeholder="输入关键词搜索...", type="text"),
                            dbc.Button("搜索", id="btn-search", color="primary", size="sm"),
                        ], size="sm"),
                    ], width=12, md=8, className="mb-3")
                ]),

                # 操作说明
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.H6("📋 操作说明：", className="alert-heading mb-2"),
                            html.Ul([
                                html.Li("🔄 左侧选择施工模式 → 右侧显示对应数据库的项目列表"),
                                html.Li("📊 选择施工模式显示模式数据，选择项目显示项目数据"),
                                html.Li("✏️ 直接点击表格单元格编辑，点击其他地方自动保存到对应数据库"),
                                html.Li("🗑️ 点击操作列删除记录，点击撤回按钮恢复删除"),
                                html.Li("➕ 在最后一行（新增行）输入数据添加新记录到当前数据库"),
                                html.Li("🔍 使用搜索框在当前数据中进行模糊搜索，数值字段支持小数"),
                            ], className="mb-0 small")
                        ], color="info", className="py-2")
                    ], width=12, className="mb-3")
                ]),

                # 数据表格 - 支持内联编辑
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id='construction-data-table',
                            columns=[],
                            data=[],
                            editable=True,  # 启用编辑功能
                            page_size=15,
                            filter_action="native",
                            sort_action="native",
                            style_table={'overflowX': 'auto', 'minHeight': '400px'},
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                                'border': '1px solid #ddd',
                                'fontSize': '14px'
                            },
                            style_cell={
                                'textAlign': 'left', 
                                'minWidth': '80px', 
                                'width': '120px', 
                                'maxWidth': '200px',
                                'padding': '8px',
                                'border': '1px solid #ddd',
                                'fontSize': '13px',
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            style_data_conditional=[
                                # 交替行颜色
                                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                                # 操作列样式
                                {
                                    'if': {'column_id': 'operations'},
                                    'backgroundColor': '#e3f2fd',
                                    'textAlign': 'center',
                                    'fontWeight': 'bold',
                                    'color': '#1976d2',
                                    'cursor': 'pointer'
                                },
                                # 序号列样式（不可编辑）
                                {
                                    'if': {'column_id': '序号'},
                                    'backgroundColor': '#f5f5f5',
                                    'textAlign': 'center',
                                    'fontWeight': 'bold'
                                },
                                # 新增行高亮 - 使用row_type字段
                                {
                                    'if': {'filter_query': '{row_type} = new'},
                                    'backgroundColor': '#e8f5e8',
                                    'border': '2px solid #4caf50'
                                },
                                # 已删除行样式（即将消失的行）
                                {
                                    'if': {'filter_query': '{row_type} = deleted'},
                                    'backgroundColor': '#ffebee',
                                    'border': '2px solid #f44336',
                                    'opacity': '0.6'
                                }
                            ],
                            # 列特定样式
                            style_cell_conditional=[
                                # 数值列右对齐
                                {
                                    'if': {'column_id': ['序号', '直接施工人工单价', '直接施工材料单价', '直接施工机械单价',
                                                        '模块化施工人工单价', '模块化施工材料单价', '模块化施工机械单价']},
                                    'textAlign': 'right'
                                },
                                # 操作列居中
                                {
                                    'if': {'column_id': 'operations'},
                                    'textAlign': 'center',
                                    'width': '80px'
                                }
                            ],
                            # 启用markdown渲染用于操作链接
                            markdown_options={"html": True},
                            # 编辑配置
                            row_deletable=False,  # 禁用默认删除功能，使用自定义删除
                            export_format="xlsx",
                            export_headers="display"
                        ),
                        width=12
                    )
                ]),

                # 分页和统计信息
                dbc.Row([
                    dbc.Col([
                        html.Div(id="data-stats", className="text-muted small mt-2")
                    ], width=12, md=6),
                    dbc.Col([
                        dbc.Pagination(
                            id="table-pagination",
                            max_value=5,
                            first_last=True,
                            previous_next=True,
                            className="pagination pagination-sm justify-content-end mt-2"
                        ),
                    ], width=12, md=6)
                ]),

                # 操作反馈提示
                dbc.Row([
                    dbc.Col([
                        html.Div(id='operation-feedback', className="mt-3"),
                        html.Div(id='delete-feedback', className="mt-2"),
                        html.Div(id='undo-feedback', className="mt-2")  # 修改2：添加撤回反馈
                    ])
                ])
            ])
        ]),

        # 存储组件 - 用于状态管理
        dcc.Store(id='current-mode', data='steel_cage'),
        dcc.Store(id='deleted-record-store', data={}),  # 存储最近删除的记录
        dcc.Store(id='current-table-name', data=''),  # 存储当前表名

    ])
    