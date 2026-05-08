# agents/orchestrator.py
from typing import Dict, List, Optional
from datetime import datetime
from core.llm_client import LLMClient
from core.database import Database


class Orchestrator:
    """
    任务编排器 — 协调多个Agent完成复杂任务
    
    工作流程：采集 → 分析 → 预警 → 报告
    """

    def __init__(self, db: Database, llm_client: LLMClient):
        self.db = db
        self.llm = llm_client
        # Agent延迟初始化，避免循环导入
        self._crawler = None
        self._analysis = None
        self._alert = None
        self._report = None

    @property
    def crawler(self):
        if self._crawler is None:
            from agents.crawler_agent import CrawlerAgent
            self._crawler = CrawlerAgent(self.llm, self.db)
        return self._crawler

    @property
    def analysis(self):
        if self._analysis is None:
            from agents.analysis_agent import AnalysisAgent
            self._analysis = AnalysisAgent(self.llm, self.db)
        return self._analysis

    @property
    def alert(self):
        if self._alert is None:
            from agents.alert_agent import AlertAgent
            self._alert = AlertAgent(self.llm, self.db)
        return self._alert

    @property
    def report(self):
        if self._report is None:
            from agents.report_agent import ReportAgent
            self._report = ReportAgent(self.llm, self.db)
        return self._report

    def run_task(self, task_type: str, **kwargs) -> Dict:
        """
        执行单个任务

        Args:
            task_type: "crawl" / "analyze" / "alert" / "report" / "full_pipeline"
        """
        if task_type == "full_pipeline":
            return self._run_full_pipeline(**kwargs)

        agent_map = {
            "crawl": self.crawler,
            "analyze": self.analysis,
            "alert": self.alert,
            "report": self.report
        }

        if task_type not in agent_map:
            raise ValueError(f"未知任务类型: {task_type}")

        return agent_map[task_type].run(**kwargs)

    def _run_full_pipeline(self, platforms: List[str] = None,
                           keywords: List[str] = None) -> Dict:
        """完整流程：采集 → 分析 → 预警 → 报告"""
        results = {}

        # 1. 采集
        print("📥 启动采集Agent...")
        crawl_result = self.crawler.run(
            platforms=platforms,
            keywords=keywords or ["原神"]
        )
        results["crawl"] = crawl_result
        if crawl_result["status"] == "failed":
            print("❌ 采集失败，流程终止")
            return results

        # 2. 分析
        print("📊 启动分析Agent...")
        analyze_result = self.analysis.run()
        results["analyze"] = analyze_result
        if analyze_result["status"] == "failed":
            print("❌ 分析失败，跳过后续步骤")
            return results

        # 3. 预警
        print("🚨 启动预警Agent...")
        alert_result = self.alert.run()
        results["alert"] = alert_result

        # 4. 报告
        print("📝 生成报告...")
        report_result = self.report.run(report_type="daily")
        results["report"] = report_result

        print("✅ 全流程完成")
        return results

    def get_all_status(self) -> Dict:
        """获取所有Agent状态"""
        return {
            "crawler": self._crawler.get_status() if self._crawler else "未初始化",
            "analysis": self._analysis.get_status() if self._analysis else "未初始化",
            "alert": self._alert.get_status() if self._alert else "未初始化",
            "report": self._report.get_status() if self._report else "未初始化",
        }