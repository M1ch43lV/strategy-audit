# -*- coding: utf-8 -*-
"""frequenthippo_ranking - read a third party's ranking as a lead list.

WHY THIS IS NOT EVIDENCE. The FrequentHippo dashboard is another operator's
backtest summary. Its ``overall_score_percent`` depends on that operator's
data, pairlists, cost model and scoring, none of which this audit controls or
reproduces. Nothing here is written into a store, no stage reads it, and no
number from it may stand in for a measurement. It answers one question: which
strategies are worth looking at next. This is the same boundary
``evidence.strategy_feed`` draws for the feed, applied to the ranking.

WHAT IT READS. The public page embeds a Grafana table (``uid=his95tj``, panel
"top strategies overall") backed by a Postgres function. Its rows are
identified as ``<strategy>_<exchange>_<market>_<quote>_<timeframe>_<run
profile>``, so one strategy appears once per exchange and quote currency - a
few thousand rows for a handful of strategies. Removing the run tail and
grouping by what is left collapses those repetitions to one rank per
strategy, keeping the best row.

TWO KINDS OF REPETITION, KEPT APART. A strategy on five exchanges is a
*revision* of one strategy and becomes one rank. Two identifiers that the
operator recorded separately but measured on identical trades are also one
strategy under two names; they are merged as well, but counted separately in
the ``trade_twins`` column, so the difference stays visible.

Read-only: one dashboard request, one datasource query, no local write.
``python -m tools.harvest owner/repo`` remains the only writer under
``repos/``.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from urllib.request import Request, urlopen


DASHBOARD = "https://frequenthippo.ddns.net/grafana/api/dashboards/uid/his95tj"
QUERY_URL = "https://frequenthippo.ddns.net/grafana/api/ds/query"
DATASOURCE = {"type": "grafana-postgresql-datasource", "uid": "ffgtqgnoejev4a"}
USER_AGENT = "strategy-audit-ranking/1.0 (+https://github.com/M1ch43lV/strategy-audit)"

# `<strategy>_<exchange>_<market>_<quote>_<timeframe>_<profile>`; the tail is the
# only part that a re-run on another exchange or quote may legitimately change.
RUN_SUFFIX_RE = re.compile(
    r"_(?P<exchange>[a-z0-9]+)_(?P<market>spot|futures|margin)"
    r"_(?P<quote>[A-Z0-9]{2,6})_(?P<timeframe>\d+[mhd])_(?P<profile>\w+)$"
)

# Every published metric of one run. Equal on all of them means equal trades.
TUPLE_KEYS = ("profit_abs_sum", "profit_rel_avg", "sortino_ratio", "cagr_ratio",
              "calmar_ratio", "expectancy", "expectancy_ratio", "worst_dd",
              "trade_count", "winrate", "profit_factor", "timespan_days")


def fetch_bytes(url: str, payload: bytes | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=payload, headers=headers)
    with urlopen(request, timeout=60) as response:  # nosec B310 - fixed HTTPS source
        return response.read()


def panel_sql(title: str) -> str:
    dashboard = json.loads(fetch_bytes(DASHBOARD).decode("utf-8"))["dashboard"]
    for panel in dashboard["panels"]:
        if panel.get("title") == title:
            return panel["targets"][0]["rawSql"]
    raise SystemExit("no panel titled %r in the dashboard" % title)


def rows(title: str) -> list[dict[str, object]]:
    body = json.dumps({
        "queries": [{
            "refId": "A", "datasource": DATASOURCE, "dataset": "db1",
            "rawSql": panel_sql(title), "format": "table", "rawQuery": True,
        }],
        "from": "now-5y", "to": "now",
    }).encode("utf-8")
    payload = json.loads(fetch_bytes(QUERY_URL, body).decode("utf-8"))
    frames = payload["results"]["A"]["frames"]
    if len(frames) != 1:
        raise SystemExit("expected one frame, got %d" % len(frames))
    fields = [field["name"] for field in frames[0]["schema"]["fields"]]
    columns = frames[0]["data"]["values"]
    return [dict(zip(fields, [column[index] for column in columns]))
            for index in range(len(columns[0]))]


def base_name(identifier: str) -> str:
    """Strip the exchange/market/quote/timeframe/profile tail, keep the strategy."""
    return RUN_SUFFIX_RE.sub("", identifier) or identifier


def collapse(rows_: list[dict[str, object]],
             merge_trade_twins: bool = True) -> list[dict[str, object]]:
    """One entry per strategy: best row per base name, then trade-identical twins.

    The metric tuple below is the whole published result set of a run. Two
    identifiers that agree on every one of those values were measured on the
    same trades - the operator resolved a strategy under two names (a file
    name and the class inside it, or a renamed copy). Exact equality is the
    test, not a similarity threshold, which is why no rounding is applied.
    """
    best: dict[str, dict[str, object]] = {}
    variants: dict[str, set[str]] = {}
    for row in rows_:
        name = base_name(str(row["identifier"]))
        variants.setdefault(name, set()).add(str(row["identifier"]))
        previous = best.get(name)
        score = float(row["overall_score_percent"] or 0)
        if previous is None or score > float(previous["overall_score_percent"] or 0):
            best[name] = row
    entries = []
    for name, row in best.items():
        entry = dict(row)
        entry["strategy"] = name
        entry["variant_count"] = len(variants[name])
        entry["trade_twins"] = []
        entries.append(entry)
    if merge_trade_twins:
        # Key -> position in `merged`, so a later, better-scoring twin can
        # replace the keeper in place instead of appending a second rank.
        groups: dict[tuple, int] = {}
        merged: list[dict[str, object]] = []
        for entry in entries:
            key = tuple(entry.get(name) for name in TUPLE_KEYS)
            position = groups.get(key)
            if position is None:
                groups[key] = len(merged)
                merged.append(entry)
                continue
            keeper = merged[position]
            winner, loser = sorted(
                (keeper, entry),
                key=lambda item: (-float(item["overall_score_percent"] or 0),
                                  str(item["strategy"])))[:2]
            winner["trade_twins"].append(str(loser["strategy"]))
            winner["variant_count"] = (int(winner["variant_count"])
                                       + int(loser["variant_count"]))
            merged[position] = winner
        entries = merged
    entries.sort(key=lambda entry: float(entry["overall_score_percent"] or 0),
                 reverse=True)
    return entries


def write_csv(entries: list[dict[str, object]], limit: int, stream) -> None:
    writer = csv.writer(stream)
    writer.writerow(["rank", "strategy", "score_pct", "variants", "trade_twins",
                     "identifier", "profit_abs_sum", "sortino_ratio",
                     "cagr_ratio", "worst_dd", "trade_count", "winrate"])
    for rank, entry in enumerate(entries[:limit], start=1):
        writer.writerow([rank, entry["strategy"],
                         "%.2f" % float(entry["overall_score_percent"]),
                         entry["variant_count"],
                         "; ".join(entry["trade_twins"]),
                         entry["identifier"],
                         entry["profit_abs_sum"], entry["sortino_ratio"],
                         entry["cagr_ratio"], entry["worst_dd"],
                         entry["trade_count"], entry["winrate"]])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", default="top strategies overall")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--no-trade-merge", action="store_true",
                        help="keep trade-identical identifiers as separate ranks")
    args = parser.parse_args(argv)
    entries = collapse(rows(args.panel), merge_trade_twins=not args.no_trade_merge)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    write_csv(entries, args.top, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
