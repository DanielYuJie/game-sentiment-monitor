# config/platforms.py
from dataclasses import dataclass
from typing import List


@dataclass
class PlatformConfig:
    name: str           # 平台名称
    crawler_type: str   # mediacrawler / custom
    search_keywords: List[str]  # 默认搜索关键词
    enabled: bool = True


PLATFORMS = {
    # 主流社交平台（复用MediaCrawler）
    "weibo": PlatformConfig("微博", "mediacrawler", ["原神", "Genshin"]),
    "xiaohongshu": PlatformConfig("小红书", "mediacrawler", ["原神"]),
    "douyin": PlatformConfig("抖音", "mediacrawler", ["原神"]),
    "kuaishou": PlatformConfig("快手", "mediacrawler", ["原神"]),
    "bilibili": PlatformConfig("B站", "mediacrawler", ["原神"]),
    "zhihu": PlatformConfig("知乎", "mediacrawler", ["原神"]),
    
    # 游戏特有平台（自定义爬虫）
    "nga": PlatformConfig("NGA", "custom", ["原神"]),
    "miyoushe": PlatformConfig("米游社", "custom", ["原神"]),
    "tieba": PlatformConfig("贴吧", "custom", ["原神吧"]),
    "taptap": PlatformConfig("TapTap", "custom", ["原神"]),
    
    # 海外平台
    "steam": PlatformConfig("Steam", "custom", ["Genshin Impact"]),
    "reddit": PlatformConfig("Reddit", "custom", ["GenshinImpact"]),
}