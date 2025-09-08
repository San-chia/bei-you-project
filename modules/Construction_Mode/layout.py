import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc
from utils.components import create_icon_button
from config import PRIMARY_COLOR
from .db_connection import get_mode_details_from_database
import mysql.connector
from .translation import reverse_translate_table_name, reverse_translate_field_name  # 新增
from datetime import datetime
import math  # 添加这个导入用于分页计算

# MySQL数据库连接配置
MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名
    'charset': 'utf8mb4',
    'autocommit': False
}

def load_custom_modes():
    """从MySQL数据库加载所有自定义模式 - 按project_id数量生成选项卡"""
    try:
        print("开始从parameter_info表查询现存项目...")
        
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 首先检查parameter_info表中有多少个不同的project_id
        cursor.execute("SELECT COUNT(DISTINCT project_id) as project_count FROM `parameter_info`")
        result = cursor.fetchone()
        print(result)
        project_count = result['project_count'] if result else 0
        
        print(f"parameter_info表中不同的project_id数量: {project_count}")
        
        # 如果没有项目ID，返回空列表
        if project_count == 0:
            print("parameter_info表中没有项目ID，返回空列表")
            conn.close()
            return []
        
        # 获取所有不同的project_id列表
        cursor.execute("SELECT DISTINCT project_id FROM `parameter_info` ORDER BY project_id")
        project_ids = [row['project_id'] for row in cursor.fetchall()]
        print(f"找到的project_id列表: {project_ids}")
        
        # 查询这些project_id对应的项目信息
        custom_modes = []
        
        for project_id in project_ids:
            # 查询该project_id在project_info表中的详细信息
            cursor.execute("""
            SELECT 
                `project_id`,
                `project_name`,
                `project_type`,
                `project_quantity`,
                `unit`,
                `normal_construction_days`,
                `modular_construction_days`,
                `remarks`,
                `create_time`
            FROM `project_info` 
            WHERE `project_id` = %s
            """, (project_id,))
            
            project_info = cursor.fetchone()
            
            # 统计该project_id在parameter_info表中的参数数量
            cursor.execute("""
            SELECT COUNT(*) as param_count 
            FROM `parameter_info` 
            WHERE `project_id` = %s
            """, (project_id,))
            
            param_result = cursor.fetchone()
            param_count = param_result['param_count'] if param_result else 0
            
            # 如果在project_info表中找到了项目信息，使用它；否则创建基本信息
            if project_info:
                mode_data = {
                    "id": project_info['project_id'],
                    "project_name": project_info['project_name'],
                    "project_type": project_info['project_type'] or "自定义",
                    "project_value": project_info['project_quantity'] or 0,
                    "project_unit": project_info['unit'] or "",
                    "regular_days": project_info['normal_construction_days'] or 0,
                    "modular_days": project_info['modular_construction_days'] or 0,
                    "created_at": project_info['create_time'],
                    "description": project_info['remarks'] or f"自定义项目 - {project_info['project_name']} (包含{param_count}个参数)",
                    "parameters": [],
                    "parameter_count": param_count
                }
                print(f"项目 {project_info['project_name']} (ID: {project_id}, 参数数量: {param_count})")
            else:
                # 如果project_info表中没有对应记录，创建基本信息
                mode_data = {
                    "id": project_id,
                    "project_name": f"项目{project_id}",
                    "project_type": "自定义",
                    "project_value": 0,
                    "project_unit": "",
                    "regular_days": 0,
                    "modular_days": 0,
                    "created_at": None,
                    "description": f"项目ID {project_id} (包含{param_count}个参数)",
                    "parameters": [],
                    "parameter_count": param_count
                }
                print(f"项目{project_id} (ID: {project_id}, 参数数量: {param_count}) - 无详细信息")
            
            custom_modes.append(mode_data)
        
        conn.close()
        print(f"成功处理的项目数: {len(custom_modes)}")
        return custom_modes
        
    except Exception as e:
        print(f"从parameter_info表查询项目时出错: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        if 'conn' in locals() and conn:
            conn.close()
        return []


# 添加一个调试函数来检查数据库的实际状态
def debug_project_ids():
    """调试函数：检查parameter_info表中的project_id统计"""
    try:
        from modules.Construction_Mode.db_connection import MYSQL_CONFIG
        import mysql.connector
        
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== parameter_info表project_id统计 ===")
        
        # 统计不同project_id的数量
        cursor.execute("SELECT COUNT(DISTINCT project_id) as project_count FROM `parameter_info`")
        result = cursor.fetchone()
        project_count = result['project_count']
        print(f"不同project_id的数量: {project_count}")
        
        # 列出所有不同的project_id及其参数数量
        cursor.execute("""
        SELECT project_id, COUNT(*) as param_count
        FROM `parameter_info`
        GROUP BY project_id
        ORDER BY project_id
        """)
        
        project_stats = cursor.fetchall()
        print("\n各project_id的参数统计:")
        for stat in project_stats:
            print(f"  project_id: {stat['project_id']}, 参数数量: {stat['param_count']}")
        
        conn.close()
        print("\n=== 统计完成 ===")
        
    except Exception as e:
        print(f"调试时出错: {e}")


    

def create_custom_modes_row_with_pagination(custom_modes, current_page=1):
    """创建带分页的自定义模式显示 - 简化版本"""
    print(f"开始创建分页显示，总项目数: {len(custom_modes)}, 当前页: {current_page}")
    
    # 分页设置
    items_per_page = 6  # 每页6个项目（2行，每行3个）
    total_pages = math.ceil(len(custom_modes) / items_per_page) if custom_modes else 1
    
    # 确保当前页面在有效范围内
    current_page = max(1, min(current_page, total_pages))
    
    # 状态信息
    status_info = html.Div([
        html.Small(f"第 {current_page}/{total_pages} 页，共 {len(custom_modes)} 个自定义模式", 
                   className="text-muted d-block text-center mb-2"),
        html.Small(f"最后刷新: {datetime.now().strftime('%H:%M:%S')}", 
                   className="text-muted d-block text-center mb-3")
    ])
    
    if not custom_modes:
        return html.Div([
            dcc.Store(id="current-page-store", data=1),
            dcc.Store(id="total-modes-store", data=0),
            status_info,
            html.Div([
                html.P("暂无自定义模式", className="text-center text-muted my-4"),
                html.P("点击上方'自定义模式'按钮创建新的自定义模式", className="text-center text-muted small")
            ], style={"minHeight": "300px", "display": "flex", "flexDirection": "column", "justifyContent": "center"}),
            # 即使没有内容也显示分页控件
            create_pagination_controls(1, 1, 0, show_always=True)
        ])
    
    # 创建当前页的卡片
    # 计算当前页显示的项目范围
    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_page_modes = custom_modes[start_index:end_index]
    
    print(f"当前页显示项目: {[mode['project_name'] for mode in current_page_modes]}")
    
    mode_cards = []
    for mode_data in current_page_modes:
        try:
            card = create_custom_mode_card(mode_data)
            mode_cards.append(card)
        except Exception as e:
            print(f"创建卡片失败 {mode_data.get('project_name', 'Unknown')}: {e}")
            continue
    
    # 按每行3个卡片分组，最多2行，用空卡片填充以保持布局一致
    rows = []
    all_slots = []  # 用于存储6个位置的卡片（包括空位）
    
    # 填充当前页的卡片
    for i in range(items_per_page):  # 6个位置
        if i < len(mode_cards):
            all_slots.append(mode_cards[i])
        else:
            # 空位用透明占位符填充
            all_slots.append(
                dbc.Col([
                    html.Div(style={"height": "120px", "visibility": "hidden"})
                ], width=4, className="mb-3")
            )
    
    # 创建2行，每行3个
    for i in range(0, items_per_page, 3):
        group = all_slots[i:i+3]
        row = dbc.Row(group, className="mb-4", justify="start")
        rows.append(row)
    
    # 创建分页控件
    pagination_controls = create_pagination_controls(current_page, total_pages, len(custom_modes), show_always=True)
    
    # 使用固定高度的容器来确保分页控件位置稳定
    return html.Div([
        dcc.Store(id="current-page-store", data=current_page),
        dcc.Store(id="total-modes-store", data=len(custom_modes)),
        status_info,
        
        # 内容区域 - 固定高度
        html.Div([
            html.Div(rows)
        ], style={
            "minHeight": "360px",  # 固定最小高度，确保2行卡片的空间
            "maxHeight": "360px",  # 固定最大高度
            "overflow": "hidden",  # 隐藏溢出内容
            "marginBottom": "20px"
        }),
        
        # 分页控件区域 - 固定在底部
        html.Div([
            pagination_controls
        ], style={
            "position": "relative",
            "zIndex": "1000",  # 确保在其他内容之上
            "backgroundColor": "white",  # 白色背景
            "paddingTop": "10px",
            "borderTop": "1px solid #e0e0e0"  # 顶部边界线
        })
    ], style={
        "position": "relative",
        "minHeight": "450px"  # 确保整个容器有足够高度
    })
    

def create_pagination_controls(current_page, total_pages, total_items, show_always=False):
    """创建分页控件 - 修复版本，支持强制显示"""
    
    # 修改：即使只有一页也显示分页控件（如果show_always=True）
    if not show_always and total_pages <= 1:
        return html.Div()
    
    # 如果强制显示但没有数据，显示禁用的控件
    if show_always and total_pages <= 1:
        return html.Div([
            html.Hr(),
            html.Div([
                dbc.Button(
                    "首页",
                    color="outline-secondary",
                    size="sm",
                    disabled=True,
                    className="me-2"
                ),
                dbc.Button(
                    "上一页",
                    color="outline-primary",
                    size="sm",
                    disabled=True,
                    className="me-2"
                ),
                html.Span(
                    f"1 / 1",
                    className="mx-3 text-muted"
                ),
                dbc.Button(
                    "下一页",
                    color="outline-primary",
                    size="sm",
                    disabled=True,
                    className="ms-2"
                ),
                dbc.Button(
                    "末页",
                    color="outline-secondary",
                    size="sm",
                    disabled=True,
                    className="ms-2"
                )
            ], className="d-flex justify-content-center align-items-center my-3"),
            #html.Div([
             #   html.Small(f"共 {total_items} 个项目", className="text-muted text-center d-block")
            #])
        ], style={
            "backgroundColor": "#f8f9fa",
            "padding": "10px",
            "borderRadius": "5px",
            "marginTop": "10px"
        })
    
    # 上一页按钮
    prev_button = dbc.Button(
        "上一页",
        id="prev-page-btn",
        color="outline-primary",
        size="sm",
        disabled=(current_page <= 1),
        className="me-2"
    )
    
    # 下一页按钮
    next_button = dbc.Button(
        "下一页",
        id="next-page-btn",
        color="outline-primary",
        size="sm",
        disabled=(current_page >= total_pages),
        className="ms-2"
    )
    
    # 页码显示
    page_info = html.Span(
        f"{current_page} / {total_pages}",
        className="mx-3 text-muted"
    )
    
    # 第一页按钮
    first_button = dbc.Button(
        "首页",
        id="first-page-btn",
        color="outline-secondary",
        size="sm",
        disabled=(current_page <= 1),
        className="me-2"
    )
    
    # 最后一页按钮
    last_button = dbc.Button(
        "末页",
        id="last-page-btn",
        color="outline-secondary",
        size="sm",
        disabled=(current_page >= total_pages),
        className="ms-2"
    )
    
    # 页面跳转输入框
    page_jump = html.Div([
        html.Span("跳转到第", className="me-2 text-muted small"),
        dbc.Input(
            id="page-jump-input",
            type="number",
            value=current_page,
            min=1,
            max=total_pages,
            size="sm",
            style={"width": "60px", "display": "inline-block"},
            className="me-2"
        ),
        html.Span("页", className="me-2 text-muted small"),
        dbc.Button(
            "跳转",
            id="page-jump-btn",
            color="outline-info",
            size="sm"
        )
    ], className="d-flex align-items-center ms-4")
    
    return html.Div([
        html.Hr(style={"margin": "15px 0 10px 0"}),
        
        # 主要分页控件
        html.Div([
            first_button,
            prev_button,
            page_info,
            next_button,
            last_button,
            page_jump  # 添加页面跳转功能
        ], className="d-flex justify-content-center align-items-center my-3"),
        
        # 统计信息
        html.Div([
            html.Small(
                f"共 {total_items} 个项目，每页显示 6 个", 
                className="text-muted text-center d-block"
            )
        ])
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "15px",
        "borderRadius": "8px",
        "marginTop": "15px",
        "border": "1px solid #dee2e6"
    })
    
def create_custom_mode_card(custom_mode_data):
    """创建自定义模式卡片 - 增加删除功能"""
    mode_id = custom_mode_data.get("id", "")
    project_name = custom_mode_data.get("project_name", "未命名项目")
    description = custom_mode_data.get("description", "")
    project_type = custom_mode_data.get("project_type", "自定义")
    
    # 构建详细描述
    project_value = custom_mode_data.get("project_value", 0)
    project_unit = custom_mode_data.get("project_unit", "")
    regular_days = custom_mode_data.get("regular_days", 0)
    modular_days = custom_mode_data.get("modular_days", 0)
    
    detail_parts = []
    if project_value and project_unit:
        detail_parts.append(f"工程量: {project_value} {project_unit}")
    if regular_days or modular_days:
        detail_parts.append(f"工期: {regular_days}天 / {modular_days}天")
    
    if detail_parts:
        full_description = description + " | " + " | ".join(detail_parts)
    else:
        full_description = description
    
    # 样式定义
    card_style = {
        'background': 'white',
        'border': '1px solid rgba(0, 105, 204, 0.2)',
        'border-radius': '8px',
        'padding': '20px',
        'margin': '10px',
        'text-align': 'left',
        'position': 'relative',  # 为删除按钮定位
        'transition': 'all 0.3s ease',
        'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)',
        'min-height': '120px'
    }
    
    title_style = {
        'color': '#0069CC', 
        'font-size': '16px', 
        'margin-bottom': '10px', 
        'font-weight': '600'
    }
    
    description_style = {
        'color': '#666666',
        'font-size': '14px',
        'margin-top': '10px',
        'line-height': '1.5',
        'max-height': '60px',
        'overflow': 'hidden'
    }
    
    type_badge_style = {
        'font-size': '12px',
        'background-color': '#e8f4f8',
        'color': '#0069CC',
        'padding': '2px 8px',
        'border-radius': '12px',
        'margin-bottom': '8px'
    }
    
    # 删除按钮样式
    delete_btn_style = {
        'position': 'absolute',
        'top': '5px',
        'right': '5px',
        'background': '#dc3545',
        'color': 'white',
        'border': 'none',
        'border-radius': '50%',
        'width': '24px',
        'height': '24px',
        'font-size': '12px',
        'cursor': 'pointer',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
        'z-index': '10'
    }
    
    unique_id = f"custom-mode-{mode_id}"
    
    return dbc.Col([
        html.Div([
            # 删除按钮
            html.Button(
                "×",
                id={'type': 'delete-custom-mode-btn', 'index': mode_id},
                className="btn btn-sm",
                style=delete_btn_style,
                title=f"删除项目: {project_name}"
            ),
            # 主要卡片内容
            dbc.Button(
                [
                    html.Span(project_type, style=type_badge_style),
                    html.H4(project_name, style=title_style),
                    html.P(full_description, style=description_style)
                ],
                id={'type': 'custom-mode-btn', 'index': unique_id},
                n_clicks=0,
                color="link",
                className="w-100 text-left p-0 border-0",
                style={'cursor': 'pointer'}
            )
        ], style=card_style)
    ], width=4, className="mb-3")



def create_custom_modes_row(custom_modes):
    """
    创建包含所有自定义模式卡片的行 - 改进版本
    
    Args:
        custom_modes (list): 自定义模式数据列表
        
    Returns:
        html.Div: 包含自定义模式卡片的容器组件
    """
    print(f"创建自定义模式行，模式数量: {len(custom_modes)}")
    
    # 如果没有自定义模式，显示提示信息
    if not custom_modes:
        return html.Div([
            html.P("暂无自定义模式", className="text-center text-muted my-4"),
            html.P("点击上方'自定义模式'按钮创建新的自定义模式", className="text-center text-muted small")
        ])
    
    # 创建卡片列表
    mode_cards = []
    for i, mode_data in enumerate(custom_modes):
        try:
            print(f"创建第{i+1}个卡片: {mode_data['project_name']}")
            card = create_custom_mode_card(mode_data)
            mode_cards.append(card)
        except Exception as e:
            print(f"创建卡片失败 {mode_data.get('project_name', 'Unknown')}: {e}")
            continue
    
    print(f"成功创建的卡片数量: {len(mode_cards)}")
    
    # 创建行组件并按每行3个卡片进行分组
    rows = []
    cards_per_row = 3
    
    for i in range(0, len(mode_cards), cards_per_row):
        group = mode_cards[i:i+cards_per_row]
        # 确保每行都有完整的Bootstrap行结构
        row = dbc.Row(group, className="mb-4", justify="start")
        rows.append(row)
    
    # 添加调试信息
    debug_info = html.Div([
        html.Small(f"当前显示 {len(mode_cards)} 个自定义模式", 
                   className="text-muted d-block text-center mb-2"),
        html.Small(f"最后刷新: {datetime.now().strftime('%H:%M:%S')}", 
                   className="text-muted d-block text-center")
    ])
    
    return html.Div([
        debug_info,
        html.Div(rows)
    ])

def update_construction_mode_layout():
    """更新施工模式选择界面的布局，包括修复的分页功能"""
    # 加载自定义模式
    custom_modes = load_custom_modes()
    
    # 创建带分页的自定义模式部分 - 使用修复版本
    custom_modes_section = html.Div([
        html.Div(
            create_custom_modes_row_with_pagination(custom_modes, current_page=1),
            id="custom-modes-container",
            style={
                "position": "relative",
                "zIndex": "1"  # 确保容器层级正确
            }
        )
    ])
    
    # 其余部分保持不变...
    title_style = {
        'color': '#0069CC',
        'font-weight': '500',
        'text-align': 'center',
        'margin-bottom': '20px',
        'font-size': '20px'
    }
    
    return dbc.Container([
        # 自定义参数和导入自定义模式按钮
        dbc.Row([
            dbc.Col([], width=2),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('自定义模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('创建新的自定义模式配置',
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='diy-open-modal-button',
                            n_clicks=None,
                            color="link",
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=6),
                ], className='mb-4'),
            ], width=8),
            dbc.Col([], width=2)
        ]),
        
        # 主标题
        html.H2('请选择模块化施工模式', style=title_style),
        
        # 预设模式行（保持原有的预设模式...）
        dbc.Row([
            dbc.Col([], width=2),
            dbc.Col([
                # 预设模式第一行
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('钢筋笼施工模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('适用于各类结构墙体，主要包括钢筋材料、连接材料及工装系统等', 
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='btn-mode-1',
                            color="link",
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('钢筋笼+钢覆面施工模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('在钢筋笼基础上增加钢覆面，提高防护性能和结构强度', 
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='btn-mode-2',
                            color="link",
                            n_clicks=None,
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('设备室顶板复合板模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('适用于设备室顶板建设，包括预制构件及二次筑材料', 
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='btn-mode-103',
                            color="link",
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=4),
                ], className='mb-4'),
                
                # 预设模式第二行
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('管廊叠合板模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('适用于C403、C409和C404管廊结构，分段预制安装', 
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='btn-mode-4',
                            color="link",
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Button(
                            [
                                html.H4('钢衬里施工模式', 
                                        style={'color': '#0069CC', 'font-size': '16px', 'margin-bottom': '10px', 'font-weight': '600'}),
                                html.P('钢衬里', 
                                       style={'color': '#666666', 'font-size': '15px', 'margin-top': '10px', 'line-height': '1.6'})
                            ],
                            id='btn-mode-5',
                            color="link",
                            className="w-100 text-left p-0 border-0",
                            style={'background': 'white', 'border': '1px solid rgba(0, 105, 204, 0.2)', 'border-radius': '4px',
                                  'padding': '20px', 'margin': '10px', 'text-align': 'left', 'cursor': 'pointer',
                                  'transition': 'all 0.3s ease', 'box-shadow': '0 2px 6px rgba(0, 0, 0, 0.08)'}
                        )
                    ], width=4),
                ], className='mb-4'),
                
                # 自定义模式部分 - 添加更好的间距和分隔
                html.Hr(style={"margin": "40px 0 30px 0", "borderTop": "2px solid #0069CC"}),
                
                dbc.Row([
                    html.H4("自定义模式", className="mt-3 mb-4", 
                            style={'color': '#0069CC', 'text-align': 'center', 'fontWeight': '600'}),
                    html.Div([
                        dbc.Button(
                            "刷新", 
                            id="refresh-custom-modes",
                            color="primary",
                            outline=True,
                            size="sm",
                            className="mb-3"
                        )
                    ], className="d-flex justify-content-end"),
                    custom_modes_section
                ])
                
            ], width=8),
            dbc.Col([], width=2)
        ]),

    ], fluid=True, style={'backgroundColor': 'white', 'minHeight': '100vh', 'paddingTop': '50px'})