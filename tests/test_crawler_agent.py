import sys
sys.path.insert(0, ".")

from core.database import Database
from agents.crawler_agent import CrawlerAgent

db = Database()
agent = CrawlerAgent(llm_client=None, db=db)

result = agent.run(platforms=["miyoushe"], limit=5)
print(f"\n采集结果: {result}")

# 用sql查一下数据库
with db.get_connection() as conn:
    cur = conn.execute("SELECT COUNT(*) FROM posts WHERE platform='miyoushe'")
    count = cur.fetchone()[0]
    print(f"数据库现有米游社帖子数: {count}")
