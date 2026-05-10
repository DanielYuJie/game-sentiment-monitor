"""情感分析服务 - 使用DeepSeek API"""
import json
from typing import List
from core.llm_client import LLMClient
from core.models import SentimentResult, SentimentLabel


class SentimentService:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze_batch(self, texts: List[str], batch_size: int = 5) -> List[SentimentResult]:
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self._analyze_single_batch(batch, start_id=i)
            results.extend(batch_results)
        return results

    def _analyze_single_batch(self, batch: List[str], start_id: int = 0) -> List[SentimentResult]:
        prompt = f"""你是一个游戏社区评论情感分析专家。
分析以下游戏评论的情感倾向，返回JSON数组格式。

评论列表：
{json.dumps([{"id": i, "text": text[:200]} for i, text in enumerate(batch)], ensure_ascii=False, indent=2)}

要求：
- 返回JSON数组，每个元素包含：id, sentiment, confidence, reason
- sentiment: positive（正面）/ neutral（中性）/ negative（负面）
- confidence: 0到1之间的置信度
- reason: 一句话情感理由
- 不要用代码块包裹，直接返回JSON"""

        response = self.llm.chat([{"role": "user", "content": prompt}])

        try:
            clean = response.strip()
            if clean.startswith("`"):
                parts = clean.split("`", 2)
                clean = parts[2] if len(parts) >= 3 else parts[1]
                if clean.startswith("json"):
                    clean = clean[4:]
                clean = clean.strip()
            data = json.loads(clean)

            results = []
            for item in data:
                idx = item["id"]
                sentiment_str = item.get("sentiment", "").lower()
                if "positive" in sentiment_str or "正面" in sentiment_str:
                    sentiment = SentimentLabel.POSITIVE
                elif "negative" in sentiment_str or "负面" in sentiment_str:
                    sentiment = SentimentLabel.NEGATIVE
                else:
                    sentiment = SentimentLabel.NEUTRAL
                results.append(SentimentResult(
                    post_id=f"batch_{start_id + idx}",
                    sentiment=sentiment,
                    confidence=item.get("confidence", 0.5),
                    keywords=[],
                    aspect=""
                ))
            return results
        except Exception as e:
            print(f"[SentimentService] 解析失败: {e}")
            return []
