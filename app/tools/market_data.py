from typing import Dict, Any, Optional
import datetime
import yfinance as yf


def fetch_last_price(symbol: str) -> Dict[str, Any]:
    """
    Fetch the last closing price for a given ticker symbol.

    Args:
        symbol (str): e.g., 'AAPL' or 'TCS.NS'
cm
    Returns:
        dict: {symbol, price, currency, timestamp}
    """
    t = yf.Ticker(symbol)
    hist = t.history(period="1d")
    if hist is None or hist.empty:
        return {
            "symbol": symbol,
            "price": None,
            "currency": None,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
    price = float(hist["Close"].iloc[-1])
    currency = None
    try:
        # fast_info is faster and often contains currency
        currency = getattr(t, "fast_info", {}).get("currency")
    except Exception:
        currency = None

    return {
        "symbol": symbol,
        "price": price,
        "currency": currency or "UNKN",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


def get_basic_fundamentals(symbol: str) -> Dict[str, Any]:
    """
    Fetch basic fundamentals: sector, marketCap, trailingPE, dividendYield (best-effort).
    This is a demo. Data fields may change or be unavailable.

    Returns:
        dict with minimal fundamentals.
    """
    t = yf.Ticker(symbol)
    try:
        info = t.info  # yfinance may warn or be slow; used here for demo.
    except Exception:
        info = {}

    return {
        "symbol": symbol,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "dividendYield": info.get("dividendYield"),
        "currency": info.get("currency"),
    }


def get_beta(symbol: str) -> Dict[str, Any]:
    """
    Fetch beta (if available). This is illustrative only.

    Returns:
        dict: {symbol, beta}
    """
    t = yf.Ticker(symbol)
    beta = None
    try:
        info = t.info
        beta = info.get("beta")
    except Exception:
        beta = None

    return {"symbol": symbol, "beta": beta}