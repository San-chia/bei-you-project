import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from dash import Input, Output, State, dcc
# def create_cost_comparison_table(cost_data):
#     """创建成本比较表格"""
#     # 准备表格数据
#     table_data = [
#         {"项目": "人工费", "直接施工": cost_data["直接施工"]["人工费"], "模块化施工": cost_data["模块化施工"]["人工费"]},
#         {"项目": "材料费", "直接施工": cost_data["直接施工"]["材料费"], "模块化施工": cost_data["模块化施工"]["材料费"]},
#         {"项目": "机械费", "直接施工": cost_data["直接施工"]["机械费"], "模块化施工": cost_data["模块化施工"]["机械费"]},
#         {"项目": "间接费用", "直接施工": cost_data["直接施工"]["间接费用"], "模块化施工": cost_data["模块化施工"]["间接费用"]},
#         {"项目": "总计", "直接施工": cost_data["直接施工"]["总计"], "模块化施工": cost_data["模块化施工"]["总计"]}
#     ]
#     print(table_data)
#     # 计算节约成本和百分比
#     savings = cost_data["模块化施工"]["总计"] - cost_data["直接施工"]["总计"]
#     savings_percent = (savings / cost_data["直接施工"]["总计"]) * 100 if cost_data["直接施工"]["总计"] > 0 else 0
    
#     # 创建表格
#     comparison_table = dash_table.DataTable(
#         id='cost-comparison-table',
#         columns=[
#             {"name": "项目", "id": "项目"},
#             {"name": "直接施工 (元)", "id": "直接施工", "type": "numeric", "format": {"specifier": ",.2f"}},
#             {"name": "模块化施工 (元)", "id": "模块化施工", "type": "numeric", "format": {"specifier": ",.2f"}}
#         ],
#         data=table_data,
#         style_table={'overflowX': 'auto'},
#         style_cell={'textAlign': 'right', 'padding': '10px'},
#         style_header={
#             'backgroundColor': '#f0f8ff',
#             'fontWeight': 'bold',
#             'textAlign': 'center'
#         },
#         style_data_conditional=[
#             {
#                 'if': {'row_index': 3},  # 总计行
#                 'fontWeight': 'bold',
#                 'backgroundColor': '#e6f7ff'
#             }
#         ]
#     )
    
#     # 创建结果卡片
#     result_card = dbc.Card([
#         dbc.CardHeader(html.H4("施工成本比较分析", className="text-center")),
#         dbc.CardBody([
#             html.Div([
#                 html.H5("成本总览", className="mb-3"),
#                 comparison_table,
#                 html.Div([
#                     html.H5(f"成本增加: {savings:,.2f} 元 (成本增幅：{savings_percent:.1f}%)", 
#                             className="mt-3 text-success" if savings > 0 else "mt-3 text-danger")
#                 ], className="text-center mt-3")
#             ])
#         ])
#     ], className="mb-4")
    
#     return result_card

def create_cost_comparison_table(cost_data, project_id=None, construction_mode=None):
    """创建成本比较表格"""
    # 准备表格数据
    table_data = [
        {"项目": "人工费", "直接施工": cost_data["直接施工"]["人工费"], "模块化施工": cost_data["模块化施工"]["人工费"]},
        {"项目": "材料费", "直接施工": cost_data["直接施工"]["材料费"], "模块化施工": cost_data["模块化施工"]["材料费"]},
        {"项目": "机械费", "直接施工": cost_data["直接施工"]["机械费"], "模块化施工": cost_data["模块化施工"]["机械费"]},
        {"项目": "间接费用", "直接施工": cost_data["直接施工"]["间接费用"], "模块化施工": cost_data["模块化施工"]["间接费用"]},
        {"项目": "总计", "直接施工": cost_data["直接施工"]["总计"], "模块化施工": cost_data["模块化施工"]["总计"]}
    ]
    
    # 计算节约成本和百分比
    savings = cost_data["模块化施工"]["总计"] - cost_data["直接施工"]["总计"]
    print(savings)
    savings_percent = (savings / cost_data["直接施工"]["总计"]) * 100 if cost_data["直接施工"]["总计"] > 0 else 0
    
    # 创建表格 - 添加可编辑单元格
    comparison_table = dash_table.DataTable(
        id='cost-comparison-table',
        columns=[
            {"name": "项目", "id": "项目"},
            {"name": "直接施工 (元)", "id": "直接施工", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工 (元)", "id": "模块化施工", "type": "numeric", "format": {"specifier": ",.2f"}}
        ],
        data=table_data,
        editable=True,  # 允许表格可编辑
        cell_selectable=True,
        column_selectable=False,
        row_selectable=False,
        # 只允许间接费用行可编辑
        style_data_conditional=[
            {
                'if': {'row_index': 3},  # 间接费用行
                'backgroundColor': '#e6f7ff',
                'fontWeight': 'bold'
            },
            {
                'if': {'row_index': 4},  # 总计行
                'backgroundColor': '#f0f8ff',
                'fontWeight': 'bold'
            },
            {
                'if': {'row_index': 4, 'column_id': '直接施工'},  # 总计行的直接施工列
                'backgroundColor': '#f0f8ff',
                'fontWeight': 'bold',
                'editable': False  # 总计列不可编辑
            },
            {
                'if': {'row_index': 4, 'column_id': '模块化施工'},  # 总计行的模块化施工列
                'backgroundColor': '#f0f8ff',
                'fontWeight': 'bold',
                'editable': False  # 总计列不可编辑
            },
            {
                'if': {'row_index': [0, 1, 2], 'column_id': '直接施工'},  # 人工费、材料费、机械费行的直接施工列
                'editable': False
            },
            {
                'if': {'row_index': [0, 1, 2], 'column_id': '模块化施工'},  # 人工费、材料费、机械费行的模块化施工列
                'editable': False
            }
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'right', 'padding': '10px'},
        style_header={
            'backgroundColor': '#f0f8ff',
            'fontWeight': 'bold',
            'textAlign': 'center'
        }
    )
    
    # 创建保存按钮
    save_button = dbc.Button(
        "保存结果", 
        id="save-cost-result-btn", 
        color="primary", 
        className="me-2 mb-3",
        style={"position": "absolute", "left": "20px", "top": "50%"}
    )
    # 在创建dcc.Store时设置初始值
    stores = [
        dcc.Store(id="initial-cost-data", data=cost_data),
        dcc.Store(id="current-project-id", data=project_id),  # 设置项目ID
        dcc.Store(id="current-construction-mode", data=construction_mode)  # 设置施工模式
    ]

    # 创建结果卡片
    result_card = dbc.Card([
        dbc.CardHeader(html.H4("施工成本比较分析", className="text-center")),
        dbc.CardBody([
            html.Div([
                html.Div([
                    save_button,  # 添加保存按钮在左侧
                    html.Div(id="save-status", className="mt-2")  # 显示保存状态
                ], style={"float": "left", "width": "120px"}),
                html.Div([
                    html.H5("成本总览", className="mb-3"),
                    comparison_table,
                    html.Div(id="cost-savings-display", className="text-center mt-3"),
                    html.H5(
                        f"成本{'增加' if savings > 0 else '减少'}: {abs(savings):,.2f} 元 (成本{'增幅' if savings > 0 else '降幅'}：{abs(savings_percent):.1f}%)",
                        className=f"mt-3 {'text-success' if savings < 0 else 'text-danger'}"
                    )
                ], style={"marginLeft": "130px"}),
                html.Div(stores, style={"display": "none"})
            ], style={"position": "relative"})
        ])
    ], className="mb-4")
    
    return result_card

def create_detailed_cost_table(cost_data):
    """创建详细成本表格"""
    details = cost_data["明细"]
    
    # 准备详细数据
    rows = []
    for item in details:
        rows.append({
            "参数类别": item["参数类别"],
            "工程参数": item["参数"],
            "数量": item["数量"],
            "直接施工人工费": item["直接施工"]["人工费"],
            "直接施工材料费": item["直接施工"]["材料费"],
            "直接施工机械费": item["直接施工"]["机械费"],
            "直接施工总计": item["直接施工"]["总计"],
            "模块化施工人工费": item["模块化施工"]["人工费"],
            "模块化施工材料费": item["模块化施工"]["材料费"],
            "模块化施工机械费": item["模块化施工"]["机械费"],
            "模块化施工总计": item["模块化施工"]["总计"]
        })
    
    # 创建表格
    detail_table = dash_table.DataTable(
        id='cost-detail-table',
        columns=[
            {"name": "参数类别", "id": "参数类别"},
            {"name": "工程参数", "id": "工程参数"},
            {"name": "数量", "id": "数量", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "直接施工人工费", "id": "直接施工人工费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "直接施工材料费", "id": "直接施工材料费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "直接施工机械费", "id": "直接施工机械费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "直接施工总计", "id": "直接施工总计", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工人工费", "id": "模块化施工人工费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工材料费", "id": "模块化施工材料费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工机械费", "id": "模块化施工机械费", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工总计", "id": "模块化施工总计", "type": "numeric", "format": {"specifier": ",.2f"}}
        ],
        data=rows,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'right',
            'minWidth': '100px',
            'maxWidth': '200px',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': '#f0f8ff',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'column_id': col},
                'fontWeight': 'bold'
            } for col in ['直接施工总计', '模块化施工总计']
        ]
    )
    
    # 创建结果卡片
    detail_card = dbc.Card([
        dbc.CardHeader(html.H4("工程参数成本明细", className="text-center")),
        dbc.CardBody([
            detail_table
        ])
    ])
    
    return detail_card

def create_result_layout(cost_data,project_id, construction_mode):
    """创建结果布局"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_cost_comparison_table(cost_data,project_id, construction_mode)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                create_detailed_cost_table(cost_data)
            ], width=12)
        ])
    ])

def create_result_layout2( cost_data,mode_id,project_type ):
    """创建结果布局"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_cost_comparison_table(cost_data,mode_id, project_type)
            ], width=12)
        ])
    ])