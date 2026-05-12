# core/database.py
import sqlite3
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime
from core.models import PostItem, SentimentResult, SentimentLabel, Alert, Report


class Database:
    """SQLite数据库封装 — 增删改查统一走这里"""

    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        self.init_tables()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_tables(self):
        """建表 — 只在首次运行时创建"""
        with self.get_connection() as conn:
            # posts表：原始帖子数据
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    post_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    author TEXT,
                    content TEXT NOT NULL,
                    post_time TIMESTAMP NOT NULL,
                    fetch_time TIMESTAMP NOT NULL,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    url TEXT,
                    version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # sentiment_results表：情感分析结果
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    confidence REAL,
                    keywords TEXT,
                    aspect TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts(post_id)
                )
            """)

            # alerts表：预警记录
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    platform TEXT,
                    content TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    acknowledged INTEGER DEFAULT 0
                )
            """)

            # reports表：分析报告
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    summary TEXT,
                    version TEXT,
                    file_path TEXT
                )
            """)

            # 索引 — 加速查询
            conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_post_time ON posts(post_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_post_id ON sentiment_results(post_id)")

    # ===== posts 操作 =====

    def insert_posts(self, posts: List[PostItem]):
        """批量插入帖子，重复的自动跳过"""
        with self.get_connection() as conn:
            for p in posts:
                conn.execute("""
                    INSERT OR IGNORE INTO posts
                    (post_id, platform, author, content, post_time, fetch_time,
                     likes, comments, shares, url, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (p.post_id, p.platform, p.author, p.content,
                      p.post_time, p.fetch_time, p.likes, p.comments,
                      p.shares, p.url, p.version))

    def get_posts(self, platform: str = None, days: int = 7,
                  limit: int = 1000) -> List[dict]:
        """按条件查询帖子"""
        query = "SELECT * FROM posts WHERE 1=1"
        params = []
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if days:
            query += " AND post_time >= datetime('now', ?)"
            params.append(f"-{days} days")
        query += " ORDER BY post_time DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    # ===== sentiment_results 操作 =====

    def insert_sentiment_results(self, results: List[SentimentResult]):
        """批量插入情感分析结果"""
        with self.get_connection() as conn:
            for r in results:
                conn.execute("""
                    INSERT INTO sentiment_results
                    (post_id, sentiment, confidence, keywords, aspect)
                    VALUES (?, ?, ?, ?, ?)
                """, (r.post_id, r.sentiment.value, r.confidence,
                      ",".join(r.keywords), r.aspect))

    def get_sentiment_stats(self, platform: str = None,
                            days: int = 7) -> dict:
        """获取情感分布统计"""
        query = """
            SELECT sentiment, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM sentiment_results sr
            JOIN posts p ON sr.post_id = p.post_id
            WHERE 1=1
        """
        params = []
        if platform:
            query += " AND p.platform = ?"
            params.append(platform)
        if days:
            query += " AND sr.created_at >= datetime('now', ?)"
            params.append(f"-{days} days")
        query += " GROUP BY sentiment"

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return {row["sentiment"]: {"count": row["count"],
                                       "avg_confidence": row["avg_conf"]}
                    for row in rows}

    # ===== alerts 操作 =====

    def insert_alert(self, alert: Alert):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO alerts
                (alert_id, alert_type, platform, content, severity, created_at, acknowledged)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (alert.alert_id, alert.alert_type, alert.platform,
                  alert.content, alert.severity, alert.created_at,
                  int(alert.acknowledged)))

    def get_unacknowledged_alerts(self) -> List[dict]:
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE acknowledged = 0 ORDER BY created_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    # ===== reports 操作 =====

    def insert_report(self, report: Report):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO reports
                (report_id, report_type, created_at, title, content, summary, version, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (report.report_id, report.report_type, report.created_at,
                  report.title, report.content, report.summary,
                  report.version, None) 