# modules/dataManagement/model_comparison.py
import pandas as pd
import numpy as np
import mysql.connector
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.linear_model import RidgeCV, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import json
import logging

logger = logging.getLogger(__name__)

class ModelPerformanceComparison:
    """模型性能对比类 - 用于评估和比较不同算法在历史数据上的表现"""
    
    def __init__(self, construction_mode='steel_cage'):
        self.construction_mode = construction_mode
        self.mysql_config = {
            'host': 'localhost',
            'user': 'dash',
            'password': '123456',
            'database': 'dash_project',
            'charset': 'utf8mb4'
        }
        self.algorithms = {}
        self.enabled_algorithms = {}
        self.evaluation_results = None
        
    def load_algorithm_configs(self):
        """从数据库加载算法配置"""
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT algorithm_type, algorithm_name, status, parameters
                FROM algorithm_configs 
                WHERE construction_mode = %s
            """
            cursor.execute(query, (self.construction_mode,))
            configs = cursor.fetchall()
            
            for config in configs:
                self.algorithms[config['algorithm_type']] = {
                    'name': config['algorithm_name'],
                    'status': config['status'],
                    'parameters': json.loads(config['parameters']) if config['parameters'] else {}
                }
                
                if config['status'] == 'enabled':
                    self.enabled_algorithms[config['algorithm_type']] = self.algorithms[config['algorithm_type']]
            
            conn.close()
            logger.info(f"加载了 {len(self.algorithms)} 个算法配置，其中 {len(self.enabled_algorithms)} 个已启用")
            return True
            
        except Exception as e:
            logger.error(f"加载算法配置失败: {e}")
            return False
    
    def load_historical_data(self):
        """加载历史数据用于性能评估"""
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            
            if self.construction_mode == 'steel_cage':
                # 钢筋笼模式的历史数据 - 移除ORDER BY避免字段不存在错误
                query = """
                    SELECT 
                        tower_crane_rental_fee, rebar_production_cost, 
                        lifting_equipment_cost, coupling_cost, 
                        project_total_price
                    FROM final_project_summary1 
                    WHERE project_total_price IS NOT NULL 
                    AND project_total_price >= 0
                    LIMIT 100
                """
            else:  # steel_lining
                # 钢衬里模式的历史数据 - 移除ORDER BY避免字段不存在错误
                query = """
                    SELECT 
                        assembly_site_cost, mold_making_cost, 
                        steel_support_embedded_cost, buttress_column_cost,
                        walkway_platform_cost, steel_grid_cost,
                        project_total_price
                    FROM final_project_summary2 
                    WHERE project_total_price IS NOT NULL 
                    AND project_total_price >= 0
                    LIMIT 100
                """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning(f"没有找到 {self.construction_mode} 模式的历史数据")
                return None, None
            
            # 检查数据量是否足够
            if len(df) < 3:
                logger.warning(f"历史数据样本过少 ({len(df)} 条)，建议至少3条以上进行有效评估")
                # 如果数据太少，生成一些模拟数据用于演示
                df = self._generate_demo_data(df)
            
            # 分离特征和目标变量
            X = df.iloc[:, :-1]  # 除最后一列外的所有列作为特征
            y = df.iloc[:, -1]   # 最后一列作为目标变量
            
            # 数据预处理
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # 移除全零或全NaN的列
            X = X.loc[:, (X != 0).any(axis=0)]
            X = X.dropna(axis=1, how='all')
            
            logger.info(f"加载了 {len(df)} 条历史数据，特征数量: {X.shape[1]}")
            return X, y
            
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")
            return None, None
    
    def _generate_demo_data(self, existing_df):
        """当历史数据不足时，生成演示数据"""
        if existing_df.empty:
            # 完全没有数据时，生成基础演示数据
            if self.construction_mode == 'steel_cage':
                demo_data = {
                    'tower_crane_rental_fee': [50000, 45000, 55000, 48000, 52000],
                    'rebar_production_cost': [120000, 115000, 125000, 118000, 122000],
                    'lifting_equipment_cost': [30000, 28000, 32000, 29000, 31000],
                    'coupling_cost': [15000, 14000, 16000, 14500, 15500],
                    'project_total_price': [280000, 265000, 295000, 272000, 288000]
                }
            else:  # steel_lining
                demo_data = {
                    'assembly_site_cost': [35000, 33000, 37000, 34000, 36000],
                    'mold_making_cost': [85000, 82000, 88000, 83000, 87000],
                    'steel_support_embedded_cost': [45000, 43000, 47000, 44000, 46000],
                    'buttress_column_cost': [25000, 24000, 26000, 24500, 25500],
                    'walkway_platform_cost': [18000, 17000, 19000, 17500, 18500],
                    'steel_grid_cost': [22000, 21000, 23000, 21500, 22500],
                    'project_total_price': [320000, 305000, 335000, 312000, 328000]
                }
            return pd.DataFrame(demo_data)
        else:
            # 基于现有数据生成更多样本
            logger.info("基于现有数据生成演示样本以确保足够的评估数据")
            extended_data = []
            for i in range(5):  # 生成5个变体
                for _, row in existing_df.iterrows():
                    # 在原数据基础上增加±10%的随机变化
                    variation = 1 + (np.random.random() - 0.5) * 0.2  # ±10%变化
                    new_row = row * variation
                    extended_data.append(new_row)
            
            return pd.DataFrame(extended_data)
    
    def create_algorithm_instance(self, algorithm_type, parameters, n_samples):
        """根据算法类型和参数创建算法实例"""
        try:
            if algorithm_type == 'linear_regression':
                alphas_range = parameters.get('alphas_range', [-3, 3, 11])
                alphas = np.logspace(alphas_range[0], alphas_range[1], alphas_range[2])
                
                # 根据样本数量动态调整交叉验证折数
                cv_folds = min(parameters.get('cv', 5), max(2, n_samples - 1))
                
                if n_samples < 5:
                    # 样本太少时使用简单的Ridge回归而不是RidgeCV
                    logger.warning(f"样本数量过少 ({n_samples})，使用Ridge回归替代RidgeCV")
                    return Ridge(alpha=1.0)  # 使用固定的正则化参数
                else:
                    return RidgeCV(alphas=alphas, cv=cv_folds)
                
            elif algorithm_type == 'decision_tree':
                # 根据样本数量调整决策树参数
                max_depth = min(parameters.get('max_depth', 4), max(2, n_samples // 3))
                min_samples_leaf = max(1, min(parameters.get('min_samples_leaf', 3), n_samples // 5))
                min_samples_split = max(2, min(parameters.get('min_samples_split', 6), n_samples // 3))
                
                return DecisionTreeRegressor(
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    min_samples_split=min_samples_split,
                    random_state=42
                )
                
            elif algorithm_type == 'random_forest':
                # 根据样本数量调整随机森林参数
                n_estimators = min(parameters.get('n_estimators', 80), max(10, n_samples * 2))
                max_depth = min(parameters.get('max_depth', 6), max(2, n_samples // 3))
                
                return RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    max_features=parameters.get('max_features', 'sqrt'),
                    random_state=42
                )
                
            elif algorithm_type == 'svm':
                return SVR(
                    C=parameters.get('C', 1.0),
                    kernel=parameters.get('kernel', 'rbf'),
                    epsilon=parameters.get('epsilon', 0.1)
                )
                
            elif algorithm_type == 'neural_network':
                hidden_layer_sizes = parameters.get('hidden_layer_sizes', [10])
                if isinstance(hidden_layer_sizes, list) and len(hidden_layer_sizes) == 1:
                    hidden_layer_sizes = tuple(hidden_layer_sizes)
                elif isinstance(hidden_layer_sizes, list):
                    hidden_layer_sizes = tuple(hidden_layer_sizes)
                
                # 根据样本数量调整神经网络参数
                max_iter = min(parameters.get('max_iter', 1000), max(200, n_samples * 10))
                
                return MLPRegressor(
                    hidden_layer_sizes=hidden_layer_sizes,
                    alpha=parameters.get('alpha', 0.01),
                    max_iter=max_iter,
                    random_state=42
                )
            else:
                logger.warning(f"未知的算法类型: {algorithm_type}")
                return None
                
        except Exception as e:
            logger.error(f"创建算法实例失败 ({algorithm_type}): {e}")
            return None
    
    def evaluate_algorithms(self):
        """评估所有启用的算法性能"""
        if not self.enabled_algorithms:
            logger.error("没有启用的算法可供评估")
            return None
        
        # 加载历史数据
        X, y = self.load_historical_data()
        if X is None or y is None:
            logger.error("无法加载历史数据")
            return None
        
        n_samples = len(X)
        if n_samples < 2:
            logger.error(f"样本数量不足 ({n_samples})，至少需要2个样本进行评估")
            return None
        
        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 选择合适的交叉验证方法
        if n_samples <= 10:
            # 样本少时使用留一法
            cv_method = LeaveOneOut()
            cv_name = "留一法交叉验证"
        else:
            # 样本多时使用k折交叉验证
            from sklearn.model_selection import KFold
            cv_method = KFold(n_splits=min(5, n_samples//2), shuffle=True, random_state=42)
            cv_name = "K折交叉验证"
        
        logger.info(f"使用 {cv_name}，样本数量: {n_samples}")
        
        results = {}
        
        for algorithm_type, config in self.enabled_algorithms.items():
            try:
                logger.info(f"正在评估算法: {config['name']} ({algorithm_type})")
                
                # 创建算法实例
                model = self.create_algorithm_instance(algorithm_type, config['parameters'], n_samples)
                if model is None:
                    continue
                
                # 执行交叉验证
                y_true = []
                y_pred = []
                
                for train_index, test_index in cv_method.split(X_scaled):
                    X_train, X_test = X_scaled[train_index], X_scaled[test_index]
                    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
                    
                    # 训练模型
                    model.fit(X_train, y_train)
                    
                    # 预测
                    pred = model.predict(X_test)
                    
                    y_true.extend(y_test.values)
                    y_pred.extend(pred)
                
                # 计算性能指标
                mae = mean_absolute_error(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                r2 = r2_score(y_true, y_pred)
                
                # 计算相对误差
                y_true_array = np.array(y_true)
                y_pred_array = np.array(y_pred)
                
                # 避免除零错误
                non_zero_mask = y_true_array != 0
                if np.any(non_zero_mask):
                    mape = np.mean(np.abs((y_true_array[non_zero_mask] - y_pred_array[non_zero_mask]) / y_true_array[non_zero_mask])) * 100
                else:
                    mape = 0
                
                results[algorithm_type] = {
                    'algorithm_name': config['name'],
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'mape': mape,
                    'y_true': y_true,
                    'y_pred': y_pred
                }
                
                logger.info(f"{config['name']} 评估完成: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")
                
            except Exception as e:
                logger.error(f"评估算法 {algorithm_type} 时出错: {e}")
                continue
        
        self.evaluation_results = results
        return results
    
    def get_comparison_summary(self):
        """获取性能对比汇总表"""
        if not self.evaluation_results:
            return []
        
        summary_data = []
        for algorithm_type, result in self.evaluation_results.items():
            summary_data.append({
                'algorithm_type': algorithm_type,
                'algorithm_name': result['algorithm_name'],
                'mae': round(result['mae'], 2),
                'rmse': round(result['rmse'], 2),
                'r2': round(result['r2'], 3),
                'mape': round(result['mape'], 2)
            })
        
        # 按R²值降序排列
        summary_data.sort(key=lambda x: x['r2'], reverse=True)
        return summary_data
    
    def get_best_algorithm(self):
        """获取表现最好的算法"""
        if not self.evaluation_results:
            return None, None
        
        best_algorithm = max(self.evaluation_results.items(), 
                           key=lambda x: x[1]['r2'])
        return best_algorithm[0], best_algorithm[1]