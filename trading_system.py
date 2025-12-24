"""
trading_system.py
NSE500 Quantitative Swing Trading System (Offline, Stable)

- Uses local NSE500 CSV (no NSE API)
- Daily batch scan
- RSI + MA + Volume based strategy
- Portfolio tracked in JSON
- No email / no credentials
"""

# ------------------ IMPORTS ------------------
import json
import math
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

import pandas as pd
import numpy as np
import yfinance as yf

# ------------------ PATHS ------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "NSE500.csv"

REPORTS_DIR = BASE_DIR / "reports"
PORTFOLIO_PATH = BASE_DIR / "portfolio.json"

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

if not PORTFOLIO_PATH.exists():
    PORTFOLIO_PATH.write_text("[]")

SAMPLE_SCAN_PATH = REPORTS_DIR / "sample_scan_output.csv"

# ------------------ CSV SYMBOL LOADER ------------------
def fetch_nse500_symbols() -> List[str]:
    """
    Load NSE500 symbols from CSV inside project (Git-safe).
    Path: data/ind_nifty500list.csv
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found: {CSV_PATH}\n"
            "Ensure data/ind_nifty500list.csv exists."
        )

    df = pd.read_csv(CSV_PATH)

    if "Symbol" not in df.columns:
        raise ValueError("CSV must contain a 'Symbol' column")

    symbols = (
        df["Symbol"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return [f"{s}.NS" for s in symbols]

# ------------------ DATA FETCH ------------------
def fetch_ohlcv(symbol: str, period="260d") -> pd.DataFrame:
    for _ in range(2):  # max 2 attempts
        try:
            df = yf.download(
                symbol,
                period=period,
                interval="1d",
                progress=False,
                threads=False,
                timeout=10
            )

            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        except Exception:
            pass

    return pd.DataFrame()

# ------------------ INDICATORS ------------------
def rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["RSI7"] = rsi(df["Close"], 7)
    df["RSI14"] = rsi(df["Close"], 14)
    df["RSI30"] = rsi(df["Close"], 30)
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    df["Vol20"] = df["Volume"].rolling(20).mean()
    df["SwingHigh30"] = df["High"].rolling(30).max()
    df["SwingLow20"] = df["Low"].rolling(20).min()
    return df

# ------------------ STRATEGY RULES ------------------
def bullish_confirmation(df: pd.DataFrame) -> bool:
    today, prev = df.iloc[-1], df.iloc[-2]
    return today["Close"] > today["Open"] and today["Close"] > prev["Close"]

def check_buy(df: pd.DataFrame) -> Tuple[bool, Dict]:
    if df.shape[0] < 200:
        return False, {}

    df = compute_indicators(df)
    last = df.iloc[-1]

    cond_rsi = (
        last["RSI14"] < 30 and
        last["RSI7"] < 35 and
        last["RSI30"] < 40
    )

    cond_trend = (
        last["Close"] > last["MA200"] or
        last["MA50"] > last["MA200"]
    )

    cond_volume = last["Volume"] > 2.5 * last["Vol20"]
    cond_candle = bullish_confirmation(df)

    buy = cond_rsi and cond_trend and cond_volume and cond_candle

    info = {
        "price": float(last["Close"]),
        "RSI14": float(last["RSI14"]),
        "VolumeMultiple": float(last["Volume"] / last["Vol20"]),
    }

    return buy, info

# ------------------ PORTFOLIO ------------------
def load_portfolio() -> List[Dict]:
    return json.loads(PORTFOLIO_PATH.read_text())

def save_portfolio(data: List[Dict]):
    PORTFOLIO_PATH.write_text(json.dumps(data, indent=2))

def add_position(symbol: str, price: float):
    portfolio = load_portfolio()

    position = {
        "symbol": symbol,
        "buy_price": price,
        "buy_date": datetime.now().isoformat(),
        "stop_loss": round(price * 0.93, 2),
        "target_price": round(price * 1.10, 2),
        "status": "OPEN"
    }

    portfolio.append(position)
    save_portfolio(portfolio)

# ------------------ SELL LOGIC ------------------
def check_sell(pos: Dict) -> Tuple[bool, str, float]:
    df = fetch_ohlcv(pos["symbol"])
    if df.empty:
        return False, "", 0.0

    df = compute_indicators(df)
    last = df.iloc[-1]
    price = float(last["Close"])

    if price <= pos["stop_loss"]:
        return True, "STOP_LOSS", price
    if price >= pos["target_price"]:
        return True, "TARGET_HIT", price
    if last["RSI14"] > 50:
        return True, "RSI_EXIT", price
    if price >= last["SwingHigh30"]:
        return True, "SWING_HIGH_EXIT", price

    return False, "", price

# ------------------ MAIN RUN ------------------
def run():
    symbols = fetch_nse500_symbols()
    print(f"Scanning {len(symbols)} symbols...")

    scan_results = []
    buys = []

    for i, symbol in enumerate(symbols, start=1):
        df = fetch_ohlcv(symbol)
        time.sleep(0.5) 
        if df.empty:
            continue

        buy, info = check_buy(df)
        scan_results.append({"symbol": symbol, "buy": buy, **info})

        if buy:
            add_position(symbol, info["price"])
            buys.append(symbol)

    # Save scan report
    scan_file = REPORTS_DIR / f"scan_{datetime.now():%Y%m%d}.csv"
    pd.DataFrame(scan_results).to_csv(scan_file, index=False)

    # Sell check
    portfolio = load_portfolio()
    for pos in portfolio:
        if pos["status"] != "OPEN":
            continue
        sell, reason, price = check_sell(pos)
        if sell:
            pos["status"] = "CLOSED"
            pos["sell_price"] = price
            pos["sell_reason"] = reason

    save_portfolio(portfolio)

    print(f"Scan saved: {scan_file}")
    print(f"New BUY signals: {len(buys)}")

def run_scan():

    symbols = fetch_nse500_symbols()

    scan_results = []
    buy_rows = []
    sell_rows = []

    # ---------------- BUY SCAN ----------------
    for symbol in symbols:
        df = fetch_ohlcv(symbol)
        time.sleep(0.5)

        if df.empty:
            continue

        buy, info = check_buy(df)

        row = {
            "symbol": symbol,
            "buy": buy,
            **info
        }

        scan_results.append(row)

        if buy:
            add_position(symbol, info["price"])
            buy_rows.append(row)

    # ---------------- SELL CHECK ----------------
    portfolio = load_portfolio()

    for pos in portfolio:
        if pos["status"] != "OPEN":
            continue

        sell, reason, price = check_sell(pos)

        if sell:
            pos["status"] = "CLOSED"
            pos["sell_price"] = price
            pos["sell_reason"] = reason

            sell_rows.append({
                "symbol": pos["symbol"],
                "exit_price": price,
                "reason": reason
            })

    save_portfolio(portfolio)

    # Convert to DataFrames
    buy_df = pd.DataFrame(buy_rows)
    sell_df = pd.DataFrame(sell_rows)
    full_df = pd.DataFrame(scan_results)

    return buy_df, sell_df, full_df


if __name__ == "__main__":
    buys, sells, full = run_scan()
    print(
        f"Scan completed | BUY signals: {len(buys)} | "
        f"SELL alerts: {len(sells)} | "
        f"Universe scanned: {len(full)}"
    )



