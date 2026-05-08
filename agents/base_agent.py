# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BaseAgent(ABC):
    """所有Agent的基类 — 统一状态管理、工具注册、错误处理"""

    def __init__(self, name: str, llm_client=None, db=None):
        self.name = name
        self.llm = llm_client
        self.db = db
        self.status = AgentStatus.IDLE
        self.last_run_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.step_count: int = 0           # ReAct推理步数计数
        self.max_steps: int = 10           # 最大推理步数（防死循环）

        # 工具注册表
        self._tools: Dict[str, callable] = {}
        self._tool_descriptions: Dict[str, str] = {}
        self._register_tools()

    @abstractmethod
    def _register_tools(self):
        """子类实现：注册本Agent可用的工具"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """子类实现：具体任务逻辑"""
        pass

    def register_tool(self, name: str, func: callable, description: str = ""):
        """注册工具"""
        self._tools[name] = func
        self._tool_descriptions[name] = description

    def call_tool(self, name: str, **kwargs) -> Any:
        """调用已注册的工具"""
        if name not in self._tools:
            raise ValueError(f"Agent [{self.name}] 未注册工具: {name}")
        return self._tools[name](**kwargs)

    def can_continue(self) -> bool:
        """检查是否还能继续推理（防ReAct死循环）"""
        self.step_count += 1
        if self.step_count > self.max_steps:
            print(f"[{self.name}] 达到最大步数 {self.max_steps}，终止推理")
            return False
        return True

    def reset_steps(self):
        """重置步数计数"""
        self.step_count = 0

    def run(self, **kwargs) -> Dict:
        """标准运行接口，包含状态管理和错误处理"""
        self.status = AgentStatus.RUNNING
        self.reset_steps()
        start_time = datetime.now()

        try:
            result = self.execute(**kwargs)
            self.status = AgentStatus.SUCCESS
            self.last_run_time = start_time
            return {
                "status": "success",
                "agent": self.name,
                "result": result,
                "duration": (datetime.now() - start_time).seconds,
                "steps": self.step_count
            }
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.last_error = str(e)
            return {
                "status": "failed",
                "agent": self.name,
                "error": str(e)
            }

    def get_status(self) -> Dict:
        """获取Agent状态信息"""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_run": str(self.last_run_time) if self.last_run_time else None,
            "last_error": self.last_error,
            "tools": list(self._tools.keys()),
            "step_count": self.step_count
        }

    def get_tool_descriptions(self) -> str:
        """获取所有工具的描述 — 用于ReAct提示词"""
        desc = []
        for name, desc_text in self._tool_descriptions.items():
            desc.append(f"- {name}: {desc_text}")
        return "\n".join(desc)