import os
import pytest

from app.config.settings import get_llm_config
from app.agents.stock_advisor import create_stock_advisor
from app.agents.financial_advisor import create_financial_advisor
from app.agents.orchestrator import create_orchestrator


def test_agent_creation():
    llm_config = get_llm_config()
    stock = create_stock_advisor(llm_config, prompts_dir=os.path.join("app", "prompts"))
    fin = create_financial_advisor(llm_config, prompts_dir=os.path.join("app", "prompts"))
    orch = create_orchestrator(work_dir="./workspace")
    assert stock.name == "StockMarketAdvisor"
    assert fin.name == "FinancialAdvisor"
    assert orch.name == "Orchestrator"