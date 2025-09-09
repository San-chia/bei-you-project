# modules/report_management/data_processor.py
"""报表数据处理模块"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ReportDataProcessor:
    """报表数据处理器"""
    
    def __init__(self):
        self.data_cache = {}
        
    def fetch_data(self, data_sources: List[str], filters: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """获取报表所需数据"""
        result = {}
        
        for source in data_sources:
            # 这里应该从实际数据源获取数据
            # 现在用模拟数据代替
            if source == "project_info":
                result[source] = self._get_project_info(filters)
            elif source == "estimation_data":
                result[source] = self._get_estimation_data(filters)
            elif source == "actual_cost":
                result[source] = self._get_actual_cost_data(filters)
            elif source == "wbs_structure":
                result[source] = self._get_wbs_data(filters)
            
        return result
    
    def process_data(self, raw_data: Dict[str, pd.DataFrame], 
                    template_config: Dict) -> Dict[str, Any]:
        """根据模板配置处理数据"""
        processed = {}
        
        # 处理各个section的数据
        for section in template_config.get("default_sections", []):
            section_id = section["id"]
            section_type = section["type"]
            
            if section_type == "summary_cards":
                processed[section_id] = self._process_summary_cards(
                    raw_data, section["metrics"]
                )
            elif section_type == "chart":
                processed[section_id] = self._process_chart_data(
                    raw_data, section["config"]
                )
            elif section_type == "table":
                processed[section_id] = self._process_table_data(
                    raw_data, section["columns"]
                )
                
        return processed
    
    def _get_project_info(self, filters: Dict) -> pd.DataFrame:
        """获取项目基本信息（模拟）"""
        return pd.DataFrame([{
            "project_id": "P001",
            "project_name": "示例工程项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "total_budget": 10000000
        }])
    
    def _get_estimation_data(self, filters: Dict) -> pd.DataFrame:
        """获取概算数据（模拟）"""
        data = []
        items = ["土建工程", "安装工程", "装饰工程", "其他费用"]
        
        for i, item in enumerate(items):
            data.append({
                "item_code": f"A{i+1:03d}",
                "item_name": item,
                "estimation": (i + 1) * 2000000,
                "month": datetime.now().strftime("%Y-%m")
            })
            
        return pd.DataFrame(data)
    
    def _get_actual_cost_data(self, filters: Dict) -> pd.DataFrame:
        """获取实际成本数据（模拟）"""
        estimation_df = self._get_estimation_data(filters)
        actual_df = estimation_df.copy()
        
        # 添加随机偏差
        actual_df["actual"] = actual_df["estimation"] * (0.9 + np.random.random(len(actual_df)) * 0.2)
        actual_df["variance"] = actual_df["actual"] - actual_df["estimation"]
        actual_df["variance_rate"] = actual_df["variance"] / actual_df["estimation"]
        
        return actual_df
    
    def _get_wbs_data(self, filters: Dict) -> pd.DataFrame:
        """获取WBS数据（模拟）"""
        data = []
        
        # 创建三级WBS结构
        for i in range(3):
            # 一级
            l1_code = f"{i+1}00"
            l1_name = f"分部工程{i+1}"
            data.append({
                "wbs_code": l1_code,
                "wbs_name": l1_name,
                "level": 1,
                "parent_code": "",
                "cost": 0  # 汇总值，后续计算
            })
            
            for j in range(2):
                # 二级
                l2_code = f"{i+1}{j+1}0"
                l2_name = f"{l1_name}-子项{j+1}"
                data.append({
                    "wbs_code": l2_code,
                    "wbs_name": l2_name,
                    "level": 2,
                    "parent_code": l1_code,
                    "cost": 0
                })
                
                for k in range(3):
                    # 三级
                    l3_code = f"{i+1}{j+1}{k+1}"
                    l3_name = f"{l2_name}-细项{k+1}"
                    cost = np.random.randint(100000, 500000)
                    data.append({
                        "wbs_code": l3_code,
                        "wbs_name": l3_name,
                        "level": 3,
                        "parent_code": l2_code,
                        "cost": cost
                    })
        
        df = pd.DataFrame(data)
        
        # 计算上级汇总
        for level in [2, 1]:
            level_df = df[df["level"] == level]
            for _, row in level_df.iterrows():
                children_cost = df[df["parent_code"] == row["wbs_code"]]["cost"].sum()
                df.loc[df["wbs_code"] == row["wbs_code"], "cost"] = children_cost
                
        return df
    
    def _process_summary_cards(self, raw_data: Dict[str, pd.DataFrame], 
                             metrics: List[Dict]) -> Dict:
        """处理汇总卡片数据"""
        result = {}
        
        # 根据实际数据表结构计算指标
        if "calculation_results" in raw_data:
            calc_df = raw_data["calculation_results"]
            
            # 计算成本相关指标
            if not calc_df.empty:
                result["total_direct_cost"] = calc_df["direct_total"].sum()
                result["total_modular_cost"] = calc_df["modular_total"].sum()
                result["cost_saving"] = result["total_direct_cost"] - result["total_modular_cost"]
                result["saving_rate"] = (result["cost_saving"] / result["total_direct_cost"]) if result["total_direct_cost"] > 0 else 0
                result["cost_difference_rate"] = calc_df["cost_difference_percentage"].mean() if "cost_difference_percentage" in calc_df.columns else 0
        
        if "prediction_reports" in raw_data:
            pred_df = raw_data["prediction_reports"]
            
            # 添加预测相关指标
            if not pred_df.empty:
                result["ml_prediction_avg"] = pred_df["ml_ensemble_prediction"].mean()
                result["ratio_prediction_avg"] = pred_df["ratio_method_prediction"].mean()
                result["total_predicted_cost"] = pred_df["total_predicted_cost"].mean()
        
        if "construction_parameter_table" in raw_data:
            param_df = raw_data["construction_parameter_table"]
            
            # 计算参数相关指标
            if not param_df.empty:
                result["param_count"] = len(param_df)
                result["avg_labor_saving"] = (
                    (param_df["direct_labor_unit_price"] - param_df["modular_labor_unit_price"]).mean()
                    / param_df["direct_labor_unit_price"].mean()
                ) if param_df["direct_labor_unit_price"].mean() > 0 else 0
        
        # 设置默认值
        for metric in metrics:
            if metric["field"] not in result:
                result[metric["field"]] = 0
                
        return result
    
    def _process_chart_data(self, raw_data: Dict[str, pd.DataFrame], 
                          config: Dict) -> Dict:
        """处理图表数据"""
        # 根据配置处理数据，返回适合Plotly的格式
        return {
            "data": [],
            "layout": {}
        }
    
    def _process_table_data(self, raw_data: Dict[str, pd.DataFrame], 
                          columns: List[Dict]) -> pd.DataFrame:
        """处理表格数据"""
        # 返回适合显示的DataFrame
        if "actual_cost" in raw_data:
            return raw_data["actual_cost"]
        return pd.DataFrame()
    
    def process_configured_data(self, raw_data: Dict[str, pd.DataFrame], 
                              template_config: Dict, 
                              user_config: Dict) -> Dict[str, Any]:
        """根据用户配置处理数据"""
        processed = {}
        
        # 处理每个启用的section
        for section_idx, section in enumerate(template_config.get("configurable_sections", [])):
            section_id = section["id"]
            
            # 检查section是否启用
            if not user_config.get(f"section_enable_{section_idx}", True):
                continue
            
            # 获取section的用户配置
            section_config = {}
            for option_key in section.get("config_options", {}):
                config_key = f"section_{section_idx}_{option_key}"
                if config_key in user_config:
                    section_config[option_key] = user_config[config_key]
            
            # 根据section类型和配置处理数据
            if section["type"] == "chart":
                processed[section_id] = self._process_chart_with_config(
                    raw_data, section, section_config
                )
            elif section["type"] == "table":
                processed[section_id] = self._process_table_with_config(
                    raw_data, section, section_config
                )
            elif section["type"] == "summary_cards":
                processed[section_id] = self._process_summary_with_config(
                    raw_data, section, section_config
                )
        
        return processed

    def _process_chart_with_config(self, raw_data: Dict[str, pd.DataFrame], 
                                  section: Dict, config: Dict) -> Dict:
        """根据配置处理图表数据"""
        chart_type = config.get("chart_type", section["config_options"]["chart_type"]["default"])
        
        # 根据不同的图表类型处理数据
        if chart_type in ["LINE", "BAR", "COMBO"]:
            # 时间序列图表
            time_dim = config.get("time_dimension", "月")
            data_series = config.get("data_series", ["planned", "actual"])
            
            # 这里应该根据实际数据处理
            # 示例代码
            result_data = {
                "x": ["1月", "2月", "3月", "4月", "5月"],
                "series": {}
            }
            
            for series in data_series:
                result_data["series"][series] = [100, 120, 115, 130, 125]
            
            return {
                "type": chart_type,
                "data": result_data,
                "config": config
            }
        
        elif chart_type == "PIE":
            # 饼图数据处理
            dimension = config.get("dimension", "cost_type")
            # 处理饼图数据...
            
        return {}

    def _process_table_with_config(self, raw_data: Dict[str, pd.DataFrame],
                                 section: Dict, config: Dict) -> pd.DataFrame:
        """根据配置处理表格数据"""
        # 获取配置的分组方式
        group_by = config.get("group_by", "wbs")
        columns = config.get("columns", ["code", "name", "budget", "actual"])
        
        # 这里应该根据实际数据处理
        # 示例：返回模拟的表格数据
        if "actual_cost" in raw_data:
            df = raw_data["actual_cost"]
            # 根据配置选择列
            selected_cols = [col for col in columns if col in df.columns]
            if selected_cols:
                return df[selected_cols]
        
        return pd.DataFrame()

    def _process_summary_with_config(self, raw_data: Dict[str, pd.DataFrame],
                                   section: Dict, config: Dict) -> Dict:
        """根据配置处理汇总数据"""
        metrics = config.get("metrics", ["total_budget", "executed_amount", "execution_rate"])
        
        result = {}
        
        # 计算各个指标
        if "estimation_data" in raw_data:
            est_df = raw_data["estimation_data"]
            total_estimation = est_df["estimation"].sum()
            
            if "total_budget" in metrics:
                result["total_budget"] = total_estimation
            
            if "actual_cost" in raw_data:
                act_df = raw_data["actual_cost"]
                total_actual = act_df["actual"].sum() if "actual" in act_df.columns else 0
                
                if "executed_amount" in metrics:
                    result["executed_amount"] = total_actual
                    
                if "execution_rate" in metrics:
                    result["execution_rate"] = total_actual / total_estimation if total_estimation > 0 else 0
                
                if "saving_rate" in metrics:
                    result["saving_rate"] = (total_estimation - total_actual) / total_estimation if total_estimation > 0 else 0
        
        return result