# -*- coding: utf-8 -*-
"""features - read every strategy file via AST and regex into a feature vector.

Regime analysis needs TRACEABLE labels, not opaque clusters. Every feature here
is a fact that can be checked against the source ("calls ta.RSI", "sets
can_short"); none of them is an interpretation. Interpretation happens in
classify.py and is refutable there, case by case.

AST rather than regex alone: indicator usages are function calls, and telling
`ta.RSI(...)` in code apart from `ta.RSI(...)` inside a comment or a docstring
is guesswork with regex. Where the AST fails - syntax errors, Python 2 leftovers
- the extractor falls back to regex and records that in the `parsed` field, so a
degraded reading is visible rather than silent.
"""
import ast
import io
import re

# Indicator -> family. This classifies the INDICATOR's intent, not the
# strategy's: an RSI can perfectly well sit inside a trend-following system.
# The weighing happens later, in classify.py.
OSCILLATOR = {
    "RSI", "STOCH", "STOCHF", "STOCHRSI", "CCI", "WILLR", "MFI", "ULTOSC",
    "CMO", "fisher_rsi", "rsi", "stoch", "williams_r",
}
TREND = {
    "EMA", "SMA", "TEMA", "DEMA", "KAMA", "WMA", "TRIMA", "T3", "MAMA",
    "SAR", "ADX", "ADXR", "PLUS_DI", "MINUS_DI", "AROON", "AROONOSC",
    "supertrend", "ichimoku", "hma", "vwma", "zema",
}
MOMENTUM = {"MACD", "MACDEXT", "MACDFIX", "ROC", "ROCP", "ROCR", "MOM", "PPO", "TRIX", "APO"}
VOLATILITY = {"ATR", "NATR", "TRANGE", "bollinger_bands", "BBANDS", "keltner_channel", "donchian"}
VOLUME = {"OBV", "AD", "ADOSC", "MFI", "volume_weighted", "VWAP", "vwap"}

RX = {
    "can_short":        re.compile(r"^\s*can_short\s*[:=]\s*True", re.M),
    "enter_short":      re.compile(r"['\"]enter_short['\"]|populate_short|short_entry"),
    "trailing_stop":    re.compile(r"^\s*trailing_stop\s*[:=]\s*True", re.M),
    "custom_stoploss":  re.compile(r"def\s+custom_stoploss\s*\("),
    "custom_exit":      re.compile(r"def\s+custom_(?:exit|sell)\s*\("),
    "position_adjust":  re.compile(r"position_adjustment_enable\s*[:=]\s*True|def\s+adjust_trade_position\s*\("),
    "protections":      re.compile(r"^\s*protections\s*[:=]", re.M),
    "informative":      re.compile(r"@informative|informative_pairs|merge_informative_pair"),
    "freqai":           re.compile(r"freqai|FreqAI|start_training|feature_engineering"),
    "hyperopt_params":  re.compile(r"(?:Decimal|Integer|Categorical|Real)Parameter\s*\("),
    "minimal_roi":      re.compile(r"^\s*minimal_roi\s*[:=]\s*\{", re.M),
    "dca":              re.compile(r"def\s+adjust_trade_position\s*\("),
    "leverage":         re.compile(r"def\s+leverage\s*\(|^\s*leverage\s*[:=]", re.M),
}

RX_TF = re.compile(r"""^\s*timeframe\s*[:=]\s*['"]([^'"]+)['"]""", re.M)
RX_STOP = re.compile(r"^\s*stoploss\s*[:=]\s*(-?[\d.]+)", re.M)
RX_STARTUP = re.compile(r"^\s*startup_candle_count\s*[:=]\s*(\d+)", re.M)


def _calls_ast(src):
    """Names of called functions (trailing attribute, or bare name)."""
    names = set()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute):
                names.add(f.attr)
            elif isinstance(f, ast.Name):
                names.add(f.id)
    return names, tree


def _calls_regex(src):
    return set(re.findall(r"\b(?:ta|qtpylib|pta|finta|indicators)\.(\w+)", src))


def extract(path):
    src = io.open(path, encoding="utf-8", errors="replace").read()
    parsed = True
    try:
        calls, tree = _calls_ast(src)
    except Exception:
        parsed = False
        calls, tree = _calls_regex(src), None

    def fam(s):
        return len(calls & s)

    tf = RX_TF.search(src)
    stop = RX_STOP.search(src)
    startup = RX_STARTUP.search(src)
    roi = RX["minimal_roi"].search(src)

    f = {
        "parsed": parsed,
        "loc": src.count("\n") + 1,
        "timeframe": tf.group(1) if tf else None,
        "stoploss": float(stop.group(1)) if stop else None,
        "startup_candles": int(startup.group(1)) if startup else None,
        "n_oscillator": fam(OSCILLATOR),
        "n_trend": fam(TREND),
        "n_momentum": fam(MOMENTUM),
        "n_volatility": fam(VOLATILITY),
        "n_volume": fam(VOLUME),
        "indicators": sorted((calls & (OSCILLATOR | TREND | MOMENTUM |
                                       VOLATILITY | VOLUME)))[:25],
    }
    for k, rx in RX.items():
        f[k] = bool(rx.search(src))
    f["has_roi_table"] = bool(roi)
    # crossed_above / crossed_below are the signature of signal-driven entries
    f["uses_crossover"] = bool(re.search(r"crossed_(?:above|below)|crossover", src))
    return f
