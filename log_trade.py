"""
log_trade.py — append one transaction to docs/transactions.csv (the tracker's data store).

Examples:
  python log_trade.py schwab deposit --amount 100000
  python log_trade.py schwab buy  --shares 90 --price 711.44
  python log_trade.py etrade sell --shares 20 --price 715 --date 2026-07-10
  python log_trade.py schwab mark --price 711.44        # weekly value snapshot

After logging, refresh the local page:  python generate_tracker.py
…and/or push so the hosted site updates:  (cd ~/growth-book && git add docs/transactions.csv && git commit -m trade && git push)
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
from pathlib import Path

FILE = Path(__file__).parent / "docs" / "transactions.csv"


def main():
    ap = argparse.ArgumentParser(description="Append a transaction to docs/transactions.csv")
    ap.add_argument("account", choices=["schwab", "etrade"])
    ap.add_argument("type", choices=["deposit", "withdraw", "buy", "sell", "mark"])
    ap.add_argument("--shares", type=float)
    ap.add_argument("--price", type=float)
    ap.add_argument("--amount", type=float)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()

    if a.type in ("buy", "sell") and (a.shares is None or a.price is None):
        ap.error(f"{a.type} requires --shares and --price")
    if a.type in ("deposit", "withdraw") and a.amount is None:
        ap.error(f"{a.type} requires --amount")
    if a.type == "mark" and a.price is None:
        ap.error("mark requires --price")

    row = [
        a.account, a.date, a.type,
        a.shares if a.type in ("buy", "sell") else "",
        a.price if a.type in ("buy", "sell", "mark") else "",
        a.amount if a.type in ("deposit", "withdraw") else "",
    ]
    with open(FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)
    print("[log_trade] appended:", ",".join(str(x) for x in row))
    print("[log_trade] ->", FILE)


if __name__ == "__main__":
    main()
