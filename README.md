## **📈 Quantitative Swing Trading System — NSE 500 (Python)**

## **This project is designed to be fully reproducible. Clone the repository, install dependencies, and run `trading_system.py` to generate daily NSE500 scan reports.**

**🔍 Project Overview**
This project is a rule-based quantitative swing trading system built using Python and NSE 500 equity data.
The system scans the market daily, identifies high-probability long trades, manages open positions with predefined risk rules, and stores portfolio state persistently.

**The goal of this project is to demonstrate:**
1. Applied quantitative finance concepts
2. Technical indicator computation from raw OHLCV data
3. Clean system design (data → signal → execution → persistence)
4. Production-ready Python engineering practices

**🎯 Problem Statement**
Retail traders often:
1. Rely on subjective chart reading
2. Manually calculate indicators
3. Lack discipline in risk management

## **This system automates decision-making using mathematically defined rules and removes emotional bias.**

## **🧠 System Design (High Level)**
<p align="center">
  <img src="data/system_design.png" alt="System Design Diagram" width="900">
</p>

> High-level architecture of the NSE500 quantitative swing trading system.

1. **CSV (NSE 500 Symbols)**
2. **Market Data Fetch** — `yfinance`
3. **Indicator Engine** — RSI, Moving Averages, Volume
4. **Signal Generator** — BUY / HOLD / SELL
5. **Portfolio Manager** — JSON persistence
6. **Daily Scan Report** — CSV output

## **⚙️ Detailed Workflow (Step-by-Step)**
### **Step 0 — Universe Selection**
- NSE 500 stocks are used as the trading universe
- Symbols are loaded from: "data/ind_nifty500list.csv"

### **Step 1 — Market Data Collection**
- Historical OHLCV data is fetched using yfinance
- Timeframe: Daily
- Lookback window ensures stable indicator calculation
### Why yfinance?
- Free
- Reliable
- No NSE API instability
- Suitable for research & prototyping  

### **Step 2 — Indicator Calculations**
📌 Relative Strength Index (RSI)
- RS is calculated as $$RSI = 100 - \frac{100}{1 + RS}$$
Where:
$$RS = \frac{\text{Avg Gain}}{\text{Avg Loss}}$$
**Periods used:**
- RSI(7) → Short-term momentum
- RSI(14) → Standard momentum
- RSI(30) → Medium-term trend exhaustion 
### Purpose:
- Identify oversold conditions within an uptrend.

### 📌 **Moving Averages (Trend Filter)**
- 50-day SMA and 200-day SMA
### Used to:
- Filter trades in broader uptrends
- Avoid counter-trend entries
### Conditions:
- Price > 200 SMA OR 50 SMA > 200 SMA

### 📌 Volume Expansion Logic
- 20-day average volume is calculated
- Current volume must be:
- **Volume > 2.5 × Avg_20_Day_Volume**

### Purpose:
- Ensure institutional participation behind price movement.

### **Step 3 — BUY Signal Logic**
- A BUY signal is generated only if ALL conditions are met:
- RSI(14) < 30
- RSI(7) < 35
- RSI(30) < 40
- Trend filter satisfied
- Volume expansion confirmed
- Bullish confirmation candle: [Close > Open] and [Close > Previous Close]

### **Step 4 — Risk Management & Trade Structuring**
### Each trade is structured before entry:
- Stop-loss: 7%
- Target: 10%
- Risk is predefined and fixed
### This enforces:
- Capital protection
- Consistent expectancy
- Repeatable execution

### **Step 5 — Portfolio Persistence**
- All open and closed trades are stored in: "portfolio.json"
### Stored fields:
- Entry price & date
- Stop-loss
- Target
- Exit price
- Exit reason
### This allows:
- Restarting the system without data loss
- Auditability
- Future performance analytics

### **Step 6 — Reporting**
- Daily scan results are saved as: "reports/scan_YYYYMMDD.csv"
### This enables:
- Manual review
- Historical signal analysis
- Easy demo recording

## **🛠 Tools & Technologies Used**
- **Python 3.9+**
- **pandas** — data processing
- **numpy** — numerical computation
- **yfinance** — market data
- **JSON / CSV** — lightweight persistence
- **VS Code** — development
- **Git & GitHub** — version control

## **🧩 Design Choices Explained**
- ❌ No live order execution (intentional)
- ❌ No NSE website scraping (unstable)
- ❌ No databases (kept simple & portable)
- ✅ Deterministic rule-based logic
- ✅ Easily extensible for backtesting

## **📌 Future Enhancements**
- Vectorized backtesting engine
- Performance metrics (CAGR, drawdown)
- Strategy optimization
- Scheduled daily runs
- Visualization dashboard

## **⚠️ Disclaimer**
- This project is for educational and research purposes only.
- It is not financial advice.

## **👤 Author**
- **Manoj Bhardwaj**
- Applied Mathematics | Quantitative Finance | Python
- 📍 Bangalore, India

















