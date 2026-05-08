#config/settings.py
from pydantic_settings import BaseSettings
from typing import List


class Setting(BaseSettings):
    #DeepSeek API配置
    DEEPSEEK_API_KEY:str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 数据库配置
    DATABASE_PATH: str = "data/database.db"
    
    # 采集配置
    CRAWL_INTERVAL_HOURS: int = 6
    MAX_POSTS_PER_PLATFORM: int = 500
    
    # 预警配置
    NEGATIVE_THRESHOLD: float = 0.3
    SPIKE_THRESHOLD: float = 0.2
    
    # Agent配置
    MAX_REACT_STEPS: int = 10          # ReAct最大推理步数
    LLM_TIMEOUT: int = 60              # API超时时间(秒)
    LLM_MAX_RETRIES: int = 3           # 最大重试次数
    
    class Config:
        env_file = ".env"

