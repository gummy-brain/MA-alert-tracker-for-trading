# =============================================================================
# MA Alert Tracker — Configuration
# Edit this file to customise your tracked instruments and alert settings.
# =============================================================================

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

# --- Email settings ---
# Sender: your Gmail address
# Receiver: where you want alerts sent (can be the same address)
SENDER_EMAIL    = "your.gmail@gmail.com"
RECEIVER_EMAIL  = "your.gmail@gmail.com"

# Do NOT put your password here.
# Set it as an environment variable called EMAIL_PASSWORD.
# On PythonAnywhere: Dashboard → Files → .env  (see README for instructions)
