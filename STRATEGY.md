# Strategy — research backing, design decisions, and known limitations

This document explains the reasoning behind the two signals this tracker uses,
where the ideas come from, and where the approach has genuine weaknesses. It is
intended to be read alongside the technical documentation in the README.

---

## The two signals and why they are defined this way

### Buy signal — three conditions, all required

The buy signal fires only when all three of the following are true on the same
daily close:

1. **Price crosses above the 50-day SMA** — it was at or below the line
   yesterday and is above it today. A cross that happened several days ago does
   not count.
2. **Price is higher than the previous day's close** — the stock itself is
   moving upward on the day of the cross, not drifting sideways into the line.
3. **The 50-day SMA is higher than it was yesterday** — the moving average
   itself is trending up, confirming that the broader medium-term trend is
   rising and not flat or declining.

All three conditions are required together. Any single one alone is weak — it
is the combination that gives the signal meaning.

### Sell signal — one condition with a minimum threshold

The sell signal fires when:

- Price closes more than **0.5% below the 150-day SMA**

The threshold exists to filter out insignificant "touches" of the line — a
single candle barely grazing the MA in an otherwise healthy uptrend. A close
of 0.5% or more below the line is a meaningful breach for a diversified index
fund, which by its nature moves more smoothly than individual stocks.

Crucially, the signal does **not** wait for the 150-day SMA itself to visibly
turn downward. That would introduce additional lag and mean acting only after a
significant portion of the decline has already happened. The premise is: if
price has convincingly broken below the long-term trend line, that is enough
reason to pay close attention — regardless of where the MA is heading.

Volume is included in the alert email as context (e.g. "1.8x average — above
average") to help judge whether the move is backed by real selling pressure,
but it does not gate the alert. Volume confirmation is left to the investor's
discretion after receiving the notification.

---

## Research backing and intellectual lineage

The 50-day and 200-day MAs are genuinely widely watched by institutional
investors, fund managers, and analysts. Because so many people watch them, they
become somewhat self-fulfilling — enough traders act on the crossover that it
creates real price momentum. This is well documented.

The specific logic here — requiring the MA itself to be rising, not just the
price crossing it — is a more sophisticated version of a classic strategy called
the "golden cross." Requiring trend confirmation before acting is a legitimate
improvement that reduces false signals.

The 150-day MA specifically was popularised by Stan Weinstein in his book
*Secrets for Profiting in Bull and Bear Markets* (1988), which is still widely
read in technical analysis circles. His Stage Analysis method uses the 30-week
MA (which is roughly 150 days) as the key line separating bull and bear phases
for a stock. The sell signal in this tracker has a direct lineage from that
framework.

---

## Known limitations

Moving average strategies are trend-following by nature, which means they are
always lagging — you never catch the exact bottom or top, you catch the middle
of a move. For index funds specifically, research consistently shows that simple
buy-and-hold outperforms MA-based timing strategies over long periods (10+
years), largely because:

- You miss some of the best days in the market while sitting out
- Transaction costs and taxes eat into gains from switching in and out
- The signals produce whipsaws in sideways markets — you get stopped out and
  back in repeatedly for small losses

These are not minor caveats. They are the central reason why passive index
investing consistently beats active timing for most retail investors over long
horizons.

---

## Where it genuinely adds value

For a long-term investor the best use of this tool is not as a strict
mechanical buy/sell system, but as a **risk management alert** — a signal to
pay closer attention, review your position, and make a conscious decision rather
than reacting emotionally to news. That framing is how most professional
discretionary investors use technical indicators.

In that context, the tracker serves a specific and honest purpose: it removes
the need to watch charts daily, surfaces the moments that are worth a second
look, and leaves the decision entirely with the investor.

---

## Further reading

- Stan Weinstein, *Secrets for Profiting in Bull and Bear Markets* (1988)
- Meb Faber, *A Quantitative Approach to Tactical Asset Allocation* (2007) —
  one of the more rigorous academic treatments of MA-based timing for index
  funds, freely available online
- Hendrik Bessembinder, *Do Stocks Outperform Treasury Bills?* (2018) — useful
  context on long-term buy-and-hold performance
