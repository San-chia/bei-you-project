# modules/report_management/layout.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import PRIMARY_COLOR # 假设您在config.py中定义了颜色

def create_report_management_layout():
    """创建报表管理模块的布局"""
    report_templates = [
        {"label": "选择报表模板...", "value": ""},
        {"label": "概算书", "value": "estimation_summary"},
        {"label": "构件成本清单", "value": "component_cost_list"},
        {"label": "标准化造价分析报告", "value": "standard_cost_analysis"},
        {"label": "成本构成分析报告", "value": "cost_composition_analysis"},
        {"label": "AI预测与实际造价误差分析报告", "value": "ai_error_analysis"},
        {"label": "敏感性分析报表", "value": "sensitivity_analysis"},
        {"label": "造价总览报表", "value": "overall_cost_overview"},
        {"label": "历史对比报表", "value": "historical_comparison"},
        # 可以根据需求添加更多模板
    ]

    export_formats = [
        {"label": "Word (.docx)", "value": "docx"},
        {"label": "Excel (.xlsx)", "value": "xlsx"},
        {"label": "PDF (.pdf)", "value": "pdf"},
    ]

    layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("报表管理", className="mb-4", style={'color': PRIMARY_COLOR}), width=12)
        ]),

        dbc.Row([
            # 左侧：模板选择和参数配置
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("报表配置"),
                    dbc.CardBody([
                        dbc.Label("选择报表模板:", html_for="report-template-dropdown"),
                        dcc.Dropdown(
                            id="report-template-dropdown",
                            options=report_templates,
                            value="",
                            clearable=False,
                            className="mb-3",
                        ),
                        html.Div(id="report-customization-area", children=[
                            # 此处可以根据选择的模板动态添加参数配置选项
                            dbc.Label("自定义报表名称 (可选):", html_for="report-custom-name"),
                            dbc.Input(id="report-custom-name", placeholder="例如：项目A-概算书-2025Q1", type="text", className="mb-3"),

                            dbc.Label("选择导出格式:", html_for="report-export-format-checklist"),
                            dbc.Checklist(
                                options=export_formats,
                                value=["pdf"], # 默认选中PDF
                                id="report-export-format-checklist",
                                inline=True,
                                className="mb-3"
                            ),
                        ]),
                        dbc.Button("生成报表", id="report-generate-button", color="primary", className="mt-3", n_clicks=0),
                    ])
                ])
            ], md=4),

            # 右侧：报表预览和操作
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("报表预览与导出"),
                    dbc.CardBody([
                        html.Div(id="report-preview-area", children=[
                            html.P("请先选择模板并生成报表以进行预览。", className="text-muted")
                            # 实际预览区域会比较复杂，这里仅作占位
                            # 可以考虑用 dcc.Loading 包裹一个 iframe 或者一个图像组件来显示预览
                        ], style={'border': '1px dashed #ccc', 'padding': '20px', 'minHeight': '300px', 'textAlign': 'center'}),
                        
                        dbc.Row([
                            dbc.Col(dbc.Button("在线编辑", id="report-edit-button", color="secondary", className="mt-3", disabled=True, n_clicks=0), width="auto"),
                            dbc.Col(dbc.Button("下载报表", id="report-download-button", color="success", className="mt-3", disabled=True, n_clicks=0), width="auto"),
                            dcc.Download(id="download-report-data"), # 用于触发下载
                        ], className="mt-3 justify-content-end")
                    ])
                ])
            ], md=8)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("可用报表模板库说明"),
                    dbc.CardBody([
                        html.P("系统内置多种技经专业常用的报表模板，确保数据展示方式、计算逻辑、统计口径等要素与技经专业工作规范保持一致。"),
                        html.Ul([
                            html.Li("概算书、构件成本清单等基础文件报表。"),
                            html.Li("标准化造价分析报告、成本构成分析、AI预测与实际造价误差分析报告。"),
                            html.Li("敏感性分析报表、造价总览报表、历史对比报表等。"),
                            html.Li("支持模板的定制化配置和报表样式的灵活调整。"),
                        ])
                    ])
                ])
            ], width=12, className="mt-4")
        ])

    ], fluid=True, className="mt-4")
    return layout