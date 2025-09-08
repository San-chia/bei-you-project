# modules/indicator/callbacks.py
from dash import Input, Output, State, callback_context, html, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import json
from decimal import Decimal, ROUND_HALF_UP
from .database import search_indicators, get_indicator_details

import logging


# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def format_number(num):
    """格式化数字为带千位分隔符的字符串"""
    if isinstance(num, str):
        num = float(num)
    num = Decimal(str(num)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    return f"{num:,.2f}"

PRIMARY_COLOR = "#2C3E50"  # 深蓝色作为主色
SECONDARY_COLOR = "#18BC9C"  # 青绿色作为次要色

def register_indicator_callbacks(app):
    """注册指标测算模块的回调函数"""
    
    def debug_callback_context(ctx, inputs=None):
        """调试回调上下文"""
        logger.debug("=== Callback Context ===")
        if ctx.triggered:
            logger.debug(f"Triggered by: {ctx.triggered[0]['prop_id']}")
        if inputs:
            logger.debug(f"Inputs: {inputs}")
        logger.debug("======================")
    
    @app.callback(
        [Output("save-project-modal", "is_open"),
         Output("project-unit-display", "children")],
        [Input("btn-save-project", "n_clicks"),
         Input("btn-cancel-save", "n_clicks"),
         Input("btn-confirm-save", "n_clicks")],
        [State("save-project-modal", "is_open"),
         State("composite-selected-items-table", "data")]
    )
    def toggle_save_project_modal(save_clicks, cancel_clicks, confirm_clicks, is_open, table_data):
        """控制保存项目模态框的显示与隐藏"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "btn-save-project" and table_data:
            # 当点击保存项目按钮时，获取第一个项目的单位作为默认单位
            unit = table_data[0].get("unit", "-") if table_data else "-"
            return True, unit
        elif button_id in ["btn-cancel-save", "btn-confirm-save"]:
            return False, no_update
        
        return is_open, no_update

    @app.callback(
        [Output("save-project-modal", "is_open", allow_duplicate=True),
         Output("save-result-toast", "is_open"),
         Output("save-result-toast", "children"),
         Output("save-result-toast", "color")],
        [Input("btn-confirm-save", "n_clicks")],
        [State("project-name-input", "value"),
         State("project-type-input", "value"),
         State("project-quantity-input", "value"),
         State("project-unit-display", "children"),
         State("normal-days-input", "value"),
         State("modular-days-input", "value"),
         State("project-remarks-input", "value"),
         State("composite-selected-items-table", "data")],  # 添加表格数据作为State
        prevent_initial_call=True
    )
    def save_project_data(n_clicks, 
                         project_name, project_type, project_quantity, 
                         unit, normal_days, modular_days, remarks,
                         table_data):  # 添加table_data参数
        """保存项目信息和参数"""
        if not n_clicks:
            return [no_update, no_update, no_update, no_update]
        
        # 验证必填字段
        if not project_name:
            return [
                no_update,  # 不关闭模态框
                True,  # 显示toast
                "请输入项目名称",  # toast内容
                "danger"  # toast颜色
            ]
        
        if not table_data:
            return [
                no_update,  # 不关闭模态框
                True,  # 显示toast
                "请先添加项目构件",  # toast内容
                "warning"  # toast颜色
            ]
            
        try:
            from .database import save_project, save_parameters
            
            # 1. 保存项目信息
            project_data = {
                "project_name": project_name,
                "project_type": project_type or "未分类",
                "project_quantity": float(project_quantity) if project_quantity else 0,
                "unit": unit,
                "normal_construction_days": int(normal_days) if normal_days else 0,
                "modular_construction_days": int(modular_days) if modular_days else 0,
                "remarks": remarks or ""
            }
            
            project_id = save_project(project_data)
            if not project_id:
                logger.error("项目保存失败")
                return [
                    no_update,  # 不关闭模态框
                    True,  # 显示toast
                    "项目信息保存失败，请检查数据库连接",  # toast内容
                    "danger"  # toast颜色
                ]

            # 2. 保存参数信息
            if table_data:
                parameters_data = []
                for item in table_data:
                    parameter = {
                        'name': item['name'],
                        'category': item.get('category', ''),
                        'unit': item['unit'],
                        'quantity': float(item['quantity']),
                        'unit_prices': {
                            # 这里我们只有模块化的单价，将其同时用作直接施工单价
                            'direct_labor': float(item['unit_price']) / 3,  # 假设各占三分之一
                            'direct_material': float(item['unit_price']) / 3,
                            'direct_machinery': float(item['unit_price']) / 3,
                            'labor': float(item['unit_price']) / 3,
                            'material': float(item['unit_price']) / 3,
                            'machinery': float(item['unit_price']) / 3
                        }
                    }
                    parameters_data.append(parameter)

                # 保存参数
                success = save_parameters(project_id, project_name, parameters_data)
                if not success:
                    logger.error("参数保存失败")
                    return [
                        no_update,  # 不关闭模态框
                        True,  # 显示toast
                        "项目参数保存失败，请重试",  # toast内容
                        "danger"  # toast颜色
                    ]

            # 所有保存成功
            return [
                False,  # 关闭模态框
                True,   # 显示toast
                f"项目 '{project_name}' 保存成功！项目ID: {project_id}",  # toast内容
                "success"  # toast颜色
            ]
                
        except ValueError as ve:
            logger.error(f"数据格式错误: {str(ve)}")
            return [
                no_update,  # 不关闭模态框
                True,  # 显示toast
                f"数据格式错误: {str(ve)}",  # toast内容
                "warning"  # toast颜色
            ]
        except Exception as e:
            logger.error(f"保存项目失败: {str(e)}")
            return [
                no_update,  # 不关闭模态框
                True,  # 显示toast
                f"保存失败: {str(e)}",  # toast内容
                "danger"  # toast颜色
            ]
    
    # Toast消息自动关闭回调
    @app.callback(
        Output("save-result-toast", "is_open", allow_duplicate=True),
        [Input("save-result-toast", "is_open")],
        prevent_initial_call=True
    )
    def auto_close_toast(is_open):
        """Toast消息4秒后自动关闭"""
        if is_open:
            # 这里不需要额外逻辑，Toast组件的duration参数会自动处理
            return is_open
        return False
    
    @app.callback(
        [Output('search-results', 'children'),
         Output('search-results', 'style')],
        [Input('indicator-search', 'value'),
         Input('construction-mode-select', 'value')],
        prevent_initial_call=True
    )
    def update_search_results(search_term, mode):
        """更新搜索结果"""
        if not search_term or len(search_term) < 1:
            return None, {'display': 'none'}
            
        results = search_indicators(mode, search_term)
        
        if not results:
            return html.Div(
                "没有找到匹配的指标",
                className="p-2 text-muted"
            ), {'display': 'block'}
            
        result_items = []
        for item in results:
            result_items.append(
                dbc.Button(
                    [
                        html.Div(
                            item['name'],  # parameter_category
                            className="text-start fw-bold"
                        ),
                        html.Small([
                            f"编码: {item['code']} | ",
                            f"工程名称: {item['project_name']} | ",
                            f"单位: {item['unit']} | ",
                            f"单价: ¥{item['total_price']:.2f}"
                        ], className="text-muted d-block")
                    ],
                    id={'type': 'search-result-item', 'index': item['code']},
                    className="text-start w-100 mb-1 p-2",
                    color="light",
                    style={'border': 'none', 'borderBottom': '1px solid #eee'}
                )
            )
        
        return html.Div(result_items), {'display': 'block'}
    
    @app.callback(
        [Output('selected-indicator', 'children'),
         Output('indicator-search', 'value'),
         Output('unit-display', 'children'),
         Output('price-details', 'style'),
         Output('labor-unit-price', 'children'),
         Output('material-unit-price', 'children'),
         Output('machinery-unit-price', 'children'),
         Output('total-unit-price', 'children')],
        [Input({'type': 'search-result-item', 'index': ALL}, 'n_clicks')],
        [State('construction-mode-select', 'value')],
        prevent_initial_call=True
    )
    def update_selected_indicator(n_clicks_list, mode):
        """更新选中的指标"""
        ctx = callback_context
        if not ctx.triggered:
            return None, "", "-", {'display': 'none'}, "", "", "", ""
            
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        indicator_id = button_id['index']
        
        # 获取指标详情
        indicator = get_indicator_details(mode, indicator_id)
        if not indicator:
            return None, "", "-", {'display': 'none'}, "", "", "", ""
            
        # 获取单价信息
        labor_price = indicator['unit_prices']['labor']
        material_price = indicator['unit_prices']['material']
        machinery_price = indicator['unit_prices']['machinery']
        total_price = labor_price + material_price + machinery_price
            
        selected_display = html.Div([
            html.Div(
                indicator['parameter_category'],
                style={'fontWeight': 'bold'}
            ),
            html.Small([
                f"编码: {indicator['code']} | ",
                f"工程名称: {indicator['name']} | ",
                f"单价: ¥{total_price:.2f}"
            ], className="text-muted")
        ])
        
        # 格式化价格显示
        def format_price(price):
            return f"¥ {price:.2f}"
        
        return (
            selected_display,           # 选中指标显示
            "",                        # 清空搜索框
            indicator['unit'],              # 单位显示
            {'display': 'block'},      # 显示价格详情区域
            format_price(labor_price),     # 人工单价
            format_price(material_price),  # 材料单价
            format_price(machinery_price), # 机械单价
            format_price(total_price)      # 总单价
        )

    @app.callback(
        [
            # 成本结果卡片输出
            Output('cost-result-material', 'children'),
            Output('cost-result-labor', 'children'),
            Output('cost-result-machinery', 'children'),
            Output('cost-result-total', 'children'),
            # 占比输出
            Output('cost-percent-material', 'children'),
            Output('cost-percent-labor', 'children'),
            Output('cost-percent-machinery', 'children'),
            # 图表输出
            Output('cost-breakdown-chart', 'figure')
        ],
        [
            Input('btn-base-calculate', 'n_clicks')
        ],
        [
            State('construction-mode-select', 'value'),
            State('selected-indicator', 'children'),
            State('input-number', 'value'),
            State('material-unit-price', 'children'),
            State('labor-unit-price', 'children'),
            State('machinery-unit-price', 'children')
        ],
        prevent_initial_call=True
    )
    def calculate_costs(n_clicks, mode, selected_indicator, quantity, material_price, labor_price, machinery_price):
        """计算成本并更新显示"""
        if not n_clicks or not selected_indicator or not quantity:
            return no_update

        # 解析单价（去除"¥ "前缀和逗号）
        def parse_price(price_str):
            return float(price_str.replace('¥ ', '').replace(',', ''))

        # 计算各项成本
        material_cost = parse_price(material_price) * quantity
        labor_cost = parse_price(labor_price) * quantity
        machinery_cost = parse_price(machinery_price) * quantity
        total_cost = material_cost + labor_cost + machinery_cost

        # 计算占比
        if total_cost > 0:
            material_percent = (material_cost / total_cost) * 100
            labor_percent = (labor_cost / total_cost) * 100
            machinery_percent = (machinery_cost / total_cost) * 100
        else:
            material_percent = labor_percent = machinery_percent = 0

        # 更新饼图
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=['材料成本', '人工成本', '设备成本'],
                    values=[material_cost, labor_cost, machinery_cost],
                    hole=.3,
                    marker=dict(
                        colors=[PRIMARY_COLOR, SECONDARY_COLOR, '#F39C12']
                    )
                )
            ],
            layout=go.Layout(
                margin=dict(l=20, r=20, t=0, b=0),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                )
            )
        )

        return (
            format_number(material_cost),   # 材料成本
            format_number(labor_cost),      # 人工成本
            format_number(machinery_cost),  # 机械成本
            format_number(total_cost),      # 总成本
            f"占比 {material_percent:.1f}%",    # 材料占比
            f"占比 {labor_percent:.1f}%",       # 人工占比
            f"占比 {machinery_percent:.1f}%",   # 机械占比
            fig                             # 更新后的图表
        )
        
    # === 复合指标回调函数 ===
    @app.callback(
        [Output('composite-search-results', 'children'),
         Output('composite-search-results', 'style')],
        [Input('composite-indicator-search', 'value'),
         Input('composite-indicator-search', 'n_submit'),
         Input('composite-construction-mode-select', 'value')],
        prevent_initial_call=True
    )
    def update_composite_search_results(search_term, n_submit, mode):
        """更新复合指标搜索结果"""
        ctx = callback_context
        debug_callback_context(ctx, {'search_term': search_term, 'n_submit': n_submit, 'mode': mode})
        
        if not ctx.triggered or not search_term:
            logger.debug("No search term provided")
            return None, {'display': 'none'}
            
        try:
            # 使用相同的搜索函数
            results = search_indicators(mode, search_term)
            logger.debug(f"Search results: {len(results) if results else 0} items found")
            
            if not results:
                return html.Div("未找到匹配的指标", className="p-2 text-muted"), {'display': 'block'}
                
            # 创建搜索结果列表
            result_items = []
            for item in results:
                total_price = item['total_price']
                result_items.append(
                    dbc.Button(
                        [
                            html.Div(
                                item['name'],
                                style={'fontWeight': 'bold'}
                            ),
                            html.Small(
                                f"编码: {item['code']} | 单位: {item['unit']} | 单价: ¥{total_price:.2f}",
                                className="text-muted"
                            )
                        ],
                        id={'type': 'composite-search-result', 'index': item['code']},
                        color="light",
                        className="text-start w-100 mb-1"
                    )
                )
                
            return html.Div(result_items), {'display': 'block'}
            
        except Exception as e:
            logger.error(f"Error in composite search: {str(e)}")
            return html.Div("搜索过程中发生错误", className="p-2 text-danger"), {'display': 'block'}
            
    @app.callback(
        [Output('composite-selected-items-table', 'data'),
         Output('composite-total', 'children')],
        [Input({'type': 'composite-search-result', 'index': ALL}, 'n_clicks'),
         Input('composite-selected-items-table', 'data_timestamp')],
        [State('composite-selected-items-table', 'data'),
         State('composite-construction-mode-select', 'value')]
    )
    def update_composite_items(clicks, timestamp, current_data, mode):
        """更新已选项目列表"""
        ctx = callback_context
        debug_callback_context(ctx)
        
        if not ctx.triggered:
            return [], "¥ 0.00"
            
        try:
            # 如果是通过点击搜索结果添加项目
            if ctx.triggered[0]['prop_id'].startswith('{'):
                clicked_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
                indicator_id = clicked_id['index']
                
                # 获取指标详情
                indicator = get_indicator_details(mode, indicator_id)
                logger.debug(f"Selected indicator details: {indicator}")
                
                if indicator:
                    total_price = sum(indicator['unit_prices'].values())
                    new_item = {
                        'id': indicator['code'],
                        'name': indicator['name'],
                        'category': indicator['parameter_category'],
                        'unit': indicator['unit'],
                        'quantity': 1,
                        'unit_price': total_price,
                        'subtotal': total_price
                    }
                    
                    # 检查是否已存在
                    if current_data:
                        for existing in current_data:
                            if existing['id'] == indicator['code']:
                                return current_data, f"¥ {sum(item['subtotal'] for item in current_data):,.2f}"
                        current_data.append(new_item)
                    else:
                        current_data = [new_item]
                        
            # 计算总价
            if current_data:
                total = sum(float(item['quantity']) * float(item['unit_price']) for item in current_data)
                return current_data, f"¥ {total:,.2f}"
                
            return [], "¥ 0.00"
            
        except Exception as e:
            logger.error(f"Error updating composite items: {str(e)}")
            return current_data or [], "¥ 0.00"

    # === 复合指标计算按钮回调函数 ===
    @app.callback(
        [
            # 成本结果卡片输出
            Output('cost-result-material', 'children', allow_duplicate=True),
            Output('cost-result-labor', 'children', allow_duplicate=True),
            Output('cost-result-machinery', 'children', allow_duplicate=True),
            Output('cost-result-total', 'children', allow_duplicate=True),
            # 占比输出
            Output('cost-percent-material', 'children', allow_duplicate=True),
            Output('cost-percent-labor', 'children', allow_duplicate=True),
            Output('cost-percent-machinery', 'children', allow_duplicate=True),
            # 图表输出
            Output('cost-breakdown-chart', 'figure', allow_duplicate=True)
        ],
        [
            Input('btn-composite-calculate', 'n_clicks')
        ],
        [
            State('composite-selected-items-table', 'data'),
            State('composite-construction-mode-select', 'value')
        ],
        prevent_initial_call=True
    )
    def calculate_composite_costs(n_clicks, table_data, mode):
        """计算复合指标成本并更新显示"""
        if not n_clicks or not table_data:
            return no_update
        
        # 初始化成本变量
        total_material_cost = 0
        total_labor_cost = 0
        total_machinery_cost = 0
        
        # 根据工程类型设置单价比例
        if mode == 'steel_cage':  # 钢筋笼模式
            labor_unit_price = 1094.076898		
            material_unit_price = 639.0420914
            machinery_unit_price = 559.4738383
            total_unit_price = labor_unit_price + material_unit_price + machinery_unit_price
        elif mode == 'steel_lining':  # 钢衬里模式
            labor_unit_price = 310.2688249
            material_unit_price = 145.2414511
            machinery_unit_price = 61.40375302
            total_unit_price = labor_unit_price + material_unit_price + machinery_unit_price
        else:
            # 默认使用钢筋笼价格
            labor_unit_price = 1094.076898
            material_unit_price = 639.0420914
            machinery_unit_price = 559.4738383
            total_unit_price = labor_unit_price + material_unit_price + machinery_unit_price
        
        # 计算各个构件的成本
        for item in table_data:
            quantity = float(item['quantity'])
            unit_price = float(item['unit_price'])
            
            # 按照单价比例分配各项成本
            item_total = quantity * unit_price
            item_labor_cost = item_total * (labor_unit_price / total_unit_price)
            item_material_cost = item_total * (material_unit_price / total_unit_price)
            item_machinery_cost = item_total * (machinery_unit_price / total_unit_price)
            
            total_labor_cost += item_labor_cost
            total_material_cost += item_material_cost
            total_machinery_cost += item_machinery_cost
        
        total_cost = total_material_cost + total_labor_cost + total_machinery_cost
        
        # 计算占比
        if total_cost > 0:
            material_percent = (total_material_cost / total_cost) * 100
            labor_percent = (total_labor_cost / total_cost) * 100
            machinery_percent = (total_machinery_cost / total_cost) * 100
        else:
            material_percent = labor_percent = machinery_percent = 0
        
        # 更新饼图
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=['材料成本', '人工成本', '设备成本'],
                    values=[total_material_cost, total_labor_cost, total_machinery_cost],
                    hole=.3,
                    marker=dict(
                        colors=[PRIMARY_COLOR, SECONDARY_COLOR, '#F39C12']
                    )
                )
            ],
            layout=go.Layout(
                margin=dict(l=20, r=20, t=0, b=0),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                )
            )
        )
        
        return (
            format_number(total_material_cost),   # 材料成本
            format_number(total_labor_cost),      # 人工成本
            format_number(total_machinery_cost),  # 机械成本
            format_number(total_cost),            # 总成本
            f"占比 {material_percent:.1f}%",    # 材料占比
            f"占比 {labor_percent:.1f}%",       # 人工占比
            f"占比 {machinery_percent:.1f}%",   # 机械占比
            fig                             # 更新后的图表
        )

    # === 综合指标测算回调函数 ===
    @app.callback(
        [
            # 成本结果卡片输出
            Output('cost-result-material', 'children', allow_duplicate=True),
            Output('cost-result-labor', 'children', allow_duplicate=True),
            Output('cost-result-machinery', 'children', allow_duplicate=True),
            Output('cost-result-total', 'children', allow_duplicate=True),
            # 占比输出
            Output('cost-percent-material', 'children', allow_duplicate=True),
            Output('cost-percent-labor', 'children', allow_duplicate=True),
            Output('cost-percent-machinery', 'children', allow_duplicate=True),
            # 图表输出
            Output('cost-breakdown-chart', 'figure', allow_duplicate=True)
        ],
        [
            Input('btn-overall-calculate', 'n_clicks')
        ],
        [
            State('dropdown-project-type', 'value'),
            State('project-size', 'value')
        ],
        prevent_initial_call=True
    )
    def calculate_overall_costs(n_clicks, project_type, project_size):
        """计算综合指标成本并更新显示"""
        if not n_clicks or not project_size:
            return no_update
        
        # 根据工程类型设置单价
        if project_type == 'steel_cage':  # 钢筋笼模式
            labor_unit_price = 1094.076898
            material_unit_price = 639.0420914
            machinery_unit_price = 559.4738383
        elif project_type == 'steel_lining':  # 钢衬里模式
            labor_unit_price = 310.2688249
            material_unit_price = 145.2414511
            machinery_unit_price = 61.40375302
        else:
            # 默认使用钢筋笼价格
            labor_unit_price = 1094.076898
            material_unit_price = 639.0420914
            machinery_unit_price = 559.4738383

        # 计算各项成本（工程规模 × 单价）
        material_cost = material_unit_price * project_size
        labor_cost = labor_unit_price * project_size
        machinery_cost = machinery_unit_price * project_size
        total_cost = material_cost + labor_cost + machinery_cost
        
        # 计算占比
        if total_cost > 0:
            material_percent = (material_cost / total_cost) * 100
            labor_percent = (labor_cost / total_cost) * 100
            machinery_percent = (machinery_cost / total_cost) * 100
        else:
            material_percent = labor_percent = machinery_percent = 0
        
        # 更新饼图
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=['材料成本', '人工成本', '设备成本'],
                    values=[material_cost, labor_cost, machinery_cost],
                    hole=.3,
                    marker=dict(
                        colors=[PRIMARY_COLOR, SECONDARY_COLOR, '#F39C12']
                    )
                )
            ],
            layout=go.Layout(
                margin=dict(l=20, r=20, t=0, b=0),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                )
            )
        )
        
        return (
            format_number(material_cost),   # 材料成本
            format_number(labor_cost),      # 人工成本
            format_number(machinery_cost),  # 机械成本
            format_number(total_cost),      # 总成本
            f"占比 {material_percent:.1f}%",    # 材料占比
            f"占比 {labor_percent:.1f}%",       # 人工占比
            f"占比 {machinery_percent:.1f}%",   # 机械占比
            fig                             # 更新后的图表
        )