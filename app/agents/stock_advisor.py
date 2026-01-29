import os
from autogen import AssistantAgent


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_stock_advisor(llm_config, prompts_dir: str):
    system_message = load_prompt(os.path.join(prompts_dir, "stock_system_prompt.txt"))
    stock_advisor = AssistantAgent(
        name="StockMarketAdvisor",
        system_message=system_message,
        llm_config=llm_config,
    )
    return stock_advisor
