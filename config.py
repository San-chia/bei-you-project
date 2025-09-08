# project/config.py
# 定义配色方案
PRIMARY_COLOR = "#2C3E50"  # 深蓝色作为主色
SECONDARY_COLOR = "#18BC9C"  # 青绿色作为次要色
ACCENT_COLOR = "#E74C3C"  # 红色作为强调色
BG_COLOR = "#F5F5F5"  # 浅灰色背景
CARD_BG = "#FFFFFF"  # 卡片白色背景

# 主题设置
THEME = "FLATLY"
FONT_AWESOME_URL = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css'

# 其他全局配置
DEFAULT_PAGE_SIZE = 5
MAX_UPLOAD_SIZE = 10  # MB

# ==================== 一体化平台对接配置 ====================

# 平台连接配置
PLATFORM_CONFIG = {
    # 基础配置
    'base_url': 'http://platform.example.com/api',
    'api_version': 'v2.0',
    'timeout': 30,
    'retry_count': 3,
    
    # 认证配置
    'auth': {
        'type': 'bearer',  # bearer, basic, api_key
        'api_key': None,
        'username': None,
        'password': None
    },
    
    # SSL配置
    'ssl': {
        'verify': True,
        'cert_path': None,
        'key_path': None
    }
}

# 数据同步配置
SYNC_CONFIG = {
    # 同步频率选项
    'frequency_options': [
        {'label': '实时同步', 'value': 'realtime'},
        {'label': '每小时', 'value': 'hourly'},
        {'label': '每日', 'value': 'daily'},
        {'label': '手动同步', 'value': 'manual'}
    ],
    
    # 数据类型配置
    'data_types': [
        {'label': '工程数据', 'value': 'engineering', 'endpoint': 'engineering/data'},
        {'label': '造价数据', 'value': 'cost', 'endpoint': 'cost/data'},
        {'label': '进度数据', 'value': 'progress', 'endpoint': 'progress/data'},
        {'label': '质量数据', 'value': 'quality', 'endpoint': 'quality/data'}
    ],
    
    # 默认同步配置
    'default': {
        'frequency': 'hourly',
        'data_types': ['engineering', 'cost'],
        'batch_size': 100,
        'max_retries': 3
    }
}

# API端点配置
API_ENDPOINTS = {
    'health': 'health',
    'sync': 'sync',
    'logs': 'logs',
    'status': 'status',
    'data': {
        'push': 'data/push',
        'pull': 'data/pull'
    }
}

# ==================== 管理模块配置 ====================

# 用户管理配置
USER_CONFIG = {
    # 用户状态选项
    'status_options': [
        {'label': '激活', 'value': 'active'},
        {'label': '禁用', 'value': 'disabled'},
        {'label': '锁定', 'value': 'locked'}
    ],
    
    # 默认用户设置
    'defaults': {
        'status': 'active',
        'password_expiry_days': 90,
        'max_login_attempts': 5
    }
}

# 角色权限配置
ROLE_CONFIG = {
    # 预定义角色
    'predefined_roles': [
        {
            'name': '管理员',
            'code': 'admin',
            'description': '系统最高权限管理员',
            'permissions': ['data_management', 'user_management', 'system_config', 'report_generation', 'log_view', 'permission_setting']
        },
        {
            'name': '操作员',
            'code': 'operator',
            'description': '数据操作和管理人员',
            'permissions': ['data_management', 'report_generation', 'log_view']
        },
        {
            'name': '查看者',
            'code': 'viewer',
            'description': '只读权限用户',
            'permissions': ['report_view', 'log_view']
        },
        {
            'name': '审计员',
            'code': 'auditor',
            'description': '审计和监督人员',
            'permissions': ['log_view', 'audit_report', 'data_audit']
        }
    ],
    
    # 权限列表
    'permissions': [
        {'name': '数据管理', 'code': 'data_management', 'description': '数据的增删改查权限'},
        {'name': '用户管理', 'code': 'user_management', 'description': '用户账户管理权限'},
        {'name': '系统配置', 'code': 'system_config', 'description': '系统参数配置权限'},
        {'name': '报表生成', 'code': 'report_generation', 'description': '生成和编辑报表权限'},
        {'name': '报表查看', 'code': 'report_view', 'description': '查看报表权限'},
        {'name': '日志查看', 'code': 'log_view', 'description': '查看系统日志权限'},
        {'name': '权限设置', 'code': 'permission_setting', 'description': '设置用户权限'},
        {'name': '审计报告', 'code': 'audit_report', 'description': '生成审计报告'},
        {'name': '数据审核', 'code': 'data_audit', 'description': '数据审核权限'}
    ]
}

# 任务管理配置
TASK_CONFIG = {
    # 任务状态
    'status_options': [
        {'label': '待开始', 'value': 'pending', 'color': 'secondary'},
        {'label': '进行中', 'value': 'in_progress', 'color': 'warning'},
        {'label': '已完成', 'value': 'completed', 'color': 'success'},
        {'label': '已逾期', 'value': 'overdue', 'color': 'danger'},
        {'label': '已取消', 'value': 'cancelled', 'color': 'dark'}
    ],
    
    # 优先级选项
    'priority_options': [
        {'label': '高', 'value': 'high', 'color': 'danger'},
        {'label': '中', 'value': 'medium', 'color': 'warning'},
        {'label': '低', 'value': 'low', 'color': 'info'}
    ],
    
    # 任务类型
    'task_types': [
        {'label': '开发任务', 'value': 'development'},
        {'label': '测试任务', 'value': 'testing'},
        {'label': '维护任务', 'value': 'maintenance'},
        {'label': '文档任务', 'value': 'documentation'},
        {'label': '其他任务', 'value': 'other'}
    ],
    
    # 自动化规则
    'automation': {
        'auto_assign': True,  # 自动分配任务
        'reminder_days': 3,   # 截止前提醒天数
        'overdue_notification': True  # 逾期通知
    }
}

# 日志管理配置
LOG_CONFIG = {
    # 日志级别
    'log_levels': [
        {'label': '调试', 'value': 'debug', 'color': 'secondary'},
        {'label': '信息', 'value': 'info', 'color': 'info'},
        {'label': '警告', 'value': 'warning', 'color': 'warning'},
        {'label': '错误', 'value': 'error', 'color': 'danger'},
        {'label': '严重', 'value': 'critical', 'color': 'dark'}
    ],
    
    # 日志模块
    'modules': [
        {'label': '用户管理', 'value': 'user_mgmt'},
        {'label': '数据管理', 'value': 'data_mgmt'},
        {'label': '系统管理', 'value': 'system_mgmt'},
        {'label': '报表管理', 'value': 'report_mgmt'},
        {'label': '权限管理', 'value': 'permission_mgmt'},
        {'label': '任务管理', 'value': 'task_mgmt'}
    ],
    
    # 日志保留策略
    'retention': {
        'default_days': 90,  # 默认保留90天
        'error_days': 365,   # 错误日志保留1年
        'audit_days': 2555,  # 审计日志保留7年
        'max_size_mb': 1000  # 最大日志文件大小
    },
    
    # 日志导出格式
    'export_formats': [
        {'label': 'CSV', 'value': 'csv'},
        {'label': 'Excel', 'value': 'xlsx'},
        {'label': 'JSON', 'value': 'json'},
        {'label': 'PDF', 'value': 'pdf'}
    ],
    
    # 集成原有配置
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': 'logs/integration.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 系统监控配置
MONITOR_CONFIG = {
    # 监控指标
    'metrics': [
        {'name': 'CPU使用率', 'threshold': 80, 'unit': '%'},
        {'name': '内存使用率', 'threshold': 85, 'unit': '%'},
        {'name': '磁盘使用率', 'threshold': 90, 'unit': '%'},
        {'name': '网络流量', 'threshold': 100, 'unit': 'Mbps'},
        {'name': '数据库连接数', 'threshold': 80, 'unit': '个'}
    ],
    
    # 告警配置
    'alerts': {
        'email_enabled': True,
        'sms_enabled': False,
        'webhook_enabled': True,
        'alert_interval': 300  # 告警间隔（秒）
    }
}

# 数据库配置
DATABASE_CONFIG = {
    # 连接池配置
    'pool': {
        'min_connections': 5,
        'max_connections': 20,
        'connection_timeout': 30
    },
    
    # 备份配置
    'backup': {
        'auto_backup': True,
        'backup_interval': 24,  # 小时
        'backup_retention': 30,  # 天
        'backup_path': 'backups/'
    }
}

# 错误重试配置
RETRY_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1,  # 秒
    'backoff_factor': 2,
    'retry_on_status': [500, 502, 503, 504]
}

# ==================== 导出配置（供其他模块使用） ====================

# 将新配置添加到全局配置，方便导入
__all__ = [
    # 原有配置
    'PRIMARY_COLOR', 'SECONDARY_COLOR', 'ACCENT_COLOR', 'BG_COLOR', 'CARD_BG',
    'THEME', 'FONT_AWESOME_URL', 'DEFAULT_PAGE_SIZE', 'MAX_UPLOAD_SIZE',
    
    # 一体化平台配置
    'PLATFORM_CONFIG', 'SYNC_CONFIG', 'API_ENDPOINTS',
    
    # 管理模块配置
    'USER_CONFIG', 'ROLE_CONFIG', 'TASK_CONFIG', 'LOG_CONFIG', 
    'MONITOR_CONFIG', 'DATABASE_CONFIG', 'RETRY_CONFIG'
]


# 在config.py中添加模块权限映射
MODULE_PERMISSIONS = {
    'tab-1': 'indicator_calculation',    # 指标测算
    'tab-2': 'data_management',         # 指标与算法管理（原来是数据管理）
    'tab-3': 'system_config',           # 系统管理（原来是软件管理）
    'tab-4': 'report_generation',       # 报表管理
    'tab-5': 'modular_construction',    # 模块化施工
    'tab-6': 'construction_management',         # 施工数据
    'tab-7': 'price_prediction',        # 价格预测
    'tab-8': 'platform_integration',    # 对接一体化平台
}