# modules/pricePrediction/data.py

import pandas as pd
import numpy as np
import mysql.connector  # 替换sqlite3
from sklearn.linear_model import RidgeCV, LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
import logging
import json

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

from .translation import (
    translate_table_name,
    translate_field_name,
    reverse_translate_table_name,
    PRICE_PREDICTION_TABLE_TRANSLATIONS
)

MYSQL_CONFIG = {
    'host': 'localhost',  # 修改为您的MySQL服务器地址
    'user': 'dash',  # 修改为您的MySQL用户名
    'password': '123456',  # 修改为您的MySQL密码
    'database': 'dash_project',  # 修改为您的MySQL数据库名
    'charset': 'utf8mb4',
    'autocommit': True  # 默认启用自动提交
}


# 算法名称映射配置
ALGORITHM_NAME_MAPPING = {
    # 数据库中的algorithm_name -> 代码中使用的模型标识
    "线性回归": "岭回归 (RidgeCV)",
    "神经网络": "神经网络 (MLPRegressor)",
    "决策树": "决策树 (Decision Tree)",
    "随机森林": "随机森林 (Random Forest)",
    "支持向量机": "支持向量回归 (SVR)"
}

# 反向映射：代码标识 -> 数据库名称
REVERSE_ALGORITHM_MAPPING = {v: k for k, v in ALGORITHM_NAME_MAPPING.items()}

def get_db_algorithm_name(model_key):
    """根据代码中的模型标识获取数据库中的算法名称"""
    # 直接映射
    db_name = REVERSE_ALGORITHM_MAPPING.get(model_key)
    if db_name:
        return db_name
    
    # 尝试模糊匹配
    model_key_lower = model_key.lower()
    if "ridge" in model_key_lower or "线性" in model_key:
        return "线性回归"
    elif "mlp" in model_key_lower or "neural" in model_key_lower or "神经" in model_key:
        return "神经网络"
    elif "decision" in model_key_lower or "tree" in model_key_lower or "决策" in model_key:
        return "决策树"
    elif "forest" in model_key_lower or "random" in model_key_lower or "随机" in model_key:
        return "随机森林"
    elif "svr" in model_key_lower or "svm" in model_key_lower or "支持" in model_key:
        return "支持向量机"
    
    return None

def get_model_key_from_db_name(db_name):
    """
    根据数据库算法名称获取代码中的模型标识
    """
    return ALGORITHM_NAME_MAPPING.get(db_name)


def get_connection():
    """获取MySQL数据库连接"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        raise

# 导入配置
from .config import (
    STEEL_CAGE_COL_MAPPING, STEEL_CAGE_ML_FEATURES,
    STEEL_LINING_COL_MAPPING, STEEL_LINING_ML_FEATURES
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CostPredictionSystem:
    """钢筋笼/钢衬里施工成本预测系统"""

    def __init__(self, mode='steel_cage'):
        """
        初始化预测系统

        Parameters:
        - mode: 'steel_cage' (钢筋笼模式) 或 'steel_lining' (钢衬里模式)
        """
        self.mode = mode
        self.df_historical = None
        self.kmeans = None
        self.scaler_cluster = None
        self.cluster_rules = {}
        self.global_rules = {}
        self.use_clustering = True
        self.n_clusters = 2

        # 机器学习模型
        self.models = {}
        self.is_trained = False
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{self.mode}")

        # 根据模式选择数据库表和特征列
        if self.mode == 'steel_cage':
            # 钢筋笼模式使用MySQL表
            self.key_factors_table = 'key_factors_1'
            self.price_table = 'price_baseline_1'
            self.col_mapping = STEEL_CAGE_COL_MAPPING
            self.ml_features = STEEL_CAGE_ML_FEATURES
            self.target_column = '项目总价'
            self.core_quantity_key = '钢筋总吨数'
            self.cluster_features_for_matching = ['钢筋总吨数', '套筒数量']
            self.ratio_method_factor_col = '五大因素实际成本占总成本的比例'

            self.ml_feature_to_qty_map = {
                '成本_塔吊租赁': '塔吊租赁工程量',
                '成本_钢筋生产线': '钢筋总吨数',
                '成本_吊索具': '吊索具数量',
                '成本_套筒': '套筒数量',
            }

        elif self.mode == 'steel_lining':
            # 钢衬里模式使用MySQL表
            self.key_factors_table = 'key_factors_2'
            self.price_table = 'price_baseline_2'
            self.col_mapping = STEEL_LINING_COL_MAPPING
            self.ml_features = STEEL_LINING_ML_FEATURES
            self.target_column = '项目总价'
            self.core_quantity_key = '拼装场地总工程量'
            self.cluster_features_for_matching = ['拼装场地总工程量', '制作胎具总工程量']
            self.ratio_method_factor_col = '六大因素实际成本占总成本的比例'

            self.ml_feature_to_qty_map = {
                '拼装场地费用': '拼装场地总工程量',
                '制作胎具费用': '制作胎具总工程量',
                '钢支墩、埋件费用': '钢支墩埋件总工程量',
                '扶壁柱费用': '扶壁柱总工程量',
                '走道板及操作平台费用': '走道板操作平台总工程量',
                '钢网架费用': '钢网梁总工程量',
            }
        else:
            raise ValueError(f"Unsupported mode: {mode}")
       
        # 新增：算法状态相关属性
        self.enabled_algorithms = {}  # 存储启用的算法信息
        self.algorithm_configs = {}   # 存储算法配置信息
        self.algorithm_status_loaded = False
        # 初始化综合指标状态相关属性
        self.comprehensive_indicators_status = {}
        self.prediction_method_availability = {}
        # 新增：算法参数缓存
        self.algorithm_parameters_cache = {}
        self.parameters_loaded = False


    def load_algorithm_parameters_from_db(self):
        """
        从algorithm_parameters表加载所有算法参数
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 查询所有算法参数
            query = """
            SELECT 
                algorithm_name,
                parameter_name,
                current_value,
                parameter_type
            FROM algorithm_parameters 
            ORDER BY algorithm_name, parameter_name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 按算法名称组织参数
            self.algorithm_parameters_cache = {}
            
            for row in results:
                algorithm_name = row['algorithm_name']
                
                if algorithm_name not in self.algorithm_parameters_cache:
                    self.algorithm_parameters_cache[algorithm_name] = {}
                
                # 暂时只存储原始值，不做复杂解析
                self.algorithm_parameters_cache[algorithm_name][row['parameter_name']] = {
                    'value': row['current_value'],
                    'type': row['parameter_type']
                }
            
            self.parameters_loaded = True
            self.logger.info(f"成功加载 {len(self.algorithm_parameters_cache)} 个算法的参数配置")
            
            # 打印加载的参数信息用于调试
            for alg_name, params in self.algorithm_parameters_cache.items():
                param_count = len(params)
                self.logger.info(f"  - {alg_name}: {param_count} 个参数")
                
            return True
            
        except mysql.connector.Error as e:
            self.logger.error(f"从数据库加载算法参数失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"加载算法参数时发生错误: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_algorithm_parameters_raw(self, algorithm_name):
        """
        获取指定算法的原始参数数据（不做解析）
        
        Args:
            algorithm_name (str): 算法名称（中文）
            
        Returns:
            dict: 原始参数数据
        """
        # 如果参数还未加载，先加载
        if not self.parameters_loaded:
            self.load_algorithm_parameters_from_db()
        
        # 从缓存中获取参数
        if algorithm_name in self.algorithm_parameters_cache:
            return self.algorithm_parameters_cache[algorithm_name]
        else:
            self.logger.warning(f"数据库中未找到算法 '{algorithm_name}' 的参数配置")
            return {}

    def test_parameter_loading(self):
        """
        测试参数加载功能的简单方法
        """
        print("🔧 测试参数加载...")
        
        success = self.load_algorithm_parameters_from_db()
        print(f"加载结果: {'✅ 成功' if success else '❌ 失败'}")
        
        if success:
            print(f"📊 加载了 {len(self.algorithm_parameters_cache)} 个算法的参数")
            
            # 显示每个算法的参数
            for alg_name, params in self.algorithm_parameters_cache.items():
                print(f"\n🔹 {alg_name}:")
                for param_name, param_info in params.items():
                    print(f"  - {param_name}: {param_info['value']} ({param_info['type']})")
        
        return success

    def _parse_parameter_value(self, value_str, param_type):
        """
        根据参数类型解析参数值
        
        Args:
            value_str (str): 数据库中存储的参数值字符串
            param_type (str): 参数类型 ('continuous', 'discrete', 'categorical')
            
        Returns:
            解析后的参数值
        """
        if value_str is None or value_str == 'None':
            return None
            
        try:
            if param_type == 'categorical':
                # 分类参数，直接返回字符串
                return str(value_str)
                
            elif param_type == 'discrete':
                # 离散参数，转换为整数
                if value_str == 'None (自动)':
                    return None
                return int(float(value_str))
                
            elif param_type == 'continuous':
                # 连续参数，处理特殊格式
                if 'np.logspace' in value_str:
                    # 解析 np.logspace(-6, 6, 13) 格式
                    import re
                    import numpy as np
                    match = re.search(r'np\.logspace\(([^)]+)\)', value_str)
                    if match:
                        params = [float(x.strip()) for x in match.group(1).split(',')]
                        return np.logspace(params[0], params[1], int(params[2]))
                elif value_str.startswith('(') and value_str.endswith(')'):
                    # 解析元组格式 (3,) -> [3]
                    content = value_str[1:-1].strip()
                    if content.endswith(','):
                        content = content[:-1]
                    if ',' in content:
                        return [int(x.strip()) for x in content.split(',')]
                    else:
                        return [int(content)] if content else []
                else:
                    # 普通数值
                    return float(value_str)
                    
        except (ValueError, TypeError) as e:
            self.logger.warning(f"解析参数值失败 '{value_str}' (类型: {param_type}): {e}")
            return value_str  # 返回原始字符串
            
        return value_str

    def get_algorithm_parameters_parsed(self, algorithm_name):
        """
        获取指定算法的解析后参数配置
        
        Args:
            algorithm_name (str): 算法名称（中文）
            
        Returns:
            dict: 解析后的参数字典，键为参数名，值为解析后的参数值
        """
        # 获取原始参数数据
        raw_params = self.get_algorithm_parameters_raw(algorithm_name)
        
        if not raw_params:
            return {}
        
        # 解析参数值
        parsed_params = {}
        for param_name, param_info in raw_params.items():
            parsed_value = self._parse_parameter_value(
                param_info['value'], 
                param_info['type']
            )
            parsed_params[param_name] = parsed_value
            
            # 记录解析结果
            self.logger.debug(f"{algorithm_name}.{param_name}: '{param_info['value']}' -> {parsed_value}")
        
        return parsed_params

    def test_parameter_parsing(self):
        """
        测试参数解析功能
        """
        print("\n🔄 测试参数解析功能:")
        
        # 测试用例
        test_cases = [
            ("np.logspace(-6, 6, 13)", "continuous", "岭回归的alphas参数"),
            ("(3,)", "continuous", "神经网络的隐藏层结构"), 
            ("linear", "categorical", "SVR的核函数类型"),
            ("2", "discrete", "决策树的最大深度"),
            ("0.1", "continuous", "正则化参数"),
            ("None (自动)", "discrete", "自动设置参数"),
            ("10", "discrete", "随机森林的树数量")
        ]
        
        print("\n📋 参数解析测试结果:")
        for value_str, param_type, description in test_cases:
            try:
                parsed_value = self._parse_parameter_value(value_str, param_type)
                value_type = type(parsed_value).__name__
                print(f"  ✅ {description}:")
                print(f"     输入: '{value_str}' ({param_type})")
                print(f"     输出: {parsed_value} ({value_type})")
                
                # 特殊情况的额外信息
                if isinstance(parsed_value, np.ndarray):
                    print(f"     数组长度: {len(parsed_value)}, 范围: [{parsed_value[0]:.2e}, {parsed_value[-1]:.2e}]")
                elif isinstance(parsed_value, list):
                    print(f"     列表内容: {parsed_value}")
                    
            except Exception as e:
                print(f"  ❌ {description}: 解析失败 - {e}")
            print()
        
        # 测试实际算法参数解析
        print("🎯 测试实际算法参数解析:")
        
        if self.parameters_loaded:
            test_algorithms = ["岭回归", "决策树", "随机森林"]
            
            for alg_name in test_algorithms:
                if alg_name in self.algorithm_parameters_cache:
                    print(f"\n📊 {alg_name}:")
                    
                    # 获取原始参数
                    raw_params = self.get_algorithm_parameters_raw(alg_name)
                    print("  原始参数:")
                    for param_name, param_info in raw_params.items():
                        print(f"    {param_name}: '{param_info['value']}' ({param_info['type']})")
                    
                    # 获取解析后参数
                    parsed_params = self.get_algorithm_parameters_parsed(alg_name)
                    print("  解析后参数:")
                    for param_name, parsed_value in parsed_params.items():
                        print(f"    {param_name}: {parsed_value} ({type(parsed_value).__name__})")
                else:
                    print(f"⚠️ 未找到算法 '{alg_name}' 的参数")

    def compare_with_default_params(self):
        """
        比较数据库参数与默认参数的差异
        """
        print("\n🔍 数据库参数与默认参数对比:")
        
        # 定义默认参数（用于对比）
        default_params = {
            "岭回归": {
                "alphas": "np.logspace(-6, 6, 13)",
                "cv": "None"
            },
            "决策树": {
                "max_depth": 2,
                "min_samples_leaf": 2,
                "min_samples_split": 2
            },
            "随机森林": {
                "n_estimators": 10,
                "max_depth": 2,
                "max_features": "None"
            }
        }
        
        for alg_name, default_values in default_params.items():
            print(f"\n📊 {alg_name}:")
            
            # 获取数据库中的解析参数
            db_params = self.get_algorithm_parameters_parsed(alg_name)
            
            for param_name, default_value in default_values.items():
                db_value = db_params.get(param_name, "❌ 未找到")
                
                # 简单比较
                if str(db_value) == str(default_value):
                    status = "✅ 相同"
                else:
                    status = "🔄 不同"
                
                print(f"  {param_name}:")
                print(f"    默认值: {default_value}")
                print(f"    数据库: {db_value} {status}")

    def _create_models_with_db_params(self):
        """
        使用数据库参数配置创建模型
        
        Returns:
            dict: 配置好的模型字典
        """
        models_config = {}
        
        # 岭回归
        ridge_params = self.get_algorithm_parameters_parsed("岭回归")
        
        # 处理alphas参数
        alphas = ridge_params.get('alphas', np.logspace(-6, 6, 13))
        cv_folds = ridge_params.get('cv', None)
        
        models_config["岭回归 (RidgeCV)"] = Pipeline([
            ('scaler', StandardScaler()), 
            ('regressor', RidgeCV(alphas=alphas, cv=cv_folds))
        ])
        
        self.logger.info(f"岭回归参数 - alphas: {type(alphas).__name__}({len(alphas) if hasattr(alphas, '__len__') else 'scalar'}), cv: {cv_folds}")
        
        # 决策树
        tree_params = self.get_algorithm_parameters_parsed("决策树")
        
        models_config["决策树 (Decision Tree)"] = Pipeline([
            ('regressor', DecisionTreeRegressor(
                random_state=42,
                max_depth=tree_params.get('max_depth', 2),
                min_samples_leaf=tree_params.get('min_samples_leaf', 2),
                min_samples_split=tree_params.get('min_samples_split', 2)
            ))
        ])
        
        self.logger.info(f"决策树参数 - max_depth: {tree_params.get('max_depth', 2)}, min_samples_leaf: {tree_params.get('min_samples_leaf', 2)}")
        
        # 随机森林
        forest_params = self.get_algorithm_parameters_parsed("随机森林")
        
        # 处理max_features参数（可能是None）
        max_features = forest_params.get('max_features', None)
        if max_features == "None (全部特征)":
            max_features = None
        
        models_config["随机森林 (Random Forest)"] = Pipeline([
            ('regressor', RandomForestRegressor(
                random_state=42,
                n_estimators=forest_params.get('n_estimators', 10),
                max_depth=forest_params.get('max_depth', 2),
                max_features=max_features
            ))
        ])
        
        self.logger.info(f"随机森林参数 - n_estimators: {forest_params.get('n_estimators', 10)}, max_features: {max_features}")
        
        # 支持向量回归
        svr_params = self.get_algorithm_parameters_parsed("支持向量回归")
        
        models_config["支持向量回归 (SVR)"] = Pipeline([
            ('scaler', StandardScaler()), 
            ('regressor', SVR(
                C=svr_params.get('C', 0.1),
                kernel=svr_params.get('kernel', 'linear'),
                epsilon=svr_params.get('epsilon', 0.1)
            ))
        ])
        
        self.logger.info(f"SVR参数 - C: {svr_params.get('C', 0.1)}, kernel: {svr_params.get('kernel', 'linear')}")
        
        # 神经网络
        nn_params = self.get_algorithm_parameters_parsed("神经网络")
        
        # 处理hidden_layer_sizes参数
        hidden_layers = nn_params.get('hidden_layer_sizes', [3])
        
        # 确保hidden_layer_sizes是元组格式（sklearn要求）
        if isinstance(hidden_layers, list):
            hidden_layers = tuple(hidden_layers)
        elif isinstance(hidden_layers, int):
            hidden_layers = (hidden_layers,)
        elif not isinstance(hidden_layers, tuple):
            hidden_layers = (3,)  # 默认值
            
        models_config["神经网络 (MLPRegressor)"] = Pipeline([
            ('scaler', StandardScaler()), 
            ('regressor', MLPRegressor(
                hidden_layer_sizes=hidden_layers,
                activation='relu',
                solver='lbfgs',
                max_iter=nn_params.get('max_iter', 2000),
                random_state=42,
                alpha=nn_params.get('alpha', 0.1)
            ))
        ])
        
        self.logger.info(f"神经网络参数 - hidden_layers: {hidden_layers}, alpha: {nn_params.get('alpha', 0.1)}")
        
        self.logger.info(f"✅ 使用数据库参数配置创建了 {len(models_config)} 个模型")
        return models_config

    def load_algorithm_configs(self):
        """从数据库加载算法配置信息"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 查询当前模式下的算法配置
            query = """
            SELECT algorithm_name, status, parameters, model_description, application_scenario
            FROM algorithm_configs 
            WHERE construction_mode = %s OR construction_mode = 'general'
            ORDER BY algorithm_name
            """
            
            cursor.execute(query, (self.mode,))
            results = cursor.fetchall()
            
            self.algorithm_configs = {}
            self.enabled_algorithms = {}
            
            for row in results:
                algorithm_name = row['algorithm_name']
                self.algorithm_configs[algorithm_name] = {
                    'status': row['status'],
                    'parameters': row['parameters'],
                    'description': row['model_description'],
                    'scenario': row['application_scenario']
                }
                
                # 如果算法启用，加入启用列表
                if row['status'] == 'enabled':
                    self.enabled_algorithms[algorithm_name] = True
                    
            self.algorithm_status_loaded = True
            self.logger.info(f"成功加载 {len(self.algorithm_configs)} 个算法配置")
            self.logger.info(f"启用的算法: {list(self.enabled_algorithms.keys())}")
            
            return True
            
        except mysql.connector.Error as e:
            self.logger.error(f"加载算法配置失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"加载算法配置时发生错误: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_enabled_algorithm_names(self):
        """获取启用的算法名称列表"""
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
        return list(self.enabled_algorithms.keys())
    
    def is_algorithm_enabled(self, algorithm_name):
        """检查指定算法是否启用"""
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
        return self.enabled_algorithms.get(algorithm_name, False)
    
    def get_algorithm_config(self, algorithm_name):
        """获取指定算法的配置信息"""
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
        return self.algorithm_configs.get(algorithm_name, {})
    
    def validate_algorithm_availability(self):
        """验证算法可用性"""
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
            
        enabled_count = len(self.enabled_algorithms)
        
        if enabled_count == 0:
            return {
                'status': 'unavailable',
                'message': '所有预测算法都已停用，无法进行机器学习预测',
                'enabled_count': 0
            }
        elif enabled_count == 1:
            return {
                'status': 'limited',
                'message': f'仅有1个算法启用，预测可靠性较低。启用算法: {list(self.enabled_algorithms.keys())[0]}',
                'enabled_count': 1
            }
        else:
            return {
                'status': 'available', 
                'message': f'有{enabled_count}个算法可用，预测功能正常',
                'enabled_count': enabled_count
            }


    def get_algorithm_status_info(self):
        """获取算法状态信息用于显示"""
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
            
        status_info = {
            'enabled': [],
            'disabled': [],
            'total_count': 0,
            'enabled_count': 0
        }
        
        # 按照显示顺序整理算法状态
        display_order = [
            "岭回归 (RidgeCV)",
            "决策树 (Decision Tree)", 
            "随机森林 (Random Forest)",
            "支持向量回归 (SVR)",
            "神经网络 (MLPRegressor)"
        ]
        
        for model_key in display_order:
            db_algorithm_name = get_db_algorithm_name(model_key)
            if db_algorithm_name:
                config = self.get_algorithm_config(db_algorithm_name)
                if config:  # 只处理在数据库中存在的算法
                    status_info['total_count'] += 1
                    
                    algorithm_info = {
                        'display_name': model_key,
                        'db_name': db_algorithm_name,
                        'status': config.get('status', 'unknown'),
                        'description': config.get('description', ''),
                        'trained': model_key in self.models
                    }
                    
                    if config.get('status') == 'enabled':
                        status_info['enabled'].append(algorithm_info)
                        status_info['enabled_count'] += 1
                    else:
                        status_info['disabled'].append(algorithm_info)
        
        return status_info

    def find_best_algorithm_prediction(self, ml_predictions, ratio_prediction_value):
        """
        找到最佳算法预测 - 改进版本，只从启用的算法中选择
        保持原有的选择逻辑：最接近比率法的算法
        """
        if not ratio_prediction_value or not ml_predictions:
            return None, None
            
        best_algorithm_key = None
        min_diff_to_ratio = float('inf')
        
        # 只考虑启用且有有效预测结果的算法
        for model_key, prediction_value in ml_predictions.items():
            # 跳过特殊键和停用算法
            if (model_key in ['集成平均预测', '_algorithm_status'] or 
                prediction_value is None or 
                isinstance(prediction_value, dict)):  # 停用算法返回字典
                continue
                
            # 确保这是一个启用的算法且有数值预测结果
            if isinstance(prediction_value, (int, float)):
                diff = abs(prediction_value - ratio_prediction_value)
                if diff < min_diff_to_ratio:
                    min_diff_to_ratio = diff
                    best_algorithm_key = model_key
        
        if best_algorithm_key:
            best_prediction_value = ml_predictions[best_algorithm_key]
            self.logger.info(f"🏆 最佳算法: {best_algorithm_key}, 预测值: {best_prediction_value:.2f}")
            return best_algorithm_key, best_prediction_value
        else:
            self.logger.warning("未找到有效的最佳算法预测")
            return None, None
        
    def load_data_from_database(self, mode, table_name=None):
        """从MySQL数据库加载数据"""
        if table_name is None:
            if mode == 'steel_cage':
                table_name = "key_factors_1"
            elif mode == 'steel_lining':
                table_name = "key_factors_2"
        
        conn = None
        try:
            # 使用MySQL连接替换SQLite
            conn = get_connection()
            
            # 添加调试信息：查看表结构
            self.logger.info(f"正在加载表: {table_name}")
            
            # 检查表是否存在并查看结构
            try:
                structure_query = f"DESCRIBE `{table_name}`"
                df_structure = pd.read_sql_query(structure_query, conn)
                self.logger.info(f"表 {table_name} 的列结构:\n{df_structure[['Field', 'Type']].to_string()}")
            except Exception as e:
                self.logger.warning(f"无法获取表结构: {e}")
            
            query = f"SELECT * FROM `{table_name}`"
            df_raw = pd.read_sql_query(query, conn)
            
            query = f"SELECT * FROM `{table_name}`"
            df_raw = pd.read_sql_query(query, conn)
            
            # 添加这些调试信息
            print(f"\n=== 调试信息 for {mode} ===")
            print(f"查询的表名: {table_name}")
            print(f"原始数据形状: {df_raw.shape}")
            print(f"原始列名: {list(df_raw.columns)}")
            print(f"前几行数据:")
            print(df_raw.head())
            print(f"配置的列名映射: {self.col_mapping}")

            
            self.logger.info(f"从表 {table_name} 加载了 {len(df_raw)} 行数据")
            self.logger.info(f"原始列名: {list(df_raw.columns)}")
            
            if len(df_raw) > 0:
                self.logger.info(f"数据预览:\n{df_raw.head()}")
            else:
                self.logger.warning(f"表 {table_name} 中没有数据！")
            
            self.df_historical = self._preprocess_data(df_raw)
            self.logger.info(f"成功从MySQL数据库加载 {len(self.df_historical)} 条历史项目数据 for {self.mode}")
            return True

        except mysql.connector.Error as e:
            self.logger.error(f"MySQL数据库读取失败 for {self.mode}: {e}")
            self.df_historical = pd.DataFrame()
            return False
        except Exception as e:
            self.logger.error(f"数据库读取失败 for {self.mode}: {e}")
            self.df_historical = pd.DataFrame()
            return False
        finally:
            if conn:
                conn.close()


    def _preprocess_data(self, df_raw):
        df_processed = df_raw.copy()

        # 根据模式重命名列
        df_processed.rename(columns=self.col_mapping, inplace=True)

        # 定义所有可能的数值列
        all_numeric_cols = list(self.ml_features) + [self.target_column] + self.cluster_features_for_matching

        # 价格基准中的数值列
        potential_price_db_numeric_cols = [
            "modular_labor_unit_price", "modular_labor_quantity", "modular_labor_total",
            "modular_material_unit_price", "modular_material_quantity", "modular_material_total",
            "modular_machinery_unit_price", "modular_machinery_quantity", "modular_machinery_total",
            "total_price"
        ]
        all_numeric_cols.extend(potential_price_db_numeric_cols)
        all_numeric_cols = list(set(all_numeric_cols))

        self.logger.debug(f"尝试将以下列转换为数值类型 for {self.mode}: {all_numeric_cols}")

        # 确保所有必要的列存在且为数值类型
        for col in all_numeric_cols:
            if col in df_processed.columns:
                original_dtype = df_processed[col].dtype
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                if df_processed[col].dtype == object and original_dtype != object:
                    self.logger.warning(f"警告: 列 '{col}' 在 {self.mode} 中转换为数值失败，可能包含非数值字符。")
            else:
                if col in (list(self.ml_features) + [self.target_column] + self.cluster_features_for_matching):
                    self.logger.warning(f"警告：处理数据时，'{col}' 字段在原始数据中缺失 for {self.mode}。将填充为0。")
                    df_processed[col] = 0.0

        # 过滤掉项目总价为 NaN 或 0 的行
        df_processed.dropna(subset=[self.target_column], inplace=True)
        df_processed = df_processed[df_processed[self.target_column] > 0].copy()

        # 记录关键列的概况
        self.logger.info(f"预处理后 {self.mode} 模式 '{self.target_column}' 统计信息:\n{df_processed[self.target_column].describe()}")
        for feature in self.ml_features:
            if feature in df_processed.columns:
                self.logger.info(f"预处理后 {self.mode} 模式 '{feature}' 统计信息:\n{df_processed[feature].describe()}")
            else:
                self.logger.warning(f"ML特征 '{feature}' 在预处理后的DataFrame中缺失 for {self.mode}。")

        # 重新检查ML特征，确保它们都是数值型
        for col in self.ml_features:
            if col not in df_processed.columns:
                df_processed[col] = 0.0
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0.0)

        if self.mode == 'steel_lining':
            # 钢衬里模式特有的比例因子计算
            for feature in self.ml_features:
                if feature not in df_processed.columns:
                    df_processed[feature] = 0.0

            temp_core_costs_sum = df_processed[self.ml_features].sum(axis=1)
            print("!!!")
            print(df_processed)
            print("!!!")
            # 避免除零
            df_processed[self.ratio_method_factor_col] = temp_core_costs_sum / df_processed[self.target_column]
            df_processed[self.ratio_method_factor_col].replace([np.inf, -np.inf], np.nan, inplace=True)
            df_processed[self.ratio_method_factor_col].fillna(0.0, inplace=True)

        self.logger.info(f"数据预处理完成 for {self.mode}，剩余 {len(df_processed)} 条有效样本。")
        return df_processed

    def train_system(self):
        if self.df_historical is None or len(self.df_historical) == 0:
            self.logger.error(f"错误：没有历史数据，请先加载数据 for {self.mode}")
            return False

        try:
            # 【新增】步骤0：加载算法参数配置
            if not self.load_algorithm_parameters_from_db():
                self.logger.warning(f"算法参数加载失败，将使用默认参数 for {self.mode}")
            
            # 新增：加载综合指标状态
            self.load_comprehensive_indicators_status()
            
            # 步骤1：聚类分析
            self._perform_clustering()

            # 步骤2：建立规则库
            self._build_rules()

            # 步骤3：训练机器学习模型（现在会使用数据库参数）
            self._train_ml_models()

            self.is_trained = True
            self.logger.info(f"系统训练完成 for {self.mode}")
            return True

        except Exception as e:
            self.logger.error(f"训练过程出错 for {self.mode}: {e}", exc_info=True)
            self.is_trained = False
            return False

    # 新增：参数配置对比方法（用于验证）

    def log_parameter_comparison(self):
        """
        记录数据库参数与默认参数的对比（用于调试）
        """
        self.logger.info("=== 算法参数配置对比 ===")
        
        # 默认参数（原来硬编码的值）
        default_configs = {
            "岭回归": {"alphas": "np.logspace(-6, 6, 13)", "cv": None},
            "决策树": {"max_depth": 2, "min_samples_leaf": 2, "min_samples_split": 2},
            "随机森林": {"n_estimators": 10, "max_depth": 2, "max_features": None},
            "支持向量回归": {"C": 0.1, "kernel": "linear", "epsilon": 0.1},
            "神经网络": {"hidden_layer_sizes": (3,), "alpha": 0.1, "max_iter": 2000}
        }
        
        for alg_name, default_params in default_configs.items():
            db_params = self.get_algorithm_parameters_parsed(alg_name)
            
            self.logger.info(f"\n📊 {alg_name}:")
            self.logger.info(f"  默认配置: {default_params}")
            self.logger.info(f"  数据库配置: {db_params}")
            
            # 检查关键参数是否有变化
            for param_name, default_value in default_params.items():
                db_value = db_params.get(param_name, "未找到")
                if str(db_value) != str(default_value):
                    self.logger.info(f"  🔄 {param_name}: {default_value} → {db_value}")
                else:
                    self.logger.info(f"  ✅ {param_name}: 保持默认值 {default_value}")

    def _perform_clustering(self):
        # 聚类特征需要根据模式进行调整
        cluster_features = [f for f in self.cluster_features_for_matching if f in self.df_historical.columns]

        if not cluster_features or len(self.df_historical) < self.n_clusters * 2:
            self.logger.warning(f"警告：数据点过少或聚类特征缺失 ({len(self.df_historical)}), 无法有效聚类 for {self.mode}，将使用全局平均规则")
            self.use_clustering = False
            self.df_historical['cluster_label'] = 0
            return

        X_for_clustering = self.df_historical[cluster_features].copy()
        X_for_clustering.dropna(inplace=True)
        if X_for_clustering.empty:
            self.logger.warning(f"聚类数据为空 after dropping NaNs for {self.mode}. Using global rules.")
            self.use_clustering = False
            self.df_historical['cluster_label'] = 0
            return

        # 标准化聚类特征
        self.scaler_cluster = StandardScaler()
        X_scaled_for_clustering = self.scaler_cluster.fit_transform(X_for_clustering)

        # 执行KMeans聚类
        try:
            kmeans = KMeans(n_clusters=min(self.n_clusters, len(X_for_clustering)), random_state=42, n_init='auto')
            self.df_historical.loc[X_for_clustering.index, 'cluster_label'] = kmeans.fit_predict(X_scaled_for_clustering)
            self.kmeans = kmeans
            self.use_clustering = True
            cluster_counts = self.df_historical['cluster_label'].value_counts().to_dict()
            self.logger.info(f"聚类完成 for {self.mode}：将项目分为 {kmeans.n_clusters} 个簇: {cluster_counts}")
        except Exception as e:
            self.logger.error(f"执行KMeans聚类出错 for {self.mode}: {e}. 回退到全局规则。", exc_info=True)
            self.use_clustering = False
            self.df_historical['cluster_label'] = 0

    def _build_rules(self):
        if self.df_historical is None or self.df_historical.empty:
            self.logger.warning(f"没有历史数据用于构建规则 for {self.mode}")
            return

        # 计算全局平均规则（作为后备）
        self.global_rules = self._calculate_rules_for_df(self.df_historical)
        self.logger.debug(f"Global rules for {self.mode}: {json.dumps(self.global_rules, indent=2)}")

        # 如果使用聚类，为每个簇计算规则
        if self.use_clustering and 'cluster_label' in self.df_historical.columns:
            for cluster_id in self.df_historical['cluster_label'].unique():
                df_cluster = self.df_historical[self.df_historical['cluster_label'] == cluster_id]
                if len(df_cluster) > 0:
                    self.cluster_rules[cluster_id] = self._calculate_rules_for_df(df_cluster)
                    self.logger.debug(f"Cluster {cluster_id} rules for {self.mode}: {json.dumps(self.cluster_rules[cluster_id], indent=2)}")
                else:
                    self.cluster_rules[cluster_id] = self.global_rules.copy()
        else:
            self.cluster_rules[0] = self.global_rules.copy()

        self.logger.info(f"规则库建立完成 for {self.mode}")

    def _calculate_rules_for_df(self, df):
        rules = {}
        # 目标总价平均值
        rules['avg_target_cost'] = df[self.target_column].mean()

        # 比率法因子
        if self.ratio_method_factor_col in df.columns:
            valid_factor_data = df[self.ratio_method_factor_col].replace([np.inf, -np.inf], np.nan).dropna()
            rules[self.ratio_method_factor_col] = valid_factor_data.mean() if not valid_factor_data.empty else 0.0
        else:
            rules[self.ratio_method_factor_col] = 0.0

        # 为所有相关列添加平均数量
        all_relevant_quantity_columns = [
            '拼装场地总工程量', '制作胎具总工程量', '钢支墩埋件总工程量', '扶壁柱总工程量',
            '走道板操作平台总工程量', '钢网梁总工程量',
            '钢筋总吨数', '塔吊租赁工程量', '吊索具数量', '套筒数量',
            '钢支墩埋件混凝土剔凿总工程量', '钢支墩埋件混凝土回填总工程量',
            '钢支墩埋件安装总工程量', '钢支墩埋件制作总工程量',
            '扶壁柱安装总工程量', '扶壁柱拆除总工程量', '扶壁柱构件使用折旧总工程量',
            '走道板操作平台制作总工程量', '走道板操作平台搭设总工程量', '走道板操作平台拆除总工程量',
            '钢网架制作总工程量', '钢网架安装总工程量', '钢网架拆除总工程量',
        ]
        existing_relevant_quantity_columns = [col for col in all_relevant_quantity_columns if col in df.columns]

        for qty_col in existing_relevant_quantity_columns:
            rules[f'avg_qty_{qty_col}'] = df[qty_col].mean() if not df[qty_col].empty else 0.0
            self.logger.debug(f"学习到 '{qty_col}' 的平均数量: {rules[f'avg_qty_{qty_col}']:.2f}")

        self.logger.debug(f"计算 '{self.ratio_method_factor_col}' for {self.mode}。")
        if self.mode == 'steel_cage':
            core_costs_sum_temp = df['成本_塔吊租赁'] + df['成本_钢筋生产线'] + df['成本_吊索具'] + df['成本_套筒']
            self.logger.debug(f"核心成本临时求和统计 (steel_cage): {core_costs_sum_temp.describe()}")
            self.logger.debug(f"项目总价统计 (steel_cage): {df[self.target_column].describe()}")
            mask = (df[self.target_column] != 0) & (~np.isnan(df[self.target_column])) & (~np.isnan(core_costs_sum_temp))
            if mask.sum() > 0:
                calculated_ratio = (core_costs_sum_temp[mask] / df[self.target_column][mask]).mean()
                self.logger.debug(f"计算出的比率因子 (steel_cage): {calculated_ratio}")
                rules[self.ratio_method_factor_col] = calculated_ratio
            else:
                self.logger.warning(f"无法计算有效比率因子 (steel_cage)：分母为零或数据无效。")
                rules[self.ratio_method_factor_col] = 0.0
        elif self.mode == 'steel_lining':
            if self.ratio_method_factor_col in df.columns:
                self.logger.debug(f"钢衬里模式已在预处理中计算 '{self.ratio_method_factor_col}'。其统计信息:\n{df[self.ratio_method_factor_col].describe()}")
            else:
                self.logger.error(f"钢衬里模式 '{self.ratio_method_factor_col}' 列不存在！")

        # 工程量之间的比率
        if self.core_quantity_key in df.columns:
            quantities_to_learn_ratios = []
            if self.mode == 'steel_cage':
                quantities_to_learn_ratios.extend([
                    '塔吊租赁工程量', '吊索具数量', '套筒数量'
                ])
                for feature in self.cluster_features_for_matching:
                    if feature != self.core_quantity_key:
                        quantities_to_learn_ratios.append(feature)
            elif self.mode == 'steel_lining':
                quantities_to_learn_ratios.extend([
                    '制作胎具总工程量', '钢支墩埋件总工程量', '扶壁柱总工程量',
                    '走道板操作平台总工程量', '钢网梁总工程量',
                ])
                for feature in self.cluster_features_for_matching:
                    if feature != self.core_quantity_key:
                        quantities_to_learn_ratios.append(feature)

            quantities_to_learn_ratios = list(set([q for q in quantities_to_learn_ratios if q in df.columns and q != self.core_quantity_key]))
            
            for qty_col in quantities_to_learn_ratios:
                valid_df = df[(df[self.core_quantity_key] > 0) & (df[qty_col].notna())].copy()
                if not valid_df.empty:
                    rules[f'avg_qty_ratio_{qty_col}_per_{self.core_quantity_key}'] = \
                        (pd.to_numeric(valid_df[qty_col], errors='coerce') / \
                         pd.to_numeric(valid_df[self.core_quantity_key], errors='coerce')).mean()
                    self.logger.debug(f"学习到 '{qty_col}' 相对于 '{self.core_quantity_key}' 的平均比率: {rules[f'avg_qty_ratio_{qty_col}_per_{self.core_quantity_key}']:.2f}")
                else:
                    rules[f'avg_qty_ratio_{qty_col}_per_{self.core_quantity_key}'] = 0.0
                    self.logger.warning(f"无法学习 '{qty_col}' 相对于 '{self.core_quantity_key}' 的平均比率：核心量为零或数据无效。")

        # 每个ML特征的平均单位成本
        for ml_feature, qty_col in self.ml_feature_to_qty_map.items():
            if ml_feature in df.columns and qty_col in df.columns:
                valid_df = df[(df[ml_feature] > 0) & (df[qty_col] > 0)].copy()
                if not valid_df.empty:
                    unit_cost = (pd.to_numeric(valid_df[ml_feature], errors='coerce') / 
                                 pd.to_numeric(valid_df[qty_col], errors='coerce')).median()
                    rules[f'avg_unit_cost_{ml_feature}'] = unit_cost
                    self.logger.debug(f"学习到 '{ml_feature}' 的平均单位成本: {unit_cost:.2f} 元/{qty_col}")
                else:
                    rules[f'avg_unit_cost_{ml_feature}'] = 0.0
                    self.logger.warning(f"无法学习 '{ml_feature}' 的平均单位成本：费用或工程量为零/无效。")
            else:
                rules[f'avg_unit_cost_{ml_feature}'] = 0.0
                self.logger.warning(f"无法学习 '{ml_feature}' 的平均单位成本：费用列或工程量列缺失。")

        return rules

    def _get_corresponding_quantity_column(self, ml_feature):
        """根据ML特征找到对应的工程量列名"""
        mapping = {
            '成本_塔吊租赁': '塔吊租赁工程量',
            '成本_钢筋生产线': '钢筋总吨数',
            '成本_吊索具': '吊索具数量',
            '成本_套筒': '套筒数量',

            '拼装场地费用': '拼装场地总工程量',
            '制作胎具费用': '制作胎具总工程量',
            '钢支墩、埋件费用': '钢支墩埋件总工程量',
            '扶壁柱费用': '扶壁柱总工程量',
            '走道板及操作平台费用': '走道板操作平台总工程量',
            '钢网架费用': '钢网梁总工程量',
        }
        return mapping.get(ml_feature, None)

    def _train_ml_models(self):
        """
        改进的模型训练方法 - 使用数据库中的参数配置
        """
        
        # 【新增】算法可用性检查
        if not self.load_algorithm_configs():
            self.logger.error("算法配置加载失败，无法训练模型")
            self.models = {}
            return
            
        availability = self.validate_algorithm_availability()
        if availability['status'] == 'unavailable':
            self.logger.warning("所有算法都已停用，跳过模型训练")
            self.models = {}
            return
        
        # 【新增】加载数据库参数
        if not self.parameters_loaded:
            if not self.load_algorithm_parameters_from_db():
                self.logger.warning(f"无法加载算法参数，使用默认配置 for {self.mode}")
        
        # 准备训练数据
        X = self.df_historical[self.ml_features].copy()
        y = self.df_historical[self.target_column].copy()

        # 处理可能存在的无穷大值
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        y.replace([np.inf, -np.inf], np.nan, inplace=True)

        # 合并X和y，然后丢弃包含NaN的行
        combined_data = X.assign(target=y).dropna()
        if combined_data.empty:
            self.logger.warning(f"No valid data for ML model training after dropping NaNs for {self.mode}.")
            self.models = {}
            return

        X_cleaned = combined_data[self.ml_features]
        y_cleaned = combined_data['target']

        if X_cleaned.empty or len(X_cleaned) < 2:
            self.logger.warning(f"Not enough data to train ML models for {self.mode}. Skipping ML training.")
            self.models = {}
            return

        # 检查特征中是否有所有值都为0或NaN的列
        for col in X_cleaned.columns:
            if X_cleaned[col].nunique() == 1 and X_cleaned[col].iloc[0] == 0:
                self.logger.warning(f"Feature column '{col}' has only zero values. This might affect model training.")
            elif X_cleaned[col].isnull().all():
                self.logger.warning(f"Feature column '{col}' has all NaN values. Dropping this column for training.")
                X_cleaned = X_cleaned.drop(columns=[col])
        if X_cleaned.empty:
            self.logger.warning(f"All feature columns became empty after preprocessing for {self.mode}. Skipping ML training.")
            self.models = {}
            return

        # 【修改】使用数据库参数配置创建模型
        models_config = self._create_models_with_db_params()

        # 训练每个模型
        for model_name, pipeline in models_config.items():
            # 检查算法是否启用
            db_algorithm_name = get_db_algorithm_name(model_name)
            
            if db_algorithm_name and self.is_algorithm_enabled(db_algorithm_name):
                try:
                    pipeline.fit(X_cleaned, y_cleaned)
                    self.models[model_name] = pipeline
                    self.logger.info(f"  ✅ {model_name} 训练成功 (使用数据库参数配置)")
                except Exception as e:
                    self.logger.error(f"  ❌ {model_name} 训练失败: {e}")
            else:
                self.logger.info(f"  🚫 {model_name} 已停用，跳过训练")

        self.logger.info(f"机器学习模型训练完成 for {self.mode}，成功训练 {len(self.models)} 个模型")

    def predict(self, user_inputs, unit_prices_from_db):
        """
        预测项目总成本 - 完全独立并行的预测方法版本
        
        Parameters:
        - user_inputs: dict, 用户输入参数
        - unit_prices_from_db: dict, 从价格基准数据库加载的单位价格
        
        Returns:
        - dict: 预测结果（四种方法完全独立）
        """
        if not self.is_trained:
            return {"error": f"系统尚未训练，请先调用 train_system() for {self.mode}"}

        try:
            # 1. 估算所有工程量参数（这部分保持不变）
            main_quantity_input = user_inputs.get(self.core_quantity_key)
            if main_quantity_input is None:
                for key, val in user_inputs.items():
                    if val is not None and val > 0 and key in self.cluster_features_for_matching:
                        main_quantity_input = val
                        self.logger.info(f"Using provided '{key}' ({main_quantity_input}) as main quantity for estimation.")
                        break
            if main_quantity_input is None or main_quantity_input <= 0:
                self.logger.error(f"无法从输入中获取有效的核心工程量 ({self.core_quantity_key}) 或其他聚类特征来估算其他工程量 for {self.mode}.")
                main_quantity_input = 0

            # 匹配集群规则
            selected_rules = self._match_cluster_rules(main_quantity_input)

            # 根据规则估算所有工程量参数
            estimated_quantities = self._estimate_quantities_based_on_rules(user_inputs, main_quantity_input, selected_rules)
            if estimated_quantities is None:
                return {"error": f"无法从输入参数估算所有工程量 for {self.mode}，请至少提供一个有效参数。"}

            # 2. 计算各项成本 (对应 ML Features)
            calculated_ml_features = self._calculate_ml_features_from_quantities_and_unit_prices(
                estimated_quantities, unit_prices_from_db
            )
            # 确保所有 ML_FEATURES 都存在且为数值
            for feature in self.ml_features:
                if feature not in calculated_ml_features or calculated_ml_features[feature] is None:
                    calculated_ml_features[feature] = 0.0

            self.logger.info(f"Calculated ML features for {self.mode}: {calculated_ml_features}")

            # 3. 获取措施费
            measures_cost_value = user_inputs.get('措施费工程量', 0.0)

            # 4. 四种独立的预测方法 - 重构后的逻辑
            prediction_results = {}
            
            # === 第一步：基于算法能力执行预测计算 ===
            ai_raw_result = None
            ai_final_result = None
            ratio_raw_result = None
            ratio_final_result = None
            
            # AI预测计算（基于算法可用性）
            if self.can_execute_ai_prediction():
                try:
                    ai_raw_result = self._ml_predict(calculated_ml_features)
                    ai_final_result = self._add_measures_cost_to_predictions(
                        ai_raw_result.copy() if ai_raw_result else None, 
                        measures_cost_value
                    )
                    self.logger.info(f"✅ AI预测计算完成 for {self.mode}")
                except Exception as e:
                    self.logger.error(f"❌ AI预测计算失败 for {self.mode}: {e}")
                    ai_raw_result = {"error": f"AI预测计算异常: {str(e)}"}
                    ai_final_result = {"error": f"AI预测计算异常: {str(e)}"}
            else:
                algo_status = self.check_algorithm_execution_capability()
                ai_error_msg = {
                    "error": "AI预测无法执行", 
                    "reason": algo_status['message'],
                    "details": f"可用算法: {algo_status['enabled_count']}/{algo_status['total_count']}"
                }
                ai_raw_result = ai_error_msg.copy()
                ai_final_result = ai_error_msg.copy()
                self.logger.warning(f"⚠️ AI预测跳过执行 for {self.mode}: {algo_status['message']}")

            # 比率法预测计算（基于比率法可用性）
            if self.can_execute_ratio_prediction():
                try:
                    ratio_raw_result = self._ratio_method_predict(calculated_ml_features, selected_rules)
                    if isinstance(ratio_raw_result, (int, float)):
                        ratio_final_result = ratio_raw_result + measures_cost_value
                    else:
                        ratio_final_result = ratio_raw_result
                    self.logger.info(f"✅ 比率法预测计算完成 for {self.mode}")
                except Exception as e:
                    self.logger.error(f"❌ 比率法预测计算失败 for {self.mode}: {e}")
                    ratio_raw_result = {"error": f"比率法预测计算异常: {str(e)}"}
                    ratio_final_result = {"error": f"比率法预测计算异常: {str(e)}"}
            else:
                ratio_error_msg = {
                    "error": "比率法预测无法执行",
                    "reason": "缺少必要的历史数据或规则库",
                    "details": f"训练状态: {self.is_trained}, 历史数据: {len(self.df_historical) if self.df_historical is not None else 0}条"
                }
                ratio_raw_result = ratio_error_msg.copy()
                ratio_final_result = ratio_error_msg.copy()
                self.logger.warning(f"⚠️ 比率法预测跳过执行 for {self.mode}: 缺少必要数据")

            # === 第二步：基于显示权限决定最终输出 ===
            prediction_methods = [
                ('ml_prediction_raw', 'AI预测-原始值', ai_raw_result),
                ('ml_prediction_final', 'AI预测-最终值', ai_final_result),
                ('ratio_method_raw', '比率法-原始值', ratio_raw_result),
                ('ratio_method_final', '比率法-最终值', ratio_final_result)
            ]

            for method_key, display_name, computed_result in prediction_methods:
                combined_status = self.get_combined_prediction_status(method_key)
                
                if combined_status['final_status'] == 'fully_available':
                    # 可以执行且可以显示
                    prediction_results[display_name] = computed_result
                    
                elif combined_status['final_status'] == 'execute_only':
                    # 可以执行但显示被禁用
                    prediction_results[display_name] = {
                        "status": "display_disabled",
                        "message": f"🚫 {combined_status['display_status']['message']}",
                        "indicator_code": combined_status['display_status']['indicator_code'],
                        "hidden_result_available": True  # 标记实际有计算结果但被隐藏
                    }
                    
                elif combined_status['final_status'] == 'display_error':
                    # 想显示但无法执行
                    prediction_results[display_name] = {
                        "status": "execution_failed",
                        "message": f"❌ 无法执行预测计算",
                        "reason": combined_status['execution_status']['message'],
                        "suggestion": f"若需使用{display_name}，请到数据管理模块启用相关算法"
                    }
                    
                else:  # fully_disabled
                    # 既不能执行也不能显示
                    prediction_results[display_name] = {
                        "status": "fully_disabled", 
                        "message": f"🚫 {display_name}已完全禁用",
                        "execution_reason": combined_status['execution_status']['message'],
                        "display_reason": combined_status['display_status']['message']
                    }

                # 添加详细的状态日志
                self.logger.info(f"📊 {display_name} 最终状态: {combined_status['final_status']}")

            # 5. 添加详细的状态控制信息到结果中
            prediction_results["预测方法状态"] = {}
            prediction_results["算法执行状态"] = self.check_algorithm_execution_capability()
            prediction_results["显示权限状态"] = {}
            
            for method_key, display_name, _ in prediction_methods:
                combined_status = self.get_combined_prediction_status(method_key)
                prediction_results["预测方法状态"][method_key] = {
                    'name': display_name,
                    'can_execute': combined_status['can_execute'],
                    'can_display': combined_status['can_display'],
                    'final_status': combined_status['final_status'],
                    'execution_message': combined_status['execution_status']['message'],
                    'display_message': combined_status['display_status']['message']
                }
                prediction_results["显示权限状态"][method_key] = combined_status['display_status']

# 6. 生成状态汇总信息
            prediction_results["状态汇总"] = get_prediction_status_summary(self.mode)

            # 7. 为了兼容现有的界面代码，智能选择主要显示结果
            # 优先选择可以正常执行且可以显示的方法
            main_ml_result = None
            main_ratio_result = None
            
            # AI预测结果选择逻辑：优先选择有效结果
            ai_methods = [
                ('AI预测-原始值', ai_raw_result),
                ('AI预测-最终值', ai_final_result)
            ]
            
            for method_name, result in ai_methods:
                method_key = 'ml_prediction_raw' if '原始值' in method_name else 'ml_prediction_final'
                combined_status = self.get_combined_prediction_status(method_key)
                
                if combined_status['final_status'] == 'fully_available':
                    # 优先选择完全可用的方法
                    if result and not isinstance(result, dict) or (isinstance(result, dict) and 'error' not in result):
                        main_ml_result = result
                        self.logger.info(f"选择 {method_name} 作为主要AI预测结果")
                        break
                elif combined_status['can_execute'] and result:
                    # 如果没有完全可用的，选择可执行的作为备选
                    if main_ml_result is None:
                        main_ml_result = result
                        self.logger.info(f"备选: {method_name} 作为主要AI预测结果")

            # 比率法预测结果选择逻辑：同样优先选择有效结果
            ratio_methods = [
                ('比率法-原始值', ratio_raw_result),
                ('比率法-最终值', ratio_final_result)
            ]
            
            for method_name, result in ratio_methods:
                method_key = 'ratio_method_raw' if '原始值' in method_name else 'ratio_method_final'
                combined_status = self.get_combined_prediction_status(method_key)
                
                if combined_status['final_status'] == 'fully_available':
                    # 优先选择完全可用的方法
                    if result and not isinstance(result, dict) or (isinstance(result, dict) and 'error' not in result):
                        main_ratio_result = result
                        self.logger.info(f"选择 {method_name} 作为主要比率法预测结果")
                        break
                elif combined_status['can_execute'] and result:
                    # 如果没有完全可用的，选择可执行的作为备选
                    if main_ratio_result is None:
                        main_ratio_result = result
                        self.logger.info(f"备选: {method_name} 作为主要比率法预测结果")

            # 如果没有找到合适的主要结果，使用错误信息
            if main_ml_result is None:
                ai_capability = self.check_algorithm_execution_capability()
                main_ml_result = {
                    "error": "AI预测不可用",
                    "reason": ai_capability['message'],
                    "suggestion": "请检查算法配置或综合指标设置"
                }
                self.logger.warning(f"未找到可用的AI预测结果，使用错误信息")

            if main_ratio_result is None:
                main_ratio_result = {
                    "error": "比率法预测不可用",
                    "reason": "缺少必要的历史数据或显示权限",
                    "suggestion": "请检查数据配置或综合指标设置"
                }
                self.logger.warning(f"未找到可用的比率法预测结果，使用错误信息")

            # 整合结果（保持向后兼容）
            results = {
                "匹配到的规则来源": selected_rules.get('source', '全局平均'),
                "估算的工程量": estimated_quantities,
                "估算的各项成本 (用于ML的特征)": calculated_ml_features,
                # 主要结果（用于兼容现有界面）- 修改后的智能选择逻辑
                "机器学习预测结果": main_ml_result,
                "比率法预测总价": main_ratio_result,
                # 新增：四种独立的预测结果
                "AI预测-原始值": prediction_results["AI预测-原始值"],
                "AI预测-最终值": prediction_results["AI预测-最终值"],
                "比率法-原始值": prediction_results["比率法-原始值"],
                "比率法-最终值": prediction_results["比率法-最终值"],
                # 状态信息 - 修改后的详细状态
                "预测方法状态": prediction_results["预测方法状态"],
                "算法执行状态": prediction_results["算法执行状态"],
                "显示权限状态": prediction_results["显示权限状态"],
                "状态汇总": prediction_results["状态汇总"],
                "算法可用性状态": self.validate_algorithm_availability(),
                "用户输入": user_inputs,
                "措施费": measures_cost_value
            }
            # 【新增】添加最佳算法参数信息
            try:
                # 获取用于比较的预测结果
                comparison_ml_result = main_ml_result
                comparison_ratio_result = main_ratio_result
                
                # 如果主要结果是字典格式（错误或状态信息），尝试从原始预测结果中获取
                if isinstance(comparison_ml_result, dict) and 'error' in comparison_ml_result:
                    # 尝试从AI预测原始值或最终值中获取数值结果
                    ai_raw = prediction_results.get("AI预测-原始值")
                    ai_final = prediction_results.get("AI预测-最终值")
                    
                    if isinstance(ai_raw, dict) and 'error' not in ai_raw:
                        comparison_ml_result = ai_raw
                    elif isinstance(ai_final, dict) and 'error' not in ai_final:
                        comparison_ml_result = ai_final
                
                if isinstance(comparison_ratio_result, dict) and 'error' in comparison_ratio_result:
                    # 尝试从比率法原始值或最终值中获取数值结果
                    ratio_raw = prediction_results.get("比率法-原始值")
                    ratio_final = prediction_results.get("比率法-最终值")
                    
                    if isinstance(ratio_raw, (int, float)):
                        comparison_ratio_result = ratio_raw
                    elif isinstance(ratio_final, (int, float)):
                        comparison_ratio_result = ratio_final
                
                # 获取最佳算法信息
                if (isinstance(comparison_ml_result, dict) and 
                    isinstance(comparison_ratio_result, (int, float))):
                    # 如果ML结果是字典（包含多个算法结果）
                    best_algorithm_info = self.get_best_algorithm_info_with_params(
                        comparison_ml_result, comparison_ratio_result
                    )
                    results["最佳算法信息"] = best_algorithm_info
                    self.logger.info(f"✅ 已添加最佳算法信息: {best_algorithm_info.get('best_algorithm_name', '未确定')}")
                else:
                    # 如果无法获取有效的比较数据
                    results["最佳算法信息"] = {
                        "best_algorithm_name": None,
                        "selection_reason": "无法获取有效的预测结果进行比较"
                    }
                    self.logger.warning("⚠️ 无法确定最佳算法：缺少有效的预测结果")
                    
            except Exception as e:
                self.logger.error(f"❌ 添加最佳算法信息时发生错误: {e}")
                results["最佳算法信息"] = {
                    "best_algorithm_name": None,
                    "selection_reason": f"获取最佳算法信息时出错: {str(e)}"
                }
            return results

        except Exception as e:
            self.logger.error(f"预测过程出错 for {self.mode}: {e}", exc_info=True)
            return {"error": f"预测过程异常 for {self.mode}: {e}"}

    def _add_measures_cost_to_predictions(self, ml_predictions, measures_cost_value):
        """
        为机器学习预测结果添加措施费的辅助方法（独立版本）
        
        Args:
            ml_predictions (dict): ML预测结果
            measures_cost_value (float): 措施费数值
            
        Returns:
            dict: 更新后的预测结果
        """
        if not isinstance(ml_predictions, dict) or 'status' in ml_predictions:
            return ml_predictions
        
        result = ml_predictions.copy()
        for model_key, prediction_value in result.items():
            if isinstance(prediction_value, (int, float)) and prediction_value is not None:
                result[model_key] += measures_cost_value
                self.logger.debug(f"为 {self.mode} 模式的 {model_key} 添加措施费 {measures_cost_value}")
        
        return result


    def _match_cluster_rules(self, main_quantity_input):
        """匹配最适合的聚类规则"""
        if self.use_clustering and self.kmeans and self.scaler_cluster and main_quantity_input is not None and main_quantity_input > 0:
            cluster_input_data = {}
            for feature in self.cluster_features_for_matching:
                if feature == self.core_quantity_key:
                    cluster_input_data[feature] = main_quantity_input
                else:
                    ratio_key = f'avg_qty_ratio_{feature}_per_{self.core_quantity_key}'
                    if ratio_key in self.global_rules and self.global_rules[ratio_key] is not None:
                        cluster_input_data[feature] = main_quantity_input * self.global_rules[ratio_key]
                    else:
                        cluster_input_data[feature] = 0

            current_project_features_df = pd.DataFrame([cluster_input_data])
            current_project_features_df = current_project_features_df[[f for f in self.cluster_features_for_matching if f in current_project_features_df.columns]]

            try:
                current_project_scaled = self.scaler_cluster.transform(current_project_features_df)
                predicted_cluster = self.kmeans.predict(current_project_scaled)[0]
                selected_rules = self.cluster_rules.get(predicted_cluster, self.global_rules)
                selected_rules['source'] = f"簇 {predicted_cluster}"
                self.logger.info(f"Matched to cluster {predicted_cluster} for {self.mode}.")
            except Exception as e:
                self.logger.warning(f"聚类匹配失败 for {self.mode}: {e}. 使用全局平均规则。", exc_info=True)
                selected_rules = self.global_rules.copy()
                selected_rules['source'] = "全局平均 (匹配失败)"
        else:
            selected_rules = self.global_rules.copy()
            selected_rules['source'] = "全局平均"
            if not self.use_clustering:
                self.logger.info(f"Clustering disabled or not enough data for {self.mode}. Using global rules.")
            elif not self.kmeans:
                self.logger.warning(f"KMeans model not trained for {self.mode}. Using global rules.")

        return selected_rules

    def _estimate_quantities_based_on_rules(self, user_inputs, main_quantity_input, rules):
        estimated_quantities = {}

        all_relevant_quantity_columns = [
            '拼装场地总工程量', '制作胎具总工程量', '钢支墩埋件总工程量', '扶壁柱总工程量',
            '走道板操作平台总工程量', '钢网梁总工程量',
            '钢筋总吨数', '塔吊租赁工程量', '吊索具数量', '套筒数量',
            '钢支墩埋件混凝土剔凿总工程量', '钢支墩埋件混凝土回填总工程量',
            '钢支墩埋件安装总工程量', '钢支墩埋件制作总工程量',
            '扶壁柱安装总工程量', '扶壁柱拆除总工程量', '扶壁柱构件使用折旧总工程量',
            '走道板操作平台制作总工程量', '走道板操作平台搭设总工程量', '走道板操作平台拆除总工程量',
            '钢网架制作总工程量', '钢网架安装总工程量', '钢网架拆除总工程量',
        ]
        relevant_quantity_columns = [col for col in all_relevant_quantity_columns if col in self.df_historical.columns]

        for qty_col in relevant_quantity_columns:
            user_val = user_inputs.get(qty_col)
            if user_val is not None and pd.notna(user_val) and float(user_val) > 0:
                estimated_quantities[qty_col] = float(user_val)
                self.logger.debug(f"Using user provided value for {qty_col}: {float(user_val)}")
            elif qty_col == self.core_quantity_key and (main_quantity_input is not None and main_quantity_input > 0):
                estimated_quantities[qty_col] = main_quantity_input
                self.logger.debug(f"Using main_quantity_input for {qty_col}: {main_quantity_input}")
            elif main_quantity_input is not None and main_quantity_input > 0:
                ratio_key = f'avg_qty_ratio_{qty_col}_per_{self.core_quantity_key}'
                if ratio_key in rules and rules[ratio_key] is not None:
                    estimated_value = main_quantity_input * rules[ratio_key]
                    estimated_quantities[qty_col] = estimated_value
                    self.logger.debug(f"Estimated {qty_col} using ratio: {estimated_value}")
                else:
                    avg_qty_key = f'avg_qty_{qty_col}'
                    if avg_qty_key in rules and rules[avg_qty_key] is not None:
                        estimated_quantities[qty_col] = rules[avg_qty_key]
                        self.logger.debug(f"Estimated {qty_col} using average quantity from rules: {rules[avg_qty_key]}")
                    else:
                        estimated_quantities[qty_col] = 0.0
                        self.logger.warning(f"Cannot estimate {qty_col} for {self.mode}. No ratio or average found.")
            else:
                avg_qty_key = f'avg_qty_{qty_col}'
                if avg_qty_key in rules and rules[avg_qty_key] is not None:
                    estimated_quantities[qty_col] = rules[avg_qty_key]
                    self.logger.debug(f"Estimated {qty_col} using average quantity from rules (no main_quantity_input): {rules[avg_qty_key]}")
                else:
                    estimated_quantities[qty_col] = 0.0
                    self.logger.warning(f"Cannot estimate {qty_col} for {self.mode}. No main_quantity_input, ratio, or average found.")

        return estimated_quantities

    def _calculate_ml_features_from_quantities_and_unit_prices(self, estimated_quantities, unit_prices_from_db):
        """根据估算的工程量和历史学习到的平均单位成本计算机器学习模型所需的特征"""
        calculated_features = {}
        selected_rules = self._match_cluster_rules(estimated_quantities.get(self.core_quantity_key, 0))

        for ml_feature, qty_col in self.ml_feature_to_qty_map.items():
            qty = estimated_quantities.get(qty_col, 0.0)
            avg_unit_cost_key = f'avg_unit_cost_{ml_feature}'
            avg_unit_cost = selected_rules.get(avg_unit_cost_key, 0.0)

            calculated_features[ml_feature] = qty * avg_unit_cost
            self.logger.debug(f"计算预测ML特征 '{ml_feature}': 工程量 {qty:.2f} * 平均单位成本 {avg_unit_cost:.2f} = {calculated_features[ml_feature]:.2f}")

        return calculated_features

    def _ml_predict(self, calculated_ml_features):
        """使用机器学习模型进行预测 - 改进版本"""
        feature_vector_dict = {col: [calculated_ml_features.get(col, 0.0)] for col in self.ml_features}
        feature_df = pd.DataFrame(feature_vector_dict)
        
        for col in self.ml_features:
            if col not in feature_df.columns:
                feature_df[col] = 0.0
        feature_df = feature_df[self.ml_features]

        predictions = {}
        
        # 首先处理启用的算法
        for model_name, model in self.models.items():
            try:
                if isinstance(model, Pipeline) and isinstance(model.steps[0][1], StandardScaler):
                    scaled_features = model.named_steps['scaler'].transform(feature_df)
                    pred = model.named_steps['regressor'].predict(scaled_features)[0]
                else:
                    pred = model.predict(feature_df)[0]

                if 0 < pred < 5000000000:
                    predictions[model_name] = pred
                    self.logger.debug(f"✅ {model_name} 预测成功: {pred:.2f}")
                else:
                    predictions[model_name] = None
                    self.logger.warning(f"⚠️ {model_name} 预测值超出合理范围: {pred:.2f}")
            except Exception as e:
                predictions[model_name] = None
                self.logger.error(f"❌ {model_name} 预测失败: {e}")

        # 然后为停用的算法添加状态信息
        algorithm_status = self.get_algorithm_status_info()
        for disabled_algorithm in algorithm_status['disabled']:
            model_key = disabled_algorithm['display_name']
            predictions[model_key] = {
                'status': 'disabled',
                'message': "算法已停用 - 若需启用请到数据管理模块",
                'db_name': disabled_algorithm['db_name']
            }
            self.logger.debug(f"🚫 {model_key} 已停用，添加状态信息")

        # 计算集成预测（只基于启用且成功的算法）
        valid_predictions = [
            p for p in predictions.values() 
            if isinstance(p, (int, float)) and p is not None
        ]
        
        if valid_predictions:
            ensemble_avg = np.mean(valid_predictions)
            predictions['集成平均预测'] = ensemble_avg
            self.logger.info(f"🎯 集成预测基于 {len(valid_predictions)} 个有效算法: {ensemble_avg:.2f}")
        else:
            predictions['集成平均预测'] = None
            self.logger.warning("⚠️ 没有有效的算法预测结果，无法计算集成预测")
        
        return predictions

    def _ratio_method_predict(self, calculated_ml_features, rules):
        """使用比率法预测总价"""
        core_costs_sum = sum(calculated_ml_features.get(col, 0) for col in self.ml_features)
        print(core_costs_sum)
        
        avg_percentage = rules.get(self.ratio_method_factor_col)
        print(avg_percentage)
        if avg_percentage is None or np.isnan(avg_percentage) or avg_percentage <= 0:
            self.logger.warning(f"比率法因子 '{self.ratio_method_factor_col}' 无效或为零 for {self.mode}. 使用默认比例 0.8。")
            avg_percentage = 0.8

        if core_costs_sum > 0 and avg_percentage > 0:
            return core_costs_sum / avg_percentage
        else:
            self.logger.warning(f"比率法预测条件不足 (核心成本为0或平均比例为0) for {self.mode}.")
            return 0.0
    # ================== CostPredictionSystem 类方法（放在类里面） ==================
    # 以下方法需要添加到 CostPredictionSystem 类中，建议放在类的末尾

    def load_comprehensive_indicators_status(self):
        """为当前模式加载综合指标状态"""
        self.comprehensive_indicators_status = get_comprehensive_indicators_status(self.mode)
        self.prediction_method_availability = check_prediction_method_availability(self.mode)
        self.logger.info(f"综合指标状态加载完成 for mode: {self.mode}")

    def is_prediction_method_enabled(self, method_key):
        """
        检查指定预测方法是否启用
        
        Args:
            method_key (str): 预测方法键名 (如 'ml_prediction_raw', 'ratio_method_final')
            
        Returns:
            bool: 是否启用
        """
        if not hasattr(self, 'prediction_method_availability'):
            self.load_comprehensive_indicators_status()
        
        return self.prediction_method_availability.get(method_key, {}).get('enabled', False)

    def get_disabled_prediction_info(self, method_key):
        """
        获取被禁用的预测方法的详细信息
        
        Args:
            method_key (str): 预测方法键名
            
        Returns:
            dict: 禁用信息
        """
        if not hasattr(self, 'prediction_method_availability'):
            self.load_comprehensive_indicators_status()
        
        method_info = self.prediction_method_availability.get(method_key, {})
        
        return {
            'status': 'disabled',
            'message': f"🚫 已禁用 - 若需启用请到数据管理模块修改「{method_info.get('name', '未知指标')}」状态",
            'indicator_code': method_info.get('indicator_code', ''),
            'indicator_name': method_info.get('name', '')
        }

    # ================== 新增方法开始 ==================
    
    def check_algorithm_execution_capability(self):
        """
        检查算法层的执行能力
        
        Returns:
            dict: 算法执行能力状态
        """
        if not self.algorithm_status_loaded:
            self.load_algorithm_configs()
        
        enabled_algorithms = list(self.enabled_algorithms.keys())
        total_algorithms = len(self.algorithm_configs)
        enabled_count = len(enabled_algorithms)
        
        return {
            'can_execute_ai': enabled_count > 0,
            'enabled_algorithms': enabled_algorithms,
            'enabled_count': enabled_count,
            'total_count': total_algorithms,
            'status': 'available' if enabled_count > 0 else 'unavailable',
            'message': f'有{enabled_count}个算法可用' if enabled_count > 0 else '所有AI预测算法已停用'
        }

    def check_result_display_permission(self, method_key):
        """
        检查综合指标层的显示权限
        
        Args:
            method_key (str): 预测方法键名
            
        Returns:
            dict: 显示权限状态
        """
        if not hasattr(self, 'prediction_method_availability'):
            self.load_comprehensive_indicators_status()
        
        method_info = self.prediction_method_availability.get(method_key, {})
        enabled = method_info.get('enabled', False)
        
        return {
            'can_display': enabled,
            'status': 'enabled' if enabled else 'disabled',
            'indicator_name': method_info.get('name', ''),
            'indicator_code': method_info.get('indicator_code', ''),
            'message': '允许显示' if enabled else f"显示已禁用 - 「{method_info.get('name', '未知指标')}」"
        }

    def can_execute_ai_prediction(self):
        """
        检查是否可以执行AI预测计算
        
        Returns:
            bool: 是否可以执行AI预测
        """
        algo_capability = self.check_algorithm_execution_capability()
        return algo_capability['can_execute_ai'] and self.is_trained and len(self.models) > 0

    def can_execute_ratio_prediction(self):
        """
        检查是否可以执行比率法预测计算
        
        Returns:
            bool: 是否可以执行比率法预测
        """
        # 比率法预测只需要历史数据和规则，不依赖算法配置
        return (self.is_trained and 
                self.df_historical is not None and 
                len(self.df_historical) > 0 and 
                bool(self.global_rules))

    def get_combined_prediction_status(self, method_key):
        """
        获取预测方法的综合状态（算法能力 + 显示权限）
        
        Args:
            method_key (str): 预测方法键名
            
        Returns:
            dict: 综合状态信息
        """
        display_permission = self.check_result_display_permission(method_key)
        
        if method_key.startswith('ml_') or 'AI预测' in method_key:
            # AI预测方法
            algo_capability = self.check_algorithm_execution_capability()
            can_execute = self.can_execute_ai_prediction()
            
            return {
                'method_key': method_key,
                'can_execute': can_execute,
                'can_display': display_permission['can_display'],
                'execution_status': algo_capability,
                'display_status': display_permission,
                'final_status': self._determine_final_status(can_execute, display_permission['can_display'], 'ai')
            }
        elif method_key.startswith('ratio_') or '比率法' in method_key:
            # 比率法预测方法
            can_execute = self.can_execute_ratio_prediction()
            
            return {
                'method_key': method_key,
                'can_execute': can_execute,
                'can_display': display_permission['can_display'],
                'execution_status': {'can_execute': can_execute, 'message': '比率法预测可用' if can_execute else '比率法预测不可用'},
                'display_status': display_permission,
                'final_status': self._determine_final_status(can_execute, display_permission['can_display'], 'ratio')
            }
        else:
            return {
                'method_key': method_key,
                'can_execute': False,
                'can_display': False,
                'final_status': 'unknown_method'
            }

    def _determine_final_status(self, can_execute, can_display, method_type):
        """
        确定预测方法的最终状态
        
        Args:
            can_execute (bool): 是否可以执行
            can_display (bool): 是否可以显示
            method_type (str): 方法类型 ('ai' 或 'ratio')
            
        Returns:
            str: 最终状态描述
        """
        if can_execute and can_display:
            return 'fully_available'
        elif can_execute and not can_display:
            return 'execute_only'  # 可以执行但不显示
        elif not can_execute and can_display:
            return 'display_error'  # 想显示但无法执行
        else:
            return 'fully_disabled'  # 既不能执行也不能显示

    def get_best_algorithm_info_with_params(self, ml_predictions, ratio_prediction_value):
        """
        获取最佳算法信息及其参数配置
        
        Args:
            ml_predictions (dict): 机器学习预测结果
            ratio_prediction_value: 比率法预测值
            
        Returns:
            dict: 最佳算法的详细信息和参数
        """
        if not ratio_prediction_value or not ml_predictions:
            return {
                "best_algorithm_name": None,
                "best_prediction_value": None,
                "algorithm_parameters": {},
                "parameter_details": {},
                "selection_reason": "无有效预测结果用于比较"
            }
        
        best_algorithm_key = None
        min_diff_to_ratio = float('inf')
        best_prediction_value = None
        
        # 找到最接近比率法的算法
        for model_key, prediction_value in ml_predictions.items():
            # 跳过特殊键和停用算法
            if (model_key in ['集成平均预测', '_algorithm_status'] or 
                prediction_value is None or 
                isinstance(prediction_value, dict)):
                continue
                
            # 确保这是一个启用的算法且有数值预测结果
            if isinstance(prediction_value, (int, float)):
                diff = abs(prediction_value - ratio_prediction_value)
                if diff < min_diff_to_ratio:
                    min_diff_to_ratio = diff
                    best_algorithm_key = model_key
                    best_prediction_value = prediction_value
        
        if not best_algorithm_key:
            return {
                "best_algorithm_name": None,
                "best_prediction_value": None,
                "algorithm_parameters": {},
                "parameter_details": {},
                "selection_reason": "未找到有效的最佳算法"
            }
        
        # 获取算法的中文名称
        algorithm_name_mapping = {
            "岭回归 (RidgeCV)": "岭回归",
            "决策树 (Decision Tree)": "决策树", 
            "随机森林 (Random Forest)": "随机森林",
            "支持向量回归 (SVR)": "支持向量回归",
            "神经网络 (MLPRegressor)": "神经网络"
        }
        
        algorithm_chinese_name = algorithm_name_mapping.get(best_algorithm_key, best_algorithm_key)
        
        # 获取算法的参数配置
        algorithm_params = self.get_algorithm_parameters_parsed(algorithm_chinese_name)
        
        # 获取参数的详细信息（包括中文名称、建议范围等）
        parameter_details = {}
        if self.parameters_loaded:
            raw_params = self.get_algorithm_parameters_raw(algorithm_chinese_name)
            for param_name, param_info in raw_params.items():
                parameter_details[param_name] = {
                    "chinese_name": param_info.get("value", param_name),  # 修正：应该从数据库字段获取中文名
                    "current_value": param_info.get("value"),
                    "type": param_info.get("type"),
                    "parsed_value": algorithm_params.get(param_name),
                    "suggested_range": "",  # 暂时为空，需要从数据库获取
                    "adjustment_tips": ""   # 暂时为空，需要从数据库获取
                }
        
        # 计算与比率法的差异百分比
        diff_percentage = (min_diff_to_ratio / ratio_prediction_value) * 100 if ratio_prediction_value > 0 else 0
        
        return {
            "best_algorithm_name": best_algorithm_key,
            "best_algorithm_chinese_name": algorithm_chinese_name,
            "best_prediction_value": best_prediction_value,
            "algorithm_parameters": algorithm_params,
            "parameter_details": parameter_details,
            "selection_reason": f"与比率法预测值最接近，差异: {min_diff_to_ratio:,.2f}元 ({diff_percentage:.2f}%)",
            "difference_to_ratio": min_diff_to_ratio,
            "difference_percentage": diff_percentage
        }

    def format_best_algorithm_params_for_report(self, best_algorithm_info):
        """
        格式化最佳算法参数信息，用于报表显示
        
        Args:
            best_algorithm_info (dict): 最佳算法信息
            
        Returns:
            dict: 格式化后的信息，适合在报表中显示
        """
        if not best_algorithm_info or not best_algorithm_info.get("best_algorithm_name"):
            return {
                "算法名称": "未确定",
                "参数配置": "无",
                "选择原因": "无有效算法结果"
            }
        
        # 格式化参数列表
        formatted_params = []
        parameter_details = best_algorithm_info.get("parameter_details", {})
        
        for param_name, param_info in parameter_details.items():
            chinese_name = param_info.get("chinese_name", param_name)
            current_value = param_info.get("current_value", "未知")
            param_type = param_info.get("type", "")
            
            formatted_params.append({
                "参数名": param_name,
                "中文名": chinese_name,
                "当前值": current_value,
                "类型": param_type,
                "建议范围": param_info.get("suggested_range", ""),
                "调优提示": param_info.get("adjustment_tips", "")
            })
        
        return {
            "算法名称": best_algorithm_info.get("best_algorithm_name", ""),
            "算法中文名": best_algorithm_info.get("best_algorithm_chinese_name", ""),
            "预测值": best_algorithm_info.get("best_prediction_value", 0),
            "选择原因": best_algorithm_info.get("selection_reason", ""),
            "与比率法差异": best_algorithm_info.get("difference_to_ratio", 0),
            "差异百分比": best_algorithm_info.get("difference_percentage", 0),
            "参数配置": formatted_params,
            "参数数量": len(formatted_params)
        }
    
# ================== 独立函数（放在文件末尾，CostPredictionSystem 类外面） ==================

def get_comprehensive_indicators_status(mode='steel_cage'):
    """
    查询comprehensive_indicators表中指定模式的状态信息
    
    Args:
        mode (str): 施工模式 ('steel_cage' 或 'steel_lining')
    
    Returns:
        dict: {指标编码: 状态信息} 的字典
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT code, name, calculation_method, indicator_type, status, calculation_logic
        FROM comprehensive_indicators 
        WHERE construction_mode = %s
        ORDER BY id
        """
        
        cursor.execute(query, (mode,))
        results = cursor.fetchall()
        
        status_dict = {}
        for row in results:
            status_dict[row['code']] = {
                'name': row['name'],
                'calculation_method': row['calculation_method'],
                'indicator_type': row['indicator_type'], 
                'status': row['status'],
                'calculation_logic': row.get('calculation_logic', ''),
                'enabled': row['status'] == 'enabled'
            }
        
        # 使用 logging 模块而不是 logger
        logging.info(f"成功查询到 {len(status_dict)} 个综合指标的状态信息 for mode: {mode}")
        return status_dict
        
    except mysql.connector.Error as e:
        logging.error(f"查询综合指标状态失败 for mode {mode}: {e}")
        return {}
    except Exception as e:
        logging.error(f"查询综合指标状态时发生错误 for mode {mode}: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def check_prediction_method_availability(mode='steel_cage'):
    """
    检查指定模式下各种预测方法的可用性
    
    Args:
        mode (str): 施工模式
        
    Returns:
        dict: 各预测方法的可用性状态
    """
    indicators_status = get_comprehensive_indicators_status(mode)
    
    # 根据模式定义指标编码映射
    if mode == 'steel_cage':
        indicator_mapping = {
            'ml_prediction_raw': 'FU-ZJ-ML-RAW',
            'ml_prediction_final': 'FU-ZJ-ML-FINAL', 
            'ratio_method_raw': 'FU-ZJ-RATIO-RAW',
            'ratio_method_final': 'FU-ZJ-RATIO-FINAL'
        }
    elif mode == 'steel_lining':
        indicator_mapping = {
            'ml_prediction_raw': 'FU-ZJ-GCL-ML-RAW',
            'ml_prediction_final': 'FU-ZJ-GCL-ML-FINAL',
            'ratio_method_raw': 'FU-ZJ-GCL-RATIO-RAW', 
            'ratio_method_final': 'FU-ZJ-GCL-RATIO-FINAL'
        }
    else:
        logging.warning(f"未支持的模式: {mode}")
        return {}
    
    availability = {}
    for method_key, indicator_code in indicator_mapping.items():
        indicator_info = indicators_status.get(indicator_code, {})
        availability[method_key] = {
            'enabled': indicator_info.get('enabled', False),
            'status': indicator_info.get('status', 'unknown'),
            'name': indicator_info.get('name', ''),
            'indicator_code': indicator_code
        }
    
    logging.info(f"预测方法可用性检查完成 for mode {mode}: {availability}")
    return availability

def get_prediction_status_summary(mode='steel_cage'):
    """
    获取预测状态的汇总信息，用于界面显示
    
    Args:
        mode (str): 施工模式
        
    Returns:
        dict: 状态汇总信息
    """
    availability = check_prediction_method_availability(mode)
    
    enabled_methods = []
    disabled_methods = []
    
    method_display_names = {
        'ml_prediction_raw': 'AI预测-原始值',
        'ml_prediction_final': 'AI预测-最终值',
        'ratio_method_raw': '比率法-原始值', 
        'ratio_method_final': '比率法-最终值'
    }
    
    for method_key, status_info in availability.items():
        display_name = method_display_names.get(method_key, method_key)
        
        if status_info['enabled']:
            enabled_methods.append({
                'key': method_key,
                'display_name': display_name,
                'indicator_name': status_info['name']
            })
        else:
            disabled_methods.append({
                'key': method_key,
                'display_name': display_name,
                'indicator_name': status_info['name']
            })
    
    return {
        'total_methods': len(availability),
        'enabled_count': len(enabled_methods),
        'disabled_count': len(disabled_methods),
        'enabled_methods': enabled_methods,
        'disabled_methods': disabled_methods,
        'all_enabled': len(disabled_methods) == 0,
        'all_disabled': len(enabled_methods) == 0,
        'partial_available': len(enabled_methods) > 0 and len(disabled_methods) > 0
    }

# ==================== 更新后的配置文件 ====================
# modules/pricePrediction/config.py

# ==================== MySQL配置 ====================
# MySQL数据库连接配置在单独的模块中定义
# 这里只定义表名和列映射

