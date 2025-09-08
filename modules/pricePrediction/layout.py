import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import sqlite3
import io
# 导入配置
from config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BG_COLOR, CARD_BG
# 修复导入：添加缺少的钢筋笼模式模态窗口
from .modals import (
    create_price_modification_modal, 
    create_steel_lining_parameter_modal, 
    create_custom_mode_parameter_modal,
    create_steel_reinforcement_parameter_modal  # 添加这个导入
)

def create_price_prediction_layout():
    """创建价格预测计算模式页面布局 - 结果表格在配置界面后面"""
    return html.Div([
        # 页面标题和修改价格按钮
        dbc.Row([
            dbc.Col(
                html.H2("请选择价格预测计算模式",
                        className="my-4",
                        style={"color": PRIMARY_COLOR, "display": "inline-block"}),
                width='auto'
            ),
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-edit me-2"), "修改价格基准"],
                    id="open-price-modification-modal-button",
                    color="info",
                    className="my-4",
                    style={'float': 'right'}
                ),
                width=True
            )
        ], justify="between", align="center", className="mb-4"),

        # 模式选择卡片容器
        html.Div([
            dbc.Row([
                # 钢筋笼施工模式卡片
                dbc.Col([
                    html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3("钢筋笼施工模式",
                                        className="text-center",
                                        style={"color": ACCENT_COLOR})
                            ], style={"height": "200px", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"})
                        ], className="shadow-sm", style={"backgroundColor": "white"})
                    ], id="steel-cage-mode-div", style={"cursor": "pointer"})
                ], width=4),

                # 钢衬里施工模式卡片
                dbc.Col([
                    html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3("钢衬里施工模式",
                                        className="text-center",
                                        style={"color": ACCENT_COLOR})

                            ], style={"height": "200px", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"})
                        ], className="shadow-sm", style={"backgroundColor": "white"})
                    ], id="steel-lining-mode-div", style={"cursor": "pointer"})
                ], width=4),

                # 自定义模式卡片
                dbc.Col([
                    html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3("自定义模式",
                                        className="text-center",
                                        style={"color": ACCENT_COLOR}),
                                html.P("根据您的需求\n自定义参数配置",
                                       className="text-center text-muted",
                                       style={"fontSize": "14px", "marginTop": "10px", "whiteSpace": "pre-line"})
                            ], style={"height": "200px", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"})
                        ], className="shadow-sm", style={"backgroundColor": "white", "border": "2px dashed #ccc"})
                    ], id="custom-mode-div", style={"cursor": "pointer"})
                ], width=4),
            ], className="my-5 justify-content-center"),
        ], style={"marginTop": "50px"}),

        # 底部按钮
        html.Div([
            dbc.Button("刷新", id="refresh-price-prediction", color="secondary", className="ms-auto")
        ], className="d-flex justify-content-end mt-4"),

        # ========== 钢筋笼模式结果显示区域 ==========
        html.Div([
            html.Div(id="steel-reinforcement-calculation-result5", className="table-responsive", style={'margin': '0', 'paddingTop': '0'}),
            html.Div(id="cost-comparison-container2", style={"display": "none"}, className="mt-5"),
            html.Div(id="cost-comparison-table2", className="table-responsive"),
            # 新增：导出按钮区域
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "导出报表"],
                    id="export-steel-cage-report-btn",
                    color="success",
                    className="mt-3 me-2",
                ),
                dbc.Button(
                    [html.I(className="fas fa-database me-2"), "保存到数据库"],
                    id="save-steel-cage-data-btn",
                    color="primary",
                    className="mt-3",
                )
            ], className="text-center"),
            
            # 新增：保存反馈区域
            html.Div(id="steel-cage-save-feedback", className="mt-3"),
            
            # 新增：下载组件
            dcc.Download(id="download-steel-cage-report")
        ], id="steel-cage-results-section", style={"display": "none"}),

        # ========== 钢衬里模式结果显示区域 ==========
        html.Div([
            html.Div(id="steel-lining-calculation-result-output", className="table-responsive"),
            html.Div(id="steel-lining-cost-comparison-container", style={"display": "none"}, className="mt-5"),
            html.Div(id="steel-lining-cost-comparison-table", className="table-responsive"),
            # 新增：导出按钮区域
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "导出报表"],
                    id="export-steel-lining-report-btn",
                    color="success",
                    className="mt-3 me-2",
                ),
                dbc.Button(
                    [html.I(className="fas fa-database me-2"), "保存到数据库"],
                    id="save-steel-lining-data-btn",
                    color="primary",
                    className="mt-3",
                )
            ], className="text-center"),
            
            # 新增：保存反馈区域
            html.Div(id="steel-lining-save-feedback", className="mt-3"),
            
            # 新增：下载组件
            dcc.Download(id="download-steel-lining-report")
        ], id="steel-lining-results-section", style={"display": "none"}),
            
        # ========== 自定义模式结果显示区域 ==========
        html.Div([
            html.Div(id="custom-mode-calculation-result", className="table-responsive"),
            html.Div(id="custom-mode-cost-comparison-container", style={"display": "none"}, className="mt-5"),
            html.Div(id="custom-mode-cost-comparison-table", className="table-responsive"),
            # 新增：导出按钮区域
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "导出报表"],
                    id="export-custom-mode-report-btn",
                    color="success",
                    className="mt-3 me-2",
                ),
                dbc.Button(
                    [html.I(className="fas fa-database me-2"), "保存到数据库"],
                    id="save-custom-mode-data-btn",
                    color="primary",
                    className="mt-3",
                )
            ], className="text-center"),
            
            # 新增：保存反馈区域
            html.Div(id="custom-mode-save-feedback", className="mt-3"),
            
            # 新增：下载组件
            dcc.Download(id="download-custom-mode-report")
        ], id="custom-mode-results-section", style={"display": "none"}),

        # 修复：添加所有必需的模态窗口
        create_price_modification_modal(),
        create_steel_reinforcement_parameter_modal(),  # 添加这个调用
        create_steel_lining_parameter_modal(),
        create_custom_mode_parameter_modal(),
        


        # ========== 数据存储组件 ==========
        dcc.Store(id="steel-cage-report-data"),      # 存储钢筋笼预测报告数据
        dcc.Store(id="steel-lining-report-data"),    # 存储钢衬里预测报告数据  
        dcc.Store(id="custom-mode-report-data"),     # 存储自定义模式预测报告数据
        # ========== 状态存储组件 ==========
        dcc.Store(id="steel-cage-field-status-store"),      # 存储钢筋笼字段状态
        dcc.Store(id="steel-lining-field-status-store"),    # 存储钢衬里字段状态  
        dcc.Store(id="current-prediction-mode", data="steel_cage"),  # 添加这个缺失的Store组件
    ])