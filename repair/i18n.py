# -*- coding: utf-8 -*-
"""i18n - render the audit harness's Russian output as English.

The audit's code is written in Russian and so are the values it stores in every
result card: the four verdict levels and the reasons attached to them. That is
fine for its author and unusable for anyone else reading the results.

WHAT THIS DOES NOT DO. It does not change the measurement, and it does not
discard the original. `harness.audit_one` runs untouched and its output is
translated afterwards; every translated field keeps the Russian source next to
it under a `_ru` suffix. A translation is a reading aid, and a reading aid that
destroys the original is a liability - if a mapping below is wrong, the raw
value is still in the card to prove it.

The table is exhaustive with respect to `harness.py`: all 37 Russian string
literals reachable in its code were extracted with an AST walk (docstrings and
comments excluded) and are covered here, either as an exact string or as a
pattern for the ones carrying %s/%d placeholders.
"""
import re

# Verdict levels. These four are the load-bearing ones: they decide which gate a
# strategy dies at, so a wrong mapping here would misreport every card.
LEVELS = {
    u"ПРОШЛА":        "PASSED",        # check ran, no defect
    u"НАЙДЕНО":       "FOUND",         # check ran, defect present
    u"НЕ ПРИМЕНИМА":  "NOT-APPLICABLE",  # check could not run, reason given
    u"НЕ ЗАПУСКАЛИ":  "NOT-RUN",       # never reached
}

# Fixed phrases, longest first so that no entry is a prefix of another.
EXACT = {
    u"freqtrade ОТКАЗАЛСЯ анализировать: startup_candle_count=0, "
    u"«приведёт к рекурсивным проблемам у части индикаторов»":
        "freqtrade REFUSED to analyse: startup_candle_count=0, "
        "\"will cause recursive issues for some indicators\"",
    u"движок вышел с кодом 0, но сводки нет "
    u"(ни одной сделки либо вывод не разобран)":
        "engine exited with code 0 but produced no summary "
        "(no trades at all, or output not parsed)",
    u"правила выхода по прибыли берутся из неопубликованного конфига":
        "profit-exit rules come from an unpublished config",
    u"trailing_stop=True без trailing_stop_positive ⇒ стоп тащится "
    u"на ВСЁ расстояние стоп-лосса":
        "trailing_stop=True without trailing_stop_positive => the stop trails "
        "the FULL stoploss distance",
    u"рекурсивных отклонений не найдено": "no recursive drift found",
    u"индикаторы меняются от объёма истории:":
        "indicators change with the amount of history:",
    u"центрированное окно center=True": "centred window center=True",
    u"мёртвые настройки трейлинга": "dead trailing-stop settings",
    u"трейлинг на полном стопе": "trailing at the full stop distance",
    u"minimal_roi закомментирован": "minimal_roi is commented out",
    u"признак утечки будущего": "sign of lookahead leakage",
    u"сдвиг в будущее .shift(-N)": "shift into the future .shift(-N)",
    u"разворот ряда [::-1]": "series reversal [::-1]",
    u"в выборке не отработала": "did not run in the author's window",
    u"смещения не обнаружено": "no bias detected",
    u"вывод не разобран": "output not parsed",
    u"ПРЕВЫШЕНО ВРЕМЯ": "TIMED OUT",
    u"прогрев не объявлен": "warm-up not declared",
    u"прогрев занижен": "warm-up too short",
    u"прогрев объявлен": "warm-up declared",
    u"стратегий к разбору:": "strategies to audit:",
    u"уже есть:": "already present:",
    u"разбираю": "auditing",
    u"в выборке": "in-sample",
    u"вне": "out-of-sample",
    u"утечка:": "lookahead:",
    u"рекурсия:": "recursion:",
}

# Format strings. Ordered: the first pattern that matches wins, so anything
# whose literal prefix could also match a shorter entry must come first.
PATTERNS = [
    (re.compile(r"^ПРЕДМЕТ НЕ ТОТ: стратегия объявила (.+?), движок считал на (.+)$"),
     "WRONG SUBJECT: strategy declared %s, engine computed on %s"),
    (re.compile(r"^ЕСТЬ СМЕЩЕНИЕ: входов (.+?), выходов (.+?) из (.+?) сигналов$"),
     "BIAS PRESENT: %s entries, %s exits out of %s signals"),
    (re.compile(r"^p-значение вне \[0,1\] \((.+?)\) — разбор вывода сломан$"),
     "p-value outside [0,1] (%s) - output parsing is broken"),
    (re.compile(r"^самый длинный индикатор (\d+) свечей, startup_candle_count "
                r"не задан \(по умолчанию 0\)$"),
     "longest indicator is %s candles, startup_candle_count not set (defaults to 0)"),
    (re.compile(r"^trailing_stop=False, но trailing_stop_positive=(.+?) задан — "
                r"читается как работающая защита$"),
     "trailing_stop=False but trailing_stop_positive=%s is set - reads as an "
     "active protection"),
    (re.compile(r"^объявлено (\d+), нужно не менее (\d+)$"),
     "declared %s, needs at least %s"),
    (re.compile(r"^(\d+) при потребности (\d+)$"),
     "%s against a requirement of %s"),
    (re.compile(r"^НЕ ЗАПУСТИЛОСЬ: (.+)$"), "FAILED TO START: %s"),
    (re.compile(r"^код (\d+)$"), "exit code %s"),
]

_EXACT_SORTED = sorted(EXACT.items(), key=lambda kv: -len(kv[0]))


def translate(text):
    """Translate one string. Unknown Russian is returned unchanged, never dropped."""
    if not text or not isinstance(text, str):
        return text
    s = text
    if s in LEVELS:
        return LEVELS[s]
    for rx, tmpl in PATTERNS:
        m = rx.match(s.strip())
        if m:
            return tmpl % m.groups()
    for ru, en in _EXACT_SORTED:
        if ru in s:
            s = s.replace(ru, en)
    for ru, en in LEVELS.items():
        if ru in s:
            s = s.replace(ru, en)
    return s


def has_cyrillic(text):
    return bool(isinstance(text, str) and re.search(u"[А-Яа-яЁё]", text))


def translate_card(card):
    """Translate a result card in place, keeping every original under `_ru`.

    Only the fields the harness fills with Russian are touched; measured numbers
    are never rewritten.
    """
    for run in card.get("runs", {}).values():
        for key in ("level", "why"):
            if key in run and has_cyrillic(run[key]):
                run[key + "_ru"] = run[key]
                run[key] = translate(run[key])
            elif key in run and run.get(key) in LEVELS:
                run[key + "_ru"] = run[key]
                run[key] = LEVELS[run[key]]
    for st in card.get("static", []):
        for key in ("level", "what", "detail"):
            if key in st and (has_cyrillic(st[key]) or st.get(key) in LEVELS):
                st[key + "_ru"] = st[key]
                st[key] = translate(st[key])
    return card
