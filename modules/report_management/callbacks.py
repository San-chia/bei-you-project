# modules/report_management/callbacks.py
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import html, dcc, no_update, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import uuid

from .templates import get_template_by_id, REPORT_TEMPLATES, ChartType, CHART_TYPE_CONFIG
from .data_processor import ReportDataProcessor
from .report_generator import ReportGenerator
from .config_builder import ConfigBuilder

def register_report_management_callbacks(app):
    
    # 初始化数据处理器和报表生成器
    data_processor = ReportDataProcessor()
    report_generator = ReportGenerator()
    
    # 模板选择时更新描述
    @app.callback(
        [Output("template-description", "children"),
         Output("generate-report-btn", "disabled")],
        Input("predefined-template-select", "value")
    )
    def update_template_description(selected_template):
        """更新模板描述"""
        if not selected_template:
            return html.P("请选择一个报表模板", className="text-muted"), True
        
        template = get_template_by_id(selected_template)
        if template:
            description = html.Div([
                html.P(template.get("description", ""), className="mb-2"),
                html.Small(f"数据需求: {', '.join(template['data_requirements']['mandatory'])}", 
                          className="text-muted")
            ])
            return description, False
        
        return html.P("模板信息未找到", className="text-danger"), True
    
    # 点击生成报表按钮
    @app.callback(
        [Output("report-generation-modal", "is_open"),
         Output("report-config-modal-title", "children"),
         Output("report-config-content", "children"),
         Output("selected-template-store", "data")],
        [Input("generate-report-btn", "n_clicks")],
        [State("predefined-template-select", "value"),
         State("report-generation-modal", "is_open")],
        prevent_initial_call=True
    )
    def open_report_generation_modal(n_clicks, selected_template, is_open):
        """打开报表生成配置模态框"""
        if not n_clicks or not selected_template:
            return no_update
        
        template = get_template_by_id(selected_template)
        if not template:
            return no_update
        
        # 创建配置表单
        config_form = create_advanced_config_form(selected_template, template)
        
        return (
            True,
            f"配置报表 - {template['name']}",
            config_form,
            selected_template
        )
    
    # 关闭配置模态框
    @app.callback(
        Output("report-generation-modal", "is_open", allow_duplicate=True),
        Input("cancel-report-config", "n_clicks"),
        State("report-generation-modal", "is_open"),
        prevent_initial_call=True
    )
    def close_generation_modal(n_clicks, is_open):
        if n_clicks:
            return False
        return is_open
    
    # 生成报表预览
    @app.callback(
        [Output("report-preview-modal", "is_open"),
         Output("report-preview-modal-title", "children"),
         Output("report-preview-content", "children")],
        Input("preview-report-btn", "n_clicks"),
        [State("selected-template-store", "data"),
         State({"type": "section-enable", "index": ALL}, "value"),
         State({"type": "section-config", "section": ALL, "option": ALL}, "value"),
         State({"type": "section-config", "section": ALL, "option": ALL}, "id")],
        prevent_initial_call=True
    )
    def generate_report_preview(n_clicks, template_id, section_enables, config_values, config_ids):
        """生成报表预览"""
        if not n_clicks or not template_id:
            return no_update
        
        template = get_template_by_id(template_id)
        if not template:
            return no_update
        
        # 构建配置参数
        config_params = {}
        for i, config_id in enumerate(config_ids):
            if i < len(config_values):
                section_idx = config_id["section"]
                option_key = config_id["option"]
                config_params[f"section_{section_idx}_{option_key}"] = config_values[i]
        
        # 添加section启用状态
        for idx, enabled in enumerate(section_enables):
            config_params[f"section_enable_{idx}"] = enabled
        
        # 获取数据
        filters = {"project_id": "P001"}  # 示例过滤条件
        raw_data = data_processor.fetch_data(
            template["data_requirements"]["mandatory"],
            filters
        )
        
        # 处理数据
        processed_data = data_processor.process_configured_data(
            raw_data, template, config_params
        )
        
        # 生成报表内容
        report_content = generate_report_content(template, processed_data, config_params)
        
        return (
            True,  # 打开预览模态框
            f"{template['name']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            report_content
        )
    
    # 创建自定义模板
    @app.callback(
        Output("custom-template-modal", "is_open"),
        [Input("create-custom-template-btn", "n_clicks"),
         Input("cancel-custom-template", "n_clicks"),
         Input("save-custom-template", "n_clicks")],
        State("custom-template-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_custom_template_modal(create_clicks, cancel_clicks, save_clicks, is_open):
        """控制自定义模板模态框"""
        ctx_id = ctx.triggered_id
        
        if ctx_id in ["cancel-custom-template", "save-custom-template"]:
            return False
        elif ctx_id == "create-custom-template-btn":
            return True
        
        return is_open
    
    # 编辑模板
    @app.callback(
        [Output("edit-template-modal", "is_open"),
         Output("template-select-for-edit", "options")],
        [Input("edit-template-btn", "n_clicks"),
         Input("cancel-edit-template", "n_clicks")],
        State("edit-template-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_edit_template_modal(edit_clicks, cancel_clicks, is_open):
        """控制编辑模板模态框"""
        ctx_id = ctx.triggered_id
        
        if ctx_id == "cancel-edit-template":
            return False, no_update
        elif ctx_id == "edit-template-btn":
            # 准备模板选项
            options = [
                {"label": template["name"], "value": tid}
                for tid, template in REPORT_TEMPLATES.items()
            ]
            return True, options
        
        return is_open, no_update
    

    
    # 历史报表
    @app.callback(
        [Output("report-history-modal", "is_open"),
         Output("report-history-content", "children")],
        [Input("report-history-btn", "n_clicks"),
         Input("close-report-history", "n_clicks")],
        State("report-history-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_report_history(history_clicks, close_clicks, is_open):
        """显示历史报表"""
        ctx_id = ctx.triggered_id
        
        if ctx_id == "close-report-history":
            return False, no_update
        
        if ctx_id == "report-history-btn":
            # 生成历史报表列表（示例数据）
            history_data = [
                {
                    "name": "项目成本分析报表 - 2024-11",
                    "created": "2024-11-15 14:30",
                    "created_by": "张三",
                    "size": "1.2 MB"
                },
                {
                    "name": "施工效率对比报表 - 2024-10",
                    "created": "2024-10-20 09:15",
                    "created_by": "李四",
                    "size": "856 KB"
                },
                {
                    "name": "财务收益报表 - 2024-09",
                    "created": "2024-09-30 16:45",
                    "created_by": "王五",
                    "size": "2.1 MB"
                }
            ]
            
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("报表名称"),
                        html.Th("创建时间"),
                        html.Th("创建人"),
                        html.Th("大小"),
                        html.Th("操作", className="text-center")
                    ])
                ])
            ]
            
            table_body = []
            for report in history_data:
                table_body.append(
                    html.Tr([
                        html.Td(report["name"]),
                        html.Td(report["created"]),
                        html.Td(report["created_by"]),
                        html.Td(report["size"]),
                        html.Td([
                            dbc.ButtonGroup([
                                dbc.Button("查看", color="info", size="sm", outline=True),
                                dbc.Button("下载", color="success", size="sm", outline=True),
                                dbc.Button("删除", color="danger", size="sm", outline=True)
                            ], size="sm")
                        ], className="text-center")
                    ])
                )
            
            history_content = dbc.Table(
                table_header + [html.Tbody(table_body)],
                striped=True,
                hover=True,
                responsive=True
            )
            
            return True, history_content
        
        return no_update, no_update
    

    

    

 
    
    # section开关控制
    @app.callback(
        Output({"type": "section-collapse", "index": MATCH}, "is_open"),
        Input({"type": "section-enable", "index": MATCH}, "value"),
        prevent_initial_call=True
    )
    def toggle_section(enabled):
        """控制section的展开/折叠"""
        return enabled
    
    # 添加图表类型变化时更新可用配置
    @app.callback(
        Output({"type": "chart-config-options", "section": MATCH}, "children"),
        Input({"type": "section-config", "section": MATCH, "option": "chart_type"}, "value"),
        State({"type": "section-config", "section": MATCH, "option": "chart_type"}, "id"),
        prevent_initial_call=True
    )
    def update_chart_options(chart_type, element_id):
        """根据图表类型更新配置选项"""
        if not chart_type:
            return no_update
        
        # 从字符串获取枚举值
        try:
            chart_type_enum = ChartType[chart_type]
        except KeyError:
            return no_update
        
        chart_config = CHART_TYPE_CONFIG.get(chart_type_enum, {})
        
        # 生成适合该图表类型的配置选项
        options = []
        
        # 添加图表说明
        options.append(
            html.Div([
                html.Small(f"适用于: {', '.join(chart_config.get('suitable_for', []))}"),
                html.Hr()
            ], className="text-muted")
        )
        
        # 根据图表类型显示不同的配置
        required_axes = chart_config.get("required_axes", [])
        
        if "x" in required_axes:
            options.append(
                html.Div([
                    dbc.Label("X轴字段"),
                    dcc.Dropdown(
                        id={"type": "axis-field", "axis": "x", "section": element_id["section"]},
                        options=[
                            {"label": "时间", "value": "time"},
                            {"label": "项目", "value": "project"},
                            {"label": "部门", "value": "department"}
                        ],
                        placeholder="选择X轴字段"
                    )
                ], className="mb-3")
            )
        
        return html.Div(options)
    

    # 动态加载项目列表
    @app.callback(
        Output("project-selector", "options"),
        Input("data-source-checklist", "value"),
        prevent_initial_call=False
    )
    def load_project_list(selected_sources):
        """根据选择的数据源加载项目列表"""
        if not selected_sources or "project" not in selected_sources:
            return []
        
        # 这里应该从数据库获取实际项目列表
        # 示例数据
        return [
            {"label": "核电项目A - 2025", "value": "P001"},
            {"label": "核电项目B - 2025", "value": "P002"},
            {"label": "示范工程C - 2024", "value": "P003"}
        ]

def create_advanced_config_form(template_id: str, template: dict) -> html.Div:
    """创建高级配置表单"""
    form_elements = []
    
    # 1. 项目选择和数据源配置
    form_elements.append(
        html.Div([
            html.H5("1. 项目选择与数据源配置", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("选择项目"),
                    dcc.Dropdown(
                        id="project-selector",
                        options=[],  # 将通过回调动态加载
                        placeholder="请选择项目",
                        clearable=False
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("施工模式"),
                    dcc.Dropdown(
                        id="construction-mode-selector",
                        options=[
                            {"label": "钢筋笼", "value": "steel_cage"},
                            {"label": "钢衬里", "value": "steel_lining"}
                        ],
                        placeholder="选择施工模式"
                    )
                ], md=6)
            ], className="mb-3"),
            
            # 数据源选择
            html.Hr(),
            html.H6("选择数据源", className="mb-3"),
            dbc.Checklist(
                id="data-source-checklist",
                options=[
                    {"label": "成本数据（calculation_results）", "value": "cost"},
                    {"label": "预算数据（construction_parameter）", "value": "budget"},
                    {"label": "项目基础数据（project_info）", "value": "project"},
                    {"label": "施工参数数据（parameter_info）", "value": "parameter"},
                    {"label": "历史对比数据", "value": "history"}
                ],
                value=["cost", "budget"],  # 默认选中
                inline=False
            ),
        ])
    )
    
    # 2. 筛选条件配置
    form_elements.append(
        html.Div([
            html.Hr(className="my-4"),
            html.H5("2. 筛选条件", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("成本类型"),
                    dcc.Dropdown(
                        id="cost-type-filter",
                        options=[
                            {"label": "人工费", "value": "labor"},
                            {"label": "材料费", "value": "material"},
                            {"label": "机械费", "value": "machinery"},
                            {"label": "间接费用", "value": "indirect"}
                        ],
                        multi=True,
                        placeholder="选择成本类型（可多选）"
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("对比维度"),
                    dcc.RadioItems(
                        id="comparison-dimension",
                        options=[
                            {"label": "施工模式对比", "value": "mode"},
                            {"label": "时间趋势对比", "value": "time"},
                            {"label": "项目间对比", "value": "project"}
                        ],
                        value="mode",
                        inline=True
                    )
                ], md=6)
            ])
        ])
    )
    
    # 3. 报表内容配置（可视化模块选择）
    form_elements.append(
        html.Div([
            html.Hr(className="my-4"),
            html.H5("3. 报表内容配置", className="mb-3"),
            html.P("选择要包含的内容模块并进行个性化配置", className="text-muted"),
            
            # 使用卡片形式展示可选模块
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Checkbox(
                                id={"type": "module-enable", "module": "overview"},
                                label="成本概览卡片",
                                value=True
                            )
                        ]),
                        dbc.CardBody([
                            html.P("显示总成本、预算金额、执行率、节约率等关键指标", 
                                   className="small text-muted mb-2"),
                            dcc.Dropdown(
                                id="overview-metrics",
                                options=[
                                    {"label": "总成本", "value": "total_cost"},
                                    {"label": "预算金额", "value": "budget"},
                                    {"label": "执行率", "value": "execution_rate"},
                                    {"label": "节约率", "value": "saving_rate"},
                                    {"label": "成本差异", "value": "variance"}
                                ],
                                multi=True,
                                value=["total_cost", "budget", "execution_rate", "saving_rate"],
                                placeholder="选择显示指标"
                            )
                        ])
                    ], className="mb-3")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Checkbox(
                                id={"type": "module-enable", "module": "composition"},
                                label="成本构成分析",
                                value=True
                            )
                        ]),
                        dbc.CardBody([
                            html.P("展示各类成本的占比情况", 
                                   className="small text-muted mb-2"),
                            dcc.RadioItems(
                                id="composition-chart-type",
                                options=[
                                    {"label": "饼图", "value": "pie"},
                                    {"label": "柱状图", "value": "bar"},
                                    {"label": "树形图", "value": "treemap"}
                                ],
                                value="pie",
                                inline=True
                            )
                        ])
                    ], className="mb-3")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Checkbox(
                                id={"type": "module-enable", "module": "comparison"},
                                label="施工模式对比",
                                value=True
                            )
                        ]),
                        dbc.CardBody([
                            html.P("对比直接施工与模块化施工成本", 
                                   className="small text-muted mb-2"),
                            dbc.Checklist(
                                id="comparison-items",
                                options=[
                                    {"label": "分项成本对比", "value": "detail"},
                                    {"label": "总成本对比", "value": "total"},
                                    {"label": "差异分析", "value": "variance"}
                                ],
                                value=["detail", "total"],
                                inline=True
                            )
                        ])
                    ], className="mb-3")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Checkbox(
                                id={"type": "module-enable", "module": "detail"},
                                label="成本明细表",
                                value=True
                            )
                        ]),
                        dbc.CardBody([
                            html.P("详细的成本项目清单", 
                                   className="small text-muted mb-2"),
                            dcc.Dropdown(
                                id="detail-group-by",
                                options=[
                                    {"label": "按类别分组", "value": "category"},
                                    {"label": "按时间分组", "value": "time"},
                                    {"label": "按项目分组", "value": "project"}
                                ],
                                value="category",
                                clearable=False
                            )
                        ])
                    ], className="mb-3")
                ], md=6)
            ])
        ])
    )
    
    # 4. 基本设置
    form_elements.append(
        html.Div([
            html.Hr(className="my-4"),
            html.H5("4. 基本设置", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("报表名称"),
                    dbc.Input(
                        id="custom-report-name",
                        placeholder=f"{template['name']} - {datetime.now().strftime('%Y-%m-%d')}",
                        value=f"{template['name']} - {datetime.now().strftime('%Y-%m-%d')}"
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("统计周期"),
                    dcc.DatePickerRange(
                        id="report-date-range",
                        start_date=datetime.now().replace(day=1).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d"),
                        display_format="YYYY-MM-DD",
                        style={"width": "100%"}
                    )
                ], md=6)
            ])
        ], className="mb-3")
    )
    
    # 5. 导出设置
    form_elements.append(
        html.Div([
            html.Hr(className="my-4"),
            html.H5("5. 导出设置", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("导出格式"),
                    dbc.Checklist(
                        id="export-formats",
                        options=[
                            {"label": "PDF", "value": "pdf"},
                            {"label": "Excel", "value": "xlsx"},
                            {"label": "Word", "value": "docx"}
                        ],
                        value=["pdf"],
                        inline=True
                    )
                ], md=6),
                dbc.Col([
                    dbc.Checkbox(
                        id="include-raw-data",
                        label="包含原始数据",
                        value=False,
                        className="mt-4"
                    )
                ], md=6)
            ])
        ])
    )
    
    return html.Div(form_elements, className="p-3")
def generate_report_content(template: dict, processed_data: dict, config_params: dict) -> html.Div:
    """生成报表内容"""
    content_elements = []
    
    # 首先处理默认sections（如果有的话）
    for section in template.get("default_sections", []):
        section_id = section["id"]
        section_type = section["type"]
        section_data = processed_data.get(section_id, {})
        
        if section_type == "summary_cards":
            element = create_summary_cards(section, section_data)
        elif section_type == "chart":
            element = create_chart_section(section, section_data)
        elif section_type == "table":
            element = create_table_section(section, section_data)
        elif section_type == "kpi_cards":
            element = create_kpi_cards(section, section_data)
        else:
            element = html.Div(f"未实现的组件类型: {section_type}")
        
        content_elements.append(
            html.Div([
                html.H4(section.get("title", ""), className="mb-3"),
                element
            ], className="mb-4")
        )
    
    # 然后处理可配置的sections
    for idx, section in enumerate(template.get("configurable_sections", [])):
        # 检查section是否启用
        if not config_params.get(f"section_enable_{idx}", True):
            continue
            
        section_id = section["id"]
        section_type = section["type"]
        section_data = processed_data.get(section_id, {})
        
        if section_type == "summary_cards":
            element = create_summary_cards(section, section_data)
        elif section_type == "chart":
            element = create_chart_section(section, section_data)
        elif section_type == "table":
            element = create_table_section(section, section_data)
        elif section_type == "tree_table":
            element = create_tree_table_section(section, section_data)
        elif section_type == "kpi_cards":
            element = create_kpi_cards(section, section_data)
        else:
            element = html.Div(f"未实现的组件类型: {section_type}")
        
        content_elements.append(
            html.Div([
                html.H4(section.get("name", ""), className="mb-3"),
                element
            ], className="mb-4")
        )
    
    return html.Div(content_elements, className="p-4")

def create_summary_cards(section: dict, data: dict) -> html.Div:
    """创建汇总卡片"""
    cards = []
    
    for metric in section.get("metrics", []):
        value = data.get(metric["field"], 0)
        
        # 格式化数值
        if metric["format"] == "currency":
            formatted_value = f"¥{value:,.2f}"
        elif metric["format"] == "percentage":
            formatted_value = f"{value*100:.1f}%"
        else:
            formatted_value = f"{value:,.2f}"
        
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(metric["name"], className="text-muted mb-2"),
                    html.H3(formatted_value, className="mb-0")
                ])
            ], className="text-center")
        ], md=3)
        
        cards.append(card)
    
    return dbc.Row(cards)

def create_chart_section(section: dict, data: dict) -> dcc.Graph:
    """创建图表"""
    chart_type = section.get("chart_type", "line")
    
    # 这里应该根据实际数据创建图表
    # 现在创建一个示例图表
    if chart_type == "line":
        fig = px.line(
            x=list(range(1, 13)),
            y=[100 + i*10 + (i%3)*5 for i in range(12)],
            title=""
        )
    elif chart_type == "bar":
        fig = px.bar(
            x=["A", "B", "C", "D"],
            y=[100, 150, 120, 180],
            title=""
        )
    elif chart_type == "pie":
        fig = px.pie(
            values=[30, 25, 20, 25],
            names=["人工", "材料", "设备", "其他"],
            title=""
        )
    else:
        # 组合图表示例
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(1, 13)),
            y=[100 + i*10 for i in range(12)],
            name="计划成本",
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=list(range(1, 13)),
            y=[95 + i*11 for i in range(12)],
            name="实际成本",
            yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=[0.95 + (i%3)*0.02 for i in range(12)],
            name="执行率",
            yaxis='y2',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            yaxis=dict(title="金额（万元）", side="left"),
            yaxis2=dict(title="执行率", side="right", overlaying='y'),
            hovermode='x unified'
        )
    
    fig.update_layout(
        template="plotly_white",
        height=400
    )
    
    return dcc.Graph(figure=fig)

def create_table_section(section: dict, data) -> html.Div:
    """创建表格"""
    if isinstance(data, pd.DataFrame) and not data.empty:
        columns = []
        for col_config in section.get("columns", []):
            col = {
                "name": col_config["title"],
                "id": col_config["field"],
                "type": "numeric" if col_config.get("format") in ["currency", "percentage"] else "text"
            }
            if col_config.get("format") == "currency":
                col["format"] = {"specifier": ",.2f"}
            elif col_config.get("format") == "percentage":
                col["format"] = {"specifier": ".1%"}
            columns.append(col)
        
        # 使用简单的HTML表格
        return dbc.Table.from_dataframe(
            data[list(data.columns[:min(len(data.columns), len(columns))])],
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-0"
        )
    else:
        return html.Div("暂无数据", className="text-muted text-center p-4")

def create_tree_table_section(section: dict, data) -> html.Div:
    """创建树形表格（WBS）"""
    # 这是一个简化的实现
    return html.Div([
        html.P("WBS结构表格", className="text-muted"),
        dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("编码"),
                    html.Th("名称"),
                    html.Th("成本", className="text-end")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td("1.0"),
                    html.Td("一级项目"),
                    html.Td("¥1,000,000", className="text-end")
                ]),
                html.Tr([
                    html.Td("  1.1", className="ps-4"),
                    html.Td("二级子项"),
                    html.Td("¥600,000", className="text-end")
                ]),
                html.Tr([
                    html.Td("    1.1.1", className="ps-5"),
                    html.Td("三级细项"),
                    html.Td("¥300,000", className="text-end")
                ])
            ])
        ], striped=True, hover=True)
    ])

def create_kpi_cards(section: dict, data: dict) -> html.Div:
    """创建KPI卡片"""
    cards = []
    
    for metric in section.get("metrics", []):
        value = data.get(metric["field"], 0)
        target = metric.get("target", 1.0)
        thresholds = metric.get("thresholds", {})
        
        # 判断状态
        if value >= thresholds.get("good", 0.95):
            color = "success"
            icon = "check-circle"
        elif value >= thresholds.get("warning", 0.9):
            color = "warning" 
            icon = "exclamation-triangle"
        else:
            color = "danger"
            icon = "times-circle"
        
        # 格式化值
        if metric.get("format") == "percentage":
            formatted_value = f"{value*100:.1f}%"
            formatted_target = f"{target*100:.0f}%"
        else:
            formatted_value = f"{value:.2f}"
            formatted_target = f"{target:.2f}"
        
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(metric["name"], className="text-muted mb-1"),
                            html.H2(formatted_value, className="mb-0"),
                            html.Small(f"目标: {formatted_target}", className="text-muted")
                        ], width=8),
                        dbc.Col([
                            html.I(className=f"fas fa-{icon} fa-3x", 
                                    style={"color": f"var(--bs-{color})"})
                        ], width=4, className="text-end")
                    ])
                ])
            ], color=color, outline=True)
        ], md=6, className="mb-3")
        
        cards.append(card)
    
    return dbc.Row(cards)

def generate_component_preview(component_type: str, config: dict) -> html.Div:
   """生成组件预览"""
   component_id = str(uuid.uuid4())
   
   # 根据组件类型生成预览
   if component_type == "summary-card":
       return dbc.Card([
           dbc.CardBody([
               html.H6(config.get("title", "汇总卡片"), className="text-muted"),
               html.H3("¥1,234,567", className="mb-0")
           ])
       ], id=component_id)
       
   elif component_type in ["line-chart", "bar-chart", "pie-chart"]:
       return dcc.Graph(
           id=component_id,
           figure={
               "data": [],
               "layout": {
                   "title": config.get("title", "图表"),
                   "height": 300
               }
           }
       )
       
   elif component_type == "data-table":
       return html.Div([
           html.H6(config.get("title", "数据表格")),
           dbc.Table(
               [
                   html.Thead([
                       html.Tr([html.Th("列1"), html.Th("列2"), html.Th("列3")])
                   ]),
                   html.Tbody([
                       html.Tr([html.Td("数据1"), html.Td("数据2"), html.Td("数据3")])
                   ])
               ],
               striped=True,
               bordered=True,
               hover=True
           )
       ], id=component_id)
       
   else:
       return html.Div(
           f"组件类型: {component_type}",
           id=component_id,
           className="border rounded p-3"
       )

def create_component_properties_panel(component_type: str) -> html.Div:
   """根据组件类型创建属性配置面板"""
   
   base_properties = [
       html.H6("基本属性", className="mb-3"),
       dbc.Row([
           dbc.Col([
               dbc.Label("组件标题"),
               dbc.Input(id="component-title", placeholder="输入标题")
           ], width=12)
       ], className="mb-3"),
       
       dbc.Row([
           dbc.Col([
               dbc.Label("宽度"),
               dcc.Slider(
                   id="component-width",
                   min=1,
                   max=12,
                   step=1,
                   marks={i: str(i) for i in range(1, 13)},
                   value=6
               )
           ], width=12)
       ], className="mb-3")
   ]
   
   # 根据组件类型添加特定属性
   specific_properties = []
   
   if component_type in ["line-chart", "bar-chart", "pie-chart", "combo-chart"]:
       specific_properties.extend([
           html.Hr(),
           html.H6("图表配置", className="mb-3"),
           dbc.Row([
               dbc.Col([
                   dbc.Label("数据字段"),
                   dcc.Dropdown(
                       id="chart-data-fields",
                       multi=True,
                       placeholder="选择数据字段"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Label("X轴字段"),
                   dcc.Dropdown(
                       id="chart-x-field",
                       placeholder="选择X轴字段"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Label("Y轴字段"),
                   dcc.Dropdown(
                       id="chart-y-fields",
                       multi=True,
                       placeholder="选择Y轴字段"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Checkbox(
                       id="show-legend",
                       label="显示图例",
                       value=True
                   )
               ])
           ])
       ])
       
   elif component_type in ["data-table", "pivot-table"]:
       specific_properties.extend([
           html.Hr(),
           html.H6("表格配置", className="mb-3"),
           dbc.Row([
               dbc.Col([
                   dbc.Label("显示列"),
                   dcc.Dropdown(
                       id="table-columns",
                       multi=True,
                       placeholder="选择显示的列"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Checkbox(
                       id="show-pagination",
                       label="显示分页",
                       value=True
                   ),
                   dbc.Checkbox(
                       id="enable-sorting",
                       label="启用排序",
                       value=True
                   ),
                   dbc.Checkbox(
                       id="enable-filtering",
                       label="启用筛选",
                       value=True
                   )
               ])
           ])
       ])
       
   elif component_type in ["summary-card", "kpi-card", "metric-card"]:
       specific_properties.extend([
           html.Hr(),
           html.H6("卡片配置", className="mb-3"),
           dbc.Row([
               dbc.Col([
                   dbc.Label("指标字段"),
                   dcc.Dropdown(
                       id="card-metric-field",
                       placeholder="选择指标字段"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Label("聚合方式"),
                   dcc.Dropdown(
                       id="card-aggregation",
                       options=[
                           {"label": "求和", "value": "sum"},
                           {"label": "平均", "value": "avg"},
                           {"label": "计数", "value": "count"},
                           {"label": "最大值", "value": "max"},
                           {"label": "最小值", "value": "min"}
                       ],
                       value="sum"
                   )
               ])
           ], className="mb-3"),
           
           dbc.Row([
               dbc.Col([
                   dbc.Label("格式"),
                   dcc.Dropdown(
                       id="card-format",
                       options=[
                           {"label": "数字", "value": "number"},
                           {"label": "货币", "value": "currency"},
                           {"label": "百分比", "value": "percentage"}
                       ],
                       value="number"
                   )
               ])
           ])
       ])
   
   return html.Div(base_properties + specific_properties)

def get_available_data_fields(selected_sources: list) -> list:
   """获取选中数据源的可用字段"""
   
   # 定义各数据源的字段
   data_fields = {
       "project": [
           {"label": "项目名称", "value": "project_name"},
           {"label": "项目编号", "value": "project_id"},
           {"label": "项目状态", "value": "project_status"},
           {"label": "开始日期", "value": "start_date"},
           {"label": "结束日期", "value": "end_date"},
           {"label": "项目经理", "value": "project_manager"}
       ],
       "cost": [
           {"label": "总成本", "value": "total_cost"},
           {"label": "直接成本", "value": "direct_cost"},
           {"label": "间接成本", "value": "indirect_cost"},
           {"label": "人工成本", "value": "labor_cost"},
           {"label": "材料成本", "value": "material_cost"},
           {"label": "设备成本", "value": "equipment_cost"}
       ],
       "schedule": [
           {"label": "计划进度", "value": "planned_progress"},
           {"label": "实际进度", "value": "actual_progress"},
           {"label": "进度偏差", "value": "schedule_variance"},
           {"label": "关键路径", "value": "critical_path"},
           {"label": "里程碑", "value": "milestones"}
       ],
       "quality": [
           {"label": "质量评分", "value": "quality_score"},
           {"label": "合格率", "value": "pass_rate"},
           {"label": "缺陷数量", "value": "defect_count"},
           {"label": "返工率", "value": "rework_rate"}
       ]
   }
   
   # 合并选中数据源的字段
   available_fields = []
   for source in selected_sources:
       if source in data_fields:
           available_fields.extend(data_fields[source])
   
   return available_fields