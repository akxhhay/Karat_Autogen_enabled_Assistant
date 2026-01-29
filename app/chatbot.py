# app/chatbot.py
import os, sys, json, re
from typing import Dict, Callable, List, Tuple

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

TOOL_TAG_RE = re.compile(r"<tool:(?P<name>[a-zA-Z0-9_]+)>(?P<json>{.*?})</tool>", re.DOTALL)


def extract_tool_calls(text: str) -> List[Tuple[str, dict]]:
    """Return a list of (tool_name, json_args) tuples from model output."""
    if not text:
        return []
    calls = []
    for m in TOOL_TAG_RE.finditer(text):
        name = m.group("name")
        raw = m.group("json")
        try:
            args = json.loads(raw)
        except Exception:
            args = {}
        calls.append((name, args))
    return calls


def exec_tool(name: str, args: dict):
    """Execute mapped tool. Prefer kwargs; fallback to positional."""
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"_error": f"Unknown tool '{name}'"}
    try:
        return fn(**args)
    except TypeError:
        try:
            return fn(*args.values())
        except Exception as e:
            return {"_error": f"Tool '{name}' failed: {e.__class__.__name__}: {e}"}
    except Exception as e:
        return {"_error": f"Tool '{name}' failed: {e.__class__.__name__}: {e}"}


# ------------------------------ INTERACTIVE IO -------------------------------
def ask(prompt: str, default: str | None = None) -> str:
    try:
        val = input(prompt).strip()
        if not val and default is not None:
            return default
        return val
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)


def ask_choice(prompt: str, choices: List[str], default_index: int | None = None) -> str:
    opts = ", ".join(f"{i+1}) {c}" for i, c in enumerate(choices))
    while True:
        raw = ask(f"{prompt} [{opts}]{' (default: '+choices[default_index]+')' if default_index is not None else ''}: ")
        if not raw and default_index is not None:
            return choices[default_index]
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw)-1]
        # allow direct text
        for c in choices:
            if raw.lower() == c.lower():
                return c
        print(f"Please pick 1..{len(choices)} or type one of {choices}.")


def print_header(title: str):
    print("\n" + "="*80)
    print(title)
    print("="*80)


# ------------------------------ AGENT RUNNERS --------------------------------
def run_agent(agent: AssistantAgent, user_message: str, max_tool_rounds: int = 3):
    """
    Sends user_message to agent, executes any tool tags returned, feeds results back,
    and returns the final agent text response (printed along the way).
    """
    reply = agent.generate_reply(messages=[{"role": "user", "content": user_message}])
    print(f"\n[{agent.name}]\n{reply}")

    rounds = 0
    last_reply = reply
    while rounds < max_tool_rounds:
        calls = extract_tool_calls(last_reply)
        if not calls:
            break

        results = []
        for (name, args) in calls:
            result = exec_tool(name, args)
            results.append({"tool": name, "args": args, "result": result})
            print(f"\n[Tool Result: {name}]\n{json.dumps(result, indent=2)}")

        last_reply = agent.generate_reply(messages=[
            {"role": "user", "content": f"Tool results:\n{json.dumps(results)}\nIncorporate and continue."}
        ])
        print(f"\n[{agent.name}]\n{last_reply}")
        rounds += 1

    return last_reply


def main():
    llm_config = get_llm_config()
    runtime = get_runtime_config()

    # Agents
    stock_agent = AssistantAgent(
        name="StockMarketAdvisor",
        system_message=open("app/prompts/stock_system_prompt.txt", encoding="utf-8").read(),
        llm_config=llm_config
    )
    fin_agent = AssistantAgent(
        name="FinancialAdvisor",
        system_message=open("app/prompts/financial_system_prompt.txt", encoding="utf-8").read(),
        llm_config=llm_config
    )

    print_header("Welcome to the Finance Chatbot (Educational only—NOT financial advice)")
    print("Hi! I can help with:")
    print("- Stock analysis (ticker-specific metrics, fundamentals, risk flags)")
    print("- Financial planning (allocation, risk profiling, rebalancing)")
    print("I’ll first ask a few quick questions to personalize the conversation.\n")

    # ------------------------------ ONBOARDING --------------------------------
    age = ask("Your age (e.g., 30): ")
    horizon_yrs = ask("Investment horizon in years (e.g., 10): ")
    risk = ask_choice("Risk tolerance", ["Low", "Moderate", "High"], default_index=1)
    market_pref = ask_choice("Primary market", ["IN", "US"], default_index=0)
    goals = ask("Your key goal(s) (e.g., long-term growth, income, child education, retirement): ")
    need_type = ask_choice(
        "What do you need help with right now?",
        ["Stock advice", "Financial/portfolio advice", "Both"],
        default_index=2
    )

    # For stock path
    default_symbol = "AAPL" if market_pref.upper() == "US" else "TCS.NS"
    ticker = ask(f"Ticker symbol (e.g., {default_symbol}): ", default=default_symbol)

    # Optional details for Finance path
    monthly_savings = ask("Approx monthly investable amount (e.g., 25000 INR): ")
    emergency_fund = ask("Emergency fund in months of expenses (e.g., 6): ")
    tax_regime = ask_choice("Tax regime (India)", ["Unknown/NA", "Old", "New"], default_index=0)

    # ------------------------------ ROUTING -----------------------------------
    symbol = ticker.strip().upper()
    # Flip the app's default market to your choice, only for this session:
    runtime_market = market_pref.upper()

    # STOCK TASK
    stock_task = f"""
    Please analyze {symbol} for a user (age: {age}, risk: {risk}, horizon: {horizon_yrs} years, market: {runtime_market}).
    Use tools when needed:
      <tool:fetch_last_price>{{"symbol":"{symbol}"}}</tool>
      <tool:get_basic_fundamentals>{{"symbol":"{symbol}"}}</tool>
      <tool:get_beta>{{"symbol":"{symbol}"}}</tool>
    Provide assumptions, uncertainties, risk factors, and an educational disclaimer.
    Avoid definitive buy/sell directives.
    """

    # FINANCE TASK
    fin_task = f"""
    User profile (India): age {age}, horizon {horizon_yrs} years, risk {risk}, goals: {goals},
    monthly savings: {monthly_savings}, emergency fund: {emergency_fund} months, tax regime: {tax_regime}.
    Suggest a moderate, diversified allocation with rationale, rebalancing guidance, and notes on liquidity & taxes.
    Use tools when helpful:
      <tool:suggest_allocation>{{"risk_tolerance":"{risk.lower()}","horizon_years":{int(horizon_yrs or 10)}}}</tool>
      <tool:compute_portfolio_risk>{{"returns":[0.10,0.06],"weights":[0.6,0.4]}}</tool>
    Include an educational-only disclaimer and no direct product recommendations.
    """

    print_header("Working on your request...")

    try:
        if need_type == "Stock advice":
            run_agent(stock_agent, stock_task)
        elif need_type == "Financial/portfolio advice":
            run_agent(fin_agent, fin_task)
        else:  # Both
            # Stock first, then Finance
            run_agent(stock_agent, stock_task)
            print_header("Switching to Financial/Portfolio Advisor...")
            run_agent(fin_agent, fin_task)

        print_header("Done")
        print("Reminder: This is educational information, not financial advice. "
              "Consider consulting a SEBI-registered/qualified advisor for personalized guidance.")
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()