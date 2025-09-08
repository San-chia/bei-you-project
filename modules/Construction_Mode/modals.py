import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
import plotly.graph_objects as go  # 添加这一行导入
import time
from datetime import datetime
import uuid

from .metal_config import (steel_materials,
                           connection_materials,
                           steel_cover_materials,
                           embedding_materials,
                           mechanical_equipment,
                           prefab_materials,
                           secondary_casting_materials,
                           support_materials,
                           place_materials,
                           Prefabricated_site_facilities,
                           rebar_materials,
                           concrete_materials,
                           formwork_materials,
                           tunnel_embedding_materials,
                           tunnel_waterproof_materials,
                           construction_materials,
                           tunnel_equipment,
                           tunnel_site_facilities,
                           cage_steel_materials,
                           cage_connection_materials,
                           cage_tool_materials,
                           cage_auxiliary_materials,
                           cage_mechanical_equipment,
                           project_types,
                           param_types,
                           units,
                           lifting_lock,
                           c404_tunnel_embedding_materials,
                           others,
                           steel_lining_foundation,
                           steel_lining_structure,
                           steel_lining_auxiliary,
                           steel_lining_equipment,
                           steel_lining_frame,
                           steel_lining_testing,
                           DEFAULT_PARAM_ID,
                           )
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG, THEME, FONT_AWESOME_URL
from .translation import (
    translate_table_name, 
    translate_field_name, 
    reverse_translate_table_name, 
    reverse_translate_field_name,
    translate_dataframe_columns,
    FIELD_TRANSLATIONS,
    TABLE_TRANSLATIONS
)



def create_steel_cage_parameter_modal():
    return dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("钢筋笼施工模式参数配置"), close_button=True),
        dbc.ModalBody([
            # 主体钢筋材料部分
            html.H5("主体钢筋材料", className="mt-3 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-steel", cage_steel_materials[0]),
                    create_input_field("cage-steel", cage_steel_materials[2]),
                    create_input_field("cage-steel", cage_steel_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-steel", cage_steel_materials[1]),
                    create_input_field("cage-steel", cage_steel_materials[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 连接材料部分
            html.H5("连接材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-connection", cage_connection_materials[0]),
                    create_input_field("cage-connection", cage_connection_materials[2]),
                    create_input_field("cage-connection", cage_connection_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-connection", cage_connection_materials[1]),
                    create_input_field("cage-connection", cage_connection_materials[3]),
                    create_input_field("cage-connection", cage_connection_materials[5]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 工装系统部分
            html.H5("工装系统", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-tool", cage_tool_materials[0]),
                    create_input_field("cage-tool", cage_tool_materials[2]),
                    create_input_field("cage-tool", cage_tool_materials[4]),
                    create_input_field("cage-tool", cage_tool_materials[6]),
                    create_input_field("cage-tool", cage_tool_materials[8]),
                    create_input_field("cage-tool", cage_tool_materials[10]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-tool", cage_tool_materials[1]),
                    create_input_field("cage-tool", cage_tool_materials[3]),
                    create_input_field("cage-tool", cage_tool_materials[5]),
                    create_input_field("cage-tool", cage_tool_materials[7]),
                    create_input_field("cage-tool", cage_tool_materials[9]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 施工辅助材料部分
            html.H5("施工辅助材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[0]),
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[3]),
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[5]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[1]),
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[2]),
                    create_input_field("cage-auxiliary", cage_auxiliary_materials[4]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 机械设备部分
            html.H5("机械设备", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-equipment", cage_mechanical_equipment[0]),
                    create_input_field("cage-equipment", cage_mechanical_equipment[2]),
                    create_input_field("cage-equipment", cage_mechanical_equipment[4]),
                    create_input_field("cage-equipment", cage_mechanical_equipment[6]),
                    create_input_field("cage-equipment", lifting_lock[0]),
                    create_input_field("cage-equipment", lifting_lock[2]),
                    create_input_field("cage-equipment", lifting_lock[4]),
                    create_input_field("cage-equipment", lifting_lock[6]),
                    create_input_field("cage-equipment", lifting_lock[8]),
                    create_input_field("cage-equipment", lifting_lock[10]),
                    ],className="col-md-6"),
                    
                html.Div([
                    create_input_field("cage-equipment", cage_mechanical_equipment[1]),
                    create_input_field("cage-equipment", cage_mechanical_equipment[3]),
                    create_input_field("cage-equipment", cage_mechanical_equipment[5]),
                    create_input_field("cage-equipment", lifting_lock[1]),
                    create_input_field("cage-equipment", lifting_lock[3]),
                    create_input_field("cage-equipment", lifting_lock[5]),
                    create_input_field("cage-equipment", lifting_lock[7]),
                    create_input_field("cage-equipment", lifting_lock[9]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 其他费用部分
            html.H5("其他费用", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-other", "模块吊装工装设计费"),
                    create_input_field("cage-other", "无损检测"),
                    create_input_field("cage-other", "钢结构验收"),
                    create_input_field("cage-other", "钢筋预埋件验收"),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-others", others[0]),
                    create_input_field("cage-others", others[1]),
                ], className="col-md-6"),
            ], className="row"),
            
        ], style={"max-height": "70vh", "overflow-y": "auto"}),
        dbc.ModalFooter([
            dbc.Button("取消", id="steel-cage-modal-close-btn", className="me-2", color="secondary"),
            dbc.Button("确认", id="steel-cage-modal-confirm-btn", color="primary"),
        ]),
        html.Div(id="steel-cage-result-container", className="mt-4"),
    ],
    id="steel-cage-parameter-modal",
    size="lg",
    is_open=False,
    style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"}
)


#创建模态窗口函数
def create_input_field(id_prefix, label):
    return html.Div([
        html.Label(label, className="mb-1"),
        dbc.Input(
            id=f"{id_prefix}-{label.replace(' ', '-').lower()}",
            type="text",
            placeholder="请输入",
            className="mb-3"
        )
    ])
#钢筋笼+钢覆面施工模式模态窗口
def create_steel_cage_plus_modal():
    return  dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("钢筋笼+钢覆面施工模式参数配置"), close_button=True),
        dbc.ModalBody([
            html.H5("主体钢筋材料", className="mt-3 mb-3"),
            html.Div([
                 html.Div([
                    create_input_field("cage-steel-plus", cage_steel_materials[0]),
                    create_input_field("cage-steel-plus", cage_steel_materials[2]),
                    create_input_field("cage-steel-plus", cage_steel_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-steel-plus", cage_steel_materials[1]),
                    create_input_field("cage-steel-plus", cage_steel_materials[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 连接材料部分
            html.H5("连接材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-connection-plus", cage_connection_materials[0]),
                    create_input_field("cage-connection-plus", cage_connection_materials[2]),
                    create_input_field("cage-connection-plus", cage_connection_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-connection-plus", cage_connection_materials[1]),
                    create_input_field("cage-connection-plus", cage_connection_materials[3]),
                    create_input_field("cage-connection-plus", cage_connection_materials[5]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 工装系统部分
            html.H5("工装系统", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-tool-plus", cage_tool_materials[0]),
                    create_input_field("cage-tool-plus", cage_tool_materials[2]),
                    create_input_field("cage-tool-plus", cage_tool_materials[4]),
                    create_input_field("cage-tool-plus", cage_tool_materials[6]),
                    create_input_field("cage-tool-plus", cage_tool_materials[8]),
                    create_input_field("cage-tool-plus", cage_tool_materials[10]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-tool-plus", cage_tool_materials[1]),
                    create_input_field("cage-tool-plus", cage_tool_materials[3]),
                    create_input_field("cage-tool-plus", cage_tool_materials[5]),
                    create_input_field("cage-tool-plus", cage_tool_materials[7]),
                    create_input_field("cage-tool-plus", cage_tool_materials[9]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 施工辅助材料部分
            html.H5("施工辅助材料", className="mt-4 mb-3"),
            html.Div([
                 html.Div([
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[0]),
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[3]),
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[5]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[1]),
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[2]),
                    create_input_field("cage-auxiliary-plus", cage_auxiliary_materials[4]),
                ], className="col-md-6"),
            ]),
            # 机械设备部分
            html.H5("机械设备", className="mt-4 mb-3"),
             html.Div([
                html.Div([
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[0]),
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[2]),
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[4]),
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[6]),
                    create_input_field("cage-equipment-plus", lifting_lock[0]),
                    create_input_field("cage-equipment-plus", lifting_lock[2]),
                    create_input_field("cage-equipment-plus", lifting_lock[4]),
                    create_input_field("cage-equipment-plus", lifting_lock[6]),
                    create_input_field("cage-equipment-plus", lifting_lock[8]),
                    create_input_field("cage-equipment-plus", lifting_lock[10]),
                    ],className="col-md-6"),
                    
                html.Div([
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[1]),
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[3]),
                    create_input_field("cage-equipment-plus", cage_mechanical_equipment[5]),
                    create_input_field("cage-equipment-plus", lifting_lock[1]),
                    create_input_field("cage-equipment-plus", lifting_lock[3]),
                    create_input_field("cage-equipment-plus", lifting_lock[5]),
                    create_input_field("cage-equipment-plus", lifting_lock[7]),
                    create_input_field("cage-equipment-plus", lifting_lock[9]),
                ], className="col-md-6"),
            ], className="row"),
             # 连接材料部分
            html.H5("连接材料及焊接材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("connection-plus", connection_materials[0]),
                    create_input_field("connection-plus", connection_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 钢覆面材料部分
            html.H5("钢覆面材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cover-plus", steel_cover_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cover-plus", steel_cover_materials[1]),
                    create_input_field("cover-plus", steel_cover_materials[2]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 埋件材料部分
            html.H5("埋件材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("embed-plus", embedding_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("embed-plus", embedding_materials[1]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("embed-plus", embedding_materials[2]),
                ], className="col-md-6"),
            ], className="row"),
            # 其他费用部分
            html.H5("其他费用", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-other-plus", "模块吊装工装设计费"),
                    create_input_field("cage-other-plus", "无损检测"),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("cage-other-plus", "钢结构验收"),
                    create_input_field("cage-other-plus", "钢筋预埋件验收"),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("cage-plus-others", others[0]),
                    create_input_field("cage-plus-others", others[1]),
                ], className="col-md-6"),
            ], className="row"),
        ], style={"max-height": "70vh", "overflow-y": "auto"}),
        dbc.ModalFooter([
            dbc.Button("取消", id="steel-cage-plus-modal-cancel", className="me-2", color="secondary"),
            dbc.Button("确认", id="steel-cage-plus-modal-submit", color="primary"),
        ]),
        html.Div(id="steel-cage-plus-result-container", className="mt-4"),
    ],
    id="steel-cage-plus-modal",
    size="lg",
    is_open=False,
    style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"},
)
    

#叠合板模块化模态窗口
def create_modular_composite_plate_modal():
    return dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("叠合板模块化施工参数配置"), close_button=True),
        dbc.ModalBody([
            # 预制构件材料部分
            html.H5("预制构件材料", className="mt-3 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("prefab", prefab_materials[0]),
                    create_input_field("prefab", prefab_materials[2]),
                    create_input_field("prefab", prefab_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("prefab", prefab_materials[1]),
                    create_input_field("prefab", prefab_materials[3]),
                    create_input_field("prefab", prefab_materials[5]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 二次浇筑材料部分
            html.H5("二次浇筑材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("casting", secondary_casting_materials[0]),
                    create_input_field("casting", secondary_casting_materials[2]),
                    create_input_field("casting", secondary_casting_materials[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("casting", secondary_casting_materials[1]),
                    create_input_field("casting", secondary_casting_materials[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 支撑系统部分
            html.H5("支撑系统", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("support", support_materials[0]),
                    create_input_field("support", support_materials[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("support", support_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 场地材料部分
            html.H5("场地材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("embed", place_materials[0]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 预制场地设施
            html.H5("预制场地设施", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("waterproof", Prefabricated_site_facilities[0]),
                    create_input_field("waterproof", Prefabricated_site_facilities[2]),
                    create_input_field("waterproof", Prefabricated_site_facilities[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("waterproof", Prefabricated_site_facilities[1]),
                    create_input_field("waterproof", Prefabricated_site_facilities[3]),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("modular-composite-plate-others", others[0]),
                    create_input_field("modular-composite-plate-others", others[1]),
                ], className="col-md-6"),
            ], className="row"),
        ], style={"max-height": "70vh", "overflow-y": "auto"}),
        dbc.ModalFooter([
            dbc.Button("取消", id="modular-composite-plate-modal-cancel", className="me-2", color="secondary"),
            dbc.Button("确认", id="modular-composite-plate-modal-submit", color="primary"),
        ]),
         html.Div(id="composite-plate-result-container", className="mt-4"),
    ],
    id="modular_composite_plate_modal",
    size="lg",
    is_open=False,
    style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"}
)

def create_c403_c409_content():
    return [
        # 主体钢筋材料部分 - C403、C409专用
        html.H5("主体钢筋材料 (1、2)", className="mt-3 mb-3"),
        html.Div([
            html.Div([
                create_input_field("c403-rebar", "钢筋制作安装"),
                create_input_field("c403-rebar", rebar_materials[2]),
            ], className="col-md-6"),
            html.Div([
                create_input_field("c403-rebar", rebar_materials[1]),
                create_input_field("c403-rebar", rebar_materials[3]),
            ], className="col-md-6"),
        ], className="row"),
        
        # C403、C409专用的其他部分
        html.H5("1、2专用混凝土材料", className="mt-4 mb-3"),
        html.Div([
            html.Div([
                create_input_field("c403-concrete", concrete_materials[0]),
            ], className="col-md-6"),
        ], className="row"),

            # 模板及支撑材料部分
            html.H5("模板及支撑材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-formwork", formwork_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c403-tunnel-formwork", formwork_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 埋件及连接材料部分
            html.H5("埋件及连接材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-embed", tunnel_embedding_materials[0]),
                    create_input_field("c403-tunnel-embed", tunnel_embedding_materials[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c403-tunnel-embed", tunnel_embedding_materials[1]),
                    create_input_field("c403-tunnel-embed", tunnel_embedding_materials[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 防水及接缝材料部分
            html.H5("防水及接缝材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-waterproof", tunnel_waterproof_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c403-tunnel-waterproof", tunnel_waterproof_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 施工处理材料部分
            html.H5("施工处理材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-construction", construction_materials[0]),
                ], className="col-md-6"),
            ], className="row"),
            # 预制场地设施部分
            html.H5("预制场地设施", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[0]),
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[2]),
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[4]),
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[6]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[1]),
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[3]),
                    create_input_field("c403-tunnel-site", tunnel_site_facilities[5]),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("机械设备", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-tunnel-equipment", tunnel_equipment[0]),
                    create_input_field("c403-tunnel-equipment", tunnel_equipment[2]),
                    create_input_field("c403-tunnel-equipment", tunnel_equipment[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c403-tunnel-equipment", tunnel_equipment[1]),
                    create_input_field("c403-tunnel-equipment", tunnel_equipment[3]),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c403-others", others[0]),
                    create_input_field("c403-others", others[1]),
                ], className="col-md-6"),
            ], className="row"),
    ]

def create_c404_content():
    return [
        # 主体钢筋材料部分 - C404专用
        html.H5("主体钢筋材料 (C404)", className="mt-3 mb-3"),
        html.Div([
            html.Div([
                create_input_field("c404-rebar", rebar_materials[0]),
                create_input_field("c404-rebar", rebar_materials[2]),
            ], className="col-md-6"),
            html.Div([
                create_input_field("c404-rebar", rebar_materials[1]),
                create_input_field("c404-rebar", rebar_materials[3]),
            ], className="col-md-6"),
        ], className="row"),
        
        # C404专用的其他部分
        html.H5("C404专用混凝土材料", className="mt-4 mb-3"),
        html.Div([
            html.Div([
                create_input_field("c404-concrete", concrete_materials[0]),
            ], className="col-md-6"),
        ], className="row"),
            # 模板及支撑材料部分
            html.H5("模板及支撑材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-formwork", formwork_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c404-tunnel-formwork", formwork_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 埋件及连接材料部分
            html.H5("埋件及连接材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-embed", c404_tunnel_embedding_materials[0]),
                    create_input_field("c404-tunnel-embed", c404_tunnel_embedding_materials[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c404-tunnel-embed", c404_tunnel_embedding_materials[1]),
                    create_input_field("c404-tunnel-embed", c404_tunnel_embedding_materials[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 防水及接缝材料部分
            html.H5("防水及接缝材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-waterproof", tunnel_waterproof_materials[0]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c404-tunnel-waterproof", tunnel_waterproof_materials[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 施工处理材料部分
            html.H5("施工处理材料", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-construction", construction_materials[0]),
                ], className="col-md-6"),
            ], className="row"),
            # 预制场地设施部分
            html.H5("预制场地设施", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[0]),
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[2]),
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[4]),
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[6]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[1]),
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[3]),
                    create_input_field("c404-tunnel-site", tunnel_site_facilities[5]),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("机械设备", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-tunnel-equipment", tunnel_equipment[0]),
                    create_input_field("c404-tunnel-equipment", tunnel_equipment[2]),
                    create_input_field("c404-tunnel-equipment", tunnel_equipment[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("c404-tunnel-equipment", tunnel_equipment[1]),
                    create_input_field("c404-tunnel-equipment", tunnel_equipment[3]),
                ], className="col-md-6"),
            ], className="row"),
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("c404-others", others[0]),
                    create_input_field("c404-others", others[1]),
                ], className="col-md-6"),
            ], className="row"),
    ]

# 创建通用部分内容
def create_common_content():
    return [
        # 机械设备部分 - 两种类型通用
        html.H5("机械设备", className="mt-4 mb-3"),
        html.Div([
                html.Div([
                    create_input_field("common-tunnel-equipment", tunnel_equipment[0]),
                    create_input_field("common-tunnel-equipment", tunnel_equipment[2]),
                    create_input_field("common-tunnel-equipment", tunnel_equipment[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("common-tunnel-equipment", tunnel_equipment[1]),
                    create_input_field("common-tunnel-equipment", tunnel_equipment[3]),
                ], className="col-md-6"),
            ], className="row"),
    ]


#管廊施工模式模态窗口
# 修改模态窗口创建函数
def create_tunnel_model_modal():
    return dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("管廊叠合板模块化施工参数配置"), close_button=True),
        dbc.ModalBody([
            # 管廊类型选择
            html.H5("管廊类型", className="mt-3 mb-3"),
            dbc.RadioItems(
                options=[
                    {"label": "1、2叠合板 ", "value": "c403_c409"},
                    {"label": "3叠合板 ", "value": "c404"},
                ],
                value="c403_c409",
                id="tunnel-type",
                inline=True,
                className="mb-4"
            ),
            
            # 预先创建C403/C409内容，默认显示
            html.Div(
                create_c403_c409_content(),
                id="c403-c409-content",
                style={"display": "block"}  # 默认显示
            ),
            
            # 预先创建C404内容，默认隐藏
            html.Div(
                create_c404_content(),
                id="c404-content",
                style={"display": "none"}  # 默认隐藏
            ),
            
            # 通用内容容器
            # html.Div(
            #     create_common_content(),
            #     id="tunnel-common-content"
            # ),
            
        ], style={"max-height": "70vh", "overflow-y": "auto"}),
        dbc.ModalFooter([
            dbc.Button("取消", id="tunnel-modal-cancel1", className="me-2", color="secondary",style={"display": "block"}),
            dbc.Button("确认", id="tunnel-modal-submit1", color="primary",style={"display": "block"}),
            dbc.Button("取消", id="tunnel-modal-cancel2", className="me-2", color="secondary",style={"display": "none"}),
            dbc.Button("确认", id="tunnel-modal-submit2", color="primary",style={"display": "none"}),
        ]),
        html.Div(id="tunnel-result-container", className="mt-4"),
        
    ],
    id="tunnel-modal",
    size="lg",
    is_open=False,
    style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"}
    )



# 创建参数表单组件函数
# 在modals.py中修改create_parameter_form函数
def create_parameter_form(param_id, is_first=False):
    return html.Div(
        [
            # 参数ID（隐藏字段）
            dcc.Store(id={'type': 'param-id', 'index': param_id}, data=param_id),
            
            # 添加价格数据存储组件 - 这是关键修改部分
            dcc.Store(id={'type': 'direct-labor-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'direct-material-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'direct-machine-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'modular-labor-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'modular-material-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'modular-machine-price', 'index': param_id}, data=0),
            
            # 删除按钮（非首个参数才显示）
            html.Div(
                html.Button(
                    '×',
                    id={'type': 'delete-param', 'index': param_id},
                    className='btn btn-sm btn-outline-danger position-absolute top-0 end-0',
                    style={'display': 'none' if is_first else 'block', 'borderRadius': '50%', 'width': '24px', 'height': '24px', 'padding': '0'}
                ),
                className='position-relative',
                style={'textAlign': 'right'}
            ),
            


                        # 在界面中添加这个组件
            html.Div([
                html.H5("参数查询", className="mt-4 mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("参数类型", className="form-label"),
                        dcc.Dropdown(
                            id="query-param-type",
                            options=[{'label': t, 'value': t} for t in param_types],
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("参数名称(可选)", className="form-label"),
                        dcc.Input(
                            id="query-param-name",
                            type="text",
                            placeholder="输入关键词筛选",
                            className="form-control mb-3"
                        )
                    ], width=6),
                    # 参数数值 - 新增的输入框
                dbc.Col([
                    html.Label("参数数值", className="form-label"),
                    dcc.Input(
                        id={'type': 'param-quantity', 'index': param_id},
                        type="number",
                        placeholder="请输入数值",
                        className="form-control mb-3"
                    )
                ], width=4),
                
                # 单位
                dbc.Col([
                    html.Label("单位", className="form-label"),
                    dcc.Dropdown(
                        id={'type': 'param-unit', 'index': param_id},
                        options=[{'label': u, 'value': u} for u in units],
                        placeholder="选择单位",
                        className="mb-3"
                    )
                ], width=4)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("查询价格数据", id="price-query-btn", color="primary", className="mb-3"),
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button("保存价格数据", id="save-price-data-btn", color="success", className="mb-3"),
                    ], width="auto", className="ms-auto")  # ms-auto使这一列靠右对齐
                ]),
                html.Div(id="price-results-container"),
                html.Div(id="selection-output", className="mt-4")  # 添加这一行来显示选择结果
            ], className="mt-4"),


        
            # 添加自定义参数表格组件
            create_custom_parameters_form(),


            # 分隔线
            html.Hr()
        ],
        id={'type': 'param-container', 'index': param_id},
        className='mb-3 position-relative'
    )

def create_diy_data_modal():
    return html.Div(
    [
        # 存储新参数的触发器
        dcc.Store(id='add-param-trigger', data=0),
        
        # 存储所有参数ID
        dcc.Store(id='param-ids', data=[DEFAULT_PARAM_ID]),
        
        # 存储表单数据
        dcc.Store(id='form-data', data={}),
        
        # 自定义参数模态窗口
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle('自定义模式配置'),
                    close_button=True
                ),
                
                dbc.ModalBody(
                    [  
                        # 工程基本信息
                        html.H5('工程基本信息', className='text-primary mb-3'),
                        
                        # 工程名称
                        html.Div(
                            [
                                html.Label('工程名称', className='form-label'),
                                dcc.Input(
                                    id='project-name',
                                    type='text',
                                    placeholder='请输入工程名称',
                                    className='form-control'
                                )
                            ],
                            className='mb-3'
                        ),
                        # 备注说明
                        html.Div(
                            [
                                html.Label('备注说明', className='form-label'),
                                dcc.Textarea(
                                    id={'type': 'project-notes'},
                                    placeholder='请输入施工模式的说明',
                                    className='form-control',
                                    style={'height': '80px'}
                                )
                            ],
                            className='mb-3'
                        ),
                        
                        # 工程类型
                        html.Div(
                            [
                                html.Label('工程类型', className='form-label'),
                                dcc.Dropdown(
                                    id='project-type',
                                    options=[{'label': t, 'value': t} for t in project_types],
                                    value=project_types[0],
                                    clearable=False,
                                    className='form-select'
                                )
                            ],
                            className='mb-3'
                        ),
                        
                        # 工程量和单位（一行两列）
                        html.Div(
                            [
                                # 工程量
                                html.Div(
                                    [
                                        html.Label('工程量', className='form-label'),
                                        dcc.Input(
                                            id='project-amount',
                                            type='number',
                                            placeholder='请输入数值',
                                            className='form-control'
                                        )
                                    ],
                                    className='col-9'
                                ),
                                
                                # 单位
                                html.Div(
                                    [
                                        html.Label('单位', className='form-label'),
                                        dcc.Dropdown(
                                            id='amount-unit',
                                            options=[{'label': u, 'value': u} for u in units],
                                            value=units[2],  # 默认为'm³'
                                            clearable=False,
                                            className='form-select'
                                        )
                                    ],
                                    className='col-3'
                                )
                            ],
                            className='row mb-3'
                        ),
                        
                        # 工日数（一行两列）
                        html.Div(
                            [
                                # 正常施工需要的工日数
                                html.Div(
                                    [
                                        html.Label('正常施工需要的工日数', className='form-label'),
                                        dcc.Input(
                                            id='normal-days',
                                            type='number',
                                            placeholder='请输入',
                                            className='form-control'
                                        )
                                    ],
                                    className='col-6'
                                ),
                                
                                # 模块化施工需要的工日数
                                html.Div(
                                    [
                                        html.Label('模块化施工需要的工日数', className='form-label'),
                                        dcc.Input(
                                            id='modular-days',
                                            type='number',
                                            placeholder='请输入',
                                            className='form-control'
                                        )
                                    ],
                                    className='col-6'
                                )
                            ],
                            className='row mb-3'
                        ),
                        
                        html.Hr(),
                        
                        # 参数信息
                        html.H5('参数信息', className='text-primary mb-3'),
                        
                        # 参数查询
                        html.Div([
                            html.H6("参数查询", className="mt-4 mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("参数类型", className="form-label"),
                                    dcc.Dropdown(
                                        id="query-param-type",
                                        options=[{'label': t, 'value': t} for t in param_types],
                                        className="mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("参数名称(可选)", className="form-label"),
                                    dcc.Input(
                                        id="query-param-name",
                                        type="text",
                                        placeholder="输入关键词筛选",
                                        className="form-control mb-3"
                                    )
                                ], width=6),
                            ]),
                            # 添加参数数值和单位输入框
                            dbc.Row([
                                dbc.Col([
                                    html.Label("参数数值", className="form-label"),
                                    dcc.Input(
                                        id={'type': 'param-quantity', 'index': 0},
                                        type="number",
                                        placeholder="请输入数值",
                                        className="form-control mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("单位", className="form-label"),
                                    dcc.Dropdown(
                                        id={'type': 'param-unit', 'index': 0},
                                        options=[{'label': u, 'value': u} for u in units],
                                        placeholder="选择单位",
                                        className="mb-3"
                                    )
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("查询价格数据", id="price-query-btn", color="primary", className="mb-3"),
                                ], width="auto"),
                                dbc.Col([
                                    dbc.Button("保存价格数据", id="save-price-data-btn", color="success", className="mb-3"),
                                ], width="auto", className="ms-auto")
                            ]),
                            html.Div(id="price-results-container"),
                            html.Div(id="selection-output", className="mt-4")
                        ], className="mb-4"),
                        
                        # 自定义参数表单
                        html.Div([
                            html.H6("自定义参数", className="mb-3"),
                            
                            # 修复ID不匹配问题：使用 params-container
                            html.Div(id="params-container", children=[
                                # 初始参数表单
                                create_parameter_form_row(0)
                            ]),
                            
                            # 添加参数按钮
                            html.Div([
                                dbc.Button("清空", id="clear-params-btn", color="secondary", outline=True)
                            ], className="d-flex justify-content-end mt-3 mb-4"),
                            
                            # 保存按钮
                            dbc.Button("保存自定义参数", id="save-custom-params-btn", color="success"),
                            
                            # 结果提示区域
                            html.Div(id="custom-params-save-result", className="mt-3")
                        ])
                    ],
                    style={"max-height": "70vh", "overflow-y": "auto"}  # 添加滚动
                ),
                
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            '取消',
                            id='diy-cancel-button',
                            color='light',
                            className='me-2'
                        ),
                        dbc.Button(
                            '确认',
                            id='diy-confirm-button',
                            color='primary'
                        )
                    ]
                )
            ],
            id='diy-custom-param-modal',
            size='xl',  # 改为xl以提供更多空间
            is_open=False,
        ),
        
    ],
    style={'margin': '0', 'padding': '0'}  # 移除 className='p-5' 并设置零边距
)

def create_custom_params_table(parameters):
    """
    创建自定义参数表格
    
    Args:
        parameters (list): 参数列表
            
    Returns:
        dash_table.DataTable: 参数表格组件
    """
    if not parameters:
        return html.Div("无参数数据", className="text-muted")
    
    # 准备表格数据
    table_data = []
    for param in parameters:
        table_data.append({
            "参数名称": param.get("name", ""),
            "参数类型": param.get("type", ""),
            "参数值": param.get("value", 0),
            "单位": param.get("unit", ""),
            "价格": param.get("price", 0),  # 添加价格列
            "描述": param.get("description", ""),
            "输入值": ""  # 添加输入值列
        })
    
    # 创建表格列
    columns = [
        {"name": "参数名称", "id": "参数名称"},
        {"name": "参数类型", "id": "参数类型"},
        {"name": "默认值", "id": "参数值", "type": "numeric", "format": {"specifier": ",.2f"}},
        {"name": "单位", "id": "单位"},
        {"name": "价格", "id": "价格", "type": "numeric", "format": {"specifier": ",.2f"}},  # 添加价格列
        {"name": "描述", "id": "描述"},
        {"name": "输入值", "id": "输入值", "presentation": "input"}
    ]
    
    # 创建表格
    return dash_table.DataTable(
        id="custom-params-table",
        columns=columns,
        data=table_data,
        editable=True,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': '#f0f8ff',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        # 每个单元格的输入框
        column_id_input_map={
            "输入值": {"type": "numeric", "id": {"type": "param-input", "index": "{{row_index}}"}}
        }
    )





# 在 modals.py 中添加通知模态窗口组件
def create_notification_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("通知")),
            dbc.ModalBody(html.Div(id="notification-message")),
            dbc.ModalFooter(
                dbc.Button("确定", id="close-notification", className="ms-auto")
            ),
        ],
        id="notification-modal",
        is_open=False,
    )

# 然后在应用的布局中引入这个组件
# app.layout = html.Div([
#     ...其他组件...,
#     create_notification_modal(),
# ])

###################################################################
####创建参数表格函数
def create_params_table(parameters):
    """
    创建简化的工程参数明细表格 - 只显示关键信息
    
    Args:
        parameters (list): 参数列表
            
    Returns:
        dash_table.DataTable: 参数表格组件
    """
    if not parameters:
        return html.Div("无参数数据", className="text-muted")
    
    # 准备简化的表格数据
    table_data = []
    for param in parameters:
        table_data.append({
            "参数类别": param.get("type", ""),
            "工程参数": param.get("name", ""),
            "数量": param.get("value", 0),
            "单位": param.get("unit", ""),
            "直接施工总价": param.get("direct_total_price", 0),
            "模块化施工总价": param.get("modular_total_price", 0),
            #"价格差异": param.get("price_difference", 0),
            "备注": param.get("description", "")
        })
    
    # 创建简化的表格
    return dash_table.DataTable(
        id="custom-params-table",
        columns=[
            {"name": "参数类别", "id": "参数类别"},
            {"name": "工程参数", "id": "工程参数"},
            {"name": "数量", "id": "数量", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "单位", "id": "单位"},
            {"name": "直接施工总价", "id": "直接施工总价", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "模块化施工总价", "id": "模块化施工总价", "type": "numeric", "format": {"specifier": ",.2f"}},
            #{"name": "价格差异", "id": "价格差异", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "备注", "id": "备注"}
        ],
        data=table_data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': '#f0f8ff',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        #style_data_conditional=[
        #    {
        #        'if': {'column_id': 'price_difference', 'filter_query': '{价格差异} < 0'},
        #        'color': 'green',
        #    },
        #    {
        #        'if': {'column_id': 'price_difference', 'filter_query': '{价格差异} > 0'},
        #        'color': 'red',
        #    }
        #]
    )


# 创建自定义模式详细信息模态窗口
def create_custom_mode_detail_modal():
    """
    创建显示自定义模式详细信息和参数的模态窗口
    
    Returns:
        dbc.Modal: 模态窗口组件
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("自定义模式详细信息"), close_button=True),
            dbc.ModalBody([
                # 存储当前模式ID
                dcc.Store(id="custom-mode-detail-id-store", data=None),
                
                # 项目基本信息
                html.Div([
                    html.H5("项目信息", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.P("项目名称：", className="font-weight-bold mb-1"),
                            html.P(id="custom-mode-name", className="mb-3"),
                            
                            html.P("项目类型：", className="font-weight-bold mb-1"),
                            html.P(id="custom-mode-type", className="mb-3"),
                        ], width=6),
                        dbc.Col([
                            html.P("工程量：", className="font-weight-bold mb-1"),
                            html.P(id="custom-mode-value", className="mb-3"),
                            
                            html.P("施工工期：", className="font-weight-bold mb-1"),
                            html.P(id="custom-mode-days", className="mb-3"),
                        ], width=6),
                    ]),
                    html.P("项目描述：", className="font-weight-bold mb-1"),
                    html.P(id="custom-mode-description", className="mb-3"),
                ], className="mb-4"),
                
                # 参数列表
                html.Div([
                    html.H5("参数列表", className="mb-3"),
                    html.Div(id="custom-mode-params-container")
                ]),
                
                # 计算结果区域
                html.Div(id="custom-mode-result-container", className="mt-4"),
            ], style={"max-height": "70vh", "overflow-y": "auto"}),
            dbc.ModalFooter([
                dbc.Button("取消", id="custom-mode-close-btn", className="me-2", color="secondary"),
                dbc.Button("计算", id="custom-mode-calculate-btn", color="primary"),
            ]),
        ],
        id="custom-mode-detail-modal",
        size="lg",
        is_open=False,
        style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"}
    )

# 在现有的 modals.py 文件中添加以下函数

def create_custom_parameters_form():
    """创建使用独立表单字段的自定义参数表"""
    return html.Div([
        html.H5("自定义参数", className="mt-4 mb-3"),
        
        # 参数容器 - 可以通过回调添加多个
        html.Div(id="params-container", children=[
            # 初始参数表单
            create_parameter_form_row(0)
        ]),
        
        # 添加参数按钮
        html.Div([
            #dbc.Button("+ 添加参数", id="add-param-btn", color="primary", outline=True, className="me-2"),
            dbc.Button("清空", id="clear-params-btn", color="secondary", outline=True)
        ], className="d-flex justify-content-end mt-3 mb-4"),
        
        # 保存按钮
        dbc.Button("保存自定义参数", id="save-custom-params-btn", color="success"),
        
        # 结果提示区域
        html.Div(id="custom-params-save-result", className="mt-3")
    ])

# 创建单个参数表单行
def create_parameter_form_row(index):
    """创建单个参数表单行"""
    return html.Div([
        dbc.Row([
            # 参数名称
            dbc.Col([
                html.Label("参数名称", className="form-label"),
                dbc.Input(
                    id={"type": "param-name", "index": index},
                    type="text",
                    placeholder="输入参数名称",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 参数类别
            dbc.Col([
                html.Label("参数类别", className="form-label"),
                dcc.Dropdown(
                    id={"type": "param-type", "index": index},
                    options=[{'label': t, 'value': t} for t in param_types],
                    placeholder="选择类别",
                    clearable=False,
                    className="mb-2"
                )
            ], width=6),
        ]),
        
        dbc.Row([
            # 参数值
            dbc.Col([
                html.Label("参数值", className="form-label"),
                dbc.Input(
                    id={"type": "param-value", "index": index},
                    type="number",
                    placeholder="输入数值",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 单位
            dbc.Col([
                html.Label("单位", className="form-label"),
                dcc.Dropdown(
                    id={"type": "param-unit", "index": index},
                    options=[{'label': u, 'value': u} for u in units],
                    placeholder="选择单位",
                    clearable=False,
                    className="mb-2"
                )
            ], width=6),
        ]),
        
        dbc.Row([
            # 直接施工人工单价
            dbc.Col([
                html.Label("直接施工人工单价", className="form-label"),
                dbc.Input(
                    id={"type": "direct-labor-price", "index": index},
                    # id=f"direct-labor-price-{index}",
                    type="number",
                    placeholder="0.00",
                    value=0,  # 添加默认值很重要
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 直接施工材料单价
            dbc.Col([
                html.Label("直接施工材料单价", className="form-label"),
                dbc.Input(
                    id={"type": "direct-material-price", "index": index},
                    # id=f"direct-material-price-{index}",  # 使用唯一的ID
                    type="number",
                    value=0,  # 添加默认值很重要
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
        ]),
        
        dbc.Row([
            # 直接施工机械单价
            dbc.Col([
                html.Label("直接施工机械单价", className="form-label"),
                dbc.Input(
                    id={"type": "direct-machine-price", "index": index},
                    # id=f"direct-machine-price-{index}",
                    type="number",
                    value=0,  # 添加默认值很重要
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 模块化施工人工单价
            dbc.Col([
                html.Label("模块化施工人工单价", className="form-label"),
                dbc.Input(
                    id={"type": "modular-labor-price", "index": index},
                    # id=f"modular-labor-price-{index}",
                    type="number",
                    value=0,  # 添加默认值很重要
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
        ]),
        
        dbc.Row([
            # 模块化施工材料单价
            dbc.Col([
                html.Label("模块化施工材料单价", className="form-label"),
                dbc.Input(
                    id={"type": "modular-material-price", "index": index},
                    # id=f"modular-material-price-{index}",
                    type="number",
                    value=0,  # 添加默认值很重要
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 模块化施工机械单价
            dbc.Col([
                html.Label("模块化施工机械单价", className="form-label"),
                dbc.Input(
                    id={"type": "modular-machine-price", "index": index},
                    # id=f"modular-machine-price-{index}",
                    type="number",
                    value=0,  # 添加默认值很重要
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
        ]),
        
        # # 删除按钮 (第一行不显示)
        # html.Div([
        #     dbc.Button(
        #         "删除", 
        #         id={"type": "remove-param", "index": index},
        #         color="danger",
        #         outline=True,
        #         size="sm",
        #         className="mb-4"
        #     )
        # ], className="d-flex justify-content-end", style={"display": "none" if index == 0 else "block"}),
        
        # 分隔线
        html.Hr(className="my-3")
    ], id={"type": "param-row", "index": index}, className="mb-3 param-row")


# 创建删除确认模态窗口
def create_delete_confirmation_modal():
    """创建删除确认模态窗口"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("确认删除"), close_button=True),
            dbc.ModalBody([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", 
                           style={"color": "#dc3545", "fontSize": "2rem", "marginRight": "10px"}),
                    html.Span("确定要删除此自定义模式吗？", style={"fontSize": "1.1rem"})
                ], className="d-flex align-items-center mb-3"),
                html.P("项目名称：", className="mb-1 font-weight-bold"),
                html.P(id="delete-project-name", className="mb-3 text-primary"),
                html.P("此操作将删除项目的所有信息和参数，且无法恢复。", 
                       className="text-danger small"),
                # 存储要删除的项目ID
                dcc.Store(id="delete-project-id-store", data=None)
            ]),
            dbc.ModalFooter([
                dbc.Button("取消", id="cancel-delete-btn", className="me-2", color="secondary"),
                dbc.Button("确认删除", id="confirm-delete-btn", color="danger"),
            ]),
        ],
        id="delete-confirmation-modal",
        is_open=False,
        centered=True
    )


def create_steel_lining_parameter_modal2():
    """创建钢衬里施工模式参数配置模态窗口 - 完善版本"""
    return dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("钢衬里施工模式参数配置"), close_button=True),
        dbc.ModalBody([
            # 基础结构类部分
            html.H5("基础结构", className="mt-3 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-foundation", steel_lining_foundation[0]),
                    create_input_field("steel-lining-foundation", steel_lining_foundation[2]),
                    create_input_field("steel-lining-foundation", steel_lining_foundation[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("steel-lining-foundation", steel_lining_foundation[1]),
                    create_input_field("steel-lining-foundation", steel_lining_foundation[3]),
                    create_input_field("steel-lining-foundation", steel_lining_foundation[5]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 结构构件类部分
            html.H5("结构构件", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-structure", steel_lining_structure[0]),
                    create_input_field("steel-lining-structure", steel_lining_structure[2]),
                    create_input_field("steel-lining-structure", steel_lining_structure[4]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("steel-lining-structure", steel_lining_structure[1]),
                    create_input_field("steel-lining-structure", steel_lining_structure[3]),
                    create_input_field("steel-lining-structure", steel_lining_structure[5]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 辅助设施类部分
            html.H5("辅助设施", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-auxiliary", steel_lining_auxiliary[0]),
                    create_input_field("steel-lining-auxiliary", steel_lining_auxiliary[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("steel-lining-auxiliary", steel_lining_auxiliary[1]),
                    create_input_field("steel-lining-auxiliary", steel_lining_auxiliary[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 机械设备类部分
            html.H5("机械设备", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-equipment", steel_lining_equipment[0]),
                    create_input_field("steel-lining-equipment", steel_lining_equipment[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("steel-lining-equipment", steel_lining_equipment[1]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 钢网架系统部分
            html.H5("钢网架系统", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-frame", steel_lining_frame[0]),
                    create_input_field("steel-lining-frame", steel_lining_frame[2]),
                ], className="col-md-6"),
                html.Div([
                    create_input_field("steel-lining-frame", steel_lining_frame[1]),
                    create_input_field("steel-lining-frame", steel_lining_frame[3]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 试验检测部分
            html.H5("试验检测", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-testing", steel_lining_testing[0]),
                ], className="col-md-6"),
            ], className="row"),
            
            # 间接施工费部分
            html.H5("间接施工费", className="mt-4 mb-3"),
            html.Div([
                html.Div([
                    create_input_field("steel-lining-others", "间接施工费（直接施工）"),
                    create_input_field("steel-lining-others", "间接施工费（模块化施工）"),
                ], className="col-md-6"),
            ], className="row"),
            
        ], style={"max-height": "70vh", "overflow-y": "auto"}),
        dbc.ModalFooter([
            dbc.Button("取消", id="steel-lining-modal-close-btn", className="me-2", color="secondary"),
            dbc.Button("计算成本", id="steel-lining-modal-confirm-btn", color="primary"),
        ]),
        
        # 结果显示容器 - 这里是关键，确保结果能正确显示
        html.Div(id="steel-lining-result-container", className="mt-4"),
    ],
    id="steel-lining-parameter-modal",
    size="xl",  # 改为xl以确保有足够空间显示结果表格
    is_open=False,
    style={"font-family": "Arial, 'Microsoft YaHei', sans-serif"}
)