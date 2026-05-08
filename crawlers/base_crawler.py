"""爬虫基类，定义统一接口"""
from abc import ABC, abstractmethod
from typing import List
from core.models import PostItem

class BaseCrawler(ABC):
    """所有爬虫的基类"""
    
    platform: str = ""
    
    @abstractmethod
    def crawl(self, keyword: str = "", limit: int = 100) -> List[PostItem]:
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__} platform={self.platform}>"
