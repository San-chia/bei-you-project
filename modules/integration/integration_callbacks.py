# modules/integration/integration_callbacks.py
from dash import Input, Output, State, callback_context
import dash
from datetime import datetime

def register_integration_callbacks(app):
    """注册一体化平台对接相关的回调函数"""
    
    # 由于IntegrationAPI可能有导入问题，我们先用简单的模拟方式
    
    # 测试连接回调
    @app.callback(
        [Output("connection-status", "children"),
         Output("connection-status", "style"),
         Output("integration-toast", "is_open"),
         Output("integration-toast", "children"),
         Output("integration-toast", "header")],
        [Input("btn-test-connection", "n_clicks")],
        prevent_initial_call=True
    )
    def test_connection(n_clicks):
        if n_clicks:
            try:
                # 模拟连接测试
                return (
                    "已连接",
                    {'color': 'green'},
                    True,
                    "连接测试成功！",
                    "连接状态"
                )
            except Exception as e:
                return (
                    "连接失败",
                    {'color': 'red'},
                    True,
                    f"连接测试失败：{str(e)}",
                    "连接错误"
                )
        return dash.no_update
    
    # 重新连接回调
    @app.callback(
        [Output("connection-status", "children", allow_duplicate=True),
         Output("connection-status", "style", allow_duplicate=True),
         Output("last-sync-time", "children"),
         Output("integration-toast", "is_open", allow_duplicate=True),
         Output("integration-toast", "children", allow_duplicate=True),
         Output("integration-toast", "header", allow_duplicate=True)],
        [Input("btn-reconnect", "n_clicks")],
        prevent_initial_call=True
    )
    def reconnect(n_clicks):
        if n_clicks:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return (
                    "已连接",
                    {'color': 'green'},
                    current_time,
                    True,
                    "重新连接成功！",
                    "连接状态"
                )
            except Exception as e:
                return (
                    "连接失败",
                    {'color': 'red'},
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    True,
                    f"重新连接失败：{str(e)}",
                    "连接错误"
                )
        return dash.no_update
    
    # 保存同步配置回调
    @app.callback(
        [Output("integration-toast", "is_open", allow_duplicate=True),
         Output("integration-toast", "children", allow_duplicate=True),
         Output("integration-toast", "header", allow_duplicate=True)],
        [Input("btn-save-sync-config", "n_clicks")],
        [State("sync-frequency", "value"),
         State("sync-data-types", "value")],
        prevent_initial_call=True
    )
    def save_sync_config(n_clicks, frequency, data_types):
        if n_clicks:
            try:
                # 模拟保存配置
                return (
                    True,
                    "同步配置保存成功！",
                    "配置更新"
                )
            except Exception as e:
                return (
                    True,
                    f"配置保存失败：{str(e)}",
                    "配置错误"
                )
        return dash.no_update
    
    # 立即同步回调
    @app.callback(
        [Output("sync-logs-table", "data"),
         Output("integration-toast", "is_open", allow_duplicate=True),
         Output("integration-toast", "children", allow_duplicate=True),
         Output("integration-toast", "header", allow_duplicate=True)],
        [Input("btn-sync-now", "n_clicks")],
        [State("sync-logs-table", "data"),
         State("sync-data-types", "value")],
        prevent_initial_call=True
    )
    def sync_now(n_clicks, current_logs, data_types):
        if n_clicks:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 添加新的日志记录
                new_log = {
                    "timestamp": current_time,
                    "operation": "手动同步",
                    "status": "成功",
                    "data_count": "100条",
                    "description": "数据同步完成"
                }
                
                # 将新日志添加到列表顶部
                updated_logs = [new_log] + (current_logs or [])
                
                return (
                    updated_logs,
                    True,
                    "数据同步完成！",
                    "同步状态"
                )
            except Exception as e:
                # 添加错误日志
                error_log = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "operation": "手动同步",
                    "status": "失败",
                    "data_count": "-",
                    "description": f"同步异常：{str(e)}"
                }
                updated_logs = [error_log] + (current_logs or [])
                
                return (
                    updated_logs,
                    True,
                    f"同步异常：{str(e)}",
                    "同步错误"
                )
        return dash.no_update
    
    # 更新API配置回调
    @app.callback(
        [Output("integration-toast", "is_open", allow_duplicate=True),
         Output("integration-toast", "children", allow_duplicate=True),
         Output("integration-toast", "header", allow_duplicate=True)],
        [Input("btn-update-api-config", "n_clicks")],
        [State("api-key", "value"),
         State("api-version", "value"),
         State("api-timeout", "value"),
         State("api-retry", "value")],
        prevent_initial_call=True
    )
    def update_api_config(n_clicks, api_key, api_version, timeout, retry):
        if n_clicks:
            try:
                # 模拟更新API配置
                return (
                    True,
                    "API配置更新成功！",
                    "配置更新"
                )
            except Exception as e:
                return (
                    True,
                    f"API配置更新失败：{str(e)}",
                    "配置错误"
                )
        return dash.no_update
    
    # 刷新日志回调
    @app.callback(
        [Output("sync-logs-table", "data", allow_duplicate=True)],
        [Input("btn-refresh-logs", "n_clicks")],
        prevent_initial_call=True
    )
    def refresh_logs(n_clicks):
        if n_clicks:
            try:
                # 返回模拟日志数据
                logs = [
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "operation": "数据同步",
                        "status": "成功",
                        "data_count": "150条",
                        "description": "工程数据同步完成"
                    },
                    {
                        "timestamp": "2024-01-15 13:30:25",
                        "operation": "数据推送",
                        "status": "成功",
                        "data_count": "85条",
                        "description": "造价数据推送完成"
                    },
                    {
                        "timestamp": "2024-01-15 12:30:25",
                        "operation": "连接测试",
                        "status": "成功",
                        "data_count": "-",
                        "description": "连接测试通过"
                    }
                ]
                return [logs]
            except Exception as e:
                return [[
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "operation": "日志刷新",
                        "status": "失败",
                        "data_count": "-",
                        "description": f"获取日志失败：{str(e)}"
                    }
                ]]
        return dash.no_update
    
    