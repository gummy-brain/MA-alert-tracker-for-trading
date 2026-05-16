# MA Alert Tracker

A lightweight Python tool that monitors index funds and stocks for moving average crossover signals and sends a daily email summary. Designed to run for free on [PythonAnywhere](https://www.pythonanywhere.com/) with no PC required.

\---

## What it does

The tracker checks each instrument you configure once per day and detects two signals:

### Buy signal — all three conditions must be true simultaneously

* Price **crosses above** the 50-day Simple Moving Average (SMA)
* Price today is **higher than yesterday** (the stock itself is moving up)
* The 50-day SMA today is **higher than yesterday** (the trend is rising, not flat)

This avoids false positives where price briefly pokes above a flat or declining MA.

### Sell signal

* Price closes more than **0.5% below** the 150-day SMA

The threshold filters out insignificant "touches" of the line. Once you receive the alert, you can check the chart manually for volume confirmation and decide whether to act.

### Volume context

Every alert email includes a volume reading (e.g. "1.8x average — above average") so you can judge buying or selling pressure at a glance.

\---

## Example email

```
MA Alert Tracker — 16 May 2025
========================================

BUY SIGNALS (price crossed above rising 50-day SMA)
--------------------------------------------------
  VWCE.DE  |  Vanguard FTSE All-World (EUR, Xetra)
  Price: 112.34  (prev: 111.20)
  50-day SMA: 111.80  (prev: 111.65  ↑ rising)
  Volume: 1.4x avg — above average

SELL SIGNALS (price dipped below 150-day SMA)
--------------------------------------------------
  MEUD.PA  |  Amundi MSCI Europe (EUR, Paris)
  Price: 38.20
  150-day SMA: 38.42
  Dip below: 0.57%
  Volume: 1.9x avg — above average
```

No signals → no email. You only hear from it when something happens.

\---

## Project structure

```
ma-alert-tracker/
├── tracker.py       # Main script — fetches data, detects signals, sends email
├── config.py        # Your tickers, MA periods, email addresses
├── requirements.txt # Python dependencies
├── .gitignore       # Keeps secrets and cache out of git
└── README.md        # This file
```

\---

## Setup

### 1\. Clone the repo

```bash
git clone https://github.com/YOUR\\\_USERNAME/ma-alert-tracker.git
cd ma-alert-tracker
```

### 2\. Edit config.py

Open `config.py` and:

* Add your tickers to the `TICKERS` dictionary
* Set your `SENDER\\\_EMAIL` and `RECEIVER\\\_EMAIL` (both can be your Gmail)

**Ticker format guide:**

|Exchange|Suffix|Example|
|-|-|-|
|Xetra (Germany)|`.DE`|`VWCE.DE`|
|Euronext Paris|`.PA`|`MEUD.PA`|
|London Stock Exchange|`.L`|`CSPX.L`|
|Euronext Amsterdam|`.AS`|`IWDA.AS`|
|US markets|*(none)*|`SPY`, `QQQ`|

You can verify any ticker at [finance.yahoo.com](https://finance.yahoo.com).

### 3\. Set up a Gmail App Password

Gmail requires an App Password (not your normal password) for SMTP access.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** if not already on
3. Search for **App Passwords** in the security settings
4. Create one for "Mail" → copy the 16-character password

You'll use this in the next step — never put it in `config.py`.

\---

## Running on PythonAnywhere (free, no PC needed)

### 1\. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com/)

### 2\. Open a Bash console and clone the repo

```bash
git clone https://github.com/YOUR\\\_gummy-brain/MA-alert-tracker-for-trading.git
cd ma-alert-tracker
pip install -r requirements.txt --user
```

### 3\. Set your email password as an environment variable

In the PythonAnywhere Bash console:

```bash
echo 'export EMAIL\\\_PASSWORD="your-16-char-app-password"' >> \\\~/.bashrc
source \\\~/.bashrc
```

### 4\. Test it manually first

```bash
python tracker.py
```

Check your inbox. If no signals fire today (likely), temporarily set `SELL\\\_THRESHOLD\\\_PCT = 999` in config.py to force a sell alert for testing, then revert.

### 5\. Schedule the daily task

1. Go to **Dashboard → Tasks** in PythonAnywhere
2. Click **Add a new scheduled task**
3. Set time to e.g. `18:00` (after European markets close)
4. Command:

```
   /bin/bash -c 'source \\\~/.bashrc \\\&\\\& cd \\\~/ma-alert-tracker \\\&\\\& python tracker.py'
   ```

5. Save — it will run every day automatically

\---

## Customisation

|Setting in config.py|Default|What it controls|
|-|-|-|
|`SHORT\\\_MA`|50|MA period for buy signal|
|`LONG\\\_MA`|150|MA period for sell signal|
|`SELL\\\_THRESHOLD\\\_PCT`|0.5|% below 150 MA to trigger sell|
|`VOLUME\\\_AVG\\\_DAYS`|20|Window for average volume calculation|

\---

## How the signals work

### Why all three buy conditions?

A price crossing a flat or declining MA often means noise — the MA hasn't confirmed the trend yet. Requiring both the price and the MA to be rising means the signal only fires when momentum is genuine. This reduces false positives significantly for long-term index fund investors.

### Why 0.5% for the sell threshold?

Index funds are smoothed by diversification — they don't spike wildly. A 0.5% close below the 150-day SMA is meaningful for an index fund in a way it might not be for a single volatile stock. You can tune this higher (e.g. 1.0%) if you want fewer, stronger signals.

### Why 150 days for the sell signal?

The 150-day SMA is a medium-to-long term trend indicator. Selling when price breaks this line — rather than waiting for the SMA itself to visibly turn down — means you act earlier in a potential downtrend, before significant losses accumulate.

\---

## Data source

Historical price and volume data is sourced from **Yahoo Finance** via the `yfinance` library. This covers most European ETFs listed on Xetra, Euronext, and the London Stock Exchange. Data is free and requires no API key.

\---

## Dependencies

* [yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance data
* [pandas](https://pandas.pydata.org/) — data manipulation

\---

## Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. Always do your own research before making investment decisions.

