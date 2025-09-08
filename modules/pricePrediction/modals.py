import dash
from dash import dcc, html ,dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# 导入配置
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG

# modules/pricePrediction/modals.py (您提供的代码，确保ID为 steel-lining-parameter-modal2)

# 禁用字段的样式定义
DISABLED_FIELD_STYLE = {
    'backgroundColor': '#f8f9fa',
    'color': '#6c757d',
    'border': '1px solid #dee2e6',
    'cursor': 'not-allowed'
}

DISABLED_SECTION_STYLE = {
    'backgroundColor': '#f8f9fa',
    'border': '1px solid #dee2e6',
    'borderRadius': '5px',
    'padding': '10px',
    'marginBottom': '15px'
}

WARNING_TEXT_STYLE = {
    'color': '#dc3545',
    'fontSize': '12px',
    'fontStyle': 'italic',
    'marginTop': '5px'
}

def create_disabled_field_warning(field_id, indicator_name):
    """创建禁用字段的警告提示组件"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-ban", style={'marginRight': '5px', 'color': '#dc3545'}),
            html.Span("已禁用", style={'color': '#dc3545', 'fontWeight': 'bold'}),
        ], style={'marginBottom': '3px'}),
        html.Div([
            html.Small(
                f"若启用请到数据管理模块修改「{indicator_name}」指标",
                style=WARNING_TEXT_STYLE
            )
        ])
    ], id=f"{field_id}-warning", style={'display': 'none'})  # 初始隐藏

def create_enhanced_input_field(field_id, placeholder_text, input_type="number", label_text=None):
    """创建增强的输入字段，支持禁用状态显示"""
    return html.Div([
        # 标签（如果提供）
        dbc.Label(label_text, style={'marginBottom': '5px'}) if label_text else None,
        
        # 输入框
        dbc.Input(
            id=field_id,
            type=input_type,
            placeholder=placeholder_text,
            style={'marginBottom': '5px'}
        ),
        
        # 禁用状态覆盖层
        html.Div([
            html.Div([
                html.I(className="fas fa-lock", style={'marginRight': '8px', 'color': '#dc3545'}),
                html.Span("已禁用", style={'color': '#dc3545', 'fontWeight': 'bold', 'fontSize': '14px'}),
            ], style={
                'position': 'absolute',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'zIndex': '10'
            })
        ], id=f"{field_id}-overlay", style={
            'position': 'absolute',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'backgroundColor': 'rgba(248, 249, 250, 0.9)',
            'borderRadius': '4px',
            'display': 'none',  # 初始隐藏
            'alignItems': 'center',
            'justifyContent': 'center'
        }),
        
        # 警告提示
        create_disabled_field_warning(field_id, "相关指标")
        
    ], style={'position': 'relative', 'marginBottom': '10px'})

# ... (create_steel_reinforcement_parameter_modal, create_custom_mode_parameter_modal, create_price_modification_modal 保持不变)

# 创建钢衬里参数模态窗口
def create_steel_lining_parameter_modal():
    """创建钢衬里施工模式参数设置模态窗口 - 支持字段状态控制"""
    return html.Div([
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("钢衬里施工模式参数配置"), close_button=True),
                dbc.ModalBody([
                    # 添加提示信息区域
                    html.Div([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle", style={'marginRight': '10px'}),
                            html.Span("若需解除字段禁用状态，请前往数据管理模块修改对应指标的启用状态")
                        ], color="info", style={
                            'marginBottom': '25px',
                            'fontSize': '14px',
                            'padding': '12px 16px',
                            'borderRadius': '6px',
                            'backgroundColor': '#e3f2fd',
                            'borderColor': '#2196f3',
                            'color': '#1565c0'
                        })
                    ]),
                    
                    # 1. 拼装场地工程量区域
                    html.Div([
                        html.Div([
                            html.H5("1. 拼装场地工程量", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "assembly-site-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-2 mb-3")
                    ], id="assembly-site-section", className="mb-4"),
                    
                    # 2. 制作胎具区域
                    html.Div([
                        html.Div([
                            html.H5("2. 制作胎具", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "fixture-making-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3")
                    ], id="fixture-making-section", className="mb-4"),
                    
                    # 3. 钢支墩、埋件区域
                    html.Div([
                        html.Div([
                            html.H5("3. 钢支墩、埋件", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "steel-support-embedded-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 钢支墩、埋件的子项
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-support-concrete-chiseling",
                                    "请输入",
                                    "number",
                                    "钢支墩、埋件混凝土剔凿"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-support-concrete-backfill",
                                    "请输入",
                                    "number",
                                    "钢支墩、埋件混凝土回填"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-support-installation",
                                    "请输入",
                                    "number",
                                    "钢支墩、埋件安装"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-support-depreciation",
                                    "请输入",
                                    "number",
                                    "钢支墩、埋件折旧"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="steel-support-section", className="mb-4"),
                    
                    # 4. 扶壁柱区域
                    html.Div([
                        html.Div([
                            html.H5("4. 扶壁柱", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "buttress-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 扶壁柱的子项
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "buttress-installation",
                                    "请输入",
                                    "number",
                                    "扶壁柱安装"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "buttress-removal",
                                    "请输入",
                                    "number",
                                    "扶壁柱拆除"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "buttress-component-depreciation",
                                    "请输入",
                                    "number",
                                    "扶壁柱构件使用折旧"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="buttress-section", className="mb-4"),
                    
                    # 5. 走道板及操作平台区域
                    html.Div([
                        html.Div([
                            html.H5("5. 走道板及操作平台", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "walkway-platform-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 走道板及操作平台的子项
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "walkway-platform-manufacturing",
                                    "请输入",
                                    "number",
                                    "走道板及操作平台制作"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "walkway-platform-erection",
                                    "请输入",
                                    "number",
                                    "走道板及操作平台搭设"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "walkway-platform-removal",
                                    "请输入",
                                    "number",
                                    "走道板及操作平台拆除"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="walkway-platform-section", className="mb-4"),
                    
                    # 6. 钢网梁区域
                    html.Div([
                        html.Div([
                            html.H5("6. 钢网梁", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "steel-grid-beam-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 钢网梁的子项
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-grid-manufacturing",
                                    "请输入",
                                    "number",
                                    "钢网架制作"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-grid-installation",
                                    "请输入",
                                    "number",
                                    "钢网架安装"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                    "steel-grid-removal",
                                    "请输入",
                                    "number",
                                    "钢网架拆除"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="steel-grid-section", className="mb-4"),
                    
                    # 7. 措施费区域
                    html.Div([
                        html.Div([
                            html.H5("7. 措施费", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(  # 🔄 改为统一函数
                                "steel-lining-measures-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3")
                    ], id="steel-lining-measures-section", className="mb-4"),
                    
                ]),
                dbc.ModalFooter([
                    dbc.Button("取消", id="close-steel-lining-modal", className="me-2", color="secondary"),
                    dbc.Button("确认", id="confirm-steel-lining", color="primary")
                ])
            ],
            id="steel-lining-parameter-modal2",
            size="xl",
            is_open=False,
        ),
    ])


def create_enhanced_input_field_with_better_disable(field_id, placeholder_text, input_type="number", label_text=None):
    """创建增强的输入字段，支持禁用状态显示 - 只保留灰色背景，移除图标和文字"""
    return html.Div([
        # 标签（如果提供）
        dbc.Label(label_text, style={'marginBottom': '5px'}) if label_text else None,
        
        # 输入框容器 - 使用相对定位
        html.Div([
            # 输入框
            dbc.Input(
                id=field_id,
                type=input_type,
                placeholder=placeholder_text,
                style={
                    'marginBottom': '5px',
                    'position': 'relative',
                    'zIndex': '1'
                }
            ),
            
            # 禁用状态覆盖层 - 只保留灰色背景，移除图标和文字
            html.Div(
                # 这里移除了所有内容，不再显示锁图标和"已禁用"文字
                id=f"{field_id}-overlay", 
                style={
                    'position': 'absolute',
                    'top': '0',
                    'left': '0',
                    'right': '0',
                    'bottom': '0',
                    'backgroundColor': '#f8f9fa',  # 保留灰色背景
                    'border': '1px solid #dee2e6',
                    'borderRadius': '0.375rem',
                    'display': 'none',  # 初始隐藏
                    'zIndex': '10',
                    'cursor': 'not-allowed'
                }
            ),
            
            # 警告提示（移除或简化）
            html.Div(
                id=f"{field_id}-warning", 
                style={'display': 'none'}
            )
            
        ], style={
            'position': 'relative', 
            'marginBottom': '10px'
        })
        
    ], style={'marginBottom': '10px'})


# 修改钢筋笼模式模态窗口创建函数
def create_steel_reinforcement_parameter_modal():
    """创建钢筋笼施工模式参数设置模态窗口 - 与钢衬里模式保持一致"""
    return html.Div([
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("钢筋笼施工模式参数配置"), close_button=True),
                dbc.ModalBody([
                    # 添加统一的提示信息区域
                    html.Div([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle", style={'marginRight': '10px'}),
                            html.Span("若需解除字段禁用状态，请前往数据管理模块修改对应指标的启用状态")
                        ], color="info", style={
                            'marginBottom': '25px',
                            'fontSize': '14px',
                            'padding': '12px 16px',
                            'borderRadius': '6px',
                            'backgroundColor': '#e3f2fd',
                            'borderColor': '#2196f3',
                            'color': '#1565c0'
                        })
                    ]),
                    
                    # 1. 塔吊租赁费区域
                    html.Div([
                        html.Div([
                            html.H5("1. 塔吊租赁费", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "tower-crane-category-param", 
                                "请输入", 
                                "number"
                            )
                        ], className="d-flex align-items-center mt-2 mb-3"),
                        
                        # 子项目
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "tower-crane-1500",
                                    "请输入",
                                    "number", 
                                    "自升式塔式起重机(1500KNm)"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "heavy-tower-crane",
                                    "请输入",
                                    "number",
                                    "重型塔吊"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="tower-crane-section", className="mb-4"),
                    
                    # 2. 钢筋生产线费用区域
                    html.Div([
                        html.Div([
                            html.H5("2. 钢筋生产线费用", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "steel-production-category-param",
                                "请输入",
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3")
                    ], id="steel-production-section", className="mb-4"),
                    
                    # 3. 吊索具数量区域
                    html.Div([
                        html.Div([
                            html.H5("3. 吊索具数量", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "lifting-equipment-category-param",
                                "请输入",
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 子项目
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "steel-wire-a36-1500",
                                    "请输入",
                                    "number",
                                    "压制钢丝绳"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "shackle-55t",
                                    "请输入", 
                                    "number",
                                    "卸扣"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "basket-bolt-3128",
                                    "请输入",
                                    "number",
                                    "花篮螺栓"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="lifting-equipment-section", className="mb-4"),
                    
                    # 4. 套筒数量区域
                    html.Div([
                        html.Div([
                            html.H5("4. 套筒数量", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "sleeve-category-param",
                                "请输入",
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3"),
                        
                        # 子项目
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "straight-threaded-sleeve",
                                    "请输入",
                                    "number",
                                    "直螺纹钢筋套筒(Φ16-Φ40)"
                                )
                            ], width=6),
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "cone-steel-sleeve",
                                    "请输入",
                                    "number",
                                    "锥套锁紧套筒"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                create_enhanced_input_field_with_better_disable(
                                    "module-vertical-connection",
                                    "请输入",
                                    "number", 
                                    "模块竖向钢筋锥套连接"
                                )
                            ], width=6)
                        ], className="mb-3"),
                    ], id="sleeve-section", className="mb-4"),
                    
                    # 5. 钢筋吨数区域
                    html.Div([
                        html.Div([
                            html.H5("5. 钢筋吨数", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "steel-tonnage-category-param",
                                "请输入",
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3")
                    ], id="steel-tonnage-section", className="mb-4"),

                    # 6. 措施费区域
                    html.Div([
                        html.Div([
                            html.H5("6. 措施费", className="mb-0 d-inline-block me-3"),
                            create_enhanced_input_field_with_better_disable(
                                "steel-price-category-param",
                                "请输入",
                                "number"
                            )
                        ], className="d-flex align-items-center mt-4 mb-3")
                    ], id="measures-section", className="mb-4"),

                ]),
                dbc.ModalFooter([
                    dbc.Button("取消", id="close-steel-reinforcement-modal", className="me-2", color="secondary"),
                    dbc.Button("确认", id="confirm-steel-reinforcement", color="primary")
                ])
            ],
            id="steel-reinforcement-parameter-modal",
            size="lg",
            is_open=False,
        ),
        # 添加结果显示区域
        html.Div(id='steel-reinforcement-calculation-result5', style={'margin': '0', 'padding': '0'})
    ])

##########自定义部分


# 假设这些配置列表存在（需要根据实际情况导入）
# 如果没有，需要定义这些列表
project_types = ["钢筋混凝土工程", "钢结构工程", "预制装配式工程", "管廊工程", "其他工程"]
param_types = ["塔吊租赁费", "钢筋生产线费用", "吊索具数量", "套筒数量", "钢筋吨数", "措施费"]
units = ["元", "台", "套", "个", "吨", "m³", "m²", "m", "项"]
DEFAULT_PARAM_ID = "param_0"

# 创建输入字段的辅助函数
def create_input_field(id_prefix, label):
    """创建输入字段的辅助函数"""
    return html.Div([
        html.Label(label, className="mb-1"),
        dbc.Input(
            id=f"{id_prefix}-{label.replace(' ', '-').lower()}",
            type="text",
            placeholder="请输入",
            className="mb-3"
        )
    ])

# 创建单个参数表单行
def create_parameter_form_row(index):
    """创建单个参数表单行 - ID冲突修复版本"""
    return html.Div([
        dbc.Row([
            # 参数名称
            dbc.Col([
                html.Label("参数名称", className="form-label"),
                dbc.Input(
                    id={"type": "table-param-name", "index": index},  # 修改前缀
                    type="text",
                    placeholder="输入参数名称",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 参数类别
            dbc.Col([
                html.Label("参数类别", className="form-label"),
                dcc.Dropdown(
                    id={"type": "table-param-type", "index": index},  # 修改前缀
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
                    id={"type": "table-param-value", "index": index},  # 修改前缀
                    type="number",
                    placeholder="输入数值",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 单位
            dbc.Col([
                html.Label("单位", className="form-label"),
                dcc.Dropdown(
                    id={"type": "table-param-unit", "index": index},  # 修改前缀：原来是 "param-unit"，现在是 "table-param-unit"
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
                    id={"type": "table-direct-labor-price", "index": index},  # 修改前缀
                    type="number",
                    placeholder="0.00",
                    value=0,
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 直接施工材料单价
            dbc.Col([
                html.Label("直接施工材料单价", className="form-label"),
                dbc.Input(
                    id={"type": "table-direct-material-price", "index": index},  # 修改前缀
                    type="number",
                    value=0,
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
                    id={"type": "table-direct-machine-price", "index": index},  # 修改前缀
                    type="number",
                    value=0,
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 模块化施工人工单价
            dbc.Col([
                html.Label("模块化施工人工单价", className="form-label"),
                dbc.Input(
                    id={"type": "table-modular-labor-price", "index": index},  # 修改前缀
                    type="number",
                    value=0,
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
                    id={"type": "table-modular-material-price", "index": index},  # 修改前缀
                    type="number",
                    value=0,
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
            
            # 模块化施工机械单价
            dbc.Col([
                html.Label("模块化施工机械单价", className="form-label"),
                dbc.Input(
                    id={"type": "table-modular-machine-price", "index": index},  # 修改前缀
                    type="number",
                    value=0,
                    placeholder="0.00",
                    className="form-control mb-2"
                )
            ], width=6),
        ]),
        
        # 分隔线
        html.Hr(className="my-3")
    ], id={"type": "table-param-row", "index": index}, className="mb-3 param-row")  # 修改前缀


# 创建自定义参数表单
def create_custom_parameters_form():
    """创建自定义参数表单"""
    return html.Div([
        html.H5("自定义参数", className="mt-4 mb-3"),
        
        # 参数容器 - 可以通过回调添加多个
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


# 创建参数表单组件函数
def create_parameter_form(param_id, is_first=False):
    """创建参数表单组件函数 - ID冲突修复版本"""
    return html.Div(
        [
            # 参数ID（隐藏字段）
            dcc.Store(id={'type': 'query-param-id', 'index': param_id}, data=param_id),
            
            # 添加价格数据存储组件
            dcc.Store(id={'type': 'query-direct-labor-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'query-direct-material-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'query-direct-machine-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'query-modular-labor-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'query-modular-material-price', 'index': param_id}, data=0),
            dcc.Store(id={'type': 'query-modular-machine-price', 'index': param_id}, data=0),
            
            # 删除按钮（非首个参数才显示）
            html.Div(
                html.Button(
                    '×',
                    id={'type': 'query-delete-param', 'index': param_id},
                    className='btn btn-sm btn-outline-danger position-absolute top-0 end-0',
                    style={'display': 'none' if is_first else 'block', 'borderRadius': '50%', 'width': '24px', 'height': '24px', 'padding': '0'}
                ),
                className='position-relative',
                style={'textAlign': 'right'}
            ),

            # 参数查询部分
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
                    # 参数数值
                    dbc.Col([
                        html.Label("参数数值", className="form-label"),
                        dcc.Input(
                            id={'type': 'query-param-quantity', 'index': param_id},  # 修改前缀：确保与上面不冲突
                            type="number",
                            placeholder="请输入数值",
                            className="form-control mb-3"
                        )
                    ], width=4),
                    
                    # 单位
                    dbc.Col([
                        html.Label("单位", className="form-label"),
                        dcc.Dropdown(
                            id={'type': 'query-param-unit', 'index': param_id},  # 修改前缀：原来是 "param-unit"，现在是 "query-param-unit"
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
                    ], width="auto", className="ms-auto")
                ]),
                html.Div(id="price-results-container"),
                html.Div(id="selection-output", className="mt-4")
            ], className="mt-4"),

            # 添加自定义参数表格组件
            create_custom_parameters_form(),

            # 分隔线
            html.Hr()
        ],
        id={'type': 'query-param-container', 'index': param_id},  # 修改前缀
        className='mb-3 position-relative'
    )



#自定义模式
def create_custom_mode_parameter_modal():
    """创建自定义模式参数设置模态窗口"""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("自定义模式参数配置"),
                close_button=True
            ),
            dbc.ModalBody([
                # 参数输入区域
                html.Div([
                    html.H5("参数信息输入", className="text-primary mb-3"),
                    
                    # 第一行：参数名称和参数工程量
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("参数名称", className="form-label"),
                            dbc.Input(
                                id="custom-param-name",
                                type="text",
                                placeholder="请输入参数名称",
                                className="form-control"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("参数工程量", className="form-label"),
                            dbc.Input(
                                id="custom-param-quantity",
                                type="number",
                                placeholder="请输入工程量",
                                className="form-control"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    # 第二行：工程量占比和价格量
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("工程量占比 (%)", className="form-label"),
                            dbc.Input(
                                id="custom-quantity-ratio",
                                type="number",
                                placeholder="请输入工程量占比",
                                min=0,
                                max=100,
                                step=0.01,
                                className="form-control"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("价格量 (元)", className="form-label"),
                            dbc.Input(
                                id="custom-price-amount",
                                type="number",
                                placeholder="请输入价格量",
                                className="form-control"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    # 第三行：价格占比和关键因素
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("价格占比 (%)", className="form-label"),
                            dbc.Input(
                                id="custom-price-ratio",
                                type="number",
                                placeholder="请输入价格占比",
                                min=0,
                                max=100,
                                step=0.01,
                                className="form-control"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("关键因素", className="form-label"),
                            dbc.Input(
                                id="custom-key-factor",
                                type="text",
                                placeholder="请输入关键因素",
                                className="form-control"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    # 添加参数按钮
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "添加参数"],
                            id="add-custom-param-btn",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-sync-alt me-2"), "更新表格"],
                            id="refresh-custom-table-btn",
                            color="info"
                        )
                    ], className="d-flex justify-content-center mb-4")
                ], className="border rounded p-3 mb-4", style={"backgroundColor": "#f8f9fa"}),
                
                # 参数表格显示区域
                html.Div([
                    html.H5("已添加的参数列表", className="text-primary mb-3"),
                    html.Div([
                        dash_table.DataTable(
                            id='custom-params-table',
                            columns=[
                                {"name": "序号", "id": "id", "type": "numeric", "editable": False},
                                {"name": "参数名称", "id": "param_name", "type": "text", "editable": True},
                                {"name": "参数工程量", "id": "param_quantity", "type": "numeric", "editable": True, "format": {"specifier": ".2f"}},
                                {"name": "工程量占比(%)", "id": "quantity_ratio", "type": "numeric", "editable": True, "format": {"specifier": ".2f"}},
                                {"name": "价格量(元)", "id": "price_amount", "type": "numeric", "editable": True, "format": {"specifier": ".2f"}},
                                {"name": "价格占比(%)", "id": "price_ratio", "type": "numeric", "editable": True, "format": {"specifier": ".2f"}},
                                {"name": "关键因素", "id": "key_factor", "type": "text", "editable": True},
                                {"name": "创建时间", "id": "create_time", "type": "text", "editable": False}
                            ],
                            data=[],
                            editable=True,
                            filter_action="native",
                            sort_action="native",
                            row_selectable="multi",
                            row_deletable=True,
                            page_action="native",
                            page_current=0,
                            page_size=10,
                            style_table={
                                'overflowX': 'auto',
                                'minHeight': '300px',
                                'maxHeight': '400px',
                                'overflowY': 'auto'
                            },
                            style_cell={
                                'minWidth': '120px',
                                'width': '150px',
                                'maxWidth': '200px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'textAlign': 'center',
                                'padding': '8px',
                                'fontSize': '14px'
                            },
                            style_header={
                                'backgroundColor': PRIMARY_COLOR,
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                },
                                {
                                    'if': {'state': 'selected'},
                                    'backgroundColor': 'rgb(230, 247, 255)',
                                    'border': '1px solid rgb(0, 116, 217)'
                                }
                            ],
                            tooltip_data=[],
                            tooltip_duration=None
                        )
                    ], className="border rounded"),
                    
                    # 表格操作提示
                    html.Div([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "提示：可以直接在表格中编辑数据，选中行后点击删除可移除参数，支持多选操作。"
                        ], color="info", className="mt-3 mb-0", style={"fontSize": "13px"})
                    ])
                ], className="mb-4"),
                
                # 操作结果反馈区域
                html.Div(id="custom-params-feedback", className="mb-3")
                
            ], style={"maxHeight": "80vh", "overflowY": "auto"}),
            
            # 底部操作按钮
            dbc.ModalFooter([
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-times me-2"), "取消"],
                        id="close-custom-mode-modal",
                        color="danger",
                        outline=True
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-calculator me-2"), "确认计算"],
                        id="confirm-custom-mode",
                        color="success"
                    )
                ], className="w-100 d-flex justify-content-center")
            ])
        ],
        id="custom-mode-parameter-modal",
        size="xl",  # 使用超大模态窗口
        is_open=False,
        backdrop="static",  # 点击背景不关闭
        scrollable=True,
        style={"fontFamily": "Arial, 'Microsoft YaHei', sans-serif"}
    )


# 创建修改价格的模态窗口
def create_price_modification_modal():
    """创建修改价格的模态窗口"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("修改价格基准数据")),
            dbc.ModalBody([
                dbc.Alert("在此处修改的单价将作为后续成本测算的基准。", color="info", className="mb-3"),
                
                # ==== 新增：选择模式的 RadioItems ====
                html.Div([
                    dbc.Label("选择施工模式:", className="me-2"),
                    dbc.RadioItems(
                        options=[
                            {"label": "钢筋笼模式", "value": "钢筋笼施工模式"},
                            {"label": "钢衬里模式", "value": "钢衬里施工模式"},
                            # 您可以根据需要添加更多模式
                        ],
                        value="钢筋笼施工模式",  # 默认选中钢筋笼模式
                        id="price-modification-mode-radio",
                        inline=True,
                        className="mb-3"
                    ),
                ], className="d-flex align-items-center mb-3"),
                
                dash_table.DataTable(
                    id='price-modification-table',
                    columns=[], # To be populated by callback
                    data=[],    # To be populated by callback
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    row_selectable=False,
                    page_action="native",
                    page_current=0,
                    page_size=15,
                    style_table={'overflowX': 'auto', 'minHeight': '400px'},
                    style_cell={
                        'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'textAlign': 'left',
                        'padding': '5px',
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'},
                         'backgroundColor': 'rgb(248, 248, 248)'}
                    ]
                ),
                html.Div(id="price-modification-feedback", className="mt-3")
            ]),
            dbc.ModalFooter(
                dbc.Button("关闭", id="close-price-modification-modal-button", color="secondary")
            ),
        ],
        id="price-modification-modal",
        size="xl", # Large modal
        is_open=False,
        scrollable=True,
    )