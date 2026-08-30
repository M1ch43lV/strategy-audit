# Zwischenstand zur technischen Strategienutzbarkeit

**Stand:** 2026-08-30

**Repository-Stand:** `c5f1ec1` (`Record Stage 9 decision stop`)

**Auswertungseinheit:** kanonisches `strategy_id x run_profile`
**Zeitfenster der kanonischen Messung:** 2020-03-01 bis 2026-08-21

Dieser Zwischenstand dokumentiert den technischen Stage-6-Status vor jeder
Stage-9-Rangbildung. Er bewertet die Zulassung zum Regime-Audit, nicht die
Profitabilitaet und nicht die Eignung fuer den Live-Handel.

## Kernergebnis

Die Eligibility-Tabelle enthaelt 900 kanonische Strategie-/Profilzeilen. Der
aeltere oeffentliche Ledger enthaelt 895 Strategieklassen; die Differenz sind
fuenf zusaetzliche provisorische Profile.

| Status | Anzahl | Anteil | Bedeutung |
|---|---:|---:|---|
| `eligible` | 67 | 7,4 % | Alle technischen Einschlusskriterien erfuellt |
| `ineligible` | 826 | 91,8 % | Mindestens ein harter Ausschlussgrund |
| `pending_diagnostics` | 7 | 0,8 % | Mindestens eine erforderliche Diagnose blieb ergebnislos |
| **Gesamt** | **900** | **100,0 %** | |

Daneben sind drei verschiedene Bedeutungen von `funktioniert` zu
unterscheiden:

- 622 von 900 Profilen wurden kanonisch gemessen.
- 608 von 900 erzeugten in der kanonischen Messung mindestens einen Trade.
- 67 von 900 sind vollstaendig auditfaehig.

Alle 67 auditfaehigen Profile schlossen den gepoolten Stage-7-Lauf ueber alle
acht Handelspaare ab. Dabei entstanden 286.616 Trades. Diese Tradezahl ersetzt
nicht die Anzahl unabhaengiger Strategien; Trades einer Strategie und verwandte
Strategiefamilien sind nicht als unabhaengige Beobachtungen zu behandeln.

## Strenge Einschlussregel

Ein Profil ist nur dann `eligible`, wenn alle folgenden Bedingungen erfuellt
sind:

1. Die kanonische Implementierung wurde im nativen Spot- oder Futures-Modus
   gemessen.
2. Eine Vollmessung erzeugte Trades.
3. Lookahead- und Recursive-Bias-Diagnostik endeten mit `PASS`.
4. Die exakte Pair-/Candle-Abdeckung im eingefrorenen Regimefenster bestand.
5. Es wurde keine publizierte technische Backtest-Falle gefunden.
6. Eine Reparatur ist nicht als `behavior_changed` klassifiziert.
7. `output_equivalent`-Overlays besitzen kanonische Bias-Wiederholungen.

Profit, Signifikanz, Buy-and-Hold-Vergleich, Strategieklasse und Cluster sind
bewusst keine technischen Einschlusskriterien.

## Harte Ausschlussgruende

Die Gruende sind nicht exklusiv. Eine Strategie kann mehrere Gruende zugleich
haben; deshalb ist ihre Summe groesser als 826.

| Ausschlussgrund | Anzahl | Konkretes Problem |
|---|---:|---|
| `recursive_bias_found` | 545 | Indikatoren oder Signale sind gegenueber der verfuegbaren Historien- bzw. Startup-Laenge nicht stabil. |
| `canonical_implementation_not_measured` | 278 | Kein vertrauenswuerdiger kanonischer Lauf im vorgesehenen nativen Ausfuehrungsmodus. |
| `lookahead_found` | 56 | Historische Berechnungen oder Signale verwenden implizit Informationen aus spaeteren Kerzen. |
| `technical_trap_found` | 42 | Exit-/ROI-Konfiguration kann Backtest-Ausfuehrungen erzeugen, die live mechanisch nicht vergleichbar sind. |
| `no_trades_in_full_measurement` | 6 | Die Vollmessung lief, erzeugte aber keinen Trade. |
| `behavior_changed_primary_exclusion` | 1 | Die notwendige Reparatur veraenderte erreichbares Handelsverhalten. |

### Exakte Kombinationen der 826 ausgeschlossenen Profile

Diese Kombinationen sind gegenseitig exklusiv und summieren sich zu 826:

| Kombination harter Gruende | Anzahl |
|---|---:|
| nur Recursive Bias | 448 |
| nur kanonische Implementierung nicht gemessen | 230 |
| nicht gemessen und Recursive Bias | 43 |
| Lookahead und Recursive Bias | 35 |
| nur technische Falle | 23 |
| nur Lookahead | 19 |
| Recursive Bias und technische Falle | 17 |
| nur keine Trades in der Vollmessung | 6 |
| nicht gemessen, Lookahead und Recursive Bias | 2 |
| nicht gemessen und technische Falle | 2 |
| nicht gemessen und verhaltensveraendernde Reparatur | 1 |

## Details der Ausschlussgruende

### Recursive Bias: 545

| Unterart | Anzahl | Bedeutung |
|---|---:|---|
| `drift_measured` | 321 | Bei veraenderter Historienlaenge wurden abweichende Indikator- oder Signalwerte gemessen. |
| `refused_no_warmup` | 134 | Die Analyse konnte ohne ausreichenden deklarierten Warm-up keine stabile Rekursion pruefen und wertete dies nach der eingefrorenen Regel als Fund. |
| ohne feinere Unterart | 90 | Recursive Bias wurde gefunden, im historischen Befund aber nicht genauer typisiert. |

Ein Backtest kann in allen drei Gruppen technisch laufen. Sein historisches
Signal ist dennoch nicht hinreichend reproduzierbar fuer die strenge
zeitkausale Auswertung.

### Kanonische Implementierung nicht gemessen: 278

- 261 Profile wurden im Runtime-Smoke nicht ausgefuehrt.
- 17 Profile scheiterten im Runtime-Smoke.
- 260 betreffen `spot_long`, 14 `futures_long_short`, drei `futures_long` und
  eines besitzt ein ungeloestes Profil.

Dies bedeutet nicht automatisch defekten Quellcode. Es fehlt ein
vertrauenswuerdiger, nativer und identitaetsgebundener Messlauf; ohne ihn sind
auch nachfolgende Bias- und Regimeaussagen nicht belastbar.

### Lookahead Bias: 56

Lookahead liegt vor, wenn historische Werte oder Entscheidungen von
Informationen abhaengen, die zum Entscheidungszeitpunkt noch nicht verfuegbar
waren. Typische Mechanismen sind Zugriffe auf spaetere Zeilen, nicht kausale
Vollfenster-Berechnungen, spaeter bestaetigte Extremwerte oder Normalisierungen
ueber den gesamten DataFrame.

Die Evidenzquellen verteilen sich auf 33 historische Spot-Diagnosen, 16
kanonisch-native Diagnosen und sieben separate historische Spot-Befunde, die
nicht auf einen anderen Ausfuehrungsmodus uebertragen wurden.

### Technische Backtest-Fallen: 42

| Falle | Anzahl | Problem |
|---|---:|---|
| Trailing-Stop enger als Spread/Handelskosten | 38 | Der Backtest kann innerhalb des Spreads fuellen; live ist diese Ausfuehrung nicht realistisch erreichbar. |
| Enges ROI-Ziel auf langem Timeframe | 4 | Der Backtest kennt die Kerzenspanne, nicht den Intrabar-Pfad, und kann ein unrealistisch guenstiges Erreichen des Ziels annehmen. |

### Keine Trades in der Vollmessung: 6

- `DoubleEMACrossoverWithTrend`
- `EMAPriceCrossoverWithThreshold`
- `MACDCrossoverWithTrend`
- `RSIDirectionalWithTrend`
- `RSIDirectionalWithTrendSlow`
- `Insomnia_short`

Weitere acht Profile hatten im kurzen Smoke-Test ebenfalls null Trades, waren
aber bereits durch Recursive Bias, Lookahead oder eine technische Falle hart
ausgeschlossen. Insgesamt hatten damit 14 der 622 kanonisch gemessenen Profile
keine beobachteten Trades; nur bei sechs war die Vollmessung ohne Trades der
primaere Ausschlussgrund.

### Verhaltensveraendernde Reparatur: 1

`AstroQAV4` benoetigte eine Reparatur, die erreichbares Handelsverhalten
veraenderte. Diese Variante darf sichtbar und separat analysiert werden, kann
aber keine Verhaltensgleichheit mit der publizierten Originalstrategie
beanspruchen.

## Sieben Profile mit offener Diagnostik

| Strategie | Profil | kanonische Trades | Offenes Problem |
|---|---|---:|---|
| `HyperStra_GSN_SMAOnly` | `spot_long` | 17 | Vollstaendiger Lookahead-Lauf endete mit Prozesscode `-9`; Recursive-Test bestand. |
| `Fakebuy` | `spot_long` | 339 | Lookahead-Analyse ueberschritt das Zeitlimit von 900 Sekunden; Recursive-Test bestand. |
| `TGMA` | `spot_long` | 8.673 | `trailing_stop_positive_offset` ist nicht groesser als `trailing_stop_positive`; eine Korrektur veraendert Exit-Verhalten. |
| `haGradient` | `futures_long` | 38 | FFT benoetigt 120 Datenpunkte; Analyzer-Teilmengen enthielten nur 102 bzw. 31. |
| `kalthetank` | `spot_long` | 172 | FFT benoetigt 282 Datenpunkte; Analyzer-Teilmengen enthielten nur 93 bzw. 211. |
| `InverseVolatilityPortfolio` | `spot_long` | 24 | Lookahead-Vergleichsmenge enthielt 0 von mindestens 10 erforderlichen Trades. |
| `RiskParityPortfolio` | `spot_long` | 23 | Lookahead-Vergleichsmenge enthielt 0 von mindestens 10 erforderlichen Trades. |

`pending_diagnostics` ist weder ein PASS noch ein FAIL. Keine dieser sieben
Strategien wird ohne neue belastbare Evidenz in den strengen Korpus aufgenommen.

## Sekundaere offene Evidenz

Diese Gruende sind ebenfalls nicht exklusiv und werden ueber alle 900 Zeilen
gezaehlt. Viele betroffene Zeilen sind bereits aus einem anderen Grund hart
ausgeschlossen.

| Offene Evidenz | Anzahl |
|---|---:|
| Artefaktrolle muss geprueft werden | 14 |
| Exakte Regimefenster-Abdeckung nicht verifiziert | 36 |
| Ausfuehrungsprofil ungeloest | 1 |
| Futures-Bias-Diagnostik nicht abgeschlossen | 51 |
| Lookahead-Diagnostik nicht abgeschlossen | 495 |
| Nativer Modus nicht zur Laufzeit validiert | 278 |
| Kanonische Bias-Wiederholung fuer `output_equivalent` fehlt | 4 |
| Recursive-Diagnostik nicht abgeschlossen | 182 |
| Null Trades im Smoke erfordern Vollfensterlauf | 8 |

Von den 36 offenen Coverage-Zeilen wartet keine ansonsten vollstaendig
qualifizierte Strategie ausschliesslich auf Coverage. Eine Lockerung der
Coverage-Regel wuerde deshalb aktuell keine weitere Strategie in den strengen
Korpus bringen.

## Massgebliche Artefakte

- `REGIME_ELIGIBILITY.csv`: maschinenlesbare Zeilen und Gruende
- `REGIME_ELIGIBILITY.md`: eingefrorene Stage-6-Regel und Zusammenfassung
- `PROFILE_BIAS.json`: kanonische Bias-Diagnosen und konkrete Fehlertexte
- `REGIME_COVERAGE.csv`: Pair-/Candle-Abdeckung
- `EXECUTION_PROFILES.csv`: kanonische Implementierung und nativer Laufmodus
- `TRAPS.md`: Definition und Haeufigkeit der technischen Backtest-Fallen
- `results/regime/full_backtest_manifest.json`: abgeschlossene Stage-7-Messung
