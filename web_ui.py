#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube RSS监控系统 - 网页版UI界面
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import logging
import threading
import time
import requests
import io
from datetime import datetime, timedelta
from main_rss import YouTubeMonitorRSS
from auto_monitor import AutoMonitor
from PIL import Image
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 全局变量
monitor = YouTubeMonitorRSS()
auto_monitor_process = None
monitoring_status = {"running": False, "start_time": None}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/test-system', methods=['GET'])
def test_system():
    """测试系统"""
    try:
        db_ok = monitor.db.test_connection()
        test_url = "https://www.youtube.com/@mkbhd"
        channel_info = monitor.rss_monitor.get_channel_info(test_url)
        rss_ok = channel_info is not None
        
        return jsonify({
            "success": True,
            "database": db_ok,
            "rss_monitor": rss_ok,
            "message": "系统测试完成"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """获取频道列表"""
    try:
        channels = monitor.db.get_active_channels()
        return jsonify({"success": True, "channels": channels})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/channels', methods=['POST'])
def add_channel():
    """添加频道"""
    try:
        data = request.get_json()
        channel_url = data.get('url')
        
        if not channel_url:
            return jsonify({"success": False, "error": "频道URL不能为空"})
        
        success = monitor.add_channel(channel_url)
        
        if success:
            return jsonify({"success": True, "message": "频道添加成功"})
        else:
            return jsonify({"success": False, "error": "频道添加失败"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/channels/<channel_id>', methods=['DELETE'])
def remove_channel(channel_id):
    """删除频道"""
    try:
        success = monitor.db.update_channel_status(channel_id, False)
        
        if success:
            return jsonify({"success": True, "message": "频道已删除"})
        else:
            return jsonify({"success": False, "error": "频道删除失败"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/check-updates', methods=['POST'])
def check_updates():
    """手动检查更新"""
    try:
        data = request.get_json() or {}
        channel_id = data.get('channel_id')
        
        result = monitor.check_channel_updates(channel_id)
        
        return jsonify({
            "success": True,
            "total_channels": result['total_channels'],
            "total_new_videos": result['total_new_videos'],
            "message": f"检查完成，发现 {result['total_new_videos']} 个新视频"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/videos/recent', methods=['GET'])
def get_recent_videos():
    """获取最近视频"""
    try:
        days = request.args.get('days', 7, type=int)
        videos = monitor.db.get_recent_videos(days)
        
        for video in videos:
            video['published_at'] = video['published_at'].strftime('%Y-%m-%d %H:%M:%S')
            video['discovered_at'] = video['discovered_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({"success": True, "videos": videos})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        days = request.args.get('days', 30, type=int)
        
        db_stats = monitor.db.get_database_stats()
        channel_stats = monitor.db.get_channel_video_stats()
        monitor_logs = monitor.db.get_monitor_stats(days=days)
        
        for log in monitor_logs:
            log['check_time'] = log['check_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            "success": True,
            "database_stats": db_stats,
            "channel_stats": channel_stats,
            "monitor_logs": monitor_logs[:10]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/channels/<channel_id>/videos', methods=['GET'])
def get_channel_videos(channel_id):
    """获取指定频道的所有视频"""
    try:
        videos = monitor.db.get_channel_videos(channel_id)
        
        for video in videos:
            video['published_at'] = video['published_at'].strftime('%Y-%m-%d %H:%M:%S')
            video['discovered_at'] = video['discovered_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({"success": True, "videos": videos})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/channels/<channel_id>/update', methods=['POST'])
def update_single_channel(channel_id):
    """更新单个频道"""
    try:
        result = monitor.check_channel_updates(channel_id)
        
        return jsonify({
            "success": True,
            "total_channels": result['total_channels'],
            "total_new_videos": result['total_new_videos'],
            "message": f"频道更新完成，发现 {result['total_new_videos']} 个新视频"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/videos/mark-old', methods=['POST'])
def mark_videos_as_old():
    """将视频标记为旧视频"""
    try:
        data = request.get_json()
        video_ids = data.get('video_ids', [])
        
        if not video_ids:
            return jsonify({"success": False, "error": "未提供视频ID"})
        
        success = monitor.db.update_video_status(video_ids, is_new=False)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"成功将 {len(video_ids)} 个视频标记为旧视频"
            })
        else:
            return jsonify({"success": False, "error": "更新失败"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/channel/<channel_id>')
def channel_detail(channel_id):
    """频道详情页面"""
    return render_template('channel_detail.html', channel_id=channel_id)

@app.route('/api/download-thumbnail/<video_id>')
def download_thumbnail(video_id):
    """下载视频缩略图并转换为PNG格式"""
    try:
        print(f"收到下载请求: {video_id}")
        
        # 从数据库获取视频信息
        video = monitor.db.db.videos.find_one({'video_id': video_id})
        if not video:
            print(f"视频不存在: {video_id}")
            return jsonify({"success": False, "error": "视频不存在"}), 404
        
        thumbnail_url = video.get('thumbnail_url')
        if not thumbnail_url:
            return jsonify({"success": False, "error": "缩略图URL不存在"}), 404
        
        print(f"缩略图URL: {thumbnail_url}")
        
        # 下载图片
        response = requests.get(thumbnail_url, timeout=10)
        if response.status_code != 200:
            return jsonify({"success": False, "error": "下载图片失败"}), 400
        
        # 使用PIL转换为PNG格式
        image = Image.open(io.BytesIO(response.content))
        
        # 转换为RGB模式
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 保存为PNG格式到内存
        img_io = io.BytesIO()
        image.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        # 生成文件名
        filename = f"{video.get('title', video_id)[:50]}_{video_id}.png"
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        
        print(f"生成文件: {filename}")
        
        return Response(
            img_io.getvalue(),
            mimetype='image/png',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'image/png'
            }
        )
        
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auto-monitor/status', methods=['GET'])
def get_auto_monitor_status():
    """获取自动监控状态"""
    try:
        global monitoring_status
        return jsonify({
            "success": True,
            "running": monitoring_status["running"],
            "start_time": monitoring_status["start_time"].strftime('%Y-%m-%d %H:%M:%S') if monitoring_status["start_time"] else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auto-monitor/start', methods=['POST'])
def start_auto_monitor():
    """启动自动监控"""
    try:
        global auto_monitor_process, monitoring_status
        
        if monitoring_status["running"]:
            return jsonify({"success": False, "error": "自动监控已在运行中"})
        
        # 启动独立的auto_monitor进程
        import subprocess
        auto_monitor_process = subprocess.Popen(
            ['python3', 'auto_monitor.py', '--hours', '1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        monitoring_status["running"] = True
        monitoring_status["start_time"] = datetime.now()
        
        return jsonify({
            "success": True,
            "message": "自动监控已启动"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auto-monitor/stop', methods=['POST'])
def stop_auto_monitor():
    """停止自动监控"""
    try:
        global auto_monitor_process, monitoring_status
        
        if not monitoring_status["running"]:
            return jsonify({"success": False, "error": "自动监控未运行"})
        
        if auto_monitor_process:
            auto_monitor_process.terminate()
            auto_monitor_process = None
        
        monitoring_status["running"] = False
        monitoring_status["start_time"] = None
        
        return jsonify({
            "success": True,
            "message": "自动监控已停止"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🌐 启动YouTube RSS监控系统 Web界面")
    print("📍 访问地址: http://localhost:8080")
    print("💡 按 Ctrl+C 停止服务")
    
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True) 