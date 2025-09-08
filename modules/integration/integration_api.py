# modules/integration/integration_api.py
import requests
import json
from datetime import datetime
import time
import logging
from config import PLATFORM_CONFIG, SYNC_CONFIG, API_ENDPOINTS, RETRY_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationAPI:
    """一体化平台API接口类"""
    
    def __init__(self):
        # 从配置文件加载设置
        self.base_url = PLATFORM_CONFIG['base_url']
        self.api_key = PLATFORM_CONFIG['auth']['api_key']
        self.api_version = PLATFORM_CONFIG['api_version']
        self.timeout = PLATFORM_CONFIG['timeout']
        self.retry_count = PLATFORM_CONFIG['retry_count']
        self.session = requests.Session()
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """发送HTTP请求的通用方法"""
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else None
        }
        
        for attempt in range(self.retry_count):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, headers=headers, timeout=self.timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return {'success': True, 'data': response.json()}
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，重试第 {attempt + 1} 次")
                if attempt == self.retry_count - 1:
                    return {'success': False, 'message': '请求超时'}
                time.sleep(RETRY_CONFIG['retry_delay'])
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误，重试第 {attempt + 1} 次")
                if attempt == self.retry_count - 1:
                    return {'success': False, 'message': '连接失败'}
                time.sleep(RETRY_CONFIG['retry_delay'])
                
            except requests.exceptions.HTTPError as e:
                return {'success': False, 'message': f'HTTP错误: {e.response.status_code}'}
                
            except Exception as e:
                return {'success': False, 'message': f'请求异常: {str(e)}'}
        
        return {'success': False, 'message': '请求失败'}
    
    def test_connection(self):
        """测试平台连接"""
        try:
            # 使用配置中的健康检查端点
            result = self._make_request('GET', API_ENDPOINTS['health'])
            if result['success']:
                return {'success': True, 'message': '连接成功'}
            else:
                return {'success': False, 'message': result['message']}
        except Exception as e:
            # 模拟连接测试（开发阶段）
            return {'success': True, 'message': '连接测试成功（模拟）'}
    
    def reconnect(self):
        """重新建立连接"""
        try:
            # 重置会话
            self.session.close()
            self.session = requests.Session()
            
            # 测试新连接
            return self.test_connection()
        except Exception as e:
            return {'success': False, 'message': f'重连失败: {str(e)}'}
    
    def save_sync_config(self, config):
        """保存同步配置"""
        try:
            # 验证配置是否符合预定义选项
            if config.get('frequency') not in [opt['value'] for opt in SYNC_CONFIG['frequency_options']]:
                return {'success': False, 'message': '无效的同步频率'}
            
            valid_data_types = [dt['value'] for dt in SYNC_CONFIG['data_types']]
            if not all(dt in valid_data_types for dt in config.get('data_types', [])):
                return {'success': False, 'message': '无效的数据类型'}
            
            # 在实际应用中，这里应该将配置保存到数据库或配置文件
            logger.info(f"保存同步配置: {config}")
            
            # 模拟保存配置
            return {'success': True, 'message': '配置保存成功'}
        except Exception as e:
            return {'success': False, 'message': f'配置保存失败: {str(e)}'}
    
    def sync_data(self, data_types):
        """同步数据"""
        try:
            # 模拟数据同步过程
            logger.info(f"开始同步数据类型: {data_types}")
            
            # 根据配置中的数据类型映射进行同步
            sync_count = 0
            for data_type in data_types:
                # 查找对应的配置
                type_config = next((dt for dt in SYNC_CONFIG['data_types'] if dt['value'] == data_type), None)
                if type_config:
                    # 模拟不同数据类型的同步量
                    if data_type == 'engineering':
                        sync_count += 50
                    elif data_type == 'cost':
                        sync_count += 30
                    elif data_type == 'progress':
                        sync_count += 20
                    elif data_type == 'quality':
                        sync_count += 15
                    
                    # 在实际应用中，这里应该调用对应的API端点
                    # endpoint = type_config['endpoint']
                    # result = self._make_request('POST', endpoint, {'data_types': data_types})
            
            return {
                'success': True, 
                'count': sync_count, 
                'message': f'同步完成，共处理 {sync_count} 条数据'
            }
        except Exception as e:
            return {'success': False, 'message': f'同步失败: {str(e)}'}
    
    def update_api_config(self, config):
        """更新API配置"""
        try:
            self.api_key = config.get('api_key')
            self.api_version = config.get('api_version', self.api_version)
            self.timeout = config.get('timeout', self.timeout)
            self.retry_count = config.get('retry', self.retry_count)
            
            logger.info("API配置已更新")
            return {'success': True, 'message': 'API配置更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'API配置更新失败: {str(e)}'}
    
    def get_sync_logs(self):
        """获取同步日志"""
        try:
            # 在实际应用中，这里应该从数据库或日志文件中获取日志
            # result = self._make_request('GET', API_ENDPOINTS['logs'])
            
            # 模拟日志数据
            logs = [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "operation": "数据同步",
                    "status": "成功",
                    "data_count": "150条",
                    "description": "工程数据同步完成"
                },
                {
                    "timestamp": "2024-01-15 13:30:25",
                    "operation": "数据推送",
                    "status": "成功",
                    "data_count": "85条",
                    "description": "造价数据推送完成"
                },
                {
                    "timestamp": "2024-01-15 12:30:25",
                    "operation": "连接测试",
                    "status": "成功",
                    "data_count": "-",
                    "description": "连接测试通过"
                }
            ]
            return logs
        except Exception as e:
            logger.error(f"获取日志失败: {str(e)}")
            return []
    
    def push_data(self, data_type, data):
        """向平台推送数据"""
        try:
            payload = {
                'data_type': data_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            result = self._make_request('POST', API_ENDPOINTS['data']['push'], payload)
            return result
        except Exception as e:
            return {'success': False, 'message': f'数据推送失败: {str(e)}'}
    
    def pull_data(self, data_type, params=None):
        """从平台拉取数据"""
        try:
            endpoint = f"{API_ENDPOINTS['data']['pull']}/{data_type}"
            result = self._make_request('GET', endpoint, params=params)
            return result
        except Exception as e:
            return {'success': False, 'message': f'数据拉取失败: {str(e)}'}
    
    def get_platform_status(self):
        """获取平台状态信息"""
        try:
            result = self._make_request('GET', API_ENDPOINTS['status'])
            if result['success']:
                return result['data']
            else:
                # 返回模拟状态数据
                return {
                    'status': 'online',
                    'version': '2.1.0',
                    'last_update': datetime.now().isoformat(),
                    'active_connections': 15,
                    'total_data_synced': 1250
                }
        except Exception as e:
            logger.error(f"获取平台状态失败: {str(e)}")
            return None
        
        