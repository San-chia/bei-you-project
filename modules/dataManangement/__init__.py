# modules/dataManagement/__init__.py (在现有的基础上添加)
from .layout import create_data_layout
from .callbacks import (
    register_data_callbacks,
    create_db_connection,
    get_all_tables,
    # 基础指标相关函数
    get_basic_indicators,
    update_basic_indicator,
    add_basic_indicator,
    delete_basic_indicator,
    # 复合指标相关函数
    get_composite_indicators,
    update_composite_indicator,
    add_composite_indicator,
    delete_composite_indicator,
    get_composite_dependencies,
    validate_composite_formula,
    # 综合指标相关函数
    get_comprehensive_indicators,
    update_comprehensive_indicator,
    add_comprehensive_indicator,
    delete_comprehensive_indicator,
    check_comprehensive_indicator_code_exists,
    get_next_comprehensive_indicator_id,
    get_comprehensive_dependencies,
    validate_comprehensive_logic,
    # 算法配置相关函数 - 保持不变
    get_algorithm_config,
    get_all_algorithm_configs,
    get_enabled_algorithms,
    update_algorithm_status,
    update_algorithm_parameters,
    check_prediction_availability,
    get_algorithm_status_summary,
    get_construction_mode_chinese_name,
    perform_prediction_with_mode_algorithms,
    get_all_modes_prediction_status
)
from .modals import (
    create_import_modal,
    create_basic_indicator_modal,
    create_composite_indicator_modal,
    create_comprehensive_indicator_modal,
    create_algorithm_config_modal,
    create_model_training_modal,
    # 修改：将预测精度评估改为模型性能对比
    create_model_comparison_modal,  # 新增
    create_model_evaluation_modal,  # 保留以兼容，但重定向到新功能
    import_choice_modal,
)
from .translation import (
    translate_table_name,
    translate_field_name,
    translate_dataframe_columns,
    translate_table_options,
    reverse_translate_table_name,
    reverse_translate_field_name,
    TABLE_TRANSLATIONS,
    FIELD_TRANSLATIONS,
    REVERSE_TABLE_TRANSLATIONS,
    REVERSE_FIELD_TRANSLATIONS
)