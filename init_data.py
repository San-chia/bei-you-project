# init_default_data.py
"""
数据库默认数据初始化脚本
运行此脚本来初始化默认的角色和权限数据
"""

from app import create_app
from models import db, User, Role, Permission

def init_default_data():
    """初始化默认数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建默认权限
            default_permissions = [
                {'name': '指标与算法管理', 'code': 'data_management', 'description': '数据的增删改查权限', 'module': 'data'},

                # {'name': '用户管理', 'code': 'user_management', 'description': '用户账户管理权限', 'module': 'user'},
                {'name': '系统管理', 'code': 'system_config', 'description': '系统参数配置权限', 'module': 'system'},
                {'name': '报表生成', 'code': 'report_generation', 'description': '生成和编辑报表权限', 'module': 'report'},
                {'name': '施工数据', 'code': 'construction_management', 'description': '查看施工数据权限', 'module': 'report2'},
                # {'name': '日志查看', 'code': 'log_view', 'description': '查看系统日志权限', 'module': 'log'},
                # {'name': '权限设置', 'code': 'permission_setting', 'description': '设置用户权限', 'module': 'permission'},
                # {'name': '审计报告', 'code': 'audit_report', 'description': '生成审计报告', 'module': 'audit'},
                # {'name': '数据审核', 'code': 'data_audit', 'description': '数据审核权限', 'module': 'audit'},

                {'name': '指标测算', 'code': 'indicator_calculation', 'description': '指标测算功能权限', 'module': 'indicator'},
                {'name': '价格预测', 'code': 'price_prediction', 'description': '价格预测功能权限', 'module': 'prediction'},
                {'name': '模块化施工', 'code': 'modular_construction', 'description': '模块化施工功能权限', 'module': 'construction'},
                {'name': '平台对接', 'code': 'platform_integration', 'description': '一体化平台对接权限', 'module': 'integration'}
            ]
            
            print("正在创建默认权限...")
            for perm_data in default_permissions:
                if not Permission.query.filter_by(code=perm_data['code']).first():
                    permission = Permission(**perm_data)
                    db.session.add(permission)
                    print(f"  创建权限: {perm_data['name']}")
                else:
                    print(f"  权限已存在: {perm_data['name']}")
            
            # 提交权限
            db.session.commit()
            print("权限创建完成！")
            
            # 创建默认角色
            default_roles = [
                {
                    'name': '管理员',
                    'code': 'super_admin',
                    'description': '系统最高权限管理员，拥有所有权限',
                    'is_system': True,
                    'permissions': [perm['code'] for perm in default_permissions]  # 所有权限
                },
                # {
                #     'name': '系统管理员',
                #     'code': 'admin',
                #     'description': '系统管理员，拥有大部分管理权限',
                #     'is_system': True,
                #     'permissions': ['data_management', 'user_management', 'system_config', 
                #                   'report_generation', 'log_view', 'permission_setting',
                #                   'indicator_calculation', 'price_prediction', 'modular_construction']
                # },
                # {
                #     'name': '业务操作员',
                #     'code': 'operator',
                #     'description': '业务操作和管理人员',
                #     'is_system': True,
                #     'permissions': ['data_management', 'report_generation', 'construction_management', 'log_view',
                #                   'indicator_calculation', 'price_prediction', 'modular_construction']
                # },
                {
                    'name': '业务查看者',
                    'code': 'viewer',
                    'description': '不可以看到软件管理界面',
                    'is_system': True,
                    'permissions': ['report_generation','data_management','construction_management', 'indicator_calculation','price_prediction','modular_construction','platform_integration']
                },
                # {
                #     'name': '审计员',
                #     'code': 'auditor',
                #     'description': '审计和监督人员',
                #     'is_system': True,
                #     'permissions': ['log_view', 'audit_report', 'data_audit', 'construction_management']
                # },
                {
                    'name': '普通用户',
                    'code': 'tech_support',
                    'description': '只能看到前四个部分',
                    'is_system': True,
                    'permissions': ['construction_management', 'indicator_calculation','price_prediction','modular_construction']
                }
            ]
            
            print("正在创建默认角色...")
            for role_data in default_roles:
                if not Role.query.filter_by(code=role_data['code']).first():
                    permission_codes = role_data.pop('permissions')
                    role = Role(**role_data)
                    
                    # 添加权限
                    for perm_code in permission_codes:
                        permission = Permission.query.filter_by(code=perm_code).first()
                        if permission:
                            role.permissions.append(permission)
                    
                    db.session.add(role)
                    print(f"  创建角色: {role.name} (权限数量: {len(role.permissions)})")
                else:
                    print(f"  角色已存在: {role_data['name']}")
            
            # 提交角色
            db.session.commit()
            print("角色创建完成！")
            
            # 为默认管理员用户分配超级管理员角色
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                super_admin_role = Role.query.filter_by(code='super_admin').first()
                if super_admin_role and super_admin_role not in admin_user.roles:
                    admin_user.roles.append(super_admin_role)
                    db.session.commit()
                    print("已为默认管理员用户分配超级管理员角色")
                else:
                    print("默认管理员用户已有相应角色")
            else:
                print("未找到默认管理员用户")
            
            print("\n=== 数据初始化完成 ===")
            print("默认用户账户: admin / admin123")
            print("默认角色:")
            
            roles = Role.query.all()
            for role in roles:
                print(f"  - {role.name}: {role.description}")
                print(f"    权限: {', '.join([p.name for p in role.permissions])}")
            
        except Exception as e:
            db.session.rollback()
            print(f"数据初始化失败: {e}")
            raise

if __name__ == '__main__':
    print("开始初始化默认数据...")
    init_default_data()
    print("初始化完成！")