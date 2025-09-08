# 修改 modules/pricePrediction/test_algorithm_status.py

import mysql.connector
import json

# MySQL配置 - 直接在这里定义，避免导入问题
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'dash',
    'password': '123456',
    'database': 'dash_project',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_connection():
    """获取MySQL数据库连接"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        return None

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        conn = get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM algorithm_configs")
        count = cursor.fetchone()[0]
        print(f"✅ 数据库连接成功，找到 {count} 个算法配置")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_algorithm_status_loading():
    """测试算法状态加载"""
    print("\n🔍 测试算法配置数据...")
    
    conn = get_connection()
    if not conn:
        print("❌ 无法连接数据库")
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 检查表结构
        cursor.execute("DESCRIBE algorithm_configs")
        columns = [row['Field'] for row in cursor.fetchall()]
        print(f"📊 表字段: {columns}")
        
        required_fields = ['algorithm_name', 'construction_mode', 'status']
        missing_fields = [field for field in required_fields if field not in columns]
        if missing_fields:
            print(f"⚠️ 缺少必要字段: {missing_fields}")
        else:
            print("✅ 必要字段都存在")
        
        # 查看钢筋笼模式的算法
        cursor.execute("""
            SELECT algorithm_name, status 
            FROM algorithm_configs 
            WHERE construction_mode = 'steel_cage'
            ORDER BY algorithm_name
        """)
        steel_cage_results = cursor.fetchall()
        
        print(f"\n🔧 钢筋笼模式算法 ({len(steel_cage_results)}个):")
        enabled_count = 0
        for row in steel_cage_results:
            name = row['algorithm_name']
            status = row['status']
            status_icon = "🟢" if status == 'enabled' else "🔴"
            print(f"   {status_icon} {name}: {status}")
            if status == 'enabled':
                enabled_count += 1
        print(f"   📊 启用: {enabled_count}个, 停用: {len(steel_cage_results)-enabled_count}个")
        
        # 查看钢衬里模式的算法
        cursor.execute("""
            SELECT algorithm_name, status 
            FROM algorithm_configs 
            WHERE construction_mode = 'steel_lining'
            ORDER BY algorithm_name
        """)
        steel_lining_results = cursor.fetchall()
        
        print(f"\n🔧 钢衬里模式算法 ({len(steel_lining_results)}个):")
        enabled_count = 0
        for row in steel_lining_results:
            name = row['algorithm_name']
            status = row['status']
            status_icon = "🟢" if status == 'enabled' else "🔴"
            print(f"   {status_icon} {name}: {status}")
            if status == 'enabled':
                enabled_count += 1
        print(f"   📊 启用: {enabled_count}个, 停用: {len(steel_lining_results)-enabled_count}个")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    finally:
        conn.close()

def test_algorithm_name_mapping():
    """测试算法名称映射"""
    print("\n🔍 测试算法名称映射...")
    
    # 定义映射关系
    ALGORITHM_NAME_MAPPING = {
        "线性回归": "岭回归 (RidgeCV)",
        "神经网络": "神经网络 (MLPRegressor)",
        "决策树": "决策树 (Decision Tree)",
        "随机森林": "随机森林 (Random Forest)",
        "支持向量机": "支持向量回归 (SVR)"
    }
    
    print("📋 预期的算法名称映射:")
    for db_name, code_name in ALGORITHM_NAME_MAPPING.items():
        print(f"   数据库: {db_name} -> 代码: {code_name}")
    
    # 检查数据库中是否有这些算法
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            print("\n🔍 检查数据库中的算法名称:")
            for db_name in ALGORITHM_NAME_MAPPING.keys():
                cursor.execute(
                    "SELECT COUNT(*) FROM algorithm_configs WHERE algorithm_name = %s", 
                    (db_name,)
                )
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   ✅ {db_name} 在数据库中找到 ({count}条记录)")
                else:
                    print(f"   ❌ {db_name} 在数据库中未找到")
        finally:
            conn.close()

def test_algorithm_status_info():
    """测试算法状态统计"""
    print("\n🔍 算法状态统计...")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 按模式和状态统计
        cursor.execute("""
            SELECT construction_mode, status, COUNT(*) as count
            FROM algorithm_configs 
            GROUP BY construction_mode, status
            ORDER BY construction_mode, status
        """)
        stats = cursor.fetchall()
        
        print("📊 算法状态统计:")
        for stat in stats:
            mode = stat['construction_mode']
            status = stat['status']
            count = stat['count']
            status_icon = "🟢" if status == 'enabled' else "🔴"
            print(f"   {mode}: {status_icon} {status} = {count}个")
        
        # 可用性评估
        print("\n🎯 预测功能可用性评估:")
        for mode in ['steel_cage', 'steel_lining']:
            cursor.execute("""
                SELECT COUNT(*) FROM algorithm_configs 
                WHERE construction_mode = %s AND status = 'enabled'
            """, (mode,))
            result = cursor.fetchone()
            enabled_count = result[0] if result else 0
            
            if enabled_count == 0:
                status = "❌ 不可用 (所有算法已停用)"
            elif enabled_count == 1:
                status = "⚠️ 可用但可靠性低 (仅1个算法)"
            else:
                status = f"✅ 正常可用 ({enabled_count}个算法)"
            
            print(f"   {mode}: {status}")
    
    except mysql.connector.Error as e:
        print(f"❌ 统计查询失败: {e}")
    finally:
        conn.close()

def main():
    """主测试函数"""
    print("🧪 开始算法状态功能测试...")
    print("=" * 60)
    
    # 1. 测试数据库连接
    if not test_database_connection():
        print("❌ 数据库连接失败，终止测试")
        return
    
    # 2. 测试算法状态加载
    test_algorithm_status_loading()
    
    # 3. 测试算法名称映射
    test_algorithm_name_mapping()
    
    # 4. 测试算法状态统计
    test_algorithm_status_info()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("\n💡 测试结果说明:")
    print("   ✅ 表示功能正常")
    print("   ❌ 表示需要修复")
    print("   ⚠️ 表示需要注意")
    print("\n💡 下一步:")
    print("   1. 如果所有测试通过，可以测试网页界面")
    print("   2. 可以手动在数据管理模块中修改算法状态来测试效果")

if __name__ == "__main__":
    main()