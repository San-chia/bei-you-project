# modules/report_management/layout.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import PRIMARY_COLOR

def create_report_management_layout():
    """创建报表管理模块的布局"""
    
    layout = dbc.Container([
        # 页面标题
        dbc.Row([
            dbc.Col([
                html.H2("报表管理", className="mb-2", style={'color': PRIMARY_COLOR}),
                html.P("选择预定义模板快速生成报表，配置管理模板，或创建自定义报表", className="text-muted")
            ], width=12)
        ]),
        
        # 操作按钮区
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-history me-2"), "历史报表"],
                        id="report-history-btn",
                        color="secondary",
                        outline=True
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "导入模板"],
                        id="import-template-btn",
                        color="secondary",
                        outline=True
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-upload me-2"), "导出模板"],
                        id="export-template-btn",
                        color="secondary",
                        outline=True
                    )
                ])
            ], width=12, className="mb-4")
        ]),
        
        # 主要功能卡片区域
        dbc.Row([
            # 预定义模板卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-file-alt fa-lg me-2", style={'color': PRIMARY_COLOR}),
                        html.Span("预定义模板", className="h5 mb-0")
                    ], className="d-flex align-items-center"),
                    dbc.CardBody([
                        html.P("使用系统预定义的报表模板快速生成专业报表", className="text-muted mb-3"),
                        dcc.Dropdown(
                            id="predefined-template-select",
                            options=[
                                {"label": "项目成本分析报表", "value": "cost_analysis"},
                                {"label": "施工效率对比报表", "value": "efficiency_comparison"},
                                {"label": "资源利用率报表", "value": "resource_utilization"},                             
                                {"label": "财务收益报表", "value": "financial_benefit"},
                                {"label": "综合管理仪表板", "value": "management_dashboard"}
                            ],
                            placeholder="选择报表模板",
                            className="mb-3"
                        ),
                        html.Div(id="template-description", className="mb-3"),
                        dbc.Button(
                            "生成报表",
                            id="generate-report-btn",
                            color="primary",
                            className="w-100",
                            disabled=True
                        )
                    ])
                ], className="h-100 shadow-sm")
            ], lg=6, md=12, className="mb-4"),
            

            
            # 模板配置卡片
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-cogs fa-lg me-2", style={'color': PRIMARY_COLOR}),
                        html.Span("模板配置", className="h5 mb-0")
                    ], className="d-flex align-items-center"),
                    dbc.CardBody([
                        html.P("管理和配置报表模板，设置权限和参数", className="text-muted mb-3"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Div([
                                    html.H6("创建自定义模板", className="mb-1"),
                                    html.Small("根据需求创建新的报表模板", className="text-muted")
                                ]),
                                dbc.Button(
                                    "创建",
                                    id="create-custom-template-btn",
                                    color="success",
                                    size="sm",
                                    className="ms-auto"
                                )
                            ], className="d-flex justify-content-between align-items-center"),
                            
                            dbc.ListGroupItem([
                                html.Div([
                                    html.H6("编辑现有模板", className="mb-1"),
                                    html.Small("修改和完善已有的报表模板", className="text-muted")
                                ]),
                                dbc.Button(
                                    "编辑",
                                    id="edit-template-btn",
                                    color="info",
                                    size="sm",
                                    className="ms-auto"
                                )
                            ], className="d-flex justify-content-between align-items-center")
                            
  
                        ])
                    ])
                ], className="h-100 shadow-sm")
            ], lg=6, md=12, className="mb-4")
        ]),
        
        # 存储选中的模板信息
        dcc.Store(id="selected-template-store"),
       
        
        # 导出下载
        dcc.Download(id="download-report"),
        
        # 模态框集合
        create_report_generation_modal(),      # 报表生成配置模态框
        create_report_preview_modal(),         # 报表预览模态框
        create_custom_template_modal(),        # 创建自定义模板模态框
        create_edit_template_modal(),          # 编辑模板模态框
        
        create_statistics_modal(),             # 使用统计模态框
        create_report_history_modal(),         # 历史报表模态框
        create_pdf_export_instruction_modal(), # PDF导出说明模态框
        
        
        
    ], fluid=True, className="mt-4")
    
    return layout

def create_report_generation_modal():
    """创建报表生成配置模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("配置报表参数", id="report-config-modal-title")),
        dbc.ModalBody([
            dbc.Spinner([
                html.Div(id="report-config-content")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-report-config", color="secondary", className="me-2"),
            dbc.Button("保存为模板", id="save-as-template-btn", color="info", outline=True, className="me-2"),
            dbc.Button("生成预览", id="preview-report-btn", color="primary")
        ])
    ], id="report-generation-modal", size="xl", is_open=False)

def create_report_preview_modal():
    """创建报表预览模态框"""
    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle("", id="report-preview-modal-title"),
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="fas fa-edit me-2"), "编辑"],
                    id="edit-report-btn",
                    color="info",
                    size="sm",
                    outline=True
                ),
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "导出"],
                    id="export-report-btn",
                    color="success",
                    size="sm",
                    outline=True
                )
            ], className="ms-auto")
        ]),
        dbc.ModalBody([
            dbc.Spinner([
                html.Div(id="report-preview-content")
            ], size="lg")
        ])
    ], id="report-preview-modal", size="xl", fullscreen=True, is_open=False)

def create_custom_template_modal():
    """创建自定义模板模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("创建自定义模板")),
        dbc.ModalBody([
            html.Div([
                html.H5("1. 基本信息", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("模板名称"),
                        dbc.Input(id="template-name-input", placeholder="输入模板名称")
                    ], md=6),
                    dbc.Col([
                        dbc.Label("模板类别"),
                        dcc.Dropdown(
                            id="template-category-select",
                            options=[
                                {"label": "技经专业核心", "value": "TECH_ECON"},
                                {"label": "项目管理", "value": "PROJECT_MGMT"},
                                {"label": "决策支持", "value": "DECISION_SUPPORT"},
                                {"label": "专项分析", "value": "SPECIAL_ANALYSIS"}
                            ]
                        )
                    ], md=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("模板描述"),
                        dbc.Textarea(id="template-description-input", placeholder="输入模板描述")
                    ])
                ], className="mb-3"),
                
                html.Hr(),
                html.H5("2. 数据配置", className="mb-3"),
                dcc.Dropdown(
                    id="template-data-sources",
                    options=[
                        {"label": "项目数据", "value": "PROJECT"},
                        {"label": "合同数据", "value": "CONTRACT"},
                        {"label": "成本数据", "value": "COST"},
                        {"label": "预算数据", "value": "BUDGET"}
                    ],
                    multi=True,
                    placeholder="选择数据源"
                ),
                
                html.Hr(),
                html.H5("3. 报表组件", className="mb-3"),
                html.Div(id="template-sections", children=[
                    html.P("点击下面按钮添加组件", className="text-muted")
                ]),
                dbc.ButtonGroup([
                    dbc.Button("添加汇总卡片", id="add-summary-section", outline=True, size="sm"),
                    dbc.Button("添加图表", id="add-chart-section", outline=True, size="sm"),
                    dbc.Button("添加表格", id="add-table-section", outline=True, size="sm"),
                    dbc.Button("添加KPI卡片", id="add-kpi-section", outline=True, size="sm")
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-custom-template", color="secondary", className="me-2"),
            dbc.Button("创建", id="save-custom-template", color="primary")
        ])
    ], id="custom-template-modal", size="xl", is_open=False)

def create_edit_template_modal():
    """创建编辑模板模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("编辑模板")),
        dbc.ModalBody([
            html.P("选择要编辑的模板："),
            dcc.Dropdown(
                id="template-select-for-edit",
                placeholder="选择模板"
            ),
            html.Hr(),
            html.Div(id="template-edit-content")
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-edit-template", color="secondary", className="me-2"),
            dbc.Button("保存修改", id="save-template-changes", color="primary")
        ])
    ], id="edit-template-modal", size="xl", is_open=False)

def create_permissions_modal():
    """创建权限管理模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("模板权限管理")),
        dbc.ModalBody([
            html.P("选择要管理权限的模板："),
            dcc.Dropdown(
                id="template-select-for-permissions",
                placeholder="选择模板"
            ),
            html.Hr(),
            html.Div(id="permissions-content")
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-permissions", color="secondary", className="me-2"),
            dbc.Button("保存权限", id="save-permissions", color="primary")
        ])
    ], id="permissions-modal", size="lg", is_open=False)

def create_statistics_modal():
    """创建使用统计模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("模板使用统计")),
        dbc.ModalBody([
            dbc.Spinner([
                html.Div(id="statistics-content")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-statistics", className="ms-auto")
        ])
    ], id="statistics-modal", size="lg", is_open=False)

def create_report_history_modal():
    """创建历史报表模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("历史报表")),
        dbc.ModalBody([
            dbc.Spinner([
                html.Div(id="report-history-content")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-report-history", className="ms-auto")
        ])
    ], id="report-history-modal", size="xl", is_open=False)

def create_pdf_export_instruction_modal():
    """创建PDF导出说明模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("PDF导出说明")),
        dbc.ModalBody([
            html.P("由于系统限制，PDF导出采用以下方式："),
            html.Ol([
                html.Li("点击导出后，系统将生成一个格式化的HTML页面"),
                html.Li("页面会在新窗口中打开"),
                html.Li("使用浏览器的打印功能 (Ctrl+P 或 Cmd+P)"),
                html.Li("在打印设置中选择'另存为PDF'"),
                html.Li("点击保存即可得到PDF格式的报表")
            ]),
            html.Hr(),
            html.P("提示：", className="fw-bold"),
            html.Ul([
                html.Li("建议使用Chrome或Edge浏览器以获得最佳效果"),
                html.Li("打印时可以调整页边距和缩放比例"),
                html.Li("选择'背景图形'选项以保留颜色和样式")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("我知道了", id="close-pdf-instruction", className="ms-auto")
        ])
    ], id="pdf-export-instruction-modal", is_open=False)

def create_custom_report_designer_modal():
    """创建自定义报表设计器模态框"""
    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle("自定义报表设计器"),
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "保存"],
                    id="save-custom-design-btn",
                    color="success",
                    size="sm"
                ),
                dbc.Button(
                    [html.I(className="fas fa-play me-2"), "预览"],
                    id="preview-custom-design-btn",
                    color="info",
                    size="sm"
                )
            ], className="ms-auto")
        ]),
        dbc.ModalBody([
            dbc.Row([
                # 左侧：组件面板
                dbc.Col([
                    html.H5("组件库", className="mb-3"),
                    dbc.Accordion([
                        dbc.AccordionItem([
                            create_draggable_component("summary-card", "汇总卡片", "id-card"),
                            create_draggable_component("kpi-card", "KPI指标卡", "tachometer-alt"),
                            create_draggable_component("metric-card", "度量卡片", "chart-line")
                        ], title="数据卡片", item_id="cards"),
                        
                        dbc.AccordionItem([
                            create_draggable_component("line-chart", "折线图", "chart-line"),
                            create_draggable_component("bar-chart", "柱状图", "chart-bar"),
                            create_draggable_component("pie-chart", "饼图", "chart-pie"),
                            create_draggable_component("combo-chart", "组合图", "chart-area"),
                            create_draggable_component("heatmap", "热力图", "th")
                        ], title="图表组件", item_id="charts"),
                        
                        dbc.AccordionItem([
                            create_draggable_component("data-table", "数据表格", "table"),
                            create_draggable_component("pivot-table", "透视表", "th"),
                            create_draggable_component("tree-table", "树形表格", "sitemap")
                        ], title="表格组件", item_id="tables"),
                        
                        dbc.AccordionItem([
                            create_draggable_component("text-box", "文本框", "font"),
                            create_draggable_component("divider", "分割线", "minus"),
                            create_draggable_component("image", "图片", "image")
                        ], title="布局组件", item_id="layout")
                    ], start_collapsed=False),
                    
                    html.Hr(className="my-3"),
                    
                    html.H5("数据源配置", className="mb-3"),
                    dbc.Button(
                        "配置数据源",
                        id="config-data-source-btn",
                        color="primary",
                        outline=True,
                        className="w-100"
                    )
                ], width=3, className="bg-light p-3"),
                
                # 中间：设计画布
                dbc.Col([
                    html.Div([
                        html.H5("设计画布", className="mb-3"),
                        html.Div(
                            id="design-canvas",
                            className="border rounded p-3",
                            style={
                                "minHeight": "600px",
                                "backgroundColor": "#fafafa",
                                "position": "relative"
                            },
                            children=[
                                html.Div(
                                    "拖拽左侧组件到此处开始设计",
                                    className="text-center text-muted",
                                    style={
                                        "position": "absolute",
                                        "top": "50%",
                                        "left": "50%",
                                        "transform": "translate(-50%, -50%)"
                                    }
                                )
                            ]
                        )
                    ])
                ], width=6),
                
                # 右侧：属性面板
                dbc.Col([
                    html.H5("属性配置", className="mb-3"),
                    html.Div(
                        id="properties-panel",
                        children=[
                            html.P("选择组件后在此配置属性", className="text-muted text-center mt-5")
                        ]
                    )
                ], width=3, className="bg-light p-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="close-designer-modal", color="secondary", className="me-2"),
            dbc.Button("生成报表", id="generate-custom-report-btn", color="primary")
        ])
    ], id="custom-report-designer-modal", size="xl", fullscreen=True, is_open=False)

def create_draggable_component(component_type, label, icon):
    """创建可拖拽的组件"""
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.I(className=f"fas fa-{icon} fa-2x mb-2"),
                html.P(label, className="mb-0 small")
            ], className="text-center p-2")
        ], className="draggable-component mb-2", style={"cursor": "move"}),
    ], 
    draggable="true",
    id={"type": "draggable", "component": component_type},
    **{"data-component-type": component_type})

def create_data_filter_modal():
    """创建数据筛选配置模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("数据源与筛选配置")),
        dbc.ModalBody([
            html.H5("1. 选择数据源", className="mb-3"),
            dbc.Checklist(
                id="data-source-checklist",
                options=[
                    {"label": "项目基础数据", "value": "project"},
                    {"label": "成本数据", "value": "cost"},
                    {"label": "进度数据", "value": "schedule"},
                    {"label": "质量数据", "value": "quality"},
                    {"label": "合同数据", "value": "contract"},
                    {"label": "人力资源数据", "value": "hr"},
                    {"label": "材料数据", "value": "material"},
                    {"label": "设备数据", "value": "equipment"}
                ],
                value=["project", "cost"],
                inline=False
            ),
            
            html.Hr(),
            html.H5("2. 数据筛选条件", className="mb-3"),
            
            # 时间范围筛选
            html.H6("时间范围"),
            dcc.DatePickerRange(
                id="filter-date-range",
                start_date_placeholder_text="开始日期",
                end_date_placeholder_text="结束日期",
                display_format="YYYY-MM-DD",
                className="mb-3 w-100"
            ),
            
            # 项目筛选
            html.H6("项目筛选"),
            dcc.Dropdown(
                id="filter-projects",
                multi=True,
                placeholder="选择项目（可多选）",
                className="mb-3"
            ),
            
            # 施工模式筛选
            html.H6("施工模式"),
            dcc.Dropdown(
                id="filter-construction-mode",
                options=[
                    {"label": "总承包", "value": "epc"},
                    {"label": "施工总承包", "value": "construction"},
                    {"label": "设计施工一体化", "value": "db"},
                    {"label": "PPP模式", "value": "ppp"}
                ],
                multi=True,
                placeholder="选择施工模式（可多选）",
                className="mb-3"
            ),
            
            # 成本类型筛选
            html.H6("成本类型"),
            dcc.Dropdown(
                id="filter-cost-types",
                options=[
                    {"label": "直接成本", "value": "direct"},
                    {"label": "间接成本", "value": "indirect"},
                    {"label": "人工成本", "value": "labor"},
                    {"label": "材料成本", "value": "material"},
                    {"label": "设备成本", "value": "equipment"},
                    {"label": "管理费用", "value": "management"}
                ],
                multi=True,
                placeholder="选择成本类型（可多选）",
                className="mb-3"
            ),
            
            # 高级筛选
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("最小金额"),
                            dbc.Input(type="number", id="filter-min-amount", placeholder="0")
                        ], width=6),
                        dbc.Col([
                            html.Label("最大金额"),
                            dbc.Input(type="number", id="filter-max-amount", placeholder="不限")
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("完成度范围"),
                            dcc.RangeSlider(
                                id="filter-completion-range",
                                min=0,
                                max=100,
                                step=5,
                                marks={i: f'{i}%' for i in range(0, 101, 25)},
                                value=[0, 100]
                            )
                        ])
                    ])
                ], title="高级筛选条件")
            ], start_collapsed=True)
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="cancel-data-filter", color="secondary", className="me-2"),
            dbc.Button("应用筛选", id="apply-data-filter", color="primary")
        ])
    ], id="data-filter-modal", size="lg", is_open=False)