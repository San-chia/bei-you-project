# utils/components.py
# 通用UI组件
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_icon_button(icon_class, button_text, button_id, color="light", style=None):
    """创建带图标的按钮"""
    default_style = {'textAlign': 'center', 'padding': '15px', 'marginBottom': '15px'}
    if style:
        default_style.update(style)
    
    return dbc.Button([
        html.I(className=icon_class, style={'marginRight': '10px'}),
        html.Span(button_text)
    ], id=button_id, color=color, className="w-100", style=default_style)

def create_card_header(title, subtitle=None):
    """创建卡片标题组件"""
    if subtitle:
        return [
            html.H4(title, className="card-title"),
            html.P(subtitle, className="card-subtitle text-muted mb-3")
        ]
    else:
        return html.H4(title, className="card-title")

def create_card(title, content, subtitle=None, id=None, className="mb-4 shadow-sm"):
    """创建一个通用卡片组件"""
    header = create_card_header(title, subtitle)
    
    return dbc.Card(
        dbc.CardBody([
            header,
            html.Div(content)
        ]),
        id=id,
        className=className
    )

def create_button_group(buttons, style=None):
    """创建按钮组"""
    default_style = {"display": "flex", "marginTop": "15px"}
    if style:
        default_style.update(style)
    
    return html.Div(buttons, style=default_style)

def create_section_title(title, style=None):
    """创建带有下划线的区域标题"""
    default_style = {'padding': '10px 0', 'borderBottom': '1px solid #eee', 'marginBottom': '15px'}
    if style:
        default_style.update(style)
    
    return html.H5(title, style=default_style)

def create_label_value_pair(label, value, label_width="100px"):
    """创建标签-值对，用于详情展示"""
    return html.Div([
        html.Label(f"{label}：", style={'fontWeight': 'bold', 'display': 'inline-block', 'width': label_width}),
        html.Span(value, style={'display': 'inline-block'})
    ], style={'marginBottom': '10px'})

def create_info_badge(text, color="light", className="me-2"):
    """创建信息徽章"""
    return dbc.Badge(text, color=color, className=className)