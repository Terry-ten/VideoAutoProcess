import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from config import Config

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        self._connect()
        self._init_database()
    
    def _connect(self):
        """连接到MongoDB"""
        try:
            # 构建连接字符串
            if Config.MONGODB_USERNAME and Config.MONGODB_PASSWORD:
                # 如果有用户名密码
                connection_string = f"mongodb://{Config.MONGODB_USERNAME}:{Config.MONGODB_PASSWORD}@{Config.MONGODB_URL.replace('mongodb://', '')}"
            else:
                connection_string = Config.MONGODB_URL
            
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5秒超时
                connectTimeoutMS=10000,         # 10秒连接超时
                maxPoolSize=50                  # 连接池大小
            )
            
            # 测试连接
            self.client.admin.command('ping')
            
            self.db = self.client[Config.MONGODB_DATABASE]
            self.logger.info(f"成功连接到MongoDB数据库: {Config.MONGODB_DATABASE}")
            
        except ConnectionFailure as e:
            self.logger.error(f"MongoDB连接失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _init_database(self):
        """初始化数据库集合和索引"""
        try:
            # 创建集合（如果不存在）
            collections = ['channels', 'videos', 'monitor_logs', 'config']
            for collection_name in collections:
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(collection_name)
                    self.logger.info(f"创建集合: {collection_name}")
            
            # 创建索引
            self._create_indexes()
            
            # 插入默认配置
            self._insert_default_config()
            
            self.logger.info("MongoDB数据库初始化完成")
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建性能优化索引"""
        try:
            # channels集合索引
            self.db.channels.create_index("channel_id", unique=True)
            self.db.channels.create_index("is_active")
            self.db.channels.create_index("updated_at")
            
            # videos集合索引
            self.db.videos.create_index("video_id", unique=True)
            self.db.videos.create_index("channel_id")
            self.db.videos.create_index("published_at")
            self.db.videos.create_index("discovered_at")
            self.db.videos.create_index([("channel_id", ASCENDING), ("published_at", DESCENDING)])
            
            # monitor_logs集合索引
            self.db.monitor_logs.create_index("channel_id")
            self.db.monitor_logs.create_index("check_time")
            self.db.monitor_logs.create_index([("channel_id", ASCENDING), ("check_time", DESCENDING)])
            
            # config集合索引
            self.db.config.create_index("config_key", unique=True)
            
            self.logger.info("MongoDB索引创建完成")
            
        except Exception as e:
            self.logger.error(f"创建索引失败: {e}")
    
    def _insert_default_config(self):
        """插入默认配置"""
        try:
            default_configs = [
                {
                    'config_key': 'check_interval',
                    'config_value': '3600',
                    'description': '检查间隔（秒），默认1小时',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'config_key': 'max_videos_per_check',
                    'config_value': '50',
                    'description': '每次检查最多获取的视频数量',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'config_key': 'retention_days',
                    'config_value': '365',
                    'description': '日志保留天数',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            ]
            
            for config in default_configs:
                try:
                    self.db.config.insert_one(config)
                except DuplicateKeyError:
                    # 配置已存在，跳过
                    pass
                    
        except Exception as e:
            self.logger.error(f"插入默认配置失败: {e}")
    
    # ===== 频道管理 =====
    def add_channel(self, channel_id: str, channel_name: str, channel_url: str, 
                   description: str = None, subscriber_count: int = None) -> bool:
        """添加要监控的频道"""
        try:
            channel_doc = {
                'channel_id': channel_id,
                'channel_name': channel_name,
                'channel_url': channel_url,
                'description': description,
                'subscriber_count': subscriber_count,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_active': True
            }
            
            # 使用upsert操作，如果存在则更新，不存在则插入
            result = self.db.channels.replace_one(
                {'channel_id': channel_id},
                channel_doc,
                upsert=True
            )
            
            self.logger.info(f"添加频道成功: {channel_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加频道失败: {e}")
            return False
    
    def get_active_channels(self) -> List[Dict]:
        """获取所有活跃的监控频道"""
        try:
            channels = list(self.db.channels.find(
                {'is_active': True},
                {'_id': 0}  # 排除MongoDB的_id字段
            ).sort('channel_name', 1))
            
            return channels
            
        except Exception as e:
            self.logger.error(f"获取频道列表失败: {e}")
            return []
    
    def update_channel_status(self, channel_id: str, is_active: bool) -> bool:
        """更新频道监控状态"""
        try:
            result = self.db.channels.update_one(
                {'channel_id': channel_id},
                {
                    '$set': {
                        'is_active': is_active,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            self.logger.error(f"更新频道状态失败: {e}")
            return False
    
    # ===== 视频管理 =====
    def add_video(self, video_data: Dict) -> bool:
        """添加新视频到数据库"""
        try:
            # 准备视频文档
            video_doc = {
                'video_id': video_data['video_id'],
                'channel_id': video_data['channel_id'],
                'title': video_data['title'],
                'description': video_data.get('description', ''),
                'video_url': video_data['video_url'],
                'thumbnail_url': video_data.get('thumbnail_url', ''),
                'duration': video_data.get('duration', ''),
                'view_count': video_data.get('view_count', 0),
                'like_count': video_data.get('like_count', 0),
                'comment_count': video_data.get('comment_count', 0),
                'published_at': datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')) if isinstance(video_data['published_at'], str) else video_data['published_at'],
                'discovered_at': datetime.now(),
                'updated_at': datetime.now(),
                'tags': video_data.get('tags', []),
                'category_id': video_data.get('category_id'),
                'is_new': video_data.get('is_new', True)  # 新添加的字段，默认为新视频
            }
            
            # 使用upsert操作
            result = self.db.videos.replace_one(
                {'video_id': video_data['video_id']},
                video_doc,
                upsert=True
            )
            
            self.logger.info(f"添加视频成功: {video_data['title']}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加视频失败: {e}")
            return False
    
    def video_exists(self, video_id: str) -> bool:
        """检查视频是否已存在"""
        try:
            count = self.db.videos.count_documents({'video_id': video_id})
            return count > 0
            
        except Exception as e:
            self.logger.error(f"检查视频存在性失败: {e}")
            return False
    
    def update_video_status(self, video_ids: List[str], is_new: bool = False) -> bool:
        """更新视频的新旧状态"""
        try:
            result = self.db.videos.update_many(
                {'video_id': {'$in': video_ids}},
                {'$set': {'is_new': is_new, 'updated_at': datetime.now()}}
            )
            
            self.logger.info(f"更新了 {result.modified_count} 个视频的状态")
            return result.modified_count > 0
            
        except Exception as e:
            self.logger.error(f"更新视频状态失败: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """删除单个视频"""
        try:
            result = self.db.videos.delete_one({'video_id': video_id})
            
            if result.deleted_count > 0:
                self.logger.info(f"删除视频成功: {video_id}")
                return True
            else:
                self.logger.warning(f"未找到要删除的视频: {video_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"删除视频失败: {e}")
            return False
    
    def delete_channel_and_videos(self, channel_id: str) -> Dict[str, int]:
        """删除频道及其所有视频"""
        try:
            # 先删除该频道的所有视频
            videos_result = self.db.videos.delete_many({'channel_id': channel_id})
            videos_deleted = videos_result.deleted_count
            
            # 再删除频道记录
            channel_result = self.db.channels.delete_one({'channel_id': channel_id})
            channels_deleted = channel_result.deleted_count
            
            # 删除相关的监控日志
            logs_result = self.db.monitor_logs.delete_many({'channel_id': channel_id})
            logs_deleted = logs_result.deleted_count
            
            self.logger.info(f"删除频道完成: {channel_id}, 删除了 {videos_deleted} 个视频, {logs_deleted} 个日志")
            
            return {
                'channels_deleted': channels_deleted,
                'videos_deleted': videos_deleted,
                'logs_deleted': logs_deleted
            }
                
        except Exception as e:
            self.logger.error(f"删除频道失败: {e}")
            return {'channels_deleted': 0, 'videos_deleted': 0, 'logs_deleted': 0}
    
    def get_channel_videos(self, channel_id: str, limit: int = None) -> List[Dict]:
        """获取指定频道的所有视频"""
        try:
            query = {'channel_id': channel_id}
            
            # 构建聚合管道
            pipeline = [
                {'$match': query},
                {
                    '$lookup': {
                        'from': 'channels',
                        'localField': 'channel_id',
                        'foreignField': 'channel_id',
                        'as': 'channel_info'
                    }
                },
                {'$unwind': '$channel_info'},
                {
                    '$project': {
                        '_id': 0,
                        'video_id': 1,
                        'title': 1,
                        'video_url': 1,
                        'thumbnail_url': 1,
                        'published_at': 1,
                        'discovered_at': 1,
                        'is_new': 1,
                        'channel_name': '$channel_info.channel_name'
                    }
                },
                {'$sort': {'published_at': -1}}
            ]
            
            if limit:
                pipeline.append({'$limit': limit})
            
            result = list(self.db.videos.aggregate(pipeline))
            return result
            
        except Exception as e:
            self.logger.error(f"获取频道视频失败: {e}")
            return []
    
    def get_latest_video_date(self, channel_id: str) -> Optional[datetime]:
        """获取频道最新视频的发布日期"""
        try:
            pipeline = [
                {'$match': {'channel_id': channel_id}},
                {'$sort': {'published_at': -1}},
                {'$limit': 1},
                {'$project': {'published_at': 1}}
            ]
            
            result = list(self.db.videos.aggregate(pipeline))
            if result:
                return result[0]['published_at']
            return None
            
        except Exception as e:
            self.logger.error(f"获取最新视频日期失败: {e}")
            return None
    
    def get_recent_videos(self, days: int = 7) -> List[Dict]:
        """获取最近几天发现的视频"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    '$match': {
                        'discovered_at': {'$gte': cutoff_date}
                    }
                },
                {
                    '$lookup': {
                        'from': 'channels',
                        'localField': 'channel_id',
                        'foreignField': 'channel_id',
                        'as': 'channel_info'
                    }
                },
                {
                    '$unwind': '$channel_info'
                },
                {
                    '$project': {
                        '_id': 0,
                        'video_id': 1,
                        'title': 1,
                        'video_url': 1,
                        'published_at': 1,
                        'discovered_at': 1,
                        'channel_name': '$channel_info.channel_name',
                        'channel_url': '$channel_info.channel_url'
                    }
                },
                {
                    '$sort': {'discovered_at': -1}
                }
            ]
            
            result = list(self.db.videos.aggregate(pipeline))
            return result
            
        except Exception as e:
            self.logger.error(f"获取最近视频失败: {e}")
            return []
    
    # ===== 监控日志 =====
    def add_monitor_log(self, channel_id: str, new_videos_count: int = 0, 
                       status: str = 'success', message: str = '') -> bool:
        """添加监控日志"""
        try:
            log_doc = {
                'channel_id': channel_id,
                'check_time': datetime.now(),
                'new_videos_count': new_videos_count,
                'status': status,
                'message': message
            }
            
            self.db.monitor_logs.insert_one(log_doc)
            return True
            
        except Exception as e:
            self.logger.error(f"添加监控日志失败: {e}")
            return False
    
    def get_monitor_stats(self, channel_id: str = None, days: int = 30) -> List[Dict]:
        """获取监控统计信息"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            match_condition = {'check_time': {'$gte': cutoff_date}}
            if channel_id:
                match_condition['channel_id'] = channel_id
            
            result = list(self.db.monitor_logs.find(
                match_condition,
                {'_id': 0}
            ).sort('check_time', -1))
            
            return result
            
        except Exception as e:
            self.logger.error(f"获取监控统计失败: {e}")
            return []
    
    # ===== 配置管理 =====
    def get_config(self, key: str) -> Optional[str]:
        """获取配置值"""
        try:
            result = self.db.config.find_one({'config_key': key})
            return result['config_value'] if result else None
            
        except Exception as e:
            self.logger.error(f"获取配置失败: {e}")
            return None
    
    def set_config(self, key: str, value: str, description: str = '') -> bool:
        """设置配置值"""
        try:
            config_doc = {
                'config_key': key,
                'config_value': value,
                'description': description,
                'updated_at': datetime.now()
            }
            
            result = self.db.config.replace_one(
                {'config_key': key},
                {**config_doc, 'created_at': datetime.now()},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"设置配置失败: {e}")
            return False
    
    # ===== 清理维护 =====
    def cleanup_old_logs(self, days: int = None) -> int:
        """清理过期的监控日志"""
        days = days or Config.RETENTION_DAYS
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            result = self.db.monitor_logs.delete_many(
                {'check_time': {'$lt': cutoff_date}}
            )
            
            deleted_count = result.deleted_count
            self.logger.info(f"清理了 {deleted_count} 条过期日志")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理日志失败: {e}")
            return 0
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            stats = {}
            
            # 活跃频道数量
            stats['active_channels'] = self.db.channels.count_documents({'is_active': True})
            
            # 视频总数
            stats['total_videos'] = self.db.videos.count_documents({})
            
            # 最近7天新增视频
            cutoff_date = datetime.now() - timedelta(days=7)
            stats['videos_last_7_days'] = self.db.videos.count_documents(
                {'discovered_at': {'$gte': cutoff_date}}
            )
            
            # 日志总数
            stats['total_logs'] = self.db.monitor_logs.count_documents({})
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取数据库统计失败: {e}")
            return {}
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB连接已关闭")
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"数据库连接测试失败: {e}")
            return False
    
    # ===== 聚合查询示例 =====
    def get_channel_video_stats(self) -> List[Dict]:
        """获取每个频道的视频统计"""
        try:
            pipeline = [
                {
                    '$lookup': {
                        'from': 'videos',
                        'localField': 'channel_id',
                        'foreignField': 'channel_id',
                        'as': 'videos'
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'channel_id': 1,
                        'channel_name': 1,
                        'is_active': 1,
                        'total_videos': {'$size': '$videos'},
                        'latest_video_date': {
                            '$max': '$videos.published_at'
                        },
                        'videos_last_7_days': {
                            '$size': {
                                '$filter': {
                                    'input': '$videos',
                                    'cond': {
                                        '$gte': [
                                            '$$this.discovered_at',
                                            datetime.now() - timedelta(days=7)
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },
                {
                    '$match': {'is_active': True}
                }
            ]
            
            result = list(self.db.channels.aggregate(pipeline))
            return result
            
        except Exception as e:
            self.logger.error(f"获取频道视频统计失败: {e}")
            return [] 