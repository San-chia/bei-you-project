# modules/report_management/templates.py
"""报表模板配置文件"""
from enum import Enum
from typing import Dict, List, Any, Optional

class ReportCategory(Enum):
    """报表类别枚举"""
    TECH_ECON = "技经专业核心"
    PROJECT_MGMT = "项目管理"
    DECISION_SUPPORT = "决策支持"
    SPECIAL_ANALYSIS = "专项分析"

class ChartType(Enum):
    """图表类型枚举"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    COMBO = "combo"
    HEATMAP = "heatmap"
    WATERFALL = "waterfall"
    GAUGE = "gauge"
    RADAR = "radar"
    SANKEY = "sankey"
    TREEMAP = "treemap"

class DataSourceType(Enum):
    """数据源类型"""
    PROJECT = "项目数据"
    CONTRACT = "合同数据"
    COST = "成本数据"
    BUDGET = "预算数据"
    MATERIAL = "材料数据"
    LABOR = "人工数据"
    EQUIPMENT = "设备数据"

class StatDimension(Enum):
    """统计维度"""
    TIME = "时间"
    PROJECT = "项目"
    DEPARTMENT = "部门"
    CATEGORY = "类别"
    SUPPLIER = "供应商"
    CONTRACT_TYPE = "合同类型"
    WBS = "WBS结构"
    COST_CENTER = "成本中心"

# 图表类型配置
CHART_TYPE_CONFIG = {
    ChartType.LINE: {
        "name": "折线图",
        "icon": "chart-line",
        "suitable_for": ["趋势分析", "时间序列"],
        "required_axes": ["x", "y"],
        "max_series": 10
    },
    ChartType.BAR: {
        "name": "柱状图", 
        "icon": "chart-bar",
        "suitable_for": ["对比分析", "排名"],
        "required_axes": ["x", "y"],
        "max_series": 5
    },
    ChartType.PIE: {
        "name": "饼图",
        "icon": "chart-pie",
        "suitable_for": ["占比分析", "构成"],
        "required_axes": ["labels", "values"],
        "max_series": 1
    },
    ChartType.AREA: {
        "name": "面积图",
        "icon": "chart-area",
        "suitable_for": ["累积趋势", "堆叠分析"],
        "required_axes": ["x", "y"],
        "max_series": 5
    },
    ChartType.SCATTER: {
        "name": "散点图",
        "icon": "braille",
        "suitable_for": ["相关性分析", "分布"],
        "required_axes": ["x", "y"],
        "max_series": 5
    },
    ChartType.HEATMAP: {
        "name": "热力图",
        "icon": "th",
        "suitable_for": ["密度分析", "相关矩阵"],
        "required_axes": ["x", "y", "z"],
        "max_series": 1
    },
    ChartType.WATERFALL: {
        "name": "瀑布图",
        "icon": "sort-amount-down",
        "suitable_for": ["增减分析", "成本构成"],
        "required_axes": ["x", "y"],
        "max_series": 1
    },
    ChartType.GAUGE: {
        "name": "仪表盘",
        "icon": "tachometer-alt",
        "suitable_for": ["KPI展示", "完成率"],
        "required_axes": ["value"],
        "max_series": 1
    },
    ChartType.RADAR: {
        "name": "雷达图",
        "icon": "project-diagram",
        "suitable_for": ["多维度分析", "能力评估"],
        "required_axes": ["dimensions", "values"],
        "max_series": 3
    }
}

# 报表模板配置
REPORT_TEMPLATES = {
    "cost_analysis": {
        "name": "价格预测模块报表模版设置",
        "category": ReportCategory.TECH_ECON,
        "description": "深入分析项目成本构成、执行情况及趋势，对比直接施工与模块化施工成本差异",
        "icon": "chart-pie",
        "data_sources": {
            "available": [
                DataSourceType.COST,
                DataSourceType.BUDGET,
                DataSourceType.PROJECT,
                DataSourceType.MATERIAL,
                DataSourceType.LABOR,
                DataSourceType.EQUIPMENT
            ],
            "default": [DataSourceType.COST, DataSourceType.BUDGET]
        },
        "data_requirements": {
            "mandatory": ["calculation_results", "construction_parameter_table"],
            "optional": ["project_info", "parameter_info"]
        },
        "default_sections": [
            {
                "id": "cost_summary",
                "type": "summary_cards",
                "title": "成本汇总概览",
                "metrics": [
                    {"field": "total_direct_cost", "name": "直接施工总成本", "format": "currency"},
                    {"field": "total_modular_cost", "name": "模块化施工总成本", "format": "currency"},
                    {"field": "cost_saving", "name": "成本节约金额", "format": "currency"},
                    {"field": "saving_rate", "name": "成本节约率", "format": "percentage"}
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "cost_comparison_chart",
                "name": "成本对比分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "BAR", "label": "柱状图"},
                            {"value": "COMBO", "label": "组合图"},
                            {"value": "WATERFALL", "label": "瀑布图"}
                        ],
                        "default": "BAR"
                    },
                    "comparison_dimension": {
                        "type": "select",
                        "label": "对比维度",
                        "options": [
                            {"value": "cost_type", "label": "成本类型"},
                            {"value": "parameter_category", "label": "参数类别"},
                            {"value": "time_period", "label": "时间周期"}
                        ],
                        "default": "cost_type"
                    },
                    "show_percentage": {
                        "type": "checkbox",
                        "label": "显示百分比",
                        "default": True
                    }
                }
            },
            {
                "id": "cost_composition",
                "name": "成本构成分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "PIE", "label": "饼图"},
                            {"value": "TREEMAP", "label": "树形图"},
                            {"value": "SANKEY", "label": "桑基图"}
                        ],
                        "default": "PIE"
                    },
                    "construction_mode": {
                        "type": "select",
                        "label": "施工模式",
                        "options": [
                            {"value": "direct", "label": "直接施工"},
                            {"value": "modular", "label": "模块化施工"},
                            {"value": "both", "label": "同时显示"}
                        ],
                        "default": "both"
                    }
                }
            },
            {
                "id": "cost_detail_table",
                "name": "成本明细表",
                "type": "table",
                "configurable": True,
                "columns": [
                    {"field": "parameter_category", "title": "参数类别", "sortable": True},
                    {"field": "engineering_parameter", "title": "工程参数", "sortable": True},
                    {"field": "unit", "title": "单位"},
                    {"field": "direct_unit_price", "title": "直接施工单价", "format": "currency"},
                    {"field": "modular_unit_price", "title": "模块化施工单价", "format": "currency"},
                    {"field": "price_difference", "title": "单价差异", "format": "currency"},
                    {"field": "difference_rate", "title": "差异率", "format": "percentage"}
                ],
                "config_options": {
                    "show_subtotal": {
                        "type": "checkbox",
                        "label": "显示小计",
                        "default": True
                    },
                    "group_by": {
                        "type": "select",
                        "label": "分组方式",
                        "options": [
                            {"value": "category", "label": "按类别分组"},
                            {"value": "none", "label": "不分组"}
                        ],
                        "default": "category"
                    }
                }
            }
        ]
    },
    
    "efficiency_comparison": {
        "name": "施工效率对比报表",
        "category": ReportCategory.PROJECT_MGMT,
        "description": "对比分析不同项目、部门或时期的施工效率，识别优化空间",
        "icon": "chart-line",
        "data_sources": {
            "available": [
                DataSourceType.PROJECT,
                DataSourceType.LABOR,
                DataSourceType.EQUIPMENT
            ],
            "default": [DataSourceType.PROJECT, DataSourceType.LABOR]
        },
        "data_requirements": {
            "mandatory": ["project_info", "calculation_results"],
            "optional": ["parameter_info"]
        },
        "default_sections": [
            {
                "id": "efficiency_indicators",
                "type": "kpi_cards",
                "title": "效率指标概览",
                "metrics": [
                    {
                        "field": "schedule_reduction_rate",
                        "name": "工期缩短率",
                        "format": "percentage",
                        "target": 0.2,
                        "thresholds": {"good": 0.15, "warning": 0.1}
                    },
                    {
                        "field": "labor_efficiency_improvement",
                        "name": "人工效率提升",
                        "format": "percentage",
                        "target": 0.25,
                        "thresholds": {"good": 0.2, "warning": 0.15}
                    },
                    {
                        "field": "overall_efficiency_score",
                        "name": "综合效率评分",
                        "format": "number",
                        "target": 85,
                        "thresholds": {"good": 80, "warning": 70}
                    }
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "schedule_comparison",
                "name": "工期对比分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "BAR", "label": "柱状图"},
                            {"value": "LINE", "label": "折线图"},
                            {"value": "COMBO", "label": "组合图"}
                        ],
                        "default": "BAR"
                    },
                    "display_mode": {
                        "type": "select",
                        "label": "显示方式",
                        "options": [
                            {"value": "absolute", "label": "绝对工日"},
                            {"value": "percentage", "label": "百分比"},
                            {"value": "both", "label": "同时显示"}
                        ],
                        "default": "both"
                    }
                }
            },
            {
                "id": "efficiency_trend",
                "name": "效率趋势分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "LINE", "label": "折线图"},
                            {"value": "AREA", "label": "面积图"}
                        ],
                        "default": "LINE"
                    },
                    "time_granularity": {
                        "type": "select",
                        "label": "时间粒度",
                        "options": [
                            {"value": "month", "label": "按月"},
                            {"value": "quarter", "label": "按季度"},
                            {"value": "year", "label": "按年"}
                        ],
                        "default": "month"
                    },
                    "metrics_to_show": {
                        "type": "multi_select",
                        "label": "显示指标",
                        "options": [
                            {"value": "labor_efficiency", "label": "人工效率"},
                            {"value": "equipment_efficiency", "label": "设备效率"},
                            {"value": "material_efficiency", "label": "材料利用率"}
                        ],
                        "default": ["labor_efficiency", "equipment_efficiency"]
                    }
                }
            },
            {
                "id": "efficiency_analysis_table",
                "name": "效率分析明细表",
                "type": "table",
                "configurable": True,
                "columns": [
                    {"field": "parameter_category", "title": "参数类别", "sortable": True},
                    {"field": "normal_days", "title": "正常施工工日", "format": "number"},
                    {"field": "modular_days", "title": "模块化施工工日", "format": "number"},
                    {"field": "days_saved", "title": "节约工日", "format": "number"},
                    {"field": "efficiency_rate", "title": "效率提升率", "format": "percentage"},
                    {"field": "cost_per_day_saved", "title": "单位工日成本节约", "format": "currency"}
                ]
            }
        ]
    },
    
    "resource_utilization": {
        "name": "资源利用率报表",
        "category": ReportCategory.PROJECT_MGMT,
        "description": "分析人力、设备、材料等资源的利用效率和优化潜力",
        "icon": "users",
        "data_sources": {
            "available": [
                DataSourceType.LABOR,
                DataSourceType.EQUIPMENT,
                DataSourceType.MATERIAL,
                DataSourceType.PROJECT
            ],
            "default": [DataSourceType.LABOR, DataSourceType.EQUIPMENT]
        },
        "data_requirements": {
            "mandatory": ["construction_parameter_table", "parameter_info"],
            "optional": ["steel_lining"]
        },
        "default_sections": [
            {
                "id": "resource_overview",
                "type": "summary_cards",
                "title": "资源利用概览",
                "metrics": [
                    {"field": "labor_utilization_rate", "name": "人力资源利用率", "format": "percentage"},
                    {"field": "material_utilization_rate", "name": "材料资源利用率", "format": "percentage"},
                    {"field": "equipment_utilization_rate", "name": "设备资源利用率", "format": "percentage"},
                    {"field": "overall_resource_efficiency", "name": "综合资源效率", "format": "percentage"}
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "resource_cost_analysis",
                "name": "资源成本分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "BAR", "label": "堆叠柱状图"},
                            {"value": "AREA", "label": "堆叠面积图"},
                            {"value": "COMBO", "label": "组合图"}
                        ],
                        "default": "BAR"
                    },
                    "resource_types": {
                        "type": "multi_select",
                        "label": "资源类型",
                        "options": [
                            {"value": "labor", "label": "人力资源"},
                            {"value": "material", "label": "材料资源"},
                            {"value": "equipment", "label": "设备资源"}
                        ],
                        "default": ["labor", "material", "equipment"]
                    },
                    "comparison_mode": {
                        "type": "select",
                        "label": "对比模式",
                        "options": [
                            {"value": "direct_vs_modular", "label": "直接vs模块化"},
                            {"value": "time_series", "label": "时间序列"},
                            {"value": "project_comparison", "label": "项目对比"}
                        ],
                        "default": "direct_vs_modular"
                    }
                }
            },
            {
                "id": "resource_efficiency_radar",
                "name": "资源效率雷达图",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "RADAR", "label": "雷达图"},
                            {"value": "BAR", "label": "条形图"}
                        ],
                        "default": "RADAR"
                    },
                    "evaluation_dimensions": {
                        "type": "multi_select",
                        "label": "评估维度",
                        "options": [
                            {"value": "utilization", "label": "利用率"},
                            {"value": "efficiency", "label": "效率"},
                            {"value": "cost_saving", "label": "成本节约"},
                            {"value": "waste_reduction", "label": "浪费减少"},
                            {"value": "quality", "label": "质量保证"}
                        ],
                        "default": ["utilization", "efficiency", "cost_saving"]
                    }
                }
            },
            {
                "id": "resource_optimization",
                "name": "资源优化建议",
                "type": "table",
                "configurable": True,
                "columns": [
                    {"field": "resource_type", "title": "资源类型"},
                    {"field": "current_utilization", "title": "当前利用率", "format": "percentage"},
                    {"field": "target_utilization", "title": "目标利用率", "format": "percentage"},
                    {"field": "gap", "title": "差距", "format": "percentage"},
                    {"field": "optimization_suggestion", "title": "优化建议"},
                    {"field": "expected_benefit", "title": "预期收益", "format": "currency"}
                ],
                "config_options": {
                    "filter_low_utilization": {
                        "type": "checkbox",
                        "label": "仅显示低利用率项",
                        "default": True
                    },
                    "utilization_threshold": {
                        "type": "number",
                        "label": "利用率阈值(%)",
                        "default": 75,
                        "min": 0,
                        "max": 100
                    }
                }
            }
        ]
    },
    
    "financial_benefit": {
        "name": "财务收益报表",
        "category": ReportCategory.DECISION_SUPPORT,
        "description": "分析项目财务绩效、收益率和投资回报情况",
        "icon": "dollar-sign",
        "data_sources": {
            "available": [
                DataSourceType.PROJECT,
                DataSourceType.BUDGET,
                DataSourceType.COST
            ],
            "default": [DataSourceType.PROJECT, DataSourceType.COST]
        },
        "data_requirements": {
            "mandatory": ["calculation_results", "prediction_reports"],
            "optional": ["price_baseline_1", "price_baseline_2"]
        },
        "default_sections": [
            {
                "id": "financial_indicators",
                "type": "summary_cards",
                "title": "财务指标概览",
                "metrics": [
                    {"field": "total_cost_saving", "name": "总成本节约", "format": "currency"},
                    {"field": "roi", "name": "投资回报率", "format": "percentage"},
                    {"field": "cost_saving_rate", "name": "成本节约率", "format": "percentage"},
                    {"field": "prediction_accuracy", "name": "预测准确率", "format": "percentage"}
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "benefit_trend",
                "name": "收益趋势分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "LINE", "label": "折线图"},
                            {"value": "AREA", "label": "面积图"},
                            {"value": "COMBO", "label": "组合图"}
                        ],
                        "default": "LINE"
                    },
                    "time_range": {
                        "type": "select",
                        "label": "时间范围",
                        "options": [
                            {"value": "3m", "label": "近3个月"},
                            {"value": "6m", "label": "近6个月"},
                            {"value": "1y", "label": "近1年"},
                            {"value": "all", "label": "全部"}
                        ],
                        "default": "6m"
                    },
                    "show_prediction": {
                        "type": "checkbox",
                        "label": "显示预测值",
                        "default": True
                    }
                }
            },
            {
                "id": "cost_benefit_waterfall",
                "name": "成本收益瀑布图",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "WATERFALL", "label": "瀑布图"},
                            {"value": "BAR", "label": "柱状图"}
                        ],
                        "default": "WATERFALL"
                    },
                    "breakdown_level": {
                        "type": "select",
                        "label": "细分级别",
                        "options": [
                            {"value": "high", "label": "高层汇总"},
                            {"value": "medium", "label": "中等细分"},
                            {"value": "detailed", "label": "详细分解"}
                        ],
                        "default": "medium"
                    }
                }
            },
            {
                "id": "financial_analysis_table",
                "name": "财务分析明细",
                "type": "table",
                "configurable": True,
                "columns": [
                    {"field": "project_name", "title": "项目名称", "sortable": True},
                    {"field": "ml_prediction", "title": "ML预测成本", "format": "currency"},
                    {"field": "ratio_prediction", "title": "比率法预测", "format": "currency"},
                    {"field": "actual_cost", "title": "实际成本", "format": "currency"},
                    {"field": "prediction_variance", "title": "预测偏差", "format": "percentage"},
                    {"field": "cost_saving", "title": "成本节约", "format": "currency"}
                ],
                "config_options": {
                    "show_variance_analysis": {
                        "type": "checkbox",
                        "label": "显示偏差分析",
                        "default": True
                    },
                    "highlight_threshold": {
                        "type": "number",
                        "label": "高亮阈值(%)",
                        "default": 10,
                        "min": 0,
                        "max": 50
                    }
                }
            }
        ]
    },
    
    "management_dashboard": {
        "name": "综合管理仪表板",
        "category": ReportCategory.DECISION_SUPPORT,
        "description": "为管理层提供关键指标的实时监控和决策支持",
        "icon": "tachometer-alt",
        "data_sources": {
            "available": [
                DataSourceType.PROJECT,
                DataSourceType.COST,
                DataSourceType.BUDGET,
                DataSourceType.LABOR,
                DataSourceType.EQUIPMENT,
                DataSourceType.MATERIAL
            ],
            "default": [DataSourceType.PROJECT, DataSourceType.COST]
        },
        "data_requirements": {
            "mandatory": ["calculation_results", "project_info"],
            "optional": ["prediction_reports", "construction_parameter_table"]
        },
        "default_sections": [
            {
                "id": "kpi_gauges",
                "type": "kpi_cards",
                "title": "核心KPI仪表盘",
                "metrics": [
                    {
                        "field": "cost_saving_rate_gauge",
                        "name": "成本节约率",
                        "format": "percentage",
                        "target": 0.2,
                        "thresholds": {"good": 0.15, "warning": 0.1, "danger": 0.05},
                        "gauge_type": "semi-circle"
                    },
                    {
                        "field": "schedule_reduction_gauge",
                        "name": "工期缩短率",
                        "format": "percentage",
                        "target": 0.15,
                        "thresholds": {"good": 0.12, "warning": 0.08, "danger": 0.05},
                        "gauge_type": "semi-circle"
                    },
                    {
                        "field": "resource_utilization_gauge",
                        "name": "资源利用率",
                        "format": "percentage",
                        "target": 0.85,
                        "thresholds": {"good": 0.8, "warning": 0.7, "danger": 0.6},
                        "gauge_type": "semi-circle"
                    },
                    {
                        "field": "prediction_accuracy_gauge",
                        "name": "预测准确率",
                        "format": "percentage",
                        "target": 0.95,
                        "thresholds": {"good": 0.92, "warning": 0.88, "danger": 0.85},
                        "gauge_type": "semi-circle"
                    }
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "comprehensive_trend",
                "name": "综合趋势分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "COMBO", "label": "组合图"},
                            {"value": "LINE", "label": "多线图"},
                            {"value": "AREA", "label": "面积图"}
                        ],
                        "default": "COMBO"
                    },
                    "primary_axis": {
                        "type": "select",
                        "label": "主轴指标",
                        "options": [
                            {"value": "cost", "label": "成本"},
                            {"value": "efficiency", "label": "效率"},
                            {"value": "schedule", "label": "进度"}
                        ],
                        "default": "cost"
                    },
                    "secondary_axis": {
                        "type": "select",
                        "label": "次轴指标",
                        "options": [
                            {"value": "percentage", "label": "百分比"},
                            {"value": "count", "label": "数量"},
                            {"value": "none", "label": "不使用"}
                        ],
                        "default": "percentage"
                    }
                }
            },
            {
                "id": "alert_panel",
                "name": "异常预警面板",
                "type": "alert_cards",
                "configurable": True,
                "alert_types": [
                    {
                        "id": "cost_overrun",
                        "name": "成本超支预警",
                        "severity_levels": ["high", "medium", "low"],
                        "threshold_field": "cost_overrun_percentage"
                    },
                    {
                        "id": "efficiency_decline",
                        "name": "效率下降预警",
                        "severity_levels": ["high", "medium", "low"],
                        "threshold_field": "efficiency_decline_rate"
                    },
                    {
                        "id": "resource_abnormal",
                        "name": "资源利用异常",
                        "severity_levels": ["high", "medium", "low"],
                        "threshold_field": "resource_abnormal_rate"
                    }
                ],
                "config_options": {
                    "alert_threshold": {
                        "type": "multi_select",
                        "label": "显示预警级别",
                        "options": [
                            {"value": "high", "label": "高级"},
                            {"value": "medium", "label": "中级"},
                            {"value": "low", "label": "低级"}
                        ],
                        "default": ["high", "medium"]
                    },
                    "auto_refresh": {
                        "type": "checkbox",
                        "label": "自动刷新",
                        "default": True
                    }
                }
            },
            {
                "id": "decision_matrix",
                "name": "快速决策矩阵",
                "type": "decision_table",
                "configurable": True,
                "columns": [
                    {"field": "decision_item", "title": "决策项"},
                    {"field": "current_status", "title": "当前状态"},
                    {"field": "risk_level", "title": "风险等级", "format": "badge"},
                    {"field": "recommended_action", "title": "建议行动"},
                    {"field": "expected_impact", "title": "预期影响"},
                    {"field": "priority", "title": "优先级", "format": "badge"}
                ],
                "config_options": {
                    "filter_by_priority": {
                        "type": "multi_select",
                        "label": "筛选优先级",
                        "options": [
                            {"value": "critical", "label": "紧急"},
                            {"value": "high", "label": "高"},
                            {"value": "medium", "label": "中"},
                            {"value": "low", "label": "低"}
                        ],
                        "default": ["critical", "high"]
                    }
                }
            }
        ]
    },
    
    "estimation_summary": {
        "name": "成本概算执行分析",
        "category": ReportCategory.TECH_ECON,
        "description": "全面分析项目概算编制与执行情况，支持多维度对比分析",
        "icon": "calculator",
        "data_sources": {
            "available": [
                DataSourceType.PROJECT,
                DataSourceType.BUDGET,
                DataSourceType.COST,
                DataSourceType.CONTRACT
            ],
            "default": [DataSourceType.PROJECT, DataSourceType.BUDGET]
        },
        "data_requirements": {
            "mandatory": ["construction_parameter_table", "calculation_results"],
            "optional": ["key_factors_1", "key_factors_2"]
        },
        "default_sections": [
            {
                "id": "estimation_overview",
                "type": "summary_cards",
                "title": "概算执行概览",
                "metrics": [
                    {"field": "total_budget", "name": "概算总额", "format": "currency"},
                    {"field": "executed_amount", "name": "已执行金额", "format": "currency"},
                    {"field": "execution_rate", "name": "执行率", "format": "percentage"},
                    {"field": "variance_rate", "name": "偏差率", "format": "percentage"}
                ]
            }
        ],
        "configurable_sections": [
            {
                "id": "execution_progress",
                "name": "执行进度分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "BAR", "label": "条形图"},
                            {"value": "COMBO", "label": "组合图"},
                            {"value": "WATERFALL", "label": "瀑布图"}
                        ],
                        "default": "BAR"
                    },
                    "group_by": {
                        "type": "select",
                        "label": "分组方式",
                        "options": [
                            {"value": "parameter_category", "label": "参数类别"},
                            {"value": "construction_mode", "label": "施工模式"},
                            {"value": "time_period", "label": "时间周期"}
                        ],
                        "default": "parameter_category"
                    },
                    "show_plan_vs_actual": {
                        "type": "checkbox",
                        "label": "显示计划vs实际",
                        "default": True
                    }
                }
            },
            {
                "id": "key_factors_analysis",
                "name": "关键因素分析",
                "type": "chart",
                "configurable": True,
                "config_options": {
                    "construction_mode": {
                        "type": "select",
                        "label": "施工模式",
                        "options": [
                            {"value": "steel_cage", "label": "钢筋笼"},
                            {"value": "steel_lining", "label": "钢衬里"}
                        ],
                        "default": "steel_cage"
                    },
                    "analysis_type": {
                        "type": "select",
                        "label": "分析类型",
                        "options": [
                            {"value": "sensitivity", "label": "敏感性分析"},
                            {"value": "correlation", "label": "相关性分析"},
                            {"value": "impact", "label": "影响度分析"}
                        ],
                        "default": "sensitivity"
                    },
                    "chart_type": {
                        "type": "select",
                        "label": "图表类型",
                        "options": [
                            {"value": "TORNADO", "label": "龙卷风图"},
                            {"value": "SCATTER", "label": "散点图"},
                            {"value": "HEATMAP", "label": "热力图"}
                        ],
                        "default": "TORNADO"
                    }
                }
            },
            {
                "id": "variance_analysis",
                "name": "偏差分析表",
                "type": "tree_table",
                "configurable": True,
                "columns": [
                    {"field": "wbs_code", "title": "WBS编码"},
                    {"field": "wbs_name", "title": "项目名称"},
                    {"field": "budget_amount", "title": "概算金额", "format": "currency"},
                    {"field": "actual_amount", "title": "实际金额", "format": "currency"},
                    {"field": "variance", "title": "偏差", "format": "currency"},
                    {"field": "variance_rate", "title": "偏差率", "format": "percentage"},
                    {"field": "reason", "title": "原因分析"}
                ],
                "config_options": {
                    "expand_level": {
                        "type": "select",
                        "label": "默认展开级别",
                        "options": [
                            {"value": "1", "label": "一级"},
                            {"value": "2", "label": "二级"},
                            {"value": "3", "label": "三级"},
                            {"value": "all", "label": "全部展开"}
                        ],
                        "default": "2"
                    },
                    "highlight_variance": {
                        "type": "checkbox",
                        "label": "高亮显示超限偏差",
                        "default": True
                    },
                    "variance_threshold": {
                        "type": "number",
                        "label": "偏差阈值(%)",
                        "default": 10,
                        "min": 0,
                        "max": 50
                    }
                }
            }
        ]
    }
}

def get_template_by_id(template_id: str) -> Dict[str, Any]:
    """根据ID获取模板配置"""
    return REPORT_TEMPLATES.get(template_id, {})

def get_available_data_sources(template_id: str) -> List[DataSourceType]:
    """获取模板可用的数据源"""
    template = get_template_by_id(template_id)
    return template.get("data_sources", {}).get("available", [])

def get_section_config(template_id: str, section_id: str) -> Dict[str, Any]:
    """获取特定section的配置"""
    template = get_template_by_id(template_id)
    for section in template.get("configurable_sections", []):
        if section["id"] == section_id:
            return section
    return {}

def get_template_categories() -> List[str]:
    """获取所有模板类别"""
    return [cat.value for cat in ReportCategory]

def get_templates_by_category(category: ReportCategory) -> Dict[str, Dict[str, Any]]:
    """根据类别获取模板"""
    return {
        tid: template 
        for tid, template in REPORT_TEMPLATES.items() 
        if template.get("category") == category
    }

def validate_template_config(template_config: Dict[str, Any]) -> bool:
    """验证模板配置是否有效"""
    required_fields = ["name", "category", "description", "data_sources", "data_requirements"]
    
    for field in required_fields:
        if field not in template_config:
            return False
    
    # 验证数据源
    if "available" not in template_config["data_sources"]:
        return False
    
    # 验证数据需求
    if "mandatory" not in template_config["data_requirements"]:
        return False
    
    return True

# 导出的函数和类
__all__ = [
    'ReportCategory',
    'ChartType',
    'DataSourceType',
    'StatDimension',
    'CHART_TYPE_CONFIG',
    'REPORT_TEMPLATES',
    'get_template_by_id',
    'get_available_data_sources',
    'get_section_config',
    'get_template_categories',
    'get_templates_by_category',
    'validate_template_config'
]