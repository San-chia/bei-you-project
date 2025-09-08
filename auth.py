from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
import re

# 导入验证码工具
from captcha_utils import captcha_generator

auth_bp = Blueprint('auth', __name__)

try:
    from models import OperationLog
except ImportError:
    OperationLog = None

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    return True, ""

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         username = request.form.get('username', '').strip()
#         password = request.form.get('password', '')
        
#         # 获取客户端IP地址
#         client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
#         user_agent = request.headers.get('User-Agent', '')
        
#         if not username or not password:
#             # 记录登录失败日志
#             if OperationLog:
#                 OperationLog.log_operation(
#                     user_id=None,
#                     operation_type='LOGIN_FAILED',
#                     operation_desc='登录失败：用户名或密码为空',
#                     module='auth',
#                     level='warning',
#                     status='failed',
#                     ip_address=client_ip,
#                     error_message='用户名或密码为空'
#                 )
            
#             flash('请输入用户名和密码', 'error')
#             return render_template('login.html')
        
#         # 查找用户
#         user = User.query.filter_by(username=username).first()
        
#         if user and user.check_password(password):
#             # 检查用户是否被锁定
#             if user.is_locked():
#                 # 记录登录失败日志
#                 if OperationLog:
#                     OperationLog.log_operation(
#                         user_id=user.id,
#                         operation_type='LOGIN_FAILED',
#                         operation_desc=f'登录失败：账户被锁定 - {username}',
#                         module='auth',
#                         level='warning',
#                         status='failed',
#                         ip_address=client_ip,
#                         error_message='账户被锁定'
#                     )
#                 flash('账户已被锁定，请联系管理员', 'error')
#                 return render_template('login.html')
            
#             # 检查密码是否过期
#             if user.is_password_expired():
#                 # 记录密码过期日志
#                 if OperationLog:
#                     OperationLog.log_operation(
#                         user_id=user.id,
#                         operation_type='LOGIN_FAILED',
#                         operation_desc=f'登录失败：密码已过期 - {username}',
#                         module='auth',
#                         level='warning',
#                         status='failed',
#                         ip_address=client_ip,
#                         error_message='密码已过期'
#                     )
#                 flash('密码已过期，请联系管理员重置密码', 'error')
#                 return render_template('login.html')
            
#             # 登录成功
#             login_user(user)
            
#             # 更新用户最后登录信息
#             user.update_last_login(client_ip)
#             db.session.commit()
            
#             # 记录登录成功日志
#             if OperationLog:
#                 OperationLog.log_operation(
#                     user_id=user.id,
#                     operation_type='LOGIN',
#                     operation_desc=f'用户登录成功 - {username}',
#                     module='auth',
#                     level='info',
#                     status='success',
#                     ip_address=client_ip
#                 )
            
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('dashboard'))
#         else:
#             # 登录失败 - 记录失败次数
#             if user:
#                 user.failed_login_attempts += 1
#                 # 如果失败次数超过5次，锁定账户30分钟
#                 if user.failed_login_attempts >= 5:
#                     user.lock_account(30)
#                     db.session.commit()
                    
#                     # 记录账户锁定日志
#                     if OperationLog:
#                         OperationLog.log_operation(
#                             user_id=user.id,
#                             operation_type='ACCOUNT_LOCKED',
#                             operation_desc=f'账户因多次登录失败被锁定 - {username}',
#                             module='auth',
#                             level='warning',
#                             status='success',
#                             ip_address=client_ip,
#                             error_message=f'连续{user.failed_login_attempts}次登录失败'
#                         )
#                     flash('多次登录失败，账户已被锁定30分钟', 'error')
#                 else:
#                     db.session.commit()
            
#             # 记录登录失败日志
#             if OperationLog:
#                 OperationLog.log_operation(
#                     user_id=user.id if user else None,
#                     operation_type='LOGIN_FAILED',
#                     operation_desc=f'登录失败：用户名或密码错误 - {username}',
#                     module='auth',
#                     level='warning',
#                     status='failed',
#                     ip_address=client_ip,
#                     error_message='用户名或密码错误'
#                 )
            
#             flash('用户名或密码错误', 'error')
    
#     return render_template('login.html')

# 修改logout函数，添加日志记录
@auth_bp.route('/logout')
@login_required
def logout():
    # 获取当前用户信息用于日志记录
    current_username = current_user.username if current_user.is_authenticated else 'Unknown'
    current_user_id = current_user.id if current_user.is_authenticated else None
    
    # 获取客户端IP地址
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    
    # 记录退出日志
    if OperationLog:
        OperationLog.log_operation(
            user_id=current_user_id,
            operation_type='LOGOUT',
            operation_desc=f'用户退出登录 - {current_username}',
            module='auth',
            level='info',
            status='success',
            ip_address=client_ip
        )
    
    logout_user()
    flash('已成功退出登录', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 验证输入
        if not all([username, email, password, confirm_password]):
            flash('请填写所有字段', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('邮箱格式不正确', 'error')
            return render_template('register.html')
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        # 检查邮箱是否存在
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'error')
    
    return render_template('register.html')


# 新增：验证码生成路由
@auth_bp.route('/captcha')
def generate_captcha():
    """生成验证码"""
    text, image_data = captcha_generator.generate_captcha()
    # 将验证码文本存储在session中
    session['captcha'] = text.upper()  # 统一转为大写
    session['captcha_generated'] = True
    
    return jsonify({
        'image': image_data,
        'success': True
    })

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        captcha_input = request.form.get('captcha', '').strip().upper()  # 转为大写
        
        # 获取客户端IP地址
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        user_agent = request.headers.get('User-Agent', '')
        
        # 验证输入完整性
        if not all([username, password, captcha_input]):
            # 记录登录失败日志
            if OperationLog:
                OperationLog.log_operation(
                    user_id=None,
                    operation_type='LOGIN_FAILED',
                    operation_desc='登录失败：输入信息不完整',
                    module='auth',
                    level='warning',
                    status='failed',
                    ip_address=client_ip,
                    error_message='用户名、密码或验证码为空'
                )
            
            flash('请填写完整的登录信息', 'error')
            return render_template('login.html')
        
        # 验证码校验
        session_captcha = session.get('captcha', '')
        if not session_captcha or captcha_input != session_captcha:
            # 清除验证码（防止重复使用）
            session.pop('captcha', None)
            session.pop('captcha_generated', None)
            
            # 记录验证码验证失败日志
            if OperationLog:
                OperationLog.log_operation(
                    user_id=None,
                    operation_type='CAPTCHA_FAILED',
                    operation_desc=f'验证码验证失败 - {username}',
                    module='auth',
                    level='warning',
                    status='failed',
                    ip_address=client_ip,
                    error_message='验证码错误'
                )
            
            flash('验证码错误，请重新输入', 'error')
            return render_template('login.html')
        
        # 清除已使用的验证码
        session.pop('captcha', None)
        session.pop('captcha_generated', None)
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # 检查用户是否被锁定
            if user.is_locked():
                # 记录登录失败日志
                if OperationLog:
                    OperationLog.log_operation(
                        user_id=user.id,
                        operation_type='LOGIN_FAILED',
                        operation_desc=f'登录失败：账户被锁定 - {username}',
                        module='auth',
                        level='warning',
                        status='failed',
                        ip_address=client_ip,
                        error_message='账户被锁定'
                    )
                flash('账户已被锁定，请联系管理员', 'error')
                return render_template('login.html')
            
            # 检查密码是否过期
            if user.is_password_expired():
                # 记录密码过期日志
                if OperationLog:
                    OperationLog.log_operation(
                        user_id=user.id,
                        operation_type='LOGIN_FAILED',
                        operation_desc=f'登录失败：密码已过期 - {username}',
                        module='auth',
                        level='warning',
                        status='failed',
                        ip_address=client_ip,
                        error_message='密码已过期'
                    )
                flash('密码已过期，请联系管理员重置密码', 'error')
                return render_template('login.html')
            
            # 登录成功
            login_user(user)
            
            # 更新用户最后登录信息
            user.update_last_login(client_ip)
            db.session.commit()
            
            # 记录登录成功日志
            if OperationLog:
                OperationLog.log_operation(
                    user_id=user.id,
                    operation_type='LOGIN',
                    operation_desc=f'用户登录成功 - {username}',
                    module='auth',
                    level='info',
                    status='success',
                    ip_address=client_ip
                )
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            # 登录失败 - 记录失败次数
            if user:
                user.failed_login_attempts += 1
                # 如果失败次数超过5次，锁定账户30分钟
                if user.failed_login_attempts >= 5:
                    user.lock_account(30)
                    db.session.commit()
                    
                    # 记录账户锁定日志
                    if OperationLog:
                        OperationLog.log_operation(
                            user_id=user.id,
                            operation_type='ACCOUNT_LOCKED',
                            operation_desc=f'账户因多次登录失败被锁定 - {username}',
                            module='auth',
                            level='warning',
                            status='success',
                            ip_address=client_ip,
                            error_message=f'连续{user.failed_login_attempts}次登录失败'
                        )
                    flash('多次登录失败，账户已被锁定30分钟', 'error')
                else:
                    db.session.commit()
            
            # 记录登录失败日志
            if OperationLog:
                OperationLog.log_operation(
                    user_id=user.id if user else None,
                    operation_type='LOGIN_FAILED',
                    operation_desc=f'登录失败：用户名或密码错误 - {username}',
                    module='auth',
                    level='warning',
                    status='failed',
                    ip_address=client_ip,
                    error_message='用户名或密码错误'
                )
            
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


