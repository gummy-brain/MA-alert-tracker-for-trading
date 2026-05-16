# =============================================================================
# MA Alert Tracker — Configuration
# Edit this file to customise your tracked instruments and alert settings.
# =============================================================================

import os

# --- Instruments to track ---
# Use Yahoo Finance tickers. Suffix guide:
#   .DE  = Xetra (Germany)   e.g. VWCE.DE
#   .PA  = Euronext Paris    e.g. MEUD.PA
#   .L   = London Stock Exchange  e.g. CSPX.L
#   .AS  = Euronext Amsterdam
#   No suffix = US-listed    e.g. SPY, QQQ, AAPL

TICKERS = {
    "VWCE.DE":  "Vanguard FTSE All-World (EUR, Xetra)",
    "CSPX.L":   "iShares Core S&P 500 (USD, LSE)",
    "MEUD.PA":  "Amundi MSCI Europe (EUR, Paris)",
    "SPY":      "SPDR S&P 500 ETF (USD)",
    # Add more below in the same format:
    # "TICKER": "Friendly name",
}

# --- Moving average periods ---
SHORT_MA  = 50   # Used for buy signal
LONG_MA   = 150  # Used for sell signal

# --- Sell signal threshold ---
# Price must close this many % BELOW the 150-day SMA to trigger.
# 0.5 means price is more than 0.5% under the line (filters out "touches").
SELL_THRESHOLD_PCT = 0.5

# --- Volume confirmation ---
# Volume window used to calculate average volume for context.
VOLUME_AVG_DAYS = 20

# --- Test mode ---
# Set to True to force both signals to fire on every instrument.
# Use this to verify the email is working, then set back to False.
TEST_MODE = True

# --- Email settings ---
# These are read from GitHub Secrets — do not put real values here.
# Add SENDER_EMAIL, RECEIVER_EMAIL, and EMAIL_PASSWORD as repository secrets:
# GitHub repo → Settings → Secrets and variables → Actions → New repository secret
SENDER_EMAIL   = os.environ.get("SENDER_EMAIL", "your.email@gmail.com")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "your.email@gmail.com")
