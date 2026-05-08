# core/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SentimentLabel(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class PostItem:
    """统一的帖子数据模型 — 所有平台爬到的数据都转成这个格式"""
    post_id: str                    # 平台+ID组合，确保唯一（如"bilibili_12345"）
    platform: str                   # 来源平台
    author: str                     # 作者
    content: str                    # 正文内容
    post_time: datetime             # 发布时间
    fetch_time: datetime = field(default_factory=datetime.now)
    likes: int = 0
    comments: int = 0
    shares: int = 0
    url: str = ""
    version: str = ""               # 游戏版本号（自动识别或手动标注）


@dataclass
class SentimentResult:
    """情感分析结果"""
    post_id: str
    sentiment: SentimentLabel
    confidence: float               # 置信度 0~1
    keywords: List[str] = field(default_factory=list)
    aspect: str = ""                # 方面词（如"画质"、"剧情"、"优化"）


@dataclass
class Topic:
    """热点话题"""
    topic_id: str
    keywords: List[str]
    post_count: int
    avg_sentiment: float
    first_seen: datetime
    last_seen: datetime


@dataclass
class Alert:
    """预警记录"""
    alert_id: str
    alert_type: str                 # "negative_spike" / "hot_topic" / "version_bug"
    platform: str
    content: str
    severity: str                   # "low" / "medium" / "high"
    created_at: datetime
    acknowledged: bool = False


@dataclass
class Report:
    """分析报告"""
    report_id: str
    report_type: str                # "daily" / "weekly" / "version_compare"
    created_at: datetime
    title: str
    content: str                    # Markdown格式
    summary: str
    version: str = ""