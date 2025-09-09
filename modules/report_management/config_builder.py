# modules/report_management/config_builder.py
"""报表配置组件生成器"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Dict, Any, List
from .templates import ChartType, DataSourceType, StatDimension, CHART_TYPE_CONFIG

class ConfigBuilder:
    """配置界面构建器"""
    
    @staticmethod
    def build_section_config(section: Dict[str, Any], section_idx: int) -> dbc.Card:
        """构建单个section的配置卡片"""
        config_elements = []
        
        # Section标题和开关
        config_elements.append(
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id={"type": "section-enable", "index": section_idx},
                            label=section["name"],
                            value=True,
                            className="mb-0"
                        )
                    ], width=8),
                    dbc.Col([
                        dbc.Badge(
                            section["type"],
                            color="primary",
                            className="float-end"
                        )
                    ], width=4)
                ])
            ])
        )
        
        # 配置选项
        config_body = []
        for option_key, option_config in section.get("config_options", {}).items():
            element = ConfigBuilder._build_config_element(
                option_key, option_config, section_idx
            )
            if element:
                config_body.append(element)
        
        config_elements.append(
            dbc.Collapse(
                dbc.CardBody(config_body),
                id={"type": "section-collapse", "index": section_idx},
                is_open=True
            )
        )
        
        return dbc.Card(config_elements, className="mb-3")
    
    @staticmethod
    def _build_config_element(option_key: str, option_config: Dict, section_idx: int) -> html.Div:
        """构建单个配置元素"""
        element_id = {
            "type": "section-config",
            "section": section_idx,
            "option": option_key
        }
        
        label = dbc.Label(option_config["label"])
        
        if option_config["type"] == "select":
            # 下拉选择
            options = ConfigBuilder._format_options(option_config["options"])
            input_element = dcc.Dropdown(
                id=element_id,
                options=options,
                value=option_config.get("default"),
                clearable=False
            )
            
        elif option_config["type"] == "multi_select":
            # 多选
            options = ConfigBuilder._format_options(option_config["options"])
            input_element = dcc.Dropdown(
                id=element_id,
                options=options,
                value=option_config.get("default", []),
                multi=True
            )
            
        elif option_config["type"] == "checkbox":
            # 复选框
            input_element = dbc.Checkbox(
                id=element_id,
                value=option_config.get("default", False),
                className="mt-2"
            )
            
        elif option_config["type"] == "number":
            # 数字输入
            input_element = dbc.Input(
                id=element_id,
                type="number",
                value=option_config.get("default", 0),
                min=option_config.get("min"),
                max=option_config.get("max")
            )
            
        elif option_config["type"] == "date_range":
            # 日期范围
            input_element = dcc.DatePickerRange(
                id=element_id,
                start_date=option_config.get("default_start"),
                end_date=option_config.get("default_end"),
                display_format="YYYY-MM-DD"
            )
        else:
            return None
        
        return html.Div([label, input_element], className="mb-3")
    
    @staticmethod
    def _format_options(options: List) -> List[Dict]:
        """格式化选项列表"""
        formatted = []
        for opt in options:
            if isinstance(opt, dict):
                # 如果值是枚举，转换为字符串
                value = opt["value"]
                if hasattr(value, 'name'):
                    opt["value"] = value.name
                formatted.append({"label": opt["label"], "value": opt["value"]})
            elif hasattr(opt, 'value'):  # Enum
                formatted.append({"label": opt.value, "value": opt.name})
            else:
                formatted.append({"label": str(opt), "value": opt})
        return formatted
    
    @staticmethod
    def build_data_source_selector(template: Dict[str, Any]) -> dbc.Card:
        """构建数据源选择器"""
        available_sources = template.get("data_sources", {}).get("available", [])
        default_sources = template.get("data_sources", {}).get("default", [])
        
        options = [
            {"label": source.value, "value": source.name} 
            for source in available_sources
        ]
        
        return dbc.Card([
            dbc.CardHeader("数据源配置"),
            dbc.CardBody([
                dbc.Label("选择数据源"),
                dcc.Dropdown(
                    id="data-source-selector",
                    options=options,
                    value=[s.name for s in default_sources],
                    multi=True
                ),
                dbc.FormText("选择报表所需的数据源，系统将自动关联相关数据表")
            ])
        ], className="mb-3")
    
    @staticmethod
    def build_export_options(template: Dict[str, Any]) -> dbc.Card:
        """构建导出选项"""
        export_options = template.get("export_options", {})
        
        elements = [
            dbc.Label("导出格式"),
            dbc.Checklist(
                id="export-formats",
                options=[
                    {"label": "PDF", "value": "pdf"},
                    {"label": "Excel", "value": "xlsx"},
                    {"label": "Word", "value": "docx"}
                ],
                value=export_options.get("formats", ["pdf"]),
                inline=True,
                className="mb-3"
            )
        ]
        
        # 其他导出选项
        for key, config in export_options.items():
            if isinstance(config, dict) and "type" in config:
                if config["type"] == "checkbox":
                    elements.append(
                        dbc.Checkbox(
                            id=f"export-option-{key}",
                            label=config["label"],
                            value=config.get("default", False)
                        )
                    )
        
        return dbc.Card([
            dbc.CardHeader("导出设置"),
            dbc.CardBody(elements)
        ], className="mb-3")