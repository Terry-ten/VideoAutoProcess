#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube视频监控系统 - RSS版本
使用RSS feed监控，无需API密钥
"""

import argparse
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from database_mongodb import MongoDBManager
from youtube_rss import YouTubeRSSMonitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class YouTubeMonitorRSS:
    def __init__(self):
        self.db = MongoDBManager()
        self.rss_monitor = YouTubeRSSMonitor()
    
    def add_channel(self, channel_url: str) -> bool:
        """添加要监控的频道"""
        try:
            print(f"📡 正在获取频道信息: {channel_url}")
            
            # 获取频道信息
            channel_info = self.rss_monitor.get_channel_info(channel_url)
            if not channel_info:
                print(f"❌ 无法获取频道信息")
                return False
            
            # 保存到数据库
            success = self.db.add_channel(
                channel_id=channel_info['channel_id'],
                channel_name=channel_info['channel_name'],
                channel_url=channel_info['channel_url'],
                description=channel_info['description'],
                subscriber_count=channel_info['subscriber_count']
            )
            
            if success:
                print(f"✅ 频道添加成功!")
                print(f"   频道名称: {channel_info['channel_name']}")
                print(f"   频道ID: {channel_info['channel_id']}")
                
                # 获取并保存最新视频
                print("📥 正在获取最新视频...")
                videos = self.rss_monitor.get_latest_videos(channel_info['channel_id'], max_results=10)
                
                new_count = 0
                for video in videos:
                    if not self.db.video_exists(video['video_id']):
                        if self.db.add_video(video):
                            new_count += 1
                
                print(f"📊 添加了 {new_count} 个新视频")
                
                # 记录监控日志
                self.db.add_monitor_log(
                    channel_id=channel_info['channel_id'],
                    new_videos_count=new_count,
                    status='success',
                    message='频道添加完成'
                )
                
                return True
            else:
                print(f"❌ 频道添加失败")
                return False
                
        except Exception as e:
            logger.error(f"添加频道失败: {e}")
            print(f"❌ 添加频道时出错: {e}")
            return False
    
    def check_channel_updates(self, channel_id: str = None) -> Dict:
        """检查频道更新"""
        try:
            # 获取要检查的频道
            if channel_id:
                channels = [ch for ch in self.db.get_active_channels() if ch['channel_id'] == channel_id]
                if not channels:
                    print(f"❌ 未找到频道: {channel_id}")
                    return {'total_channels': 0, 'total_new_videos': 0}
            else:
                channels = self.db.get_active_channels()
            
            if not channels:
                print("❌ 没有可监控的频道")
                return {'total_channels': 0, 'total_new_videos': 0}
            
            print(f"🔍 开始检查 {len(channels)} 个频道的更新...")
            
            total_new_videos = 0
            
            for i, channel in enumerate(channels, 1):
                try:
                    print(f"\n[{i}/{len(channels)}] 检查频道: {channel['channel_name']}")
                    
                    # 获取最新视频发布时间
                    latest_date = self.db.get_latest_video_date(channel['channel_id'])
                    
                    # 获取RSS中的最新视频
                    videos = self.rss_monitor.get_latest_videos(channel['channel_id'], max_results=20)
                    
                    new_videos = []
                    for video in videos:
                        # 检查是否是新视频
                        if not self.db.video_exists(video['video_id']):
                            if latest_date is None or video['published_at'] > latest_date:
                                new_videos.append(video)
                    
                    # 保存新视频
                    saved_count = 0
                    for video in new_videos:
                        if self.db.add_video(video):
                            saved_count += 1
                            print(f"  📥 新视频: {video['title']}")
                    
                    total_new_videos += saved_count
                    
                    # 记录监控日志
                    self.db.add_monitor_log(
                        channel_id=channel['channel_id'],
                        new_videos_count=saved_count,
                        status='success',
                        message=f'找到 {saved_count} 个新视频'
                    )
                    
                    if saved_count == 0:
                        print(f"  ✅ 没有新视频")
                    else:
                        print(f"  ✅ 添加了 {saved_count} 个新视频")
                    
                except Exception as e:
                    logger.error(f"检查频道 {channel['channel_id']} 失败: {e}")
                    print(f"  ❌ 检查失败: {e}")
                    
                    # 记录错误日志
                    self.db.add_monitor_log(
                        channel_id=channel['channel_id'],
                        new_videos_count=0,
                        status='error',
                        message=str(e)
                    )
            
            print(f"\n🎉 检查完成! 总共发现 {total_new_videos} 个新视频")
            
            return {
                'total_channels': len(channels),
                'total_new_videos': total_new_videos
            }
            
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            print(f"❌ 检查更新时出错: {e}")
            return {'total_channels': 0, 'total_new_videos': 0}
    
    def list_channels(self):
        """列出所有监控频道"""
        try:
            channels = self.db.get_active_channels()
            
            if not channels:
                print("❌ 没有找到监控频道")
                return
            
            print(f"\n📺 监控频道列表 (共 {len(channels)} 个):")
            print("=" * 80)
            
            for i, channel in enumerate(channels, 1):
                print(f"{i}. {channel['channel_name']}")
                print(f"   频道ID: {channel['channel_id']}")
                print(f"   URL: {channel['channel_url']}")
                if channel.get('subscriber_count'):
                    print(f"   订阅者: {channel['subscriber_count']:,}")
                print(f"   添加时间: {channel['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 80)
                
        except Exception as e:
            logger.error(f"列出频道失败: {e}")
            print(f"❌ 获取频道列表时出错: {e}")
    
    def show_recent_videos(self, days: int = 7):
        """显示最近的视频"""
        try:
            videos = self.db.get_recent_videos(days)
            
            if not videos:
                print(f"❌ 最近 {days} 天没有发现新视频")
                return
            
            print(f"\n🎥 最近 {days} 天的视频 (共 {len(videos)} 个):")
            print("=" * 100)
            
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']}")
                print(f"   频道: {video['channel_name']}")
                print(f"   发布时间: {video['published_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   URL: {video['video_url']}")
                if video.get('view_count'):
                    print(f"   观看次数: {video['view_count']:,}")
                print("-" * 100)
                
        except Exception as e:
            logger.error(f"显示最近视频失败: {e}")
            print(f"❌ 获取最近视频时出错: {e}")
    
    def show_stats(self, days: int = 30):
        """显示统计信息"""
        try:
            print(f"\n📊 系统统计信息 (最近 {days} 天):")
            print("=" * 60)
            
            # 数据库统计
            db_stats = self.db.get_database_stats()
            print(f"活跃频道数: {db_stats.get('active_channels', 0)}")
            print(f"总视频数: {db_stats.get('total_videos', 0)}")
            print(f"最近7天新视频: {db_stats.get('videos_last_7_days', 0)}")
            print(f"监控日志总数: {db_stats.get('total_logs', 0)}")
            
            # 频道视频统计
            channel_stats = self.db.get_channel_video_stats()
            if channel_stats:
                print("\n📺 各频道视频数量:")
                print("-" * 40)
                for stat in channel_stats:
                    print(f"{stat['channel_name']}: {stat['total_videos']} 个视频 (最近7天: {stat['videos_last_7_days']})")
            
            # 监控统计
            monitor_stats = self.db.get_monitor_stats(days=days)
            if monitor_stats:
                print(f"\n🔍 最近 {days} 天监控统计:")
                print("-" * 40)
                for stat in monitor_stats:
                    print(f"频道ID: {stat['channel_id']}, 状态: {stat['status']}, 新视频: {stat['new_videos_count']}, 时间: {stat['check_time'].strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logger.error(f"显示统计失败: {e}")
            print(f"❌ 获取统计信息时出错: {e}")
    
    def test_system(self):
        """测试系统功能"""
        print("🔧 系统功能测试")
        print("=" * 50)
        
        try:
            # 测试数据库连接
            print("1. 测试数据库连接...")
            if self.db.test_connection():
                print("   ✅ MongoDB连接正常")
            else:
                print("   ❌ MongoDB连接失败")
                return False
            
            # 测试RSS监控
            print("2. 测试RSS监控...")
            test_url = "https://www.youtube.com/@mkbhd"
            channel_info = self.rss_monitor.get_channel_info(test_url)
            if channel_info:
                print(f"   ✅ RSS监控正常 (测试频道: {channel_info['channel_name']})")
            else:
                print("   ❌ RSS监控失败")
                return False
            
            # 测试网络连接
            print("3. 测试网络连接...")
            videos = self.rss_monitor.get_latest_videos(channel_info['channel_id'], max_results=1)
            if videos:
                print("   ✅ 网络连接正常")
            else:
                print("   ❌ 网络连接失败")
                return False
            
            print("\n🎉 所有测试通过！系统工作正常。")
            return True
            
        except Exception as e:
            logger.error(f"系统测试失败: {e}")
            print(f"❌ 系统测试时出错: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='YouTube视频监控系统 - RSS版本')
    
    parser.add_argument('command', choices=[
        'test-system', 'add-channel', 'list-channels', 
        'check-updates', 'show-recent', 'show-stats'
    ], help='要执行的命令')
    
    parser.add_argument('url_or_id', nargs='?', help='频道URL或频道ID')
    parser.add_argument('--days', type=int, default=7, help='天数 (默认: 7)')
    parser.add_argument('--channel-id', help='特定频道ID')
    
    args = parser.parse_args()
    
    # 创建监控实例
    monitor = YouTubeMonitorRSS()
    
    try:
        if args.command == 'test-system':
            monitor.test_system()
            
        elif args.command == 'add-channel':
            if not args.url_or_id:
                print("❌ 请提供频道URL")
                sys.exit(1)
            monitor.add_channel(args.url_or_id)
            
        elif args.command == 'list-channels':
            monitor.list_channels()
            
        elif args.command == 'check-updates':
            monitor.check_channel_updates(args.channel_id)
            
        elif args.command == 'show-recent':
            monitor.show_recent_videos(args.days)
            
        elif args.command == 'show-stats':
            monitor.show_stats(args.days)
            
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"❌ 程序执行时出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 