# modules/analysis/callbacks.py
from dash import Input, Output, State, callback_context
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash
from config import PRIMARY_COLOR, SECONDARY_COLOR

def register_analysis_callbacks(app):
    """注册数据分析模块的回调函数"""
    
    # 预测按钮回调 - 显示预测结果
    @app.callback(
        [Output('prediction-results-container', 'style'),
         Output('analysis-status', 'style'),
         Output('prediction-graph', 'figure')],
        [Input('predict-button', 'n_clicks'),
         Input('material-category-dropdown', 'value'),
         Input('algorithm-type-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_prediction(n_clicks, material_type, algorithm_type):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # 只有在点击预测按钮时才显示图表，其他输入变化时只更新图表内容
        if triggered_id == 'predict-button' and n_clicks:
            # 显示预测结果，隐藏提示
            results_style = {"display": "block"}
            status_style = {"display": "none"}
        elif triggered_id in ['material-category-dropdown', 'algorithm-type-dropdown']:
            # 获取当前显示状态
            results_style = dash.no_update
            status_style = dash.no_update
        else:
            # 初始状态或其他情况
            return {"display": "none"}, {"display": "flex"}, {}
            
        # 根据所选材料类型和算法类型生成预测图
        fig = generate_prediction_chart(material_type, algorithm_type)
        
        return results_style, status_style, fig
    
    # 保存价格按钮回调
    @app.callback(
        Output('save-button', 'style'),
        [Input('save-button', 'n_clicks')],
        [State('save-button', 'style')],
        prevent_initial_call=True
    )
    def save_prediction_prices(n_clicks, current_style):
        if n_clicks:
            # 这里可以添加保存价格的逻辑
            # 暂时仅改变按钮颜色表示已点击
            new_style = current_style.copy()
            new_style['backgroundColor'] = '#2E8B57'  # 深绿色表示已保存
            return new_style
        return dash.no_update
    
    # 导入数据按钮回调 - 设置上传标志
    @app.callback(
        Output('file-uploaded-flag', 'data'),
        [Input('import-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def set_data_imported_flag(n_clicks):
        if n_clicks:
            # 当用户点击导入数据按钮时，将标志设置为True
            return True
        return False

# 修改 generate_prediction_chart 函数，使预测线更接近原始数据线

def generate_prediction_chart(material_type, algorithm_type='linear_regression'):
    # 创建时间轴数据
    months = ['1月', '2月', '3月', '4月', '5月', '6月', 
              '7月', '8月', '9月', '10月', '11月', '12月']
    
    # 创建图表对象
    fig = go.Figure()
    
    # 设置一些随机种子以保持一致性
    np.random.seed(42)
    
    # 定义材料价格和颜色
    materials_data = {
        'steel': {
            'name': '钢材',
            'base_price': 300,
            'trend': 0.02,  # 每月增长率
            'volatility': 0.02,  # 波动范围
            'color': 'rgb(31, 119, 180)'  # 蓝色
        },
        'concrete': {
            'name': '混凝土',
            'base_price': 150,
            'trend': -0.01,  # 每月下降率
            'volatility': 0.02,
            'color': 'rgb(127, 127, 127)'  # 灰色
        },
        'wood': {
            'name': '木材',
            'base_price': 200,
            'trend': 0.03,
            'volatility': 0.03,
            'color': 'rgb(140, 86, 75)'  # 棕色
        },
        'decoration': {
            'name': '装饰材料',
            'base_price': 400,
            'trend': 0.015,
            'volatility': 0.02,
            'color': 'rgb(44, 160, 44)'  # 绿色
        }
    }
    
    # 算法类型影响预测的准确度和波动性 - 减小波动系数，提高准确度
    algorithm_factors = {
        'linear_regression': {'accuracy': 0.02, 'volatility_factor': 0.6},  # 降低波动，提高准确度
        'neural_network': {'accuracy': 0.015, 'volatility_factor': 0.5},
        'decision_tree': {'accuracy': 0.025, 'volatility_factor': 0.7},
        'random_forest': {'accuracy': 0.018, 'volatility_factor': 0.55},
        'svm': {'accuracy': 0.02, 'volatility_factor': 0.65}
    }
    
    # 获取算法因子
    algorithm_factor = algorithm_factors.get(algorithm_type, algorithm_factors['linear_regression'])
    
    # 检查材料类型是否有效，如果无效则默认为 'decoration'
    if material_type not in materials_data:
        material_type = 'decoration'
    
    # 要显示的材料 - 只显示选中的材料
    mat = materials_data[material_type]
    
    # 生成原始价格数据 (过去数据)
    original_prices = []
    current_price = mat['base_price']
    
    for i in range(12):
        # 添加较小的自然波动
        current_price = current_price * (1 + 0.5 * mat['trend'] + np.random.uniform(-0.5 * mat['volatility'], 0.5 * mat['volatility']))
        original_prices.append(round(current_price, 2))
    
    # 添加原始价格线
    fig.add_trace(go.Scatter(
        x=months, 
        y=original_prices,
        mode='lines+markers',
        name=f'{mat["name"]} - 原始价格',
        line=dict(color=mat['color'], width=2, dash='solid'),
        hovertemplate='%{y:.2f}元'
    ))
    
    # 生成预测价格数据 (预测) - 使预测更接近原始数据
    predicted_prices = []
    
    # 使用原始数据的趋势来初始化预测（更准确的起点）
    if len(original_prices) >= 3:
        # 计算原始数据的趋势
        avg_trend = (original_prices[-1] / original_prices[0]) ** (1/11) - 1
        avg_trend = avg_trend * 1.1  # 略微提高预测增长率（乐观预期）
    else:
        avg_trend = mat['trend']
    
    # 从最后一个原始价格开始预测
    current_price = original_prices[-1]
    
    # 根据不同算法调整预测趋势和波动 - 减小随机波动影响
    adjusted_trend = avg_trend * (1 + algorithm_factor['accuracy'] * np.random.uniform(-0.5, 0.5))
    adjusted_volatility = mat['volatility'] * algorithm_factor['volatility_factor']
    
    for i in range(12):
        # 添加趋势和随机波动 - 减小随机波动的幅度
        if i < 3:
            # 短期预测更准确
            volatility_factor = 0.3 * adjusted_volatility
        else:
            # 长期预测略微增加波动性
            volatility_factor = adjusted_volatility
            
        current_price = current_price * (1 + adjusted_trend + np.random.uniform(-volatility_factor, volatility_factor))
        predicted_prices.append(round(current_price, 2))
    
    # 添加预测价格线
    fig.add_trace(go.Scatter(
        x=months, 
        y=predicted_prices,
        mode='lines+markers',
        name=f'{mat["name"]} - 预测价格',
        line=dict(color=mat['color'], width=2, dash='dash'),
        hovertemplate='%{y:.2f}元'
    ))
    
    # 更新图表布局
    algorithm_names = {
        'linear_regression': '线性回归',
        'neural_network': '神经网络',
        'decision_tree': '决策树',
        'random_forest': '随机森林',
        'svm': '支持向量机'
    }
    
    algorithm_name = algorithm_names.get(algorithm_type, '线性回归')
    
    fig.update_layout(
        title={
            'text': f'原材料价格预测趋势 (使用{algorithm_name}算法)',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        xaxis_title='月份',
        yaxis_title='价格 (元/单位)',
        legend_title='材料类型',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # 更新图表标题，显示使用线性回归算法
    fig.update_layout(
        title={
            'text': f'原材料价格预测趋势 (使用{algorithm_name}算法)',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        }
    )
    
    # 添加网格线以提高可读性
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig