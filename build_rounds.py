#!/usr/bin/env python3
"""
build_rounds.py — fetch real DAILY candles from Stooq for the Predict-the-Graph
game. Stooq's free CSV is commercial-friendly and serves decades of daily
history, which also gives you a large, varied pool (no repeats).

Why Stooq + daily (not 5-minute):
    Stooq's free download is a daily data source. Free intraday/5-minute history
    is not reliably available there, so true 5-min commercially needs a paid
    vendor (Alpha Vantage / Polygon / Tiingo). Daily from Stooq is the clean,
    free, commercial-safe choice — and gives FAR more variety than 5-min would.

No API key needed. No extra libraries — uses only Python's standard library.

USAGE
-----
    python build_rounds.py

Writes rounds.json next to the game. Run it once on your own machine
(it needs internet; the game itself makes no API calls afterward).

LICENSE NOTE
------------
Raw price values are facts (not copyrightable), and Stooq's free data is widely
used. Still, for a paid product, confirm Stooq's current terms permit
redistributing historical data inside a commercial app, and consider a brief
legal check. This file documents the source so your provenance is clean.
"""

import csv, io, json, random, sys, time, urllib.request

# ----------------------------- CONFIG --------------------------------------
# Stooq US tickers use a ".us" suffix (handled automatically below).
TICKERS = [
    "SPY",   # broad index ETF
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD",
    "QQQ",   # tech index
    "META", "AMZN", "GOOGL", "JPM", "NFLX",
    "KO",    # slow mover (variety)
    "XOM",   # commodity-linked
    "GLD",   # gold ETF (different regime)
]
WINDOW       = 80      # daily candles per round (history + future)
HISTORY_FRAC = 0.6     # fraction shown as history before prediction
ROUNDS_OUT   = 300     # total windows to emit
TIMEFRAME_LABEL = "1D"
SEED         = 7
OUT_PATH     = "rounds.json"
REQUEST_PAUSE = 0.4    # seconds between requests, be polite to the server
# ---------------------------------------------------------------------------


def stooq_symbol(t):
    """Map a plain US ticker to Stooq's symbol convention."""
    t = t.lower()
    return t if "." in t else f"{t}.us"


def fetch_daily(ticker):
    """Download daily OHLCV from Stooq as a list of [date,o,h,l,c,v] rows."""
    sym = stooq_symbol(ticker)
    url = f"https://stooq.com/q/d/l/?s={sym}&i=d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", "replace")
    # Stooq returns "No data" (or an HTML error) when a symbol is unknown.
    if not text or "No data" in text or "<html" in text.lower():
        raise ValueError("no data returned")
    rows = list(csv.DictReader(io.StringIO(text)))
    out = []
    for r in rows:
        try:
            out.append([
                r["Date"],
                float(r["Open"]), float(r["High"]),
                float(r["Low"]),  float(r["Close"]),
                float(r.get("Volume") or 0),
            ])
        except (ValueError, KeyError):
            continue  # skip malformed/blank lines
    return out


def main():
    random.seed(SEED)
    pool = []

    for t in TICKERS:
        print(f"Fetching {t} ...", flush=True)
        try:
            rows = fetch_daily(t)
        except Exception as e:
            print(f"  skipped {t}: {e}")
            continue
        if len(rows) < WINDOW + 5:
            print(f"  not enough data for {t} ({len(rows)} rows)")
            continue

        o = [r[1] for r in rows]; h = [r[2] for r in rows]
        l = [r[3] for r in rows]; c = [r[4] for r in rows]
        v = [r[5] for r in rows]
        n = len(c)

        # carve non-overlapping windows across the full history
        starts = list(range(0, n - WINDOW, WINDOW))
        random.shuffle(starts)
        for s in starts:
            cseg = c[s:s + WINDOW]
            if min(cseg) <= 0 or max(cseg) / min(cseg) > 8:
                continue  # skip degenerate / split-distorted windows
            candles = [[round(o[i], 4), round(h[i], 4), round(l[i], 4),
                        round(c[i], 4), int(v[i])] for i in range(s, s + WINDOW)]
            pool.append({
                "asset": t,
                "window": f"{WINDOW} sessions",
                "candles": candles,
                "series": [round(x, 4) for x in cseg],
            })

        time.sleep(REQUEST_PAUSE)

    if not pool:
        sys.exit("No windows produced — check your network / tickers.")

    random.shuffle(pool)
    rounds = pool[:ROUNDS_OUT]
    out = {
        "window": WINDOW,
        "history_frac": HISTORY_FRAC,
        "format": "ohlcv",
        "timeframe": TIMEFRAME_LABEL,
        "source": "Stooq",
        "rounds": rounds,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f)
    print(f"\nWrote {len(rounds)} rounds across "
          f"{len(set(r['asset'] for r in rounds))} tickers to {OUT_PATH}")


if __name__ == "__main__":
    main()
