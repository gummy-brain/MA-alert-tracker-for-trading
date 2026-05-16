"""
MA Alert Tracker
================
Checks each tracked instrument daily for two signals:

  BUY  — Price crosses above the 50-day SMA, price is rising, and the
          50-day SMA itself is rising.

  SELL — Price closes more than SELL_THRESHOLD_PCT% below the 150-day SMA.
          Designed to catch a real dip below the line, not a brief touch.

Volume context is included in every alert so you can judge buying/selling
pressure manually after receiving the notification.

Run this script once daily via GitHub Actions (see .github/workflows/daily.yml).
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yfinance as yf
import pandas as pd

from config import (
    TEST_MODE,
    TICKERS,
    SHORT_MA,
    LONG_MA,
    SELL_THRESHOLD_PCT,
    VOLUME_AVG_DAYS,
    SENDER_EMAIL,
    RECEIVER_EMAIL,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_data(ticker: str, days: int = 300) -> pd.DataFrame:
    """
    Download daily OHLCV data for *ticker* covering the last *days* calendar
    days.  Returns a DataFrame with columns: Open, High, Low, Close, Volume.
    Returns an empty DataFrame on failure.
    """
    try:
        df = yf.download(ticker, period=f"{days}d", interval="1d", progress=False)
        if df.empty:
            log.warning(f"No data returned for {ticker}")
        return df
    except Exception as exc:
        log.error(f"Failed to fetch {ticker}: {exc}")
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Signal detection
# ---------------------------------------------------------------------------

def compute_signals(df: pd.DataFrame) -> dict:
    """
    Given a daily OHLCV DataFrame, compute MAs and detect signals.

    Returns a dict with keys:
        date, close, prev_close,
        sma50, prev_sma50, sma150,
        vol_today, vol_avg, vol_ratio,
        buy_signal, sell_signal, error
    """
    result = {
        "date": None, "close": None, "prev_close": None,
        "sma50": None, "prev_sma50": None, "sma150": None,
        "vol_today": None, "vol_avg": None, "vol_ratio": None,
        "buy_signal": False, "sell_signal": False, "error": None,
    }

    if df.empty or len(df) < LONG_MA + 5:
        result["error"] = "Not enough historical data"
        return result

    # Flatten MultiIndex columns that yfinance sometimes returns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close  = df["Close"]
    volume = df["Volume"]

    # Moving averages
    sma50  = close.rolling(SHORT_MA).mean()
    sma150 = close.rolling(LONG_MA).mean()
    vol_avg = volume.rolling(VOLUME_AVG_DAYS).mean()

    # Most recent complete values (index -1 = today, -2 = yesterday)
    today_close   = float(close.iloc[-1])
    yest_close    = float(close.iloc[-2])
    today_sma50   = float(sma50.iloc[-1])
    yest_sma50    = float(sma50.iloc[-2])
    today_sma150  = float(sma150.iloc[-1])
    today_vol     = float(volume.iloc[-1])
    avg_vol       = float(vol_avg.iloc[-1])
    vol_ratio     = today_vol / avg_vol if avg_vol > 0 else 1.0

    result.update({
        "date":       df.index[-1].strftime("%Y-%m-%d"),
        "close":      today_close,
        "prev_close": yest_close,
        "sma50":      today_sma50,
        "prev_sma50": yest_sma50,
        "sma150":     today_sma150,
        "vol_today":  today_vol,
        "vol_avg":    avg_vol,
        "vol_ratio":  vol_ratio,
    })

    # ---- BUY signal --------------------------------------------------------
    if TEST_MODE:
        result["buy_signal"] = True
    else:
        # 1. Price crossed above 50-day SMA  (was below yesterday, above today)
        crossed_above_50 = (yest_close <= yest_sma50) and (today_close > today_sma50)
        # 2. Price is rising
        price_rising = today_close > yest_close
        # 3. 50-day SMA is rising
        sma50_rising = today_sma50 > yest_sma50
        result["buy_signal"] = crossed_above_50 and price_rising and sma50_rising

    # ---- SELL signal -------------------------------------------------------
    # Price closes more than SELL_THRESHOLD_PCT% below the 150-day SMA
    pct_below = (today_sma150 - today_close) / today_sma150 * 100
    result["pct_below_150"] = pct_below  # useful context in email
    if TEST_MODE:
        result["sell_signal"] = True
    else:
        result["sell_signal"] = pct_below > SELL_THRESHOLD_PCT

    return result


# ---------------------------------------------------------------------------
# Email composition
# ---------------------------------------------------------------------------

def volume_label(ratio: float) -> str:
    """Human-readable volume description."""
    if ratio >= 2.0:
        return f"{ratio:.1f}x avg — very high volume"
    elif ratio >= 1.3:
        return f"{ratio:.1f}x avg — above average"
    elif ratio >= 0.7:
        return f"{ratio:.1f}x avg — normal volume"
    else:
        return f"{ratio:.1f}x avg — low volume"


def build_email_body(alerts: list[dict]) -> tuple[str, str]:
    """
    Build plain-text and HTML email bodies from a list of alert dicts.
    Each dict has keys: ticker, name, signal, signals (the compute_signals result).
    Returns (plain_text, html).
    """
    date_str = datetime.now().strftime("%d %B %Y")
    buy_alerts  = [a for a in alerts if a["signal"] == "BUY"]
    sell_alerts = [a for a in alerts if a["signal"] == "SELL"]

    # ---- Plain text --------------------------------------------------------
    lines = [f"MA Alert Tracker — {date_str}", "=" * 40, ""]

    if buy_alerts:
        lines.append("BUY SIGNALS (price crossed above rising 50-day SMA)")
        lines.append("-" * 50)
        for a in buy_alerts:
            s = a["signals"]
            lines += [
                f"  {a['name']} ({a['ticker']})",
                f"  Price:      {s['close']:.2f}  (prev: {s['prev_close']:.2f})",
                f"  50-day SMA: {s['sma50']:.2f}  (prev: {s['prev_sma50']:.2f}  ↑ rising)",
                f"  Volume:     {volume_label(s['vol_ratio'])}",
                "",
            ]

    if sell_alerts:
        lines.append("SELL SIGNALS (price dipped below 150-day SMA)")
        lines.append("-" * 50)
        for a in sell_alerts:
            s = a["signals"]
            lines += [
                f"  {a['name']} ({a['ticker']})",
                f"  Price:       {s['close']:.2f}",
                f"  150-day SMA: {s['sma150']:.2f}",
                f"  Dip below:   {s.get('pct_below_150', 0):.2f}%",
                f"  Volume:      {volume_label(s['vol_ratio'])}",
                "",
            ]

    lines += [
        "---",
        "Check your charts before acting. This alert is informational only.",
        "MA Alert Tracker — github.com/YOUR_USERNAME/ma-alert-tracker",
    ]

    plain = "\n".join(lines)

    # ---- HTML --------------------------------------------------------------
    def signal_rows(alert_list, color, label):
        rows = ""
        for a in alert_list:
            s = a["signals"]
            vol_color = "#1a7a3f" if s["vol_ratio"] >= 1.3 else (
                        "#c0392b" if s["vol_ratio"] < 0.7 else "#555")
            if label == "BUY":
                detail = (
                    f"Price <b>{s['close']:.2f}</b> crossed above "
                    f"50-day SMA <b>{s['sma50']:.2f}</b> (SMA ↑ rising)"
                )
            else:
                detail = (
                    f"Price <b>{s['close']:.2f}</b> is "
                    f"<b>{s.get('pct_below_150',0):.2f}%</b> below "
                    f"150-day SMA <b>{s['sma150']:.2f}</b>"
                )
            rows += f"""
            <tr>
              <td style="padding:10px 8px; border-bottom:1px solid #eee;">
                <span style="font-weight:600;">{a['ticker']}</span><br>
                <span style="color:#666; font-size:13px;">{a['name']}</span>
              </td>
              <td style="padding:10px 8px; border-bottom:1px solid #eee; font-size:13px;">{detail}</td>
              <td style="padding:10px 8px; border-bottom:1px solid #eee; font-size:13px; color:{vol_color};">{volume_label(s['vol_ratio'])}</td>
            </tr>"""
        return rows

    sections = ""
    if buy_alerts:
        buy_rows_html = signal_rows(buy_alerts, "#1a7a3f", "BUY")
        sections += (
            "<h2 style='color:#1a7a3f; font-size:16px; margin:24px 0 8px;'>"
            "&#8593; Buy signals &mdash; price crossed above rising 50-day SMA</h2>"
            "<table width='100%' cellpadding='0' cellspacing='0' "
            "style='border-collapse:collapse; font-size:14px; background:#fff; "
            "border:1px solid #e0e0e0; border-radius:6px; overflow:hidden;'>"
            "<thead><tr style='background:#f5f5f5;'>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Instrument</th>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Signal detail</th>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Volume</th>"
            "</tr></thead><tbody>" + buy_rows_html + "</tbody></table>"
        )

    if sell_alerts:
        sell_rows_html = signal_rows(sell_alerts, "#c0392b", "SELL")
        sections += (
            "<h2 style='color:#c0392b; font-size:16px; margin:24px 0 8px;'>"
            "&#8595; Sell signals &mdash; price dipped below 150-day SMA</h2>"
            "<table width='100%' cellpadding='0' cellspacing='0' "
            "style='border-collapse:collapse; font-size:14px; background:#fff; "
            "border:1px solid #e0e0e0; border-radius:6px; overflow:hidden;'>"
            "<thead><tr style='background:#f5f5f5;'>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Instrument</th>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Signal detail</th>"
            "<th style='padding:8px; text-align:left; font-weight:600; font-size:12px; color:#888;'>Volume</th>"
            "</tr></thead><tbody>" + sell_rows_html + "</tbody></table>"
        )


    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif; max-width:680px; margin:0 auto; color:#222; padding:16px;">
  <h1 style="font-size:20px; border-bottom:2px solid #222; padding-bottom:8px;">
    MA Alert Tracker &mdash; {date_str}
  </h1>
  {sections}
  <p style="margin-top:32px; font-size:12px; color:#999; border-top:1px solid #eee; padding-top:12px;">
    Check your charts before acting. This alert is informational only.<br>
    <a href="https://github.com/YOUR_USERNAME/ma-alert-tracker" style="color:#999;">
      github.com/YOUR_USERNAME/ma-alert-tracker
    </a>
  </p>
</body></html>"""

    return plain, html


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------

def send_email(subject: str, plain: str, html: str) -> bool:
    """Send a multipart email via Gmail SMTP. Returns True on success."""
    password = os.environ.get("EMAIL_PASSWORD")
    if not password:
        log.error("EMAIL_PASSWORD environment variable not set.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, password)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        log.info("Email sent successfully.")
        return True
    except Exception as exc:
        log.error(f"Failed to send email: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info(f"Running MA Alert Tracker for {len(TICKERS)} instrument(s)...")
    alerts = []

    for ticker, name in TICKERS.items():
        log.info(f"  Checking {ticker} ({name})...")
        df      = fetch_data(ticker)
        signals = compute_signals(df)

        log.info(f"  Data rows fetched: {len(df)}")
        if signals["error"]:
            log.warning(f"  Skipped {ticker}: {signals['error']}")
            continue
        log.info(f"  buy_signal={signals['buy_signal']} sell_signal={signals['sell_signal']}")

        if signals["buy_signal"]:
            log.info(f"  BUY signal detected for {ticker}")
            alerts.append({"ticker": ticker, "name": name,
                           "signal": "BUY", "signals": signals})

        if signals["sell_signal"]:
            log.info(f"  SELL signal detected for {ticker}")
            alerts.append({"ticker": ticker, "name": name,
                           "signal": "SELL", "signals": signals})

    if not alerts:
        log.info("No signals today. No email sent.")
        return

    n_buy  = sum(1 for a in alerts if a["signal"] == "BUY")
    n_sell = sum(1 for a in alerts if a["signal"] == "SELL")
    parts  = []
    if n_buy:  parts.append(f"{n_buy} buy")
    if n_sell: parts.append(f"{n_sell} sell")
    subject = f"MA Alert: {', '.join(parts)} signal{'s' if len(alerts)>1 else ''} — {datetime.now().strftime('%d %b %Y')}"

    plain, html = build_email_body(alerts)
    send_email(subject, plain, html)
    log.info("Done.")


if __name__ == "__main__":
    main()
