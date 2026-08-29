"""Episode and transition tables for daily categorical states."""
from __future__ import annotations

import pandas as pd


def build_episodes(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair, group in frame.sort_values(["pair", "date"]).groupby("pair", sort=True):
        group = group.reset_index(drop=True)
        boundary = group["coin_regime"].ne(group["coin_regime"].shift())
        boundary |= group["date"].diff().gt(pd.Timedelta(days=1))
        for episode_id, episode in group.groupby(boundary.cumsum(), sort=True):
            rows.append({
                "pair": pair,
                "episode_id": int(episode_id),
                "regime": episode["coin_regime"].iloc[0],
                "start": episode["date"].iloc[0],
                "end": episode["date"].iloc[-1],
                "days": len(episode),
            })
    return pd.DataFrame(rows)


def build_transitions(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair, group in frame.sort_values(["pair", "date"]).groupby("pair", sort=True):
        previous = group["coin_regime"].shift()
        changed = previous.notna() & previous.ne(group["coin_regime"])
        counts = (pd.DataFrame({"from_state": previous[changed],
                                "to_state": group.loc[changed, "coin_regime"]})
                  .value_counts().sort_index())
        for (from_state, to_state), count in counts.items():
            rows.append({"pair": pair, "from_state": from_state,
                         "to_state": to_state, "count": int(count)})
    return pd.DataFrame(rows)


def episode_ids(dates: pd.Series, states: pd.Series, prefix: str) -> pd.Series:
    boundary = states.ne(states.shift()) | dates.diff().gt(pd.Timedelta(days=1))
    numbers = boundary.cumsum().astype(int)
    return numbers.map(lambda value: f"{prefix}-{value:04d}")
