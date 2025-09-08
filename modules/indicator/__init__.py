# modules/indicator/__init__.py
from .layout import create_indicator_layout
from .callbacks import register_indicator_callbacks


def init_indicator_module(app):
    """初始化指标测算模块"""
    register_indicator_callbacks(app)