from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import bcrypt

db = SQLAlchemy()

# 用户角色关联表（多对多关系）
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

# 角色权限关联表（多对多关系）
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    """用户模型 - 扩展版"""
    __tablename__ = 'users'
    
    # 基础字段
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 新增状态字段
    status = db.Column(db.String(20), default='active', nullable=False)  # active, disabled, locked
    is_active = db.Column(db.Boolean, default=True)
    
    # 安全相关字段
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_expires_at = db.Column(db.DateTime, nullable=True)
    
    # 时间戳字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)  # 支持IPv6
    
    # 个人信息字段
    real_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    
    # 关联关系
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    created_tasks = db.relationship('Task', foreign_keys='Task.creator_id', 
                                  backref='creator', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id',
                                   backref='assignee', lazy='dynamic')
    operation_logs = db.relationship('OperationLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password_changed_at = datetime.utcnow()
        # 设置密码过期时间（90天后）
        self.password_expires_at = datetime.utcnow() + timedelta(days=90)
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_password_expired(self):
        """检查密码是否过期"""
        if not self.password_expires_at:
            return False
        return datetime.utcnow() > self.password_expires_at
    
    def is_locked(self):
        """检查账户是否被锁定"""
        if self.status == 'locked':
            return True
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    def lock_account(self, minutes=30):
        """锁定账户"""
        self.status = 'locked'
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
    
    def unlock_account(self):
        """解锁账户"""
        self.status = 'active'
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def has_permission(self, permission_code):
        """检查用户是否拥有特定权限"""
        for role in self.roles:
            if role.has_permission(permission_code):
                return True
        return False
    
    def has_any_permission(self, permission_codes):
        """检查用户是否拥有任意一个权限"""
        return any(self.has_permission(code) for code in permission_codes)
    
    def has_role(self, role_code):
        """检查用户是否拥有特定角色"""
        return any(role.code == role_code for role in self.roles)
    
    def get_all_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            permissions.update(role.get_permissions())
        return list(permissions)
    
    def get_role_names(self):
        """获取用户所有角色名称"""
        return [role.name for role in self.roles]
    
    def add_role(self, role):
        """添加角色"""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """移除角色"""
        if role in self.roles:
            self.roles.remove(role)
    
    def update_last_login(self, ip_address=None):
        """更新最后登录信息"""
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
        self.failed_login_attempts = 0
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'roles': [role.to_dict() for role in self.roles],
            'permissions': self.get_all_permissions()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    is_system = db.Column(db.Boolean, default=False)  # 是否为系统内置角色
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
                                backref=db.backref('roles', lazy=True))
    
    def has_permission(self, permission_code):
        """检查角色是否拥有特定权限"""
        return any(p.code == permission_code for p in self.permissions)
    
    def get_permissions(self):
        """获取角色的所有权限代码"""
        return [p.code for p in self.permissions]
    
    def get_permission_names(self):
        """获取角色的所有权限名称"""
        return [p.name for p in self.permissions]
    
    def add_permission(self, permission):
        """添加权限"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """移除权限"""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def set_permissions(self, permission_list):
        """设置权限列表"""
        self.permissions = permission_list
    
    def get_user_count(self):
        """获取拥有该角色的用户数量"""
        return len(self.users)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'permissions': [p.to_dict() for p in self.permissions],
            'user_count': self.get_user_count()
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    module = db.Column(db.String(50), nullable=False, index=True)  # 权限所属模块
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_role_count(self):
        """获取拥有该权限的角色数量"""
        return len(self.roles)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'module': self.module,
            'is_active': self.is_active,
            'role_count': self.get_role_count()
        }
    
    def __repr__(self):
        return f'<Permission {self.name}>'


class Task(db.Model):
    """任务模型"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 任务属性
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, in_progress, completed, overdue, cancelled
    priority = db.Column(db.String(10), default='medium', nullable=False)  # high, medium, low
    task_type = db.Column(db.String(50), default='other', nullable=False)
    progress = db.Column(db.Integer, default=0)  # 进度百分比 0-100
    
    # 时间相关
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # 附加信息
    tags = db.Column(db.Text, nullable=True)  # JSON格式存储标签
    attachments = db.Column(db.Text, nullable=True)  # JSON格式存储附件信息
    
    def is_overdue(self):
        """检查任务是否逾期"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    def complete_task(self):
        """完成任务"""
        self.status = 'completed'
        self.progress = 100
        self.completed_at = datetime.utcnow()
    
    def get_status_color(self):
        """获取状态对应的颜色"""
        status_colors = {
            'pending': 'secondary',
            'in_progress': 'warning', 
            'completed': 'success',
            'overdue': 'danger',
            'cancelled': 'dark'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_priority_color(self):
        """获取优先级对应的颜色"""
        priority_colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info'
        }
        return priority_colors.get(self.priority, 'info')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'task_type': self.task_type,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator': self.creator.username if self.creator else None,
            'assignee': self.assignee.username if self.assignee else None,
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'


class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 操作信息
    operation_type = db.Column(db.String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT等
    operation_desc = db.Column(db.String(500), nullable=False)
    module = db.Column(db.String(50), nullable=False, index=True)  # 操作模块
    target_type = db.Column(db.String(50), nullable=True)  # 操作目标类型
    target_id = db.Column(db.String(50), nullable=True)  # 操作目标ID
    
    # 日志级别和状态
    level = db.Column(db.String(20), default='info', nullable=False)  # debug, info, warning, error, critical
    status = db.Column(db.String(20), default='success', nullable=False)  # success, failed
    
    # 请求信息
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    request_url = db.Column(db.String(500), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    
    # 附加数据
    old_values = db.Column(db.Text, nullable=True)  # JSON格式，操作前的值
    new_values = db.Column(db.Text, nullable=True)  # JSON格式，操作后的值
    error_message = db.Column(db.Text, nullable=True)  # 错误信息
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    @classmethod
    def log_operation(cls, user_id=None, operation_type='', operation_desc='', 
                     module='', target_type=None, target_id=None, level='info',
                     status='success', ip_address=None, old_values=None, 
                     new_values=None, error_message=None):
        """记录操作日志"""
        import json
        
        log = cls(
            user_id=user_id,
            operation_type=operation_type,
            operation_desc=operation_desc,
            module=module,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            level=level,
            status=status,
            ip_address=ip_address,
            old_values=json.dumps(old_values, ensure_ascii=False) if old_values else None,
            new_values=json.dumps(new_values, ensure_ascii=False) if new_values else None,
            error_message=error_message
        )
        
        try:
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"记录操作日志失败: {e}")
    
    def get_level_color(self):
        """获取日志级别对应的颜色"""
        level_colors = {
            'debug': 'secondary',
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'critical': 'dark'
        }
        return level_colors.get(self.level, 'info')
    
    def to_dict(self):
        """转换为字典格式"""
        import json
        
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'operation_desc': self.operation_desc,
            'module': self.module,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'level': self.level,
            'status': self.status,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.username if self.user else 'System',
            'old_values': json.loads(self.old_values) if self.old_values else None,
            'new_values': json.loads(self.new_values) if self.new_values else None,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<OperationLog {self.operation_type}-{self.module}>'


def init_default_data():
    """初始化默认数据（简化版，主要用于app.py中调用）"""
    # 检查是否已经有权限数据
    if Permission.query.count() > 0:
        return
    
    # 创建基础权限
    basic_permissions = [
        {'name': '数据管理', 'code': 'data_management', 'description': '数据的增删改查权限', 'module': 'data'},
        {'name': '用户管理', 'code': 'user_management', 'description': '用户账户管理权限', 'module': 'user'},
        {'name': '报表查看', 'code': 'construction_management', 'description': '查看报表权限', 'module': 'report'},
    ]
    
    for perm_data in basic_permissions:
        permission = Permission(**perm_data)
        db.session.add(permission)
    
    # 创建管理员角色
    admin_role = Role(
        name='管理员',
        code='admin',
        description='系统管理员',
        is_system=True
    )
    
    # 为管理员角色分配所有权限
    admin_role.permissions = Permission.query.all()
    db.session.add(admin_role)
    
    try:
        db.session.commit()
        print("基础数据初始化完成")
    except Exception as e:
        db.session.rollback()
        print(f"基础数据初始化失败: {e}")