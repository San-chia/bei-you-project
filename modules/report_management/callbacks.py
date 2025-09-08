# modules/report_management/callbacks.py
from dash.dependencies import Input, Output, State
from dash import html, no_update, ctx
import dash_bootstrap_components as dbc

def register_report_management_callbacks(app):
    @app.callback(
        [Output("report-preview-area", "children"),
         Output("report-edit-button", "disabled"),
         Output("report-download-button", "disabled")],
        [Input("report-generate-button", "n_clicks")],
        [State("report-template-dropdown", "value"),
         State("report-custom-name", "value"),
         State("report-export-format-checklist", "value")]
    )
    def generate_report_preview(n_clicks, template_value, custom_name, export_formats):
        if n_clicks == 0 or not template_value:
            return html.P("请先选择模板并点击“生成报表”以进行预览。", className="text-muted"), True, True

        # ---- 实际功能未实现 ----
        # 这里应该调用后端逻辑来生成报表数据和预览
        # 我们仅模拟一个简单的预览
        
        template_label_map = {
            "estimation_summary": "概算书",
            "component_cost_list": "构件成本清单",
            "standard_cost_analysis": "标准化造价分析报告",
            "cost_composition_analysis": "成本构成分析报告",
            "ai_error_analysis": "AI预测与实际造价误差分析报告",
            "sensitivity_analysis": "敏感性分析报表",
            "overall_cost_overview": "造价总览报表",
            "historical_comparison": "历史对比报表",
        }
        selected_template_label = template_label_map.get(template_value, "未知模板")
        report_title = custom_name if custom_name else f"生成的《{selected_template_label}》"
        
        formats_str = ", ".join(export_formats) if export_formats else "未选择格式"

        preview_content = html.Div([
            html.H5(f"报表预览：{report_title}"),
            html.P(f"模板类型：{selected_template_label}"),
            html.P(f"选择的导出格式：{formats_str}"),
            html.Hr(),
            html.Em("（此处为模拟预览区域，实际报表内容将在此展示）"),
            html.Br(),
            html.Img(src="/assets/placeholder_report.png", style={"maxWidth": "100%", "maxHeight": "400px", "marginTop": "10px"}) # 假设有一个占位图片
        ])
        
        # 假设生成成功，则启用编辑和下载按钮
        return preview_content, False, False

    # ---- 实际下载逻辑未实现 ----
    # @app.callback(
    #     Output("download-report-data", "data"),
    #     [Input("report-download-button", "n_clicks")],
    #     [State("report-template-dropdown", "value"), # 需要更多状态来确定下载内容
    #      State("report-export-format-checklist", "value")] # 需要导出格式
    # )
    # def download_report(n_clicks, template, formats):
    #     if n_clicks > 0 and template and formats:
    #         # 此处应根据 template 和 formats 生成相应的文件内容并返回
    #         # 例如: dcc.send_data_frame(df.to_excel, "my_report.xlsx", sheet_name="Sheet_1")
    #         # 或者 dcc.send_file("path/to/generated/report.pdf")
    #         
    #         # 模拟下载一个文本文件
    #         file_content = f"这是模拟生成的报表: {template}, 格式: {', '.join(formats)}"
    #         # 确定文件名和类型
    #         filename = f"simulated_report_{template}.txt" # 简化为txt
    #         if "pdf" in formats:
    #             filename = f"simulated_report_{template}.pdf"
    #         elif "xlsx" in formats:
    #             filename = f"simulated_report_{template}.xlsx"
    #         elif "docx" in formats:
    #             filename = f"simulated_report_{template}.docx"
    #         
    #         return dict(content=file_content, filename=filename, type="text/plain") # 或 application/pdf 等
    #     return no_update
    
    @app.callback(
        Output("report-customization-area", "style"),
        Input("report-template-dropdown", "value")
    )
    def toggle_customization_area(template_value):
        if template_value:
            return {"display": "block"}
        return {"display": "none"}


    print("报表管理模块回调已注册")