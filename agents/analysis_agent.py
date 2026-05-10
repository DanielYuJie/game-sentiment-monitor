# agents/analysis_agent.py
"""AnalysisAgent - 情感分析与话题提取"""
from agents.base_agent import BaseAgent
from typing import List
from core.database import Database
from services.sentiment_service import SentimentService


class AnalysisAgent(BaseAgent):
    """情感分析Agent"""

    def __init__(self, llm_client, db: Database):
        super().__init__("AnalysisAgent", llm_client)
        self.db = db
        self.sentiment_service = SentimentService(llm_client)

    def _register_tools(self):
        self.register_tool("analyze_sentiment", self._analyze_sentiment)
        self.register_tool("get_stats", self._get_stats)

    def execute(self, platform: str = "miyoushe", limit: int = 100) -> dict:
        """执行分析：从数据库取帖子 → 情感分析 → 存结果"""
        # 1. 取帖子
        posts = self.db.get_posts(platform=platform, days=30, limit=limit)
        if not posts:
            return {"status": "no_posts", "message": f"平台 {platform} 没有帖子"}

        texts = [p["content"] for p in posts]
        post_ids = [p["post_id"] for p in posts]

        # 2. 情感分析
        results = self.sentiment_service.analyze_batch(texts, batch_size=5)

        # 3. 把post_id关联回去
        for r, post_id in zip(results, post_ids):
            r.post_id = post_id

        # 4. 存数据库
        self.db.insert_sentiment_results(results)

        # 5. 统计
        stats = self._get_stats(platform)

        return {
            "status": "success",
            "analyzed": len(results),
            "stats": stats
        }

    def _analyze_sentiment(self, platform: str = "miyoushe") -> dict:
        return self.execute(platform=platform)

    def _get_stats(self, platform: str = None) -> dict:
        return self.db.get_sentiment_stats(platform=platform)