import os, sys, json, re
from typing import Dict, Callable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from autogen import AssistantAgent
from app.config.settings import get_llm_config, get_runtime_config

# Tools
from app.tools.market_data import fetch_last_price, get_basic_fundamentals, get_beta
from app.tools.portfolio_tools import compute_portfolio_risk, suggest_allocation


# ------------------------------ TOOL MAP ------------------------------------
TOOL_MAP: Dict[str, Callable] = {
    "fetch_last_price": fetch_last_price,
    "get_basic_fundamentals": get_basic_fundamentals,
    "get_beta": get_beta,
    "compute_portfolio_risk": compute_portfolio_risk,
    "suggest_allocation": suggest_allocation,
}

TOOL_TAG = re.compile(
    r"<tool:(?P<name>[a-zA-Z0-9_]+)>(?P<json>{.*?})</tool>",
    re.DOTALL
)


def extract_tool_call(text: str):
    if not text:
        return None
    m = TOOL_TAG.search(text)
    if not m:
        return None
    return m.group("name"), json.loads(m.group("json"))


# ------------------------------ MAIN -----------------------------------------
def main():
    llm_config = get_llm_config()
    runtime = get_runtime_config()

    # Load agents
    stock_agent = AssistantAgent(
        name="StockMarketAdvisor",
        system_message=open("app/prompts/stock_system_prompt.txt").read(),
        llm_config=llm_config
    )

    fin_agent = AssistantAgent(
        name="FinancialAdvisor",
        system_message=open("app/prompts/financial_system_prompt.txt").read(),
        llm_config=llm_config
    )

    symbol = "AAPL" if runtime["default_market"] == "US" else "TCS.NS"

    kickoff = f"""
    Work together.

    STOCK ADVISOR:
        Analyze {symbol}. 
        If you need live data, emit tags like:
        <tool:fetch_last_price>{{"symbol":"{symbol}"}}</tool>

    FINANCIAL ADVISOR:
        Build a sample moderate-risk allocation for a 30-year-old in India.
        Use tools if needed:
            <tool:compute_portfolio_risk>{{"returns":[0.1,0.06],"weights":[0.6,0.4]}}</tool>

    Always include disclaimers.
    """

    # ------------------------------ STOCK ADVISOR ------------------------------
    msg1 = stock_agent.generate_reply(messages=[{"role": "user", "content": kickoff}])
    print(f"\n[Stock Advisor]\n{msg1}")

    tc = extract_tool_call(msg1)
    if tc:
        name, args = tc
        result = TOOL_MAP[name](**args)
        print("\n[Tool Result]", result)

        follow = stock_agent.generate_reply(messages=[
            {"role": "user", "content": json.dumps(result)}
        ])
        print(f"\n[Stock Advisor Follow-up]\n{follow}")

    # ------------------------------ FINANCIAL ADVISOR ------------------------------
    msg2 = fin_agent.generate_reply(messages=[{"role": "user", "content": "Proceed with allocation."}])
    print(f"\n[Financial Advisor]\n{msg2}")

    tc2 = extract_tool_call(msg2)
    if tc2:
        name2, args2 = tc2
        result2 = TOOL_MAP[name2](**args2)
        print("\n[Tool Result]", result2)

        follow2 = fin_agent.generate_reply(messages=[
            {"role": "user", "content": json.dumps(result2)}
        ])
        print(f"\n[Financial Advisor Follow-up]\n{follow2}")


if __name__ == "__main__":
    main()