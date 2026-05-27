# MA Alert Tracker

This is Python tool that monitors index funds and stocks for moving average crossover signals and sends a daily email summary. Runs for free on **GitHub Actions** — no server, no subscription, no PC needed.

I came up with this tool while researching beginner-friendly approaches to timing buy and sell decisions for my own portfolio. Moving Average crossovers seemed to be a straightforward and well-grounded method for this — see STRATEGY.md for the theoretical background.

Once I knew what I wanted to track, I needed a way to monitor these signals without checking my portfolio constantly. Trading apps like Trading 212 and TradingView offer similar alert functionality, but only with a paid subscription. Building my own alerts was the practical alternative.

As a beginner investor, I might improve and expand the tracker as my knowledge grows.

\---

## What it does

The tracker checks each instrument you configure once per day (weekdays only, after European markets close) and detects two signals:

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
├── .github/
│   └── workflows/
│       └── daily.yml    # GitHub Actions schedule — runs every weekday at 18:00 UTC
├── tracker.py           # Main script — fetches data, detects signals, sends email
├── config.py            # Your tickers, MA periods, email addresses
├── requirements.txt     # Python dependencies
├── .gitignore           # Keeps secrets and cache out of git
├── STRATEGY.md          # Research backing, design decisions, and known limitations
└── README.md            # This file
```

\---

## Setup

### 1\. Fork or clone the repo

```bash
git clone https://github.com/gummy-brain/MA-alert-tracker-for-trading.git
cd ma-alert-tracker
```

### 2\. Edit config.py

Open `config.py` and:

* Add your tickers to the `TICKERS` dictionary
* Set your `SENDER\_EMAIL` and `RECEIVER\_EMAIL` (both can be your Gmail)

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

### 4\. Add the App Password as a GitHub Secret

This is how your password is kept secure — it is stored encrypted in GitHub and never exposed in your code.

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `EMAIL_PASSWORD`
4. Value: paste your 16-character Gmail App Password
5. Click **Add secret**

### 5\. Push to GitHub — Actions starts automatically

Once your code is pushed and the secret is set, GitHub Actions will run the tracker automatically every weekday at 18:00 UTC (after European markets close).

To run it immediately without waiting for the schedule:

1. Go to your repo → **Actions** tab
2. Click **Daily MA Alert** in the left sidebar
3. Click **Run workflow** → **Run workflow**

Check your inbox after a minute.

\---

## Adjusting the schedule

The schedule is set in `.github/workflows/daily.yml`. The default is `0 18 \* \* 1-5` which means 18:00 UTC on weekdays. To change it, edit the cron expression:

```yaml
- cron: '0 18 \* \* 1-5'
#        │  │  │ │ └─ weekdays only (1=Mon, 5=Fri)
#        │  │  │ └─── every month
#        │  │  └───── every day of month
#        │  └──────── hour in UTC
#        └─────────── minute
```

A helpful tool for building cron expressions: [crontab.guru](https://crontab.guru)

\---

## Customisation

|Setting in config.py|Default|What it controls|
|-|-|-|
|`SHORT\_MA`|50|MA period for buy signal|
|`LONG\_MA`|150|MA period for sell signal|
|`SELL\_THRESHOLD\_PCT`|0.5|% below 150 MA to trigger sell|
|`VOLUME\_AVG\_DAYS`|20|Window for average volume calculation|

\---

## How the signals work

### Why all three buy conditions?

A price crossing a flat or declining MA often means noise — the MA hasn't confirmed the trend yet. Requiring both the price and the MA to be rising means the signal only fires when momentum is genuine. This reduces false positives significantly for long-term index fund investors.

### Why 0.5% for the sell threshold?

Index funds are smoothed by diversification — they don't spike wildly. A 0.5% close below the 150-day SMA is meaningful for an index fund in a way it might not be for a single volatile stock. You can tune this higher (e.g. 1.0%) if you want fewer, stronger signals.

### Why 150 days for the sell signal?

The 150-day SMA is a medium-to-long term trend indicator. Selling when price breaks this line — rather than waiting for the SMA itself to visibly turn down — means you act earlier in a potential downtrend, before significant losses accumulate.

See [STRATEGY.md](STRATEGY.md) for the research backing, design decisions, and known limitations.

\---

## Data source

Historical price and volume data is sourced from **Yahoo Finance** via the `yfinance` library. This covers most European ETFs listed on Xetra, Euronext, and the London Stock Exchange. Data is free and requires no API key.

\---

## Dependencies

* [yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance data
* [pandas](https://pandas.pydata.org/) — data manipulation

\---

## Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. I am just a beginner investor, so please do your own research before making any investment decisions.

