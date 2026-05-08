"""测试米游社爬虫"""
import sys
sys.path.insert(0, ".")
from crawlers.miyoushe_crawler import MiyousheCrawler

crawler = MiyousheCrawler()
posts = crawler.crawl(limit=5)

print(f"采集到 {len(posts)} 条帖子")
for i, post in enumerate(posts, 1):
    print(f"--- 帖子 {i} ---")
    print(f"ID: {post.post_id}")
    print(f"作者: {post.author}")
    print(f"内容: {post.content[:80]}...")
    print(f"点赞: {post.likes} 评论: {post.comments}")
    print(f"链接: {post.url}")
