#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube RSS监控系统 - 无需API密钥
使用YouTube的RSS feed获取频道视频信息
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import logging

class YouTubeRSSMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract_channel_id(self, url: str) -> Optional[str]:
        """从各种YouTube URL格式提取频道ID"""
        try:
            # 直接的频道ID URL
            if '/channel/' in url:
                return url.split('/channel/')[-1].split('/')[0].split('?')[0]
            
            # @username 格式
            if '/@' in url:
                username = url.split('/@')[-1].split('/')[0].split('?')[0]
                return self._get_channel_id_from_username(username)
            
            # /c/channelname 格式  
            if '/c/' in url:
                channel_name = url.split('/c/')[-1].split('/')[0].split('?')[0]
                return self._get_channel_id_from_custom_name(channel_name)
            
            # /user/ 格式
            if '/user/' in url:
                username = url.split('/user/')[-1].split('/')[0].split('?')[0]
                return self._get_channel_id_from_username(username)
            
            return None
            
        except Exception as e:
            self.logger.error(f"提取频道ID失败: {e}")
            return None
    
    def _get_channel_id_from_username(self, username: str) -> Optional[str]:
        """通过用户名获取频道ID"""
        try:
            # 尝试访问频道主页获取真实的频道ID
            url = f"https://www.youtube.com/@{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # 从页面HTML中提取频道ID
                pattern = r'"channelId":"([^"]+)"'
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
                
                # 备用方案：查找其他模式
                pattern = r'externalId":"([^"]+)"'
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"通过用户名获取频道ID失败: {e}")
            return None
    
    def _get_channel_id_from_custom_name(self, custom_name: str) -> Optional[str]:
        """通过自定义名称获取频道ID"""
        try:
            url = f"https://www.youtube.com/c/{custom_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                pattern = r'"channelId":"([^"]+)"'
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"通过自定义名称获取频道ID失败: {e}")
            return None
    
    def get_channel_info(self, channel_url: str) -> Optional[Dict]:
        """获取频道信息"""
        try:
            channel_id = self.extract_channel_id(channel_url)
            if not channel_id:
                self.logger.error("无法提取频道ID")
                return None
            
            # 获取频道RSS信息
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            response = self.session.get(rss_url, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"获取RSS失败: {response.status_code}")
                return None
            
            # 解析RSS XML
            root = ET.fromstring(response.content)
            
            # 提取频道信息
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'yt': 'http://www.youtube.com/xml/schemas/2015',
                'media': 'http://search.yahoo.com/mrss/'
            }
            
            title = root.find('.//atom:title', ns)
            author = root.find('.//atom:author/atom:name', ns)
            
            channel_info = {
                'channel_id': channel_id,
                'channel_name': title.text if title is not None else 'Unknown',
                'channel_url': channel_url,
                'rss_url': rss_url,
                'description': f"通过RSS监控的频道",
                'subscriber_count': None  # RSS中没有订阅者数量
            }
            
            return channel_info
            
        except Exception as e:
            self.logger.error(f"获取频道信息失败: {e}")
            return None
    
    def get_latest_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """获取频道最新视频"""
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            response = self.session.get(rss_url, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"获取RSS失败: {response.status_code}")
                return []
            
            # 解析RSS XML
            root = ET.fromstring(response.content)
            
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'yt': 'http://www.youtube.com/xml/schemas/2015',
                'media': 'http://search.yahoo.com/mrss/'
            }
            
            videos = []
            entries = root.findall('.//atom:entry', ns)
            
            for entry in entries[:max_results]:
                try:
                    # 提取视频信息
                    video_id = entry.find('.//yt:videoId', ns)
                    title = entry.find('.//atom:title', ns)
                    published = entry.find('.//atom:published', ns)
                    updated = entry.find('.//atom:updated', ns)
                    link = entry.find('.//atom:link[@rel="alternate"]', ns)
                    
                    # 媒体信息
                    media_group = entry.find('.//media:group', ns)
                    description = None
                    thumbnail_url = None
                    
                    if media_group is not None:
                        desc_elem = media_group.find('.//media:description', ns)
                        if desc_elem is not None:
                            description = desc_elem.text
                        
                        thumb_elem = media_group.find('.//media:thumbnail', ns)
                        if thumb_elem is not None:
                            thumbnail_url = thumb_elem.get('url')
                    
                    video_data = {
                        'video_id': video_id.text if video_id is not None else '',
                        'channel_id': channel_id,
                        'title': title.text if title is not None else 'Unknown',
                        'description': description or '',
                        'video_url': link.get('href') if link is not None else '',
                        'published_at': self._parse_datetime(published.text) if published is not None else datetime.now(),
                        'updated_at': self._parse_datetime(updated.text) if updated is not None else datetime.now(),
                        'thumbnail_url': thumbnail_url,
                        'duration': None,  # RSS中没有时长信息
                        'view_count': None,  # RSS中没有观看次数
                        'like_count': None,  # RSS中没有点赞数
                        'comment_count': None  # RSS中没有评论数
                    }
                    
                    videos.append(video_data)
                    
                except Exception as e:
                    self.logger.error(f"解析视频条目失败: {e}")
                    continue
            
            return videos
            
        except Exception as e:
            self.logger.error(f"获取最新视频失败: {e}")
            return []
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """解析RSS中的时间格式"""
        try:
            # RSS时间格式: 2024-01-15T10:00:00+00:00
            if 'T' in datetime_str:
                datetime_str = datetime_str.split('+')[0].split('Z')[0]
                return datetime.fromisoformat(datetime_str)
            else:
                return datetime.now()
        except:
            return datetime.now()

def test_rss_monitor():
    """测试RSS监控功能"""
    print("🔧 测试YouTube RSS监控系统")
    print("=" * 50)
    
    monitor = YouTubeRSSMonitor()
    
    # 测试频道
    test_urls = [
        "https://www.youtube.com/@mkbhd",
        "https://www.youtube.com/@veritasium",
    ]
    
    for url in test_urls:
        print(f"\n测试频道: {url}")
        print("-" * 30)
        
        # 获取频道信息
        channel_info = monitor.get_channel_info(url)
        if channel_info:
            print(f"✓ 频道名称: {channel_info['channel_name']}")
            print(f"✓ 频道ID: {channel_info['channel_id']}")
            
            # 获取最新视频
            videos = monitor.get_latest_videos(channel_info['channel_id'], max_results=3)
            print(f"✓ 找到 {len(videos)} 个视频")
            
            for i, video in enumerate(videos, 1):
                print(f"  {i}. {video['title']}")
                print(f"     发布: {video['published_at'].strftime('%Y-%m-%d %H:%M')}")
                print(f"     URL: {video['url']}")
                
        else:
            print("❌ 获取频道信息失败")

if __name__ == '__main__':
    test_rss_monitor() 