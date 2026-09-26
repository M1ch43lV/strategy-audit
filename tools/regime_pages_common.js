// Language switch: every page sets PAGE_LANG = 'en' before this script; without it the helpers fall back to German.
// T(de, en) picks the string, dec() the decimal separator.
var EN = typeof PAGE_LANG !== 'undefined' && PAGE_LANG === 'en';
var LOCALE = EN ? 'en-US' : 'de-DE';
function T(de, en){ return EN ? en : de; }
function dec(str){ return EN ? String(str) : String(str).replace('.', ','); }
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
// 5m recovery marker (2026-09-21): the strategy's own timeframe is 1m, its canonical 1m pooled backtest ran out of
// memory, and the figures are those of an owner-approved rerun at 5m (manifest scope owner_approved_timeframe_5m_recovery_*).
var REC5 = new Set(typeof RECOVERY5MSTRATEGIES === 'undefined' ? [] : RECOVERY5MSTRATEGIES);
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
// Origin-repo lookup (added 2026-09-22, explicit user request): every table
// on both pages renders strategy names through this one function, so wiring
// the link here reaches all of them at once rather than each table's own
// row-rendering code separately.
var REPO = typeof REPOMAP === 'undefined' ? {} : REPOMAP;
function futuresLabel(strategyId){
  var base = baseStrategyId(strategyId);
  var label = strategyId + (FUTURES.has(base) ? ' *' : '') + (DCA.has(base) ? ' #' : '') + (REC5.has(base) ? ' †' : '');
  var repo = REPO[base];
  if (!repo) return label;
  return '<a href="https://github.com/' + repo + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
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
  const s = Math.round(Math.abs(v)).toLocaleString(LOCALE);
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
  if (abs >= 1e9) return (abs / 1e9).toFixed(1) + T('Mrd', 'B');
  if (abs >= 1e6) return (abs / 1e6).toFixed(1) + T('Mio', 'M');
  if (abs >= 1e3) return (abs / 1e3).toFixed(1) + T('Tsd', 'k');
  return abs.toFixed(2);
}
function fmtSortino(v){
  if (v === null || v === undefined) return '&mdash;';
  // freqtrade's own "-100.0" broken-Sortino sentinel (no losing trades at
  // all) - FreqForge scores this best-in-class, not worst, so it is shown
  // as such rather than as a literal -100.00.
  if (v <= -99.99) return T('kein Verlust', 'no loss');
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
  return (v >= 0 ? '+' : '−') + Math.abs(100 * v).toFixed(1).replace('.', T(',', '.')) + ' %';
}
/* Confirmation across the discovery and the validation window (regime/discovery_comparison.py).
   cf: 2 confirmed, 1 floor in both windows but not confirmed, 0 no discovery floor.
   sc: the smaller of the two lower confidence bounds, the weakest link. */
function confirmCell(r){
  var score = '<span class="confscore" title="' + T('Score: die kleinere der beiden unteren Vertrauensgrenzen', 'Score: the smaller of the two lower confidence bounds') + '">' + fmtConf(r.sc) + '</span>';
  if (r.cf === 2) {
    return '<td class="num"><span class="rbadge rb-ok" title="' + T('Floor in beiden Fenstern, und die untere Vertrauensgrenze des Excess-Returns liegt in der Discovery und in der Validation über 0.', 'Floor in both windows, and the lower confidence bound of the excess return is above 0 in discovery and in validation.') + '">' + T('bestätigt', 'confirmed') + '</span>' + score + '</td>';
  }
  if (r.cf === 1) {
    return '<td class="num"><span class="rbadge rb-warn" title="' + T('Floor in beiden Fenstern, aber mindestens eine untere Vertrauensgrenze liegt nicht über 0.', 'Floor in both windows, but at least one lower confidence bound is not above 0.') + '">' + T('nicht bestätigt', 'not confirmed') + '</span>' + score + '</td>';
  }
  return '<td class="num"><span class="rbadge rb-no" title="' + T('Die Strategie erreicht in dieser Phase in der Discovery den Floor nicht (weniger als 5 Episoden oder 10 Trades).', 'The strategy does not reach the floor in this phase in discovery (fewer than 5 episodes or 10 trades).') + '">–</span></td>';
}
/* Universal candidates: 2 strict (confirmed in all four coin phases), 1 mild (better than
   Buy-and-Hold in both windows in at least three of the four phases), 0 neither. */
function uconfirmCell(r){
  var cls = r.ur === 2 ? 'rb-ok' : (r.ur === 1 ? 'rb-warn' : 'rb-no');
  var text = r.ur === 2 ? T('streng bestätigt', 'strictly confirmed') : (r.ur === 1 ? T('mild bestätigt', 'mildly confirmed') : T('nicht bestätigt', 'not confirmed'));
  var title = r.ur === 2 ? T('In allen vier Coin-Phasen bestätigt.', 'Confirmed in all four coin phases.') :
    (r.ur === 1 ? T('Nicht in allen vier Phasen bestätigt, aber in ' + r.up + ' von 4 Phasen in beiden Fenstern besser als Buy-and-Hold (mildere Regel).', 'Not confirmed in all four phases, but better than buy-and-hold in both windows in ' + r.up + ' of 4 phases (milder rule).') :
    T('In weniger als drei Phasen in beiden Fenstern besser als Buy-and-Hold.', 'Better than buy-and-hold in both windows in fewer than three phases.'));
  return '<td class="num"><span class="rbadge ' + cls + '" title="' + title + '">' + text + '</span><span class="confscore" title="' + T('Score der schwächsten Phase: die kleinere der beiden unteren Vertrauensgrenzen', 'Score of the weakest phase: the smaller of the two lower confidence bounds') + '">' + fmtConf(r.us) + '</span></td>';
}
function robustCell(r){
  if (r.ok) {
    return '<td class="num"><span class="rbadge rb-ok" title="' + T('5m-Detaillauf bestanden und Kostenstress (0,1 % Slippage je Seite) in diesem ADX-Zustand bestanden', '5m detail run passed and cost stress (0.1 % slippage per side) passed in this ADX state') + '">PASS</span></td>';
  }
  var text, cls = 'rb-no', title;
  if (r.xs === 'SENSITIVE') { text = T('sensitiv', 'sensitive'); cls = 'rb-warn'; title = T('Das Ergebnis ändert sich unter 5m-Detailkerzen wesentlich (Vorzeichen, mehr als 50 % Gewinnänderung oder mehr als 10 % andere Trades).', 'The result changes materially under 5m detail candles (sign, more than 50 % change in profit, or more than 10 % different trades).'); }
  else if (r.xs === 'PENDING') { text = T('5m offen', '5m open'); title = T('Timeframe über 5m; der 5m-Detaillauf steht noch aus.', 'Timeframe above 5m; the 5m detail run is still pending.'); }
  else if (r.xs === 'ERROR') { text = T('Fehler', 'Error'); title = T('Der 5m-Detaillauf oder sein Vergleich ist fehlgeschlagen.', 'The 5m detail run or its comparison failed.'); }
  else if (r.xs === 'PASS') { text = T('Kosten ✗', 'Cost ✗'); cls = 'rb-warn'; title = T('Ausführung bestanden, aber der Gewinn in diesem Zustand übersteht 0,1 % zusätzlichen Slippage je Seite nicht oder hat zu wenige Trades.', 'Execution passed, but the profit in this state does not survive 0.1 % additional slippage per side, or has too few trades.'); }
  else { text = '–'; title = T('Kein Robustheitsergebnis für diese Strategie.', 'No robustness result for this strategy.'); }
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
  var scoreText = partial ? '<span class="confscore" title="' + T('In wie vielen der vier Coin- und der vier BTC-Marktphasen die Strategie bestätigt ist.', 'In how many of the four coin and the four BTC market phases the strategy is confirmed.') + '">Coin ' + (r.cn || 0) + '/4 · BTC ' + (r.bn || 0) + '/4</span>' : '';
  var badge;
  if (r.ur === 2) badge = '<span class="rbadge rb-ok" title="' + T('Universal-Kandidat, in allen vier Coin-Phasen in Discovery und Validation bestätigt.', 'Universal candidate, confirmed in discovery and validation in all four coin phases.') + '">' + T('streng bestätigt', 'strictly confirmed') + '</span>';
  else if (r.ur === 1) badge = '<span class="rbadge rb-warn" title="' + T('Universal-Kandidat, in mindestens drei der vier Coin-Phasen in beiden Fenstern besser als Buy-and-Hold (mildere Regel).', 'Universal candidate, better than buy-and-hold in both windows in at least three of the four coin phases (milder rule).') + '">' + T('mild bestätigt', 'mildly confirmed') + '</span>';
  else if (partial) badge = '<span class="rbadge rb-warn" title="' + T('Nicht als Universal-Kandidat bestätigt, aber in einzelnen Marktphasen bestätigt.', 'Not confirmed as a universal candidate, but confirmed in individual market phases.') + '">' + T('teilweise', 'partly') + '</span>';
  else if (r.ur === 0) badge = '<span class="rbadge rb-no" title="' + T('Universal-Kandidat, aber weder streng noch mild bestätigt.', 'Universal candidate, but neither strictly nor mildly confirmed.') + '">' + T('nicht bestätigt', 'not confirmed') + '</span>';
  else badge = '<span class="rbadge rb-no" title="' + T('In keiner Marktphase in beiden Fenstern bestätigt.', 'Not confirmed in both windows in any market phase.') + '">–</span>';
  return '<td class="num" data-v="' + (r.cq || 0) + '">' + badge + scoreText + '</td>';
}
/* The same, inline, for the winner cards (one phase). */
function confInline(r){
  if (r.cf === 2) return '<span class="rbadge rb-ok" title="' + T('Floor in beiden Fenstern, untere Vertrauensgrenze in Discovery und Validation über 0. Score: die schwächere der beiden Grenzen.', 'Floor in both windows, lower confidence bound above 0 in discovery and validation. Score: the weaker of the two bounds.') + '">' + T('bestätigt ', 'confirmed ') + fmtConf(r.sc) + '</span>';
  if (r.cf === 1) return '<span class="rbadge rb-warn" title="' + T('Floor in beiden Fenstern, aber mindestens eine untere Vertrauensgrenze liegt nicht über 0.', 'Floor in both windows, but at least one lower confidence bound is not above 0.') + '">' + T('nicht bestätigt', 'not confirmed') + '</span>';
  return '<span class="rbadge rb-no" title="' + T('In der Discovery unter dem Floor in dieser Phase.', 'Below the floor in discovery in this phase.') + '">–</span>';
}

/* ---- sorting for tables that have no sorter of their own (a click on any header) ---- */
function parseNumberText(text){
  var t = String(text).replace(/−/g, '-').trim();
  if (/^(kein Verlust|no loss)/.test(t) || t.charAt(0) === '∞') return Infinity;
  var m = t.match(/^([-+]?)\$?\s?(\d[\d.,]*)(Tsd|Mio|Mrd|k|M|B)?/);
  if (!m) return null;
  var s = m[2];
  if (EN) s = s.replace(/,/g, '');
  else {
    if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) s = s.replace(/\./g, '');
    s = s.replace(',', '.');
  }
  var v = parseFloat(s);
  if (isNaN(v)) return null;
  var mult = {Tsd: 1e3, Mio: 1e6, Mrd: 1e9, k: 1e3, M: 1e6, B: 1e9}[m[3]] || 1;
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
        var c = numeric ? (a.v === b.v ? 0 : (a.v < b.v ? -1 : 1)) : String(a.v).localeCompare(String(b.v), LOCALE);
        return c === 0 ? a.k - b.k : c * dir;
      });
      order.forEach(function(o){ body.appendChild(o.r); });
      markArrows(ths, th, dir);
    });
  });
}

/* ---- header tooltips: what a term means, for every table header that has no title yet ---- */
var TERMS = {
  'strategie': 'Name der FreqTrade-Strategie. * = Futures-Strategie, # = DCA-Strategie, † = Autor-Timeframe 1m, auf 5m neu gerechnet (siehe Legende).',
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
var TERMS_EN = {
  'strategy': 'Name of the FreqTrade strategy. * = futures strategy, # = DCA strategy, † = author timeframe 1m, rerun at 5m (see legend).',
  'state': 'ADX market phase: uptrend, downtrend, sideways or transition. Definition in the section “ADX regime”.',
  'regime': 'Kind of market phase: BTC (the state of BTC) or coin (the state of the traded coin).',
  'phase': 'ADX market phase: uptrend, downtrend, sideways or transition.',
  'weakest regime': 'The coin phase with this strategy\'s worst excess return. For a universal candidate it is the weak spot of the all-round claim.',
  'trades': 'Number of trades opened in the window shown.',
  'episodes': 'Contiguous stretches of a market phase (for example an uptrend over seven weeks). Each episode counts as one independent observation; the floor requires at least 5.',
  'excess return': 'Return of the strategy in the episodes of this phase minus buy-and-hold over the same episodes. Above 0 means: better than holding.',
  'dollar gain': 'Sum of the gains of all trades at a fixed $1,000 stake per trade, without reinvestment.',
  'b&h gain': 'The same amount for buy-and-hold of the respective coin over the whole episodes.',
  'excess in the weakest': 'Excess return in the coin phase in which this strategy is weakest.',
  'median excess': 'Median of this strategy\'s excess returns over its four coin phases.',
  'max drawdown': 'Largest drop of the gain curve at a fixed $1,000 stake, in percent of the capital deployed up to that point.',
  'worst trade': 'The worst single trade in this phase, in percent of its stake.',
  'sortino': 'Return divided by the dispersion of the losing trades, annualised. “no loss” means: there was no losing trade.',
  'return p.a.': 'Mean trade return times trades per year. Extrapolated linearly, without compounding.',
  'profit factor': 'Gross profit divided by gross loss. Above 1 means: more profit than loss. ∞ means: no losing trade.',
  'freqforge score': 'Score from 0 to 100 from six categories after FreqForge (Sortino, drawdown, return, liquidation, profit factor, worst trade). An additional column only, not a ranking criterion.',
  'episode excess lcb': 'LCB (lower confidence bound): lower 95 % confidence bound of the mean excess return per episode. Above 0 means: the lead is statistically reliable.',
  'grade': 'Grade A to F from the LCB: A above +2 %, B 0 to +2 %, C −2 to 0 %, D −5 to −2 %, F below.',
  'robustness': 'Stage 8b. PASS: the 5m detail run is passed (up to 5m by rule) and the profit survives 0.1 % additional slippage per side.',
  'confirmation': 'Confirmed means: floor in discovery and validation, and the lower confidence bound is above 0 in both. The value next to it is the score, the weaker of the two bounds.',
  'consistency': 'Share of the four coin phases in which the strategy beats buy-and-hold.',
  'total gain': 'Sum of the gains of all validation trades at a fixed $1,000 stake per trade, all market phases together.',
  'benchmark': 'Buy-and-hold of the respective coin over exactly the same trades (open to close), also $1,000 each.',
  'excess ($)': 'Total gain minus benchmark, in dollars.',
  'rank without filter': 'Rank by total gain of the 5m run among all strategies with a 5m dollar result, without robustness filter. Strategies at or below 5m rank by their own run.',
  'share': 'Share of the strategies with robustness PASS.',
  'pass': 'Strategies with robustness PASS (5m run and cost stress passed).',
  '5m sensitive': 'Strategies whose result changes materially under 5m detail candles: different sign, more than 50 % change in profit, or more than 10 % different trade count.',
  'cost ✗': 'Strategies that pass the 5m run but do not survive 0.1 % additional slippage per side in this phase.',
  '5m open': 'Timeframe above 5m, but the 5m run is not finished (open or failed).',
  'confirmed': 'Strategies confirmed in discovery and validation in this phase.',
  'confirmed + pass': 'Confirmed and at the same time with robustness PASS.',
  'strategies': 'Number of strategies with the floor in this phase (at least 5 episodes and 10 trades).',
  'rank 1 without filter': 'The best strategy of the phase by excess return, without robustness filter.',
  'rank 1 with pass': 'The best strategy of the phase by excess return among those with robustness PASS.',
  'rank': 'Place in this list.',
  'excess discovery': 'Excess return in discovery (before 2024-01-01).',
  'excess validation': 'Excess return in validation (from 2024-01-01).',
  'trades / episodes': 'Number of trades and episodes in the discovery window.',
  'rank in validation': 'Place among all strategies with the floor in validation. “below floor”: fewer than 5 episodes or 10 trades, not ranked.',
  'win rate': 'Share of winning trades.',
  'cagr': 'Annual growth with compounding over the whole period: (final capital ÷ starting capital)^(365 ÷ days) − 1.',
  'sharpe': 'Freqtrade\'s Sharpe ratio: mean daily gain divided by its dispersion, annualised.',
  'calmar': 'Freqtrade\'s Calmar ratio: expected return divided by the maximum drawdown.',
  'max dd': 'Largest drop from the previous peak, in percent of the account.',
  'final capital': 'Account balance at the end with $1,000 start and real reinvestment.',
  'coin': 'The trading pair against USDT.',
  'start': 'First day of the episode.',
  'end': 'Last day of the episode.',
  'days': 'Duration of the episode in days.',
  'total': 'Sum over all four states.',
  'timeframe': 'The strategy\'s timeframe (from the author). Above 5m the run is resolved with 5m candles; the author-timeframe result is not shown.',
  'adx uptrend': 'ADX ≥ 25 and +DI > −DI: strong uptrend.',
  'adx downtrend': 'ADX ≥ 25 and −DI > +DI: strong downtrend.',
  'adx sideways': 'ADX < 20: no pronounced trend.',
  'adx transition': '20 ≤ ADX < 25: transition zone.'
};
if (EN) TERMS = TERMS_EN;
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

/* ---- Autor / 5m: which side a numeric column sorts by ---- */
var SORT_BASIS = 'd5';
var TABLE_RENDERS = [];
function syncBasisUi(){
  Array.prototype.forEach.call(document.querySelectorAll('input[name="sort-basis"]'), function(el){ el.checked = el.value === SORT_BASIS; });
  Array.prototype.forEach.call(document.querySelectorAll('.hs'), function(el){ el.classList.toggle('active', el.getAttribute('data-basis') === SORT_BASIS); });
}
function setBasis(basis){
  SORT_BASIS = basis;
  syncBasisUi();
  TABLE_RENDERS.forEach(function(fn){ fn(); });
}
/* a click on the "Autor" or "5m" half of a header picks that side before the header sorts */
document.addEventListener('click', function(ev){
  var hs = ev.target.closest ? ev.target.closest('.hs') : null;
  if (hs) { SORT_BASIS = hs.getAttribute('data-basis'); syncBasisUi(); }
}, true);
document.addEventListener('change', function(ev){
  if (ev.target && ev.target.name === 'sort-basis') setBasis(ev.target.value);
});
/* The value a table sorts by. Keys named in `keys5` (a map to flat fields) or `pairedKeys`
   (fields of the nested `x5` object) have a 5m side; every other key sorts by the row itself. */
function basisValue(r, key, opts){
  if (SORT_BASIS === 'd5') {
    // at or below 5m the author run already is the 5m resolution: sort by its own figure
    if (r.tfm && r.tfm <= 5) return r[key];
    if (opts.keys5 && opts.keys5[key]) return r[opts.keys5[key]];
    if (opts.pairedKeys && opts.pairedKeys.indexOf(key) !== -1) return r.x5 ? r.x5[key] : null;
  }
  return r[key];
}
function isMissing(v){ return v === null || v === undefined || (typeof v === 'number' && isNaN(v)); }

/* ---- a cell with two figures, author timeframe / 5m rerun ---- */
function why5(r){
  if (r.x5 && r.x5.tier) return T('Im 5m-Lauf unter dem Floor in dieser Phase (', 'Below the floor in the 5m run in this phase (') + r.x5.trades + T(' Trades, ', ' trades, ') + r.x5.episodes + T(' Episoden): kein belastbares Ergebnis.', ' episodes): no reliable result.');
  if (r.tfm && r.tfm < 5) return T('Kein 5m-Lauf: der Timeframe der Strategie ist ' + r.tf + ' und liegt unter 5m (Regel, keine Messung).', 'No 5m run: the strategy\'s timeframe is ' + r.tf + ', below 5m (rule, not a measurement).');
  if (r.tfm > 5) return T('Kein verwertbarer 5m-Lauf: der Lauf ist fehlgeschlagen, oder die Strategie erreicht im 5m-Lauf nicht in allen vier Coin-Phasen den Floor.', 'No usable 5m run: the run failed, or the strategy does not reach the floor in all four coin phases in the 5m run.');
  return T('Kein 5m-Wert.', 'No 5m value.');
}
function fmtOrDash(f, v){ return isMissing(v) ? '<span class="na5">–</span>' : f(v); }
/* Above 5m the author-timeframe run is not a real result (the order of events inside a candle is not
   resolved), so only the 5m side is shown for those strategies. */
function authorHidden(r){ return !!(r.tfm && r.tfm > 5); }
function pairCell(f, r, k){
  var b = (r.x5 && !isMissing(r.x5[k])) ? f(r.x5[k]) : '<span class="na5" title="' + why5(r) + '">–</span>';
  if (authorHidden(r)) return '<td class="num">' + b + '</td>';
  return '<td class="num">' + fmtOrDash(f, r[k]) + '</td>';
}
/* header of a column that has both sides; the two halves of "Author / 5m" are clickable */
function pairTh(key, label, tip, extra){
  return '<th class="sortable num' + (extra || '') + '" data-key="' + key + '" title="' + tip + '">' + label +
    '<span class="arrow">&#9662;</span></th>';
}
var F = {
  int: function(v){ return '<span class="mono">' + v + '</span>'; },
  pct: function(v){ return '<span class="val ' + valClass(v) + '">' + fmtPct(v) + '</span>'; },
  usd: function(v){ return '<span class="val ' + dollarClass(v) + '">' + fmtUsd(v) + '</span>'; },
  dd: function(v){ return '<span class="mono">' + fmtDrawdown(v) + '</span>'; },
  sortino: function(v){ return '<span class="val ' + valClass(v) + '">' + fmtSortino(v) + '</span>'; },
  ann: function(v){ return '<span class="val ' + valClass(v) + '">' + fmtAnnualizedReturn(v) + '</span>'; },
  pf: function(v){ return '<span class="mono">' + fmtProfitFactor(v) + '</span>'; },
  score: function(v){ return '<span class="val ' + scoreClass(v) + '">' + fmtScore(v) + '</span>'; },
  lcb: function(v){ return '<span class="mono">' + fmtLcb(v) + '</span>'; },
  grade: function(v){ return '<span class="val ' + gradeClass(v) + '">' + v + '</span>'; },
  cons: function(v){ return '<span class="mono">' + Math.round(v * 100) + '%</span>'; }
};

/* ---- search + sort wiring for one strategy table ----
   opts: data, tableId, bodyId, countId, searchId, defaultKey, defaultDir, rowHtml,
   optional filter(row), keys5 / pairedKeys (the columns that have a 5m side), extra(rows). */
function wireSearchSortTable(opts){
  var key = opts.defaultKey, dir = opts.defaultDir;
  var body = document.getElementById(opts.bodyId);
  var count = document.getElementById(opts.countId);
  var search = document.getElementById(opts.searchId);
  var headers = Array.prototype.slice.call(document.querySelectorAll('#' + opts.tableId + ' th.sortable'));
  function valueOf(r){
    if (key === 'lcb_grade') { var g = basisValue(r, key, opts); return isMissing(g) ? null : gradeScore(g); }
    if (key === 'ur') return (r.ur === undefined ? -1 : r.ur) * 100 + (isMissing(r.us) ? -9 : r.us);
    if (key === 'cf') return r.cf * 100 + (isMissing(r.sc) ? -9 : r.sc);
    if (key === 'tf') return Math.min(r.tfm, 5);
    return basisValue(r, key, opts);
  }
  function render(){
    var q = search.value.trim().toLowerCase();
    var rows = opts.data.filter(function(r){
      return r.strategy_id.toLowerCase().indexOf(q) !== -1 && (!opts.filter || opts.filter(r));
    }).map(function(r, i){ return {r: r, v: valueOf(r), i: i}; });
    rows.sort(function(a, b){
      var ma = isMissing(a.v), mb = isMissing(b.v);
      if (ma || mb) return ma && mb ? a.i - b.i : (ma ? 1 : -1);
      var c = (typeof a.v === 'string' || typeof b.v === 'string') ? String(a.v).localeCompare(String(b.v), LOCALE) : (a.v === b.v ? 0 : (a.v < b.v ? -1 : 1));
      return c === 0 ? a.i - b.i : c * dir;
    });
    var shown = rows.map(function(o){ return o.r; });
    count.textContent = shown.length + T(' von ', ' of ') + opts.data.length;
    body.innerHTML = shown.map(opts.rowHtml).join('');
    if (opts.extra) opts.extra(shown);
  }
  var sortedBasis = SORT_BASIS;
  search.addEventListener('input', render);
  headers.forEach(function(th){
    th.addEventListener('click', function(){
      var k = th.getAttribute('data-key');
      if (key === k) {
        if (sortedBasis === SORT_BASIS) dir *= -1;      // same column, same side: turn around
      } else {
        key = k;
        var sample = opts.data.find(function(r){ return !isMissing(r[k]); });
        dir = (sample && typeof sample[k] === 'string') ? 1 : -1;
        if (k === 'rk') dir = 1;
      }
      sortedBasis = SORT_BASIS;
      markArrows(headers, th, dir);
      TABLE_RENDERS.forEach(function(fn){ fn(); });   // the side may have changed for every table
    });
  });
  var initial = headers.filter(function(t){ return t.getAttribute('data-key') === key; })[0];
  if (initial) markArrows(headers, initial, dir);
  render();
  TABLE_RENDERS.push(render);
  return {render: render};
}
document.addEventListener('DOMContentLoaded', syncBasisUi);
