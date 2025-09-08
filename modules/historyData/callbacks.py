# modules/historyData/callbacks.py (修改版本)
import json
import os
from datetime import datetime
from dash.exceptions import PreventUpdate
from dash import Output, Input, State, callback_context
import dash_bootstrap_components as dbc

from .data import (
    get_table_schema, get_table_data, get_next_id, update_record, add_record, delete_record,
    get_all_project_tables, dynamic_get_schema_from_table, restore_deleted_record,
    debug_database_structure
)
from .translation import (
    translate_history_table_name,
    translate_history_field_name,
    reverse_translate_field_name,
    translate_table_options
)

def register_history_data_callbacks(app):
    # 启动时调试数据库结构
    try:
        debug_database_structure()
    except Exception as e:
        print(f"调试数据库结构失败: {e}")

    # 1. 更新项目下拉框选项
    @app.callback(
        Output('project-select', 'options'),
        [Input('btn-refresh', 'n_clicks'),
        Input('construction-mode-radio', 'value')],  # 新增：监听模式变化
        prevent_initial_call=False  # 允许初始调用
    )
    def update_project_options(n_clicks, mode_value):
        """更新项目选项，根据施工模式显示对应数据库的项目"""
        try:
            current_mode = mode_value or 'steel_cage'
            print(f"更新项目选项，当前模式: {current_mode}")
            return get_all_project_tables(current_mode)  # 传入模式参数
        except Exception as e:
            print(f"更新项目选项失败: {e}")
            return []

    # 2. 主表格数据更新回调（实现左右互相覆盖）
    @app.callback(
        [Output('construction-data-table', 'columns'),
        Output('construction-data-table', 'data'),
        Output('current-mode', 'data'),
        Output('data-stats', 'children'),
        Output('table-pagination', 'max_value'),
        Output('current-table-name', 'data'),
        Output('project-select', 'value', allow_duplicate=True)],  # 项目选择控制
        [Input('construction-mode-radio', 'value'),
        Input('btn-refresh', 'n_clicks'),
        Input('btn-search', 'n_clicks'),
        Input('project-select', 'value')],
        [State('search-input2', 'value'),
        State('current-mode', 'data')],
        prevent_initial_call=True
    )
    def update_table_data(mode_value, n_refresh, n_search, selected_project, search_term, current_mode):
        # 在函数开始就定义所有变量
        mode_to_use = mode_value or current_mode or 'steel_cage'
        current_table_name = ""
        schema = None
        data = []
        table_display_name = "默认表格"
        project_value_to_return = selected_project  # 默认保持当前项目选择
        
        try:
            ctx = callback_context
            trigger_id = 'construction-mode-radio'
            if ctx.triggered:
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            print(f"Debug: trigger_id={trigger_id}, mode_value={mode_value}, selected_project={selected_project}")

            # 关键逻辑：根据触发器决定显示什么数据
            if trigger_id == 'construction-mode-radio':
                # 左边施工模式被点击，清空右边项目选择，显示施工模式数据
                project_value_to_return = None  # 清空项目选择
                
                schema = get_table_schema(mode_to_use)
                if not schema:
                    # 如果施工模式数据库没有找到表，尝试使用该模式下的项目表作为替代
                    try:
                        project_options = get_all_project_tables(mode_to_use)  # 传入模式参数
                        if project_options:
                            first_project = project_options[0]['value']
                            schema = dynamic_get_schema_from_table(first_project, mode_to_use)  # 传入模式参数
                            current_table_name = first_project
                            # 翻译表名为中文显示
                            chinese_table_name = translate_history_table_name(first_project)
                            table_display_name = f"默认显示: {chinese_table_name}"
                            data = get_table_data(first_project, mode=mode_to_use)  # 传入模式参数
                            print(f"施工模式表未找到，使用项目表作为默认: {first_project}")
                        else:
                            return [], [], mode_to_use, f"未找到可用的数据表", 1, "", None
                    except Exception as e:
                        print(f"获取项目表作为替代失败: {e}")
                        return [], [], mode_to_use, f"未找到可用的数据表", 1, "", None
                else:
                    current_table_name = schema['table_name']
                    table_display_name = schema.get('display_name', '未知模式')
                    use_mode_db = schema.get('use_mode_db', False)
                    
                    # 获取施工模式数据
                    if trigger_id == 'btn-search' and search_term and search_term.strip():
                        data = get_table_data(current_table_name, search_term, use_mode_db=use_mode_db)
                    else:
                        data = get_table_data(current_table_name, use_mode_db=use_mode_db)
                    
                    print(f"显示施工模式数据: {mode_to_use}, 表: {current_table_name}, 专用数据库: {use_mode_db}")
                    
            elif trigger_id == 'project-select':
                # 右边项目被选择，显示项目数据
                if selected_project:
                    current_table_name = selected_project
                    schema = dynamic_get_schema_from_table(selected_project, mode_to_use)  # 传入模式参数
                    if not schema:
                        return [], [], mode_to_use, f"无法获取项目 {selected_project} 的数据", 1, "", selected_project
                    
                    if trigger_id == 'btn-search' and search_term and search_term.strip():
                        data = get_table_data(selected_project, search_term, mode=mode_to_use)  # 传入模式参数
                    else:
                        data = get_table_data(selected_project, mode=mode_to_use)  # 传入模式参数
                    
                    # 翻译项目表名为中文显示
                    chinese_table_name = translate_history_table_name(selected_project)
                    table_display_name = f"项目: {chinese_table_name}"
                    print(f"显示项目数据: {selected_project} (模式: {mode_to_use})")
                else:
                    # 项目被清空，显示当前施工模式数据
                    schema = get_table_schema(mode_to_use)
                    if schema:
                        current_table_name = schema['table_name']
                        table_display_name = schema.get('display_name', '未知模式')
                        use_mode_db = schema.get('use_mode_db', False)
                        data = get_table_data(current_table_name, use_mode_db=use_mode_db)
                        print(f"项目清空，回到施工模式数据: {mode_to_use}")
                    else:
                        return [], [], mode_to_use, "无可用数据", 1, "", None
            
            else:
                # 其他触发器（刷新、搜索等），保持当前显示的数据源
                if selected_project:
                    # 当前显示的是项目数据
                    current_table_name = selected_project
                    schema = dynamic_get_schema_from_table(selected_project, mode_to_use)  # 传入模式参数
                    if not schema:
                        return [], [], mode_to_use, f"无法获取项目 {selected_project} 的数据", 1, "", selected_project
                    
                    if trigger_id == 'btn-search' and search_term and search_term.strip():
                        data = get_table_data(selected_project, search_term, mode=mode_to_use)  # 传入模式参数
                    else:
                        data = get_table_data(selected_project, mode=mode_to_use)  # 传入模式参数
                    
                    # 翻译项目表名为中文显示
                    chinese_table_name = translate_history_table_name(selected_project)
                    table_display_name = f"项目: {chinese_table_name}"
                    print(f"保持项目数据: {selected_project} (模式: {mode_to_use})")
                else:
                    # 当前显示的是施工模式数据
                    schema = get_table_schema(mode_to_use)
                    if schema:
                        current_table_name = schema['table_name']
                        table_display_name = schema.get('display_name', '未知模式')
                        use_mode_db = schema.get('use_mode_db', False)
                        
                        if trigger_id == 'btn-search' and search_term and search_term.strip():
                            data = get_table_data(current_table_name, search_term, use_mode_db=use_mode_db)
                        else:
                            data = get_table_data(current_table_name, use_mode_db=use_mode_db)
                        
                        print(f"保持施工模式数据: {mode_to_use}")
                    else:
                        return [], [], mode_to_use, "无可用数据", 1, "", None

            print(f"Debug: current_table_name={current_table_name}, schema存在={schema is not None}, data数量={len(data) if data else 0}")

            # 确保有有效的schema
            if not schema:
                return [], [], mode_to_use, "无可用数据", 1, "", project_value_to_return

            # 构建列定义
            columns = []
            
            # 添加操作列
            columns.append({
                "id": "operations",
                "name": "操作",
                "type": "text",
                "editable": False
            })
            
            # 添加原有列（schema中的列名已经是翻译后的中文）
            for col in schema["columns"]:
                chinese_timestamp = translate_history_field_name("timestamp")
                if col["name"] != chinese_timestamp:  # 隐藏时间戳列
                    # 检查是否为ID类列（使用中文名称判断）
                    is_id_column = col["name"] in ["序号", "ID", "id", "ROWID"]
                    column_def = {
                        "id": col["name"],  # 使用中文名称作为ID 
                        "name": col["name"], 
                        "type": col["type"],
                        "editable": not is_id_column  # ID类列不可编辑
                    }
                    columns.append(column_def)

            # 确保data是列表格式
            if not isinstance(data, list):
                data = []

            # 为每行数据添加操作按钮和行类型标识
            for i, row in enumerate(data):
                if isinstance(row, dict):
                    row["operations"] = "删除"
                    row["row_type"] = "normal"  # 标识为普通行
                else:
                    print(f"警告: 第{i}行数据格式不正确: {row}")

            # 添加一个新增行
            if schema and schema.get("columns"):
                new_row = {
                    "operations": "新增",
                    "row_type": "new"  # 标识为新增行
                }
                
                for col in schema["columns"]:
                    chinese_id_field = translate_history_field_name("sequence_number")
                    chinese_timestamp_field = translate_history_field_name("timestamp")
                    
                    if col["name"] in [chinese_id_field, "ID", "id"]:
                        try:
                            # 需要区分项目数据和施工模式数据
                            if selected_project:
                                # 项目数据：传入mode参数
                                new_row[col["name"]] = get_next_id(current_table_name, mode_to_use) if current_table_name else 1
                            else:
                                # 施工模式数据：不传mode参数
                                new_row[col["name"]] = get_next_id(current_table_name) if current_table_name else 1
                        except Exception as e:
                            print(f"获取下一个ID失败: {e}")
                            new_row[col["name"]] = 1
                    elif col["name"] not in [chinese_timestamp_field, "ROWID"]:
                        new_row[col["name"]] = ""
                data.append(new_row)

            # 分页计算
            page_size = 15
            total_pages = max(1, (len(data) + page_size - 1) // page_size)

            # 构建统计信息
            actual_data_count = max(0, len(data) - 1) if data else 0  # 减去新增行
            if trigger_id == 'btn-search' and search_term and search_term.strip():
                stats_text = f"{table_display_name} - 搜索 '{search_term}' 结果: 共 {actual_data_count} 条记录"
            else:
                stats_text = f"{table_display_name} - 共 {actual_data_count} 条记录"

            print(f"Debug: 最终返回 - columns={len(columns)}, data={len(data)}, mode={mode_to_use}, project={project_value_to_return}")
            return columns, data, mode_to_use, stats_text, total_pages, current_table_name, project_value_to_return

        except Exception as e:
            print(f"更新表格数据失败: {e}")
            import traceback
            traceback.print_exc()
            # 确保在异常情况下也返回有效的 mode_to_use
            return [], [], mode_to_use, f"加载数据失败: {str(e)}", 1, "", project_value_to_return

    # 3. 处理表格单元格编辑（简化版）
    @app.callback(
        Output('operation-feedback', 'children'),
        Input('construction-data-table', 'data'),
        [State('construction-data-table', 'data_previous'),
        State('project-select', 'value'),
        State('construction-mode-radio', 'value'),
        State('current-table-name', 'data')]
    )
    def handle_table_edit(current_data, previous_data, selected_project, mode_value, current_table_name):
        if not current_data or not previous_data or len(current_data) == 0:
            raise PreventUpdate
        
        try:
            # 确定当前模式
            current_mode = mode_value or 'steel_cage'
            
            # 获取当前使用的表名和schema
            if selected_project:
                table_name = selected_project
                schema = dynamic_get_schema_from_table(selected_project, current_mode)  # 传入模式参数
            else:
                schema = get_table_schema(current_mode)
                table_name = schema['table_name'] if schema else None
            
            if not table_name or not schema:
                return dbc.Alert("错误：无法确定目标表", color="danger", duration=3000)

            # 比较数据找出变化
            for i in range(min(len(current_data), len(previous_data))):
                current_row = current_data[i]
                previous_row = previous_data[i]
                
                if not isinstance(current_row, dict) or not isinstance(previous_row, dict):
                    continue
                
                # 跳过新增行的常规编辑检查
                if current_row.get("operations") == "新增":
                    continue
                
                # 检查是否有变化
                has_changes = False
                for key in current_row:
                    if key not in ["operations", "row_type"] and str(current_row.get(key, "")) != str(previous_row.get(key, "")):
                        has_changes = True
                        break
                
                if has_changes:
                    # 准备更新数据
                    record_data = {}
                    for col in schema["columns"]:
                        chinese_id_field = translate_history_field_name("sequence_number")
                        chinese_timestamp_field = translate_history_field_name("timestamp")
                        
                        if col["name"] not in [chinese_id_field, chinese_timestamp_field]:
                            value = current_row.get(col["name"], "")
                            # 处理数值字段（检查中文字段名）
                            if "单价" in col["name"]:
                                try:
                                    value = float(value) if str(value).strip() != "" else 0.0
                                except (ValueError, TypeError):
                                    value = 0.0
                            record_data[col["name"]] = value
                    
                    record_data[translate_history_field_name("timestamp")] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    chinese_id_field = translate_history_field_name("sequence_number")
                    record_id = current_row.get(chinese_id_field)
                    
                    if record_id:
                        # 根据是否为项目数据选择更新方法
                        if selected_project:
                            success = update_record(table_name, record_id, record_data, current_mode)  # 传入模式参数
                        else:
                            # 施工模式数据使用原有方法
                            success = update_record(table_name, record_id, record_data)
                        
                        if success:
                            return dbc.Alert("记录更新成功！", color="success", duration=3000)
                        else:
                            return dbc.Alert("记录更新失败！", color="danger", duration=3000)
            
            # 检查是否是新增行的编辑
            if len(current_data) > 0:
                last_row = current_data[-1]
                if isinstance(last_row, dict) and last_row.get("operations") == "新增":
                    # 检查新增行是否有数据
                    has_data = False
                    for col in schema["columns"]:
                        chinese_id_field = translate_history_field_name("sequence_number")
                        chinese_timestamp_field = translate_history_field_name("timestamp")
                        
                        if col["name"] not in [chinese_id_field, chinese_timestamp_field, "operations", "row_type"]:
                            if str(last_row.get(col["name"], "")).strip():
                                has_data = True
                                break
                    
                    if has_data:
                        # 检查必填字段（使用中文字段名）
                        chinese_mode_field = translate_history_field_name("mode")
                        chinese_category_field = translate_history_field_name("parameter_category")
                        required_fields = [chinese_mode_field, chinese_category_field]
                        
                        for field in required_fields:
                            if not str(last_row.get(field, "")).strip():
                                return dbc.Alert(f"错误：{field}为必填项", color="warning", duration=3000)
                        
                        # 添加新记录
                        record_data = {}
                        for col in schema["columns"]:
                            chinese_id_field = translate_history_field_name("sequence_number")
                            chinese_timestamp_field = translate_history_field_name("timestamp")
                            
                            if col["name"] not in [chinese_id_field, chinese_timestamp_field]:
                                value = last_row.get(col["name"], "")
                                if "单价" in col["name"]:
                                    try:
                                        value = float(value) if str(value).strip() != "" else 0.0
                                    except (ValueError, TypeError):
                                        value = 0.0
                                record_data[col["name"]] = value
                        
                        # 根据是否为项目数据选择添加方法
                        if selected_project:
                            chinese_id_field = translate_history_field_name("sequence_number")
                            chinese_timestamp_field = translate_history_field_name("timestamp")
                            record_data[chinese_id_field] = get_next_id(table_name, current_mode)  # 传入模式参数
                            record_data[chinese_timestamp_field] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            success = add_record(table_name, record_data, current_mode)  # 传入模式参数
                        else:
                            # 施工模式数据使用原有方法
                            chinese_id_field = translate_history_field_name("sequence_number")
                            chinese_timestamp_field = translate_history_field_name("timestamp")
                            record_data[chinese_id_field] = get_next_id(table_name)
                            record_data[chinese_timestamp_field] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            success = add_record(table_name, record_data)
                        
                        if success:
                            return dbc.Alert("新记录添加成功！请刷新页面查看", color="success", duration=4000)
                        else:
                            return dbc.Alert("新记录添加失败！", color="danger", duration=3000)
            
            raise PreventUpdate
            
        except Exception as e:
            print(f"处理表格编辑失败: {e}")
            return dbc.Alert(f"操作失败：{str(e)}", color="danger", duration=3000)

    # 4. 处理删除操作（简化版）
    @app.callback(
        [Output('construction-data-table', 'data', allow_duplicate=True),
        Output('delete-feedback', 'children'),
        Output('deleted-record-store', 'data'),
        Output('btn-undo-delete', 'disabled')],
        Input('construction-data-table', 'active_cell'),
        [State('construction-data-table', 'data'),
        State('project-select', 'value'),
        State('construction-mode-radio', 'value'),
        State('current-table-name', 'data')],
        prevent_initial_call=True
    )
    def handle_delete_click(active_cell, table_data, selected_project, mode_value, current_table_name):
        if not active_cell or not table_data:
            raise PreventUpdate
        
        try:
            # 确定当前模式
            current_mode = mode_value or 'steel_cage'
            
            # 检查是否点击了操作列的删除
            if active_cell.get('column_id') == 'operations':
                row_index = active_cell.get('row')
                if row_index is not None and row_index < len(table_data):
                    clicked_row = table_data[row_index]
                    
                    if not isinstance(clicked_row, dict):
                        raise PreventUpdate
                    
                    # 检查是否是删除操作（不是新增行）
                    if clicked_row.get('operations') == '删除':
                        # 获取当前使用的表名
                        if selected_project:
                            table_name = selected_project
                        else:
                            schema = get_table_schema(current_mode)
                            table_name = schema['table_name'] if schema else None
                        
                        if not table_name:
                            return table_data, dbc.Alert("错误：无法确定目标表", color="danger", duration=3000), {}, True
                        
                        # 使用中文字段名获取记录ID
                        chinese_id_field = translate_history_field_name("sequence_number")
                        record_id = clicked_row.get(chinese_id_field)
                        
                        if record_id:
                            # 根据是否为项目数据选择删除方法
                            if selected_project:
                                success, deleted_data = delete_record(table_name, record_id, current_mode)  # 传入模式参数
                            else:
                                # 施工模式数据使用原有方法
                                success, deleted_data = delete_record(table_name, record_id)
                            
                            if success and deleted_data:
                                # 立即从表格数据中移除该行
                                updated_table_data = [row for i, row in enumerate(table_data) if i != row_index]
                                
                                # 保存删除的记录信息
                                deleted_record_info = {
                                    'table_name': table_name,
                                    'deleted_data': deleted_data,
                                    'delete_time': datetime.now().isoformat(),
                                    'row_index': row_index,
                                    'mode': current_mode,  # 保存模式信息
                                    'is_project': selected_project is not None,  # 标记是否为项目数据
                                    'use_mode': current_mode if selected_project else None 
                                }
                                return (updated_table_data,
                                    dbc.Alert("记录删除成功！该行已立即移除", color="success", duration=3000), 
                                    deleted_record_info, False)
                            else:
                                return table_data, dbc.Alert("记录删除失败！", color="danger", duration=3000), {}, True
                        else:
                            return table_data, dbc.Alert("错误：无法获取记录ID", color="danger", duration=3000), {}, True
            
            raise PreventUpdate
            
        except Exception as e:
            print(f"处理删除操作失败: {e}")
            return table_data, dbc.Alert(f"删除失败：{str(e)}", color="danger", duration=3000), {}, True

    # 5. 处理撤回操作
    @app.callback(
        [Output('undo-feedback', 'children'),
        Output('construction-data-table', 'data', allow_duplicate=True),
        Output('deleted-record-store', 'data', allow_duplicate=True),
        Output('btn-undo-delete', 'disabled', allow_duplicate=True)],
        Input('btn-undo-delete', 'n_clicks'),
        [State('deleted-record-store', 'data'),
        State('construction-data-table', 'data')],
        prevent_initial_call=True
    )
    def handle_undo_operation(n_clicks, deleted_record_info, current_table_data):
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # 如果有删除记录，则恢复删除
            if deleted_record_info and deleted_record_info.get('deleted_data'):
                table_name = deleted_record_info.get('table_name')
                deleted_data = deleted_record_info.get('deleted_data')
                row_index = deleted_record_info.get('row_index', len(current_table_data))
                mode = deleted_record_info.get('mode', 'steel_cage')
                is_project = deleted_record_info.get('is_project', False)
                use_mode = deleted_record_info.get('use_mode')  # 获取保存的模式参数

                if not table_name or not deleted_data:
                    return dbc.Alert("错误：没有可撤回的删除记录", color="warning", duration=3000), current_table_data, {}, True
                
                # 根据是否为项目数据选择恢复方法
                if is_project and use_mode:
                    success = restore_deleted_record(table_name, deleted_data, use_mode)  # 传入模式参数
                else:
                    success = restore_deleted_record(table_name, deleted_data)  # 施工模式数据不传mode
                            
                if success:
                    # 将删除的记录重新插入到表格数据中的原位置
                    updated_data = current_table_data.copy()
                    
                    # 重新构造删除的行数据（添加操作列和行类型）
                    restored_row = deleted_data.copy()
                    restored_row["operations"] = "删除"
                    restored_row["row_type"] = "normal"
                    
                    # 插入到原位置或末尾（新增行之前）
                    if len(updated_data) > 0 and updated_data[-1].get("row_type") == "new":
                        # 如果最后一行是新增行，在其之前插入
                        insert_index = min(row_index, len(updated_data) - 1)
                        updated_data.insert(insert_index, restored_row)
                    else:
                        # 否则直接添加到末尾
                        updated_data.append(restored_row)
                    
                    return (dbc.Alert("记录恢复成功！", color="success", duration=3000), 
                        updated_data, {}, True)
                else:
                    return dbc.Alert("记录恢复失败！", color="danger", duration=3000), current_table_data, deleted_record_info, False
            else:
                return dbc.Alert("没有可撤回的操作", color="info", duration=3000), current_table_data, {}, True
                
        except Exception as e:
            print(f"处理撤回操作失败: {e}")
            return dbc.Alert(f"撤回失败：{str(e)}", color="danger", duration=3000), current_table_data, deleted_record_info, False
        