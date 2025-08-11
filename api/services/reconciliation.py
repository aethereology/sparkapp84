import os, csv, json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List

def dec(v: str) -> Decimal:
    return Decimal(v or "0").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _load_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def run_reconciliation(data_dir: str) -> Dict:
    sq_path = os.path.join(data_dir, "donations.csv")
    internal_path = os.path.join(data_dir, "internal_donations.csv")
    sq = _load_csv(sq_path) if os.path.exists(sq_path) else []
    internal = _load_csv(internal_path) if os.path.exists(internal_path) else []
    def rollup(rows: List[Dict]):
        by_des, total = defaultdict(Decimal), Decimal("0.00")
        for r in rows:
            des = r.get("designation") or "General Fund"
            amt = dec(r.get("amount"))
            by_des[des] += amt; total += amt
        return {"total": f"{total:.2f}", "by_designation": {k: f"{v:.2f}" for k,v in sorted(by_des.items())}}
    res = {"square": rollup(sq), "internal": rollup(internal)}
    try:
        res["variance_total"] = f'{Decimal(res["square"]["total"]) - Decimal(res["internal"]["total"]):.2f}'
    except Exception:
        res["variance_total"] = None
    with open(os.path.join(data_dir, "reconciliation_report.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    return res

def latest_report(data_dir: str):
    try:
        with open(os.path.join(data_dir, "reconciliation_report.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"status":"no report"}
