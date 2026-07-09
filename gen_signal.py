"""
gen_signal.py — Standalone: compute the FULL Growth Book signal (trend +
volatility target + breadth dip-buy) from live data and write docs/signal.json.
This is what the scheduled GitHub Action runs.

Breadth is computed from a ~125-name universe via ONE batched yf.download call
(fast, reliable in CI). If the universe download hiccups, we fall back to the
QQQ-only signal (breadth = null, no dip-buy) so the daily job can never break.

Deps: numpy, pandas, yfinance.  No imports from the rest of the project.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

TARGET_VOL = 0.20
ANN = 252

STOCKS = ("AAPL MSFT GOOGL AMZN META NVDA TSLA AVGO ORCL CRM ADBE CSCO ACN INTC AMD "
          "QCOM TXN IBM NOW INTU MU AMAT LRCX ADI NFLX DIS CMCSA T VZ JPM BAC WFC GS MS "
          "C SCHW BLK AXP SPGI CB PGR USB PNC TFC COF BK MET AIG UNH JNJ LLY MRK ABBV "
          "PFE TMO ABT DHR BMY AMGN CVS MDT GILD ISRG SYK ELV CI VRTX REGN HD MCD NKE "
          "LOW SBUX TJX BKNG GM F MAR PG KO PEP COST WMT MDLZ CL MO PM TGT CAT DE BA HON "
          "UNP UPS GE RTX LMT MMM XOM CVX COP SLB EOG PSX MPC VLO OXY LIN APD SHW FCX "
          "NEM NUE DOW NEE DUK SO D AEP EXC AMT PLD CCI EQIX SPG").split()


def compute_breadth(close: pd.DataFrame) -> tuple[float | None, int]:
    """% of universe stocks above their own 200-day MA (latest day)."""
    cols = [t for t in STOCKS if t in close.columns]
    if len(cols) < 40:
        return None, 0
    sub = close[cols]
    ma = sub.rolling(200).mean().iloc[-1]
    px = sub.iloc[-1]
    valid = ma.notna() & px.notna()
    if int(valid.sum()) < 40:
        return None, int(valid.sum())
    return float((px[valid] > ma[valid]).mean()), int(valid.sum())


def main():
    tickers = ["QQQ"] + STOCKS
    data = yf.download(" ".join(tickers), period="2y", auto_adjust=True,
                       progress=False, threads=True)
    if data is None or data.empty:
        raise SystemExit("download failed")
    close = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]

    qqq = close["QQQ"].dropna()
    ret = qqq.pct_change()
    px = float(qqq.iloc[-1])
    ma200 = float(qqq.rolling(200).mean().iloc[-1])
    vol = float(ret.rolling(20).std().iloc[-1] * np.sqrt(ANN))
    trend = px > ma200
    vt = min(1.0, TARGET_VOL / vol) if trend else 0.0

    breadth, n = compute_breadth(close)          # None => graceful fallback
    dip = bool(trend and breadth is not None and breadth < 0.40)
    target = min(1.0, vt * (1.4 if dip else 1.0))

    out_data = {
        "date": str(qqq.index[-1].date()),
        "qqq": round(px, 2), "ma200": round(ma200, 2), "vol": round(vol, 4),
        "breadth": (round(breadth, 4) if breadth is not None else None),
        "breadth_n": n, "trend": bool(trend), "vt": round(vt, 3),
        "dip": dip, "target": round(target, 3),
    }
    out = Path(__file__).parent / "docs" / "signal.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(out_data))
    print("[gen_signal] wrote", out)
    print("[gen_signal]", out_data)


if __name__ == "__main__":
    main()
