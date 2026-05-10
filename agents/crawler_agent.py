# agents/crawler_agent.py
"""CrawlerAgent - 统一调度各平台爬虫"""
from agents.base_agent import BaseAgent
from typing import List, Optional
from core.database import Database
from crawlers.miyoushe_crawler import MiyousheCrawler


class CrawlerAgent(BaseAgent):
    """数据采集Agent"""

    def __init__(self, llm_client, db: Database):
        super().__init__("CrawlerAgent", llm_client)
        self.db = db

        # 初始化爬虫（目前只有米游社）
        self.crawlers = {
            "miyoushe": MiyousheCrawler()
        }

    def _register_tools(self):
        """注册采集工具"""
        self.register_tool("crawl_platform", self._crawl_platform)
        self.register_tool("crawl_all", self._crawl_all)

    def execute(self, platforms: List[str] = None, keywords: List[str] = None,
                limit: int = 100) -> dict:
        """
        执行采集任务

        Args:
            platforms: 要采集的平台列表，默认 ["miyoushe"]
            keywords: 关键词列表
            limit: 每个平台采集数量
        """
        platforms = platforms or ["miyoushe"]
        all_posts = []

        for platform in platforms:
            for keyword in (keywords or [""]):
                posts = self._crawl_platform(platform, keyword, limit)
                all_posts.extend(posts)

        # 存入数据库
        if all_posts:
            self.db.insert_posts(all_posts)

        return {
            "total_posts": len(all_posts),
            "platforms": platforms
        }

    def _crawl_platform(self, platform: str, keyword: str = "",
                         limit: int = 100) -> List:
        """采集单个平台"""
        if platform not in self.crawlers:
            print(f"[CrawlerAgent] 不支持的平台: {platform}")
            return []

        crawler = self.crawlers[platform]
        print(f"[CrawlerAgent] 开始采集 {platform}...")
        posts = crawler.crawl(keyword=keyword, limit=limit)
        print(f"[CrawlerAgent] {platform} 采集完成，获得 {len(posts)} 条")
        return posts

    def _crawl_all(self, limit: int = 100) -> dict:
        """采集所有已配置平台"""
        platforms = list(self.crawlers.keys())
        return self.execute(platforms=platforms, limit=limit)