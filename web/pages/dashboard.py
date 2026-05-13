import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import jieba
import os
# 一键全流程按钮
st.subheader("🎯 全流程一键运行")

col1, col2 = st.columns(2)

if col1.button("🚀 一键采集+分析"):
    with st.spinner("全流程运行中，请等待..."):
        try:
            from crawlers.bilibili_crawler import BilibiliCrawler
            from crawlers.miyoushe_crawler import MiyousheCrawler
            from core.database import Database
            from core.llm_client import LLMClient
            from agents.analysis_agent import AnalysisAgent
            
            db = Database()
            llm = LLMClient()
            agent = AnalysisAgent(llm, db)
            
            all_count = 0
            
            # 1. 爬取米游社
            st.write("📱 采集米游社数据...")
            miyo = MiyousheCrawler()
            miyo_posts = miyo.crawl(keyword="星穹铁道", limit=50)
            db.insert_posts(miyo_posts)
            st.write(f"  米游社: {len(miyo_posts)} 条")
            all_count += len(miyo_posts)
            
            # 2. 爬取B站
            st.write("🎬 采集B站数据...")
            bili = BilibiliCrawler()
            bv_list = ['BV16p9UBgEhT', 'BV1tphVeWE2y', 'BV1gYd3BdENv']
            bili_posts = []
            for bv in bv_list:
                posts = bili.get_comments(bv, max_pages=5)
                bili_posts.extend(posts)
            db.insert_posts(bili_posts)
            st.write(f"  B站: {len(bili_posts)} 条")
            all_count += len(bili_posts)
            
            # 3. 情感分析
            st.write("🧠 情感分析...")
            result = agent.run(platform='miyoushe', limit=200)
            result2 = agent.run(platform='bilibili', limit=200)
            
            stats = result.get('result', {}).get('stats', {})
            stats2 = result2.get('result', {}).get('stats', {})
            
            st.success(f"✅ 全流程完成！共采集 {all_count} 条，情感分析完成")
            st.balloons()
        except Exception as e:
            st.error(f"出错: {str(e)}")

if col2.button("🔄 刷新页面"):
    st.rerun()
# 简洁白色主题
st.markdown("""
<style>
    /* 白色背景 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 标题 */
    h1 {
        color: #1a1a2e !important;
        text-align: center;
        font-family: 'Microsoft YaHei', sans-serif;
        font-size: 2.5rem !important;
        padding: 20px 0;
    }
    
    /* 子标题 */
    h2 {
        color: #2d3748 !important;
        border-left: 4px solid #667eea;
        padding-left: 15px;
        margin: 30px 0 20px 0;
    }
    
    /* 指标卡片 - 蓝色 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 指标数字 */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        font-weight: bold;
    }
    
    /* 指标标签 */
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        opacity: 0.9;
    }
    
    /* 成功数字 */
    .positive { color: #10b981 !important; }
    
    /* 警告数字 */
    .negative { color: #ef4444 !important; }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    
    /* 表格 */
    .dataframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="游戏社区氛围监控", page_icon="🎮", layout="wide")

st.title("🎮 游戏社区氛围监控仪表盘")

# 连接数据库
db_path = 'data/database.db'
conn = sqlite3.connect(db_path)

# ========== 基础统计 ==========
col1, col2, col3 = st.columns(3)

# 帖子总数
posts = pd.read_sql("SELECT COUNT(*) as count FROM posts", conn)
with col1:
    st.metric("总帖子数", posts['count'].iloc[0])

# 情感分布
sentiments = pd.read_sql("""
    SELECT sentiment, COUNT(*) as count 
    FROM sentiment_results 
    GROUP BY sentiment
""", conn)

# 正面数
positive = sentiments[sentiments['sentiment'] == 'positive']['count'].sum() if 'positive' in sentiments['sentiment'].values else 0
with col2:
    st.metric("😊 正面", positive)

# 负面数
negative = sentiments[sentiments['sentiment'] == 'negative']['count'].sum() if 'negative' in sentiments['sentiment'].values else 0
with col3:
    st.metric("😞 负面", negative)

# ========== 多平台对比 ==========
st.subheader("多平台对比")

# 获取各平台数据
platform_stats = pd.read_sql("""
    SELECT p.platform, sr.sentiment, COUNT(*) as count
    FROM posts p
    JOIN sentiment_results sr ON p.post_id = sr.post_id
    GROUP BY p.platform, sr.sentiment
""", conn)

if not platform_stats.empty:
    # 转换为透视表
    platform_pivot = platform_stats.pivot_table(
        index='platform', 
        columns='sentiment', 
        values='count', 
        fill_value=0
    )
    
    # 显示对比柱状图
    st.bar_chart(platform_pivot)
    
    # 平台帖子数统计
    platform_counts = pd.read_sql("""
        SELECT p.platform, COUNT(*) as total,
               SUM(CASE WHEN sr.sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
               SUM(CASE WHEN sr.sentiment = 'negative' THEN 1 ELSE 0 END) as negative
        FROM posts p
        LEFT JOIN sentiment_results sr ON p.post_id = sr.post_id
        GROUP BY p.platform
    """, conn)
    
    st.dataframe(platform_counts, use_container_width=True)
else:
    st.info("暂无平台对比数据")

# ========== 情感分布图 ==========
st.subheader("📊 情感分布")

if not sentiments.empty:
    st.bar_chart(sentiments.set_index('sentiment'))
else:
    st.info("暂无情感分析数据")

# ========== 情感趋势图 ==========
st.subheader("📈 情感趋势")

# 查询每日情感统计
trend = pd.read_sql("""
    SELECT DATE(sr.created_at) as date,
           sr.sentiment,
           COUNT(*) as count
    FROM sentiment_results sr
    GROUP BY DATE(sr.created_at), sr.sentiment
    ORDER BY date
""", conn)

if not trend.empty:
    # 转换为透视表
    trend_pivot = trend.pivot(index='date', columns='sentiment', values='count').fillna(0)
    st.line_chart(trend_pivot)
else:
    st.info("暂无趋势数据")

# ========== 关键词展示 ==========
st.subheader("🔑 高频关键词")

df = pd.read_sql("SELECT content FROM posts WHERE content IS NOT NULL AND content != ''", conn)

if not df.empty:
    text = ' '.join(df['content'].tolist())
    words = jieba.lcut(text)
    
    # 过滤
    stopwords = {'的', '了', '是', '我', '你', '他', '这', '那', '就', '都', '在', '和', '有', '个', '一', '不', '也', '很', '着'}
    words = [w for w in words if len(w) > 1 and w not in stopwords]
    
    # 统计词频
    from collections import Counter
    word_count = Counter(words)
    top_words = word_count.most_common(20)
    
    st.write("TOP 20 高频词：")
    cols = st.columns(4)
    for i, (word, count) in enumerate(top_words):
        with cols[i % 4]:
            st.metric(word, count)
else:
    st.info("暂无帖子内容")
    # 显示