/*
 Navicat Premium Dump SQL

 Source Server         : local_database
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3306
 Source Schema         : dash_project

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 08/09/2025 15:19:11
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for algorithm_configs
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_configs`;
CREATE TABLE `algorithm_configs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `algorithm_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `algorithm_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `construction_mode` enum('steel_cage','steel_lining') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` enum('enabled','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'enabled',
  `application_scenario` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `model_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '参数最后修改时间',
  `parameters` json NULL COMMENT '当前算法参数配置',
  `parameter_ranges` json NULL COMMENT '参数范围和验证规则',
  `tuning_suggestions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '参数调优建议',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_algorithm_mode`(`algorithm_type` ASC, `construction_mode` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_configs
-- ----------------------------
INSERT INTO `algorithm_configs` VALUES (1, 'linear_regression', '线性回归', 'steel_cage', 'enabled', '在钢筋笼施工模式下，适用于塔吊租赁、钢筋生产线等成本要素的线性关系预测。通过正则化防止过拟合。', '基于钢筋笼施工的历史项目成本进行线性回归预测，主要针对塔吊租赁费、钢筋生产线费用、吊索具费用、套筒费用等核心成本要素。', '2025-08-07 18:01:57', '2025-08-15 18:12:11', '2025-08-15 18:12:11', '{\"cv\": 5, \"alphas_range\": [-3, 3, 11]}', '{\"cv\": {\"max\": 10, \"min\": 3, \"type\": \"integer\", \"default\": 5, \"description\": \"交叉验证折数，数据少用3-5折，数据多用5-10折\"}, \"alphas_range\": {\"max\": 6, \"min\": -6, \"type\": \"logspace_range\", \"default\": [-3, 3, 11], \"description\": \"正则化强度范围，值越大正则化越强，防止过拟合\"}}', '岭回归适合线性关系明显的工程数据。alphas值建议从小范围开始调试，观察验证误差变化。cv折数根据数据量调整。');
INSERT INTO `algorithm_configs` VALUES (2, 'neural_network', '神经网络', 'steel_cage', 'enabled', '在钢筋笼施工模式下，处理塔吊租赁与钢筋总吨数、套筒数量等复杂非线性关系。自动学习钢筋笼施工的成本模式。', '采用多层感知机学习钢筋笼施工中各成本要素的复杂交互关系，特别适合处理钢筋总吨数与各项费用的非线性映射。', '2025-08-07 18:01:57', '2025-08-15 16:43:47', '2025-08-15 16:43:47', '{\"alpha\": 0.01, \"max_iter\": 1000, \"hidden_layer_sizes\": [10]}', '{\"alpha\": {\"max\": 1.0, \"min\": 0.0001, \"type\": \"float\", \"default\": 0.01, \"description\": \"L2正则化，防止过拟合，小数据用大值(0.01-0.1)\"}, \"max_iter\": {\"max\": 5000, \"min\": 500, \"type\": \"integer\", \"default\": 1000, \"description\": \"最大迭代次数，收敛慢增加迭代次数，但避免过拟合\"}, \"hidden_layer_sizes\": {\"type\": \"array_select\", \"default\": [10], \"options\": [[5], [10], [5, 3], [10, 5]], \"description\": \"隐藏层结构，特征少用小网络，一般1-2层，每层3-20个神经元\"}}', '神经网络需要充足训练数据。隐藏层不宜过大，避免过拟合。alpha参数很重要，从0.01开始调试。如果loss不收敛可增加max_iter。');
INSERT INTO `algorithm_configs` VALUES (3, 'decision_tree', '决策树', 'steel_cage', 'enabled', '在钢筋笼施工模式下，提供清晰的成本决策规则。可以明确展示钢筋总吨数、套筒数量对总成本的影响路径。', '通过决策树分析钢筋笼施工中的成本决策逻辑，清晰展示不同工程量范围对应的成本预测规则。', '2025-08-07 18:01:57', '2025-08-15 16:43:17', '2025-08-15 16:43:17', '{\"max_depth\": 4, \"min_samples_leaf\": 3, \"min_samples_split\": 6}', '{\"max_depth\": {\"max\": 10, \"min\": 2, \"type\": \"integer\", \"default\": 4, \"description\": \"最大深度，深度过大易过拟合，工程数据建议3-6\"}, \"min_samples_leaf\": {\"max\": 10, \"min\": 1, \"type\": \"integer\", \"default\": 3, \"description\": \"叶子节点最小样本数，值越大模型越简单，小数据集用2-5\"}, \"min_samples_split\": {\"max\": 20, \"min\": 2, \"type\": \"integer\", \"default\": 6, \"description\": \"分裂最小样本数，应≥2倍min_samples_leaf\"}}', '决策树容易过拟合，建议从较小的max_depth开始。min_samples_split应该是min_samples_leaf的2倍以上。工程数据特征不多时，深度控制在3-6较好。');
INSERT INTO `algorithm_configs` VALUES (4, 'random_forest', '随机森林', 'steel_cage', 'enabled', '在钢筋笼施工模式下，集成多个决策树提高预测稳定性。对钢筋笼施工数据的异常值具有较强鲁棒性。', '采用随机森林算法集成多个钢筋笼施工成本决策树，通过bootstrap抽样提升对钢筋笼项目成本预测的准确性。', '2025-08-07 18:01:57', '2025-08-15 16:43:27', '2025-08-15 16:43:27', '{\"max_depth\": 6, \"max_features\": \"sqrt\", \"n_estimators\": 80}', '{\"max_depth\": {\"max\": 15, \"min\": 3, \"type\": \"integer\", \"default\": 6, \"description\": \"最大深度，比单棵树可以更深，工程数据建议5-10\"}, \"max_features\": {\"type\": \"select\", \"default\": \"sqrt\", \"options\": [\"sqrt\", \"log2\", \"auto\"], \"description\": \"sqrt适合回归，auto使用全部特征\"}, \"n_estimators\": {\"max\": 200, \"min\": 10, \"type\": \"integer\", \"default\": 80, \"description\": \"树的数量，更多树通常更好但计算慢，工程数据建议50-100\"}}', '随机森林对参数不敏感，但n_estimators太少会欠拟合，太多计算慢。max_features使用sqrt通常效果好。工程数据建议先用默认参数测试效果。');
INSERT INTO `algorithm_configs` VALUES (5, 'svm', '支持向量机', 'steel_cage', 'enabled', '在钢筋笼施工模式下，通过核函数处理钢筋笼成本的复杂非线性关系。适合中小规模钢筋笼项目数据。', '使用支持向量回归处理钢筋笼施工成本预测，通过径向基核函数学习钢筋总吨数等特征与成本的复杂映射关系。', '2025-08-07 18:01:57', '2025-08-15 16:43:37', '2025-08-15 16:43:37', '{\"C\": 1.0, \"kernel\": \"rbf\", \"epsilon\": 0.1}', '{\"C\": {\"max\": 100, \"min\": 0.01, \"type\": \"float\", \"default\": 1.0, \"description\": \"正则化参数，值越大对误差容忍度越小，易过拟合\"}, \"kernel\": {\"type\": \"select\", \"default\": \"rbf\", \"options\": [\"linear\", \"rbf\", \"poly\"], \"description\": \"linear适合线性关系，rbf适合非线性，poly适合多项式关系\"}, \"epsilon\": {\"max\": 1.0, \"min\": 0.01, \"type\": \"float\", \"default\": 0.1, \"description\": \"损失函数参数，容忍误差范围，值越大模型越简单\"}}', 'SVR对数据缩放敏感，建议先标准化数据。C参数从1.0开始调试，kernel选择根据数据分布，工程数据通常rbf效果好。');
INSERT INTO `algorithm_configs` VALUES (6, 'linear_regression', '线性回归', 'steel_lining', 'enabled', '在钢衬里施工模式下，适用于拼装场地、制作胎具等费用的线性关系预测。处理钢衬里施工的多重共线性问题。', '基于钢衬里施工的历史项目进行线性回归预测，主要针对拼装场地费用、制作胎具费用、钢支墩埋件费用等核心成本。', '2025-08-07 18:02:06', '2025-08-16 16:35:19', '2025-08-16 16:35:19', '{\"cv\": 5, \"alphas_range\": [-3, 3, 11]}', '{\"cv\": {\"max\": 10, \"min\": 3, \"type\": \"integer\", \"default\": 5, \"description\": \"交叉验证折数，数据少用3-5折，数据多用5-10折\"}, \"alphas_range\": {\"max\": 6, \"min\": -6, \"type\": \"logspace_range\", \"default\": [-3, 3, 11], \"description\": \"正则化强度范围，值越大正则化越强，防止过拟合\"}}', '岭回归适合线性关系明显的工程数据。alphas值建议从小范围开始调试，观察验证误差变化。cv折数根据数据量调整。');
INSERT INTO `algorithm_configs` VALUES (7, 'neural_network', '神经网络', 'steel_lining', 'enabled', '在钢衬里施工模式下，学习拼装场地工程量与各项费用的复杂非线性关系。自动提取钢衬里施工特征。', '采用深度学习处理钢衬里施工的复杂成本模式，特别适合拼装场地总工程量、制作胎具总工程量等特征的非线性建模。', '2025-08-07 18:02:06', '2025-08-15 17:44:32', '2025-08-15 17:44:32', '{\"alpha\": 0.01, \"max_iter\": 1000, \"hidden_layer_sizes\": [10]}', '{\"alpha\": {\"max\": 1.0, \"min\": 0.0001, \"type\": \"float\", \"default\": 0.01, \"description\": \"L2正则化，防止过拟合，小数据用大值(0.01-0.1)\"}, \"max_iter\": {\"max\": 5000, \"min\": 500, \"type\": \"integer\", \"default\": 1000, \"description\": \"最大迭代次数，收敛慢增加迭代次数，但避免过拟合\"}, \"hidden_layer_sizes\": {\"type\": \"array_select\", \"default\": [10], \"options\": [[5], [10], [5, 3], [10, 5]], \"description\": \"隐藏层结构，特征少用小网络，一般1-2层，每层3-20个神经元\"}}', '神经网络需要充足训练数据。隐藏层不宜过大，避免过拟合。alpha参数很重要，从0.01开始调试。如果loss不收敛可增加max_iter。');
INSERT INTO `algorithm_configs` VALUES (8, 'decision_tree', '决策树', 'steel_lining', 'enabled', '在钢衬里施工模式下，提供钢衬里成本的可解释决策规则。清晰展示工程量对钢网架、扶壁柱等费用的影响。', '通过决策树分析钢衬里施工的成本构成逻辑，明确不同拼装场地规模对各项费用的决策边界。', '2025-08-07 18:02:06', '2025-08-16 16:30:47', '2025-08-16 16:30:47', '{\"max_depth\": 4, \"min_samples_leaf\": 3, \"min_samples_split\": 6}', '{\"max_depth\": {\"max\": 10, \"min\": 2, \"type\": \"integer\", \"default\": 4, \"description\": \"最大深度，深度过大易过拟合，工程数据建议3-6\"}, \"min_samples_leaf\": {\"max\": 10, \"min\": 1, \"type\": \"integer\", \"default\": 3, \"description\": \"叶子节点最小样本数，值越大模型越简单，小数据集用2-5\"}, \"min_samples_split\": {\"max\": 20, \"min\": 2, \"type\": \"integer\", \"default\": 6, \"description\": \"分裂最小样本数，应≥2倍min_samples_leaf\"}}', '决策树容易过拟合，建议从较小的max_depth开始。min_samples_split应该是min_samples_leaf的2倍以上。工程数据特征不多时，深度控制在3-6较好。');
INSERT INTO `algorithm_configs` VALUES (9, 'random_forest', '随机森林', 'steel_lining', 'enabled', '在钢衬里施工模式下，集成多树算法提高钢衬里成本预测稳定性。处理钢衬里施工数据噪声。', '采用随机森林集成学习钢衬里施工成本，通过多个决策树投票提升走道板、操作平台等复杂费用的预测精度。', '2025-08-07 18:02:06', '2025-08-16 16:30:50', '2025-08-16 16:30:50', '{\"max_depth\": 6, \"max_features\": \"sqrt\", \"n_estimators\": 80}', '{\"max_depth\": {\"max\": 15, \"min\": 3, \"type\": \"integer\", \"default\": 6, \"description\": \"最大深度，比单棵树可以更深，工程数据建议5-10\"}, \"max_features\": {\"type\": \"select\", \"default\": \"sqrt\", \"options\": [\"sqrt\", \"log2\", \"auto\"], \"description\": \"sqrt适合回归，auto使用全部特征\"}, \"n_estimators\": {\"max\": 200, \"min\": 10, \"type\": \"integer\", \"default\": 80, \"description\": \"树的数量，更多树通常更好但计算慢，工程数据建议50-100\"}}', '随机森林对参数不敏感，但n_estimators太少会欠拟合，太多计算慢。max_features使用sqrt通常效果好。工程数据建议先用默认参数测试效果。');
INSERT INTO `algorithm_configs` VALUES (10, 'svm', '支持向量机', 'steel_lining', 'enabled', '在钢衬里施工模式下，通过核映射处理钢衬里成本的高维复杂关系。适合钢衬里项目的精确预测。', '使用支持向量回归建模钢衬里施工成本，通过非线性核函数学习拼装场地等核心特征与总成本的映射关系。', '2025-08-07 18:02:06', '2025-08-16 16:35:13', '2025-08-16 16:35:13', '{\"C\": 1.0, \"kernel\": \"rbf\", \"epsilon\": 0.1}', '{\"C\": {\"max\": 100, \"min\": 0.01, \"type\": \"float\", \"default\": 1.0, \"description\": \"正则化参数，值越大对误差容忍度越小，易过拟合\"}, \"kernel\": {\"type\": \"select\", \"default\": \"rbf\", \"options\": [\"linear\", \"rbf\", \"poly\"], \"description\": \"linear适合线性关系，rbf适合非线性，poly适合多项式关系\"}, \"epsilon\": {\"max\": 1.0, \"min\": 0.01, \"type\": \"float\", \"default\": 0.1, \"description\": \"损失函数参数，容忍误差范围，值越大模型越简单\"}}', 'SVR对数据缩放敏感，建议先标准化数据。C参数从1.0开始调试，kernel选择根据数据分布，工程数据通常rbf效果好。');

-- ----------------------------
-- Table structure for algorithm_parameters
-- ----------------------------
DROP TABLE IF EXISTS `algorithm_parameters`;
CREATE TABLE `algorithm_parameters`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `algorithm_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '算法中文名称',
  `algorithm_name_en` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '算法英文名称',
  `algorithm_class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '算法类别',
  `parameter_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '参数名称',
  `parameter_name_cn` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '参数中文名称',
  `current_value` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '当前值',
  `suggested_range` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '建议范围',
  `adjustment_tips` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '调整提示',
  `parameter_type` enum('continuous','discrete','categorical') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '参数类型',
  `priority` enum('high','medium','low') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'medium' COMMENT '调参优先级',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_algorithm_name`(`algorithm_name` ASC) USING BTREE,
  INDEX `idx_parameter_name`(`parameter_name` ASC) USING BTREE,
  INDEX `idx_priority`(`priority` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of algorithm_parameters
-- ----------------------------
INSERT INTO `algorithm_parameters` VALUES (1, '岭回归', 'RidgeCV', 'linear_regression', 'alphas', '正则化强度范围', 'np.logspace(-3, 4, 14)', 'np.logspace(-3, 3, 11)', '值越大正则化越强，防止过拟合；值越小模型越复杂', 'continuous', 'high', '2025-08-15 23:07:36', '2025-08-16 16:42:37');
INSERT INTO `algorithm_parameters` VALUES (2, '岭回归', 'RidgeCV', 'linear_regression', 'cv', '交叉验证折数', '7', '3-10', '数据少用3-5折，数据多用5-10折', 'discrete', 'medium', '2025-08-15 23:07:36', '2025-08-16 16:42:37');
INSERT INTO `algorithm_parameters` VALUES (3, '决策树', 'DecisionTreeRegressor', 'tree_based', 'max_depth', '最大深度', '4', '2-10', '深度过大易过拟合，过小易欠拟合。工程数据建议3-6', 'discrete', 'high', '2025-08-15 23:07:46', '2025-08-16 16:33:07');
INSERT INTO `algorithm_parameters` VALUES (4, '决策树', 'DecisionTreeRegressor', 'tree_based', 'min_samples_leaf', '叶子节点最小样本数', '7', '1-10', '值越大模型越简单，防止过拟合。小数据集用2-5', 'discrete', 'high', '2025-08-15 23:07:46', '2025-08-16 16:33:07');
INSERT INTO `algorithm_parameters` VALUES (5, '决策树', 'DecisionTreeRegressor', 'tree_based', 'min_samples_split', '分裂最小样本数', '5', '2-20', '应≥2倍min_samples_leaf，控制节点分裂条件', 'discrete', 'medium', '2025-08-15 23:07:47', '2025-08-16 16:33:07');
INSERT INTO `algorithm_parameters` VALUES (6, '随机森林', 'RandomForestRegressor', 'ensemble', 'n_estimators', '树的数量', '12', '10-200', '更多树通常更好但计算慢。工程数据建议50-100', 'discrete', 'high', '2025-08-15 23:08:07', '2025-08-16 16:31:49');
INSERT INTO `algorithm_parameters` VALUES (7, '随机森林', 'RandomForestRegressor', 'ensemble', 'max_depth', '最大深度', '3', '3-15', '比单棵树可以更深。工程数据建议5-10', 'discrete', 'high', '2025-08-15 23:08:07', '2025-08-16 16:31:49');
INSERT INTO `algorithm_parameters` VALUES (8, '随机森林', 'RandomForestRegressor', 'ensemble', 'max_features', '特征采样比例', 'sqrt', 'sqrt, log2, 0.3-1.0', 'sqrt适合回归，0.5-0.8适合特征多的情况', 'categorical', 'medium', '2025-08-15 23:08:09', '2025-08-16 16:31:49');
INSERT INTO `algorithm_parameters` VALUES (9, '支持向量回归', 'SVR', 'kernel_method', 'C', '正则化参数', '0.3', '0.01-100', '值越大对误差容忍度越小，易过拟合。建议0.1-10', 'continuous', 'high', '2025-08-15 23:08:18', '2025-08-16 14:19:07');
INSERT INTO `algorithm_parameters` VALUES (10, '支持向量回归', 'SVR', 'kernel_method', 'kernel', '核函数类型', 'rbf', 'linear, rbf, poly', 'linear适合线性关系，rbf适合非线性，poly适合多项式关系', 'categorical', 'high', '2025-08-15 23:08:19', '2025-08-16 14:19:07');
INSERT INTO `algorithm_parameters` VALUES (11, '支持向量回归', 'SVR', 'kernel_method', 'epsilon', '损失函数参数', '0.4', '0.01-1.0', '容忍误差范围，值越大模型越简单', 'continuous', 'medium', '2025-08-15 23:08:19', '2025-08-16 14:19:07');
INSERT INTO `algorithm_parameters` VALUES (12, '神经网络', 'MLPRegressor', 'neural_network', 'hidden_layer_sizes', '隐藏层结构', '(4,4)', '(5,), (10,), (5,3), (10,5)', '特征少用小网络，一般1-2层，每层3-20个神经元', 'categorical', 'high', '2025-08-15 23:08:30', '2025-08-16 16:29:39');
INSERT INTO `algorithm_parameters` VALUES (13, '神经网络', 'MLPRegressor', 'neural_network', 'alpha', 'L2正则化', '0.06', '0.0001-1.0', '防止过拟合，小数据用大值(0.01-0.1)', 'continuous', 'high', '2025-08-15 23:08:30', '2025-08-16 16:29:38');
INSERT INTO `algorithm_parameters` VALUES (14, '神经网络', 'MLPRegressor', 'neural_network', 'max_iter', '最大迭代次数', '2333', '500-5000', '收敛慢增加迭代次数，但避免过拟合', 'discrete', 'medium', '2025-08-15 23:08:31', '2025-08-16 16:29:39');

-- ----------------------------
-- Table structure for basic_indicators
-- ----------------------------
DROP TABLE IF EXISTS `basic_indicators`;
CREATE TABLE `basic_indicators`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指标编码',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指标名称',
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '分类',
  `unit` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '单位',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '说明',
  `status` enum('enabled','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'enabled' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `code`(`code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 403 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '基础指标表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of basic_indicators
-- ----------------------------
INSERT INTO `basic_indicators` VALUES (1, 'GJL-JI-01', '塔吊租赁单价', '机械费', '元/台班', '对应您的 \"1. 塔吊租赁费\"34345', 'enabled', '2025-08-02 21:50:19', '2025-08-07 23:26:26');
INSERT INTO `basic_indicators` VALUES (2, 'GJL-JI-02', '钢筋生产线单价', '机械费', '元/套', '对应您的 \"2. 钢筋生产线费用\"', 'enabled', '2025-08-02 21:50:19', '2025-08-05 14:56:33');
INSERT INTO `basic_indicators` VALUES (3, 'GJL-CAI-01', '吊索具综合单价', '材料费', '元/套', '对应您的 \"3. 吊索具数量\"', 'enabled', '2025-08-02 21:50:19', '2025-08-05 14:56:35');
INSERT INTO `basic_indicators` VALUES (4, 'GJL-CAI-02', '套筒综合单价', '材料费', '元/个', '对应您的 \"4. 套筒数量\"', 'enabled', '2025-08-02 21:50:19', '2025-08-05 16:46:56');
INSERT INTO `basic_indicators` VALUES (5, 'GJL-CAI-03', '钢筋综合单价', '材料费', '元/吨', '对应您的 \"5. 钢筋吨数\"', 'enabled', '2025-08-02 21:50:19', '2025-08-05 16:47:02');
INSERT INTO `basic_indicators` VALUES (100, 'GCL-CAI-01', '拼装场地综合单价', '措施费', '元/m', '对应您的 \"1. 拼装场地工程量\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:12');
INSERT INTO `basic_indicators` VALUES (101, 'GCL-CAI-02', '制作胎具综合单价', '材料费', '元/套', '对应您的 \"2. 制作胎具\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:18');
INSERT INTO `basic_indicators` VALUES (102, 'GCL-CAI-03', '钢支墩及埋件综合单价', '材料费', '元/吨', '对应您的 \"3. 钢支墩、埋件\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:24');
INSERT INTO `basic_indicators` VALUES (103, 'GCL-CAI-04', '扶壁柱综合单价', '材料费', '元/吨', '对应您的 \"4. 扶壁柱\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:30');
INSERT INTO `basic_indicators` VALUES (104, 'GCL-CAI-05', '走道板及平台综合单价', '材料费', '元/吨', '对应您的 \"5. 走道板及操作平台\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:35');
INSERT INTO `basic_indicators` VALUES (105, 'GCL-CAI-06', '钢网梁综合单价', '材料费', '元/吨', '对应您的 \"6. 钢网梁\"', 'enabled', '2025-08-02 21:50:32', '2025-08-05 16:47:42');
INSERT INTO `basic_indicators` VALUES (200, 'FEI-01', '措施费率', '措施费', '%', '适用于所有模式的通用费用', 'enabled', '2025-08-02 21:50:39', '2025-08-05 14:58:45');

-- ----------------------------
-- Table structure for calculation_results
-- ----------------------------
DROP TABLE IF EXISTS `calculation_results`;
CREATE TABLE `calculation_results`  (
  `project_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `construction_mode` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `result_data` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `direct_labor_cost` double NULL DEFAULT NULL,
  `direct_material_cost` double NULL DEFAULT NULL,
  `direct_machinery_cost` double NULL DEFAULT NULL,
  `direct_indirect_cost` double NULL DEFAULT NULL,
  `direct_total` double NULL DEFAULT NULL,
  `modular_labor_cost` double NULL DEFAULT NULL,
  `modular_material_cost` double NULL DEFAULT NULL,
  `modular_machinery_cost` double NULL DEFAULT NULL,
  `modular_indirect_cost` double NULL DEFAULT NULL,
  `modular_total` double NULL DEFAULT NULL,
  `cost_difference` double NULL DEFAULT NULL,
  `cost_difference_percentage` double NULL DEFAULT NULL,
  `calculation_time` time NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of calculation_results
-- ----------------------------
INSERT INTO `calculation_results` VALUES ('1001', ' 钢筋笼施工模式 ', '{\"直接施工\": {\"人工费\": 248408.96, \"材料费\": 482131.98, \"机械费\": 240678.96, \"间接费用\": 23.0, \"总计\": 972369.9}, \"模块化施工\": {\"人工费\": 1313208.24, \"材料费\": 1315364.19, \"机械费\": 756547.74, \"间接费用\": 245.0, \"总计\": 3397370.17}, \"差异\": {\"成本差异\": 2425000.27, \"成本差异百分比\": 249.39071746256235}}', 248408.96, 482131.98, 240678.96, 23, 972369.9, 1313208.24, 1315364.19, 756547.74, 245, 3397370.17, 2425000.27, 249.39071746256235, NULL);
INSERT INTO `calculation_results` VALUES ('1002', ' 钢筋笼+钢覆面施工模式 ', '{\"直接施工\": {\"人工费\": 10570.0, \"材料费\": 2902.14, \"机械费\": 0.0, \"间接费用\": 3456.0, \"总计\": 210464.14}, \"模块化施工\": {\"人工费\": 103149.16, \"材料费\": 346089.28, \"机械费\": 3514.85, \"间接费用\": 2457.0, \"总计\": 592802.29}, \"差异\": {\"成本差异\": 382338.15, \"成本差异百分比\": 181.66427306808657}}', 10570, 2902.14, 0, 3456, 210464.14, 103149.16, 346089.28, 3514.85, 2457, 592802.29, 382338.15, 181.66427306808657, NULL);
INSERT INTO `calculation_results` VALUES ('1003', ' 设备室顶板复合板模式 ', '{\"直接施工\": {\"人工费\": 26248.0, \"材料费\": 102.2, \"机械费\": 30.0, \"间接费用\": 465.0, \"总计\": 35680.2}, \"模块化施工\": {\"人工费\": 411510.0, \"材料费\": 48053.42, \"机械费\": 2204.92, \"间接费用\": 347.0, \"总计\": 468708.34}, \"差异\": {\"成本差异\": 433028.14, \"成本差异百分比\": 1213.6370872360583}}', 26248, 102.2, 30, 465, 35680.2, 411510, 48053.42, 2204.92, 347, 468708.34, 433028.14, 1213.6370872360583, NULL);
INSERT INTO `calculation_results` VALUES ('1004', ' 管廊叠合板模式 ', '{\"直接施工\": {\"人工费\": 43834.0, \"材料费\": 130355.0, \"机械费\": 1084630.64, \"间接费用\": 23.0, \"总计\": 1259256.6400000001}, \"模块化施工\": {\"人工费\": 360711.32, \"材料费\": 526762.27, \"机械费\": 88404.8, \"间接费用\": 245.0, \"总计\": 980533.39}, \"差异\": {\"成本差异\": -278723.2500000001, \"成本差异百分比\": -22.133951185677297}}', 43834, 130355, 1084630.64, 23, 1259256.6400000001, 360711.32, 526762.27, 88404.8, 245, 980533.39, -278723.2500000001, -22.133951185677297, NULL);
INSERT INTO `calculation_results` VALUES ('1006', '钢衬里施工模式', '{\"直接施工\": {\"人工费\": 102360495.94, \"材料费\": 34958527.16, \"机械费\": 20256919.08, \"间接费用\": 0.0, \"总计\": 157575942.18}, \"模块化施工\": {\"人工费\": 81888396.75, \"材料费\": 38454379.88, \"机械费\": 18231227.17, \"间接费用\": 0.0, \"总计\": 138574003.8}, \"差异\": {\"成本差异\": -19001938.379999995, \"成本差异百分比\": -12.058908306125792}}', 102360495.94, 34958527.16, 20256919.08, 0, 157575942.18, 81888396.75, 38454379.88, 18231227.17, 0, 138574003.8, -19001938.379999995, -12.058908306125792, NULL);

-- ----------------------------
-- Table structure for composite_indicators
-- ----------------------------
DROP TABLE IF EXISTS `composite_indicators`;
CREATE TABLE `composite_indicators`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID，自动递增',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '指标编码，如FU-GJL-TDCB',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '指标名称',
  `construction_mode` enum('steel_cage','steel_lining') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `unit` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '单位',
  `formula` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '计算公式',
  `calculation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'custom' COMMENT '计算类型',
  `dependencies` json NULL COMMENT '依赖关系JSON',
  `result_cache` decimal(15, 4) NULL DEFAULT NULL COMMENT '结果缓存',
  `cache_timestamp` timestamp NULL DEFAULT NULL COMMENT '缓存时间',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '说明',
  `status` enum('enabled','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'enabled' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `code`(`code` ASC) USING BTREE,
  INDEX `idx_construction_mode`(`construction_mode` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 200 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of composite_indicators
-- ----------------------------
INSERT INTO `composite_indicators` VALUES (1, 'FU-GJL-TDCB', '成本_塔吊租赁', 'steel_cage', '元', 'QTY_塔吊 * {GJL-JI-01}', 'product', '{\"basic_indicators\": [{\"code\": \"GJL-JI-01\", \"name\": \"塔吊租赁单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_塔吊\", \"name\": \"塔吊租赁工程量\", \"type\": \"quantity\", \"unit\": \"台班\"}]}', NULL, NULL, '将用户输入的\"塔吊租赁工程量\"乘以\"塔吊租赁单价\"，得到总费用。这是AI模型的第一个输入特征。', 'enabled', '2025-08-05 16:01:29', '2025-08-06 16:12:38');
INSERT INTO `composite_indicators` VALUES (2, 'FU-GJL-GJSCX', '成本_钢筋生产线', 'steel_cage', '元', 'QTY_钢筋 * {GJL-CAI-03}', 'product', '{\"basic_indicators\": [{\"code\": \"GJL-CAI-03\", \"name\": \"钢筋综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_钢筋\", \"name\": \"钢筋吨数\", \"type\": \"quantity\", \"unit\": \"吨\"}]}', NULL, NULL, '将用户输入的\"钢筋吨数\"乘以\"钢筋综合单价\"，得到总费用。这是AI模型的第二个输入特征。', 'enabled', '2025-08-05 16:01:29', '2025-08-05 18:23:12');
INSERT INTO `composite_indicators` VALUES (3, 'FU-GJL-DSJ', '成本_吊索具', 'steel_cage', '元', 'QTY_吊索具 * {GJL-CAI-01}', 'product', '{\"basic_indicators\": [{\"code\": \"GJL-CAI-01\", \"name\": \"吊索具综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_吊索具\", \"name\": \"吊索具数量\", \"type\": \"quantity\", \"unit\": \"套\"}]}', NULL, NULL, '将用户输入的\"吊索具数量\"乘以\"吊索具综合单价\"，得到总费用。这是AI模型的第三个输入特征。', 'enabled', '2025-08-05 16:01:29', '2025-08-05 18:05:26');
INSERT INTO `composite_indicators` VALUES (4, 'FU-GJL-TT', '成本_套筒', 'steel_cage', '元', 'QTY_套筒 * {GJL-CAI-02}', 'product', '{\"basic_indicators\": [{\"code\": \"GJL-CAI-02\", \"name\": \"套筒综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_套筒\", \"name\": \"套筒数量\", \"type\": \"quantity\", \"unit\": \"个\"}]}', NULL, NULL, '将用户输入的\"套筒数量\"乘以\"套筒综合单价\"，得到总费用。这是AI模型的第四个输入特征。', 'disabled', '2025-08-05 16:01:29', '2025-08-05 17:40:25');
INSERT INTO `composite_indicators` VALUES (99, 'FU-GJL-CORE-COSTS', '钢筋笼-核心成本合计', 'steel_cage', '元', '{FU-GJL-TDCB} + {FU-GJL-GJSCX} + {FU-GJL-DSJ} + {FU-GJL-TT}', 'sum', '{\"composite_indicators\": [{\"code\": \"FU-GJL-TDCB\", \"name\": \"成本_塔吊租赁\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GJL-GJSCX\", \"name\": \"成本_钢筋生产线\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GJL-DSJ\", \"name\": \"成本_吊索具\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GJL-TT\", \"name\": \"成本_套筒\", \"operation\": \"+\", \"coefficient\": 1.0}]}', NULL, NULL, '将上述四个核心成本相加，这个值是\"比率法\"计算的基础分子。', 'enabled', '2025-08-05 16:01:29', '2025-08-05 16:05:11');
INSERT INTO `composite_indicators` VALUES (101, 'FU-GCL-ZZTJ', '成本_制作胎具', 'steel_lining', '元', 'QTY_胎具 * {GCL-CAI-02}', 'product', '{\"basic_indicators\": [{\"code\": \"GCL-CAI-02\", \"name\": \"制作胎具综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_胎具\", \"name\": \"制作胎具工程量\", \"type\": \"quantity\", \"unit\": \"套\"}]}', NULL, NULL, '将用户输入的\"制作胎具\"工程量乘以对应的\"综合单价\"。', 'enabled', '2025-08-05 16:05:30', '2025-08-05 16:05:30');
INSERT INTO `composite_indicators` VALUES (102, 'FU-GCL-GZD', '成本_钢支墩及埋件', 'steel_lining', '元', 'QTY_钢支墩 * {GCL-CAI-03}', 'product', '{\"basic_indicators\": [{\"code\": \"GCL-CAI-03\", \"name\": \"钢支墩及埋件综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_钢支墩\", \"name\": \"钢支墩、埋件工程量\", \"type\": \"quantity\", \"unit\": \"吨\"}]}', NULL, NULL, '将用户输入的\"钢支墩、埋件\"工程量乘以对应的\"综合单价\"。', 'enabled', '2025-08-05 16:05:30', '2025-08-05 16:05:30');
INSERT INTO `composite_indicators` VALUES (103, 'FU-GCL-FBZ', '成本_扶壁柱', 'steel_lining', '元', 'QTY_扶壁柱 * {GCL-CAI-04}', 'product', '{\"basic_indicators\": [{\"code\": \"GCL-CAI-04\", \"name\": \"扶壁柱综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_扶壁柱\", \"name\": \"扶壁柱工程量\", \"type\": \"quantity\", \"unit\": \"吨\"}]}', NULL, NULL, '将用户输入的\"扶壁柱\"工程量乘以对应的\"综合单价\"。', 'enabled', '2025-08-05 16:05:30', '2025-08-05 16:05:30');
INSERT INTO `composite_indicators` VALUES (104, 'FU-GCL-ZDB', '成本_走道板及平台', 'steel_lining', '元', 'QTY_走道板 * {GCL-CAI-05}', 'product', '{\"basic_indicators\": [{\"code\": \"GCL-CAI-05\", \"name\": \"走道板及平台综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_走道板\", \"name\": \"走道板及操作平台工程量\", \"type\": \"quantity\", \"unit\": \"吨\"}]}', NULL, NULL, '将用户输入的\"走道板及操作平台\"工程量乘以对应的\"综合单价\"。', 'disabled', '2025-08-05 16:05:30', '2025-08-05 17:40:25');
INSERT INTO `composite_indicators` VALUES (105, 'FU-GCL-GWL', '成本_钢网梁', 'steel_lining', '元', 'QTY_钢网梁 * {GCL-CAI-06}', 'product', '{\"basic_indicators\": [{\"code\": \"GCL-CAI-06\", \"name\": \"钢网梁综合单价\", \"operation\": \"*\", \"coefficient\": 1.0}], \"input_parameters\": [{\"code\": \"QTY_钢网梁\", \"name\": \"钢网梁工程量\", \"type\": \"quantity\", \"unit\": \"吨\"}]}', NULL, NULL, '将用户输入的\"钢网梁\"工程量乘以对应的\"综合单价\"。', 'enabled', '2025-08-05 16:05:30', '2025-08-05 16:05:30');
INSERT INTO `composite_indicators` VALUES (199, 'FU-GCL-CORE-COSTS', '钢衬里-核心成本合计', 'steel_lining', '元', '{FU-GCL-PZCD} + {FU-GCL-ZZTJ} + {FU-GCL-GZD} + {FU-GCL-FBZ} + {FU-GCL-ZDB} + {FU-GCL-GWL}', 'sum', '{\"composite_indicators\": [{\"code\": \"FU-GCL-PZCD\", \"name\": \"成本_拼装场地\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GCL-ZZTJ\", \"name\": \"成本_制作胎具\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GCL-GZD\", \"name\": \"成本_钢支墩及埋件\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GCL-FBZ\", \"name\": \"成本_扶壁柱\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GCL-ZDB\", \"name\": \"成本_走道板及平台\", \"operation\": \"+\", \"coefficient\": 1.0}, {\"code\": \"FU-GCL-GWL\", \"name\": \"成本_钢网梁\", \"operation\": \"+\", \"coefficient\": 1.0}]}', NULL, NULL, '将钢衬里模式的所有核心成本相加。', 'enabled', '2025-08-05 16:05:30', '2025-08-05 16:05:30');

-- ----------------------------
-- Table structure for comprehensive_indicators
-- ----------------------------
DROP TABLE IF EXISTS `comprehensive_indicators`;
CREATE TABLE `comprehensive_indicators`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `construction_mode` enum('steel_cage','steel_lining') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `calculation_method` enum('ml_prediction','ratio_method') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `indicator_type` enum('raw_value','final_value') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `calculation_logic` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `dependencies` json NULL,
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `status` enum('enabled','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'enabled',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `code`(`code` ASC) USING BTREE,
  INDEX `idx_construction_mode`(`construction_mode` ASC) USING BTREE,
  INDEX `idx_calculation_method`(`calculation_method` ASC) USING BTREE,
  INDEX `idx_indicator_type`(`indicator_type` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 104 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of comprehensive_indicators
-- ----------------------------
INSERT INTO `comprehensive_indicators` VALUES (1, 'FU-ZJ-ML-RAW', '项目总造价(AI预测-原始值)', 'steel_cage', 'ml_prediction', 'raw_value', 'CALL ML_Model_GJL({FU-GJL-CORE-COSTS})', '{}', '元', '调用钢筋笼AI模型，传入其核心成本，得到原始预测值', 'enabled', '2025-08-06 17:49:48', '2025-08-11 11:05:15');
INSERT INTO `comprehensive_indicators` VALUES (2, 'FU-ZJ-RATIO-RAW', '项目总造价(比率法-原始值)', 'steel_cage', 'ratio_method', 'raw_value', '{FU-GJL-CORE-COSTS} / RULE(avg_core_cost_ratio_GJL)', '{}', '元', '使用钢筋笼核心成本合计除以钢筋笼的历史成本占比', 'enabled', '2025-08-06 17:49:48', '2025-08-08 17:48:47');
INSERT INTO `comprehensive_indicators` VALUES (3, 'FU-ZJ-ML-FINAL', '项目总造价(AI预测-最终)', 'steel_cage', 'ml_prediction', 'final_value', '{FU-ZJ-ML-RAW} + INPUT_措施费', '{}', '元', '将AI预测原始值加上措施费', 'enabled', '2025-08-06 17:49:48', '2025-08-08 22:51:36');
INSERT INTO `comprehensive_indicators` VALUES (4, 'FU-ZJ-RATIO-FINAL', '项目总造价(比率法-最终)', 'steel_cage', 'ratio_method', 'final_value', '{FU-ZJ-RATIO-RAW} + INPUT_措施费', '{}', '元', '将比率法原始值加上措施费', 'enabled', '2025-08-06 17:49:48', '2025-08-08 22:51:41');
INSERT INTO `comprehensive_indicators` VALUES (100, 'FU-ZJ-GCL-ML-RAW', '项目总造价(AI预测-原始值)', 'steel_lining', 'ml_prediction', 'raw_value', 'CALL ML_Model_GCL({FU-GCL-CORE-COSTS})', '{}', '元', '调用钢衬里AI模型，传入其核心成本，得到原始预测值', 'enabled', '2025-08-06 17:49:48', '2025-08-06 19:55:32');
INSERT INTO `comprehensive_indicators` VALUES (101, 'FU-ZJ-GCL-RATIO-RAW', '项目总造价(比率法-原始值)', 'steel_lining', 'ratio_method', 'raw_value', '{FU-GCL-CORE-COSTS} / RULE(avg_core_cost_ratio_GCL)', '{}', '元', '使用钢衬里核心成本合计除以钢衬里的历史成本占比', 'enabled', '2025-08-06 17:49:48', '2025-08-16 16:27:55');
INSERT INTO `comprehensive_indicators` VALUES (102, 'FU-ZJ-GCL-ML-FINAL', '项目总造价(AI预测-最终)', 'steel_lining', 'ml_prediction', 'final_value', '{FU-ZJ-GCL-ML-RAW} + INPUT_措施费', '{}', '元', '将钢衬里AI预测原始值加上措施费', 'enabled', '2025-08-06 17:49:48', '2025-08-08 22:51:26');
INSERT INTO `comprehensive_indicators` VALUES (103, 'FU-ZJ-GCL-RATIO-FINAL', '项目总造价(比率法-最终)', 'steel_lining', 'ratio_method', 'final_value', '{FU-ZJ-GCL-RATIO-RAW} + INPUT_措施费', '{\"input_parameters\": [\"措施费\"], \"comprehensive_indicators\": [\"FU-ZJ-GCL-RATIO-RAW\"]}', '元', '将钢衬里比率法原始值加上措施费', 'enabled', '2025-08-06 17:49:48', '2025-08-06 17:49:48');

-- ----------------------------
-- Table structure for construction_parameter_table
-- ----------------------------
DROP TABLE IF EXISTS `construction_parameter_table`;
CREATE TABLE `construction_parameter_table`  (
  `sequence_number` int NULL DEFAULT NULL,
  `mode` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `direct_labor_unit_price` double NULL DEFAULT NULL,
  `direct_material_unit_price` double NULL DEFAULT NULL,
  `direct_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `timestamp` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of construction_parameter_table
-- ----------------------------
INSERT INTO `construction_parameter_table` VALUES (1, ' 钢筋笼施工模式 ', ' 主体钢筋材料 ', ' Q235B钢筋(现浇构件钢筋) ', NULL, 0, 0, 0, 900.51, 3321.46, 147.79, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (2, ' 钢筋笼施工模式 ', ' 主体钢筋材料 ', ' 水平钢筋绑扎 ', NULL, 380, 0, 0, 380, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (3, ' 钢筋笼施工模式 ', ' 主体钢筋材料 ', ' 竖向钢筋绑扎 ', NULL, 380, 0, 0, 380, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (4, ' 钢筋笼施工模式 ', ' 主体钢筋材料 ', ' 拉筋绑扎 ', NULL, 380, 0, 0, 380, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (5, ' 钢筋笼施工模式 ', ' 主体钢筋材料 ', ' 预留水平钢筋绑扎 ', NULL, 380, 0, 0, 380, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (6, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 直螺纹钢筋套筒(Φ16-Φ40) ', NULL, 0, 0, 0, 5.52, 10.99, 4.99, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (7, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 锥套锁紧套筒 ', NULL, 0, 0, 0, 5.52, 154.31, 4.99, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (8, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 保护帽 ', NULL, 0, 0.5, 0, NULL, 0.5, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (9, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 滚压轮 ', NULL, 0, 7.14, 0, 0, 7.14, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (10, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 润滑液 ', NULL, 0, 4.84, 0, 0, 4.84, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (11, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 砂轮片 ', NULL, 0, 8.02, 0, 0, 8.02, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (12, ' 钢筋笼施工模式 ', ' 连接材料 ', ' Q345预埋铁件(钢筋锚固板) ', NULL, 0, NULL, 0, 5.52, 31.42, 4.99, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (13, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 模块竖向钢筋锥套连接 ', NULL, 380, 18.3, 0, 380, 132.57, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (14, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 措施短柱预埋件安装及调整 ', NULL, 600, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (15, ' 钢筋笼施工模式 ', ' 连接材料 ', ' 模块起吊、落位、短柱连接 ', NULL, 350, 0, 0, 350, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (16, ' 钢筋笼施工模式 ', ' 工装系统 ', ' Q235B零星钢结构(盖板等工装) ', NULL, 0, 0, 0, 4574.74, 4182.91, 1063.11, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (17, ' 钢筋笼施工模式 ', ' 工装系统 ', ' 立柱(HW150*150) ', NULL, NULL, NULL, NULL, 1500, 4181.42, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (18, ' 钢筋笼施工模式 ', ' 工装系统 ', ' 立柱(HW100*100) ', NULL, 0, 0, 0, 1500, 4181.42, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (19, ' 钢筋笼施工模式 ', ' 工装系统 ', ' 立柱安装 ', NULL, 0, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (20, ' 钢筋笼施工模式 ', ' 工装系统 ', ' 立柱拆除 ', NULL, 0, 0, 0, 350, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (21, ' 钢筋笼施工模式 ', ' 工装系统 ', ' 钢筋限位工装安装及调整 ', NULL, NULL, 0, 0, 350, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (22, ' 钢筋笼施工模式 ', ' 工装系统 ', 'L型钢筋 ', NULL, 0, 0, 0, 238, 3791.26, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (23, ' 钢筋笼施工模式 ', ' 工装系统 ', '\"J\"钢筋 ', NULL, 0, 0, 0, 238, 3791.26, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (24, ' 钢筋笼施工模式 ', ' 工装系统 ', '剪刀撑 ', NULL, 0, 0, 0, 238, 3791.26, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (25, ' 钢筋笼施工模式 ', ' 工装系统 ', 'U型卡 ', NULL, 0, 0, 0, 0, 1.4, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (26, ' 钢筋笼施工模式 ', ' 工装系统 ', '双U型卡 ', NULL, 0, 0, 0, 0, 1.8, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (27, ' 钢筋笼施工模式 ', ' 工装系统 ', '短柱(HW150*150) ', NULL, 0, 0, 0, 1500, 4181.42, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (28, ' 钢筋笼施工模式 ', ' 工装系统 ', '预埋件安装 ', NULL, NULL, 0, 0, 3150, 3955.75, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (28, ' 钢筋笼施工模式 ', ' 工装系统 ', '测量放线', NULL, 367.82, NULL, NULL, 367.82, NULL, NULL, NULL);
INSERT INTO `construction_parameter_table` VALUES (29, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '定型围栏安拆 ', NULL, 0, 90.12, 0, 93.4, 90.12, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (30, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '单层彩钢板 ', NULL, 0, 34.51, 0, 93.4, 34.51, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (31, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '电焊条 ', NULL, 0, 6.02, 0, 93.4, 6.02, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (32, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '铁件 ', NULL, 0, 6.28, 0, 93.4, 6.28, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (33, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '模板支设 ', NULL, 0, 0, 0, 420, 37.47, 0.82, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (34, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', '模板支设 ', NULL, 0, 0, 0, 420, 37.47, 0.82, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (35, ' 钢筋笼施工模式 ', ' 施工辅助材料 ', 'C25混凝土 ', NULL, 0, 0, 0, 380, 390.86, 30, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (36, ' 钢筋笼施工模式 ', ' 机械设备 ', '螺栓套丝机(φ39) ', NULL, 0, 0, 0, 120, 0, 34.61, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (37, ' 钢筋笼施工模式 ', ' 机械设备 ', '砂轮切割机(500) ', NULL, 0, 0, 0, 120, 0, 42.48, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (38, ' 钢筋笼施工模式 ', ' 机械设备 ', '自升式塔式起重机(1500KNm) ', NULL, 0, 0, 0, 120, 0, 1182.72, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (39, ' 钢筋笼施工模式 ', ' 机械设备 ', '重型塔吊 ', NULL, 60169.74, 120339.48, 60169.74, 69711.74, 90985.2, 179313.46, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (40, ' 钢筋笼施工模式 ', ' 机械设备 ', '汽车吊(80t) ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (41, ' 钢筋笼施工模式 ', ' 机械设备 ', '汽车吊(25t) ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (42, ' 钢筋笼施工模式 ', ' 机械设备 ', '吊装索具 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (43, ' 钢筋笼施工模式 ', ' 机械设备 ', '花篮螺栓  (JW3128-16.78T-1156.7±304.8-UU) ', NULL, 0, 0, 0, 0, 5.05, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (44, ' 钢筋笼施工模式 ', ' 机械设备 ', '花篮螺栓  (JW3319-32T-1127.5±152.5-UU) ', NULL, 0, 0, 0, 0, 5.05, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (45, ' 钢筋笼施工模式 ', ' 机械设备 ', '花篮螺栓  (JW3409-50T-1100±300-UU) ', NULL, 0, 0, 0, 0, 5.05, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (46, ' 钢筋笼施工模式 ', ' 机械设备 ', '压制钢丝绳（A68 6*36 7.500m）', NULL, NULL, NULL, NULL, NULL, 3720, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (47, ' 钢筋笼施工模式 ', ' 机械设备 ', '压制钢丝绳（A52 6*36 7.407m）', NULL, NULL, NULL, NULL, NULL, 3177, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (48, ' 钢筋笼施工模式 ', ' 机械设备 ', '压制钢丝绳（A36 6*36 1.500m）', NULL, NULL, NULL, NULL, NULL, 849.56, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (49, ' 钢筋笼施工模式 ', ' 机械设备 ', '压制钢丝绳（A68 6*36 9.447M）', NULL, NULL, NULL, NULL, NULL, 4464, NULL, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (50, ' 钢筋笼施工模式 ', ' 机械设备 ', '压制钢丝绳（φ52 6*36 8.678m）', NULL, 0, 0, 0, 0, 3530, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (51, ' 钢筋笼施工模式 ', ' 机械设备 ', ' 卸扣 (17T) ', NULL, 0, 0, 0, 0, 134.52, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (52, ' 钢筋笼施工模式 ', ' 机械设备 ', ' 卸扣 (30T) ', NULL, 0, 0, 0, 0, 387, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (53, ' 钢筋笼施工模式 ', ' 机械设备 ', ' 卸扣 (55T) ', NULL, 0, 0, 0, 0, 709.5, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (54, ' 钢筋笼施工模式 ', ' 其他费用项目 ', ' 模块吊装工装设计费 ', NULL, 0, 0, 0, 255000, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (55, ' 钢筋笼施工模式 ', ' 其他费用项目 ', ' 无损检测 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (56, ' 钢筋笼施工模式 ', ' 其他费用项目 ', ' 钢结构验收 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (57, ' 钢筋笼施工模式 ', ' 其他费用项目 ', ' 钢筋预埋件验收 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (58, ' 钢筋笼+钢覆面施工模式 ', ' 钢覆面材料 ', ' 单侧钢覆面埋件临时安装 ', NULL, 600, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (59, ' 钢筋笼+钢覆面施工模式 ', ' 钢覆面材料 ', ' 另一侧钢覆面埋件临时安装 ', NULL, 600, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (60, ' 钢筋笼+钢覆面施工模式 ', ' 钢覆面材料 ', ' 钢覆面后台制作 ', NULL, 258, 4145, 0, 258, 4145, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (61, ' 钢筋笼+钢覆面施工模式 ', ' 埋件材料 ', ' 不锈钢埋件后台制作 ', NULL, 3500, 21773, 0, 3500, 21773, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (62, ' 钢筋笼+钢覆面施工模式 ', ' 埋件材料 ', ' 碳钢埋件后台制作 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (63, ' 钢筋笼+钢覆面施工模式 ', ' 埋件材料 ', ' 套管、镶入件后台制作 ', NULL, 3500, 21773, 0, 3500, 21773, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (64, ' 钢筋笼+钢覆面施工模式 ', ' 连接及焊接材料 ', ' 单侧钢覆面安装加固+埋件焊接材料+镶入件焊接材料 ', NULL, 600, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (65, ' 钢筋笼+钢覆面施工模式 ', ' 连接及焊接材料 ', ' 通常设备室钢覆面及预留钢覆面组队焊接 ', NULL, 600, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (66, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 预制板模板支设 ', NULL, 0, 0, 0, 80, 84, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (67, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 预制板钢筋制作安装 ', NULL, 0, 0, 0, 1358, 3552.7, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (68, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 预制板混凝土浇筑 ', NULL, 0, 0, 0, 40, 0, 30, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (69, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 模块化角钢制作安装 ', NULL, 0, 0, 0, 2200, 5165, 250, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (70, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 模块起重吊装设备 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (71, ' 叠合板模块化施工(设备室顶板) ', ' 预制构件材料 ', ' 模块运输设备 ', NULL, 0, 0, 0, 0, 0, 200, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (72, ' 叠合板模块化施工(设备室顶板) ', ' 二次浇筑材料 ', ' 二浇区板模板支设 ', NULL, 350, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (73, ' 叠合板模块化施工(设备室顶板) ', ' 二次浇筑材料 ', ' 二浇区板钢筋制作安装 ', NULL, 3800, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (74, ' 叠合板模块化施工(设备室顶板) ', ' 二次浇筑材料 ', ' 二浇区混凝土浇筑 ', NULL, 300, 0, 30, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (75, ' 叠合板模块化施工(设备室顶板) ', ' 二次浇筑材料 ', ' 钢丝网模板 ', NULL, 360, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (76, ' 叠合板模块化施工(设备室顶板) ', ' 二次浇筑材料 ', ' 施工缝凿毛材料 ', NULL, 360, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (77, ' 叠合板模块化施工(设备室顶板) ', ' 支撑系统 ', ' 满堂脚手架搭设 ', NULL, 80, 7.3, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (78, ' 叠合板模块化施工(设备室顶板) ', ' 支撑系统 ', ' 外双排脚手架搭设 ', NULL, 33, 7.3, 0, 33, 7.3, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (79, ' 叠合板模块化施工(设备室顶板) ', ' 支撑系统 ', ' 模块落位钢筋接头连接 ', NULL, 0, 0, 0, 380, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (80, ' 叠合板模块化施工(设备室顶板) ', ' 场地材料 ', ' 预制场地摊销费 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (81, ' 叠合板模块化施工(设备室顶板) ', ' 预制场地设施 ', ' 场地平整 ', NULL, 0, 0, 0, NULL, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (82, ' 叠合板模块化施工(设备室顶板) ', ' 预制场地设施 ', ' 模块支设 ', NULL, 0, 0, 0, 420, 37.47, 0.82, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (83, ' 叠合板模块化施工(设备室顶板) ', ' 预制场地设施 ', ' C25混凝土浇筑（15cm+5cm） ', NULL, 0, 0, 0, 380, 390.86, 30, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (84, ' 叠合板模块化施工(设备室顶板) ', ' 预制场地设施 ', ' 模板拆除 ', NULL, 0, 0, 0, 420, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (85, ' 叠合板模块化施工(设备室顶板) ', ' 预制场地设施 ', ' 预制场地维护 ', NULL, 0, 0, 0, 350, 1.54, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (86, ' 叠合板模块化施工(C403、C409) ', ' 主体钢筋材料 ', ' 钢筋制作安装 ', NULL, 1414, 4205, 407.44, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (87, ' 叠合板模块化施工(C403、C409) ', ' 主体钢筋材料 ', ' 预制板顶分布钢筋(c10@200*200) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (88, ' 叠合板模块化施工(C403、C409) ', ' 主体钢筋材料 ', ' 预制板吊环钢筋(4c16) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (89, ' 叠合板模块化施工(C403、C409) ', ' 主体钢筋材料 ', ' 底部加大钢筋(28代替25) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (90, ' 叠合板模块化施工(C403、C409) ', ' 混凝土材料 ', ' 预制构件混凝土安装(板厚200mm) ', NULL, 0, 0, 0, 240, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (91, ' 叠合板模块化施工(C403、C409) ', ' 模板及支撑材料 ', ' 模板支拆 ', NULL, 105, 84, 0, 94.5, 84, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (92, ' 叠合板模块化施工(C403、C409) ', ' 模板及支撑材料 ', ' 满堂支撑架体搭设拆除 ', NULL, 40, 10, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (93, ' 叠合板模块化施工(C403、C409) ', ' 埋件及连接材料 ', ' 支撑角钢埋件(L100*10，15.12kg/m) ', NULL, 0, 0, 0, 5958.53, 7162.73, 1865.1, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (94, ' 叠合板模块化施工(C403、C409) ', ' 埋件及连接材料 ', ' 墙体埋件(T2型，34.98kg/m) ', NULL, 0, 0, 0, 5958.53, 7162.73, 1865.1, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (95, ' 叠合板模块化施工(C403、C409) ', ' 埋件及连接材料 ', ' 顶板埋件(M-1型，37.583kg/m) ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (96, ' 叠合板模块化施工(C403、C409) ', ' 埋件及连接材料 ', ' 特殊机械套筒 ', NULL, 5, 15, 0, 5, 120, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (97, ' 叠合板模块化施工(C403、C409) ', ' 防水及接缝材料 ', ' 遇水膨胀止水条 ', NULL, 0, 0, 0, 10.71, 4.51, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (98, ' 叠合板模块化施工(C403、C409) ', ' 防水及接缝材料 ', ' 三元乙丙橡胶垫(100*20) ', NULL, 0, 0, 0, 10.71, 4.51, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (99, ' 叠合板模块化施工(C403、C409) ', ' 施工处理材料 ', ' 叠合板凿毛材料 ', NULL, 0, 0, 0, 85, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (100, ' 叠合板模块化施工(C403、C409) ', ' 机械设备 ', ' 25t汽车吊 ', NULL, 0, 0, 3000, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (101, ' 叠合板模块化施工(C403、C409) ', ' 机械设备 ', ' 平板车(9.6m) ', NULL, 0, 0, 1000, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (102, ' 叠合板模块化施工(C403、C409) ', ' 机械设备 ', ' 随车吊(8t) ', NULL, 0, 0, 1550, 5.15, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (103, ' 叠合板模块化施工(C403、C409) ', ' 机械设备 ', ' 80吨汽车吊 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (104, ' 叠合板模块化施工(C403、C409) ', ' 机械设备 ', ' 预制构件运输设备 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (105, ' 叠合板模块化施工(C404) ', ' 主体钢筋材料 ', ' 钢筋制作安装材料 ', NULL, 1414, 4205, 407.44, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (106, ' 叠合板模块化施工(C404) ', ' 主体钢筋材料 ', ' 预制板顶分布钢筋(c10@200*200) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (107, ' 叠合板模块化施工(C404) ', ' 主体钢筋材料 ', ' 预制板吊环钢筋(4c16) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (108, ' 叠合板模块化施工(C404) ', ' 主体钢筋材料 ', ' 底部加大钢筋(28代替25) ', NULL, 0, 0, 0, 1272.6, 4205, 84.2, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (109, ' 叠合板模块化施工(C404) ', ' 混凝土材料 ', ' 预制构件混凝土(板厚200mm) ', NULL, 0, 0, 0, NULL, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (110, ' 叠合板模块化施工(C404) ', ' 模板及支撑材料 ', ' 模板支拆材料 ', NULL, NULL, NULL, 0, NULL, NULL, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (111, ' 叠合板模块化施工(C404) ', ' 模板及支撑材料 ', ' 满堂支撑架体 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (112, ' 叠合板模块化施工(C404) ', ' 埋件及连接材料 ', ' 角钢埋件(L100*100) ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (113, ' 叠合板模块化施工(C404) ', ' 埋件及连接材料 ', ' 支撑角钢埋件(L100*10，15.12kg/m) ', NULL, 0, 0, 0, 5958.53, 7162.73, 1865.1, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (114, ' 叠合板模块化施工(C404) ', ' 埋件及连接材料 ', ' 墙体埋件(T2型，34.98kg/m) ', NULL, 0, 0, 0, 5958.53, 7162.73, 1865.1, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (115, ' 叠合板模块化施工(C404) ', ' 埋件及连接材料 ', ' 普通套筒 ', NULL, 5, 15, 0, 5, 15, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (116, ' 叠合板模块化施工(C404) ', ' 防水及接缝材料 ', ' 遇水膨胀止水条 ', NULL, 0, 0, 0, 10.71, 4.51, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (117, ' 叠合板模块化施工(C404) ', ' 防水及接缝材料 ', ' 三元乙丙橡胶垫(100*20) ', NULL, 0, 0, 0, 10.71, 4.51, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (118, ' 叠合板模块化施工(C404) ', ' 施工处理材料 ', ' 叠合板凿毛材料 ', NULL, 0, 0, 0, 85, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (119, ' 叠合板模块化施工(C404) ', ' 机械设备 ', ' 25t汽车吊 ', NULL, 0, 0, 3000, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (120, ' 叠合板模块化施工(C404) ', ' 机械设备 ', ' 平板车(9.6m) ', NULL, 0, 0, 1000, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (121, ' 叠合板模块化施工(C404) ', ' 机械设备 ', ' 随车吊(8t) ', NULL, 0, 0, 1550, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (122, ' 叠合板模块化施工(C404) ', ' 机械设备 ', ' 80吨汽车吊 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (123, ' 叠合板模块化施工(C404) ', ' 机械设备 ', ' 预制构件运输设备 ', NULL, 0, 0, 0, 0, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (124, ' 叠合板模块化施工(共用) ', ' 预制场基础设施 ', ' 场地平整 ', NULL, 0, 0, 0, 8, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (125, ' 叠合板模块化施工(共用) ', ' 预制场基础设施 ', ' 场地硬化材料(200厚C20混凝土) ', NULL, 0, 0, 0, 90, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (126, ' 叠合板模块化施工(共用) ', ' 预制场基础设施 ', ' 办公区建设材料 ', NULL, 0, 0, 0, 10, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (127, ' 叠合板模块化施工(共用) ', ' 预制场基础设施 ', ' 围墙建设材料 ', NULL, 0, 0, 0, 280, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (128, ' 叠合板模块化施工(共用) ', ' 预制场机械设备 ', ' 200T龙门吊 ', NULL, 0, 0, 0, 500000, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (129, ' 叠合板模块化施工(共用) ', ' 预制场机械设备 ', ' 龙门吊轨道 ', NULL, 0, 0, 0, 600, 0, 0, '2025-04-04 00:00:00');
INSERT INTO `construction_parameter_table` VALUES (130, ' 叠合板模块化施工(共用) ', ' 预制场机械设备 ', ' 预制加工场摊销 ', NULL, 0, 0, 0, 0, 193.27, 0, '2025-04-04 00:00:00');

-- ----------------------------
-- Table structure for custom_modules
-- ----------------------------
DROP TABLE IF EXISTS `custom_modules`;
CREATE TABLE `custom_modules`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `components` json NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of custom_modules
-- ----------------------------

-- ----------------------------
-- Table structure for final_project_summary1
-- ----------------------------
DROP TABLE IF EXISTS `final_project_summary1`;
CREATE TABLE `final_project_summary1`  (
  `project_id` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `tower_crane_rental_fee` double NULL DEFAULT NULL,
  `rebar_production_cost` double NULL DEFAULT NULL,
  `lifting_equipment_cost` double NULL DEFAULT NULL,
  `coupling_cost` double NULL DEFAULT NULL,
  `total_rebar_tonnage` double NULL DEFAULT NULL,
  `coupling_quantity` bigint NULL DEFAULT NULL,
  `lifting_equipment_quantity` double NULL DEFAULT NULL,
  `tower_crane_rental_quantity` double NULL DEFAULT NULL,
  `project_total_price` double NULL DEFAULT NULL,
  `钢筋总吨数` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of final_project_summary1
-- ----------------------------
INSERT INTO `final_project_summary1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 10.25086199, 5855.467243, 5.77487, 116680.4413, 1.34, 681, 0.0033, 0.0046, 450502.4499, '1.34');
INSERT INTO `final_project_summary1` VALUES ('项目二：三期工程C103、C105、C109子项汇总', 10200000, 2066674.07, 700678.13, 878000, 525.79, 3000, 686.7, 30, 17568769.42, NULL);
INSERT INTO `final_project_summary1` VALUES ('项目二：C103', 5069400, 1151692.71, 348237.0294, 436366, 261.57, 1500, 341.2899, 14.91, 7784033.459, NULL);
INSERT INTO `final_project_summary1` VALUES ('项目二：C105', 1968600, 446680.47, 135230.8786, 169454, 101.49, 600, 132.5331, 5.79, 4203315.309, NULL);
INSERT INTO `final_project_summary1` VALUES ('项目二：C109', 3162000, 468120.89, 217210.2195, 272180, 162.73, 900, 212.877, 9.3, 5581420.65, NULL);
INSERT INTO `final_project_summary1` VALUES ('项目三：管廊叠合板钢筋笼项目', 122, 7243.39508, 188.3434419, 8780, 1.302347276, 124, 0.033771125, 0.1, 36346.32741, '0.302347276');

-- ----------------------------
-- Table structure for final_project_summary2
-- ----------------------------
DROP TABLE IF EXISTS `final_project_summary2`;
CREATE TABLE `final_project_summary2`  (
  `project_id` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `assembly_site_cost` double NULL DEFAULT NULL,
  `mold_making_cost` double NULL DEFAULT NULL,
  `steel_support_embedded_cost` double NULL DEFAULT NULL,
  `buttress_column_cost` double NULL DEFAULT NULL,
  `walkway_platform_cost` double NULL DEFAULT NULL,
  `steel_grid_cost` double NULL DEFAULT NULL,
  `project_total_price` double NULL DEFAULT NULL,
  `total_assembly_site_quantity` double NULL DEFAULT NULL,
  `total_mold_making_quantity` double NULL DEFAULT NULL,
  `total_steel_support_embedded_quantity` double NULL DEFAULT NULL,
  `total_buttress_column_quantity` double NULL DEFAULT NULL,
  `total_walkway_platform_quantity` double NULL DEFAULT NULL,
  `total_steel_grid_beam_quantity` double NULL DEFAULT NULL,
  `拼装场地费用` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of final_project_summary2
-- ----------------------------
INSERT INTO `final_project_summary2` VALUES ('项目一', 1351799.534, 363361.488, 397440.575, 893834.4128, 1009760.376, 787183.3324, 15284363.55, 2227.3476, 29.3958, 20.625, 28.636992, 35.43822128, 38.59, NULL);
INSERT INTO `final_project_summary2` VALUES ('项目二', 409910.1696, 2275724.275, 94060.18743, 1149282.431, 1459241.055, 852212.1132, 13002046.36, 1808.64, 86.2, 0.96, 36.82, 35.43822128, 38.59, NULL);

-- ----------------------------
-- Table structure for key_factors_1
-- ----------------------------
DROP TABLE IF EXISTS `key_factors_1`;
CREATE TABLE `key_factors_1`  (
  `project_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `tower_crane_rental_fee` double NULL DEFAULT NULL,
  `rebar_production_cost` double NULL DEFAULT NULL,
  `lifting_equipment_cost` double NULL DEFAULT NULL,
  `coupling_cost` double NULL DEFAULT NULL,
  `total_rebar_tonnage` double NULL DEFAULT NULL,
  `coupling_quantity` int NULL DEFAULT NULL,
  `lifting_equipment_quantity` double NULL DEFAULT NULL,
  `tower_crane_rental_quantity` double NULL DEFAULT NULL,
  `project_total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of key_factors_1
-- ----------------------------
INSERT INTO `key_factors_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 10.25086199, 5855.467243, 5.77487, 116680.4413, 1.34, 681, 0.0033, 0.0046, 450502.4499);
INSERT INTO `key_factors_1` VALUES ('项目二：三期工程C103、C105、C109子项汇总', 10200000, 2066674.07, 700678.13, 878000, 525.79, 3000, 686.7, 30, 17568769.42);
INSERT INTO `key_factors_1` VALUES ('项目二：C103', 5069400, 1151692.71, 348237.0294, 436366, 261.57, 1500, 341.2899, 14.91, 7784033.459);
INSERT INTO `key_factors_1` VALUES ('项目二：C105', 1968600, 446680.47, 135230.8786, 169454, 101.49, 600, 132.5331, 5.79, 4203315.309);
INSERT INTO `key_factors_1` VALUES ('项目二：C109', 3162000, 468120.89, 217210.2195, 272180, 162.73, 900, 212.877, 9.3, 5581420.65);
INSERT INTO `key_factors_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 122, 7243.39508, 188.3434419, 8780, 1.302347276, 124, 0.033771125, 0.1, 36346.32741);

-- ----------------------------
-- Table structure for key_factors_2
-- ----------------------------
DROP TABLE IF EXISTS `key_factors_2`;
CREATE TABLE `key_factors_2`  (
  `project_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `assembly_site_cost` double NULL DEFAULT NULL,
  `mold_making_cost` double NULL DEFAULT NULL,
  `steel_support_embedded_cost` double NULL DEFAULT NULL,
  `buttress_column_cost` double NULL DEFAULT NULL,
  `walkway_platform_cost` double NULL DEFAULT NULL,
  `steel_grid_cost` double NULL DEFAULT NULL,
  `project_total_price` double NULL DEFAULT NULL,
  `total_assembly_site_quantity` double NULL DEFAULT NULL,
  `total_mold_making_quantity` double NULL DEFAULT NULL,
  `total_steel_support_embedded_quantity` double NULL DEFAULT NULL,
  `total_buttress_column_quantity` double NULL DEFAULT NULL,
  `total_walkway_platform_quantity` double NULL DEFAULT NULL,
  `total_steel_grid_beam_quantity` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of key_factors_2
-- ----------------------------
INSERT INTO `key_factors_2` VALUES ('项目一', 1351799.534, 363361.488, 397440.575, 893834.4128, 1009760.376, 787183.3324, 15284363.55, 2227.3476, 29.3958, 20.625, 28.636992, 35.43822128, 38.59);
INSERT INTO `key_factors_2` VALUES ('项目二', 409910.1696, 2275724.275, 94060.18743, 1149282.431, 1459241.055, 852212.1132, 13002046.36, 1808.64, 86.2, 0.96, 36.82, 35.43822128, 38.59);

-- ----------------------------
-- Table structure for operation_logs
-- ----------------------------
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `operation_type` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `operation_desc` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `module` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `target_type` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `target_id` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `level` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `user_agent` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `request_url` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `request_method` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `old_values` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `new_values` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `error_message` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `user_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_operation_logs_module`(`module` ASC) USING BTREE,
  INDEX `ix_operation_logs_operation_type`(`operation_type` ASC) USING BTREE,
  INDEX `ix_operation_logs_created_at`(`created_at` ASC) USING BTREE,
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 35 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of operation_logs
-- ----------------------------
INSERT INTO `operation_logs` VALUES (1, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:22:39', 1);
INSERT INTO `operation_logs` VALUES (2, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:23:00', 1);
INSERT INTO `operation_logs` VALUES (3, 'CAPTCHA_FAILED', '验证码验证失败 - user', 'auth', NULL, NULL, 'warning', 'failed', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, '验证码错误', '2025-09-07 09:23:08', NULL);
INSERT INTO `operation_logs` VALUES (4, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:23:16', 2);
INSERT INTO `operation_logs` VALUES (5, 'LOGOUT', '用户退出登录 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:26:47', 2);
INSERT INTO `operation_logs` VALUES (6, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:26:56', 1);
INSERT INTO `operation_logs` VALUES (7, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:27:12', 1);
INSERT INTO `operation_logs` VALUES (8, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:27:19', 2);
INSERT INTO `operation_logs` VALUES (9, 'LOGOUT', '用户退出登录 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:31:16', 2);
INSERT INTO `operation_logs` VALUES (10, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:31:25', 1);
INSERT INTO `operation_logs` VALUES (11, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:31:37', 1);
INSERT INTO `operation_logs` VALUES (12, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 09:31:45', 2);
INSERT INTO `operation_logs` VALUES (13, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:14:31', 2);
INSERT INTO `operation_logs` VALUES (14, 'LOGOUT', '用户退出登录 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:14:34', 2);
INSERT INTO `operation_logs` VALUES (15, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:14:39', 1);
INSERT INTO `operation_logs` VALUES (16, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:14:48', 1);
INSERT INTO `operation_logs` VALUES (17, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:14:56', 2);
INSERT INTO `operation_logs` VALUES (18, 'LOGOUT', '用户退出登录 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:25:53', 2);
INSERT INTO `operation_logs` VALUES (19, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:25:59', 1);
INSERT INTO `operation_logs` VALUES (20, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:26:40', 1);
INSERT INTO `operation_logs` VALUES (21, 'LOGIN', '用户登录成功 - viewer', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:26:48', 3);
INSERT INTO `operation_logs` VALUES (22, 'LOGOUT', '用户退出登录 - viewer', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:26:51', 3);
INSERT INTO `operation_logs` VALUES (23, 'LOGOUT', '用户退出登录 - viewer', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:27:09', 3);
INSERT INTO `operation_logs` VALUES (24, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-07 11:27:16', 2);
INSERT INTO `operation_logs` VALUES (25, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:24:04', 1);
INSERT INTO `operation_logs` VALUES (26, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:24:12', 1);
INSERT INTO `operation_logs` VALUES (27, 'LOGIN', '用户登录成功 - viewer', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:24:22', 3);
INSERT INTO `operation_logs` VALUES (28, 'LOGOUT', '用户退出登录 - viewer', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:25:37', 3);
INSERT INTO `operation_logs` VALUES (29, 'LOGIN', '用户登录成功 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:25:46', 2);
INSERT INTO `operation_logs` VALUES (30, 'LOGOUT', '用户退出登录 - user', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:27:21', 2);
INSERT INTO `operation_logs` VALUES (31, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:27:30', 1);
INSERT INTO `operation_logs` VALUES (32, 'LOGOUT', '用户退出登录 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:32:21', 1);
INSERT INTO `operation_logs` VALUES (33, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 01:32:59', 1);
INSERT INTO `operation_logs` VALUES (34, 'LOGIN', '用户登录成功 - admin', 'auth', NULL, NULL, 'info', 'success', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-08 06:58:19', 1);

-- ----------------------------
-- Table structure for parameter_change_logs
-- ----------------------------
DROP TABLE IF EXISTS `parameter_change_logs`;
CREATE TABLE `parameter_change_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `algorithm_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '算法类型',
  `construction_mode` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '施工模式',
  `old_parameters` json NULL COMMENT '修改前的参数',
  `new_parameters` json NULL COMMENT '修改后的参数',
  `change_reason` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '修改原因',
  `changed_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '修改人',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_algorithm_mode`(`algorithm_type` ASC, `construction_mode` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '算法参数变更日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of parameter_change_logs
-- ----------------------------

-- ----------------------------
-- Table structure for parameter_info
-- ----------------------------
DROP TABLE IF EXISTS `parameter_info`;
CREATE TABLE `parameter_info`  (
  `parameter_id` int NULL DEFAULT NULL,
  `project_id` int NULL DEFAULT NULL,
  `project_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `parameter_unique_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `parameter_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `parameter_type` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `parameter_value` int NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `direct_labor_unit_price` double NULL DEFAULT NULL,
  `direct_material_unit_price` double NULL DEFAULT NULL,
  `direct_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of parameter_info
-- ----------------------------
INSERT INTO `parameter_info` VALUES (NULL, 706, '测试项目', '72db54cc-3c90-437d-889c-b398736f7e13', ' Q235B钢筋(现浇构件钢筋) ', ' 主体钢筋材料 ', 0, '', ' 钢筋笼施工模式 ', 0, 0, 0, 900.51, 3321.46, 147.79);
INSERT INTO `parameter_info` VALUES (NULL, 706, '测试项目', '573013ba-3539-41c3-9232-57680a5d8a56', ' 水平钢筋绑扎 ', ' 主体钢筋材料 ', 0, '', ' 钢筋笼施工模式 ', 380, 0, 0, 380, 0, 0);
INSERT INTO `parameter_info` VALUES (NULL, 706, '测试项目', '3cb49cb6-3ae2-45eb-a6cd-162d398af148', ' 竖向钢筋绑扎 ', ' 主体钢筋材料 ', 0, '', ' 钢筋笼施工模式 ', 380, 0, 0, 380, 0, 0);
INSERT INTO `parameter_info` VALUES (NULL, 706, '测试项目', '63cc151a-cc8f-4608-b47d-0b9fd0b8d86b', '测试参数', '混凝土材料', 400, '', '', 50, 50, 50, 50, 50, 50);

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `code` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `module` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_permissions_code`(`code` ASC) USING BTREE,
  INDEX `ix_permissions_module`(`module` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES (1, '指标与算法管理', 'data_management', '数据的增删改查权限', 'data', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (2, '系统管理', 'system_config', '系统参数配置权限', 'system', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (3, '报表生成', 'report_generation', '生成和编辑报表权限', 'report', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (4, '施工数据', 'construction_management', '查看施工数据权限', 'report2', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (5, '指标测算', 'indicator_calculation', '指标测算功能权限', 'indicator', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (6, '价格预测', 'price_prediction', '价格预测功能权限', 'prediction', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (7, '模块化施工', 'modular_construction', '模块化施工功能权限', 'construction', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `permissions` VALUES (8, '平台对接', 'platform_integration', '一体化平台对接权限', 'integration', 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');

-- ----------------------------
-- Table structure for prediction_reports
-- ----------------------------
DROP TABLE IF EXISTS `prediction_reports`;
CREATE TABLE `prediction_reports`  (
  `report_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `report_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `mode_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `generation_time` datetime NULL DEFAULT NULL,
  `total_predicted_cost` decimal(15, 2) NULL DEFAULT NULL,
  `ml_ensemble_prediction` decimal(15, 2) NULL DEFAULT NULL,
  `ratio_method_prediction` decimal(15, 2) NULL DEFAULT NULL,
  `raw_data` json NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`) USING BTREE,
  INDEX `idx_report_type`(`report_type` ASC) USING BTREE,
  INDEX `idx_generation_time`(`generation_time` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '预测报告数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of prediction_reports
-- ----------------------------
INSERT INTO `prediction_reports` VALUES ('45644ffa-d313-4642-9613-adff474228c1', 'steel_cage', '钢筋笼施工模式', '2025-08-07 23:16:41', 8167830.92, 8167830.92, 48276970.99, '{\"模式\": \"钢筋笼施工模式\", \"措施费\": 24533, \"生成时间\": \"2025-08-07 23:16:41\", \"预测结果\": {\"用户输入\": {\"套筒数量\": 2345, \"吊索具数量\": 541, \"钢筋总吨数\": 2345, \"塔吊租赁工程量\": 324}, \"估算的工程量\": {\"套筒数量\": 2345, \"吊索具数量\": 541, \"钢筋总吨数\": 2345, \"塔吊租赁工程量\": 324}, \"最佳算法预测\": {\"algorithm_name\": \"决策树 (Decision Tree)\", \"prediction_value\": 12676401.4395}, \"比率法预测总价\": 48276970.99238384, \"算法可用性状态\": {\"status\": \"available\", \"message\": \"有4个算法可用，预测功能正常\", \"enabled_count\": 4}, \"匹配到的规则来源\": \"簇 0\", \"机器学习预测结果\": {\"集成平均预测\": 8167830.915167971, \"岭回归 (RidgeCV)\": {\"status\": \"disabled\", \"db_name\": \"线性回归\", \"message\": \"算法已停用 - 若需启用请到数据管理模块\"}, \"支持向量回归 (SVR)\": 4916908.166013314, \"决策树 (Decision Tree)\": 12700934.4395, \"神经网络 (MLPRegressor)\": 4437557.89915023, \"随机森林 (Random Forest)\": 10615923.156008337}, \"估算的各项成本 (用于ML的特征)\": {\"成本_套筒\": 684244.4233333335, \"成本_吊索具\": 552012.3309617571, \"成本_塔吊租赁\": 0, \"成本_钢筋生产线\": 9771154.687993305}}, \"工程量数据\": {\"套筒数量\": 2345, \"吊索具数量\": 541, \"钢筋总吨数\": 2345, \"措施费工程量\": 24533, \"塔吊租赁工程量\": 324}}', '2025-08-07 23:17:23');
INSERT INTO `prediction_reports` VALUES ('a0c07611-f96a-4d52-b2d2-2182c5de1cf3', 'custom_mode', '自定义模式', '2025-07-24 17:49:40', 5569.00, NULL, NULL, '{\"模式\": \"自定义模式\", \"估算价格\": {\"456\": 546, \"3456\": 456, \"钢筋笼\": 4567}, \"生成时间\": \"2025-07-24 17:49:40\", \"输入参数\": [{\"name\": \"3456\", \"quantity\": 454, \"key_factor\": \"123\", \"price_ratio\": 11, \"price_amount\": 456, \"quantity_ratio\": 11}, {\"name\": \"钢筋笼\", \"quantity\": 23, \"key_factor\": \"456\", \"price_ratio\": 34, \"price_amount\": 4567, \"quantity_ratio\": 34}, {\"name\": \"456\", \"quantity\": 245, \"key_factor\": \"11\", \"price_ratio\": 45, \"price_amount\": 546, \"quantity_ratio\": 23}], \"预测结果\": {\"param_costs\": {\"456\": 546, \"3456\": 456, \"钢筋笼\": 4567}, \"total_predicted_cost\": 5569}, \"估算工程量\": {\"456\": 245, \"3456\": 454, \"钢筋笼\": 23}}', '2025-07-24 17:50:05');
INSERT INTO `prediction_reports` VALUES ('c11a898e-4a6d-4d7f-8e20-57d523d29a53', 'steel_lining', '钢衬里施工模式', '2025-07-24 17:48:06', 64294147.65, 64294147.65, 99360175.26, '{\"模式\": \"钢衬里施工模式\", \"措施费\": 2352, \"生成时间\": \"2025-07-24 17:48:06\", \"预测结果\": {\"用户输入\": {\"扶壁柱总工程量\": 234, \"钢网梁总工程量\": 234, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 245, \"走道板操作平台总工程量\": 235}, \"估算的工程量\": {\"扶壁柱总工程量\": 234, \"钢网梁总工程量\": 234, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 245, \"走道板操作平台总工程量\": 235}, \"比率法预测总价\": 99360175.25835884, \"匹配到的规则来源\": \"全局平均\", \"机器学习预测结果\": {\"集成平均预测\": 64294147.65088213, \"岭回归 (RidgeCV)\": null, \"支持向量回归 (SVR)\": 14145533.00752381, \"决策树 (Decision Tree)\": 14145556.955, \"神经网络 (MLPRegressor)\": 214511711.96700472, \"随机森林 (Random Forest)\": 14373788.674}, \"估算的各项成本 (用于ML的特征)\": {\"扶壁柱费用\": 7303855.72167865, \"钢网架费用\": 4970439.67699404, \"制作胎具费用\": 4535097.11155426, \"拼装场地费用\": 97525.3501094701, \"钢支墩、埋件费用\": 14363027.97593987, \"走道板及操作平台费用\": 8186293.150842361}}, \"工程量数据\": {\"扶壁柱总工程量\": 234, \"钢网梁总工程量\": 234, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 245, \"走道板操作平台总工程量\": 235}}', '2025-07-24 17:48:09');
INSERT INTO `prediction_reports` VALUES ('ca95d435-94e7-435d-90d1-990cd832334c', 'steel_cage', '钢筋笼施工模式', '2025-07-24 17:46:35', 3448492.91, 3448492.91, 10648387.00, '{\"模式\": \"钢筋笼施工模式\", \"措施费\": 2353, \"生成时间\": \"2025-07-24 17:46:35\", \"预测结果\": {\"用户输入\": {\"套筒数量\": 22, \"吊索具数量\": 234, \"钢筋总吨数\": 524, \"塔吊租赁工程量\": 234}, \"估算的工程量\": {\"套筒数量\": 22, \"吊索具数量\": 234, \"钢筋总吨数\": 524, \"塔吊租赁工程量\": 234}, \"比率法预测总价\": 10648387.003551988, \"匹配到的规则来源\": \"簇 0\", \"机器学习预测结果\": {\"集成平均预测\": 3448492.9075463815, \"岭回归 (RidgeCV)\": 3319549.4657779746, \"支持向量回归 (SVR)\": 4894721.820486525, \"决策树 (Decision Tree)\": 245777.388655, \"神经网络 (MLPRegressor)\": 3955229.198759494, \"随机森林 (Random Forest)\": 4827186.664052917}, \"估算的各项成本 (用于ML的特征)\": {\"成本_套筒\": 6419.350666666667, \"成本_吊索具\": 238763.18936238665, \"成本_塔吊租赁\": 0, \"成本_钢筋生产线\": 2183405.141368227}}, \"工程量数据\": {\"套筒数量\": 22, \"吊索具数量\": 234, \"钢筋总吨数\": 524, \"措施费工程量\": 2353, \"塔吊租赁工程量\": 234}}', '2025-07-24 17:47:01');
INSERT INTO `prediction_reports` VALUES ('df91e6e7-d8ec-4550-a18f-b2a6f7d83805', 'steel_cage', '钢筋笼施工模式', '2025-08-07 22:47:20', 2181593.36, 2181593.36, 23892696.17, '{\"模式\": \"钢筋笼施工模式\", \"措施费\": 2351, \"生成时间\": \"2025-08-07 22:47:20\", \"预测结果\": {\"用户输入\": {\"套筒数量\": 234, \"吊索具数量\": 235, \"钢筋总吨数\": 1234}, \"估算的工程量\": {\"套筒数量\": 234, \"吊索具数量\": 235, \"钢筋总吨数\": 1234, \"塔吊租赁工程量\": 70.37437196972759}, \"最佳算法预测\": {\"algorithm_name\": \"支持向量回归 (SVR)\", \"prediction_value\": 4892370.738428631}, \"比率法预测总价\": 23892696.169798, \"算法可用性状态\": {\"status\": \"available\", \"message\": \"有5个算法可用，预测功能正常\", \"enabled_count\": 5}, \"匹配到的规则来源\": \"簇 0\", \"机器学习预测结果\": {\"集成平均预测\": 2181593.3608992677, \"岭回归 (RidgeCV)\": 368377.92052811105, \"支持向量回归 (SVR)\": 4894721.738428631, \"决策树 (Decision Tree)\": 245775.388655, \"神经网络 (MLPRegressor)\": 571907.0928316812, \"随机森林 (Random Forest)\": 4827184.664052917}, \"估算的各项成本 (用于ML的特征)\": {\"成本_套筒\": 68278.54800000001, \"成本_吊索具\": 239783.5448724823, \"成本_塔吊租赁\": 0, \"成本_钢筋生产线\": 5141835.771848076}}, \"工程量数据\": {\"套筒数量\": 234, \"吊索具数量\": 235, \"钢筋总吨数\": 1234, \"措施费工程量\": 2351, \"塔吊租赁工程量\": 0}}', '2025-08-07 22:47:26');
INSERT INTO `prediction_reports` VALUES ('f5d21543-9dd9-410a-b26c-1d12c6561d0c', 'steel_lining', '钢衬里施工模式', '2025-08-07 22:44:36', 34772911.37, 34772911.37, 81265057.87, '{\"模式\": \"钢衬里施工模式\", \"措施费\": 2345, \"生成时间\": \"2025-08-07 22:44:36\", \"预测结果\": {\"用户输入\": {\"扶壁柱总工程量\": 23, \"钢网梁总工程量\": 235, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 235, \"走道板操作平台总工程量\": 234}, \"估算的工程量\": {\"扶壁柱总工程量\": 23, \"钢网梁总工程量\": 235, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 235, \"走道板操作平台总工程量\": 234}, \"最佳算法预测\": {\"algorithm_name\": \"神经网络 (MLPRegressor)\", \"prediction_value\": 130847615.14551029}, \"比率法预测总价\": 81265057.86914295, \"算法可用性状态\": {\"status\": \"available\", \"message\": \"有5个算法可用，预测功能正常\", \"enabled_count\": 5}, \"匹配到的规则来源\": \"全局平均\", \"机器学习预测结果\": {\"集成平均预测\": 34772911.37238969, \"岭回归 (RidgeCV)\": 349729.63973133825, \"支持向量回归 (SVR)\": 14145535.44770679, \"决策树 (Decision Tree)\": 14145549.955, \"神经网络 (MLPRegressor)\": 130849960.14551029, \"随机森林 (Random Forest)\": 14373781.674}, \"估算的各项成本 (用于ML的特征)\": {\"扶壁柱费用\": 717900.348712004, \"钢网架费用\": 4991680.8721948685, \"制作胎具费用\": 4535097.11155426, \"拼装场地费用\": 97525.3501094701, \"钢支墩、埋件费用\": 13776781.936105588, \"走道板及操作平台费用\": 8151457.860838776}}, \"工程量数据\": {\"扶壁柱总工程量\": 23, \"钢网梁总工程量\": 235, \"制作胎具总工程量\": 234, \"拼装场地总工程量\": 234, \"钢支墩埋件总工程量\": 235, \"走道板操作平台总工程量\": 234}}', '2025-08-07 22:46:30');

-- ----------------------------
-- Table structure for price_baseline_1
-- ----------------------------
DROP TABLE IF EXISTS `price_baseline_1`;
CREATE TABLE `price_baseline_1`  (
  `project` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of price_baseline_1
-- ----------------------------
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 1, '塔吊租赁', '台班', 121, 0.046, 5.52, 0, 0, 0, 1182.715497, 0.004, 4.730861989, 10.25086199);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 2, '吊索具数量', '吨', 120, 0.046, 5.52, 0, 0, 0, 42.48, 0.0033, 0.140184, 5.660184);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 3, '吊索具数量', '台班', 0, 0, 0, 8.02, 0.0143, 0.114686, 0, 0, 0, 0.114686);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 4, '套筒数量', '个', 5.52, -31, -171.12, 10.993298, -31, -340.792238, 4.985258989, -31, -154.5430287, -666.4552667);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 5, '套筒数量', '个', 5.52, 712, 3930.24, 154.307798, 712, 109867.1522, 4.985258989, 712, 3549.504401, 117346.8966);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 6, '钢筋吨数', '吨', 900.5063568, 1.34, 1206.678518, 3321.459628, 1.34, 4450.755901, 147.7856893, 1.34, 198.0328237, 5855.467243);
INSERT INTO `price_baseline_1` VALUES ('项目一：1516 2RF内部结构环墙钢筋笼项目', 7, '项目总价', '元', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 450502.4499);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程A', 8, '钢筋生产线费用', '吨', 258, 42.12, 10866.96, 4145, 42.12, 174587.4, 0, 0, 0, 185454.36);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程A', 9, '钢筋生产线费用', '吨', 258, 121.03, 31225.74, 4145, 121.03, 501669.35, 0, 0, 0, 532895.09);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程A', 10, '钢筋生产线费用', '吨', 258, 98.42, 25392.36, 4145, 98.42, 407950.9, 0, 0, 0, 433343.26);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程A', 11, '钢筋吨数', '吨', 0, 0, 0, 0, 261.57, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程A', 12, '项目总价', '元', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1930030.43);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程B', 13, '钢筋生产线费用', '吨', 258, 53.06, 13689.48, 4145, 53.06, 219933.7, 0, 0, 0, 233623.18);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程B', 14, '钢筋生产线费用', '吨', 258, 48.43, 12494.94, 4145, 48.43, 200742.35, 0, 0, 0, 213237.29);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程B', 15, '钢筋吨数', '吨', 0, 0, 0, 0, 101.49, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程B', 16, '项目总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1230593.24);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程C', 17, '钢筋生产线费用', '吨', 258, 63.9, 16486.2, 4145, 63.9, 16486.2, 0, 0, 0, 32972.4);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程C', 18, '钢筋生产线费用', '吨', 258, 64.13, 16545.54, 4145, 64.13, 265818.85, 0, 0, 0, 282364.39);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程C', 19, '钢筋生产线费用', '吨', 258, 34.7, 8952.6, 4145, 34.7, 143831.5, 0, 0, 0, 152784.1);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程C', 20, '钢筋吨数', '吨', 0, 0, 0, 0, 162.73, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目二：三期工程C', 21, '项目总价', '元', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2335466.869);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 22, '塔吊租赁', '月', 0, 0, 0, 0, 0, 0, 340000, 30, 10200000, 10200000);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 23, '吊索具数量', '套', 0, 0, 0, 3720, 15, 55800, 0, 0, 0, 55800);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 24, '吊索具数量', '套', 0, 0, 0, 3177, 15, 47655, 0, 0, 0, 47655);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 25, '吊索具数量', '套', 0, 0, 0, 849.56, 114, 96849.84, 0, 0, 0, 96849.84);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 26, '吊索具数量', '套', 0, 0, 0, 4464, 15, 66960, 0, 0, 0, 66960);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 27, '吊索具数量', '套', 0, 0, 0, 3530, 66, 232980, 0, 0, 0, 232980);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 28, '吊索具数量', '套', 0, 0, 0, 5.05, 114, 575.7, 0, 0, 0, 575.7);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 29, '吊索具数量', '套', 0, 0, 0, 5.05, 78, 393.9, 0, 0, 0, 393.9);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 30, '吊索具数量', '套', 0, 0, 0, 5.05, 27, 136.35, 0, 0, 0, 136.35);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 31, '吊索具数量', '套', 0, 0, 0, 134.52, 114, 15335.28, 0, 0, 0, 15335.28);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 32, '吊索具数量', '套', 0, 0, 0, 387, 78, 30186, 0, 0, 0, 30186);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 33, '吊索具数量', '套', 0, 0, 0, 709.5, 27, 19156.5, 0, 0, 0, 19156.5);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 34, '吊索具数量', 'T', 1500, 8.4, 12600, 4181.415929, 8.4, 35123.89381, 0, 0, 0, 47723.89381);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 35, '吊索具数量', 'T', 1500, 15.3, 22950, 4181.415929, 15.3, 63975.66372, 0, 0, 0, 86925.66372);
INSERT INTO `price_baseline_1` VALUES ('项目二共用参数', 36, '项目总价', '元', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 15100745.66);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 37, '塔吊租赁费', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 38, '塔吊租赁费', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 122, 122);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 39, '塔吊租赁费', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 40, '塔吊租赁费', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 41, '钢筋生产线费用', '吨', 1272.6, 0.5, 636.3, 4205, 0.5, 2102.5, 84.2, 0.5, 42.1, 2780.9);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 42, '钢筋生产线费用', '吨', 1272.6, 0.5, 636.3, 4205, 0.5, 2102.5, 84.2, 0.5, 42.1, 2780.9);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 43, '吊索具数量', NULL, 1272.6, 0.019044569, 24.23611825, 4205, 0.019044569, 80.0824118, 84.2, 0.019044569, 1.603552693, 105.9220828);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 44, '吊索具数量', NULL, 1272.6, 0.014726556, 18.74101517, 4205, 0.014726556, 61.92516798, 84.2, 0.014726556, 1.239976015, 81.90615916);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 45, '吊索具数量', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 46, '吊索具数量', '台班', 5.152, 0.1, 0.5152, 0, 0, 0, 0, 0, 0, 0.5152);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 47, '吊索具数量', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 48, '吊索具数量', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 49, '钢筋吨数', NULL, 1272.6, 0.0760144, 96.73592544, 4205, 0.0760144, 319.640552, 84.2, 0.0760144, 6.40041248, 422.7768899);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 50, '钢筋吨数', NULL, 1272.6, 0.040722, 51.8228172, 4205, 0.040722, 171.23601, 84.2, 0.040722, 3.4287924, 226.4876196);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 51, '钢筋吨数', NULL, 1272.6, 0.120862896, 153.8101214, 4205, 0.120862896, 508.2284777, 84.2, 0.120862896, 10.17665584, 672.215255);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 52, '钢筋吨数', NULL, 1272.6, 0.06474798, 82.39827935, 4205, 0.06474798, 272.2652559, 84.2, 0.06474798, 5.451779916, 360.1153152);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 53, '套筒数量', '个', 5, 60, 300, 120, 60, 7200, 0, 0, 0, 7500);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 54, '套筒数量', '个', 5, 64, 320, 15, 64, 960, 0, 0, 0, 1280);
INSERT INTO `price_baseline_1` VALUES ('项目三：管廊叠合板钢筋笼项目', 55, '项目总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 36346.32741);

-- ----------------------------
-- Table structure for price_baseline_2
-- ----------------------------
DROP TABLE IF EXISTS `price_baseline_2`;
CREATE TABLE `price_baseline_2`  (
  `project` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of price_baseline_2
-- ----------------------------
INSERT INTO `price_baseline_2` VALUES ('项目一：1-3成本测算', 1, '拼装场地', '立方米', 178, 2227.3476, 398071.5631, 426.72, 2227.3476, 950453.7679, 0.47, 2227.3476, 1046.853372, 1349572.184);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-4成本测算', 2, '制作胎具', '吨', 7281.5, 29.3958, 214045.5177, 3655.5, 29.3958, 107456.3469, 1423, 29.3958, 41830.2234, 363332.09);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-5成本测算', 3, '钢支墩、埋件混凝土剔凿', '立方米', 1100.25, 20.625, 22692.65625, 0, 0, 0, 0, 0, 0, 22692.66);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-6成本测算', 4, '钢支墩、埋件混凝土回填', '立方米', 134.64, 10.15, 1366.596, 424.13, 10.15, 4304.9195, 0.38, 10.15, 3.857, 5675.37);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-7成本测算', 5, '钢支墩、埋件安装', '吨', 3153.6, 20.625, 65043, 606.91, 20.625, 12517.51875, 427.38, 20.625, 8814.7125, 86375.23);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-8成本测算', 6, '钢支墩、埋件制作', '吨', 5040, 20.625, 103950, 3409, 20.625, 70310.625, 5254, 20.625, 108363.75, 282624.38);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-9成本测算', 7, '扶壁柱安装', '吨', 4558.32, 28.636992, 130536.5734, 351.95, 28.636992, 10078.78933, 820.85, 28.636992, 23506.67488, 328244.08);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-10成本测算', 8, '扶壁柱拆除', '吨', 3014.12, 28.636992, 86315.33033, 229.57, 28.636992, 6574.194253, 550.87, 28.636992, 15775.25978, 217329.57);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-11成本测算', 9, '扶壁柱构件使用折旧', '吨', 1586.43, 28.636992, 45430.58322, 3715.68, 28.636992, 106405.8984, 777, 28.636992, 22250.94278, 348174.85);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-12成本测算', 10, '走道板及操作平台制作', '吨', 3040.56, 35.43822128, 107752.0381, 2999.04, 35.43822128, 106280.6431, 302.15, 35.43822128, 10707.65856, 449480.68);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-13成本测算', 11, '走道板及操作平台搭设', '吨', 1373.04, 70.87644256, 97316.19069, 450.03, 70.87644256, 31896.52545, 693.95, 70.87644256, 49184.70731, 356794.85);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-14成本测算', 12, '走道板及操作平台拆除', '吨', 702, 70.87644256, 49755.26268, 38.29, 70.87644256, 2713.858986, 693.95, 70.87644256, 49184.70731, 203307.66);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-15成本测算', 13, '钢网架制作', '吨', 5001, 38.59, 192988.59, 7439, 38.59, 287071.01, 2697, 38.59, 104077.23, 584136.83);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-16成本测算', 14, '钢网架安装', '吨', 912.25, 38.59, 35203.7275, 77.21, 38.59, 2979.5339, 597.15, 38.59, 23044.0185, 122454.56);
INSERT INTO `price_baseline_2` VALUES ('项目一：1-17成本测算', 15, '钢网架拆除', '吨', 602.085, 38.59, 23234.46015, 46.5036, 38.59, 1794.573924, 394.119, 38.59, 15209.05221, 80476.17);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-7成本测算', 16, '拼装场地', '立方米', 81.88, 1808.64, 148091.4432, 20.22, 1808.64, 36570.7008, 10.72, 1808.64, 19388.6208, 408101.5296);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-8成本测算', 17, '制作胎具', '吨', 15513.28, 86.2, 1337244.736, 8000.4, 86.2, 689634.48, 2891.47, 86.2, 249244.714, 2275638.075);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-9成本测算', 18, '钢支墩、埋件混凝土剔凿', '立方米', 1100.25, 19.5, 21454.875, NULL, NULL, 0, NULL, NULL, 0, 42909.75);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-10成本测算', 19, '钢支墩、埋件混凝土回填', '立方米', 134.64, 10.15, 1366.596, 424.13, 10.15, 4304.9195, 0.38, 10.15, 3.857, 11350.75);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-11成本测算', 20, '钢支墩、埋件安装', '吨', 3153.6, 0.96, 3027.456, 606.91, 0.96, 582.6336, 427.38, 0.96, 410.2848, 8037.94);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-12成本测算', 21, '钢支墩、埋件折旧', '吨', 2520, 1.85, 4662, 3409.13, 1.85, 6306.8905, 2626.62, 1.85, 4859.247, 31729.29);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-13成本测算', 22, '扶壁柱安装', '吨', 4558.32, 36.82, 167837.3424, 351.95, 36.82, 12958.799, 820.85, 36.82, 30223.697, 422052.62);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-14成本测算', 23, '扶壁柱拆除', '吨', 3014.12, 36.82, 110979.8984, 229.57, 36.82, 8452.7674, 550.87, 36.82, 20283.0334, 279439.97);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-15成本测算', 24, '扶壁柱构件使用折旧', '吨', 1586.43, 36.82, 58412.3526, 3715.68, 36.82, 136811.3376, 777, 36.82, 28609.14, 447679.39);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-16成本测算', 25, '走道板及操作平台制作', '吨', 6081.12, 35.43822128, 215504.0762, 5998.08, 35.43822128, 212561.2863, 604.3, 35.43822128, 21415.31712, 898961.36);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-17成本测算', 26, '走道板及操作平台搭设', '吨', 1373.04, 70.87644256, 97316.19069, 450.03, 70.87644256, 31896.52545, 693.95, 70.87644256, 49184.70731, 356794.85);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-18成本测算', 27, '走道板及操作平台拆除', '吨', 702, 70.87644256, 49755.26268, 38.29, 70.87644256, 2713.858986, 693.95, 70.87644256, 49184.70731, 203307.66);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-19成本测算', 28, '钢网架制作', '吨', 5951.68, 38.59, 229675.3312, 8128.32, 38.59, 313671.8688, 2742.12, 38.59, 105818.4108, 649165.61);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-20成本测算', 29, '钢网架安装', '吨', 912.25, 38.59, 35203.7275, 77.21, 38.59, 2979.5339, 597.15, 38.59, 23044.0185, 122454.56);
INSERT INTO `price_baseline_2` VALUES ('项目二：4-21成本测算', 30, '钢网架拆除', '吨', 602.085, 38.59, 23234.46015, 46.5036, 38.59, 1794.573924, 394.119, 38.59, 15209.05221, 80476.17);

-- ----------------------------
-- Table structure for price_custom_calculation_results
-- ----------------------------
DROP TABLE IF EXISTS `price_custom_calculation_results`;
CREATE TABLE `price_custom_calculation_results`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary key ID, auto increment',
  `batch_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Calculation batch identifier',
  `project_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT 'Project name',
  `total_quantity` decimal(15, 4) NULL DEFAULT 0.0000 COMMENT 'Total quantity',
  `total_price` decimal(15, 2) NULL DEFAULT 0.00 COMMENT 'Total price amount (yuan)',
  `avg_quantity_ratio` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT 'Average quantity ratio',
  `avg_price_ratio` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT 'Average price ratio',
  `predicted_total_cost` decimal(15, 2) NULL DEFAULT 0.00 COMMENT 'Predicted total cost (yuan)',
  `key_factors_summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT 'Summary of key factors',
  `calculation_formula` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT 'Calculation formula used',
  `parameter_count` int NULL DEFAULT 0 COMMENT 'Number of parameters involved in calculation',
  `calculation_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Calculation time',
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'default' COMMENT 'User identifier',
  `status` tinyint NULL DEFAULT 1 COMMENT 'Status (1:active, 0:deleted)',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT 'Calculation remarks',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_batch_no`(`batch_no` ASC) USING BTREE,
  INDEX `idx_calc_time`(`calculation_time` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Custom parameters calculation results table' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of price_custom_calculation_results
-- ----------------------------

-- ----------------------------
-- Table structure for price_custom_parameters
-- ----------------------------
DROP TABLE IF EXISTS `price_custom_parameters`;
CREATE TABLE `price_custom_parameters`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary key ID, auto increment',
  `param_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Parameter name',
  `param_quantity` decimal(15, 4) NULL DEFAULT 0.0000 COMMENT 'Parameter quantity',
  `quantity_ratio` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT 'Quantity ratio (percentage)',
  `price_amount` decimal(15, 2) NULL DEFAULT 0.00 COMMENT 'Price amount (yuan)',
  `price_ratio` decimal(8, 4) NULL DEFAULT 0.0000 COMMENT 'Price ratio (percentage)',
  `key_factor` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT 'Key factor description',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Create time',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `status` tinyint NULL DEFAULT 1 COMMENT 'Status (1:active, 0:deleted)',
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'default' COMMENT 'User identifier',
  `project_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT 'Associated project name',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT 'Remarks',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_param_name`(`param_name` ASC) USING BTREE,
  INDEX `idx_create_time`(`create_time` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Custom mode parameter configuration table' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of price_custom_parameters
-- ----------------------------
INSERT INTO `price_custom_parameters` VALUES (16, '11', 34.0000, 45.0000, 235.00, 45.0000, '222', '2025-07-24 17:48:39', '2025-07-24 17:48:41', 0, 'default', '', NULL);
INSERT INTO `price_custom_parameters` VALUES (17, '456', 245.0000, 23.0000, 546.00, 45.0000, '11', '2025-07-24 17:48:56', '2025-07-24 17:49:39', 0, 'default', '', NULL);
INSERT INTO `price_custom_parameters` VALUES (18, '钢筋笼', 23.0000, 34.0000, 4567.00, 34.0000, '456', '2025-07-24 17:49:13', '2025-07-24 17:49:38', 0, 'default', '', NULL);
INSERT INTO `price_custom_parameters` VALUES (19, '3456', 454.0000, 11.0000, 456.00, 11.0000, '123', '2025-07-24 17:49:31', '2025-07-24 17:49:38', 0, 'default', '', NULL);

-- ----------------------------
-- Table structure for project_five
-- ----------------------------
DROP TABLE IF EXISTS `project_five`;
CREATE TABLE `project_five`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL,
  `data_source` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `original_table_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_five
-- ----------------------------
INSERT INTO `project_five` VALUES (1, '拼装场地', '拼装场地', '立方米', 81.88, 1808.64, 148091.4432, 20.22, 1808.64, 36570.7008, 10.72, 1808.64, 19388.6208, 408101.5296, '项目二', '项目二');
INSERT INTO `project_five` VALUES (2, '制作胎具', '制作胎具', '吨', 15513.28, 86.2, 1337244.736, 8000.4, 86.2, 689634.48, 2891.47, 86.2, 249244.714, 2275638.07524, '项目二', '项目二');
INSERT INTO `project_five` VALUES (3, '钢支墩、埋件', '钢支墩、埋件混凝土剔凿', '立方米', 1100.25, 19.5, 21454.875, NULL, NULL, 0, NULL, NULL, 0, 42909.75, '项目二', '项目二');
INSERT INTO `project_five` VALUES (4, '钢支墩、埋件', '钢支墩、埋件混凝土回填', '立方米', 134.64, 10.15, 1366.596, 424.13, 10.15, 4304.9195, 0.38, 10.15, 3.857, 11350.745, '项目二', '项目二');
INSERT INTO `project_five` VALUES (5, '钢支墩、埋件', '钢支墩、埋件安装', '吨', 3153.6, 0.96, 3027.456, 606.91, 0.96, 582.6336, 427.38, 0.96, 410.2848, 8037.93872581, '项目二', '项目二');
INSERT INTO `project_five` VALUES (6, '钢支墩、埋件', '钢支墩、埋件折旧', '吨', 2520, 1.85, 4662, 3409.13, 1.85, 6306.8905, 2626.62, 1.85, 4859.247, 31729.2897705, '项目二', '项目二');
INSERT INTO `project_five` VALUES (7, '扶壁柱', '扶壁柱安装', '吨', 4558.32, 36.82, 167837.3424, 351.95, 36.82, 12958.799, 820.85, 36.82, 30223.697, 422052.61766896, '项目二', '项目二');
INSERT INTO `project_five` VALUES (8, '扶壁柱', '扶壁柱拆除', '吨', 3014.12, 36.82, 110979.8984, 229.57, 36.82, 8452.7674, 550.87, 36.82, 20283.0334, 279439.96651648, '项目二', '项目二');
INSERT INTO `project_five` VALUES (9, '扶壁柱', '扶壁柱构件使用折旧', '吨', 1586.43, 36.82, 58412.3526, 3715.68, 36.82, 136811.3376, 777, 36.82, 28609.14, 447679.38703038, '项目二', '项目二');
INSERT INTO `project_five` VALUES (10, '走道板及操作平台', '走道板及操作平台制作', '吨', 6081.12, 35.43822128, 215504.076190234, 5998.08, 35.43822128, 212561.286295142, 604.3, 35.43822128, 21415.317119504, 898961.35920976, '项目二', '项目二');
INSERT INTO `project_five` VALUES (11, '走道板及操作平台', '走道板及操作平台搭设', '吨', 1373.04, 70.87644256, 97316.1906925824, 450.03, 70.87644256, 31896.5254452768, 693.95, 70.87644256, 49184.707314512, 356794.846904742, '项目二', '项目二');
INSERT INTO `project_five` VALUES (12, '走道板及操作平台', '走道板及操作平台拆除', '吨', 702, 70.87644256, 49755.26267712, 38.29, 70.87644256, 2713.8589856224, 693.95, 70.87644256, 49184.707314512, 203307.657954509, '项目二', '项目二');
INSERT INTO `project_five` VALUES (13, '钢网架', '钢网架制作', '吨', 5951.68, 38.59, 229675.3312, 8128.32, 38.59, 313671.8688, 2742.12, 38.59, 105818.4108, 649165.6108, '项目二', '项目二');
INSERT INTO `project_five` VALUES (14, '钢网架', '钢网架安装', '吨', 912.25, 38.59, 35203.7275, 77.21, 38.59, 2979.5339, 597.15, 38.59, 23044.0185, 122454.5598, '项目二', '项目二');
INSERT INTO `project_five` VALUES (15, '钢网架', '钢网架拆除', '吨', 602.085, 38.59, 23234.46015, 46.5036, 38.59, 1794.573924, 394.119, 38.59, 15209.05221, 80476.172568, '项目二', '项目二');
INSERT INTO `project_five` VALUES (16, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 6238099.50678914, '项目二', '项目二');

-- ----------------------------
-- Table structure for project_four
-- ----------------------------
DROP TABLE IF EXISTS `project_four`;
CREATE TABLE `project_four`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_four
-- ----------------------------
INSERT INTO `project_four` VALUES (2, '制作胎具', '制作胎具', '吨', 15513.28, 86.2, 1337244.736, 8000.4, 86.2, 689634.48, 2891.47, 86.2, 249244.714, 2275638.07524);
INSERT INTO `project_four` VALUES (4, '钢支墩、埋件', '钢支墩、埋件混凝土回填', '立方米', 134.64, 10.15, 1366.596, 424.13, 10.15, 4304.9195, 0.38, 10.15, 3.857, 11350.745);
INSERT INTO `project_four` VALUES (6, '钢支墩、埋件', '钢支墩、埋件折旧', '吨', 2520, 1.85, 4662, 3409.13, 1.85, 6306.8905, 2626.62, 1.85, 4859.247, 31729.2897705);
INSERT INTO `project_four` VALUES (8, '扶壁柱', '扶壁柱拆除', '吨', 3014.12, 36.82, 110979.8984, 229.57, 36.82, 8452.7674, 550.87, 36.82, 20283.0334, 279439.96651648);
INSERT INTO `project_four` VALUES (9, '扶壁柱', '扶壁柱构件使用折旧', '吨', 1586.43, 36.82, 58412.3526, 3715.68, 36.82, 136811.3376, 777, 36.82, 28609.14, 447679.38703038);
INSERT INTO `project_four` VALUES (10, '走道板及操作平台', '走道板及操作平台制作', '吨', 6081.12, 35.43822128, 215504.076190234, 5998.08, 35.43822128, 212561.286295142, 604.3, 35.43822128, 21415.317119504, 898961.35920976);
INSERT INTO `project_four` VALUES (11, '走道板及操作平台', '走道板及操作平台搭设', '吨', 1373.04, 70.87644256, 97316.1906925824, 450.03, 70.87644256, 31896.5254452768, 693.95, 70.87644256, 49184.707314512, 356794.846904742);
INSERT INTO `project_four` VALUES (12, '走道板及操作平台', '走道板及操作平台拆除', '吨', 702, 70.87644256, 49755.26267712, 38.29, 70.87644256, 2713.8589856224, 693.95, 70.87644256, 49184.707314512, 203307.657954509);
INSERT INTO `project_four` VALUES (13, '钢网架', '钢网架制作', '吨', 5951.68, 38.59, 229675.3312, 8128.32, 38.59, 313671.8688, 2742.12, 38.59, 105818.4108, 649165.6108);
INSERT INTO `project_four` VALUES (14, '钢网架', '钢网架安装', '吨', 912.25, 38.59, 35203.7275, 77.21, 38.59, 2979.5339, 597.15, 38.59, 23044.0185, 122454.5598);
INSERT INTO `project_four` VALUES (15, '钢网架', '钢网架拆除', '吨', 602.085, 38.59, 23234.46015, 46.5036, 38.59, 1794.573924, 394.119, 38.59, 15209.05221, 80476.172568);
INSERT INTO `project_four` VALUES (16, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 6238099.50678914);

-- ----------------------------
-- Table structure for project_info
-- ----------------------------
DROP TABLE IF EXISTS `project_info`;
CREATE TABLE `project_info`  (
  `project_id` int NOT NULL AUTO_INCREMENT,
  `project_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_quantity` decimal(15, 2) NULL DEFAULT 0.00,
  `unit` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `normal_construction_days` int NULL DEFAULT 0,
  `modular_construction_days` int NULL DEFAULT 0,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 708 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_info
-- ----------------------------
INSERT INTO `project_info` VALUES (701, '测试111', 'A', 45.00, '台班', 20, 25, '', '2025-08-27 15:52:58');
INSERT INTO `project_info` VALUES (706, '测试项目', '桥梁工程', 100.00, 'm³', 50, 40, '测试项目', '2025-09-07 09:17:38');

-- ----------------------------
-- Table structure for project_one
-- ----------------------------
DROP TABLE IF EXISTS `project_one`;
CREATE TABLE `project_one`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_one
-- ----------------------------
INSERT INTO `project_one` VALUES (1, '塔吊租赁', '自升式塔式起重机(1500KNm)', '台班', 120, 0.046, 5.52, 0, 0, 0, 1182.715497, 0.004, 4.730861989, '10.25086199');
INSERT INTO `project_one` VALUES (7, '预埋铁件', '预埋铁件(Q345钢筋锚固板)', '个', 5.52, -3, -16.56, 31.419798, -3, -94.259394, 4.985258989, -3, -14.95577697, '-125.775171');
INSERT INTO `project_one` VALUES (8, '零星钢结构', '盖板', '吨', 4574.736, 5.75918, 26346.72808, 4182.910652, 5.75918, 24090.13537, 1063.107475, 5.75918, 6122.627305, '56559.49075');
INSERT INTO `project_one` VALUES (9, '定型围栏', '定型围栏安拆', 'M2', 93.4, 90, 8406, 90.12, 90, 8110.8, 0, 0, 0, '16516.8');
INSERT INTO `project_one` VALUES (10, '模块吊装', '模块吊装工装设计费', '项', 255000, 1, 255000, 0, 0, 0, 0, 0, 0, '255000');
INSERT INTO `project_one` VALUES (11, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '#REF!');

-- ----------------------------
-- Table structure for project_three
-- ----------------------------
DROP TABLE IF EXISTS `project_three`;
CREATE TABLE `project_three`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_three
-- ----------------------------
INSERT INTO `project_three` VALUES (1, '塔吊租赁费', '机械设备费25t汽车吊C403、C409', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (2, '塔吊租赁费', '机械设备费80吨汽车吊C403、C409', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 122, 122);
INSERT INTO `project_three` VALUES (3, '塔吊租赁费', '机械设备费25t汽车吊C404', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (4, '塔吊租赁费', '机械设备费80吨汽车吊C404', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (5, '钢筋生产线费用', '钢筋制作安装C403、C409', 't', 1272.6, 0.5, 636.3, 4205, 0.5, 2102.5, 84.2, 0.5, 42.1, 2780.9);
INSERT INTO `project_three` VALUES (6, '钢筋生产线费用', '钢筋制作安装C404', 't', 1272.6, 0.5, 636.3, 4205, 0.5, 2102.5, 84.2, 0.5, 42.1, 2780.9);
INSERT INTO `project_three` VALUES (7, '吊索具数量', '预制板新增吊环（4c16）C403、C409', NULL, 1272.6, 0.019044569, 24.23611825, 4205, 0.019044569, 80.0824118, 84.2, 0.019044569, 1.603552693, 105.9220828);
INSERT INTO `project_three` VALUES (8, '吊索具数量', '预制板新增吊环（4c16）C404', NULL, 1272.6, 0.014726556, 18.74101517, 4205, 0.014726556, 61.92516798, 84.2, 0.014726556, 1.239976015, 81.90615916);
INSERT INTO `project_three` VALUES (9, '吊索具数量', '机械设备费平板车（9.6m）C403、C409', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (10, '吊索具数量', '机械设备费随车吊（8t）C403、C409', '台班', 5.152, 0.1, 0.5152, 0, 0, 0, 0, 0, 0, 0.5152);
INSERT INTO `project_three` VALUES (11, '吊索具数量', '机械设备费平板车（9.6m）C404', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (12, '吊索具数量', '机械设备费随车吊（8t）C404', '台班', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (13, '钢筋吨数', '增加预制板顶分布钢筋（c10@200*200)C403、C409', NULL, 1272.6, 0.0760144, 96.73592544, 4205, 0.0760144, 319.640552, 84.2, 0.0760144, 6.40041248, 422.7768899);
INSERT INTO `project_three` VALUES (14, '钢筋吨数', '增加预制板顶分布钢筋（c10@200*200)C404', NULL, 1272.6, 0.040722, 51.8228172, 4205, 0.040722, 171.23601, 84.2, 0.040722, 3.4287924, 226.4876196);
INSERT INTO `project_three` VALUES (15, '钢筋吨数', '底部钢筋升级（28代替25）C403、C409', NULL, 1272.6, 0.120862896, 153.8101214, 4205, 0.120862896, 508.2284777, 84.2, 0.120862896, 10.17665584, 672.215255);
INSERT INTO `project_three` VALUES (16, '钢筋吨数', '底部钢筋升级（28代替25）C404', NULL, 1272.6, 0.06474798, 82.39827935, 4205, 0.06474798, 272.2652559, 84.2, 0.06474798, 5.451779916, 360.1153152);
INSERT INTO `project_three` VALUES (17, '套筒数量', '特殊机械套筒增加费C403、C409', '个', 5, 60, 300, 120, 60, 7200, 0, 0, 0, 7500);
INSERT INTO `project_three` VALUES (18, '套筒数量', '普通套筒C404', '个', 5, 64, 320, 15, 64, 960, 0, 0, 0, 1280);
INSERT INTO `project_three` VALUES (19, '混凝土工程', '混凝土浇筑（模块化预制构件制作费用）C403、C409', 'm3', 97.2, 2.24, 217.728, 680, 2.24, 1523.2, 0, 0, 0, 1740.928);
INSERT INTO `project_three` VALUES (20, '混凝土工程', '混凝土浇筑（模块化预制构件制作费用）C404', 'm3', 97.2, 1.2, 116.64, 680, 1.2, 816, 0, 0, 0, 932.64);
INSERT INTO `project_three` VALUES (21, '混凝土工程', '预制构件混凝土安装C403、C409', 'm3', 240, 2.24, 537.6, 0, 0, 0, 0, 0, 0, 537.6);
INSERT INTO `project_three` VALUES (22, '混凝土工程', '预制构件混凝土安装C404', 'm3', 240, 1.2, 288, 0, 0, 0, 0, 0, 0, 288);
INSERT INTO `project_three` VALUES (23, '混凝土工程', '正常施工考虑泵送费+砼运输费C403、C409', 'm3', 0, 0, 0, 0, 0, 0, 45, 2.24, 100.8, 100.8);
INSERT INTO `project_three` VALUES (24, '混凝土工程', '正常施工考虑泵送费+砼运输费C404', 'm3', 0, 0, 0, 0, 0, 0, 45, 1.2, 54, 54);
INSERT INTO `project_three` VALUES (25, '模板工程', '模板支拆C403、C409', 'm2', 94.5, 13.92, 1315.44, 84, 13.92, 1169.28, 0, 0, 0, 2484.72);
INSERT INTO `project_three` VALUES (26, '模板工程', '模板支拆C404', 'm2', 94.5, 8, 756, 84, 8, 672, 0, 0, 0, 1428);
INSERT INTO `project_three` VALUES (27, '模板工程', '叠合板凿毛费C403、C409', 'm2', 85, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (28, '模板工程', '叠合板凿毛费C404', 'm2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (29, '预制加工场地', '预制加工场摊销C403、C409', 'm3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (30, '预制加工场地', '预制加工场摊销C404', 'm3', 0, 0, 0, 193.2666667, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_three` VALUES (31, '运输费用', '预制构件运输费C403、C409', 'm3', 0, 0, 0, 0, 0, 0, 38.33333333, 1.2, 46, 46);
INSERT INTO `project_three` VALUES (32, '运输费用', '预制构件运输费C404', 'm3', 0, 0, 0, 0, 0, 0, 0, 0, 46, 46);
INSERT INTO `project_three` VALUES (33, '模块化埋件系列', '模块化支撑角钢（埋件）制作安装费C403、C409', 't', 5958.53, 0.12096, 720.7437888, 7162.73, 0.12096, 866.4038208, 1865.1, 0.12096, 225.602496, 1812.750106);
INSERT INTO `project_three` VALUES (34, '模块化埋件系列', '模块化支撑角钢（埋件）制作安装费C404', 't', 5958.53, 0.06048, 360.3718944, 7162.73, 0.06048, 433.2019104, 1865.1, 0.06048, 112.801248, 906.3750528);
INSERT INTO `project_three` VALUES (35, '模块化埋件系列', '模块化埋件（墙体）制作安装费C403、C409', 't', 5958.53, 0.27984, 1667.435035, 7162.73, 0.27984, 2004.418363, 1865.1, 0.27984, 521.929584, 4193.782982);
INSERT INTO `project_three` VALUES (36, '模块化埋件系列', '模块化埋件（墙体）制作安装费C404', 't', 5958.53, 0.13992, 833.7175176, 7162.73, 0.13992, 1002.209182, 1865.1, 0.13992, 260.964792, 2096.891491);
INSERT INTO `project_three` VALUES (37, '模块化埋件系列', '模块化埋件（顶板）制作安装费C403、C409', 't', 5958.53, 0.2104648, 1254.060825, 7162.73, 0.2104648, 1507.502537, 1865.1, 0.2104648, 392.5378985, 3154.10126);
INSERT INTO `project_three` VALUES (38, '模块化埋件系列', '模块化角钢（埋件）制作安装费C404', 't', 2600, 0.025, 65, 5000, 0.025, 125, NULL, NULL, NULL, 190);
INSERT INTO `project_three` VALUES (39, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 36346.32741);

-- ----------------------------
-- Table structure for project_two_shared_params
-- ----------------------------
DROP TABLE IF EXISTS `project_two_shared_params`;
CREATE TABLE `project_two_shared_params`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` int NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` double NULL DEFAULT NULL,
  `modular_machinery_quantity` double NULL DEFAULT NULL,
  `modular_machinery_total` double NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_two_shared_params
-- ----------------------------
INSERT INTO `project_two_shared_params` VALUES (1, '塔吊租赁', '塔吊租赁费用', '月', 0, 0, 0, 0, 0, 0, 340000, 30, 10200000, 10200000);
INSERT INTO `project_two_shared_params` VALUES (2, '吊索具数量', '压制钢丝绳（A68 6*36 7.500m）', '套', 0, 0, 0, 3720, 15, 55800, 0, 0, 0, 55800);
INSERT INTO `project_two_shared_params` VALUES (3, '吊索具数量', '压制钢丝绳（A52 6*36 7.407m）', '套', 0, 0, 0, 3177, 15, 47655, 0, 0, 0, 47655);
INSERT INTO `project_two_shared_params` VALUES (4, '吊索具数量', '压制钢丝绳（A36 6*36 1.500m）', '套', 0, 0, 0, 849.56, 114, 96849.84, 0, 0, 0, 96849.84);
INSERT INTO `project_two_shared_params` VALUES (5, '吊索具数量', '压制钢丝绳（A68 6*36 9.447M）', '套', 0, 0, 0, 4464, 15, 66960, 0, 0, 0, 66960);
INSERT INTO `project_two_shared_params` VALUES (6, '吊索具数量', '压制钢丝绳（φ52 6*36 8.678m）', '套', 0, 0, 0, 3530, 66, 232980, 0, 0, 0, 232980);
INSERT INTO `project_two_shared_params` VALUES (7, '吊索具数量', '花篮螺栓（JW3128-16.78T-1156.7±304.8-UU）', '套', 0, 0, 0, 5.05, 114, 575.7, 0, 0, 0, 575.7);
INSERT INTO `project_two_shared_params` VALUES (8, '吊索具数量', '花篮螺栓（JW3319-32T-1127.5±152.5-UU）', '套', 0, 0, 0, 5.05, 78, 393.9, 0, 0, 0, 393.9);
INSERT INTO `project_two_shared_params` VALUES (9, '吊索具数量', '花篮螺栓（JW3409-50T-1100±300-UU）', '套', 0, 0, 0, 5.05, 27, 136.35, 0, 0, 0, 136.35);
INSERT INTO `project_two_shared_params` VALUES (10, '吊索具数量', '卸扣（17T）', '套', 0, 0, 0, 134.52, 114, 15335.28, 0, 0, 0, 15335.28);
INSERT INTO `project_two_shared_params` VALUES (11, '吊索具数量', '卸扣（30T）', '套', 0, 0, 0, 387, 78, 30186, 0, 0, 0, 30186);
INSERT INTO `project_two_shared_params` VALUES (12, '吊索具数量', '卸扣（55T）', '套', 0, 0, 0, 709.5, 27, 19156.5, 0, 0, 0, 19156.5);
INSERT INTO `project_two_shared_params` VALUES (13, '吊索具数量', '型钢（HW400*400）', 'T', 1500, 8.4, 12600, 4181.415929, 8.4, 35123.89381, 0, 0, 0, 47723.89381);
INSERT INTO `project_two_shared_params` VALUES (14, '吊索具数量', '型钢（HW300*300）', 'T', 1500, 15.3, 22950, 4181.415929, 15.3, 63975.66372, 0, 0, 0, 86925.66372);
INSERT INTO `project_two_shared_params` VALUES (15, '拼装设施', '立柱（HW150*150）', 'T', 1500, 124, 186000, 4181.415929, 124, 518495.5752, 0, 0, 0, 704495.5752);
INSERT INTO `project_two_shared_params` VALUES (16, '拼装设施', '立柱（HW100*100）', 'T', 1500, 52, 78000, 4181.415929, 52, 217433.6283, 0, 0, 0, 295433.6283);
INSERT INTO `project_two_shared_params` VALUES (17, '拼装设施', 'U型卡（φ8）', '个', 0, 0, 0, 1.4, 160000, 224000, 0, 0, 0, 224000);
INSERT INTO `project_two_shared_params` VALUES (18, '拼装设施', '双U型卡（DN25~DN32）', '个', 0, 0, 0, 1.8, 100000, 180000, 0, 0, 0, 180000);
INSERT INTO `project_two_shared_params` VALUES (19, '拼装设施', 'L型钢筋', 'T', 238, 105.6, 25132.8, 3791.262136, 105.6, 400357.2816, 0, 0, 0, 425490.0816);
INSERT INTO `project_two_shared_params` VALUES (20, '拼装设施', '剪刀撑', 'T', 238, 35.52, 8453.76, 3791.262136, 35.52, 134665.6311, 0, 0, 0, 143119.3911);
INSERT INTO `project_two_shared_params` VALUES (21, '拼装设施', '型钢HW150*150', 'T', 238, 30, 7140, 4181.415929, 30, 125442.4779, 0, 0, 0, 132582.4779);
INSERT INTO `project_two_shared_params` VALUES (22, '拼装设施', '“J”钢筋', 'T', 238, 22.08, 5255.04, 3791.262136, 22.08, 83711.06796, 0, 0, 0, 88966.10796);
INSERT INTO `project_two_shared_params` VALUES (23, '拼装设施', '短柱', 'T', 1500, 10.4, 15600, 4181.415929, 10.4, 43486.72566, 0, 0, 0, 59086.72566);
INSERT INTO `project_two_shared_params` VALUES (24, '拼装设施', '预埋件', 'T', 3150, 20.16, 63504, 3955.752212, 20.16, 79747.9646, 0, 0, 0, 143251.9646);
INSERT INTO `project_two_shared_params` VALUES (25, '拼装场地建设', '场地平整', 'm2', 3, 4081.35, 12244.05, 0, 0, 0, 0, 0, 0, 12244.05);
INSERT INTO `project_two_shared_params` VALUES (26, '拼装场地建设', '模板支设', 'm2', 420, 73.24, 4200, 37.47, 73.24, 2744.3028, 0.82, 73.24, 60.0568, 7004.3596);
INSERT INTO `project_two_shared_params` VALUES (27, '拼装场地建设', 'C25混凝土浇筑（15cm+5cm)', 'm3', 380, 816.27, 1900, 390.86, 816.27, 319047.2922, 30, 816.27, 24488.1, 345435.3922);
INSERT INTO `project_two_shared_params` VALUES (28, '拼装场地建设', '模板拆除', 'm2', 420, 73.24, 4200, 0, 0, 0, 0, 0, 0, 4200);
INSERT INTO `project_two_shared_params` VALUES (29, '拼装场地建设', '预制场地维护', 'm2', 350, 4081.35, 1428472.5, 1.54, 4081.35, 6285.279, 0, 0, 0, 1434757.779);
INSERT INTO `project_two_shared_params` VALUES (30, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 15100745.66);

-- ----------------------------
-- Table structure for project_two_sub_one
-- ----------------------------
DROP TABLE IF EXISTS `project_two_sub_one`;
CREATE TABLE `project_two_sub_one`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` int NULL DEFAULT NULL,
  `modular_machinery_quantity` int NULL DEFAULT NULL,
  `modular_machinery_total` int NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_two_sub_one
-- ----------------------------
INSERT INTO `project_two_sub_one` VALUES (2, '钢筋生产线费用', '钢筋后台制作费用（负一层）', '吨', 258, 121.03, 31225.74, 4145, 121.03, 501669.35, 0, 0, 0, 532895.09);
INSERT INTO `project_two_sub_one` VALUES (3, '钢筋生产线费用', '钢筋后台制作费用（一层）', '吨', 258, 98.42, 25392.36, 4145, 98.42, 407950.9, 0, 0, 0, 433343.26);
INSERT INTO `project_two_sub_one` VALUES (4, '钢筋吨数', '钢筋', '吨', 0, 0, 0, 0, 261.57, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (5, '人工单价', '木工', '工日', 420, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (6, '人工单价', '钢筋工', '工日', 380, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (7, '人工单价', '架子工', '工日', 550, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (8, '人工单价', '混凝土工', '工日', 380, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (9, '人工单价', '焊工', '工日', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (10, '人工单价', '铆工', '工日', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (11, '埋件制作', '不锈钢埋件后台制作费用', 't', 3500, 11.84, 41440, 21773, 11.84, 257792.32, 0, 0, 0, 299232.32);
INSERT INTO `project_two_sub_one` VALUES (12, '埋件制作', '碳钢埋件后台制作费用', 't', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (13, '埋件制作', '套管、镶入件后台制作费用', 't', 3500, 0, 0, 21773, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (14, '埋件制作', '钢覆面后台制作费用', 't', 3500, 13.78, 48230, 21773, 13.78, 300031.94, 0, 0, 0, 348261.94);
INSERT INTO `project_two_sub_one` VALUES (15, '施工工序', '测量放线', '项', 367.82, 3, 1103.46, 0, 0, 0, 0, 0, 0, 1103.46);
INSERT INTO `project_two_sub_one` VALUES (16, '施工工序', '内外侧双排操作架搭设', 'm2', 550, 33, 18150, 7.3, 0, 0, 0, 0, 0, 18150);
INSERT INTO `project_two_sub_one` VALUES (17, '施工工序', '立柱安装(周转，仅人工费）', 't', 600, 5, 3000, 0, 0, 0, 0, 0, 0, 3000);
INSERT INTO `project_two_sub_one` VALUES (18, '施工工序', '钢筋限位工装安装及调整', 't', 350, 17, 5950, 0, 0, 0, 0, 0, 0, 5950);
INSERT INTO `project_two_sub_one` VALUES (19, '施工工序', '水平钢筋、竖向钢筋绑扎', '项', 380, 211, 80180, 0, 0, 0, 0, 0, 0, 80180);
INSERT INTO `project_two_sub_one` VALUES (20, '施工工序', '单侧钢覆面埋件临时安装', '项', 600, 33, 19800, 0, 0, 0, 0, 0, 0, 19800);
INSERT INTO `project_two_sub_one` VALUES (21, '施工工序', '钢覆面镶入件临时安装', '项', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_one` VALUES (22, '施工工序', '模块钢筋调整、加固', '项', 380, 7, 2660, 0, 0, 0, 0, 0, 0, 2660);
INSERT INTO `project_two_sub_one` VALUES (23, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1930030.43);

-- ----------------------------
-- Table structure for project_two_sub_three
-- ----------------------------
DROP TABLE IF EXISTS `project_two_sub_three`;
CREATE TABLE `project_two_sub_three`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` int NULL DEFAULT NULL,
  `modular_machinery_quantity` int NULL DEFAULT NULL,
  `modular_machinery_total` int NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_two_sub_three
-- ----------------------------
INSERT INTO `project_two_sub_three` VALUES (1, '钢筋生产线费用', '钢筋后台制作费用（负二层）', '吨', 258, 63.9, 16486.2, 4145, 63.9, 16486.2, 0, 0, 0, 32972.4);
INSERT INTO `project_two_sub_three` VALUES (2, '钢筋生产线费用', '钢筋后台制作费用（负一层）', '吨', 258, 64.13, 16545.54, 4145, 64.13, 265818.85, 0, 0, 0, 282364.39);
INSERT INTO `project_two_sub_three` VALUES (3, '钢筋生产线费用', '钢筋后台制作费用（一层）', '吨', 258, 34.7, 8952.6, 4145, 34.7, 143831.5, 0, 0, 0, 152784.1);
INSERT INTO `project_two_sub_three` VALUES (4, '钢筋吨数', '钢筋', '吨', 0, 0, 0, 0, 261.57, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (5, '拼装场地建设', '预制场地维护', 'm2', 350, 4081.35, 1428472.5, 1.54, 4081.35, 6285.279, 0, 0, 0, 1434757.779);
INSERT INTO `project_two_sub_three` VALUES (6, '施工工序费用（负二层）', '测量放线', '项', 367.82, 4, 1471.28, 0, 0, 0, 0, 0, 0, 1471.28);
INSERT INTO `project_two_sub_three` VALUES (7, '施工工序费用（负二层）', '内外侧双排操作架搭设', 'm2', 550, 49, 26950, 7.3, 0, 0, 0, 0, 0, 26950);
INSERT INTO `project_two_sub_three` VALUES (8, '施工工序费用（负二层）', '立柱安装(周转，仅人工费）', 't', 600, 8, 4800, 0, 0, 0, 0, 0, 0, 4800);
INSERT INTO `project_two_sub_three` VALUES (9, '施工工序费用（负二层）', '钢筋限位工装安装及调整（一次性投入，主要材料为扁钢和方钢管）', 't', 600, 25, 15000, 0, 0, 0, 0, 0, 0, 15000);
INSERT INTO `project_two_sub_three` VALUES (10, '施工工序费用（负二层）', '水平钢筋、竖向钢筋绑扎', '项', 600, 320, 192000, 0, 0, 0, 0, 0, 0, 192000);
INSERT INTO `project_two_sub_three` VALUES (11, '施工工序费用（负二层）', '单侧钢覆面埋件临时安装', '项', 600, 49, 29400, 0, 0, 0, 0, 0, 0, 29400);
INSERT INTO `project_two_sub_three` VALUES (12, '施工工序费用（负二层）', '钢覆面镶入件临时安装', '项', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (13, '施工工序费用（负二层）', '模块钢筋调整、加固', '项', 380, 10, 3800, 0, 0, 0, 0, 0, 0, 3800);
INSERT INTO `project_two_sub_three` VALUES (14, '施工工序费用（负一层）', '测量放线', '项', 367.82, 4, 1471.28, 0, 0, 0, 0, 0, 0, 1471.28);
INSERT INTO `project_two_sub_three` VALUES (15, '施工工序费用（负一层）', '内外侧双排操作架搭设', 'm2', 450, 49, 22050, 7.3, 0, 0, 0, 0, 0, 22050);
INSERT INTO `project_two_sub_three` VALUES (16, '施工工序费用（负一层）', '立柱安装(周转，仅人工费）', 't', 600, 8, 4800, 0, 0, 0, 0, 0, 0, 4800);
INSERT INTO `project_two_sub_three` VALUES (17, '施工工序费用（负一层）', '钢筋限位工装安装及调整（一次性投入，主要材料为扁钢和方钢管）', 't', 350, 25, 8750, 0, 0, 0, 0, 0, 0, 8750);
INSERT INTO `project_two_sub_three` VALUES (18, '施工工序费用（负一层）', '水平钢筋、竖向钢筋绑扎', '项', 380, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (19, '施工工序费用（负一层）', '单侧钢覆面埋件临时安装', '项', 600, 49, 29400, 0, 0, 0, 0, 0, 0, 29400);
INSERT INTO `project_two_sub_three` VALUES (20, '施工工序费用（负一层）', '钢覆面镶入件临时安装', '项', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (21, '施工工序费用（负一层）', '模块钢筋调整、加固', '项', 380, 10, 3800, 0, 0, 0, 0, 0, 0, 3800);
INSERT INTO `project_two_sub_three` VALUES (22, '施工工序费用（一层）', '测量放线', '项', 367.82, 2, 735.64, 0, 0, 0, 0, 0, 0, 735.64);
INSERT INTO `project_two_sub_three` VALUES (23, '施工工序费用（一层）', '内外侧双排操作架搭设', 'm2', 550, 0, 0, 7.3, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (24, '施工工序费用（一层）', '立柱安装(周转，仅人工费）', 't', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (25, '施工工序费用（一层）', '钢筋限位工装安装及调整（一次性投入，主要材料为扁钢和方钢管）', 't', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (26, '施工工序费用（一层）', '水平钢筋、竖向钢筋绑扎', '项', 380, 232, 88160, 0, 0, 0, 0, 0, 0, 88160);
INSERT INTO `project_two_sub_three` VALUES (27, '施工工序费用（一层）', '单侧钢覆面埋件临时安装', '项', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (28, '施工工序费用（一层）', '钢覆面镶入件临时安装', '项', 600, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (29, '施工工序费用（一层）', '模块钢筋调整、加固', '项', 380, 0, 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_three` VALUES (30, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2335466.869);

-- ----------------------------
-- Table structure for project_two_sub_two
-- ----------------------------
DROP TABLE IF EXISTS `project_two_sub_two`;
CREATE TABLE `project_two_sub_two`  (
  `sequence_number` int NULL DEFAULT NULL,
  `parameter_category` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `engineering_parameter` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `modular_labor_unit_price` double NULL DEFAULT NULL,
  `modular_labor_quantity` double NULL DEFAULT NULL,
  `modular_labor_total` double NULL DEFAULT NULL,
  `modular_material_unit_price` double NULL DEFAULT NULL,
  `modular_material_quantity` double NULL DEFAULT NULL,
  `modular_material_total` double NULL DEFAULT NULL,
  `modular_machinery_unit_price` int NULL DEFAULT NULL,
  `modular_machinery_quantity` int NULL DEFAULT NULL,
  `modular_machinery_total` int NULL DEFAULT NULL,
  `total_price` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_two_sub_two
-- ----------------------------
INSERT INTO `project_two_sub_two` VALUES (2, '钢筋生产线费用', '钢筋后台制作费用（-0.050~-5.950m段）', '吨', 258, 48.43, 12494.94, 4145, 48.43, 200742.35, 0, 0, 0, 213237.29);
INSERT INTO `project_two_sub_two` VALUES (3, '钢筋吨数', '钢筋', '吨', 0, 0, 0, 0, 261.57, 0, 0, 0, 0, 0);
INSERT INTO `project_two_sub_two` VALUES (4, '施工工序费用（6.150~-0.050m段）', '测量放线', '项', 367.82, 4, 1471.28, 0, 0, 0, 0, 0, 0, 1471.28);
INSERT INTO `project_two_sub_two` VALUES (5, '施工工序费用（6.150~-0.050m段）', '内外侧双排操作架搭设', 'm2', 550, 41, 22550, 7.3, 0, 0, 0, 0, 0, 22550);
INSERT INTO `project_two_sub_two` VALUES (6, '施工工序费用（6.150~-0.050m段）', '立柱安装', 't', 600, 7, 4200, 0, 0, 0, 0, 0, 0, 4200);
INSERT INTO `project_two_sub_two` VALUES (7, '施工工序费用（6.150~-0.050m段）', '钢筋限位工装安装及调整', 't', 350, 21, 7350, 0, 0, 0, 0, 0, 0, 7350);
INSERT INTO `project_two_sub_two` VALUES (8, '施工工序费用（6.150~-0.050m段）', '水平钢筋、竖向钢筋绑扎', '项', 380, 266, 101080, 0, 0, 0, 0, 0, 0, 101080);
INSERT INTO `project_two_sub_two` VALUES (9, '施工工序费用（6.150~-0.050m段）', '单侧钢覆面埋件临时安装', '项', 600, 41, 24600, 0, 0, 0, 0, 0, 0, 24600);
INSERT INTO `project_two_sub_two` VALUES (10, '施工工序费用（6.150~-0.050m段）', '模块起吊、落位、短柱连接', '项', 350, 31, 10850, 0, 0, 0, 0, 0, 0, 10850);
INSERT INTO `project_two_sub_two` VALUES (11, '施工工序费用（6.150~-0.050m段）', '模块竖向钢筋锥套连接', '项', 380, 1338, 28880, 132.57, 1338, 177378.66, 0, 1338, 0, 206258.66);
INSERT INTO `project_two_sub_two` VALUES (12, '施工工序费用（-0.050~-5.950m段）', '测量放线', '项', 367.82, 0, 1103.46, 0, 0, 0, 0, 0, 0, 1103.46);
INSERT INTO `project_two_sub_two` VALUES (13, '施工工序费用（-0.050~-5.950m段）', '内外侧双排操作架搭设', 'm2', 550, 0, 20350, 7.3, 0, 0, 0, 0, 0, 20350);
INSERT INTO `project_two_sub_two` VALUES (14, '施工工序费用（-0.050~-5.950m段）', '立柱安装', 't', 600, 0, 3600, 0, 0, 0, 0, 0, 0, 3600);
INSERT INTO `project_two_sub_two` VALUES (15, '施工工序费用（-0.050~-5.950m段）', '钢筋限位工装安装及调整', 't', 600, 0, 11400, 0, 0, 0, 0, 0, 0, 11400);
INSERT INTO `project_two_sub_two` VALUES (16, '施工工序费用（-0.050~-5.950m段）', '水平钢筋、竖向钢筋绑扎', '项', 600, 0, 145800, 0, 0, 0, 0, 0, 0, 145800);
INSERT INTO `project_two_sub_two` VALUES (17, '施工工序费用（-0.050~-5.950m段）', '单侧钢覆面埋件临时安装', '项', 600, 0, 22200, 0, 0, 0, 0, 0, 0, 22200);
INSERT INTO `project_two_sub_two` VALUES (18, '施工工序费用（-0.050~-5.950m段）', '模块起吊、落位、短柱连接', '项', 350, 0, 9800, 0, 0, 0, 0, 0, 0, 9800);
INSERT INTO `project_two_sub_two` VALUES (19, '施工工序费用（-0.050~-5.950m段）', '模块竖向钢筋锥套连接', '项', 380, 1241, 26600, 132.57, 1241, 164519.37, 0, 1241, 0, 191119.37);
INSERT INTO `project_two_sub_two` VALUES (20, '总价', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1230593.24);

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions`  (
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  `assigned_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `permission_id`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of role_permissions
-- ----------------------------
INSERT INTO `role_permissions` VALUES (1, 1, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 2, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 3, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 4, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 5, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 6, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 7, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (1, 8, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 1, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 3, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 4, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 5, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 6, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 7, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (2, 8, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (3, 4, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (3, 5, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (3, 6, '2025-09-07 11:25:13');
INSERT INTO `role_permissions` VALUES (3, 7, '2025-09-07 11:25:13');

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `code` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `is_system` tinyint(1) NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `ix_roles_code`(`code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, '管理员', 'super_admin', '系统最高权限管理员，拥有所有权限', 1, 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `roles` VALUES (2, '业务查看者', 'viewer', '不可以看到软件管理界面', 1, 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');
INSERT INTO `roles` VALUES (3, '普通用户', 'tech_support', '只能看到前四个部分', 1, 1, '2025-09-07 11:25:13', '2025-09-07 11:25:13');

-- ----------------------------
-- Table structure for sqlite_sequence
-- ----------------------------
DROP TABLE IF EXISTS `sqlite_sequence`;
CREATE TABLE `sqlite_sequence`  (
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `seq` int NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sqlite_sequence
-- ----------------------------
INSERT INTO `sqlite_sequence` VALUES ('计算结果', 2);
INSERT INTO `sqlite_sequence` VALUES ('工程信息', 3);
INSERT INTO `sqlite_sequence` VALUES ('参数信息', 6);

-- ----------------------------
-- Table structure for steel_lining
-- ----------------------------
DROP TABLE IF EXISTS `steel_lining`;
CREATE TABLE `steel_lining`  (
  `sequence_number` int NULL DEFAULT NULL,
  `project_code` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `quantity` double NULL DEFAULT NULL,
  `labor_cost` double NULL DEFAULT NULL,
  `material_cost` double NULL DEFAULT NULL,
  `machinery_cost` double NULL DEFAULT NULL,
  `unit_price` double NULL DEFAULT NULL,
  `total_price_ten_thousand` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of steel_lining
-- ----------------------------
INSERT INTO `steel_lining` VALUES (1, 'B001', '网架存放场地', 'm2', 1808.64, 81.88, 20.22, 10.72, 112.82, 408101.53);
INSERT INTO `steel_lining` VALUES (2, 'B002', '制作胎具', 't', 65.3, 7576, 1247, 1483, 10306.835, 672610.65);
INSERT INTO `steel_lining` VALUES (3, 'B003', '钢支墩、埋件混凝土剔凿', 'm3', 19.5, 1100.25, NULL, NULL, 1100.25, 42909.75);
INSERT INTO `steel_lining` VALUES (4, 'B004', '钢支墩、埋件混凝土回填', 'm3', 10.15, 134.64, 424.13, 0.38, 559.15, 11350.75);
INSERT INTO `steel_lining` VALUES (5, 'B005', '钢支墩、埋件安装', 'T', 0.96, 3153.6, 606.91, 427.38, 4187.89, 8037.94);
INSERT INTO `steel_lining` VALUES (6, 'B006', '钢支墩、埋件使用折旧', 't', 1.85, 2520, 3409.13, 2626.62, 8555.75, 31729.29);
INSERT INTO `steel_lining` VALUES (7, 'B007', '扶壁柱安装', 'T', 36.82, 4558.32, 351.95, 820.85, 5731.12, 422052.62);
INSERT INTO `steel_lining` VALUES (8, 'B008', '扶壁柱拆除', 'T', 36.82, 3014.12, 229.57, 550.87, 3794.56, 279439.97);
INSERT INTO `steel_lining` VALUES (9, 'B009', '扶壁柱构件使用折旧费', 'T', 36.82, 1586.43, 3715.68, 777, 6079.11, 447679.39);
INSERT INTO `steel_lining` VALUES (10, 'B010', '走道板及操作平台制作', 'T', 35.44, 3040.56, 2999.04, 302.15, 6341.75, 449480.68);
INSERT INTO `steel_lining` VALUES (11, 'B011', '走道板及操作平台搭设', 'T', 70.88, 1373.04, 450.03, 693.95, 2517.02, 356794.85);
INSERT INTO `steel_lining` VALUES (12, 'B012', '走道板及操作平台拆除', 'T', 70.88, 702, 38.29, 693.95, 1434.24, 203307.66);
INSERT INTO `steel_lining` VALUES (13, 'B013', '脚手架搭拆', 'm2', 6968.79, 28.77, 11.62, 1.64, 42.03, 585796.23);
INSERT INTO `steel_lining` VALUES (14, 'B014', '环向加固工装', 'T', 6.84, 6790.32, 1071.1, 782.94, 8644.36, 118254.84);
INSERT INTO `steel_lining` VALUES (15, 'B015', '模块就位措施', 'T', 2.79, 6790.32, 1071.1, 782.94, 8644.36, 48262.91);
INSERT INTO `steel_lining` VALUES (16, 'B016', '角钢增设', 'T', 0.62, 11364.34, 4379.9, 2169.1, 17913.34, 22074.37);
INSERT INTO `steel_lining` VALUES (17, 'B018', '人工保养吊索具', '工日', 13, 450, 0, 0, 450, NULL);
INSERT INTO `steel_lining` VALUES (18, 'B019', '吊索具使用机械倒运', '台班', 1.13, 0, 0, 5189.69, 5189.69, 11728.7);
INSERT INTO `steel_lining` VALUES (19, 'B020', '模块试吊、吊装投入的人工', '工日', 189, 450, 0, 0, 450, NULL);
INSERT INTO `steel_lining` VALUES (22, 'B023', '钢网架制作', 'T', 38.59, 2449.35, 1903.23, 1332.61, 5685.19, 219391.29);
INSERT INTO `steel_lining` VALUES (23, 'B024', '钢网架安装', 'T', 38.59, 912.25, 77.21, 597.15, 1586.61, 122454.56);
INSERT INTO `steel_lining` VALUES (24, 'B025', '钢网架拆除', 'T', 38.59, 602.09, 46.5, 394.12, 1042.71, 80476.17);
INSERT INTO `steel_lining` VALUES (25, 'B026', '模块吊耳制、安、拆', 'T', 7.5, 9804.44, 1956.19, 7341.19, 19101.82, 286527.3);
INSERT INTO `steel_lining` VALUES (26, NULL, '荷载试验人工配合', NULL, 188, 450, NULL, NULL, 450, NULL);
INSERT INTO `steel_lining` VALUES (27, '合计', '合计', NULL, NULL, NULL, NULL, NULL, NULL, 5524998.44);

-- ----------------------------
-- Table structure for tasks
-- ----------------------------
DROP TABLE IF EXISTS `tasks`;
CREATE TABLE `tasks`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `status` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `priority` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `task_type` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `progress` int NULL DEFAULT NULL,
  `start_date` datetime NULL DEFAULT NULL,
  `due_date` datetime NULL DEFAULT NULL,
  `completed_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `creator_id` int NOT NULL,
  `assignee_id` int NULL DEFAULT NULL,
  `tags` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  `attachments` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `creator_id`(`creator_id` ASC) USING BTREE,
  INDEX `assignee_id`(`assignee_id` ASC) USING BTREE,
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `tasks_ibfk_2` FOREIGN KEY (`assignee_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tasks
-- ----------------------------

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles`  (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  `assigned_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_roles
-- ----------------------------
INSERT INTO `user_roles` VALUES (1, 1, '2025-09-07 11:25:13');
INSERT INTO `user_roles` VALUES (2, 3, '2025-09-07 11:26:38');
INSERT INTO `user_roles` VALUES (3, 2, '2025-09-07 11:26:33');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `failed_login_attempts` int NULL DEFAULT NULL,
  `locked_until` datetime NULL DEFAULT NULL,
  `password_changed_at` datetime NULL DEFAULT NULL,
  `password_expires_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `last_login_at` datetime NULL DEFAULT NULL,
  `last_login_ip` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `real_name` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `department` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  `position` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `ix_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin@example.com', '$2b$12$hQQU34cEr1SaDvUveV.wEuCNaG/f41FilncuNTQkXi3rzAh5wydr2', 'active', 1, 0, NULL, '2025-09-07 09:22:04', '2025-12-06 09:22:04', '2025-09-07 09:22:04', '2025-09-08 06:58:19', '2025-09-08 06:58:19', '127.0.0.1', NULL, NULL, NULL, NULL);
INSERT INTO `users` VALUES (2, 'user', 'user@gmail.com', '$2b$12$OC8M5yZ.ev8xgVMPNu7R9.whaU8RFS3tuXRFtK7ulVW0g17Cr.fNu', 'active', 1, 0, NULL, '2025-09-07 09:22:54', '2025-12-06 09:22:54', '2025-09-07 09:22:54', '2025-09-08 01:25:46', '2025-09-08 01:25:46', '127.0.0.1', '', '', '', '');
INSERT INTO `users` VALUES (3, 'viewer', 'viewer@gmail.com', '$2b$12$4vmMcK60lRRTREBr76fvW.u2H0SpDQphG8Q3SNCHkeayNZwP8SXvm', 'active', 1, 0, NULL, '2025-09-07 11:26:27', '2025-12-06 11:26:27', '2025-09-07 11:26:27', '2025-09-08 01:24:22', '2025-09-08 01:24:22', '127.0.0.1', '', '', '', '');
INSERT INTO `users` VALUES (4, 'test', 'test@gmail.com', '$2b$12$.Mh/N4txo1p581OguaZcYufgXvbAswBQw/rWpG9jjPxvtlXrhRBy6', 'active', 1, 0, NULL, '2025-09-08 01:31:06', '2025-12-07 01:31:06', '2025-09-08 01:31:06', '2025-09-08 01:31:06', NULL, NULL, '测试', '11100011111', '', '');

SET FOREIGN_KEY_CHECKS = 1;
