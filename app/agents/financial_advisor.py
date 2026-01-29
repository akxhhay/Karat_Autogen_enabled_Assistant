import os
from autogen import AssistantAgent


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_financial_advisor(llm_config, prompts_dir: str):
    system_message = load_prompt(os.path.join(prompts_dir, "financial_system_prompt.txt"))
    financial_advisor = AssistantAgent(
        name="FinancialAdvisor",
        system_message=system_message,
        llm_config=llm_config,
    )
    return financial_advisor