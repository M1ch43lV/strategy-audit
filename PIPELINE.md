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
| `harvest.py` | GitHub-API (nur `.py`-Dateien mit `IStrategy`) | Dateien unter `repos/<repo>/` |
| `census_repos.py` | `evidence/corpus_sources.json`, `repos/**` | Statistiken zu Kopie-Familien (Konsole/Referenz für `exclusion_criteria.py`s C-Text) |
| `evidence/new_repo_candidates.py` | GitHub-Themensuche, `evidence/corpus_sources.json` | `evidence/NEW_REPO_CANDIDATES.json`, `evidence/NEW_REPO_CANDIDATES.md` |
| `evidence/repo_freshness.py` | lokales `git log` je Repo, GitHub-Tip, `evidence/EXECUTION_PROFILES.csv` | `evidence/REPO_FRESHNESS.csv`, `evidence/REPO_FRESHNESS.md` |

Ergebnis dieser Stufe: neue Zeilen in `evidence/EXECUTION_PROFILES.csv` (eine Zeile pro
Strategie-Implementierung, die kanonische Quelle für den ganzen Rest der
Kette).

## Stufe 1 — Probelauf (lädt die Strategie, prüft ob überhaupt gehandelt wird)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/profile_smoke.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/PROFILE_CLASS1.json` (Reparatur-Regeln) | `evidence/PROFILE_SMOKE.json` |

**2026-09-06, erledigt:** `ELIGIBILITY_NEVER_RUN.json` und
`ELIGIBILITY_TRAP_SMOKE.json` waren einmalige Fallback-Stores früherer
Wellen (kein Runner im aktuellen Repo schrieb sie neu) — 65 der 83 Zeilen
darin hatten keinen eigenen `evidence/PROFILE_SMOKE.json`-Eintrag, `strategy_status.py`
fiel für sie auf diese beiden Dateien zurück. Per gezieltem
`evidence/profile_smoke.py --strategy ... --profiles spot_long futures_long unknown`
nachgeholt (empirisch geprüft: vorher änderten sich 65 von 83 Zeilen in
`STRATEGY_STATUS.csv`, wenn man die Dateien wegließ, danach keine einzige
mehr) und beide Dateien entfernt, inklusive der Fallback-Schleife in
`strategy_status.py`.

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

## Stufe 2 — Bias-Ausschlussprüfung: Recursive-Bias zuerst

| Programm | Liest | Schreibt |
|---|---|---|
| `warmup_convergence.py` | `evidence/EXECUTION_PROFILES.csv`, `STRATEGY_STATUS.csv` (für die Kohorten-Auswahl), Reparatur-Stores | `evidence/WARMUP_CONVERGENCE.json` |

Leiter aus `REGIME_PREREGISTRATION.md`s eingefrorener Konvergenz-Regel: 1, 2,
7, 14, 30, 90, 365 Tage, umgerechnet in Kerzen über den eigenen Zeitrahmen der
Strategie. Eine Zeile ist `converged`, `not_converged_within_ladder` oder
`inconclusive` (technisches Hindernis, kein Befund).

## Stufe 3 — Bias-Ausschlussprüfung: Look-Ahead-Bias

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/profile_bias.py` (`run_diagnostic`, native oder Docker) | `evidence/EXECUTION_PROFILES.csv`, Reparatur-Stores | `evidence/PROFILE_BIAS.json` |
| `evidence/eligibility_lookahead_backfill.py` | `STRATEGY_STATUS.csv`, `evidence/EXECUTION_PROFILES.csv`, `evidence/WARMUP_CONVERGENCE.json`, `evidence/PROFILE_CLASS1.json`, für Zeilen ohne native Messung aus der ursprünglichen Sichtung | `evidence/ELIGIBILITY_LOOKAHEAD_BACKFILL.json` |
| `evidence/profile_bias_merge.py` | disjunkte Shard-Dateien (bei parallelen Läufen) | die kanonische `evidence/PROFILE_BIAS.json` |

`evidence/LOOKAHEAD_INDICATOR_REVIEW.json` ist kein Skript-Ausgang, sondern eine von
Hand geprüfte, an `canonical_sha256` gebundene Ausnahmeliste: Zeilen, bei
denen freqtrades `lookahead-analysis` nur eine Zwischenspalte markiert (0
verfälschte Entries/Exits), nachweislich weil die Spalte nie unverändert in
die Signal-Logik einfließt. `strategy_status.py` liest sie mit derselben
Präzedenz wie eine native Messung.

## Stufe 4 — Datenabdeckung (Coverage)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/regime_coverage.py` | `evidence/EXECUTION_PROFILES.csv`, Kerzendateien unter `user_data/data/binance` | `evidence/REGIME_COVERAGE.csv`, `evidence/REGIME_COVERAGE.md` |

Reine Dateisystem-Prüfung (keine Freqtrade-Ausführung), pro `(mode,
timeframe)` gecacht — günstig, jederzeit sicher neu zu erzeugen. Deckt seit
2026-09-06 alle 919 Zeilen ab (vorher 900, siehe unten).

## Stufe 5 — Zusammenführung

| Programm | Liest | Schreibt |
|---|---|---|
| `strategy_status.py` | **alles** aus Stufe 0–4 plus `evidence/REGIME_ELIGIBILITY.csv` (invalidierter historischer E0-Snapshot, ausschließlich Provenienz), `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` (aktive E1-Entscheidungen), `evidence/STRATEGY_CLASSIFICATION.json`, `evidence/MARKET_PHASE_HYPOTHESIS.json`, `evidence/BLOCKED_TRIAGE.json` | `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, **im selben Lauf automatisch**: `evidence/exclusion_criteria_list.md`, `evidence/repair_measures_list.md`, `RUNTIME_ENVIRONMENTS.md` |

Ein einziger Aufruf (`python strategy_status.py`) schreibt alle fünf Dateien.
`--check` prüft nur, ob sie noch aktuell sind (schreibt nichts); `--selftest`
läuft die eingebauten Konsistenz-Prüfungen.

E0 ist keine Rückfalloption: seine 67 alten `regime_eligible=true`-Flags dürfen
keinen Check ersetzen und keine Zeile zulassen. Nur eine aktive
`admitted_E1`-Entscheidung erzeugt `cohort=E1_expanded`; die alte E0-
Mitgliedschaft erscheint lediglich in `gate_notes`.

## Stufe 6 — Zulassung (Admission)

| Programm | Liest | Schreibt |
|---|---|---|
| `evidence/eligibility_admit_converged.py` (aktuelle Regel, `converged_clean_gates_v1`) | `STRATEGY_STATUS.csv`, `evidence/WARMUP_CONVERGENCE.json` | hängt neue `admitted_E1`-Zeilen an `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` an |
| `evidence/eligibility_expansion_adjudicate.py` (ältere Wave-B/C-Regeln, `zero_warmup_analyzer_adapter_v1` / `native_gate_pass_v1`) | `evidence/ELIGIBILITY_EXPANSION_PROOFS.json`, `evidence/ELIGIBILITY_EXPANSION_WARMUP.json`, `evidence/ELIGIBILITY_EXPANSION_LOOKAHEAD.json`, `evidence/ELIGIBILITY_EXPANSION_EQUIVALENCE.json` | dieselbe `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, plus `.md`-Bericht |

**Danach zwingend zurück zu Stufe 5.** Die Zulassungs-Entscheidung steht erst
in `STRATEGY_STATUS.csv`, wenn `strategy_status.py` erneut läuft und die
erweiterte `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` zurückliest. Ein Lauf
von Stufe 6 ohne anschließende Stufe 5 zeigt in `STRATEGY_STATUS.csv` noch
den alten Stand.

## Stufe 7 — Backtest über das volle Fenster

Zwei strukturell verschiedene, beide nötige Messungen (siehe
`REGIME_AUDIT_PLAN.md` §28.1) — keine ersetzt die andere:

| Programm | Zweck | Liest | Schreibt |
|---|---|---|---|
| `evidence/profile_full_window.py` (paarweise sharded) | Stage-6-Bestätigung: handelt die Strategie über das ganze Fenster, pro Paar | `evidence/EXECUTION_PROFILES.csv` | `evidence/PROFILE_FULL_WINDOW.json` (oder Shard-Dateien bei parallelen Containern) |
| `merge_full_window_shards.py` | führt Shards zusammen | `evidence/PROFILE_FULL_WINDOW_shardA.json`, `_shardB.json`, `_shardTF.json` | die kanonische `evidence/PROFILE_FULL_WINDOW.json` |
| `regime/full_backtest.py` (gepoolt, `canonical_pooled_native_pair_universe`) | Phase A: tatsächlicher Performance-Backtest über alle 8 Paare gepoolt | `STRATEGY_STATUS.csv` (E1-Kohorte) | `results/regime/full_backtest_manifest.json`, `full_backtest_native.json` |

`evidence/PROFILE_FULL_WINDOW.json` fließt zurück in Stufe 5 (`strategy_status.py`
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
`strategy_status.py`: die Zulassung selbst braucht nur `observed_trades !=
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

## Stufe 8 — Marktregime-Klassifikation

| Programm | Liest | Schreibt |
|---|---|---|
| `regime/regime_engine.py` | lokale Kerzendateien | `results/regime/regime_daily.csv`, `regime_episodes.csv`, `regime_transitions.csv`, `regime_btc_episodes.csv`, `regime_state_summary.csv`, `regime_feature_distributions.csv`, `regime_manifest.json` |
| `regime/validate_regime.py` | dieselben `results/regime/regime_*.csv` | nichts (reine Prüfung, Konsolenausgabe PASS/FAIL) |
| `regime/report.py` | dieselben Dateien | `REGIME_DATA_REPORT.md` |

Erzeugt das eingefrorene 4-Zustands-Modell (BULL/BEAR/SIDEWAYS/TRANSITION aus
DMI(14)/ADX(14)) plus die Rohdaten, aus denen die Sechs-Phasen-Erweiterung
(`bull_trend`/`bear_trend`/`range_quiet`/`range_choppy`/`transition`/
`high_vol_shock`) in Stufe 9 abgeleitet wird.

## Stufe 9 — Attribution (pro Strategie/Kandidat, pro Regime/Phase)

| Programm | Liest | Schreibt |
|---|---|---|
| `regime/attribution.py` | `results/regime/regime_daily.csv`, `full_backtest_manifest.json`, `STRATEGY_STATUS.csv` (E1-Kohorte) | `results/regime/trade_regime_attribution.csv`, `strategy_btc_regime_summary.csv`, `strategy_regime_summary.csv`, `strategy_episode_summary.csv`, `strategy_phase_summary.csv`, `strategy_phase_episode_summary.csv`, `attribution_manifest.json` |
| `regime/gated_attribution.py` | `regime_daily.csv`, ein vollständiges `model1_backtest_manifest.json`, `model2_backtest_manifest.json` oder `model3_backtest_manifest.json`, aktuelle E1-Identitäten | je Modell in `results/regime/modelN_attribution/`: Trade-Attribution, fünf `candidate_*_summary.csv` und `attribution_manifest.json` |

Die beiden `*_phase_*`-Dateien (Sechs-Phasen-Modell, Nachtrag 2026-09-05)
existieren als Code bereits, wurden aber noch nicht produktiv durchlaufen —
sie brauchen `regime/full_backtest.py`s vollständige Ergebnisse (Stufe 7),
die derzeit noch in den drei laufenden Hintergrund-Containern entstehen.
Die gegatete Attribution verweigert standardmäßig einen unvollständigen
Kandidatensatz; `--allow-partial` erzeugt nur einen ausdrücklich als partiell
markierten technischen Zwischenstand und ist keine Ranking-Freigabe.

## Stufe 10 — Hypothese (unabhängig, vor jeder Auswertung einzufrieren)

| Programm | Liest | Schreibt |
|---|---|---|
| `market_phase_hypothesis.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/STRATEGY_CLASSIFICATION.json`, `cluster/clusters.json` | `evidence/MARKET_PHASE_HYPOTHESIS.json` |

Muss geschrieben sein, **bevor** irgendjemand die Ergebnisse aus Stufe 9
ansieht — sonst ist es keine Vorhersage mehr (`REGIME_AUDIT_PLAN.md` §28.3).
Bereits durchgelaufen; wird von `strategy_status.py` (Stufe 5) nur gelesen,
nie neu entschieden.

## Stufe 11 — Benchmark: Modell 0/1/2/3

Nach der am 2026-09-07 vor jedem produktiven Gate-Lauf eingefrorenen
Erweiterung, vier Vergleichsebenen pro Strategie:

- **Modell 0 — läuft bereits.** "Original strategy, no regime filter" ist
  genau das, was `regime/full_backtest.py` (Stufe 7) berechnet: der
  ungegatete, gepoolte Backtest über alle 8 Paare. Der aktuell laufende
  Container `full-backtest-pooled` (`python -m regime.full_backtest --workers
  2 --timeout 3600 --force`) ist Modell 0 in Arbeit, keine gesonderte, noch
  zu bauende Stufe. **Korrektur gegenüber der Vorversion dieser Datei:** hier
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
Discovery/Validation und Portfolioregel. Acht offene Preregistration-Fragen
(siehe `DOCUMENT_MAP.md`) verhindern weiterhin eine Rangfolge und vor allem
das Erzeugen eines ergebnisgetriebenen Kandidaten-Specs.

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
| `README.md`, `LEDGER.csv`, `LEDGER.md` | `ledger.py` (eigener Generator, unabhängig von `strategy_status.py`) | `STRATEGY_STATUS.md` |
| `CORPUS.md`, `CORPUS_PLAN.md`, `corpus/INDEX.md` + 896 Karten unter `corpus/` | (Vorgänger-Tooling, nicht Teil dieser Kette) | `evidence/EXECUTION_PROFILES.csv`, `evidence/corpus_sources.json` |
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

Alle Dateien hier sind aktuell und nicht veraltet, laufen aber nur auf Zuruf,
nie automatisch von Stufe 0–11 aus aufgerufen. **2026-09-08 aus dem Root
hierher verschoben** (acht Dateien, siehe Begründung unten): jede wurde vorher
geprüft — keine ist von einem anderen Root-Skript importiert, keine hat einen
eigenen `_docker.ps1`-Wrapper, keine steht in `sync_repo.py`s `PIPELINE`-Liste.
`ROOT`-Pfadannahmen (`os.path.dirname(os.path.abspath(__file__))`) wurden um
eine Ebene korrigiert; `warmup_reparse.py`s `from evidence import profile_bias` bekam einen
`sys.path.insert` auf das Root-Verzeichnis, denselben Kniff, den `repair/*.py`
schon vorher benutzte.

| Programm | Zweck | Wann laufen lassen |
|---|---|---|
| `tools/secret_gate.py` | Verhindert, dass ein Commit ein Secret enthält (vier Schichten, siehe eigener Docstring) | vor jedem Commit, das neue Dateien einführt |
| `tools/translation_repair.py` | Übersetzt russische Kommentare/Strings in Python-Dateien, AST-geprüft, übersetzt fehlgeschlagene Stellen nie stillschweigend | wenn `harvest.py` (Stufe 0) ein Repo mit nicht-englischen Kommentaren einbringt |
| `tools/blocked_triage.py` | Findet behebbare Ursachen für Zeilen, die der Probelauf nie erreicht (freqtrade startete sie gar nicht); schreibt `REPAIR_LIST.md` und `evidence/BLOCKED_TRIAGE.json`, das Stufe 5 liest | nach neuem Harvest oder wenn sich die Zahl blockierter Zeilen ändert (`--probe --list`) |
| `tools/eligibility_expansion.py` | Friert das historische, ergebnisblinde Eligibility-Expansion-Inventar ein (nur technische Stage-6-Artefakte, keine Performance) | wenn `REGIME_PREREGISTRATION.md`/`ELIGIBILITY_EXPANSION_PLAN.md` geändert werden |
| `tools/probe_double_advise.py` | Prüft, ob der doppelte `ft_advise_signals`-Aufruf in `lookahead-analysis` eine Spalte dupliziert | bei Verdacht, der `enter_tag`-Shim verfälsche das Ergebnis |
| `tools/probe_shim_neutral.py` | Vergleicht Backtest-Ergebnisse mit/ohne `enter_tag`-Shim auf Neutralität | nach einer Änderung am Shim-Mechanismus |
| `tools/probe_zero.py` | Unterscheidet bei einer Zeile ohne Trades, ob die Entry-Bedingung nie wahr wird oder der Indikator fehlt | wenn eine Zeile 0 Trades zeigt und die Ursache unklar ist |
| `tools/strategy_classification.py` | Klassifiziert Typ/Timeframe je Zeile aus `evidence/EXECUTION_PROFILES.csv` und dem Strategie-Quellcode; schreibt `evidence/STRATEGY_CLASSIFICATION.json`, das Stufe 5 und Stufe 10 lesen. `strategy_type` ist immer explizit: erkannte Familie, `unclassified` oder für Test-/Template-Artefakte `not_applicable`. Reihenfolge: Klassifikation vor Phasenhypothese, Status und HTML-Seite. | nach neuem Harvest, wenn sich `evidence/EXECUTION_PROFILES.csv` ändert oder Klassifikationsregeln geändert wurden |
| `tools/strategy_status_page.py` | Baut die veröffentlichte Seite aus `STRATEGY_STATUS.csv`, damit Seite und Tabelle nie auseinanderlaufen | nach jedem `strategy_status.py`-Lauf, vor Veröffentlichung |
| `tools/warmup_reparse.py` | Liest gespeicherte Leiter-Logs mit dem aktuellen Parser erneut, ohne freqtrade neu laufen zu lassen | nach einer Korrektur am Drift-Tabellen-Parser |

`repair/FREQAI_RESULTS.md`, `repair/REGISTER.md`, `repair/TRANSLATION_AUDIT.md`
sind ebenfalls eigene, aktuelle Dateien, aber Provenienz-Protokolle, keine
Werkzeuge — nur relevant, wenn eine konkrete reparierte Implementierung zur
Debatte steht (siehe `DOCUMENT_MAP.md`).
