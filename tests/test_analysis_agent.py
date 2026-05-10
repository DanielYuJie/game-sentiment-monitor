import sys
sys.path.insert(0, ".")

from core.database import Database
from core.llm_client import LLMClient
from agents.analysis_agent import AnalysisAgent

db = Database()
llm = LLMClient()
agent = AnalysisAgent(llm, db)

result = agent.run(platform="miyoushe", limit=10)
print(f"\n分析结果: {result}")

stats = agent._get_stats("miyoushe")
print(f"\n情感统计: {stats}")
