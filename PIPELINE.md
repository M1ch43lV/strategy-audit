# Pipeline — welches Programm läuft wann, und was es anfasst

Handgeschrieben, nicht generiert: anders als `STRATEGY_STATUS.csv` oder
`RUNTIME_ENVIRONMENTS.md` ändert sich diese Abfolge nicht mit jeder Messung,
sondern nur, wenn sich die Prüfkette selbst ändert. Wer eine neue Stufe
einbaut oder eine bestehende umbaut, aktualisiert diese Datei von Hand.

Diese Datei beantwortet eine einzige Frage: **in welcher Reihenfolge laufen
die Skripte, und welche Datei liest/schreibt welches?** Was jede Stufe
inhaltlich bedeutet und warum sie so und nicht anders entschieden wurde,
steht in `REGIME_PREREGISTRATION.md` (bindend) und `REGIME_AUDIT_PLAN.md`
(Referenz) — siehe `DOCUMENT_MAP.md` für die Lesereihenfolge dorthin.

Alle nativen Läufe (nicht Docker) brauchen den Python-Interpreter aus
`ftenv/Scripts/python.exe` (dort ist `freqtrade`/`pandas` installiert, nicht
im System-Python) — meist über die Umgebungsvariable `PROFILE_PYTHON`.

## Stufe 0 — Corpus-Erfassung (einmalig, oder wenn neue Repos dazukommen)

| Programm | Liest | Schreibt |
|---|---|---|
| `tools/harvest.py` | GitHub-API (nur `.py`-Dateien mit `IStrategy`) | Dateien unter `repos/<repo>/` |
| `tools/census_repos.py` | `evidence/corpus_sources.json`, `repos/**` | Statistiken zu Kopie-Familien (Konsole/Referenz für `evidence/exclusion_criteria.py`s C-Text) |
| `evidence/new_repo_candidates.py` | GitHub-Themensuche, `evidence/corpus_sources.json` | `evidence/NEW_REPO_CANDIDATES.json`, `evidence/NEW_REPO_CANDIDATES.md` |
| `evidence/repo_freshness.py` | lokales `git log` je Repo, GitHub-Tip, `evidence/EXECUTION_PROFILES.csv` | `evidence/REPO_FRESHNESS.csv`, `evidence/REPO_FRESHNESS.md` |

Ergebnis dieser Stufe: neue Zeilen in `evidence/EXECUTION_PROFILES.csv` (eine Zeile pro
Strategie-Implementierung, die kanonische Quelle für den ganzen Rest der
Kette).

## Stufe 1 — Probelauf (lädt die Strategie, prüft ob überhaupt gehandelt wird)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/profile_smoke.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/PROFILE_CLASS1.json` (Reparatur-Regeln) | `evidence/PROFILE_SMOKE.json` |

Seit dem prospektiven Amendment vom 2026-09-10 ist der Probelauf eine feste
Kaskade: `20200301-20200401` (1 Monat), bei weniger als 10 Trades
`20200301-20200601` (3 Monate), danach `20200301-20210301` (1 Jahr). Er stoppt
beim ersten Ergebnis mit mindestens 10 Trades und speichert alle Versuche.
Fehler/Timeouts werden nicht durch ein längeres Fenster als bestanden
umgedeutet. Bereits vorhandene Vollfenster-Evidenz bleibt vorrangig.

**2026-09-06, erledigt:** `ELIGIBILITY_NEVER_RUN.json` und
`ELIGIBILITY_TRAP_SMOKE.json` waren einmalige Fallback-Stores früherer
Wellen (kein Runner im aktuellen Repo schrieb sie neu) — 65 der 83 Zeilen
darin hatten keinen eigenen `evidence/PROFILE_SMOKE.json`-Eintrag, `evidence/strategy_status.py`
fiel für sie auf diese beiden Dateien zurück. Per gezieltem
`evidence/profile_smoke.py --strategy ... --profiles spot_long futures_long unknown`
nachgeholt (empirisch geprüft: vorher änderten sich 65 von 83 Zeilen in
`STRATEGY_STATUS.csv`, wenn man die Dateien wegließ, danach keine einzige
mehr) und beide Dateien entfernt, inklusive der Fallback-Schleife in
`evidence/strategy_status.py`.

Scheitert der Probelauf an einem benannten, behebbaren Hindernis (fehlender
`timeframe`, fehlendes lokales Modul, Signatur-Änderung von freqtrade/pandas/
numpy), greift eine der folgenden Reparaturrouten, danach läuft Stufe 1 für
diese Zeile erneut:

| Reparaturroute | Schreibt |
|---|---|
| `evidence/eligibility_timeframe_evidence.py` → `evidence/eligibility_timeframe_repair.py` | `evidence/ELIGIBILITY_TIMEFRAME_EVIDENCE.json`, `evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json` |
| `repair/local_modules.py` | `evidence/REPAIR_LOCAL_MODULES.json` |
| `repair/patch_class2.py`-artige Signatur-Reparaturen | `evidence/ELIGIBILITY_SIGNATURE_REPAIR.json` |
| `repair/compat_signature.py` (17 Shims, automatisch über `evidence/profile_freqtrade.py` geladen) | kein eigener Store — wirkt zur Laufzeit, protokolliert in `evidence/PROFILE_CLASS1.json` |

## Stufe 2 — Bias-Ausschlussprüfung: Look-Ahead zuerst

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/profile_bias.py` (`run_diagnostic`, native oder Docker) | `evidence/EXECUTION_PROFILES.csv`, Reparatur-Stores | `evidence/PROFILE_BIAS.json` |
| `evidence/eligibility_lookahead_backfill.py` | `STRATEGY_STATUS.csv`, `evidence/EXECUTION_PROFILES.csv`, `evidence/WARMUP_CONVERGENCE.json`, `evidence/PROFILE_CLASS1.json` | `evidence/ELIGIBILITY_LOOKAHEAD_BACKFILL.json` |
| `evidence/profile_bias_merge.py` | disjunkte Shard-Dateien (bei parallelen Läufen) | die kanonische `evidence/PROFILE_BIAS.json` |

Ein nativer Look-Ahead-Befund `FOUND` ist ein finaler Informationsleck-Ausschluss.
Dann laufen weder Warm-up-Leiter noch Recursive-Bias: Sie können ein
Informationsleck nicht reparieren.

Das Diagnoseintervall ist seit dem Amendment vom 2026-09-10 in beiden Modi
identisch: `20200301-20200601`. Ein gespeicherter Futures-Leiterlauf über nur
einen Monat oder ein Spot-Lauf über `20190101-20190401` ist historische
Provenienz und muss vor einer neuen Entscheidung supersediert und erneut
gemessen werden.

Eine Ausnahme gilt für die Arbeits-Queue: Ein erfolgreicher kanonischer
gepoolter Stage-8-Full-Backtest schließt die ihm vorangehende technische
Prüfkette für genau dieselbe Implementierung. `evidence/strategy_status.py`
zeigt dies als `technical_chain_complete=true` und setzt dann kein `open_work`,
wenn Source-Hash und Run-Profil mit
`results/regime/full_backtest_manifest.json` übereinstimmen. Das ist kein
nachträglicher E1-Zugang und hebt keinen dokumentierten Ausschluss auf;
fehlgeschlagene, OOM- oder Timeout-Stage-8-Versuche zählen nicht als Abschluss.

Unabhängig davon ist jede Zeile im Kohortenwert `excluded` ein abgeschlossener
Arbeitsfall: Sie bleibt mit Ausschlussgrund und Belegen sichtbar, erhält aber
kein `open_work`. `exclusion_unconfirmed` ist ausdrücklich nicht synonym dazu;
diese noch nicht verdienten Ausschlüsse bleiben offen, bis die fehlende
Entscheidungsevidenz vorliegt.

Zusätzlich hat der Owner am 2026-09-10 für Stufe 8 entschieden: Eine zuvor
zugelassene Strategie mit `full_backtest_status` `failed`,
`resource_inconclusive` oder `timeout` ist für diesen Benchmark nicht testbar
und wird als C10 `full_backtest_not_testable` final ausgeschlossen. Diese drei
Zustände werden nicht erneut in den Full-Backtest eingeplant.

## Stufe 3 — Warm-up-Konvergenzleiter nach bestandenem Look-Ahead

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/warmup_convergence.py` (`lookahead_pass`) | `evidence/EXECUTION_PROFILES.csv`, identitätsgebundener Look-Ahead-PASS, Reparatur-Stores | `evidence/WARMUP_CONVERGENCE.json` |

Nur eine Look-Ahead-Zeile mit `PASS` kann diese Stufe erreichen. `NA` ist kein
Pass und erhält keine Folgemessung, bis die technische Ursache geklärt ist. Die
eingefrorene Konvergenzleiter ist 1, 2, 7, 14, 30, 90, 365 Tage, umgerechnet in
Kerzen über den eigenen Zeitrahmen. Eine Zeile ist `converged`,
`not_converged_within_ladder` oder `inconclusive`.

## Stufe 4 — Finaler Recursive-Bias nach konvergiertem Warm-up

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/profile_bias.py` (`recursive`, native oder Docker) | `evidence/EXECUTION_PROFILES.csv`, gespeicherter Look-Ahead-PASS und konvergierte Leiter mit gewähltem Startwert | `evidence/PROFILE_BIAS.json` |

Der finale Recursive-Lauf erhält den kleinsten konvergierten
`chosen_startup_candle_count` der Leiter explizit als `--startup-candle`. Ohne
Look-Ahead-`PASS` und aktuelle konvergierte Leiter wird er durch den Runner
deferiert. Damit kann weder eine zu kurze Autorenangabe noch Freqtrades
Standard-Warm-up den finalen Befund bestimmen.

## Stufe 5 — Datenabdeckung (Coverage)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/regime_coverage.py` | `evidence/EXECUTION_PROFILES.csv`, Kerzendateien unter `user_data/data/binance` | `evidence/REGIME_COVERAGE.csv`, `evidence/REGIME_COVERAGE.md` |

Reine Dateisystem-Prüfung (keine Freqtrade-Ausführung), pro `(mode,
timeframe)` gecacht — günstig, jederzeit sicher neu zu erzeugen. Deckt aktuell
alle 1.050 Zeilen ab; der historische Stand vom 2026-09-06 betrug 919.

## Stufe 6 — Zusammenführung

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/strategy_status.py` | **alles** aus Stufe 0–5 plus `evidence/REGIME_ELIGIBILITY.csv` (invalidierter historischer E0-Snapshot, ausschließlich Provenienz), `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` (aktive E1-Entscheidungen), `evidence/STRATEGY_CLASSIFICATION.json`, `evidence/MARKET_PHASE_HYPOTHESIS.json`, `evidence/BLOCKED_TRIAGE.json` | `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, **im selben Lauf automatisch**: `evidence/exclusion_criteria_list.md`, `evidence/repair_measures_list.md`, `RUNTIME_ENVIRONMENTS.md` |

Ein einziger Aufruf (`python -m evidence.strategy_status`) schreibt alle fünf Dateien.
`--check` prüft nur, ob sie noch aktuell sind (schreibt nichts); `--selftest`
läuft die eingebauten Konsistenz-Prüfungen.

E0 ist keine Rückfalloption: seine 67 alten `regime_eligible=true`-Flags dürfen
keinen Check ersetzen und keine Zeile zulassen. Nur eine aktive
`admitted_E1`-Entscheidung erzeugt `cohort=E1_expanded`; die alte E0-
Mitgliedschaft erscheint lediglich in `gate_notes`.

## Stufe 7 — Zulassung (Admission)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/eligibility_admit_converged.py` (aktuelle Regel, `converged_clean_gates_v1`) | `STRATEGY_STATUS.csv`, `evidence/WARMUP_CONVERGENCE.json` | hängt neue `admitted_E1`-Zeilen an `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` an |
| `evidence/eligibility_expansion_adjudicate.py` (ältere Wave-B/C-Regeln, `zero_warmup_analyzer_adapter_v1` / `native_gate_pass_v1`) | `evidence/ELIGIBILITY_EXPANSION_PROOFS.json`, `evidence/ELIGIBILITY_EXPANSION_WARMUP.json`, `evidence/ELIGIBILITY_EXPANSION_LOOKAHEAD.json`, `evidence/ELIGIBILITY_EXPANSION_EQUIVALENCE.json` | dieselbe `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, plus `.md`-Bericht |

**Danach zwingend zurück zu Stufe 6.** Die Zulassungs-Entscheidung steht erst
in `STRATEGY_STATUS.csv`, wenn `evidence/strategy_status.py` erneut läuft und die
erweiterte `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` zurückliest. Ein Lauf
von Stufe 7 ohne anschließende Stufe 6 zeigt in `STRATEGY_STATUS.csv` noch
den alten Stand.

## Stufe 8 — Backtest über das volle Fenster

Zwei strukturell verschiedene, beide nötige Messungen (siehe
`REGIME_AUDIT_PLAN.md` §28.1) — keine ersetzt die andere:

| Programm | Zweck | Liest | Schreibt |
|---|---|---|---|
| `evidence/profile_full_window.py` (paarweise sharded) | Stage-7-Bestätigung: handelt die Strategie über das ganze Fenster, pro Paar | `evidence/EXECUTION_PROFILES.csv` | `evidence/PROFILE_FULL_WINDOW.json` (oder Shard-Dateien bei parallelen Containern) |
| `evidence/merge_full_window_shards.py` | führt Shards zusammen | `evidence/PROFILE_FULL_WINDOW_shardA.json`, `_shardB.json`, `_shardTF.json` | die kanonische `evidence/PROFILE_FULL_WINDOW.json` |
| `regime/full_backtest.py` (gepoolt, `canonical_pooled_native_pair_universe`) | Phase A: tatsächlicher Performance-Backtest über alle 8 Paare gepoolt | `STRATEGY_STATUS.csv` (E1-Kohorte) | `results/regime/full_backtest_manifest.json`, `full_backtest_native.json` |

`evidence/PROFILE_FULL_WINDOW.json` fließt zurück in Stufe 5 (`evidence/strategy_status.py`
liest es für `observed_trades`/`trade_evidence`). Die gepoolten
Backtest-Ergebnisse aus `regime/full_backtest.py` fließen **nicht** in die
Zulassung zurück — sie sind die Datengrundlage für Stufe 9.

**Missverständnis, das sich anbietet: "Einzelpaar" heißt nicht "jedes Paar
vollständig gemessen".** `evidence/profile_full_window.py` ist eine Ja/Nein-Schranke,
keine Performance-Messung: Sie beantwortet nur "handelt die Strategie über
das ganze Fenster überhaupt, bei mindestens einem Paar?" Sobald EIN Paar
Trades produziert, ist die Frage beantwortet und der Rest der Paarliste
wird für diese Strategie nicht mehr angefasst (Kommentar im Skriptkopf:
"One positive pair is sufficient to resolve a zero-trade smoke as
positive... Sharding does not replace pooled performance backtests"). Nur
wenn ALLE konfigurierten Paare null Trades liefern, muss wirklich jedes
einzelne durchgelaufen sein, um "0 Trades" zu bestätigen — deshalb zeigen
`evidence/PROFILE_FULL_WINDOW_shardA.json`/`_shardB.json` bei vielen Strategien
weniger abgeschlossene Paar-Messungen als konfigurierte Paare, obwohl die
Strategie selbst schon als `measured` gilt.

Die tatsächliche Vollständigkeit — jedes Paar, über das komplette
6,5-Jahres-Fenster, ohne Abbruch — liefert ausschließlich
`regime/full_backtest.py` (Zeile darüber): der ruft freqtrade ohne
`--pairs`-Filter auf, also mit der kompletten Paarliste gemeinsam in einem
einzigen Backtest, und bricht nie früh ab.

**Performance-Limit statt endlosem Retry.** Der 3600s-Timeout ist eine
harte Grenze, nicht pro Strategie einstellbar. `SuperHV27` und `Schism`
liefen je zweimal unabhängig exakt bis zur 3600s-Grenze, ohne Absturz und
ohne OOM-Signatur — die Kompatibilitäts-Shims (`repair/compat_signature.py`)
haben den ursprünglichen Absturz behoben, aber die verbleibenden
Pro-Trade-Kosten über 8 Paare und 6,5 Jahre reichen dafür nicht.
`evidence/POOLED_BACKTEST_PERFORMANCE_LIMIT.json` hält diese Bestätigung fest (Regel:
mindestens zwei unabhängige Timeouts, keine andere Fehlerart dazwischen);
`regime/full_backtest.py` liest sie und setzt den Status einmalig auf
`performance_limited`, statt bei jedem Container-Durchlauf erneut eine
volle Stunde zu verbrauchen. Die Strategie bleibt zugelassen
(`E1_expanded`) — es fehlt ihr dauerhaft nur die gepoolte
Performance-Kennzahl für Stufe 9.

**Dasselbe Prinzip für bestätigten Speichermangel.** 52 Strategien
(BBRSI2/BBands/BinHV45-\*/Cluc\*-Familie u.a.) waren `resource_inconclusive`
sowohl unter der ursprünglichen 13-14GB/`--workers 2`-Einstellung als auch
danach, nach der Anhebung auf 16GB VM-Speicher mit `--workers 1` am
2026-09-07 — ein einzelner Prozess mit dem vollen Speicherbudget, keine
Nebenläufigkeit mehr, die die Schuld tragen könnte. Das entkräftet
Ressourcenkonkurrenz als Ursache; übrig bleibt der eigene
Speicherverbrauch der Strategie über 8 Paare und 6,5 Jahre.
`evidence/POOLED_BACKTEST_OOM_LIMIT.json` hält die Bestätigung fest,
`regime/full_backtest.py` setzt den Status einmalig auf `oom_confirmed`
statt endlos erneut zu versuchen. Auch hier: weiterhin zugelassen, nur
ohne Stufe-9-Kennzahl.

**Dritte Kategorie: unbegrenztes Einsatzwachstum.** `FastSupertrend_optim3_rsi_75lev`
scheiterte bei 37% des gepoolten Laufs mit `Stake amount 12570778.900608359
too high for XMR/USDT:USDT`. Ursache: `runtime/profile_futures_config.json` setzt
`stake_amount: unlimited`, die Strategie hält 5×-Hebel fest und lässt
Gewinne laufen (`minimal_roi = {"0": 0.99}`) — über genug profitable Jahre
wächst das Wallet exponentiell, bis der errechnete Einsatz jede reale
Marktliquidität übersteigt. Anders als bei den ersten beiden Kategorien
ist das zu 100% deterministisch: kein Zusammenhang mit Speicher, Workern
oder Zeit, ein Retry reproduziert exakt denselben Fehler an derselben
Stelle. Auch von keiner früheren Stufe erkennbar — der Probelauf nutzt
dieselbe Config, aber nur ein Monat, viel zu kurz für diese Art
Verzinsung, und Recursive-/Look-Ahead-Bias prüfen auf Informationslecks,
nicht auf Kapitalskalierung. `evidence/POOLED_BACKTEST_STAKE_OVERFLOW.json` hält
die Bestätigung fest, derselbe Mechanismus wie oben setzt
`stake_overflow_confirmed`. Nicht geprüft: ob weitere gehebelte
Strategien dasselbe Risiko tragen — bewusst offen gelassen.

**Korrektur 2026-09-07: `evidence/profile_full_window.py` ist nicht für die ganze
E1-Kohorte nötig, nur für Zero-Trade-Kandidaten.** Die Zitation oben
(`REGIME_AUDIT_PLAN.md` §28.1) trägt diese Behauptung nicht — §28.1 handelt
von einem anderen Thema (Trade-Attribution vs. gegatete Performance,
Phase A/B), nicht von Einzelpaar- vs. gepooltem Backtest. Der tatsächliche
Grund, warum `evidence/profile_full_window.py` überhaupt existiert, steht in
`evidence/strategy_status.py`: die Zulassung selbst braucht nur `observed_trades !=
0` aus dem Probelauf (`evidence/eligibility_admit_converged.py`, keine
Mindestanzahl — auch nicht 10, trotz anderslautender Erinnerung, geprüft
und im ganzen Repo nicht gefunden). Das volle 6,5-Jahres-Fenster ist nur
dann zwingend, wenn der Probelauf null Trades zeigte und eine Strategie
deswegen ausgeschlossen werden soll (`full_window_measurement_pending`,
nur für `reason == "no_trades_in_full_measurement"`) — sonst würde ein
zufällig ruhiger Probelauf-Monat eine tatsächlich handelnde Strategie zu
Unrecht verwerfen.

Stichprobe an diesem Datum: **0 von 608 `E1_expanded`-Strategien haben
`observed_trades == 0`.** Der Bedarf, der diese Stufe rechtfertigt, bestand
zu diesem Zeitpunkt für niemanden im zugelassenen Bestand — alle 571 den
Containern `full-window-a`/`full-window-b` zugeteilten Strategien hatten
bereits positive Probelauf-Evidenz und brauchten die Bestätigung nicht.
`regime/full_backtest.py` (gepoolt, ohnehin für dieselbe Kohorte laufend)
liefert für diese Mehrheit einen repräsentativeren Trade-Count obendrein
(gemeinsame `max_open_trades`-Kapitalbindung über alle Paare, nicht pro
Paar isoliert). Beide Container deshalb gestoppt (571/571 zugeteilt, davon
0 mit echtem Zero-Trade-Bedarf) — bei einer künftigen Kohortenerweiterung
lohnt sich vorher genau diese Prüfung (`observed_trades == 0` in
`STRATEGY_STATUS.csv`), bevor `evidence/profile_full_window.py` erneut für die
ganze Kohorte statt nur die Zero-Trade-Teilmenge gestartet wird.

## Stufe 9 — Marktregime-Klassifikation

| Programm | Liest | Schreibt |
|---|---|---|
| `regime/regime_engine.py` | lokale Kerzendateien | `results/regime/regime_daily.csv`, `regime_episodes.csv`, `regime_transitions.csv`, `regime_btc_episodes.csv`, `regime_state_summary.csv`, `regime_feature_distributions.csv`, `regime_manifest.json` |
| `regime/validate_regime.py` | dieselben `results/regime/regime_*.csv` | nichts (reine Prüfung, Konsolenausgabe PASS/FAIL) |
| `regime/report.py` | dieselben Dateien | `REGIME_DATA_REPORT.md` |

Erzeugt das eingefrorene 4-Zustands-Modell (BULL/BEAR/SIDEWAYS/TRANSITION aus
DMI(14)/ADX(14)) plus die Rohdaten, aus denen die Sechs-Phasen-Erweiterung
(`bull_trend`/`bear_trend`/`range_quiet`/`range_choppy`/`transition`/
`high_vol_shock`) in Stufe 9 abgeleitet wird.

## Stufe 10 — Attribution (pro Strategie/Kandidat, pro Regime/Phase)

| Programm | Liest | Schreibt |
|---|---|---|
| `regime/attribution.py` | `results/regime/regime_daily.csv`, `full_backtest_manifest.json`, `STRATEGY_STATUS.csv` (E1-Kohorte) | `results/regime/trade_regime_attribution.csv`, `strategy_btc_regime_summary.csv`, `strategy_regime_summary.csv`, `strategy_episode_summary.csv`, `strategy_phase_summary.csv`, `strategy_phase_episode_summary.csv`, `attribution_manifest.json` |
| `regime/gated_attribution.py` | `regime_daily.csv`, ein vollständiges `model1_backtest_manifest.json`, `model2_backtest_manifest.json` oder `model3_backtest_manifest.json`, aktuelle E1-Identitäten | je Modell in `results/regime/modelN_attribution/`: Trade-Attribution, fünf `candidate_*_summary.csv` und `attribution_manifest.json` |

Die beiden `*_phase_*`-Dateien (Sechs-Phasen-Modell, Nachtrag 2026-09-05)
existieren als Code bereits, wurden aber noch nicht produktiv durchlaufen —
sie brauchen `regime/full_backtest.py`s vollständige Ergebnisse (Stufe 7).
Ob dafür gerade ein Writer läuft, wird ausschließlich mit den Prüfungen in
`HANDOFF.md` festgestellt; diese Pipeline-Datei ist kein Laufstatus.
Die gegatete Attribution verweigert standardmäßig einen unvollständigen
Kandidatensatz; `--allow-partial` erzeugt nur einen ausdrücklich als partiell
markierten technischen Zwischenstand und ist keine Ranking-Freigabe.

## Stufe 11 — Hypothese (unabhängig, vor jeder Auswertung einzufrieren)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/market_phase_hypothesis.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/STRATEGY_CLASSIFICATION.json`, `cluster/clusters.json` | `evidence/MARKET_PHASE_HYPOTHESIS.json` |

Muss geschrieben sein, **bevor** irgendjemand die Ergebnisse aus Stufe 9
ansieht — sonst ist es keine Vorhersage mehr (`REGIME_AUDIT_PLAN.md` §28.3).
Bereits durchgelaufen; wird von `evidence/strategy_status.py` (Stufe 5) nur gelesen,
nie neu entschieden.

## Stufe 12 — Benchmark: Modell 0/1/2/3

Nach der am 2026-09-07 vor jedem produktiven Gate-Lauf eingefrorenen
Erweiterung, vier Vergleichsebenen pro Strategie:

- **Modell 0 — teilweise gemessen.** "Original strategy, no regime filter" ist
  genau das, was `regime/full_backtest.py` (Stufe 7) berechnet: der
  ungegatete, gepoolte Backtest über alle 8 Paare. Der resumierbare Aufruf
  `python -m regime.full_backtest` setzt diese Messung fort; laufende Writer
  werden vorher gemäß `HANDOFF.md` ausgeschlossen. Es ist keine gesonderte,
  noch zu bauende Stufe. **Korrektur gegenüber der Vorversion dieser Datei:** hier
  stand fälschlich "kein Skript existiert" für die gesamte Stufe 11 — das
  galt nur für Modell 1/2 und den Vergleich selbst, nicht für Modell 0.
- **Modell 1 — implementiert, noch nicht produktiv gelaufen.**
  `regime/gated_backtest.py --model model1` filtert Entries auf die im
  Kandidaten-Spec ausdrücklich genannten BTC-Zustände. Globale BTC-Zustände
  bleiben auch dann verfügbar, wenn für einen delisteten Coin keine lokale
  Tageszeile mehr existiert.
- **Modell 2 — implementiert, noch nicht produktiv gelaufen.**
  `regime/gated_backtest.py --model model2` filtert Entries ausschließlich auf
  die ausdrücklich genannten lokalen Coin-Zustände. Es liest und verlangt
  keinen BTC-Zustand. Fehlt der lokale Zustand, schließt das Gate.
- **Modell 3 — implementiert, noch nicht produktiv gelaufen.**
  `regime/gated_backtest.py --model model3` ist die bisherige kombinierte
  Modell-2-Logik: Entries brauchen sowohl einen erlaubten globalen BTC-Zustand
  als auch einen erlaubten lokalen Coin-Zustand. Exits bleiben in allen drei
  Gate-Modellen vollständig bei der Originalstrategie.
- **Der technische Vergleich der vier Ebenen ist implementiert, noch nicht
  produktiv gelaufen.** `regime/model_compare.py` prüft identische Kandidaten,
  Modell-3s Übereinstimmung mit Modell 1s BTC-Gate und Modell 2s Coin-Gate,
  Zeitfenster, Identitäten und Archive, bevor es die vier Laufmetriken
  nebeneinanderstellt. Es schreibt `model_metrics_long.csv`,
  `model_comparison.csv` und `model_comparison_manifest.json`, sortiert oder
  rangiert aber keine Strategie. Die mechanischen Deltas sind Modell 1 minus
  0, Modell 2 minus 0, Modell 3 minus 0, Modell 3 minus 1 und Modell 3 minus 2;
  Modell 2 minus Modell 1 wird nicht als inkrementeller Effekt ausgegeben,
  weil die beiden Einzel-Gates nicht ineinander verschachtelt sind.

Der Runner schreibt nach jedem Kandidaten atomar, sperrt einen Ausgabestore
gegen einen zweiten Writer und bindet jeden Lauf an Quell-/Config-Identität,
Regime-Datenhash, Gate-Regel, Kandidaten-Spec, Timerange und Analyse-Rolle.
Mehrere Gatevarianten derselben Strategie erhalten getrennte Archive.

Das Kandidaten-Spec wird nicht aus Performance-Ergebnissen erzeugt. Es hat
Schema-Version 1 und enthält:

```json
{
  "schema_version": 1,
  "candidate_set_id": "predeclared-id",
  "analysis_role": "PILOT",
  "timerange": {
    "spot": "YYYYMMDD-YYYYMMDD",
    "futures": "YYYYMMDD-YYYYMMDD"
  },
  "candidates": [{
    "candidate_id": "stable-candidate-id",
    "strategy_id": "canonical-strategy-id",
    "long_btc_states": ["BULL"],
    "short_btc_states": ["BEAR"],
    "long_coin_states": ["BULL"],
    "short_coin_states": ["BEAR"]
  }]
}
```

Die BTC-Felder sind für Modell 1 und 3 Pflicht, die Coin-Felder für Modell 2
und 3. Dasselbe eingefrorene Spec darf alle vier Felder tragen; jeder Runner
liest ausschließlich die für sein Modell relevanten Felder. Auch leere Listen
müssen explizit stehen; ein vergessenes Feld darf nie stillschweigend alle
Zustände erlauben. Die drei Aufrufe gegen dasselbe eingefrorene Spec sind:

```bash
python -m regime.gated_backtest --model model1 --candidate-spec <spec.json>
python -m regime.gated_backtest --model model2 --candidate-spec <spec.json>
python -m regime.gated_backtest --model model3 --candidate-spec <spec.json>
python -m regime.gated_attribution --model model1
python -m regime.gated_attribution --model model2
python -m regime.gated_attribution --model model3
python -m regime.model_compare
```

Die noch offene Auswertungsstufe ist nicht das mechanische Nebeneinanderstellen,
sondern die präregistrierte Bewertung: Exposure-Match, Spezialisten-Schwellen,
Discovery/Validation und Portfolioregel. Alle neun Preregistration-Fragen
(`REGIME_PREREGISTRATION.md`, Amendment 2026-09-11) sind seit 2026-09-11
entschieden — ein Kandidaten-Spec und ein produktiver Modell-1/2/3-Lauf sind
damit freigegeben. Portfolio-Allokation bei mehreren gleichzeitig
qualifizierenden Kandidaten ist dabei bewusst für Version 1 zurückgestellt,
nicht entschieden.

## Stufe 13 — Specialist-/Universal-Auswertung

| Programm | Liest | Schreibt |
|---|---|---|
| `regime/specialist_evaluation.py` | eine `trade_regime_attribution.csv` (Modell 0 kanonisch, oder eine `modelN_attribution/`-Datei), Kerzendaten unter `user_data/data/binance` | `results/regime/specialist_evaluation/`: `btc_specialist_table.csv`, `coin_specialist_table.csv`, `btc_specialist_ranking.csv`, `coin_specialist_ranking.csv`, `universal_strategies.csv`, `strategy_total_dollar_gain.csv`, `evaluation_manifest.json` |

Wendet die im Amendment 2026-09-11 eingefrorenen Regeln auf eine bereits
vorhandene Attribution an: Discovery/Validation-Split, die 5-Episoden-/
10-Trade-Specialist-Schwelle, und den Exposure-matched Benchmark (Coin-eigene
Spot-Buy&Hold-Rendite über genau das Handelsintervall jedes einzelnen
Trades, per `merge_asof` gegen 1-Minuten-Kerzen). Rankt ausschließlich
`VALIDATION`-Tier-Zeilen; alles andere wird berichtet, aber nie gerankt.

`max_drawdown` (§19 `worst_regime_drawdown`, 2026-09-12 auf expliziten
Nutzerwunsch nachgezogen): pro (Strategie, Regime) der schlimmste
Peak-to-Trough-Einbruch einer hypothetischen Kurve aus genau den in diesem
Regime gematchten Trades, nach `close_date` geordnet — `_regime_drawdown()`.
Dieselbe Fixed-$1000-je-Trade-Konvention wie die Dollar-Ansicht unten, aus
demselben Grund: eine kompoundierende Kurve über die Regime-Trades einer
Strategie reproduziert dieselbe Exponential-Verzerrung, die dort schon
verworfen wurde. Für jede Zeile berechnet (VALIDATION wie EXPLORATORY), nie
nur für die "schlimmste" Kombination — in der Universal-Kandidaten-Ansicht
kommt der Wert einfach aus der Zeile, die `worst_regime` ohnehin schon
referenziert.

**Korrektur 2026-09-13** (Nutzerfrage: "Warum max. Drawdown > 100%? Gehebelt?"):
die erste Implementierung normalisierte gegen den bisherigen Kurven-Höchststand
statt gegen das tatsächlich eingesetzte Kapital. Bei vielen Trades in einem
Regime bleibt der Höchststand klein, während sich viele gewöhnliche kleine
Verluste zu einem großen Betrag summieren — `CryptoFrogHO2` zeigte 685%
Drawdown in einem Regime, obwohl der schlechteste Einzeltrade nur −13% verlor
(kein Short, kein Hebel; geprüft: nur 4 von 589 Strategien haben überhaupt
einen Trade mit `profit_ratio < -1`). Behoben durch Normalisierung gegen das
kumulierte Kapital (`Trades-so-far × $1000`) statt gegen den Höchststand —
dadurch mathematisch nicht über 100% steigbar, solange kein Einzeltrade mehr
als 100% seines eigenen Einsatzes verliert (echte Hebelwirkung oder ein
Short-Verlust über den vollen Einsatz hinaus wäre genau das). Nach der
Korrektur liegt aktuell keine Zeile in Modell 0 oder dem 7er-Piloten über
100%; sollte das im vollen Modell-1/2/3-Lauf (in Arbeit) doch vorkommen, ist
es ein echtes Hebel-/Short-Signal und wird dann markiert.

**FreqForge-inspirierte Zusatzmetriken (2026-09-14, auf expliziten
Nutzerwunsch, nach Diskussion mit DeepSeek-v4-pro):** sechs weitere Spalten
je (Strategie, Regime) — `profit_factor`, `worst_trade`, `liquidation_rate`,
`sortino`, `cagr`, `drawdown_since_peak` —, plus die sechs zugehörigen
Punktwerte und ein gewichteter `freqforge_score` (0-100), nachgebildet nach
den sechs Kategorien von [github.com/baxr6/FreqForge](https://github.com/baxr6/FreqForge)
(Sortino 25%, Drawdown-Control 25%, CAGR 15%, Liquidation-Safety 15%,
Profit-Factor 10%, Worst-Trade-Severity 10%). Ausdrücklich nur eine weitere
Berichtsspalte, keine Ablösung der Tier-/Excess-Return-Rangfolge — §17
("Do not rely on a single composite score") bleibt für das eigentliche
Ranking in Kraft.

Zwei echte Fehler im ersten Entwurf, von DeepSeek-v4-pro vor der Umsetzung
gefunden (`mcp__deepseek-mcp__critique`, nicht nachträglich):
1. *CAGR* kompoundierte ursprünglich `mean_profit_ratio` (Durchschnitt pro
   Trade), was die Trade-Zahl komplett ignoriert — 10 Trades und 50 Trades
   zu je +2% über denselben Tage-Zeitraum hätten identisches CAGR ergeben,
   obwohl der tatsächliche Gewinn fünffach verschieden ist. Behoben: CAGR
   kompoundiert jetzt die tatsächliche Gesamtrendite der Gruppe
   (`dollar_gain_usd / START_CAPITAL`), nicht den Mittelwert.
2. Die Wiederverwendung von `_regime_drawdown()` für die Drawdown-Control-
   Kategorie war positionsabhängig verzerrt: derselbe −40%-Trade ergab als
   1. Trade der Gruppe 40% Drawdown, als 100. Trade nur ~0,4%, weil das
   bisher committete Kapital seit Gruppenbeginn akkumuliert statt seit dem
   letzten Hoch zurückgesetzt wird. Neue, separate Funktion
   `_regime_drawdown_since_peak()` behoben — normalisiert gegen das Kapital
   seit dem letzten Hoch, nicht seit Gruppenbeginn. `_regime_drawdown()`
   selbst (die bestehende `max_drawdown`-Spalte) bleibt unverändert, sie
   beantwortet weiterhin korrekt die andere, bereits ausgelieferte Frage
   (Hebel-Nachweis über die ganze Regime-Historie).

Eigener Fund beim Selftest (Perfect-Win-Rate-Fall): `profit_factor` bei
null Verlust-Trades ergab `-inf` statt `+inf`, weil `-leere_Summe.sum()`
`-0.0` statt `0.0` liefert und `x/-0.0 = -inf` (IEEE-754-Vorzeichen-Null-
Falle). Behoben mit `abs()` statt Negation; `+inf` wird jetzt wie von
FreqForge dokumentiert als Bestwert (100 Punkte) behandelt, nicht als
Fehlerfall.

Annualisierung von Sortino/CAGR läuft gegen `total_regime_days` — die Summe
der tatsächlichen Tage-Spannen der eigenen (deduplizierten) Episoden einer
Gruppe (`_regime_days()`, aus neuen `btc_episode_days`/`coin_episode_days`/
`joint_episode_days`-Spalten in `attach_benchmark()`), nicht die
Kalenderspanne zwischen erstem und letztem gematchten Trade — sonst zählten
Jahre außerhalb des Regimes zwischen verstreuten Episoden als Regime-Zeit
mit. CAGR kann bei kurzen Episoden extreme Werte annehmen (Maximum im
kompletten Modell-0-Bestand: 139 Mio. %) — bekannte, akzeptierte
Einschränkung, deshalb die Log-Skalierung beim Scoring. Modell 0 (589
Strategien) und der 7er-Pilot berechnet und im Artefakt verdrahtet
(Version 30); welches Kriterium die Top-10-Neuauswahl für Modell 1/2/3
nutzt, ist eine offene, separate Entscheidung.

**Episoden-Excess-LCB und Korrektur des Excess-Return-Mittelwerts
(2026-09-14, auf expliziten Nutzerwunsch nach DeepSeek-v4-pro-Rücksprache
"regime-audit-reliability-score"):** Nutzerziel war eine Kennzahl für
"schlägt Trading B&H, UND ist das statistisch verlässlich (viele
Episoden), nicht nur zufällig gut bei wenigen Trades" — Profit-Factor
allein wurde verworfen, weil er bei sehr wenigen Trades sehr hoch und bei
vielen Trades niedriger, aber verlässlicher ausfallen kann, ohne dass das
sichtbar wird. DeepSeek empfahl eine einseitige 95%-Lower-Confidence-Bound
auf den mittleren **episodischen** Excess-Return (`_episode_excess_lcb()`):
`LCB = Mittelwert(x_i) − t(0,95, n−1) × Standardfehler(x_i)`, `x_i` = die
Excess-Rendite der i-ten unabhängigen Episode, `n` = Episoden, nie Trades.
Wenige/stark schwankende Episoden drücken die Grenze automatisch ins
Negative — keine separate Mindest-Trade-Regel nötig, die Verlässlichkeit
steckt schon in der Formel. `lcb_grade` bildet daraus ein Gainium-artiges
A-F-Rating über feste, vor jeder Ergebnis-Sichtung eingefrorene Schwellen
(A: LCB>+2%, B: 0 bis +2%, C: −2% bis 0, D: −5% bis −2%, F: darunter).
Verworfene Alternativen: Bayes'sches Hierarchie-Shrinkage (eleganter bei
vielen Strategien, deutlich aufwändiger) und Wilson-Score auf ein binäres
"schlägt B&H ja/nein" (zu einfach, verwirft die Größe der Überrendite).
Beide neuen Spalten rein deskriptiv, kein Ersatz für Tier/Ranking oder den
`freqforge_score` — separat gehalten, damit die "kein Einzelscore"-Regel
(§17) nicht zweimal verletzt wird.

Bei der Umsetzung fiel ein echter, eigenständiger Fehler auf:
`excess_return` mittelte bislang über **Trades**, nicht über Episoden —
dieselbe Schieflage, die die Dollar-Korrektur oben schon einmal behoben
hat, nur als Mittelwert statt als Summe (eine Episode mit 50 Trades zählte
25-mal so stark wie eine mit 2 Trades, obwohl beide nur eine unabhängige
Beobachtung sind). Behoben in `_episode_pairs()`: jede Episode wird zuerst
für sich aufsummiert, dann erst über die Episoden gemittelt — symmetrisch
zum längst korrekten `mean_benchmark_return`. Das verschiebt Excess-Return
(und alles Abgeleitete — Ranking, Top-N-Auswahl, Universal-Kandidaten-
Zahlen) über den ganzen Bestand; alle konkreten Zahlen im Artefakt-Text
wurden neu hergeleitet (u. a. "ADX Uptrend schwächstes Regime" 372→359 von
379, vollständig konsistente Kandidaten 0→8). Modell 0 und der 7er-Pilot
neu gerechnet, Selftest um Regressionsfälle für beides ergänzt.

**ADX-Sideways-/Transition-Gate für Modell 1/2/3 (2026-09-14, auf
expliziten Nutzerwunsch, bewusste Abweichung vom eingefrorenen Plan — siehe
Addendum in `REGIME_AUDIT_PLAN.md` §15):** bisher gatete jeder Kandidat nur
Long auf BULL / Short auf BEAR (Trendfolge-Annahme). Neuer Kandidaten-Spec
`results/regime/candidate_spec_pilot_v1_sideways_transition.json` (14
Kandidaten: die 7 Piloten-Strategien je einmal mit `-sideways`- und einmal
mit `-transition`-Suffix, `candidate_set_id =
pilot_v1_stratified_sideways_transition_gate`, `analysis_role = PILOT`).
Anders als BULL/BEAR haben SIDEWAYS/TRANSITION keine Richtungsannahme, daher
symmetrisches Gate: `long_btc_states = short_btc_states = long_coin_states =
short_coin_states = ["SIDEWAYS"]` bzw. `["TRANSITION"]` — testet, ob ein
Gate auf reine Seitwärts-/Übergangsphasen hilft, unabhängig davon in welche
Richtung die Strategie dabei tatsächlich eintritt. Läuft durch dieselbe
unveränderte Kette (`gated_backtest.py` → `gated_attribution.py` →
`specialist_evaluation.py`); die neuen Kandidaten erscheinen als
zusätzliche Zeilen in denselben Modell-1/2/3-Tabellen (eigene candidate_id,
z. B. `ADXDM-sideways`), nicht als separate Tabelle. Backtest lief zum
Zeitpunkt dieses Eintrags noch (`--workers 1`, sequenziell über alle drei
Modelle wegen des 16-GB-Speicherwächters); Ergebniszahlen folgen nach
Abschluss.

Dollar-Ansicht (2026-09-11, auf expliziten Nutzerwunsch): zusätzlich zur
Benchmark-relativen Excess-Return-Prozentzahl ein Dollar-Betrag —
`dollar_gain_usd`/`benchmark_dollar_gain_usd`/`excess_dollar_gain_usd` in
den Regime-Tabellen, sowie regime-unabhängig je Strategie in
`strategy_total_dollar_gain.csv`. Erste Implementierung kompoundierte
sequenziell ($1000 Start, jeder Trade multipliziert den laufenden
Kontostand, sortiert nach `close_date`) — verworfen, weil das Ergebnis ab
einigen hundert Trades von der Exponentialrechnung dominiert wird statt von
der Strategiequalität (eine Pilotstrategie: $1000 → $0,006 über ~3.000
Trades) und weil es ein Konto mit genau einer offenen Position suggeriert,
das keine der Strategien je hatte (sie laufen auf bis zu 8 Paaren
gleichzeitig). Stattdessen: fixer $1000-Einsatz je Trade, keine
Wiederanlage, einfache Summe — robust, aber kein Aussage über
Kapitalwachstum bei echtem Reinvestment.

Erster produktiver Lauf (2026-09-11) auf den 7 Piloten-Kandidaten aus Stufe
12s Kandidaten-Spec, gegen deren Modell-0-Attribution (ihr natürliches,
ungegatetes Handelsverhalten): 5 von 7 Strategien erreichen mindestens eine
`VALIDATION`-Tier-Zeile, 5 erfüllen die Schwelle in allen vier
Coin-Regimen gleichzeitig (Universal-Kandidaten). `ASDTSRockwellTrading` hat
alle 13.402 Trades vor 2024-01-01 — keine einzige Validation-Zeile, korrekt
ausgeschlossen statt mit Discovery-Daten aufgefüllt. `ADXMomentum` hat genug
Episoden, aber zu wenige Trades je Regime (3-7, unter der 10er-Schwelle) —
`EXPLORATORY`, nicht gerankt.

Zweiter Lauf (2026-09-11), ohne `--strategies`-Filter: alle 589 Strategien,
die in `trade_regime_attribution.csv` überhaupt eine Modell-0-Attribution
haben (von 647 grundsätzlich eligiblen — 58 fehlen dort aus in
`attribution_manifest.json` protokollierten Gründen, z. B. Archiv-Hash- oder
Identity-Mismatch, nicht weil sie hier ausgeschlossen wurden). Laufzeit
36s (warmer Cache, vektorisiert). 3.459.380 Trades, 1.828 `VALIDATION`-Zeilen
BTC-Regime / 1.770 Coin-Regime, 379 Universal-Kandidaten (alle vier
Coin-Regime auf `VALIDATION`-Tier abgedeckt), davon 44 mit
`regime_consistency == 1.0` (schlagen den Benchmark in jedem der vier
Coin-Regime). 92 der 589 Strategien liefern keine einzige Zeile in beiden
Tabellen — kein Trade im Validation-Fenster, analog zum
`ASDTSRockwellTrading`-Fall aus dem Pilotlauf. Bei ~450-480 gerankten
Kandidaten je Regime-Spalte ist ein einzelner Rang-1-Platz nicht mehr
aussagekräftig für "beste Strategie" im Ganzen; die Auswertung soll pro
Regime gelesen werden, nicht als Gesamt-Leaderboard.

Dritter Lauf (2026-09-11), mit der Dollar-Ansicht: 497 von 589 Strategien
(die mit &ge;1 Validation-Fenster-Trade) bekommen eine Zeile in
`strategy_total_dollar_gain.csv`. 239/497 mit positivem `dollar_gain_usd`,
186/497 schlagen den Benchmark auch in Dollar (`excess_dollar_gain_usd`
&gt; 0). Median `dollar_gain_usd` liegt bei &minus;$81, Median
`excess_dollar_gain_usd` bei &minus;$297 — für diesen unkuratierten,
größtenteils von GitHub gezogenen Bestand kein überraschendes Bild. Größter
Gewinn: `FastSupertrend_optim_quick`, +$23.492 über 11.065 Trades. Größter
Verlust: `CryptoFrogHO2`, &minus;$20.280 über 15.692 Trades.

Vierter Lauf (2026-09-11), gegen die Modell-1/2/3-Kandidaten-Attribution
statt Modell 0s natürlichem Handelsverhalten (`--trades
results/regime/modelN_attribution/trade_regime_attribution.csv --outdir
results/regime/specialist_evaluation/modelN/`). Zwei Bugs dabei gefunden und
behoben: `load_trades()` erwartete hart eine Spalte `strategy_id`, aber
`gated_attribution.py`s Ausgabe nennt denselben Slot `candidate_id` — behoben
mit `_detect_id_column()`, erkennt automatisch, welche Spalte vorliegt, und
normalisiert intern auf `strategy_id` (protokolliert als
`source_id_column` im Manifest). `universal_table()` warf `KeyError:
'worst_regime_return'`, sobald eine nicht-leere `coin_table` null Zeilen
lieferte, die alle vier Coin-Regime abdecken — traf sofort bei Modell 2 und
3, wo das engere Gate zu wenige Trades je Regime übrig lässt, damit einer
der 7 Piloten-Kandidaten in allen vieren gleichzeitig die Schwelle
erreicht. Ergebnis: Modell 1 (BTC-Gate) 4/7 Universal-Kandidaten, keiner
vollständig konsistent; Modell 2 (Coin-Gate) und Modell 3 (Kombi-Gate) 0
Universal-Kandidaten. Gegatet-vs-ungegatet-Vergleich des Gesamtgewinns in
Dollar (6 Kandidaten mit Validierungs-Trades): jedes Gate verkleinert den
Verlust der drei Verlust-Strategien (`ADXDM`, `ADX_15M_USDT`,
`AlmgrenChrissStrategy`), am stärksten Modell 3; jedes Gate verkleinert
aber auch den Gewinn der einzigen ungegatet bereits profitablen Strategie
(`BBMod`) — das Gate filtert eben auch profitable Trades außerhalb der
Trendfolge-Regime heraus. `AdaptiveRegime` bleibt über alle vier Varianten
in etwa gleich. Deckte zusätzlich eine dritte `.gitignore`-Lücke auf
(`results/regime/specialist_evaluation/modelN/*.csv` liegt zwei statt eine
Ebene unter dem ersten Ausnahme-Pattern) — behoben mit
`!results/regime/*/*/*.csv`.

`attach_benchmark()`'s Benchmark-Definition geändert (2026-09-12, expliziter
Nutzerwunsch): statt Buy-and-Hold nur über das Open-Close-Intervall des
einzelnen Trades jetzt Buy-and-Hold über die *gesamte* ADX-Regime-Episode
(erster bis letzter klassifizierter Tag, aus `regime_daily.csv`s
`btc_episode_id`/`coin_episode_id`). Grund: die Trade-Intervall-Definition
konnte ein ungehebelter 1x-Long-Trade praktisch nie schlagen (seine eigene
Rendite *ist* näherungsweise die Intervall-Rendite, minus Gebühren) — sie
konnte also nie beantworten, ob eine Strategie eine Marktphase besser timt
als simples Halten. Zwei neue Spalten (`btc_episode_benchmark_return`,
`coin_episode_benchmark_return`) ersetzen die alte `benchmark_return` in
`_specialist_table()`; `benchmark_return` selbst bleibt unverändert und wird
weiterhin nur von `total_dollar_gain_table()`s regime-unabhängigem
Gesamtwert benutzt, der keine einzelne Marktphase hat, gegen die er messen
könnte. Alle drei Läufe (Modell 0 voll, Modell 1/2/3 gegen die
Piloten-Kandidaten) mit identischen Zeilen-/Episoden-/Trade-Zahlen wie zuvor
neu gerechnet — nur die Excess-Return-Werte selbst ändern sich, keine
Tier-/Floor-Zuordnung. Ergebnis bei Modell 0: von den 379 Universal-Kandidaten
schlägt jetzt **keiner** (vorher 44) den Benchmark noch in allen vier
Coin-Regimen gleichzeitig — 375 von 379 (99%) haben BULL als schwächstes
Regime, weil praktisch jede aktiv tradende Strategie einen Teil einer langen
Rally verpasst, den simples Durchhalten nicht verpasst. Das ist die direkte,
erwartete Antwort auf die Ausgangsfrage ("gibt es ungehebelte Long-Strategien,
die eine Bull-Phase besser timen als Buy-and-Hold") — mit dieser strengeren
Messlatte praktisch nein, im Rahmen dieses Bestands.

Bug in genau dieser Änderung gefunden und behoben (2026-09-12, vom Nutzer im
veröffentlichten Artefakt entdeckt): `_specialist_table()` summierte/mittelte
`benchmark_dollar_gain_usd`/`mean_benchmark_return` über jeden validierten
Trade statt über jede eindeutige Episode. Da `attach_benchmark()` allen
Trades einer Episode denselben Episoden-Benchmarkwert zuweist, zählte eine
Strategie mit vielen Trades in wenigen Episoden dieselbe Buy-and-Hold-Phase
mehrfach — Symptom im Artefakt: `Obelisk_TradePro_Ichi_v2_2` zeigte bei 1.230
Trades über nur 40 Episoden einen "B&H-Gewinn" von +$94.882 (real rund
$4.800, Faktor ~20 zu hoch). Fix: vor der Aggregation wird auf eindeutige
`(strategy_id, regime, coin_pair, episode_id)`-Kombinationen dedupliziert —
`coin_pair` ist Teil des Schlüssels, weil eine BTC-Regime-Episode ein
global geteiltes Kalenderfenster ist, in dem verschiedene Coins verschiedene
eigene Kursverläufe haben, also verschiedene Buy-and-Hold-Einsätze sind.
Betrifft sowohl die Dollar-Summe als auch den Prozent-Mittelwert (und damit
`excess_return`) gleichermaßen. Alle vier Läufe neu gerechnet — Zeilen-/
Episoden-/Trade-Zahlen unverändert (der Floor hängt nicht vom Benchmark ab),
Excess-Return- und Dollar-Werte teils deutlich verschoben; die "0 von 379
vollständig konsistent"-Kernaussage bleibt bestehen (BULL bleibt bei 372/379
das schwächste Regime, vorher 375/379 — die Größenordnung der Grundaussage
ändert sich nicht, nur einzelne Kandidatenwerte).

Modell 3 zeigte bislang zwei getrennte Tabellen (BTC-Regime, Coin-Regime),
obwohl das Gate beide Dimensionen gleichzeitig verlangt — auf Nutzerwunsch
zu einer kombinierten Tabelle zusammengeführt. Trades und Dollar-Gewinn
waren zwischen beiden Tabellen bereits identisch (dieselben Trades), aber
Episodenzahl und Excess-Return unterschieden sich, weil BTC-Episode und
Coin-Episode unterschiedliche Zeitfenster sind. Neue vierte Benchmark-Spalte
`joint_episode_benchmark_return` in `attach_benchmark()`: die echte
Schnittmenge aus BTC-Episode und Coin-Episode eines Trades (nicht eine der
beiden allein) — das ist die tatsächliche Bedingung, die Modell 3s
UND-Gate verlangt. Neue Funktion `joint_specialist_table()`, hinter
`--joint` (nur explizit angefordert, da sie nur für ein UND-gegatetes
Modell sinnvoll ist — auf Modell 0/1/2 angewandt ergäbe eine bedeutungslose
Tabelle). Beim Bau entdeckt: `btc_regime`/`coin_regime` stimmen bei
gegateten Trades fast immer überein, aber nicht ausnahmslos — 7 von rund
22.000 Modell-3-Trades weichen ab (Signal-Kerze und Fill-Kerze können je
einen Tag auseinanderliegen, in dem sich eine der beiden Regime-Dimensionen
unabhängig von der anderen weiterbewegt; keiner erreicht VALIDATION-Tier).
Kein Bug, also nicht als Fehler behandelt: `joint_specialist_table()` nimmt
`coin_regime` als alleinige Anzeige-Bezeichnung statt Übereinstimmung
vorauszusetzen. Modell 1/2 unverändert (nur eine Dimension gegatet, kein
kombiniertes Regime sinnvoll).

## Wo Docker statt nativem Python steht

Stufen 1–3 (Probelauf, beide Bias-Prüfungen) laufen sowohl nativ als auch in
den gepinnten Docker-Images (`strategy-audit-runtime:2026.7` und Varianten),
je nachdem welcher Runner sie aufruft — beide schreiben in dieselben
JSON-Stores, unterschieden nur durch das Feld `runtime_id`
(`native_unversioned` vs. `docker:sha256:...`). Stufe 7 (Vollfenster,
gepoolt) läuft ausschließlich in Docker, weil sie stundenlang unbeaufsichtigt
läuft.

## Alte Dateien, die nicht mehr gebraucht werden

Drei verschiedene Kategorien, nicht eine — wichtig, weil sie unterschiedlich
behandelt werden.

### 1. Vom ursprünglichen Autor der Vorgänger-Arbeit (895/900-Strategien-Sichtung, vor dieser Prüfkette)

Publikations-Vorspann und Fallstudien einer früheren, weniger strengen
Sichtung. Keine Datei hier wird von einem Skript aus Stufe 0–11 gelesen oder
geschrieben; sie beschreiben einen Stand, den `STRATEGY_STATUS.csv` längst
ersetzt hat.

| Datei/Verzeichnis | Erzeugt von | Ersetzt durch |
|---|---|---|
| `old/predecessor_audit/README.md`, `LEDGER.csv`, `LEDGER.md` | archiviertes `ledger.py` | `STRATEGY_STATUS.md` |
| `old/predecessor_audit/CORPUS.md`, `CORPUS_PLAN.md`, `corpus/INDEX.md` + 896 Karten unter `corpus/` | archiviertes Vorgänger-Tooling | `evidence/EXECUTION_PROFILES.csv`, `evidence/corpus_sources.json` |
| `old/predecessor_audit/ANALYSIS.md`, `ANALYSIS.ru.md` | (Vorgänger-Tooling) | fünf handverlesene Fallstudien, keine Population — `STRATEGY_STATUS.csv` deckt die aktuelle Population |
| `old/predecessor_audit/results/*.md` (`DoubleEMACrossoverWithTrend.md` u.a., `INDEX.md`) | (Vorgänger-Tooling) | dieselben fünf Fallstudien — **nicht zu verwechseln mit `results/regime/`**, das ist aktuell und wird von Stufe 7–9 beschrieben |
| `old/predecessor_audit/DCA.md`, `DEPTH.md`, `RESOLVABLE.md` | (Vorgänger-Tooling) | eigenständige Seitenuntersuchungen ohne Regime-Bezug, nichts ersetzt sie, weil nichts in der aktuellen Kette dieselbe Frage stellt |
| `old/**` (`corpus_repair`, `eligibility_zwischenstand_2026-08`, `hmm_prototype_2026-08`, `proxy_backtests_2026-08`, `root_prototypes_2026-08`, `translation_attempts_2026-08`, `vorueberlegungen`, eigenes `old/README.md`) | verschiedene, alle vor dieser Kette | bewusst archiviert, nicht gelöscht |
| `.codex/CONTINUATION.md` | (Vorgänger-Tooling) | erklärt sich selbst durch `HANDOFF.md` ersetzt |

### 2. Eigene Dateien dieser Prüfkette, aber verwaist (kein Erzeugerskript mehr vorhanden)

Anders als Kategorie 1: **unsere** Dateien, nicht die des ursprünglichen
Autors — aber das Skript, das sie einmal schrieb, existiert nicht mehr im
Repo. `ELIGIBILITY_NEVER_RUN.json` und `ELIGIBILITY_TRAP_SMOKE.json` waren
die letzten beiden dieser Art und sind am 2026-09-06 entfernt worden (siehe
Stufe 1) — aktuell keine Kandidaten in dieser Kategorie. Ein künftiger Fund
würde genauso behandelt: erst per Diff bestätigen, dass keine Zeile mehr
darauf angewiesen ist, dann committen, dann entfernen — nie umgekehrt.

### 3. `tools/` — eigene Werkzeuge, aber manuell, nicht Teil der automatischen Kette

Alle Dateien hier sind aktuell und nicht veraltet. Die meisten laufen auf
Zuruf; Stufe 0 nutzt zusätzlich die Corpus-Werkzeuge in diesem Verzeichnis.
Sie wurden aus dem Root hierher verschoben und ihre Root-Pfadannahmen angepasst.
Die veralteten Vorgänger-Gates `sync_repo.py`, `freeze_guard.py`,
`verify_ledger.py` und `totality.py` liegen dagegen unter
`old/predecessor_audit/` und sind nicht mehr Teil der aktuellen CI. `totality.py`
meldet auf der heutigen Pipeline 124 ungeprüfte Heuristiktreffer und eignet sich
damit nicht als unveränderter Commit-Guard.
`ROOT`-Pfadannahmen (`os.path.dirname(os.path.abspath(__file__))`) wurden um
eine Ebene korrigiert; `warmup_reparse.py`s `from evidence import profile_bias` bekam einen
`sys.path.insert` auf das Root-Verzeichnis, denselben Kniff, den `repair/*.py`
schon vorher benutzte.

| Programm | Zweck | Wann laufen lassen |
|---|---|---|
| `tools/secret_gate.py` | Verhindert, dass ein Commit ein Secret enthält (vier Schichten, siehe eigener Docstring) | vor jedem Commit, das neue Dateien einführt |
| `tools/translation_repair.py` | Übersetzt russische Kommentare/Strings in Python-Dateien, AST-geprüft, übersetzt fehlgeschlagene Stellen nie stillschweigend | wenn `tools/harvest.py` (Stufe 0) ein Repo mit nicht-englischen Kommentaren einbringt |
| `tools/blocked_triage.py` | Findet behebbare Ursachen für Zeilen, die der Probelauf nie erreicht (freqtrade startete sie gar nicht); schreibt `REPAIR_LIST.md` und `evidence/BLOCKED_TRIAGE.json`, das Stufe 5 liest | nach neuem Harvest oder wenn sich die Zahl blockierter Zeilen ändert (`--probe --list`) |
| `tools/eligibility_expansion.py` | Friert das historische, ergebnisblinde Eligibility-Expansion-Inventar ein (nur technische Stage-6-Artefakte, keine Performance) | wenn `REGIME_PREREGISTRATION.md`/`ELIGIBILITY_EXPANSION_PLAN.md` geändert werden |
| `tools/probe_double_advise.py` | Prüft, ob der doppelte `ft_advise_signals`-Aufruf in `lookahead-analysis` eine Spalte dupliziert | bei Verdacht, der `enter_tag`-Shim verfälsche das Ergebnis |
| `tools/probe_shim_neutral.py` | Vergleicht Backtest-Ergebnisse mit/ohne `enter_tag`-Shim auf Neutralität | nach einer Änderung am Shim-Mechanismus |
| `tools/probe_zero.py` | Unterscheidet bei einer Zeile ohne Trades, ob die Entry-Bedingung nie wahr wird oder der Indikator fehlt | wenn eine Zeile 0 Trades zeigt und die Ursache unklar ist |
| `tools/strategy_classification.py` | Klassifiziert Typ/Timeframe je Zeile aus `evidence/EXECUTION_PROFILES.csv` und dem Strategie-Quellcode; schreibt `evidence/STRATEGY_CLASSIFICATION.json`, das Stufe 5 und Stufe 10 lesen. `strategy_type` ist immer explizit: erkannte Familie, `unclassified` oder für Test-/Template-Artefakte `not_applicable`. Reihenfolge: Klassifikation vor Phasenhypothese, Status und HTML-Seite. | nach neuem Harvest, wenn sich `evidence/EXECUTION_PROFILES.csv` ändert oder Klassifikationsregeln geändert wurden |
| `tools/strategy_status_page.py` | Baut die veröffentlichte Seite aus `STRATEGY_STATUS.csv`, damit Seite und Tabelle nie auseinanderlaufen | nach jedem `evidence/strategy_status.py`-Lauf, vor Veröffentlichung |
| `tools/warmup_reparse.py` | Liest gespeicherte Leiter-Logs mit dem aktuellen Parser erneut, ohne freqtrade neu laufen zu lassen | nach einer Korrektur am Drift-Tabellen-Parser |

`repair/FREQAI_RESULTS.md`, `repair/REGISTER.md`, `repair/TRANSLATION_AUDIT.md`
sind ebenfalls eigene, aktuelle Dateien, aber Provenienz-Protokolle, keine
Werkzeuge — nur relevant, wenn eine konkrete reparierte Implementierung zur
Debatte steht (siehe `DOCUMENT_MAP.md`).
