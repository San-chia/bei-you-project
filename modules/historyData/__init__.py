# modules/historyData/__init__.py (修改版本)
from .layout import history_data_layout
from .callbacks import register_history_data_callbacks
from .translation import (
    translate_history_table_name,
    translate_history_field_name,
    reverse_translate_table_name,
    reverse_translate_field_name,
    TABLE_TRANSLATIONS,
    FIELD_TRANSLATIONS
)