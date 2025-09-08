# dash_app.py
import dash
from dash import dcc, html, dash_table, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from flask_login import current_user

# 导入配置
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG, THEME, FONT_AWESOME_URL
from modules.dataManangement import create_model_comparison_modal
# 导入现有模块
from modules.historyData import history_data_layout, register_history_data_callbacks
from modules.pricePrediction import create_price_prediction_layout, create_steel_lining_parameter_modal, register_price_prediction_callbacks, create_steel_reinforcement_parameter_modal,create_custom_mode_parameter_modal,create_price_modification_modal
from modules.indicator import create_indicator_layout, register_indicator_callbacks
from modules.dataManangement import (
    create_data_layout, 
    register_data_callbacks,
    create_import_modal,
    create_basic_indicator_modal,
    create_composite_indicator_modal,
    create_comprehensive_indicator_modal,
    create_algorithm_config_modal,
    create_model_training_modal,
    create_model_evaluation_modal,
    import_choice_modal,
)
from modules.analysis import (
    create_analysis_layout, 
    register_analysis_callbacks,
)
from modules.Construction_Mode import(
    create_steel_cage_parameter_modal,
    create_model_modal_callback,
    create_steel_cage_plus_modal,
    create_modular_composite_plate_modal,
    create_tunnel_model_modal,
    create_diy_data_modal,
    init_db,
    update_construction_mode_layout,
    create_custom_mode_detail_modal,
    register_custom_mode_callbacks,
    create_notification_modal,
    create_steel_lining_parameter_modal2,
    create_delete_confirmation_modal,
)

# 导入新增模块
from modules.integration.integration_layout import create_integration_layout
from modules.integration.integration_callbacks import register_integration_callbacks
from modules.management.management_layout import create_management_layout
from modules.management.management_callback import management_callbacks

from modules.report_management.layout import create_report_management_layout
from modules.report_management.callbacks import register_report_management_callbacks

# 导入权限控制模块
try:
    from utils.permission_utils import check_module_permission, get_user_accessible_tabs, get_user_permissions, MODULE_NAMES
except ImportError:
    print("权限控制模块未找到，将使用默认权限")
    def check_module_permission(tab_id):
        return True
    def get_user_accessible_tabs():
        # 按新的顺序返回标签页：指标测算 价格预测 模块化施工 施工数据 指标与算法管理 系统管理 报表管理 对接一体化平台
        return [
            {'tab_id': 'tab-1', 'tab_name': '指标测算'},
            {'tab_id': 'tab-7', 'tab_name': '价格预测'},
            {'tab_id': 'tab-5', 'tab_name': '模块化施工'},
            {'tab_id': 'tab-6', 'tab_name': '施工数据'},
            {'tab_id': 'tab-2', 'tab_name': '指标与算法管理'},
            {'tab_id': 'tab-3', 'tab_name': '系统管理'},
            {'tab_id': 'tab-4', 'tab_name': '报表管理'},
            {'tab_id': 'tab-8', 'tab_name': '对接一体化平台'},
        ]
    def get_user_permissions():
        return []
    MODULE_NAMES = {
        'tab-1': '指标测算',
        'tab-2': '指标与算法管理',
        'tab-3': '系统管理',
        'tab-4': '报表管理',
        'tab-5': '模块化施工',
        'tab-6': '施工数据',
        'tab-7': '价格预测',
        'tab-8': '对接一体化平台',
    }

# 初始化数据库
init_db()

def create_dash_app(server):
    """创建Dash应用"""
    app = dash.Dash(
        __name__, 
        server=server,
        url_base_pathname='/dashboard/',
        external_stylesheets=[
            getattr(dbc.themes, THEME),
            FONT_AWESOME_URL,
            {
                'href': 'data:text/css;charset=utf-8,' + '''
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    html, body { margin: 0 !important; padding: 0 !important; height: 100%; }
                    #react-entry-point { margin: 0 !important; padding: 0 !important; }
                    ._dash-loading { margin: 0 !important; padding: 0 !important; }
                    .root-container { margin: 0 !important; padding: 0 !important; }
                    .navbar { margin: 0 !important; padding: 8px 0 !important; position: sticky; top: 0; z-index: 1000; }
                    .navbar-brand { margin: 0 !important; }
                    .container-fluid { padding: 12px 15px !important; margin: 0 !important; }
                    .tab-content { padding-top: 0 !important; margin-top: 0 !important; }
                    .nav-tabs { margin-bottom: 0 !important; border-bottom: 1px solid #dee2e6; }
                    .main-container { padding: 0 !important; margin: 0 !important; }
                    .navbar .container-fluid { padding: 8px 15px !important; }
                    .dash-table-container { margin-top: 0 !important; }
                    .row { margin: 0 !important; }
                    .col, .col-12, .col-md-6, .col-lg-4, .col-xl-3 { padding: 0 15px !important; }
                    
                    /* 特定元素的空白移除 */
                    #steel-reinforcement-calculation-result5 { margin: 0 !important; padding: 0 !important; }
                    .p5 { margin: 0 !important; padding: 0 !important; }
                    
                    /* Bootstrap margin 和 padding 类的重写 */
                    .mb-3, .mb-4, .mb-5 { margin-bottom: 0 !important; }
                    .mt-3, .mt-4, .mt-5 { margin-top: 0 !important; }
                    .pt-3, .pt-4, .pt-5 { padding-top: 0 !important; }
                    .pb-3, .pb-4, .pb-5 { padding-bottom: 0 !important; }
                    .p-5 { padding: 0 !important; }
                    .p-4 { padding: 0 !important; }
                    .p-3 { padding: 5px !important; }  /* 保留小的padding以维持可读性 */
                    .p-2 { padding: 3px !important; }  /* 保留小的padding以维持可读性 */
                    
                    /* 表格和响应式组件 */
                    .table-responsive { margin: 0 !important; padding-top: 0 !important; }
                    .table { margin-bottom: 0 !important; }
                    
                    /* 卡片组件 */
                    .card { margin-bottom: 0 !important; }
                    .card-body { padding-top: 10px !important; }
                    
                    /* 特定于价格预测模块的样式调整 */
                    [id*="calculation-result"] { margin: 0 !important; padding: 0 !important; }
                    [id*="cost-comparison"] { margin-top: 10px !important; }
                    
                    /* 保留必要的间距 */
                    .btn { margin: 2px !important; }
                    .form-control, .form-select { margin-bottom: 5px !important; }
                ''',
                'type': 'text/css'
            }
        ],
        suppress_callback_exceptions=True
    )

    # 创建导航栏 - 支持动态用户名显示
    def create_navbar():
        return dbc.Navbar(
            dbc.Container(
                [
                    # 左侧标题
                    html.Div([
                        html.H1('模块化施工技术快速估价', 
                                style={'fontSize': '24px', 'fontWeight': 'bold', 'margin': '0', 'color': 'white'}),
                        html.Div('基于人工智能算法的模块化施工技术快速估价模型软件平台', 
                                 style={'fontSize': '14px', 'color': 'rgba(255,255,255,0.8)'})
                    ]),
                    
                    # 右侧按钮 - 添加动态用户名显示
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user", 
                                  style={'marginRight': '8px', 'color': 'white'}),
                            html.Span(id="current-username", 
                                     children="用户", 
                                     style={'color': 'white', 'fontSize': '16px'})
                        ], style={'marginRight': '15px', 'display': 'flex', 'alignItems': 'center'}),
                        dbc.Button("导入数据", id="import-button", color="light", className="me-2"),
                        dbc.Button("导出报告", color="success", className="me-2"),
                        html.A(
                            dbc.Button("退出登录", color="outline-light", size="sm"),
                            href="/logout",
                            style={'textDecoration': 'none'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ],
                fluid=True,
                style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}
            ),
            color=PRIMARY_COLOR,
            dark=True,
            className="mb-4"
        )

    # 创建动态选项卡（基于用户权限）
    def create_dynamic_tabs():
        """根据用户权限创建动态选项卡"""
        try:
            accessible_tabs = get_user_accessible_tabs()
            
            if not accessible_tabs:
                # 如果用户没有任何权限，显示默认消息
                return dbc.Alert("您没有访问任何模块的权限，请联系管理员。", color="warning")
            
            tabs = []
            for i, tab_info in enumerate(accessible_tabs):
                tab_id = tab_info['tab_id']
                tab_name = tab_info['tab_name']
                
                # 第一个可访问的标签页设为默认活动标签
                is_first = i == 0
                
                tabs.append(dbc.Tab(
                    label=tab_name, 
                    tab_id=tab_id, 
                    label_style={"fontWeight": "bold"} if is_first else {}
                ))
            
            return dbc.Tabs(
                tabs, 
                id="tabs", 
                active_tab=accessible_tabs[0]['tab_id'] if accessible_tabs else "tab-1",
                className="mb-4"
            )
        except Exception as e:
            print(f"创建动态标签页失败: {e}")
            # 如果权限系统失败，返回所有标签页（向后兼容）
            return create_fallback_tabs()

    # 创建后备选项卡（权限系统不可用时使用）
    def create_fallback_tabs():
        """创建后备选项卡 - 按新顺序排列"""
        return dbc.Tabs([
            dbc.Tab(label='指标测算', tab_id='tab-1', label_style={"fontWeight": "bold"}),
            dbc.Tab(label='价格预测', tab_id='tab-7'),
            dbc.Tab(label='模块化施工', tab_id='tab-5'),
            dbc.Tab(label='施工数据', tab_id='tab-6'),
            dbc.Tab(label='指标与算法管理', tab_id='tab-2'),
            dbc.Tab(label='系统管理', tab_id='tab-3'),
            dbc.Tab(label='报表管理', tab_id='tab-4'),
            dbc.Tab(label='对接一体化平台', tab_id='tab-8'),
        ], id="tabs", active_tab="tab-1", className="mb-4")

    # 创建主布局
    app.layout = html.Div([
        # 模态窗口
        create_import_modal(),
        import_choice_modal(),
        create_basic_indicator_modal(),
        create_composite_indicator_modal(),
        create_comprehensive_indicator_modal(),
        create_algorithm_config_modal(),
        create_model_training_modal(),
        create_model_evaluation_modal(),
        create_model_comparison_modal(), 
        create_steel_cage_parameter_modal(),
        create_steel_cage_plus_modal(),
        create_modular_composite_plate_modal(),
        create_tunnel_model_modal(),
        create_diy_data_modal(),
        create_custom_mode_detail_modal(),
        create_delete_confirmation_modal(),

        # create_steel_lining_parameter_modal(),
        create_steel_reinforcement_parameter_modal(),
        create_custom_mode_parameter_modal(),
        create_price_modification_modal(),
        create_steel_lining_parameter_modal2(),

        create_notification_modal(),
        
        # 添加定时刷新组件
        dcc.Interval(
            id='interval-component',
            interval=5*60*1000,  # 每5分钟刷新一次
            n_intervals=0
        ),
        
        # 数据存储组件
        dcc.Store(id='page-refresh-trigger', data=None),
        dcc.Store(id='custom-mode-id-store', data=None),
        dcc.Store(id='user-permissions-store', data=None),
        dcc.Store(id='accessible-tabs-store', data=None),

        # 顶部导航栏
        create_navbar(),
        
        # 主体内容
        dbc.Container([
            # 动态选项卡容器
            html.Div(id="dynamic-tabs-container"),
            
            # 内容区域容器
            html.Div(id="tab-content-container"),
            
            # 原有的固定内容区域（用于向后兼容）
            html.Div(id="tab-1-content", children=[], style={"display": "none"}),
            html.Div(id="tab-2-content", children=[], style={"display": "none"}),
            html.Div(id="tab-3-content", children=[], style={"display": "none"}),
            html.Div(id="tab-4-content", children=[], style={"display": "none"}),
            html.Div(id="tab-5-content", children=[], style={"display": "none"}),
            html.Div(id="tab-6-content", children=[], style={"display": "none"}),
            html.Div(id="tab-7-content", children=[], style={"display": "none"}),
            html.Div(id="tab-8-content", children=[], style={"display": "none"}),
     
        ], fluid=True)
    ], style={"backgroundColor": BG_COLOR, "minHeight": "100vh"})

    # 更新用户名显示的回调
    @app.callback(
        Output('current-username', 'children'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_username(n_intervals):
        """更新导航栏中显示的用户名"""
        try:
            if current_user and current_user.is_authenticated:
                # 优先显示真实姓名，如果没有则显示用户名
                if hasattr(current_user, 'real_name') and current_user.real_name:
                    return current_user.real_name
                else:
                    return current_user.username
            else:
                return "未登录用户"
        except Exception as e:
            # 如果获取用户信息失败，显示默认文本
            print(f"获取用户信息失败: {e}")
            return "用户"

    # 初始化用户权限和可访问标签页的回调
    @app.callback(
        [Output('user-permissions-store', 'data'),
         Output('accessible-tabs-store', 'data'),
         Output('dynamic-tabs-container', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_user_permissions_and_tabs(n_intervals):
        """更新用户权限信息和动态标签页"""
        try:
            # 获取用户权限
            permissions = get_user_permissions()
            
            # 获取可访问的标签页
            accessible_tabs = get_user_accessible_tabs()
            
            # 创建动态标签页
            tabs_component = create_dynamic_tabs()
            
            return permissions, accessible_tabs, tabs_component
            
        except Exception as e:
            print(f"更新用户权限失败: {e}")
            # 返回默认值
            return [], [], create_fallback_tabs()

    # 动态内容渲染回调
    @app.callback(
        Output('tab-content-container', 'children'),
        [Input('tabs', 'active_tab')],
        [State('accessible-tabs-store', 'data')]
    )
    def render_tab_content(active_tab, accessible_tabs):
        """根据选中的标签页渲染对应内容"""
        if not active_tab:
            return dbc.Alert("请选择一个标签页", color="info")
        
        # 权限检查
        if not check_module_permission(active_tab):
            return dbc.Alert(
                [
                    html.H4("访问被拒绝", className="alert-heading"),
                    html.P("您没有访问此模块的权限。"),
                    html.P("如需访问，请联系系统管理员申请相应权限。"),
                ],
                color="danger"
            )
        
        # 如果有可访问标签页列表，再次验证
        if accessible_tabs:
            accessible_tab_ids = [tab['tab_id'] for tab in accessible_tabs]
            if active_tab not in accessible_tab_ids:
                return dbc.Alert("您没有访问此模块的权限", color="danger")
        
        # 根据标签ID渲染对应内容
        try:
            content_mapping = {
                'tab-1': create_indicator_layout(),
                'tab-2': create_data_layout(),
                'tab-3': create_management_layout(),
                'tab-4': create_report_management_layout(),
                'tab-5': update_construction_mode_layout(),
                'tab-6': history_data_layout(),
                'tab-7': create_price_prediction_layout(),
                'tab-8': create_integration_layout(),
            }
            
            content = content_mapping.get(active_tab)
            if content is None:
                return dbc.Alert("模块内容加载失败", color="warning")
            
            return content
            
        except Exception as e:
            print(f"渲染标签页内容失败: {e}")
            return dbc.Alert(f"模块内容加载失败: {str(e)}", color="danger")

        # 添加标签页切换时重置模态窗口的回调
    @app.callback(
        [
            # 模块化施工相关模态窗口
            Output("steel-cage-parameter-modal", "is_open", allow_duplicate=True),
            Output("steel-cage-plus-modal", "is_open", allow_duplicate=True),
            Output("modular_composite_plate_modal", "is_open", allow_duplicate=True),
            Output("tunnel-modal", "is_open", allow_duplicate=True),
            Output("steel-lining-parameter-modal", "is_open", allow_duplicate=True),
            Output("diy-custom-param-modal", "is_open", allow_duplicate=True),
            Output("custom-mode-detail-modal", "is_open", allow_duplicate=True),
        ],
        [Input("tabs", "active_tab")],
        prevent_initial_call=True
    )
    def reset_modals_on_tab_switch(active_tab):
        """当切换标签页时，关闭所有模态窗口"""
        # 返回False来关闭所有模态窗口
        return [False] * 7
    
    # 向后兼容的选项卡切换回调（用于不支持权限控制的情况）
    @app.callback(
        [Output("tab-1-content", "style"),
         Output("tab-2-content", "style"),
         Output("tab-3-content", "style"),
         Output("tab-4-content", "style"),
         Output("tab-5-content", "style"),
         Output("tab-6-content", "style"),
         Output("tab-7-content", "style"),
         Output("tab-8-content", "style")],
        [Input("tabs", "active_tab")],
        prevent_initial_call=True
    )
    def render_tab_content_fallback(active_tab):
        """向后兼容的选项卡切换（当权限系统不可用时使用）"""
        # 如果使用新的权限系统，这个回调就不会被触发
        # 这里保留是为了向后兼容
        tab_contents = {f"tab-{i}": {"display": "none"} for i in range(1, 9)}
        
        # 检查权限
        if active_tab and check_module_permission(active_tab):
            tab_contents[active_tab] = {"display": "block"}
        
        return [tab_contents[f"tab-{i}"] for i in range(1, 9)]

    # 权限验证中间件回调
    @app.callback(
        Output('tab-content-container', 'children', allow_duplicate=True),
        [Input('tabs', 'active_tab')],
        prevent_initial_call=True
    )
    def validate_tab_access(active_tab):
        """验证标签页访问权限（额外的安全检查）"""
        if active_tab and not check_module_permission(active_tab):
            return dbc.Alert(
                [
                    html.H4("访问被拒绝", className="alert-heading"),
                    html.P("您没有访问此模块的权限。"),
                    html.P("如需访问，请联系系统管理员申请相应权限。"),
                    html.Hr(),
                    html.P([
                        "当前尝试访问的模块：",
                        html.Strong(MODULE_NAMES.get(active_tab, active_tab))
                    ])
                ],
                color="danger"
            )
        return dash.no_update

    # 用户权限信息显示回调（可选，用于调试）
    @app.callback(
        Output('user-permissions-store', 'data', allow_duplicate=True),
        [Input('current-username', 'children')],
        prevent_initial_call=True
    )
    def debug_user_permissions(username):
        """调试用户权限信息"""
        try:
            permissions = get_user_permissions()
            if permissions:
                print(f"用户 {username} 的权限: {permissions}")
            return permissions
        except Exception as e:
            print(f"调试权限信息失败: {e}")
            return []

    # 注册各模块回调
    try:
        register_indicator_callbacks(app)
        # register_composite_callbacks(app)
        register_data_callbacks(app)
        create_model_modal_callback(app)
        register_custom_mode_callbacks(app)
        register_history_data_callbacks(app)
        register_price_prediction_callbacks(app)
        register_integration_callbacks(app)
        management_callbacks(app=app)
        register_report_management_callbacks(app)
        print("所有模块回调注册成功")
    except Exception as e:
        print(f"注册模块回调时发生错误: {e}")
    
    return app

    