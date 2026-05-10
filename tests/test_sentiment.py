import sys
sys.path.insert(0, ".")

from core.database import Database
from core.llm_client import LLMClient
from core.models import SentimentLabel
from services.sentiment_service import SentimentService

# 1. 从数据库读帖子
db = Database()
with db.get_connection() as conn:
    cur = conn.execute("SELECT post_id, content FROM posts LIMIT 10")
    rows = cur.fetchall()

texts = [row[1] for row in rows]
print(f"准备分析 {len(texts)} 条帖子\n")

# 2. 调用情感分析
llm = LLMClient()
service = SentimentService(llm)

results = service.analyze_batch(texts, batch_size=5)

# 3. 打印结果
for i, r in enumerate(results):
    print(f"[{i+1}] {r.sentiment.value} (置信度: {r.confidence:.2f})")

# 4. 统计
pos = sum(1 for r in results if r.sentiment == SentimentLabel.POSITIVE)
neg = sum(1 for r in results if r.sentiment == SentimentLabel.NEGATIVE)
neu = sum(1 for r in results if r.sentiment == SentimentLabel.NEUTRAL)
print(f"\n统计: 正面={pos} 中性={neu} 负面={neg}")

