"""
B站崩铁视频评论采集测试
"""
import requests
import sqlite3
import time

# B站API - 崩铁分区 (rid=29)
url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=29&type=0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com"
}

print("正在获取崩铁区视频列表...")

try:
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    
    if data['code'] == 0:
        videos = data['data']['list'][:5]  # 只取前5条
        
        print(f"获取到 {len(videos)} 条视频")
        
        # 连接数据库
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        for video in videos:
            bvid = video['bvid']
            title = video['title']
            author = video['owner']['name']
            stat = video['stat']
            publish_time = video['pubdate']
            
            print(f"视频: {title}")
            
            # 插入数据库
            cursor.execute("""
                INSERT OR IGNORE INTO posts 
                (post_id, platform, author, content, post_time, likes, comments, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bvid,
                'bilibili',
                author,
                title,
                publish_time,
                stat['like'],
                stat['reply'],
                f"https://www.bilibili.com/video/{bvid}"
            ))
        
        conn.commit()
        conn.close()
        print("完成！")
    else:
        print(f"API错误: {data['message']}")
        
except Exception as e:
    print(f"错误: {e}")