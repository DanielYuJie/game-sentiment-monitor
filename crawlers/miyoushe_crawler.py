"""米游社爬虫 - 基于API采集"""
import requests
import time
from typing import List
from datetime import datetime
from core.models import PostItem
from crawlers.base_crawler import BaseCrawler


class MiyousheCrawler(BaseCrawler):
    """米游社崩铁版块爬虫"""

    platform = "miyoushe"

    def __init__(self, forum_id: str = "52"):
        self.forum_id = forum_id
        self.base_url = "https://bbs-api.miyoushe.com/post/wapi/getForumPostList"
        self.seen_ids = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def crawl(self, keyword: str = "", limit: int = 100) -> List[PostItem]:
        posts = []
        last_id = ""

        while len(posts) < limit:
            params = {
                "forum_id": self.forum_id,
                "is_good": "false",
                "is_hot": "true",
                "page_size": 20,
                "sort_type": 1,
                "last_id": last_id
            }

            try:
                resp = self.session.get(self.base_url, params=params, timeout=10)
                data = resp.json()
            except Exception as e:
                print(f"[米游社] 请求失败: {e}")
                break

            post_list = data.get("data", {}).get("list", [])
            if not post_list:
                print("[米游社] 没有更多数据")
                break

            for item in post_list:
                post_data = item.get("post", {})
                post_id = str(post_data.get("post_id", ""))
                if post_id in self.seen_ids:
                    continue
                self.seen_ids.add(post_id)

                post = self._convert_to_postitem(item)
                if keyword and keyword not in post.content:
                    continue
                posts.append(post)

            last_id = data.get("data", {}).get("last_id", "")
            time.sleep(1)

        print(f"[米游社] 采集完成，共 {len(posts)} 条")
        return posts

    def _convert_to_postitem(self, item: dict) -> PostItem:
        post_data = item.get("post", {})
        user_data = item.get("user", {})
        stat_data = item.get("stat", {})

        content = post_data.get("subject", "")
        structured = post_data.get("content", "")
        if isinstance(structured, list):
            text = " ".join(
                block.get("text", "") for block in structured
                if isinstance(block, dict)
            )
            content = content + " " + text if content else text

        return PostItem(
            post_id=f"miyoushe_{post_data.get('post_id', '')}",
            platform="miyoushe",
            author=user_data.get("nickname", "unknown"),
            content=content,
            post_time=datetime.fromtimestamp(post_data["created_at"]) if isinstance(post_data.get("created_at"), int) else (datetime.strptime(post_data["created_at"], "%Y-%m-%d %H:%M:%S") if post_data.get("created_at") else datetime.now()),
            likes=stat_data.get("like_num", 0),
            comments=stat_data.get("reply_num", 0),
            shares=0,
            url=f"https://www.miyoushe.com/sr/post/{post_data.get('post_id', '')}"
        )


