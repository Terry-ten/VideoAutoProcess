#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube RSS监控系统 - 自动定时监控
每小时自动检查频道更新并加入数据库
"""

import time
import schedule
import logging
import signal
import sys
from datetime import datetime
from main_rss import YouTubeMonitorRSS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutoMonitor:
    def __init__(self):
        self.monitor = YouTubeMonitorRSS()
        self.running = True
        
        # 设置信号处理器，优雅退出
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        print(f"\n收到退出信号 {signum}，正在停止监控...")
        self.running = False
    
    def check_updates_job(self):
        """定时任务：检查更新"""
        try:
            print(f"\n🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动检查更新...")
            logger.info("开始自动检查更新")
            
            # 执行更新检查
            result = self.monitor.check_channel_updates()
            
            total_channels = result.get('total_channels', 0)
            total_new_videos = result.get('total_new_videos', 0)
            
            print(f"✅ 检查完成: {total_channels} 个频道, 发现 {total_new_videos} 个新视频")
            logger.info(f"自动检查完成: {total_channels} 个频道, {total_new_videos} 个新视频")
            
            if total_new_videos > 0:
                print(f"🎉 发现 {total_new_videos} 个新视频已添加到数据库!")
            
        except Exception as e:
            error_msg = f"自动检查更新失败: {e}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
    
    def start_monitoring(self, interval_hours: int = 1):
        """开始自动监控"""
        print("🎬 YouTube RSS自动监控系统")
        print("=" * 50)
        print(f"⏰ 监控间隔: 每 {interval_hours} 小时")
        print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💡 按 Ctrl+C 停止监控")
        print("=" * 50)
        
        # 立即执行一次检查
        print("🚀 执行首次检查...")
        self.check_updates_job()
        
        # 设置定时任务
        schedule.every(interval_hours).hours.do(self.check_updates_job)
        
        logger.info(f"自动监控启动，间隔 {interval_hours} 小时")
        
        # 主循环
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次是否有待执行的任务
                
        except KeyboardInterrupt:
            pass
        finally:
            print("\n👋 自动监控已停止")
            logger.info("自动监控已停止")
    
    def get_next_run_time(self):
        """获取下次运行时间"""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = jobs[0].next_run
            return next_run.strftime('%Y-%m-%d %H:%M:%S')
        return "未设置"
    
    def show_status(self):
        """显示监控状态"""
        try:
            # 获取频道统计
            channels = self.monitor.db.get_active_channels()
            db_stats = self.monitor.db.get_database_stats()
            
            print("\n📊 监控系统状态")
            print("-" * 30)
            print(f"活跃频道数: {len(channels)}")
            print(f"总视频数: {db_stats.get('total_videos', 0)}")
            print(f"最近7天新视频: {db_stats.get('videos_last_7_days', 0)}")
            print(f"下次检查时间: {self.get_next_run_time()}")
            print()
            
            if channels:
                print("📺 监控频道:")
                for i, channel in enumerate(channels, 1):
                    print(f"  {i}. {channel['channel_name']}")
            
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube RSS自动监控系统')
    parser.add_argument('--hours', type=int, default=1, help='监控间隔小时数 (默认: 1)')
    parser.add_argument('--status', action='store_true', help='显示当前状态')
    parser.add_argument('--test', action='store_true', help='执行一次测试检查')
    
    args = parser.parse_args()
    
    auto_monitor = AutoMonitor()
    
    try:
        if args.status:
            # 显示状态
            auto_monitor.show_status()
        elif args.test:
            # 测试检查
            print("🧪 执行测试检查...")
            auto_monitor.check_updates_job()
        else:
            # 开始自动监控
            auto_monitor.start_monitoring(args.hours)
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 