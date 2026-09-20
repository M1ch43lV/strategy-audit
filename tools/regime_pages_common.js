// Asterisk-marks a futures-mode strategy wherever its name is displayed -
// added 2026-09-13 per explicit user request, after a max-drawdown question
// showed most >100% figures were a bug, not leverage, but futures/margin
// trading is a real, separate reason a strategy's own losses can exceed its
// nominal stake. FUTURES is exactly EXECUTION_PROFILES.csv's run_profile
// starting "futures_" (long/short/long_short) - the same spot/futures split
// profile_smoke.run_one() already uses, not a leverage-amount estimate.
var FUTURES = new Set(FUTURESSTRATEGIES);
// DCA marker (2026-09-14, explicit user request): position_adjustment_enable
// == True AND adjust_trade_position actually implemented, checked directly
// against each strategy's own source file - stricter than STRATEGY_STATUS.csv's
// strategy_type=grid_dca marker (a bare regex on "position_adjustment_enable"/
// "dca"/"grid" as substrings, no True-check, no behavior check; that broader
// marker hits 121 strategies, this verified set 108).
var DCA = new Set(DCASTRATEGIES);
// Modell 1/2/3 rows carry a candidate_id (e.g. "FastSupertrend_optim3_rsi_80-trend"), not
// the bare strategy_id FUTURESSTRATEGIES is keyed on - an exact-match
// lookup silently never marked a single gated row (found 2026-09-14 while
// updating this section for the new -sideways/-transition candidates).
// Strip a known gate-variant suffix before the FUTURES check; a bare
// strategy_id (every Modell-0 table) has none of these suffixes and passes
// through unchanged.
var CANDIDATE_SUFFIXES = ['-trend', '-sideways', '-transition', '-uptrend', '-downtrend'];
function baseStrategyId(id){
  for (var i = 0; i < CANDIDATE_SUFFIXES.length; i++){
    if (id.endsWith(CANDIDATE_SUFFIXES[i])) return id.slice(0, id.length - CANDIDATE_SUFFIXES[i].length);
  }
  return id;
}
function futuresLabel(strategyId){
  var base = baseStrategyId(strategyId);
  return strategyId + (FUTURES.has(base) ? ' *' : '') + (DCA.has(base) ? ' #' : '');
}

// Display names only (renamed 2026-09-12 per user request) - the underlying
// codes (BULL/BEAR/SIDEWAYS/TRANSITION) stay as-is everywhere they are data
// (CSS classes, chip data-value, Set membership, JSON fields), so nothing
// downstream of the CSV pipeline needs to change to show the new names.
var STATE_LABEL = {BULL: 'ADX Uptrend', BEAR: 'ADX Downtrend',
                   SIDEWAYS: 'ADX Sideways', TRANSITION: 'ADX Transition'};
function stateLabel(code){ return STATE_LABEL[code] || code; }

function fmtPct(v){
  const p = (v*100);
  const s = p.toFixed(2) + '%';
  return (p >= 0 ? '+' : String.fromCharCode(8722)) + s.replace('-','');
}
function valClass(v){
  if (v >= 0) return 'pos';
  if (v >= -0.005) return 'neg-1';
  if (v >= -0.02) return 'neg-2';
  return 'neg-3';
}
function fmtUsd(v){
  const s = Math.round(Math.abs(v)).toLocaleString('de-DE');
  return (v >= 0 ? '+$' : String.fromCharCode(8722) + '$') + s;
}
function dollarClass(v){
  if (v >= 0) return 'pos';
  if (v >= -1000) return 'neg-1';
  if (v >= -5000) return 'neg-2';
  return 'neg-3';
}
function fmtDrawdown(v){
  if (v === null || v === undefined) return '&mdash;';
  return Math.round(v * 100) + '%';
}
function fmtProfitFactor(v){
  if (v === null || v === undefined) return '&mdash;';
  if (v === Infinity) return '&#8734;';
  return v.toFixed(2);
}
function scoreClass(v){
  if (v === null || v === undefined) return '';
  if (v >= 65) return 'pos';
  if (v >= 45) return 'neg-1';
  if (v >= 25) return 'neg-2';
  return 'neg-3';
}
function fmtBigNumber(abs){
  // Sortino/Rendite p.a. can still reach large values at very high trade
  // frequency (extreme annualization, not a bug - see the callout above the
  // table) - compact suffixes keep the column readable instead of a
  // ten-digit decimal.
  if (abs >= 1e9) return (abs / 1e9).toFixed(1) + 'Mrd';
  if (abs >= 1e6) return (abs / 1e6).toFixed(1) + 'Mio';
  if (abs >= 1e3) return (abs / 1e3).toFixed(1) + 'Tsd';
  return abs.toFixed(2);
}
function fmtSortino(v){
  if (v === null || v === undefined) return '&mdash;';
  // freqtrade's own "-100.0" broken-Sortino sentinel (no losing trades at
  // all) - FreqForge scores this best-in-class, not worst, so it is shown
  // as such rather than as a literal -100.00.
  if (v <= -99.99) return 'kein Verlust';
  return (v >= 0 ? '+' : String.fromCharCode(8722)) + fmtBigNumber(Math.abs(v));
}
function fmtAnnualizedReturn(v){
  if (v === null || v === undefined) return '&mdash;';
  const p = v * 100;
  return (p >= 0 ? '+' : String.fromCharCode(8722)) + fmtBigNumber(Math.abs(p)) + '%';
}
function fmtScore(v){
  if (v === null || v === undefined) return '&mdash;';
  return Math.round(v);
}
function fmtLcb(v){
  // null below n=2 episodes - a sample std needs at least two points, and
  // the VALIDATION floor already requires 5, so this only ever shows up
  // for EXPLORATORY rows with 0-1 episodes.
  if (v === null || v === undefined) return '&mdash;';
  return (v >= 0 ? '+' : String.fromCharCode(8722)) + Math.abs(v * 100).toFixed(1) + '%';
}
function gradeClass(g){
  if (g === 'A' || g === 'B') return 'pos';
  if (g === 'D') return 'neg-2';
  if (g === 'F') return 'neg-3';
  return '';
}
// A best .. F worst, missing/null sorts as worse than F - so the same
// descending-by-default convention used for every other column (highest
// value = best, shown first) also puts the best grade first for Grade.
function gradeScore(g){
  var order = {A: 4, B: 3, C: 2, D: 1, F: 0};
  return order.hasOwnProperty(g) ? order[g] : -1;
}
function signClass(v){ return v >= 0 ? 'pos' : 'neg-3'; }
function fmtRatio(v){ return (v >= 0 ? '+' : String.fromCharCode(8722)) + Math.abs(v).toFixed(2); }
function fmtCagr(v){
  const p = v * 100;
  return (p >= 0 ? '+' : String.fromCharCode(8722)) + Math.abs(p).toFixed(1) + '%';
}

/* Stage 8b annotation. `ok` is set only when the strategy passed the 5m detail
   rerun (measured, or by the owner rule at or below 5m) AND the cost screen in
   the claimed ADX state. It changes no ranking; it is a column. */
function fmtConf(v){
  if (v === null || v === undefined) return '–';
  return (v >= 0 ? '+' : '−') + Math.abs(100 * v).toFixed(1).replace('.', ',') + ' %';
}
/* Confirmation across the discovery and the validation window (regime/discovery_comparison.py).
   cf: 2 confirmed, 1 floor in both windows but not confirmed, 0 no discovery floor.
   sc: the smaller of the two lower confidence bounds, the weakest link. */
function confirmCell(r){
  if (r.cf === 2) {
    return '<td class="num"><span class="rbadge rb-ok" title="Floor in beiden Fenstern, und die untere Vertrauensgrenze des Excess-Returns liegt in der Discovery und in der Validation über 0.">bestätigt</span><span class="confscore" title="Score: die kleinere der beiden unteren Vertrauensgrenzen">' + fmtConf(r.sc) + '</span></td>';
  }
  if (r.cf === 1) {
    return '<td class="num"><span class="rbadge rb-warn" title="Floor in beiden Fenstern, aber mindestens eine untere Vertrauensgrenze liegt nicht über 0.">nicht bestätigt</span><span class="confscore" title="Score: die kleinere der beiden unteren Vertrauensgrenzen">' + fmtConf(r.sc) + '</span></td>';
  }
  return '<td class="num"><span class="rbadge rb-no" title="Die Strategie erreicht in dieser Phase in der Discovery den Floor nicht (weniger als 5 Episoden oder 10 Trades).">–</span></td>';
}
/* Universal candidates: 2 strict (confirmed in all four coin phases), 1 mild (better than
   Buy-and-Hold in both windows in at least three of the four phases), 0 neither. */
function uconfirmCell(r){
  var cls = r.ur === 2 ? 'rb-ok' : (r.ur === 1 ? 'rb-warn' : 'rb-no');
  var text = r.ur === 2 ? 'streng bestätigt' : (r.ur === 1 ? 'mild bestätigt' : 'nicht bestätigt');
  var title = r.ur === 2 ? 'In allen vier Coin-Phasen bestätigt.' :
    (r.ur === 1 ? 'Nicht in allen vier Phasen bestätigt, aber in ' + r.up + ' von 4 Phasen in beiden Fenstern besser als Buy-and-Hold (mildere Regel).' :
    'In weniger als drei Phasen in beiden Fenstern besser als Buy-and-Hold.');
  return '<td class="num"><span class="rbadge ' + cls + '" title="' + title + '">' + text + '</span><span class="confscore" title="Score der schwächsten Phase: die kleinere der beiden unteren Vertrauensgrenzen">' + fmtConf(r.us) + '</span></td>';
}
function robustCell(r){
  if (r.ok) {
    return '<td class="num"><span class="rbadge rb-ok" title="5m-Detaillauf bestanden und Kostenstress (0,1 % Slippage je Seite) in diesem ADX-Zustand bestanden">PASS</span></td>';
  }
  var text, cls = 'rb-no', title;
  if (r.xs === 'SENSITIVE') { text = 'sensitiv'; cls = 'rb-warn'; title = 'Das Ergebnis ändert sich unter 5m-Detailkerzen wesentlich (Vorzeichen, mehr als 50 % Gewinnänderung oder mehr als 10 % andere Trades).'; }
  else if (r.xs === 'PENDING') { text = '5m offen'; title = 'Timeframe über 5m; der 5m-Detaillauf steht noch aus.'; }
  else if (r.xs === 'ERROR') { text = 'Fehler'; title = 'Der 5m-Detaillauf oder sein Vergleich ist fehlgeschlagen.'; }
  else if (r.xs === 'PASS') { text = 'Kosten ✗'; cls = 'rb-warn'; title = 'Ausführung bestanden, aber der Gewinn in diesem Zustand übersteht 0,1 % zusätzlichen Slippage je Seite nicht oder hat zu wenige Trades.'; }
  else { text = '–'; title = 'Kein Robustheitsergebnis für diese Strategie.'; }
  return '<td class="num"><span class="rbadge ' + cls + '" title="' + title + '">' + text + '</span></td>';
}
document.querySelectorAll('.tabs').forEach(function(tabsEl){
  var tabs = Array.from(tabsEl.querySelectorAll('.tab'));
  var targets = tabs.map(function(t){ return t.getAttribute('data-target'); });
  tabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      tabs.forEach(function(t){ t.classList.remove('active'); });
      tab.classList.add('active');
      var target = tab.getAttribute('data-target');
      targets.forEach(function(id){
        var panel = document.getElementById(id);
        if (panel) panel.style.display = (id === target) ? '' : 'none';
      });
    });
  });
});
// Table zoom - shrinks/grows every table.plain via the shared --tzoom CSS
// var, added 2026-09-14 per explicit user request so wide tables (Regime-
// Spezialisten, Universal-Kandidaten, gated Modell 1/2/3) can be zoomed
// down to fit the viewport instead of relying on the .tablebox horizontal
// scrollbar. One control for the whole page since every such table shares
// the same variable. Per-viewer convenience only - wrapped in try/catch,
// silently no-ops if storage is blocked (private window, etc.).
(function(){
  var STEPS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25];
  var idx = STEPS.indexOf(1.0);
  try {
    var saved = parseFloat(localStorage.getItem('regime-tzoom'));
    var savedIdx = STEPS.indexOf(saved);
    if (savedIdx !== -1) idx = savedIdx;
  } catch (e) {}
  var label = document.getElementById('zoom-label');
  function apply(){
    var z = STEPS[idx];
    document.documentElement.style.setProperty('--tzoom', z);
    label.textContent = Math.round(z * 100) + '%';
    try { localStorage.setItem('regime-tzoom', String(z)); } catch (e) {}
  }
  document.getElementById('zoom-out').addEventListener('click', function(){
    idx = Math.max(0, idx - 1); apply();
  });
  document.getElementById('zoom-in').addEventListener('click', function(){
    idx = Math.min(STEPS.length - 1, idx + 1); apply();
  });
  apply();
})();

/* ------------------------------------------------------------------ shared by both pages
   Sorting, header tooltips and the search/sort wiring. The page defines its data first. */

/* Stage 8b + confirmation cell for a strategy that is not tied to one phase (whole-window
   tables). ur: 2 strict, 1 mild, 0 universal but not confirmed, -1 not a universal candidate.
   cn/bn: number of coin/BTC phases in which the strategy is confirmed. */
function stratConfirmCell(r){
  var partial = (r.cn || 0) + (r.bn || 0) > 0;
  var scoreText = partial ? '<span class="confscore" title="In wie vielen der vier Coin- und der vier BTC-Marktphasen die Strategie bestätigt ist.">Coin ' + (r.cn || 0) + '/4 · BTC ' + (r.bn || 0) + '/4</span>' : '';
  var badge;
  if (r.ur === 2) badge = '<span class="rbadge rb-ok" title="Universal-Kandidat, in allen vier Coin-Phasen in Discovery und Validation bestätigt.">streng bestätigt</span>';
  else if (r.ur === 1) badge = '<span class="rbadge rb-warn" title="Universal-Kandidat, in mindestens drei der vier Coin-Phasen in beiden Fenstern besser als Buy-and-Hold (mildere Regel).">mild bestätigt</span>';
  else if (partial) badge = '<span class="rbadge rb-warn" title="Nicht als Universal-Kandidat bestätigt, aber in einzelnen Marktphasen bestätigt.">teilweise</span>';
  else if (r.ur === 0) badge = '<span class="rbadge rb-no" title="Universal-Kandidat, aber weder streng noch mild bestätigt.">nicht bestätigt</span>';
  else badge = '<span class="rbadge rb-no" title="In keiner Marktphase in beiden Fenstern bestätigt.">–</span>';
  return '<td class="num" data-v="' + (r.cq || 0) + '">' + badge + scoreText + '</td>';
}
/* The same, inline, for the winner cards (one phase). */
function confInline(r){
  if (r.cf === 2) return '<span class="rbadge rb-ok" title="Floor in beiden Fenstern, untere Vertrauensgrenze in Discovery und Validation über 0. Score: die schwächere der beiden Grenzen.">bestätigt ' + fmtConf(r.sc) + '</span>';
  if (r.cf === 1) return '<span class="rbadge rb-warn" title="Floor in beiden Fenstern, aber mindestens eine untere Vertrauensgrenze liegt nicht über 0.">nicht bestätigt</span>';
  return '<span class="rbadge rb-no" title="In der Discovery unter dem Floor in dieser Phase.">–</span>';
}

/* ---- sorting for tables that have no sorter of their own (a click on any header) ---- */
function parseNumberText(text){
  var t = String(text).replace(/−/g, '-').trim();
  if (/^kein Verlust/.test(t) || t.charAt(0) === '∞') return Infinity;
  var m = t.match(/^([-+]?)\$?\s?(\d[\d.,]*)(Tsd|Mio|Mrd)?/);
  if (!m) return null;
  var s = m[2];
  if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) s = s.replace(/\./g, '');
  s = s.replace(',', '.');
  var v = parseFloat(s);
  if (isNaN(v)) return null;
  var mult = {Tsd: 1e3, Mio: 1e6, Mrd: 1e9}[m[3]] || 1;
  return (m[1] === '-' ? -1 : 1) * v * mult;
}
function cellSortValue(td){
  var d = td.getAttribute('data-v');
  if (d !== null) { var n = Number(d); return (d !== '' && !isNaN(n)) ? n : d; }
  var text = td.textContent.trim();
  var num = parseNumberText(text);
  return num === null ? text : num;
}
function markArrows(headers, active, dir){
  headers.forEach(function(t){
    t.classList.remove('active');
    var a = t.querySelector('.arrow'); if (a) a.innerHTML = '&#9662;';
  });
  active.classList.add('active');
  var arrow = active.querySelector('.arrow'); if (arrow) arrow.innerHTML = dir > 0 ? '&#9652;' : '&#9662;';
}
function enableSort(table){
  if (table.getAttribute('data-gsort') || table.hasAttribute('data-nosort')) return;
  var head = table.querySelector('thead tr:last-child');
  if (!head) return;
  var ths = Array.prototype.slice.call(head.children);
  if (ths.some(function(th){ return th.classList.contains('sortable'); })) return;
  table.setAttribute('data-gsort', '1');
  var state = {col: -1, dir: 1};
  ths.forEach(function(th, i){
    th.classList.add('sortable');
    th.insertAdjacentHTML('beforeend', '<span class="arrow">&#9662;</span>');
    th.addEventListener('click', function(){
      var body = table.tBodies[0];
      if (!body) return;
      var rows = Array.prototype.slice.call(body.rows);
      var vals = rows.map(function(r){ return r.cells[i] ? cellSortValue(r.cells[i]) : null; });
      var present = vals.filter(function(v){ return v !== null && v !== ''; });
      var numeric = present.length > 0 && present.filter(function(v){ return typeof v === 'number'; }).length >= 0.6 * present.length;
      state.dir = state.col !== i ? (numeric ? -1 : 1) : -state.dir;
      state.col = i;
      var dir = state.dir;
      var order = rows.map(function(r, k){ return {r: r, v: vals[k], k: k}; });
      function missing(v){ return v === null || v === '' || (numeric && typeof v !== 'number'); }
      order.sort(function(a, b){
        var ma = missing(a.v), mb = missing(b.v);
        if (ma || mb) return ma && mb ? a.k - b.k : (ma ? 1 : -1);
        var c = numeric ? (a.v === b.v ? 0 : (a.v < b.v ? -1 : 1)) : String(a.v).localeCompare(String(b.v), 'de');
        return c === 0 ? a.k - b.k : c * dir;
      });
      order.forEach(function(o){ body.appendChild(o.r); });
      markArrows(ths, th, dir);
    });
  });
}

/* ---- header tooltips: what a term means, for every table header that has no title yet ---- */
var TERMS = {
  'strategie': 'Name der FreqTrade-Strategie. * = Futures-Strategie, # = DCA-Strategie (siehe Legende).',
  'kandidat': 'Gate-Kandidat: eine Strategie mit Entry-Gate auf einen ADX-Zustand. Der Suffix nennt den Zustand: -uptrend, -downtrend, -sideways, -transition, -trend (long im Uptrend, short im Downtrend).',
  'zustand': 'ADX-Marktphase: Uptrend, Downtrend, Sideways oder Transition. Definition im Abschnitt „ADX-Regime“.',
  'regime': 'Art der Marktphase: BTC (der Zustand von BTC) oder Coin (der Zustand des gehandelten Coins).',
  'phase': 'ADX-Marktphase: Uptrend, Downtrend, Sideways oder Transition.',
  'schwächstes regime': 'Die Coin-Phase mit dem schlechtesten Excess-Return dieser Strategie. Bei einem Universal-Kandidaten ist sie die Schwachstelle der Rundum-Aussage.',
  'trades': 'Anzahl der Trades, die im betrachteten Fenster eröffnet wurden.',
  'episoden': 'Zusammenhängende Abschnitte einer Marktphase (zum Beispiel ein Aufwärtstrend über sieben Wochen). Jede Episode zählt als eine unabhängige Beobachtung; der Floor verlangt mindestens 5.',
  'excess-return': 'Rendite der Strategie in den Episoden dieser Phase minus Buy-and-Hold über dieselben Episoden. Über 0 heißt: besser als Halten.',
  'dollar-gewinn': 'Summe der Gewinne aller Trades bei festem 1.000-$-Einsatz je Trade, ohne Wiederanlage.',
  'b&h-gewinn': 'Derselbe Betrag für Buy-and-Hold des jeweiligen Coins über die ganzen Episoden.',
  'excess im schwächsten': 'Excess-Return in der Coin-Phase, in der diese Strategie am schwächsten ist.',
  'median excess': 'Median der Excess-Returns dieser Strategie über ihre vier Coin-Phasen.',
  'modell 0 (ungegatet)': 'Ergebnis der Strategie ohne Gate: ihr natürliches Handelsverhalten, in Dollar bei festem 1.000-$-Einsatz je Trade (Trades in Klammern).',
  'modell 1 (btc-regime gate)': 'Dieselbe Strategie mit Entry-Gate nach der BTC-Marktphase.',
  'modell 2 (coin-regime gate)': 'Dieselbe Strategie mit Entry-Gate nach der Marktphase des gehandelten Coins.',
  'modell 3 (kombi-gate)': 'Dieselbe Strategie mit Entry-Gate nach BTC-Phase und Coin-Phase zugleich (UND-Verknüpfung).',
  'btc-regime': 'Marktphase von BTC, die für alle Paare am selben Tag gilt.',
  'coin-regime': 'Marktphase des gehandelten Coins selbst.',
  'kombiniertes regime (btc ∧ coin)': 'Nur Trades, bei denen BTC-Phase und Coin-Phase zugleich den erlaubten Zustand haben.',
  'median excess-return': 'Median der Excess-Returns dieser Strategie über ihre Phasen, in denen sie den Floor erreicht.',
  'max drawdown': 'Größter Einbruch der Gewinnkurve bei festem 1.000-$-Einsatz, in Prozent des bis dahin eingesetzten Kapitals.',
  'worst trade': 'Der schlechteste einzelne Trade in dieser Phase, in Prozent seines Einsatzes.',
  'sortino': 'Ertrag geteilt durch die Streuung der Verlust-Trades, aufs Jahr hochgerechnet. „kein Verlust“ heißt: es gab keinen Verlust-Trade.',
  'rendite p.a.': 'Mittlere Trade-Rendite mal Trades pro Jahr. Linear hochgerechnet, ohne Zinseszins.',
  'profit-factor': 'Bruttogewinn geteilt durch Bruttoverlust. Über 1 heißt: mehr Gewinn als Verlust. ∞ heißt: kein Verlust-Trade.',
  'freqforge-score': 'Punktwert von 0 bis 100 aus sechs Kategorien nach FreqForge (Sortino, Drawdown, Rendite, Liquidation, Profit-Factor, Worst Trade). Nur eine Zusatzspalte, kein Ranking-Kriterium.',
  'episoden-excess-lcb': 'LCB (Lower Confidence Bound): untere 95-%-Vertrauensgrenze des mittleren Excess-Returns je Episode. Über 0 heißt: der Vorsprung ist statistisch belastbar.',
  'grade': 'Note A bis F aus dem LCB: A über +2 %, B 0 bis +2 %, C −2 bis 0 %, D −5 bis −2 %, F darunter.',
  'robustheit': 'Stufe 8b. PASS: der 5m-Detaillauf ist bestanden (bis 5m per Regel) und der Gewinn übersteht 0,1 % zusätzlichen Slippage je Seite.',
  'bestätigung': 'Bestätigt heißt: Floor in Discovery und Validation, und die untere Vertrauensgrenze liegt in beiden über 0. Der Wert daneben ist der Score, die schwächere der beiden Grenzen.',
  'konsistenz': 'Anteil der vier Coin-Phasen, in denen die Strategie Buy-and-Hold schlägt.',
  'gesamtgewinn': 'Summe der Gewinne aller Validation-Trades bei festem 1.000-$-Einsatz je Trade, alle Marktphasen zusammen.',
  'benchmark': 'Buy-and-Hold des jeweiligen Coins über genau dieselben Trades (Öffnen bis Schließen), ebenfalls je 1.000 $.',
  'excess ($)': 'Gesamtgewinn minus Benchmark, in Dollar.',
  'rang ohne filter': 'Rang nach Gesamtgewinn (Autor-Timeframe) unter allen Strategien mit Dollar-Ergebnis, ohne Robustheits-Filter.',
  'anteil': 'Anteil der Strategien mit Robustheits-PASS.',
  'pass': 'Strategien mit Robustheits-PASS (5m-Lauf und Kostenstress bestanden).',
  '5m sensitiv': 'Strategien, deren Ergebnis sich unter 5m-Detailkerzen wesentlich ändert: anderes Vorzeichen, mehr als 50 % Gewinnänderung oder mehr als 10 % andere Trade-Zahl.',
  'kosten ✗': 'Strategien, die den 5m-Lauf bestehen, aber 0,1 % zusätzlichen Slippage je Seite in dieser Phase nicht überstehen.',
  '5m offen': 'Timeframe über 5m, aber der 5m-Lauf ist nicht abgeschlossen (offen oder fehlgeschlagen).',
  'bestätigt': 'Strategien, die in dieser Phase in Discovery und Validation bestätigt sind.',
  'bestätigt + pass': 'Bestätigt und zugleich mit Robustheits-PASS.',
  'strategien': 'Anzahl der Strategien mit Floor in dieser Phase (mindestens 5 Episoden und 10 Trades).',
  'rang 1 ohne filter': 'Die beste Strategie der Phase nach Excess-Return, ohne Robustheits-Filter.',
  'rang 1 mit pass': 'Die beste Strategie der Phase nach Excess-Return unter denen mit Robustheits-PASS.',
  'rang': 'Platz in dieser Liste.',
  'excess discovery': 'Excess-Return in der Discovery (vor 2024-01-01).',
  'excess validation': 'Excess-Return in der Validation (ab 2024-01-01).',
  'trades / episoden': 'Anzahl der Trades und der Episoden im Discovery-Fenster.',
  'rang in validation': 'Platz unter allen Strategien mit Floor in der Validation. „unter Floor“: weniger als 5 Episoden oder 10 Trades, nicht gerankt.',
  'win-rate': 'Anteil der Gewinn-Trades.',
  'cagr': 'Jährliches Wachstum mit Zinseszins über den ganzen Zeitraum: (Endkapital ÷ Startkapital)^(365 ÷ Tage) − 1.',
  'sharpe': 'Freqtrades Sharpe-Ratio: Ø täglicher Gewinn geteilt durch dessen Streuung, aufs Jahr hochgerechnet.',
  'calmar': 'Freqtrades Calmar-Ratio: erwarteter Ertrag geteilt durch den maximalen Drawdown.',
  'max-dd': 'Größter Einbruch vom bisherigen Höchststand, in Prozent des Kontos.',
  'endkapital': 'Kontostand am Ende bei $1.000 Start und echtem Reinvestment.',
  'tier': 'VALIDATION: mindestens 5 Episoden und 10 Trades in dieser Phase, wird gerankt. EXPLORATORY: darunter, wird nur berichtet.',
  'ziel-regime': 'Der ADX-Zustand, auf den das Entry-Gate der Strategie beschränkt wurde.',
  'gate-kandidat(en)': 'Der Kandidat mit Entry-Gate; bei Uptrend eventuell zusätzlich mit dem -trend-Gate.',
  'excess-return verbessert': 'Bei wie vielen der 31 Kandidaten der Excess-Return durch das Gate höher ausfiel als ohne.',
  'median-delta': 'Median der Veränderung des Excess-Returns durch das Gate, in Prozentpunkten.',
  'trade-erhalt (median)': 'Wie viel Prozent der Trades das Gate im Median übrig ließ.',
  'kandidaten <10 trades danach': 'Bei wie vielen Kandidaten nach dem Gate weniger als 10 Trades blieben (unter dem Floor).',
  'modell': 'Modell 1: Gate nach BTC-Phase. Modell 2: nach Coin-Phase. Modell 3: nach beiden gleichzeitig.',
  'coin': 'Das Handelspaar gegen USDT.',
  'start': 'Erster Tag der Episode.',
  'ende': 'Letzter Tag der Episode.',
  'tage': 'Dauer der Episode in Tagen.',
  'gesamt': 'Summe über alle vier Zustände.',
  'adx uptrend': 'ADX ≥ 25 und +DI > −DI: starker Aufwärtstrend.',
  'adx downtrend': 'ADX ≥ 25 und −DI > +DI: starker Abwärtstrend.',
  'adx sideways': 'ADX < 20: kein ausgeprägter Trend.',
  'adx transition': '20 ≤ ADX < 25: Übergangszone.'
};
function tipFor(label){
  var key = label.toLowerCase().replace(/\s+/g, ' ').trim();
  return TERMS[key] || null;
}
function decorate(){
  document.querySelectorAll('table.plain').forEach(enableSort);
  document.querySelectorAll('table.plain th').forEach(function(th){
    if (th.getAttribute('title')) return;
    var tip = tipFor(th.textContent.replace(/[▴▾]/g, ''));
    if (tip) th.setAttribute('title', tip);
  });
}
(function(){
  var pending = false;
  function schedule(){
    if (pending) return;
    pending = true;
    requestAnimationFrame(function(){ pending = false; decorate(); });
  }
  new MutationObserver(schedule).observe(document.body, {childList: true, subtree: true});
  document.addEventListener('DOMContentLoaded', schedule);
  schedule();
})();

/* ---- search + sort wiring for one strategy table ----
   opts: data, tableId, bodyId, countId, searchId, defaultKey, defaultDir, rowHtml,
   optional filter(row), compare(key, a, b) returning a number or undefined, extra() run after a render. */
function wireSearchSortTable(opts){
  var key = opts.defaultKey, dir = opts.defaultDir;
  var body = document.getElementById(opts.bodyId);
  var count = document.getElementById(opts.countId);
  var search = document.getElementById(opts.searchId);
  var headers = Array.prototype.slice.call(document.querySelectorAll('#' + opts.tableId + ' th.sortable'));
  function compare(a, b){
    if (opts.compare) { var c = opts.compare(key, a, b, dir); if (c !== undefined) return c * dir; }
    if (key === 'strategy_id') return dir * a.strategy_id.localeCompare(b.strategy_id);
    if (key === 'lcb_grade') return dir * (gradeScore(a.lcb_grade) - gradeScore(b.lcb_grade));
    if (key === 'ur') {
      var du = a.ur - b.ur;
      if (du === 0) du = (a.us === null || a.us === undefined ? -9 : a.us) - (b.us === null || b.us === undefined ? -9 : b.us);
      return du * dir;
    }
    var av = a[key], bv = b[key];
    if (typeof av === 'string' || typeof bv === 'string') return dir * String(av || '').localeCompare(String(bv || ''));
    var an = av === null || av === undefined, bn = bv === null || bv === undefined;
    if (an || bn) return an && bn ? 0 : (an ? 1 : -1);
    return (av - bv) * dir;
  }
  function render(){
    var q = search.value.trim().toLowerCase();
    var rows = opts.data.filter(function(r){
      return r.strategy_id.toLowerCase().indexOf(q) !== -1 && (!opts.filter || opts.filter(r));
    });
    rows = rows.slice().sort(compare);
    count.textContent = rows.length + ' von ' + opts.data.length;
    body.innerHTML = rows.map(opts.rowHtml).join('');
    if (opts.extra) opts.extra(rows);
  }
  search.addEventListener('input', render);
  headers.forEach(function(th){
    th.addEventListener('click', function(){
      var k = th.getAttribute('data-key');
      if (key === k) { dir *= -1; }
      else {
        key = k;
        var sample = opts.data.find(function(r){ return r[k] !== null && r[k] !== undefined; });
        dir = (sample && typeof sample[k] === 'string') ? 1 : -1;
        if (k === 'rk') dir = 1;
      }
      markArrows(headers, th, dir);
      render();
    });
  });
  var initial = headers.filter(function(t){ return t.getAttribute('data-key') === key; })[0];
  if (initial) markArrows(headers, initial, dir);
  render();
  return {render: render};
}

