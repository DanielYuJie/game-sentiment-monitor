# run_pipeline.py
# 一键运行：爬取B站 -> 导入数据库 -> 情感分析

import sys
sys.path.insert(0, '.')

from crawlers.bilibili_crawler import BilibiliCrawler
from core.database import Database
from core.llm_client import LLMClient
from agents.analysis_agent import AnalysisAgent

def main():
    print("=" * 50)
    print("游戏社区舆情监控 - 一键运行")
    print("=" * 50)
    
    db = Database()
    llm = LLMClient()
    agent = AnalysisAgent(llm, db)
    
    # 1. 爬取B站数据
    print("\n[1/3] 爬取B站崩铁官方数据...")
    crawler = BilibiliCrawler()
    posts = crawler.crawl_up_comments("1340190821", video_count=5, comment_pages=3)
    print(f"获取到 {len(posts)} 条评论")
    
    # 2. 导入数据库
    print("\n[2/3] 导入数据库...")
    db.insert_posts(posts)
    print("导入成功")
    
    # 3. 情感分析
    print("\n[3/3] 情感分析...")
    result = agent.run(platform='bilibili', limit=100)
    print(f"分析完成: {result['result']}")
    
    print("\n" + "=" * 50)
    print("全部完成！启动 Web 页面查看结果")
    print("=" * 50)

if __name__ == "__main__":
    main()