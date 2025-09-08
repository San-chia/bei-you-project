import dash
from dash import Input, Output, State, callback_context, ALL, no_update,html,dash_table,MATCH
import plotly.graph_objects as go
from config import PRIMARY_COLOR, SECONDARY_COLOR
import json
import uuid
from dash.exceptions import PreventUpdate
from .modals import create_parameter_form,create_c403_c409_content,create_c404_content,create_common_content,create_custom_params_table,create_params_table,create_custom_mode_detail_modal,create_parameter_form_row
from .metal_config import DEFAULT_PARAM_ID,param_types,units
from .results import create_result_layout,create_result_layout2
from .db_connection import calculate_cost,save_project,save_custom_parameters,init_db,get_mode_details_from_database,get_parameter_suggestions,get_connection,get_connection_diy,calculate_cost_diy,save_calculation_result,calculate_steel_lining_cost_fixed,debug_steel_lining_database,delete_custom_project,get_project_basic_info
from .layout import (update_construction_mode_layout, load_custom_modes, create_custom_modes_row,create_custom_modes_row_with_pagination,create_pagination_controls)
import mysql.connector
import time
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime
import copy
import math 


from .translation import (
    reverse_translate_table_name, 
    reverse_translate_field_name,
    translate_field_name,
    translate_table_name
)
# MySQL数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名
    'charset': 'utf8mb4',
    'autocommit': False
}

# 在 modules/Construction_Mode/callbacks.py 中添加/修改以下函数

def create_model_modal_callback(app):
    """创建模态窗口回调函数 - 修正版本"""
    
    # 钢筋笼模态窗口回调
    @app.callback(
        Output("steel-cage-parameter-modal", "is_open"),
        [Input("btn-mode-1", "n_clicks"),
         Input("steel-cage-modal-close-btn", "n_clicks"),
         Input("steel-cage-modal-confirm-btn", "n_clicks")],
        [State("steel-cage-parameter-modal", "is_open")],
        prevent_initial_call=True  # 重要：防止初始调用
    )
    def toggle_steel_cage_modal(open_clicks, close_clicks, confirm_clicks, is_open):
        print(f"1窗口回调触发: open={open_clicks}, close={close_clicks}, confirm={confirm_clicks}, current_state={is_open}")
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "btn-mode-1" and open_clicks:
            return True
        elif trigger_id in ["steel-cage-modal-close-btn"]:
            return False
        
        return is_open

    # 钢筋笼+钢覆面模态窗口回调
    @app.callback(
        Output("steel-cage-plus-modal", "is_open"),
        [Input("btn-mode-2", "n_clicks"),
         Input("steel-cage-plus-modal-cancel", "n_clicks"),
         Input("steel-cage-plus-modal-submit", "n_clicks")],
        [State("steel-cage-plus-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_steel_cage_plus_modal(open_clicks, close_clicks, confirm_clicks, is_open):
        print(f"2窗口回调触发: open={open_clicks}, close={close_clicks}, confirm={confirm_clicks}, current_state={is_open}")
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "btn-mode-2" and open_clicks:
            return True
        elif trigger_id in ["steel-cage-plus-modal-cancel"]:
            return False
        
        return is_open

    # 叠合板模态窗口回调
    @app.callback(
        Output("modular_composite_plate_modal", "is_open"),
        [Input("btn-mode-103", "n_clicks"),
         Input("modular-composite-plate-modal-cancel", "n_clicks"),
         Input("modular-composite-plate-modal-submit", "n_clicks")],
        [State("modular_composite_plate_modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_composite_plate_modal(open_clicks, close_clicks, confirm_clicks, is_open):
        print(f"3窗口回调触发: open={open_clicks}, close={close_clicks}, confirm={confirm_clicks}, current_state={is_open}")
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(trigger_id)
        if trigger_id == "btn-mode-103" and open_clicks:
            return True
        elif trigger_id in ["modular-composite-plate-modal-cancel"]:
            return False
        else:
            return False


    # 管廊模态窗口回调
    @app.callback(
        Output("tunnel-modal", "is_open"),
        [Input("btn-mode-4", "n_clicks"),
         Input("tunnel-modal-cancel1", "n_clicks"),
         Input("tunnel-modal-cancel2", "n_clicks"),
         Input("tunnel-modal-submit1", "n_clicks"),
         Input("tunnel-modal-submit2", "n_clicks")],
        [State("tunnel-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_tunnel_modal(open_clicks, close_clicks1, close_clicks2, confirm_clicks1, confirm_clicks2, is_open):
        print(f"4窗口回调触发: open={open_clicks}, close={close_clicks1}, confirm={confirm_clicks1}, current_state={is_open}")
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "btn-mode-4" and open_clicks:
            return True
        elif trigger_id in ["tunnel-modal-cancel1", "tunnel-modal-cancel2"]:
            return False
        
        return is_open

    # 钢衬里模态窗口回调 - 修正版本
    @app.callback(
        Output("steel-lining-parameter-modal", "is_open"),
        [Input("btn-mode-5", "n_clicks"),
         Input("steel-lining-modal-close-btn", "n_clicks"),
         Input("steel-lining-modal-confirm-btn", "n_clicks")],
        [State("steel-lining-parameter-modal", "is_open")],
        prevent_initial_call=True  # 确保防止初始调用
    )
    def toggle_steel_lining_modal(btn_mode_5_clicks, close_clicks, confirm_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # 只有明确的按钮点击才触发
        if prop_id == "btn-mode-5" and btn_mode_5_clicks:
            print("打开钢衬里模态窗口")
            return True
        elif prop_id == "steel-lining-modal-close-btn" and close_clicks:
            print("关闭钢衬里模态窗口")
            return False
        elif prop_id == "steel-lining-modal-confirm-btn" and confirm_clicks:
            print("钢衬里计算完成，保持模态窗口打开以显示结果")
            return True
        
        # 默认返回当前状态
        raise dash.exceptions.PreventUpdate

    # 自定义模式模态窗口回调
    @app.callback(
        Output('diy-custom-param-modal', 'is_open'),
        [Input('diy-open-modal-button', 'n_clicks'),
         Input('diy-cancel-button', 'n_clicks'),
         Input('diy-confirm-button', 'n_clicks')],
        [State('diy-custom-param-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_diy_modal(open_clicks, cancel_clicks, confirm_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'diy-open-modal-button' and open_clicks:
            return True
        elif trigger_id in ['diy-cancel-button', 'diy-confirm-button'] and (cancel_clicks or confirm_clicks):
            return False
        
        raise dash.exceptions.PreventUpdate
    


    @app.callback(
    Output('add-param-trigger', 'data'),
    Input('add-param-button', 'n_clicks'),
    prevent_initial_call=True
)
    def trigger_add_param(n_clicks):
        if n_clicks:
            return n_clicks
        raise PreventUpdate

# 响应添加参数触发器
    @app.callback(
    Output('param-ids', 'data'),
    Input('add-param-trigger', 'data'),
    State('param-ids', 'data'),
    prevent_initial_call=True
)
    def add_new_parameter(trigger, param_ids):
        if trigger:
            new_param_id = str(uuid.uuid4())
            return param_ids + [new_param_id]
        return param_ids

# 处理删除参数
    @app.callback(
    [Output('parameters-container', 'children', allow_duplicate=True),
     Output('param-ids', 'data', allow_duplicate=True)],
    Input({'type': 'delete-param', 'index': ALL}, 'n_clicks'),
    State('param-ids', 'data'),
    prevent_initial_call=True
)
    def handle_delete_param(delete_clicks, param_ids):
        ctx = dash.callback_context
        if not ctx.triggered or not any(click for click in delete_clicks if click):
            raise PreventUpdate
        
        # 找出哪个删除按钮被点击了
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        param_to_delete = json.loads(button_id)['index']
        
        # 从参数列表中移除
        updated_param_ids = [pid for pid in param_ids if pid != param_to_delete]
        
        # 重新生成参数表单
        updated_forms = [create_parameter_form(pid, i==0) for i, pid in enumerate(updated_param_ids)]
        
        return updated_forms, updated_param_ids
    
    
    @app.callback(
    Output('param-ids', 'data', allow_duplicate=True),
    Input('diy-open-modal-button', 'n_clicks'),
    State('param-ids', 'data'),
    prevent_initial_call=True
)
    def reset_params_when_open(n_clicks, param_ids):
        if n_clicks and (not param_ids or len(param_ids) == 0):
            return [DEFAULT_PARAM_ID]
        return param_ids
    @app.callback(
    [Output("c403-c409-content", "style"),
     Output("c404-content", "style"),
     Output("tunnel-result-container", "children",allow_duplicate=True),
     Output("tunnel-modal-submit1","style"),
     Output("tunnel-modal-submit2","style")],
    Input("tunnel-type", "value"),
    prevent_initial_call = True
)
    def update_content_visibility(selected_type):
        c403_style = {"display": "block" if selected_type == "c403_c409" else "none"}
        c404_style = {"display": "block" if selected_type == "c404" else "none"}
        submit1_style = {"display": "block" if selected_type == "c403_c409" else "none"}
        submit2_style = {"display": "block" if selected_type == "c404" else "none"}
    
    # 返回空内容以清除结果容器
        return c403_style, c404_style, [], submit1_style, submit2_style

    #钢筋笼施工模式计算回调
    @app.callback(
        Output("steel-cage-result-container", "children"),
        Input("steel-cage-modal-confirm-btn", "n_clicks"),
        [State("cage-steel-q235b钢筋(现浇构件钢筋)", "value"),
         State("cage-steel-水平钢筋绑扎", "value"),
         State("cage-steel-竖向钢筋绑扎", "value"),
         State("cage-steel-拉筋绑扎", "value"),
         State("cage-steel-预留水平钢筋绑扎", "value"),
         State("cage-connection-直螺纹钢筋套筒(φ16-φ40)", "value"),
         State("cage-connection-锥套锁紧套筒及配套材料", "value"),
         State("cage-connection-q345预埋铁件(钢筋锚固板)", "value"),
         State("cage-connection-模块竖向钢筋锥套连接", "value"),
         State("cage-connection-措施短柱预埋件安装及调整", "value"),
         State("cage-connection-模块起吊、落位、短柱连接", "value"),
         State("cage-tool-q235b零星钢结构(盖板等工装)", "value"),
         State("cage-tool-立柱(hw150*150)", "value"),
         State("cage-tool-立柱(hw100*100)", "value"),
         State("cage-tool-钢筋限位工装安装及调整", "value"),
         State("cage-tool-l型钢筋", "value"),
         State("cage-tool-\"j\"钢筋", "value"),
         State("cage-tool-剪刀撑", "value"),
         State("cage-tool-u型卡", "value"),
         State("cage-tool-双u型卡", "value"),
         State("cage-tool-短柱(hw150*150)", "value"),
         State("cage-tool-预埋件安装", "value"),
         State("cage-auxiliary-定型围栏", "value"),
         State("cage-auxiliary-模板支设", "value"),
         State("cage-auxiliary-c25混凝土", "value"),
         State("cage-auxiliary-铁件", "value"),
         State("cage-auxiliary-电焊条", "value"),
         State("cage-auxiliary-单层彩钢板", "value"),
         State("cage-equipment-螺栓套丝机(φ39)", "value"),
         State("cage-equipment-砂轮切割机(500)", "value"),
         State("cage-equipment-自升式塔式起重机(1500knm)", "value"),
         State("cage-equipment-重型塔吊", "value"),
         State("cage-equipment-汽车吊(80t)", "value"),
         State("cage-equipment-汽车吊(25t)", "value"),
         State("cage-equipment-吊装索具", "value"),
         State("cage-equipment-压制钢丝绳（a68-6*36-7500cm）", "value"),
         State("cage-equipment-压制钢丝绳（a52-6*36-7407cm）", "value"),
         State("cage-equipment-压制钢丝绳（a36-6*36-1500cm）", "value"),
         State("cage-equipment-压制钢丝绳（a68-6*36-9447cm）", "value"),
         State("cage-equipment-压制钢丝绳（φ52-6*36-8678cm）", "value"),
         State("cage-equipment-花篮螺栓-jw3128", "value"),
         State("cage-equipment-花篮螺栓-jw3319", "value"),
         State("cage-equipment-花篮螺栓-jw3409", "value"),
         State("cage-equipment-卸扣-17t", "value"),
         State("cage-equipment-卸扣-30t", "value"),
         State("cage-equipment-卸扣-55t", "value"),
         State("cage-other-模块吊装工装设计费", "value"),
         State("cage-other-无损检测", "value"),
         State("cage-other-钢结构验收", "value"),
         State("cage-other-钢筋预埋件验收", "value"),
         State("cage-others-间接施工费（直接施工）", "value"),
         State("cage-others-间接施工费（模块化施工）", "value"),
         
         
         
        ]
    )
    def calculate_steel_cage_cost(n_clicks, *params):
        if not n_clicks:
            raise PreventUpdate
        
        indirect_costs = {
                "直接施工间接费": float(params[-2]) if params[-2] else 0,
                "模块化施工间接费": float(params[-1]) if params[-1] else 0
            }
            
            # 剔除最后两个参数
        main_params = params[:-2]
        print(indirect_costs)
        # 参数标签和值的映射
        param_labels = [
            " Q235B钢筋(现浇构件钢筋) ",
            " 水平钢筋绑扎 ",
            " 竖向钢筋绑扎 ",
            " 拉筋绑扎 ",
            " 预留水平钢筋绑扎 ",
            " 直螺纹钢筋套筒(Φ16-Φ40) ",
            " 锥套锁紧套筒 ",
            " Q345预埋铁件(钢筋锚固板) ",
            " 模块竖向钢筋锥套连接 ",
            " 措施短柱预埋件安装及调整 ",
            " 模块起吊、落位、短柱连接 ",
            " Q235B零星钢结构(盖板等工装) ",
            " 立柱(HW150*150) ",
            " 立柱(HW100*100) ",
            " 钢筋限位工装安装及调整 ",
            "L型钢筋 ",
            "\"J\"钢筋 ",
            "剪刀撑 ",
            "U型卡 ",
            "双U型卡 ",
            "短柱(HW150*150) ",
            "预埋件安装 ",
            "定型围栏安拆 ",
            "模板支设 ",
            "C25混凝土 ",
            "铁件 ",
            "电焊条 ",
            "单层彩钢板 ",
            "螺栓套丝机(φ39) ",
            "砂轮切割机(500) ",
            "自升式塔式起重机(1500KNm) ",
            "重型塔吊 ",
            "汽车吊(80t) ",
            "汽车吊(25t) ",
            "吊装索具 ",
            "压制钢丝绳（A68 6*36 7.500m）",
            "压制钢丝绳（A52 6*36 7.407m）",
            "压制钢丝绳（A36 6*36 1.500m）",
            "压制钢丝绳（A68 6*36 9.447M）",
            "压制钢丝绳（φ52 6*36 8.678m）",
            "花篮螺栓  (JW3128-16.78T-1156.7±304.8-UU) ",
            "花篮螺栓  (JW3319-32T-1127.5±152.5-UU) ",
            "花篮螺栓  (JW3409-50T-1100±300-UU) ",
            " 卸扣 (17T) ",
            " 卸扣 (30T) ",
            " 卸扣 (55T) ",
            " 模块吊装工装设计费 ",
            " 无损检测 ",
            " 钢结构验收 ",
            " 钢筋预埋件验收 ",

        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                # 尝试转换为浮点数
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                # 如果转换失败则设为0
                params_dict[label] = 0
        
        # 计算成本
        cost_data = calculate_cost(" 钢筋笼施工模式 ", params_dict,indirect_costs)
        project_id = "steel-cage-mode"  # 这里可以替换为实际的项目ID
        construction_mode = " 钢筋笼施工模式 "
        # 返回结果布局
        return create_result_layout(cost_data,project_id, construction_mode)
    #钢筋笼+钢覆面施工模式计算回调
    @app.callback(
        Output("steel-cage-plus-result-container", "children"),
        Input("steel-cage-plus-modal-submit", "n_clicks"),
        [State("cage-steel-plus-q235b钢筋(现浇构件钢筋)", "value"),
         State("cage-steel-plus-水平钢筋绑扎", "value"),
         State("cage-steel-plus-竖向钢筋绑扎", "value"),
         State("cage-steel-plus-拉筋绑扎", "value"),
         State("cage-steel-plus-预留水平钢筋绑扎", "value"),
         State("cage-connection-plus-直螺纹钢筋套筒(φ16-φ40)", "value"),
         State("cage-connection-plus-锥套锁紧套筒及配套材料", "value"),
         State("cage-connection-plus-q345预埋铁件(钢筋锚固板)", "value"),
         State("cage-connection-plus-模块竖向钢筋锥套连接", "value"),
         State("cage-connection-plus-措施短柱预埋件安装及调整", "value"),
         State("cage-connection-plus-模块起吊、落位、短柱连接", "value"),
         State("cage-tool-plus-q235b零星钢结构(盖板等工装)", "value"),
         State("cage-tool-plus-立柱(hw150*150)", "value"),
         State("cage-tool-plus-立柱(hw100*100)", "value"),
         State("cage-tool-plus-钢筋限位工装安装及调整", "value"),
         State("cage-tool-plus-l型钢筋", "value"),
         State("cage-tool-plus-\"j\"钢筋", "value"),
         State("cage-tool-plus-剪刀撑", "value"),
         State("cage-tool-plus-u型卡", "value"),
         State("cage-tool-plus-双u型卡", "value"),
         State("cage-tool-plus-短柱(hw150*150)", "value"),
         State("cage-tool-plus-预埋件安装", "value"),
         State("cage-auxiliary-plus-定型围栏", "value"),
         State("cage-auxiliary-plus-模板支设", "value"),
         State("cage-auxiliary-plus-c25混凝土", "value"),
         State("cage-auxiliary-plus-铁件", "value"),
         State("cage-auxiliary-plus-电焊条", "value"),
         State("cage-auxiliary-plus-单层彩钢板", "value"),
         State("cage-equipment-plus-螺栓套丝机(φ39)", "value"),
         State("cage-equipment-plus-砂轮切割机(500)", "value"),
         State("cage-equipment-plus-自升式塔式起重机(1500knm)", "value"),
         State("cage-equipment-plus-重型塔吊", "value"),
         State("cage-equipment-plus-汽车吊(80t)", "value"),
         State("cage-equipment-plus-汽车吊(25t)", "value"),
         State("cage-equipment-plus-吊装索具", "value"),
         State("cage-equipment-plus-压制钢丝绳（a68-6*36-7500cm）", "value"),
         State("cage-equipment-plus-压制钢丝绳（a52-6*36-7407cm）", "value"),
         State("cage-equipment-plus-压制钢丝绳（a36-6*36-1500cm）", "value"),
         State("cage-equipment-plus-压制钢丝绳（a68-6*36-9447cm）", "value"),
         State("cage-equipment-plus-压制钢丝绳（φ52-6*36-8678cm）", "value"),
         State("cage-equipment-plus-花篮螺栓-jw3128", "value"),
         State("cage-equipment-plus-花篮螺栓-jw3319", "value"),
         State("cage-equipment-plus-花篮螺栓-jw3409", "value"),
         State("cage-equipment-plus-卸扣-17t", "value"),
         State("cage-equipment-plus-卸扣-30t", "value"),
         State("cage-equipment-plus-卸扣-55t", "value"),
         State("cage-other-plus-模块吊装工装设计费", "value"),
         State("cage-other-plus-无损检测", "value"),
         State("cage-other-plus-钢结构验收", "value"),
         State("cage-other-plus-钢筋预埋件验收", "value"),
         State("connection-plus-单侧钢覆面安装加固+埋件焊接材料+镶入件焊接材料", "value"),
         State("connection-plus-通常设备室钢覆面及预留钢覆面组队焊接", "value"),
         State("cover-plus-单侧钢覆面埋件临时安装", "value"),
         State("cover-plus-另一侧钢覆面埋件临时安装", "value"),
         State("cover-plus-钢覆面后台制作", "value"),
         State("embed-plus-不锈钢埋件后台制作", "value"),
         State("embed-plus-碳钢埋件后台制作", "value"),
         State("embed-plus-套管、镶入件后台制作", "value"),
         State("cage-plus-others-间接施工费（直接施工）", "value"),
         State("cage-plus-others-间接施工费（模块化施工）", "value"),
         
         
         
        ]
    )
    def calculate_steel_cage_plus_cost(n_clicks, *params):
        if not n_clicks:
            raise PreventUpdate
        
        indirect_costs = {
                "直接施工间接费": float(params[-2]) if params[-2] else 0,
                "模块化施工间接费": float(params[-1]) if params[-1] else 0
            }
            
            # 剔除最后两个参数
        main_params = params[:-2]
        
        # 参数标签和值的映射
        param_labels = [
            " Q235B钢筋(现浇构件钢筋) ",
            " 水平钢筋绑扎 ",
            " 竖向钢筋绑扎 ",
            " 拉筋绑扎 ",
            " 预留水平钢筋绑扎 ",
            " 直螺纹钢筋套筒(Φ16-Φ40) ",
            " 锥套锁紧套筒 ",
            " Q345预埋铁件(钢筋锚固板) ",
            " 模块竖向钢筋锥套连接 ",
            " 措施短柱预埋件安装及调整 ",
            " 模块起吊、落位、短柱连接 ",
            " Q235B零星钢结构(盖板等工装) ",
            " 立柱(HW150*150) ",
            " 立柱(HW100*100) ",
            " 钢筋限位工装安装及调整 ",
            "L型钢筋 ",
            "\"J\"钢筋 ",
            "剪刀撑 ",
            "U型卡 ",
            "双U型卡 ",
            "短柱(HW150*150) ",
            "预埋件安装 ",
            "定型围栏安拆 ",
            "模板支设 ",
            "C25混凝土 ",
            "铁件 ",
            "电焊条 ",
            "单层彩钢板 ",
            "螺栓套丝机(φ39) ",
            "砂轮切割机(500) ",
            "自升式塔式起重机(1500KNm) ",
            "重型塔吊 ",
            "汽车吊(80t) ",
            "汽车吊(25t) ",
            "吊装索具 ",
            "压制钢丝绳（A68 6*36 7.500m）",
            "压制钢丝绳（A52 6*36 7.407m）",
            "压制钢丝绳（A36 6*36 1.500m）",
            "压制钢丝绳（A68 6*36 9.447M）",
            "压制钢丝绳（φ52 6*36 8.678m）",
            "花篮螺栓  (JW3128-16.78T-1156.7±304.8-UU) ",
            "花篮螺栓  (JW3319-32T-1127.5±152.5-UU) ",
            "花篮螺栓  (JW3409-50T-1100±300-UU) ",
            " 卸扣 (17T) ",
            " 卸扣 (30T) ",
            " 卸扣 (55T) ",
            " 模块吊装工装设计费 ",
            " 无损检测 ",
            " 钢结构验收 ",
            " 钢筋预埋件验收 ",
            " 单侧钢覆面安装加固+埋件焊接材料+镶入件焊接材料 ",
            " 通常设备室钢覆面及预留钢覆面组队焊接 ",
            " 单侧钢覆面埋件临时安装 ",
            " 另一侧钢覆面埋件临时安装 ",
            " 钢覆面后台制作 ",
            " 不锈钢埋件后台制作 ",
            " 碳钢埋件后台制作 ",
            " 套管、镶入件后台制作 ",

        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                # 尝试转换为浮点数
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                # 如果转换失败则设为0
                params_dict[label] = 0
        
        # 分离后八个数据
        all_cost = list(params_dict.keys())
        cost1 = all_cost[:-8]  # 除最后八个之外的所有键
        cost2 = all_cost[-8:]  # 后八个键
        # 创建两个不同的字典
        cost1_dict = {k: params_dict[k] for k in cost1}
        cost2_dict = {k: params_dict[k] for k in cost2}

        # 计算主要成本
        main_cost = calculate_cost(" 钢筋笼施工模式 ", cost1_dict,indirect_costs)

        additional_cost = calculate_cost(" 钢筋笼+钢覆面施工模式 ", cost2_dict,indirect_costs)

        # 合并直接施工和模块化施工的成本项，但排除间接费用
        for construction_type in ['直接施工', '模块化施工']:
            if construction_type in main_cost and construction_type in additional_cost:
                # 首先合并除间接费用外的其他成本
                for cost_type in ['人工费', '材料费', '机械费', '总计']:
                    main_cost[construction_type][cost_type] += additional_cost[construction_type][cost_type]
                
                # 调整总计，减去additional_cost中的间接费用
                # 因为间接费用不应重复计算
                main_cost[construction_type]['总计'] -= additional_cost[construction_type]['间接费用']

        # 处理明细项，确保间接费用不重复
        if '明细' in main_cost and '明细' in additional_cost:
            for detail_item in additional_cost['明细']:
                # 创建一个新版本的detail_item，移除间接费用
                modified_item = detail_item.copy()
                
                for const_type in ['直接施工', '模块化施工']:
                    if const_type in modified_item:
                        # 设置间接费用为0
                        modified_item[const_type]['间接费用'] = 0
                        # 调整总计
                        modified_item[const_type]['总计'] -= detail_item[const_type]['间接费用']
                
                main_cost['明细'].append(modified_item)

        # 如果第一个字典没有"明细"，先创建一个空列表
        if '明细' not in main_cost:
            additional_cost['明细'] = []

        # 将第二个字典的"明细"列表合并到第一个字典中
        if '明细' in additional_cost:
            main_cost['明细'].extend(additional_cost['明细'])

        # 现在 main_cost_dict 包含了合并后的结果
        total_cost_dict = main_cost
        
        project_id = "steel-cage-cover-mode"  # 这里可以替换为实际的项目ID
        construction_mode = " 钢筋笼+钢覆面施工模式 "
        # 返回结果布局
        return create_result_layout(total_cost_dict, project_id, construction_mode)
    #叠合板模块化施工模式计算回调
    @app.callback(
        Output("composite-plate-result-container", "children"),
        Input("modular-composite-plate-modal-submit", "n_clicks"),
        [State("prefab-预制板模板支设", "value"),
         State("prefab-预制板钢筋制作安装", "value"),
         State("prefab-预制板混凝土浇筑", "value"),
         State("prefab-模块化角钢制作安装", "value"),
         State("prefab-模块起重吊装设备", "value"),
         State("prefab-模块运输设备", "value"),
         State("casting-二浇区板模板支设", "value"),
         State("casting-二浇区板钢筋制作安装", "value"),
         State("casting-二浇区混凝土浇筑", "value"),
         State("casting-钢丝网模板", "value"),
         State("casting-施工缝凿毛材料", "value"),
         State("support-满堂脚手架搭设", "value"),
         State("support-外双排脚手架搭设", "value"),
         State("support-模块落位钢筋接头连接", "value"),
         State("embed-预制场地摊销费", "value"),
         State("waterproof-场地平整", "value"),
         State("waterproof-模块支设", "value"),
         State("waterproof-c25混凝土浇筑(15cm+5cm)", "value"),
         State("waterproof-模板拆除", "value"),
         State("waterproof-预制场地维护", "value"),
         State("modular-composite-plate-others-间接施工费（直接施工）","value"),
         State("modular-composite-plate-others-间接施工费（模块化施工）","value"),
         
         
        ]
    )
    def calculate_composite_plate_cost(n_clicks, *params):
        if not n_clicks:
            raise PreventUpdate
        indirect_costs = {
                "直接施工间接费": float(params[-2]) if params[-2] else 0,
                "模块化施工间接费": float(params[-1]) if params[-1] else 0
            }
            
            # 剔除最后两个参数
        main_params = params[:-2]
        # 参数标签和值的映射
        param_labels = [
            " 预制板模板支设 ",
            " 预制板钢筋制作安装 ",
            " 预制板混凝土浇筑 ",
            " 模块化角钢制作安装 ",
            " 模块起重吊装设备 ",
            " 模块运输设备 ",
            " 二浇区板模板支设 ",
            " 二浇区板钢筋制作安装 ",
            " 二浇区混凝土浇筑 ",
            " 钢丝网模板 ",
            " 施工缝凿毛材料 ",
            " 满堂脚手架搭设 ",
            " 外双排脚手架搭设 ",
            " 模块落位钢筋接头连接 ",
            " 预制场地摊销费 ",
            " 场地平整 ",
            " 模块支设 ",
            " C25混凝土浇筑（15cm+5cm） ",
            " 模板拆除 ",
            " 预制场地维护 ",

           

        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                # 尝试转换为浮点数
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                # 如果转换失败则设为0
                params_dict[label] = 0
        
        # 计算成本
        cost_data = calculate_cost(" 叠合板模块化施工(设备室顶板) ", params_dict,indirect_costs)
        project_id = "equipment-room-composite-mode"  # 这里可以替换为实际的项目ID
        construction_mode = " 设备室顶板复合板模式 "
        # 返回结果布局
        return create_result_layout(cost_data,project_id,construction_mode)
    @app.callback(
        Output("tunnel-result-container", "children",allow_duplicate=True),
        Input("tunnel-modal-submit1", "n_clicks"),
        [ State("c403-rebar-钢筋制作安装", "value"),
         State("c403-rebar-预制板顶分布钢筋", "value"),
         State("c403-rebar-预制板吊环钢筋", "value"),
         State("c403-rebar-底部加大钢筋", "value"),
         State("c403-concrete-预制构件混凝土", "value"),
         State("c403-tunnel-formwork-模板支拆", "value"),
         State("c403-tunnel-formwork-满堂支撑架体搭设拆除", "value"),
         State("c403-tunnel-embed-支撑角钢埋件", "value"),
         State("c403-tunnel-embed-墙体埋件", "value"),
         State("c403-tunnel-embed-顶板埋件", "value"),
         State("c403-tunnel-embed-特殊机械套筒", "value"),
         State("c403-tunnel-waterproof-遇水膨胀止水条", "value"),
         State("c403-tunnel-waterproof-三元乙丙橡胶垫", "value"),
         State("c403-tunnel-construction-叠合板凿毛材料", "value"),
         State("c403-tunnel-site-场地平整材料", "value"),
         State("c403-tunnel-site-场地硬化材料", "value"),
         State("c403-tunnel-site-办公区建设材料", "value"),
         State("c403-tunnel-site-围墙建设材料", "value"),
         State("c403-tunnel-site-200t龙门吊", "value"),
         State("c403-tunnel-site-龙门吊轨道", "value"),
         State("c403-tunnel-site-预制加工场摊销", "value"),
         State("c403-tunnel-equipment-25t汽车吊", "value"),
         State("c403-tunnel-equipment-平板车", "value"),
         State("c403-tunnel-equipment-随车吊", "value"),
         State("c403-tunnel-equipment-80吨汽车吊", "value"),
         State("c403-tunnel-equipment-预制构件运输设备", "value"),
         State("c403-others-间接施工费（直接施工）", "value"),
         State("c403-others-间接施工费（模块化施工）", "value"),
         
         
         
        ],prevent_initial_call=True,
        
    )
    def calculate_tunnel_result_cost(n_clicks, *params):
        if not n_clicks:
            raise PreventUpdate
        indirect_costs = {
                "直接施工间接费": float(params[-2]) if params[-2] else 0,
                "模块化施工间接费": float(params[-1]) if params[-1] else 0
            }
            
            # 剔除最后两个参数
        main_params = params[:-2]
        # 参数标签和值的映射
        param_labels = [
            " 钢筋制作安装 ",
            " 预制板顶分布钢筋 ",
            " 预制板吊环钢筋 ",
            " 底部加大钢筋 ",
            " 预制构件混凝土安装(板厚200mm) ",
            " 模板支拆 ",
            " 满堂支撑架体搭设拆除 ",
            " 支撑角钢埋件(L100*10，15.12kg/m) ",
            " 墙体埋件(T2型，34.98kg/m) ",
            " 顶板埋件(M-1型，37.583kg/m) ",
            " 特殊机械套筒 ",
            " 遇水膨胀止水条 ",
            " 三元乙丙橡胶垫 ",
            " 叠合板凿毛材料 ",
            " 场地平整 ",
            " 场地硬化材料 ",
            " 办公区建设材料 ",
            " 围墙建设材料 ",
            " 200T龙门吊 ",
            " 龙门吊轨道 ",
            " 预制加工场摊销 ",
            " 25t汽车吊 ",
            " 平板车(9.6m) ",
            " 随车吊 ",
            " 80吨汽车吊 ",
            " 预制构件运输设备 ",


        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                # 尝试转换为浮点数
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                # 如果转换失败则设为0
                params_dict[label] = 0
        
        all_cost = list(params_dict.keys())
        cost1 = all_cost[:-7]  # 除最后八个之外的所有键
        cost2 = all_cost[-7:]  # 后八个键
        # 创建两个不同的字典
        cost1_dict = {k: params_dict[k] for k in cost1}
        cost2_dict = {k: params_dict[k] for k in cost2}

        # 计算主要成本
        main_cost = calculate_cost(" 叠合板模块化施工(C403、C409) ", cost1_dict,indirect_costs)

        additional_cost = calculate_cost(" 叠合板模块化施工(共用) ", cost2_dict,indirect_costs)

        # 合并直接施工和模块化施工的成本项，但排除间接费用
        for construction_type in ['直接施工', '模块化施工']:
            if construction_type in main_cost and construction_type in additional_cost:
                # 首先合并除间接费用外的其他成本
                for cost_type in ['人工费', '材料费', '机械费', '总计']:
                    main_cost[construction_type][cost_type] += additional_cost[construction_type][cost_type]
                
                # 调整总计，减去additional_cost中的间接费用
                # 因为间接费用不应重复计算
                main_cost[construction_type]['总计'] -= additional_cost[construction_type]['间接费用']

        # 处理明细项，确保间接费用不重复
        if '明细' in main_cost and '明细' in additional_cost:
            for detail_item in additional_cost['明细']:
                # 创建一个新版本的detail_item，移除间接费用
                modified_item = detail_item.copy()
                
                for const_type in ['直接施工', '模块化施工']:
                    if const_type in modified_item:
                        # 设置间接费用为0
                        modified_item[const_type]['间接费用'] = 0
                        # 调整总计
                        modified_item[const_type]['总计'] -= detail_item[const_type]['间接费用']
                
                main_cost['明细'].append(modified_item)

        # 如果第一个字典没有"明细"，先创建一个空列表
        if '明细' not in main_cost:
            additional_cost['明细'] = []

        # 将第二个字典的"明细"列表合并到第一个字典中
        if '明细' in additional_cost:
            main_cost['明细'].extend(additional_cost['明细'])

        # 现在 main_cost_dict 包含了合并后的结果
        total_cost_dict = main_cost

        project_id = "utility-tunnel-composite-mode"  # 这里可以替换为实际的项目ID
        construction_mode = " 管廊叠合板模式 "
        # 返回结果布局
        return create_result_layout(total_cost_dict,project_id,construction_mode)
    @app.callback(
        Output("tunnel-result-container", "children"),
        Input("tunnel-modal-submit2", "n_clicks"),
        [ State("c404-rebar-钢筋制作安装材料", "value"),
         State("c404-rebar-预制板顶分布钢筋", "value"),
         State("c404-rebar-预制板吊环钢筋", "value"),
         State("c404-rebar-底部加大钢筋", "value"),
         State("c404-concrete-预制构件混凝土", "value"),
         State("c404-tunnel-formwork-模板支拆", "value"),
         State("c404-tunnel-formwork-满堂支撑架体搭设拆除", "value"),
         State("c404-tunnel-embed-角钢埋件(l100*100)", "value"),
         State("c404-tunnel-embed-支撑角钢埋件(l100*10，15kg/m)", "value"),
         State("c404-tunnel-embed-墙体埋件(t2型，34kg/m)", "value"),
         State("c404-tunnel-embed-普通套筒", "value"),
         State("c404-tunnel-waterproof-遇水膨胀止水条", "value"),
         State("c404-tunnel-waterproof-三元乙丙橡胶垫", "value"),
         State("c404-tunnel-construction-叠合板凿毛材料", "value"),
         State("c404-tunnel-equipment-25t汽车吊", "value"),
         State("c404-tunnel-equipment-平板车", "value"),
         State("c404-tunnel-equipment-随车吊", "value"),
         State("c404-tunnel-equipment-80吨汽车吊", "value"),
         State("c404-tunnel-equipment-预制构件运输设备", "value"),
         State("c404-tunnel-site-场地平整材料", "value"),
         State("c404-tunnel-site-场地硬化材料", "value"),
         State("c404-tunnel-site-办公区建设材料", "value"),
         State("c404-tunnel-site-围墙建设材料", "value"),
         State("c404-tunnel-site-200t龙门吊", "value"),
         State("c404-tunnel-site-龙门吊轨道", "value"),
         State("c404-tunnel-site-预制加工场摊销", "value"),
         State("c404-others-间接施工费（直接施工）", "value"),
         State("c404-others-间接施工费（模块化施工）", "value"),
         
         
         
        ],prevent_initial_call=True,
        
    )
    def calculate_tunnel_result_cost_c404(n_clicks, *params):
        if not n_clicks:
            raise PreventUpdate
        indirect_costs = {
                "直接施工间接费": float(params[-2]) if params[-2] else 0,
                "模块化施工间接费": float(params[-1]) if params[-1] else 0
            }
            
            # 剔除最后两个参数
        main_params = params[:-2]
        # 参数标签和值的映射
        param_labels = [
            " 钢筋制作安装材料 ",
            " 预制板顶分布钢筋 ",
            " 预制板吊环钢筋 ",
            " 底部加大钢筋 ",
            " 预制构件混凝土 ",
            " 模板支拆材料 ",
            " 满堂支撑架体 ",
            " 角钢埋件(L100*100) ",
            " 支撑角钢埋件(L100*10，15.12kg/m) ",
            " 墙体埋件(T2型，34.98kg/m) ",
            " 普通套筒 ",
            " 遇水膨胀止水条 ",
            " 三元乙丙橡胶垫 ",
            " 叠合板凿毛材料 ",
            " 25t汽车吊 ",
            " 平板车(9.6m) ",
            " 随车吊 ",
            " 80吨汽车吊 ",
            " 预制构件运输设备 ",
            " 场地平整 ",
            " 场地硬化材料 ",
            " 办公区建设材料 ",
            " 围墙建设材料 ",
            " 200T龙门吊 ",
            " 龙门吊轨道 ",
            " 预制加工场摊销 ",


        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                # 尝试转换为浮点数
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                # 如果转换失败则设为0
                params_dict[label] = 0
        
        all_cost = list(params_dict.keys())
        cost1 = all_cost[:-7]  # 除最后7个之外的所有键
        cost2 = all_cost[-7:]  # 后7个键
        # 创建两个不同的字典
        cost1_dict = {k: params_dict[k] for k in cost1}
        cost2_dict = {k: params_dict[k] for k in cost2}

        # 计算主要成本
        main_cost = calculate_cost(" 叠合板模块化施工(C404) ", cost1_dict,indirect_costs)

        additional_cost = calculate_cost(" 叠合板模块化施工(共用) ", cost2_dict,indirect_costs)

        # 合并直接施工和模块化施工的成本项，但排除间接费用
        for construction_type in ['直接施工', '模块化施工']:
            if construction_type in main_cost and construction_type in additional_cost:
                # 首先合并除间接费用外的其他成本
                for cost_type in ['人工费', '材料费', '机械费', '总计']:
                    main_cost[construction_type][cost_type] += additional_cost[construction_type][cost_type]
                
                # 调整总计，减去additional_cost中的间接费用
                # 因为间接费用不应重复计算
                main_cost[construction_type]['总计'] -= additional_cost[construction_type]['间接费用']

        # 处理明细项，确保间接费用不重复
        if '明细' in main_cost and '明细' in additional_cost:
            for detail_item in additional_cost['明细']:
                # 创建一个新版本的detail_item，移除间接费用
                modified_item = detail_item.copy()
                
                for const_type in ['直接施工', '模块化施工']:
                    if const_type in modified_item:
                        # 设置间接费用为0
                        modified_item[const_type]['间接费用'] = 0
                        # 调整总计
                        modified_item[const_type]['总计'] -= detail_item[const_type]['间接费用']
                
                main_cost['明细'].append(modified_item)

        # 如果第一个字典没有"明细"，先创建一个空列表
        if '明细' not in main_cost:
            additional_cost['明细'] = []

        # 将第二个字典的"明细"列表合并到第一个字典中
        if '明细' in additional_cost:
            main_cost['明细'].extend(additional_cost['明细'])

        # 现在 main_cost_dict 包含了合并后的结果
        total_cost_dict = main_cost
        
        # 返回结果布局
        project_id = "utility-tunnel-c404-mode"  # 添加项目ID
        construction_mode = "管廊叠合板C404模式"     # 添加施工模式名称
        return create_result_layout(total_cost_dict, project_id, construction_mode)
    

    # 添加这个回调函数，查询价格参数
    @app.callback(
        Output("price-results-container", "children"),
        Input("price-query-btn", "n_clicks"),
        [State("query-param-type", "value"),
        State("query-param-name", "value")],
        prevent_initial_call=True
    )
    def query_price_data(n_clicks, param_type, param_name):
        if not n_clicks:
            return []
        
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 构建查询条件
            if param_name and param_type:
                query = """
                SELECT * FROM `construction_parameter_table`
                WHERE `parameter_category` LIKE %s AND `engineering_parameter` LIKE %s
                """
                cursor.execute(query, (f'%{param_type}%', f'%{param_name}%'))
            elif param_type:
                query = """
                SELECT * FROM `construction_parameter_table`
                WHERE `parameter_category` LIKE %s
                """
                cursor.execute(query, (f'%{param_type}%',))
            else:
                return html.Div("请选择参数类型")
            
            results = cursor.fetchall()
            conn.close()
            
            # 如果没有数据
            if not results:
                return html.Div("未找到匹配的价格数据")
            
            # 创建数据表格
            return dash_table.DataTable(
                id="price-data-table1",
                columns=[
                    {"name": "参数名称", "id": "engineering_parameter"},
                    {"name": "参数类别", "id": "parameter_category"},
                    {"name": "施工模式", "id": "mode"},
                    {"name": "直接施工人工单价", "id": "direct_labor_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    {"name": "直接施工材料单价", "id": "direct_material_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    {"name": "直接施工机械单价", "id": "direct_machinery_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    {"name": "模块化施工人工单价", "id": "modular_labor_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    {"name": "模块化施工材料单价", "id": "modular_material_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    {"name": "模块化施工机械单价", "id": "modular_machinery_unit_price", "type": "numeric", "format": {"specifier": ",.2f"}}
                ],
                data=results,
                row_selectable="multi",  # 允许选择多行
                selected_rows=[],        # 初始时没有选中的行
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px'},
                style_header={
                    'backgroundColor': '#f0f8ff',
                    'fontWeight': 'bold'
                },
                filter_action="native",
                sort_action="native",
                page_size=10
            )
        
        except Exception as e:
            return html.Div(f"查询出错: {str(e)}")

    @app.callback(
        [Output("selection-output", "children")],
        [Input("save-price-data-btn", "n_clicks")],
        [State("price-data-table1", "selected_rows"),
        State("price-data-table1", "data"),
        State({"type": "param-quantity", "index": ALL}, "value"),
        State({"type": "param-unit", "index": ALL}, "value"),
        # 添加项目基本信息的状态
        State("project-name", "value"),       # 工程名称
        State("project-type", "value"),       # 工程类型
        State("project-amount", "value"),     # 工程量
        State("amount-unit", "value"),        # 单位
        State("normal-days", "value"),        # 正常施工需要的工日数
        State("modular-days", "value"),       # 模块化施工需要的工日数
        State({"type": "project-notes"}, "value")  # 备注说明
        ],
        prevent_initial_call=True
    )
    def save_selected_price_data(n_clicks, selected_row_indices, data, param_quantities, param_units,
                            project_name, project_type, project_amount, amount_unit,
                            normal_days, modular_days, project_notes):
        """
        保存用户选中的价格数据行到数据库
        如果项目已存在，则只保存参数到现有项目中
        """
        if not n_clicks:
            raise PreventUpdate
        
        # 如果没有选中的行
        if not selected_row_indices or not data:
            return [html.Div("请先选择要保存的参数", className="text-danger")]
        if not project_name or not project_name.strip():
            return [html.Div("请先填写工程名称", className="text-warning")]
        # 获取选中的行数据
        selected_rows = [data[i] for i in selected_row_indices]
        
        try:
            init_db() 
            # 检查项目名称是否已存在
            mysql_config = MYSQL_CONFIG.copy()
            mysql_config['autocommit'] = True  # 对于简单查询使用自动提交
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # 准备要保存的数据
            save_params = []
            param_names = []  # 用于收集参数名称

            for i, row in enumerate(selected_rows):
                # 获取对应行的数量和单位，修复索引问题
                current_quantity = param_quantities[i] if i < len(param_quantities) and param_quantities[i] is not None else 0
                current_unit = param_units[i] if i < len(param_units) and param_units[i] is not None else ""
                
                # 确保数量是浮点数
                try:
                    quantity_value = float(current_quantity) if current_quantity else 0
                except (ValueError, TypeError):
                    quantity_value = 0
                
                param_name = row["engineering_parameter"]
                param_names.append(param_name)  # 收集参数名称
                
                # 安全获取价格数据的辅助函数
                def safe_float(value):
                    """安全地将值转换为浮点数"""
                    if value is None:
                        return 0.0
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return 0.0
                
                # 构建完整的参数数据结构，与save_custom_parameters函数期望的格式一致
                param_data = {
                    "id": str(uuid.uuid4()),  # 生成唯一ID
                    "name": param_name,       # 参数名称
                    "type": row["parameter_category"] if row["parameter_category"] else "其他材料",  # 参数类型
                    "value": quantity_value,  # 参数值（用户输入的数量）
                    "unit": current_unit,     # 单位
                    "description": row["mode"] if row["mode"] else "",  # 描述（施工模式）
                    "direct_labor_price": safe_float(row.get("direct_labor_unit_price", 0)),
                    "direct_material_price": safe_float(row.get("direct_material_unit_price", 0)),
                    "direct_machine_price": safe_float(row.get("direct_machinery_unit_price", 0)),
                    "modular_labor_price": safe_float(row.get("modular_labor_unit_price", 0)),
                    "modular_material_price": safe_float(row.get("modular_material_unit_price", 0)),
                    "modular_machine_price": safe_float(row.get("modular_machinery_unit_price", 0))
                }
                save_params.append(param_data)
                        
            # 查询项目名称是否已存在
            cursor.execute("SELECT `project_id` FROM `project_info` WHERE `project_name` = %s", (project_name,))
            existing_project = cursor.fetchone()
            
            if existing_project:
                # 如果项目已存在，直接将参数添加到现有项目中
                project_id = existing_project['project_id']
                # 使用现有项目ID保存参数
                save_custom_parameters(project_id, save_params, replace_existing=False)
                
                # 格式化参数名称列表
                if len(param_names) <= 3:
                    param_names_str = "、".join(param_names)
                else:
                    param_names_str = "、".join(param_names[:3]) + f" 等{len(param_names)}个参数"
                
                # 返回成功消息，指明保存的参数名称和项目名称
                return [html.Div(f"已将 {param_names_str} 添加到现有项目 '{project_info['project_name']}'", className="text-success")]
            else:
                # 如果项目不存在，创建新项目
                project_info = {
                    "project_name": project_name.strip(),  # 使用用户输入的工程名称
                    "project_type": project_type or "自定义",
                    "project_value": float(project_amount or 0),
                    "project_unit": amount_unit or "",
                    "regular_days": int(normal_days or 0),
                    "modular_days": int(modular_days or 0),
                    "description": project_notes or f"从查询导入的参数，共{len(save_params)}个"
                }
                
                # 保存项目和参数
                project_id = save_project(project_info)
                save_custom_parameters(project_id, save_params, replace_existing=False)
                
                # 格式化参数名称列表
                if len(param_names) <= 3:
                    param_names_str = "、".join(param_names)
                else:
                    param_names_str = "、".join(param_names[:3]) + f" 等{len(param_names)}个参数"
                
                # 返回成功消息，指明保存的参数名称和项目名称
                return [html.Div(f"成功创建新项目 '{project_info['project_name']}' 并保存 {param_names_str}", className="text-success")]
            
        except Exception as e:
            import traceback
            print(f"保存参数时出错: {e}")
            print(traceback.format_exc())
            return [html.Div(f"保存失败: {str(e)}", className="text-danger")]
        finally:
            if 'conn' in locals() and conn:
                conn.close()

###################显示自定义部分的详情
    @app.callback(
        [Output("custom-mode-detail-modal", "is_open"),
        Output("custom-mode-detail-id-store", "data")],
        [Input({"type": "custom-mode-btn", "index": ALL}, "n_clicks")],
        prevent_initial_call=True
    )
    def open_custom_mode_detail(n_clicks_list):
        """点击自定义模式卡片时打开详情模态窗口"""
        ctx = dash.callback_context
        
        # 打印调试信息
        print(f"触发的回调: {ctx.triggered}")
        print(f"n_clicks_list: {n_clicks_list}")
        
        # 如果没有触发或所有按钮都没被点击，则不更新
        if not ctx.triggered or not any(click for click in n_clicks_list if click):
            raise dash.exceptions.PreventUpdate
        
        # 获取被点击的按钮ID
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(f"被点击的按钮ID: {button_id}")
        
        try:
            button_dict = json.loads(button_id)
            
            # 提取mode_id (从"custom-mode-{mode_id}"中提取实际的mode_id)
            index_value = button_dict['index']
            mode_id = index_value.replace("custom-mode-", "")
            
            print(f"提取的mode_id: {mode_id}")
            
            # 返回打开模态窗口并设置当前选中的模式ID
            return True, mode_id
        except Exception as e:
            print(f"处理按钮ID时出错: {e}")
            raise dash.exceptions.PreventUpdate

###添加加载项目详情数据的回调
    @app.callback(
        [Output("custom-mode-name", "children"),
        Output("custom-mode-type", "children"),
        Output("custom-mode-value", "children"),
        Output("custom-mode-days", "children"),
        Output("custom-mode-description", "children"),
        Output("custom-mode-params-container", "children")],
        Input("custom-mode-detail-id-store", "data"),
        prevent_initial_call=True
    )
    def load_custom_mode_details(mode_id):
        """加载自定义模式详细信息"""
        if not mode_id:
            raise PreventUpdate
            
        # 从数据库获取模式详情
        mode_data = get_mode_details_from_database(mode_id)
        
        if not mode_data:
            return "未找到", "未知", "0", "0/0", "无描述", "无参数"
        
        # 显示工程量和单位
        project_value = f"{mode_data['project_value']} {mode_data['project_unit']}"
        
        # 显示工期比较
        project_days = f"直接施工: {mode_data['regular_days']}天 / 模块化施工: {mode_data['modular_days']}天"
        
        # 创建参数表格
        params_table = create_params_table(mode_data['parameters'])
        
        return (
            mode_data['project_name'],
            mode_data['project_type'],
            project_value,
            project_days,
            mode_data['description'],
            params_table
        )
#########添加成本计算和显示回调
    @app.callback(
        Output("custom-mode-result-container", "children"),
        Input("custom-mode-calculate-btn", "n_clicks"),
        State("custom-mode-detail-id-store", "data"),
        prevent_initial_call=True
    )
    def calculate_custom_mode_costs(n_clicks, mode_id):
        """计算自定义模式的成本并显示比较结果"""
        if not n_clicks or not mode_id:
            raise PreventUpdate
            
        # 获取模式详情
        mode_data = get_mode_details_from_database(mode_id)
        
        if not mode_data or not mode_data.get('parameters'):
            return html.Div("无法计算成本：缺少参数数据", className="text-danger")
        
        # 准备参数字典，用于计算成本
        params_dict = {}
        for param in mode_data['parameters']:
            params_dict[param['name']] = param['value']
        
        # 间接成本设置
        indirect_costs = {
            "直接施工间接费": 0,  # 可以从数据中获取或设置默认值
            "模块化施工间接费": 0  # 可以从数据中获取或设置默认值
        }
        
        # 计算成本
        cost_data = calculate_cost_diy(mode_data['project_type'], params_dict, indirect_costs)
        
        # 创建结果布局
        return create_result_layout2(cost_data,mode_id, mode_data['project_type'])

#####结果实时更新
    @app.callback(
        [Output('cost-comparison-table', 'data'),
        Output('cost-savings-display', 'children')],
        [Input('cost-comparison-table', 'data_timestamp')],
        [State('cost-comparison-table', 'data'),
        State('initial-cost-data', 'data')]
    )
    def update_totals(timestamp, rows, initial_cost_data):
        if not timestamp or not rows:
            raise PreventUpdate
        
        # 创建一个深拷贝以避免修改原始数据
        updated_rows = copy.deepcopy(rows)
        
        # 获取间接费用行的值
        direct_indirect = float(updated_rows[3]['直接施工'])
        modular_indirect = float(updated_rows[3]['模块化施工'])
        
        # 计算并更新总计
        direct_total = (
            initial_cost_data["直接施工"]["人工费"] +
            initial_cost_data["直接施工"]["材料费"] +
            initial_cost_data["直接施工"]["机械费"] +
            direct_indirect
        )
        
        modular_total = (
            initial_cost_data["模块化施工"]["人工费"] +
            initial_cost_data["模块化施工"]["材料费"] +
            initial_cost_data["模块化施工"]["机械费"] +
            modular_indirect
        )
        
        # 更新总计行
        updated_rows[4]['直接施工'] = direct_total
        updated_rows[4]['模块化施工'] = modular_total
        
        # 计算节约成本和百分比
        savings = modular_total - direct_total
        savings_percent = (savings / direct_total) * 100 if direct_total > 0 else 0
        
        # 更新成本节约显示
        savings_text = f"修改间接费用后，成本{'增加' if savings > 0 else '减少'}: {abs(savings):,.2f} 元 (成本{'增幅' if savings > 0 else '降幅'}：{abs(savings_percent):.1f}%)"
        savings_display = html.H5(
            savings_text,
            className=f"mt-3 {'text-success' if savings < 0 else 'text-danger'}"
        )
        
        return updated_rows, savings_display

    ###保存结果
    @app.callback(
        Output('save-status', 'children'),
        Input('save-cost-result-btn', 'n_clicks'),
        [State('cost-comparison-table', 'data'),
        State('current-project-id', 'data'),
        State('current-construction-mode', 'data')]
    )
    def save_cost_result(n_clicks, table_data, project_id, construction_mode):
        if not n_clicks:
            raise PreventUpdate
        
        if not project_id:
            return html.Div("错误：未指定工程ID", className="text-danger")
        
        if not construction_mode:
            return html.Div("错误：未指定施工模式", className="text-danger")
        
        try:
            # 提取表格数据
            direct_labor = float(table_data[0]['直接施工'])
            direct_material = float(table_data[1]['直接施工'])
            direct_machine = float(table_data[2]['直接施工'])
            direct_indirect = float(table_data[3]['直接施工'])
            direct_total = float(table_data[4]['直接施工'])
            
            modular_labor = float(table_data[0]['模块化施工'])
            modular_material = float(table_data[1]['模块化施工'])
            modular_machine = float(table_data[2]['模块化施工'])
            modular_indirect = float(table_data[3]['模块化施工'])
            modular_total = float(table_data[4]['模块化施工'])
            
            # 计算差异
            cost_diff = modular_total - direct_total
            cost_diff_percent = (cost_diff / direct_total * 100) if direct_total > 0 else 0
            
            # 所有成本数据整合为字典
            cost_data = {
                "直接施工": {
                    "人工费": direct_labor,
                    "材料费": direct_material,
                    "机械费": direct_machine,
                    "间接费用": direct_indirect,
                    "总计": direct_total
                },
                "模块化施工": {
                    "人工费": modular_labor,
                    "材料费": modular_material,
                    "机械费": modular_machine,
                    "间接费用": modular_indirect,
                    "总计": modular_total
                },
                "差异": {
                    "成本差异": cost_diff,
                    "成本差异百分比": cost_diff_percent
                }
            }
            
            # 将字典转换为JSON字符串
            cost_json = json.dumps(cost_data, ensure_ascii=False)
            
            # 调用保存函数
            result = save_calculation_result(project_id, construction_mode, cost_data, cost_json)
            
            if result:
                return html.Div("结果保存成功！", className="text-success")
            else:
                return html.Div("保存失败，请重试", className="text-danger")
        
        except Exception as e:
            print(f"保存结果时出错: {e}")
            return html.Div(f"保存出错: {str(e)}", className="text-danger")

    @app.callback(
        Output("custom-mode-detail-modal", "is_open", allow_duplicate=True),
        Input("custom-mode-close-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def close_custom_mode_detail(n_clicks):
        """点击取消按钮关闭详情模态窗口"""
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        
        # 关闭模态窗口
        return False

#################添加自定义参数部分
    # 添加新行到自定义参数表格
# 添加新参数行回调
    @app.callback(
        Output("params-container", "children"),
        Input("add-param-btn", "n_clicks"),
        State("params-container", "children"),
        prevent_initial_call=True
    )
    def add_parameter_row(n_clicks, current_children):
        if n_clicks:
            # 创建新的参数行索引
            new_index = len(current_children)
            # 添加新的参数行
            return current_children + [create_parameter_form_row(new_index)]
        return current_children

    # 删除参数行回调
    @app.callback(
        Output("params-container", "children", allow_duplicate=True),
        Input({"type": "remove-param", "index": ALL}, "n_clicks"),
        State("params-container", "children"),
        prevent_initial_call=True
    )
    def remove_parameter_row(n_clicks_list, current_children):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        # 获取被点击的按钮ID
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        removed_index = json.loads(trigger_id)['index']
        
        # 删除对应索引的参数行
        updated_children = [child for i, child in enumerate(current_children) if i != removed_index]
        
        # 更新剩余参数行的索引
        # 注意：这部分可能需要额外处理，因为组件ID已经渲染
        # 一种简单的方法是清除所有行并重新创建
        return updated_children

    # 清空所有参数输入框内容的回调函数
    @app.callback(
        [
            Output({"type": "param-name", "index": 0}, "value"),
            Output({"type": "param-type", "index": 0}, "value"),
            Output({"type": "param-value", "index": 0}, "value"),
            Output({"type": "param-unit", "index": 0}, "value"),
            Output({"type": "direct-labor-price", "index": 0}, "value"),
            Output({"type": "direct-material-price", "index": 0}, "value"),
            Output({"type": "direct-machine-price", "index": 0}, "value"),
            Output({"type": "modular-labor-price", "index": 0}, "value"),
            Output({"type": "modular-material-price", "index": 0}, "value"),
            Output({"type": "modular-machine-price", "index": 0}, "value")
        ],
        Input("clear-params-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_input_fields(n_clicks):
        """清空所有输入框内容"""
        # 打印调试信息
        print(f"清空按钮回调被触发，n_clicks={n_clicks}")
        ctx = dash.callback_context
        print(f"回调上下文: {ctx.triggered}")
        
        if n_clicks:
            print("准备清空字段...")
            # 返回清空后的值
            result = [
                "",       # 参数名称 - 文本，清空为空字符串
                None,     # 参数类别 - 下拉框，清空为None
                None,     # 参数值 - 数字，清空为None
                None,     # 单位 - 下拉框，清空为None
                0,        # 直接施工人工单价 - 数字，清空为0
                0,        # 直接施工材料单价 - 数字，清空为0
                0,        # 直接施工机械单价 - 数字，清空为0
                0,        # 模块化施工人工单价 - 数字，清空为0
                0,        # 模块化施工材料单价 - 数字，清空为0
                0         # 模块化施工机械单价 - 数字，清空为0
            ]
            print(f"返回清空值: {result}")
            return result
        
        print("没有触发清空操作")
        raise dash.exceptions.PreventUpdate

    # 保存参数回调
    @app.callback(
        Output("custom-params-save-result", "children"),
        Input("save-custom-params-btn", "n_clicks"),
        [State({"type": "param-name", "index": ALL}, "value"),
        State({"type": "param-type", "index": ALL}, "value"),
        State({"type": "param-value", "index": ALL}, "value"),
        State({"type": "param-unit", "index": ALL}, "value"),
        State({"type": "direct-labor-price", "index": ALL}, "value"),
        State({"type": "direct-material-price", "index": ALL}, "value"),
        State({"type": "direct-machine-price", "index": ALL}, "value"),
        State({"type": "modular-labor-price", "index": ALL}, "value"),
        State({"type": "modular-material-price", "index": ALL}, "value"),
        State({"type": "modular-machine-price", "index": ALL}, "value"),
        # 项目信息状态
        State("project-name", "value"),
        State("project-type", "value"),
        State("project-amount", "value"),
        State("amount-unit", "value"),
        State("normal-days", "value"),
        State("modular-days", "value"),
        State({"type": "project-notes"}, "value")],
        prevent_initial_call=True
    )
    def save_parameters(n_clicks, names, types, values, units, 
                    direct_labor, direct_material, direct_machine,
                    modular_labor, modular_material, modular_machine,
                    project_name, project_type, project_amount, 
                    amount_unit, normal_days, modular_days, project_notes):
        
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        if not project_name or not project_name.strip():
            return html.Div("请先填写工程名称", className="text-warning")
        # 收集参数数据（保持原有逻辑）
        params = []
        param_names_list = []
        
        for i in range(len(names)):
            if not names[i]:
                continue
            
            param_names_list.append(names[i])
            
            def get_non_none_value(value_list, index):
                if index < len(value_list):
                    if value_list[index] is not None:
                        return _safe_float(value_list[index])
                    for v in value_list:
                        if v is not None:
                            return _safe_float(v)
                return 0.0
            
            param = {
                "id": str(uuid.uuid4()),
                "name": names[i],
                "type": types[i] if types[i] else "其他材料",
                "value": _safe_float(values[i]),
                "unit": units[i] if units[i] else "",
                "direct_labor_price": get_non_none_value(direct_labor, i),
                "direct_material_price": get_non_none_value(direct_material, i),
                "direct_machine_price": get_non_none_value(direct_machine, i),
                "modular_labor_price": get_non_none_value(modular_labor, i),
                "modular_material_price": get_non_none_value(modular_material, i),
                "modular_machine_price": get_non_none_value(modular_machine, i),
                "description": ""
            }
            
            params.append(param)
        
        if not params:
            return html.Div("请至少输入一个有效参数名称", className="text-warning")
        
        # 格式化参数名称列表
        if len(param_names_list) <= 3:
            param_names_str = "、".join(param_names_list)
        else:
            param_names_str = "、".join(param_names_list[:3]) + f"等共{len(param_names_list)}个参数"
        
        # 准备项目信息
        project_info = {
            "project_name": project_name.strip(),
            "project_type": project_type or "自定义",
            "project_value": float(project_amount or 0),
            "project_unit": amount_unit or "",
            "regular_days": int(normal_days or 0),
            "modular_days": int(modular_days or 0),
            "description": project_notes or f"自定义参数项目，包含 {len(params)} 个参数"
        }
        
        try:
            # 初始化数据库
            init_db()
            
            # 检查项目名称是否已存在
            mysql_config = MYSQL_CONFIG.copy()
            mysql_config['autocommit'] = True
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT `project_id` FROM `project_info` WHERE `project_name` = %s", (project_info["project_name"],))
            existing_project = cursor.fetchone()
            
            if existing_project:
                # 如果项目已存在，使用现有项目ID
                project_id = existing_project['project_id']
                print(f"使用现有项目ID: {project_id}")
                conn.close()
                save_custom_parameters(project_id, params, replace_existing=False)
                
                return html.Div([
                    html.P(f"成功将 {param_names_str} 添加到现有项目:", className="mb-1"),
                    html.Strong(f"'{project_info['project_name']}'", className="text-primary"),
                    html.P(f"项目ID: {project_id}", className="mt-2 mb-0 small text-muted")
                ], className="alert alert-success")
            else:
                # 创建新项目并获取新的project_id
                project_id = save_project(project_info)
                print(f"创建新项目，获得project_id: {project_id}")
                save_custom_parameters(project_id, params, replace_existing=False)
                conn.close()
                
                return html.Div([
                    html.P(f"成功创建新项目:", className="mb-1"),
                    html.Strong(f"'{project_info['project_name']}'", className="text-primary"),
                    html.P(f"项目ID: {project_id}", className="mt-1 mb-1"),
                    html.P(f"已保存参数: {param_names_str}", className="mt-1 mb-0")
                ], className="alert alert-success")
        
        except Exception as e:
            print(f"保存参数时出错: {e}")
            return html.Div([
                html.P("保存失败:", className="mb-1"),
                html.Strong(f"{str(e)}", className="text-danger")
            ], className="alert alert-danger")

    ##########################

    

        # 2. 在 callbacks.py 的 create_model_modal_callback 函数中添加钢衬里计算回调
    @app.callback(
        Output("steel-lining-result-container", "children"),
        Input("steel-lining-modal-confirm-btn", "n_clicks"),
        [
            # 基础结构类参数
            State("steel-lining-foundation-网架存放场地", "value"),
            State("steel-lining-foundation-制作胎具", "value"), 
            State("steel-lining-foundation-钢支墩、埋件混凝土剔凿", "value"),
            State("steel-lining-foundation-钢支墩、埋件混凝土回填", "value"),
            State("steel-lining-foundation-钢支墩、埋件安装", "value"),
            State("steel-lining-foundation-钢支墩、埋件使用折旧", "value"),
            
            # 结构构件类参数
            State("steel-lining-structure-扶壁柱安装", "value"),
            State("steel-lining-structure-扶壁柱拆除", "value"),
            State("steel-lining-structure-扶壁柱构件使用折旧费", "value"),
            State("steel-lining-structure-走道板及操作平台制作", "value"),
            State("steel-lining-structure-走道板及操作平台搭设", "value"),
            State("steel-lining-structure-走道板及操作平台拆除", "value"),
            
            # 辅助设施类参数
            State("steel-lining-auxiliary-脚手架搭拆", "value"),
            State("steel-lining-auxiliary-环向加固工装", "value"),
            State("steel-lining-auxiliary-模块就位措施", "value"),
            State("steel-lining-auxiliary-角钢增设", "value"),
            
            # 机械设备类参数
            State("steel-lining-equipment-人工保养吊索具", "value"),
            State("steel-lining-equipment-吊索具使用机械倒运", "value"),
            State("steel-lining-equipment-模板试吊、吊装投入的人工", "value"),
            
            # 钢网架系统参数
            State("steel-lining-frame-钢网架制作", "value"),
            State("steel-lining-frame-钢网架安装", "value"),
            State("steel-lining-frame-钢网架拆除", "value"),
            State("steel-lining-frame-模块吊耳制、安、拆", "value"),
            
            # 试验检测参数
            State("steel-lining-testing-荷载试验人工配合", "value"),
            
            # 间接费用
            State("steel-lining-others-间接施工费（直接施工）", "value"),
            State("steel-lining-others-间接施工费（模块化施工）", "value"),
        ]
    )
    def calculate_steel_lining_cost_callback_fixed(n_clicks, *params):
        """修正后的钢衬里施工模式计算回调"""
        if not n_clicks:
            raise PreventUpdate
        
        # 首先运行诊断
        #debug_steel_lining_database()
        
        # 处理间接费用
        indirect_costs = {
            "直接施工间接费": float(params[-2]) if params[-2] else 0,
            "模块化施工间接费": float(params[-1]) if params[-1] else 0
        }
        
        # 剔除最后两个间接费用参数
        main_params = params[:-2]
        
        # 参数标签列表
        param_labels = [
            "网架存放场地",
            "制作胎具", 
            "钢支墩、埋件混凝土剔凿",
            "钢支墩、埋件混凝土回填",
            "钢支墩、埋件安装",
            "钢支墩、埋件使用折旧",
            "扶壁柱安装",
            "扶壁柱拆除",
            "扶壁柱构件使用折旧费",
            "走道板及操作平台制作",
            "走道板及操作平台搭设",
            "走道板及操作平台拆除",
            "脚手架搭拆",
            "环向加固工装",
            "模块就位措施",
            "角钢增设",
            "人工保养吊索具",
            "吊索具使用机械倒运",
            "模板试吊、吊装投入的人工",
            "钢网架制作",
            "钢网架安装",
            "钢网架拆除",
            "模块吊耳制、安、拆",
            "荷载试验人工配合"
        ]
        
        # 创建参数字典
        params_dict = {}
        for label, value in zip(param_labels, main_params):
            try:
                value = float(value) if value else 0
                params_dict[label] = value
            except ValueError:
                params_dict[label] = 0
        
        print(f"传入的参数: {params_dict}")
        
        # 使用修正后的计算函数
        cost_data = calculate_steel_lining_cost_fixed("钢衬里施工模式", params_dict, indirect_costs)
        
        project_id = "steel-lining-mode"
        construction_mode = "钢衬里施工模式"
        
        # 返回结果布局
        return create_result_layout(cost_data, project_id, construction_mode)


    # 新代码（只需要修改函数内部的部分代码）- 将上面函数中的这几行：
        print(f"传入的参数: {params_dict}")
        
        # 使用修正后的计算函数
        cost_data = calculate_steel_lining_cost_fixed("钢衬里施工模式", params_dict, indirect_costs)

    # 替换为：
        print(f"钢衬里计算 - 传入的参数: {params_dict}")
        print(f"钢衬里计算 - 间接费用: {indirect_costs}")
        
        # 使用修正后的计算函数（使用标准计算方式）
        cost_data = calculate_steel_lining_cost_fixed("钢衬里施工模式", params_dict, indirect_costs)


def register_custom_mode_callbacks(app):
    """注册自定义模式相关的回调函数 - 简化版本"""
    
    # 注册分页回调
    register_pagination_callbacks(app)
    
    @app.callback(
        Output("custom-modes-container", "children", allow_duplicate=True),
        Input("refresh-custom-modes", "n_clicks"),
        prevent_initial_call=True
    )   
    def update_custom_modes_section(n_clicks):
        """响应刷新按钮点击，从parameter_info表更新自定义模式部分"""
        print(f"刷新按钮被点击，n_clicks: {n_clicks}")
        
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        
        try:
            print("开始从parameter_info表加载自定义模式...")
            
            # 直接调用加载函数
            custom_modes = load_custom_modes()
            
            print(f"加载完成，获得 {len(custom_modes)} 个模式")
            
            # 打印项目名称用于确认
            if custom_modes:
                print("加载的项目:")
                for i, mode in enumerate(custom_modes):
                    print(f"  {i+1}. {mode['project_name']} (参数数量: {mode['parameter_count']})")
            else:
                print("没有找到任何项目")
            
            # 创建带分页的自定义模式行 - 重置到第一页
            result = create_custom_modes_row_with_pagination(custom_modes, current_page=1)
            print("自定义模式行创建完成")
            
            return result
            
        except Exception as e:
            print(f"更新自定义模式时出错: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            
            # 返回错误信息
            return html.Div([
                html.P("从parameter_info表加载自定义模式时出错", className="text-center text-danger"),
                html.P(f"错误信息: {str(e)}", className="text-center text-muted small")
            ])

# 添加一个安全的浮点数转换函数
def _safe_float(value):
    """
    安全地将值转换为浮点数
    
    Args:
        value: 需要转换的值
        
    Returns:
        float: 转换后的浮点数，如果转换失败则返回0.0
    """
    if value is None:
        return 0.1
    
    if isinstance(value, str):
        value = value.strip()  # 去除两端空白
    
    try:
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        print(f"警告: 无法转换值 '{value}' 为浮点数，使用0代替")
        return 0.0

# 添加分页控件回调函数
def register_pagination_callbacks(app):
    """注册分页相关的回调函数"""
    
    @app.callback(
        Output("custom-modes-container", "children"),
        [
            Input("prev-page-btn", "n_clicks"),
            Input("next-page-btn", "n_clicks"),
            Input("first-page-btn", "n_clicks"),
            Input("last-page-btn", "n_clicks"),
            Input("page-jump-btn", "n_clicks")
        ],
        [
            State("current-page-store", "data"),
            State("total-modes-store", "data"),
            State("page-jump-input", "value")
        ],
        prevent_initial_call=True
    )
    def handle_pagination(prev_clicks, next_clicks, first_clicks, last_clicks, jump_clicks,
                         current_page, total_modes, jump_page):
        """处理分页按钮点击"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        # 获取触发的按钮
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # 重新加载自定义模式数据
        custom_modes = load_custom_modes()
        items_per_page = 6
        total_pages = math.ceil(len(custom_modes) / items_per_page) if custom_modes else 1
        
        # 根据按钮确定新页面
        new_page = current_page or 1
        
        if button_id == "prev-page-btn":
            new_page = max(1, new_page - 1)
        elif button_id == "next-page-btn":
            new_page = min(total_pages, new_page + 1)
        elif button_id == "first-page-btn":
            new_page = 1
        elif button_id == "last-page-btn":
            new_page = total_pages
        elif button_id == "page-jump-btn":
            if jump_page and 1 <= jump_page <= total_pages:
                new_page = jump_page
        
        # 确保页面在有效范围内
        new_page = max(1, min(new_page, total_pages))
        
        # 返回新的分页内容
        return create_custom_modes_row_with_pagination(custom_modes, new_page)

    @app.callback(
        Output("page-jump-input", "value"),
        Input("current-page-store", "data"),
        prevent_initial_call=True
    )
    def update_jump_input(current_page):
        """更新跳转输入框的值"""
        return current_page or 1


    # 删除自定义模式相关回调
    @app.callback(
        [Output("delete-confirmation-modal", "is_open"),
         Output("delete-project-name", "children"),
         Output("delete-project-id-store", "data")],
        [Input({"type": "delete-custom-mode-btn", "index": ALL}, "n_clicks")],
        [State("delete-confirmation-modal", "is_open")],
        prevent_initial_call=True
    )
    def open_delete_confirmation(delete_clicks_list, is_open):
        """打开删除确认模态窗口"""
        ctx = dash.callback_context
        
        # 检查是否有删除按钮被点击
        if not ctx.triggered or not any(click for click in delete_clicks_list if click):
            raise dash.exceptions.PreventUpdate
        
        # 获取被点击的删除按钮的项目ID
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            button_dict = json.loads(button_id)
            project_id = button_dict['index']
            
            print(f"准备删除项目ID: {project_id}")
            
            # 获取项目基本信息
            project_info = get_project_basic_info(project_id)
            
            if project_info:
                project_display = f"{project_info['project_name']} (包含 {project_info['parameter_count']} 个参数)"
                return True, project_display, project_id
            else:
                print(f"未找到项目ID {project_id} 的信息")
                return False, "", None
                
        except Exception as e:
            print(f"处理删除按钮点击时出错: {e}")
            return False, "", None

    @app.callback(
        Output("delete-confirmation-modal", "is_open", allow_duplicate=True),
        Input("cancel-delete-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def close_delete_confirmation(n_clicks):
        """取消删除，关闭确认模态窗口"""
        if n_clicks:
            return False
        raise dash.exceptions.PreventUpdate

    @app.callback(
        [Output("delete-confirmation-modal", "is_open", allow_duplicate=True),
         Output("custom-modes-container", "children", allow_duplicate=True)],
        [Input("confirm-delete-btn", "n_clicks")],
        [State("delete-project-id-store", "data")],
        prevent_initial_call=True
    )
    def confirm_delete_project(n_clicks, project_id):
        """确认删除项目"""
        if not n_clicks or not project_id:
            raise dash.exceptions.PreventUpdate
        
        try:
            print(f"确认删除项目ID: {project_id}")
            
            # 执行删除操作
            delete_result = delete_custom_project(project_id)
            
            if delete_result["success"]:
                print(f"✅ {delete_result['message']}")
                
                # 删除成功后重新加载自定义模式列表
                custom_modes = load_custom_modes()
                updated_container = create_custom_modes_row_with_pagination(custom_modes, current_page=1)
                
                # 关闭模态窗口并更新列表
                return False, updated_container
            else:
                print(f"❌ 删除失败: {delete_result['message']}")
                # 删除失败，只关闭模态窗口，不更新列表
                return False, dash.no_update
                
        except Exception as e:
            print(f"确认删除时出错: {e}")
            return False, dash.no_update