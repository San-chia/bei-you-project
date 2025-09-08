# modules/data/layout.py
import dash_bootstrap_components as dbc
from dash import html, dash_table
from utils.components import create_icon_button
from config import PRIMARY_COLOR

def create_indicator_management_card():
    """创建指标管理卡片"""
    return html.Div([
        html.Div([
            html.H5("多层次数据指标管理", style={'margin': '0', 'fontWeight': 'normal'})
        ], style={'padding': '15px 20px', 'borderBottom': '1px solid #eee'}),

        html.Div([
            html.Div([
                create_icon_button("fas fa-database", "基础指标库", "btn-basic-indicator")
            ]),

            html.Div([
                create_icon_button("fas fa-database", "复合指标库", "btn-composite-indicator")
            ]),

            html.Div([
                create_icon_button("fas fa-database", "综合指标库", "btn-comprehensive-indicator")
            ])
        ], style={'padding': '20px'})
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '5px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'height': '100%',
        'width': '48%', 
        'boxSizing': 'border-box'
    })

def create_algorithm_management_card():
    """创建算法管理卡片"""
    return html.Div([
        html.Div([
            html.H5("智能分析算法管理", style={'margin': '0', 'fontWeight': 'normal'})
        ], style={'padding': '15px 20px', 'borderBottom': '1px solid #eee'}),
        
        html.Div([
            html.Div([
                create_icon_button("fas fa-cog", "算法模型配置", "btn-algorithm-config")
            ]),
            
            html.Div([
                create_icon_button("fas fa-chart-line", "算法参数管理", "btn-model-training")
            ]),
            
            html.Div([
                create_icon_button("fas fa-chart-pie", "模型性能对比", "btn-model-comparison")
            ])
        ], style={'padding': '20px'})
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '5px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'height': '100%',
        'width': '48%',
        'boxSizing': 'border-box'
    })

def create_data_table_card():
    """创建数据表格卡片"""
    return html.Div([
        html.Div([
            html.H5("上传文件内容", style={'margin': '0', 'fontWeight': 'normal', 'textAlign': 'center'})
        ], style={'padding': '15px 20px', 'borderBottom': '1px solid #eee'}),

        html.Div([
            dash_table.DataTable(
                id="table-data",
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                page_size=10
            )
        ], style={'padding': '20px', 'overflowY': 'auto', 'maxHeight': '400px'})
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '5px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'height': 'auto',
        'margin': '20px auto',
        'width': '100%',
        'maxWidth': '1200px',
        'boxSizing': 'border-box'
    })

def create_data_layout():
    """创建数据管理模块的布局"""
    return html.Div([
        # 主要内容区域
        html.Div([
            # 左侧卡片容器 - 多层次数据指标管理
            create_indicator_management_card(),
            
            # 右侧卡片容器 - 智能分析算法管理
            create_algorithm_management_card()
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '0 0 20px 0'}),
        
        # 上传文件显示表格区域
        create_data_table_card()
    ])