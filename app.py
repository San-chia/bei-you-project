# app.py
from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_session import Session
import os
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 导入模块
from models import db, User
from auth import auth_bp
from dash_app import create_dash_app

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    
    # 初始化扩展
    db.init_app(app)
    Session(app)
    
    # 配置登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录访问该页面'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    
    # 主页路由
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    # 仪表盘路由（需要登录）
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return redirect('/dashboard/')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("默认管理员账户已创建: admin/admin123")
    
    # 创建并集成Dash应用
    dash_app = create_dash_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()

    app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=8050)