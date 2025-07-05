import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # YouTube API配置
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    # 数据库配置
    # MongoDB配置
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'youtube_monitor')
    
    # 如果需要认证
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
    
    # 监控配置
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 3600))  # 默认1小时
    MAX_VIDEOS_PER_CHECK = int(os.getenv('MAX_VIDEOS_PER_CHECK', 50))
    RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', 365))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'youtube_monitor.log')
    
    # 安全配置
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def validate(cls):
        """验证关键配置是否存在"""
        if not cls.YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY 未设置，请在.env文件中配置")
        return True 