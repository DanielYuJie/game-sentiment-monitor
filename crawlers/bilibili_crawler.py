# crawlers/bilibili_crawler.py
"""
B站评论爬虫
"""
import requests
import time
import random
import re
from typing import List
from core.models import PostItem


class BilibiliCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com"
        }
    
    def bv_to_av(self, bv: str) -> str:
        url = f"https://www.bilibili.com/video/{bv}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            match = re.search(r'"aid":(\d+)', resp.text)
            if match:
                return match.group(1)
        except:
            return None
    
    def get_comments(self, bv: str, max_pages: int = 5) -> List[PostItem]:
        oid = self.bv_to_av(bv)
        if not oid:
            return []
        
        posts = []
        for page in range(1, max_pages + 1):
            url = f"https://api.bilibili.com/x/v2/reply/main?type=1&oid={oid}&mode=2&pn={page}&ps=20"
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                data = resp.json()
                
                if data.get("data", {}).get("replies"):
                    for reply in data["data"]["replies"]:
                        post = PostItem(
                            post_id=f"bilibili_{reply['rpid']}",
                            platform="bilibili",
                            author=reply['member']['uname'],
                            content=reply['content']['message'],
                            post_time=int(time.time()),
                            fetch_time=int(time.time()),
                            likes=reply.get('like', 0),
                            comments=0,
                            shares=0,
                            url=f"https://www.bilibili.com/video/{bv}",
                            version="1.0"
                        )
                        posts.append(post)
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass
        return posts