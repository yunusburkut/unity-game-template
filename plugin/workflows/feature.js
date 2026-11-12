export const meta = {
  name: 'feature',
  description: 'PLAN.md Now\'daki kartı gözetimsiz yapar: bağlam, plan, birim birim derleme kontrolü ve commit, doğrulama, 9/10 olana kadar puanlı review (en çok 3 tur), teslim',
  whenToUse: 'The user asked for the workflow on a game feature sized M or L, the Unity Editor is open, and either PLAN.md Now holds its spec card with the open questions answered or the request is typed after the command (args)',
  phases: [
    { title: 'Bağlam', detail: 'kart kontrolü, iki ajan kodu okur' },
    { title: 'Plan', detail: 'birimler karta yazılır' },
    { title: 'Yap', detail: 'birim birim: kod, derleme kontrolü, commit' },
    { title: 'Doğrula', detail: 'kabul maddeleri kanıtla işaretlenir' },
    { title: 'Review', detail: 'yeni reviewer\'lar 10 üzerinden puanlar; 9 olana kadar düzelt ve tekrar' },
    { title: 'Teslim', detail: 'PLAN.md teslim commit\'i, ya da kart açık bulgularıyla kalır' },
  ],
}

// Ceiling: a workflow cannot ask the user anything, so it refuses a card with open questions and stops at the first
// FAIL or UNKNOWN gate instead of guessing. Builders run one at a time: Unity code has one writer (no worktrees), and
// the main session writes nothing until this run reports.
const SPEC = 'PLAN.md'
const MAX_ROUNDS = 3
// the request typed after /gamekit:feature, if any; with no card in Now it becomes one (pipeline phase 1)
const ask = (args == null ? '' : typeof args === 'string' ? args : JSON.stringify(args)).trim()
// an agent awaited directly that stalls on every retry would end the run with a bare error: make it null, so each
// step's own stop message (with the word to type) reaches the user
const call = (prompt, opts) => agent(prompt, opts).catch(e => { log(opts.label + ': ' + String(e && e.message || e)); return null })

const CHECK = {
  type: 'object',
  properties: {
    card: { enum: ['none', 'same', 'other'], description: 'none: "## Now" holds no spec card; same: a card, and the typed request (if any) asks for its goal; other: a card for something else' },
    ready: { type: 'boolean' },
    reason: { type: 'string' },
    base: { type: 'string', description: 'the card\'s "Base:" line after "Base:", as written; with no such line, or one with no sha: git rev-parse --short=7 HEAD if no Plan line is ticked, else "yok"' },
    goal: { type: 'string' },
    accept: { type: 'array', items: { type: 'string' } },
    done: { type: 'array', items: { type: 'string' }, description: 'Plan lines already ticked [x]' },
    disputes: { type: 'array', items: { type: 'string' }, description: '"## Known issues" lines "review <the card\'s Base>: disputed ...", verbatim' },
  },
  required: ['card', 'ready', 'reason', 'base', 'goal', 'accept', 'done'],
}
const CARD = {
  type: 'object',
  properties: {
    goal: { type: 'string' },
    open: { type: 'array', items: { type: 'string' }, description: 'open questions that change the build, else empty' },
  },
  required: ['goal', 'open'],
}
const PLAN = {
  type: 'object',
  properties: {
    units: {
      type: 'array',
      description: 'only the units still to build',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          files: { type: 'string' },
          platforms: { type: 'array', items: { enum: ['android', 'ios'] }, description: 'phones whose code the unit touches: #if UNITY_ANDROID / UNITY_IOS, or #if !UNITY_EDITOR code they compile' },
        },
        required: ['title', 'files', 'platforms'],
      },
    },
    reviewers: {
      type: 'array',
      items: { enum: ['gamekit:unity-reviewer', 'gamekit:clarity-reviewer', 'gamekit:design-critic'] },
    },
    rulings: { type: 'array', items: { type: 'string' } },
  },
  required: ['units', 'reviewers', 'rulings'],
}
const BUILD = {
  type: 'object',
  properties: {
    status: { enum: ['PASS', 'FAIL', 'UNKNOWN'] },
    gate: { type: 'string', description: 'the gk-bridge verdict line' },
    commit: { type: 'string', description: 'short sha and subject, or empty' },
    note: { type: 'string', description: 'a step the user must do (Inspector, scene, a build check), else empty' },
    playerText: { type: 'boolean', description: 'true when this commit adds or changes player-facing text (UI strings, hints, labels)' },
    extras: { type: 'array', items: { type: 'string' }, description: 'work outside the unit the change needs, one line each, else empty' },
    disputes: { type: 'array', items: { type: 'string' }, description: 'review findings judged wrong, each with file:line evidence' },
  },
  required: ['status', 'gate', 'commit', 'note', 'playerText', 'extras', 'disputes'],
}
const VERIFY = {
  type: 'object',
  properties: {
    accept: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          item: { type: 'string' },
          state: { enum: ['ticked', 'playmode', 'failed', 'not run'], description: 'playmode: needs the user\'s hands, moved to Pending; failed: its check ran and failed; not run: its check could not run' },
          evidence: { type: 'string', description: 'the evidence, or how it failed, or why it did not run' },
        },
        required: ['item', 'state', 'evidence'],
      },
    },
    unverified: { type: 'array', items: { type: 'string' } },
    playerText: { type: 'boolean', description: 'true when the range adds or changes player-facing text (UI strings, hints, labels)' },
  },
  required: ['accept', 'unverified', 'playerText'],
}
const SCORE = {
  type: 'object',
  properties: {
    score: { type: 'number', minimum: 0, maximum: 10 },
    findings: {
      type: 'array',
      description: 'every deduction, including missing (yüksek) or unevidenced (orta) Accept items',
      items: {
        type: 'object',
        properties: {
          severity: { enum: ['yüksek', 'orta', 'düşük', 'karar'], description: 'karar = Karar/Ölç: the user\'s call or a playtest, 0 points' },
          where: { type: 'string', description: 'file:line or a quoted line' },
          what: { type: 'string' },
          breaks: { type: 'string' },
          fix: { type: 'string', description: 'for karar: the options and the cost of each, or the playtest to run' },
        },
        required: ['severity', 'where', 'what', 'breaks', 'fix'],
      },
    },
    inspector: { type: 'string', description: 'Inspector/scene steps the diff needs, or "yok"' },
    older: { type: 'string', description: 'the unscored "Önceden:" line (problems older than the range), or "yok"' },
  },
  required: ['score', 'findings', 'inspector', 'older'],
}
const HANDOFF = {
  type: 'object',
  properties: {
    commit: { type: 'string', description: 'short sha of the LAST commit you made, or "yok"' },
    subject: { type: 'string', description: 'that commit\'s subject line, or "yok"' },
    playmode: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' }, description: 'the card\'s Assumptions, else empty' },
  },
  required: ['commit', 'subject', 'playmode', 'assumptions'],
}

const short = t => t.replace('gamekit:', '')
const fmt = (f, who) => '[' + f.severity + '] ' + f.where + ' - ' + f.what + (who ? ' (' + short(who) + ')' : '')
const given = t => t && !/^\s*yok\s*\.?\s*$/i.test(t)
const uniq = xs => Array.from(new Set(xs))
const list = (title, xs) => xs.length ? title + ':\n- ' + xs.join('\n- ') + '\n' : ''
// the same shapes in PLAN.md as a main-session round writes (pipeline 6.4)
const decided = s => s.findings.filter(f => f.severity === 'karar').map(f => fmt(f, s.reviewer) + ' - ' + f.fix)
const olderLine = s => 'önceden ' + s.older + ' (' + short(s.reviewer) + ')'
// the score is the rubric's arithmetic on the listed findings; a reviewer's own number is logged, never used
const points = s => Math.max(0, 10 - 3 * s.findings.filter(f => f.severity === 'yüksek').length -
  s.findings.filter(f => f.severity === 'orta').length)
// a stopped gate, in the user's words: FAIL is Claude's to fix, UNKNOWN needs the Editor fixed first (REHBER: Sinyaller)
const gateStop = b => b.status + ': ' + b.gate + (b.status === 'FAIL'
  ? '. `devam` yaz, Claude düzeltir' : '. Satırdaki nedeni gider (Unity\'yi aç, Play\'den çık), sonra `devam`')

const checkCard = () => call(
  'Read ' + SPEC + ' (the spec card under "## Now", format in the gamekit:pipeline skill) and run, in Bash, ' +
  '`git rev-parse HEAD`, `git status --short` and `gk-bridge refresh`.' +
  (ask ? ' The user typed this request with the command: "' + ask + '".' : '') +
  ' ready=false when: card is not "same", its "Open questions" line lists anything unanswered, an Accept line has no ' +
  'evidence named, a `*.cs`, `*.asmdef` or `*.asmref` has uncommitted changes (other dirty files are fine: builders ' +
  'leave them unstaged), gk-bridge exits 1 (the build is already broken; unless every error is in a file of the ' +
  'card\'s own unticked Plan line committed as "compile unverified", which its builder gates again), or gk-bridge ' +
  'exits 2 (Editor closed, Play Mode, busy; "command not found" is no reason, the builders have a fallback). Say which ' +
  'in reason, in Turkish, with what the user should do (card none: "`/gamekit:feature <istek>` yaz"; card other: ' +
  '"Now\'da başka kart var: `devam` ile bitir ya da `kartı Next\'e taşı` yaz"; dirty code: "commit edilmemiş kod var: ' +
  '`commit et` ya da geri al"; exit 1: "derleme zaten kırık (<first error>): bu satırı yapıştır, Claude düzeltir"; exit 2: ' +
  'its line). base = the card\'s "Base:" line as written (with none, or one with no sha: HEAD if no Plan line is ' +
  'ticked, else "yok"). ' +
  'done = the Plan lines already ticked. ' +
  'disputes = the card\'s "review <Base>: disputed" lines under "## Known issues". Do not edit anything.',
  { label: 'kart kontrol', phase: 'Bağlam', schema: CHECK })

phase('Bağlam')
let check = await checkCard()
if (check && check.card === 'none' && ask) {
  const card = await call(
    'Write the spec card for this request under "## Now" in ' + SPEC + ', following the gamekit:pipeline skill, phase ' +
    '1 (load it with the Skill tool): "' + ask + '". Read the code it touches first. Nobody can answer questions during ' +
    'this run: settle anything with two reasonable readings under "Assumptions:" (the reversible reading), and list ' +
    'under "Open questions:" only what changes the build and has no reversible default. Its "Base:" line is ' +
    '`git rev-parse --short=7 HEAD`, run now. Commit ' + SPEC + ' alone with ' +
    '`git commit -F -`, subject "design: spec <goal>", and the line "Verified: spec card only".',
    { label: 'kart yaz', phase: 'Bağlam', schema: CARD })
  if (!card) return { stopped: 'Bağlam', reason: 'Kartı yazan ajan cevap vermedi: PLAN.md Now\'a bak, sonra yine `/gamekit:feature`' }
  if (card.open.length) {
    return { stopped: 'Bağlam', reason: 'Kart yazıldı, açık soruları var: cevapla; Claude cevapları karta yazıp commit eder, sonra /gamekit:feature', questions: card.open }
  }
  check = await checkCard()
}
if (!check || !check.ready) {
  return { stopped: 'Bağlam', reason: check ? check.reason : 'Kart kontrolü cevap vermedi: yine `/gamekit:feature`' }
}
log('Kart: ' + check.goal + ' (' + check.accept.length + ' kabul maddesi, ' + check.done.length + ' birim hazır)')
// the card's key (pipeline phase 1): its commits carry "Card: <KEY>", so other work inside KEY..HEAD (an S task
// between sessions, another card while this one was parked) is neither reviewed nor pruned as this card's
// an agent's string: the sha may come in backticks or after "Base:", and a wrong key loses every later commit
const keyMatch = /\b[0-9a-f]{7,40}\b/i.exec(String(check.base).replace(/`/g, ''))
if (!keyMatch) {
  return { stopped: 'Bağlam', reason: 'Kartın Base satırı okunamadı ("' + check.base + '"): `devam` yaz, Claude düzeltir' }
}
const KEY = keyMatch[0].slice(0, 7).toLowerCase()
// a Base repaired by `devam` (pipeline, Longer than one session): commits made before the repair carry "Card: <x>"
const before = /\(önce: ([^)]*)\)/.exec(String(check.base))
const ALIAS = before ? before[1].trim() : ''
const BASE = KEY + (ALIAS ? ' (önce: ' + ALIAS + ')' : '')
const RANGE = "the card's commits (`git log --format=%h --grep='^Card: " + KEY + "'" +
  (ALIAS ? " --grep='^Card: " + ALIAS + "'" : '') + ' ' + KEY + '..HEAD`; other ' +
  'commits in that span are other work: leave them out)'
const CARDLINE = ' Its commit body carries the line "Card: ' + KEY + '".'

const scouts = await parallel([
  'Which files implement or must respect this goal, and which Core/Game types, helpers or config assets already do part of it?',
  'Which scenes, prefabs and assets use the scripts this goal will change (by GUID), which serialized fields it may rename, and which platform #if, static or per-frame risks sit in that code?',
].map((q, i) => () => agent(
  'Goal: ' + check.goal + '\nSpec card: ' + SPEC + ' "## Now".\nQuestion: ' + q,
  { agentType: 'gamekit:scout', label: 'scout ' + (i + 1), phase: 'Bağlam' })))
const context = scouts.filter(Boolean).join('\n\n---\n\n')
if (!context) log('Scout raporu yok: plan kodu kendisi okur')

phase('Plan')
const plan = await call(
  'You plan a Unity game change. Follow the gamekit:pipeline skill, phase 3 (load it with the Skill tool).\n' +
  'Spec card: ' + SPEC + ' "## Now". Scout reports:\n' + context + '\n\n' +
  (check.done.length ? 'Already built (keep these lines ticked, do not plan them again):\n- ' + check.done.join('\n- ') + '\n' : '') +
  'Order the remaining units so each compiles alone and is one commit of about 1-3 files; climb the lean ladder ' +
  'first. Write them as the card\'s "Plan:" lines (`1. [ ] <unit> - <files> - gate: gk-bridge refresh`), its line ' +
  '"Base: ' + BASE + '" and any design choice under "Assumptions:" in ' + SPEC + '; edit nothing ' +
  'else. A design choice with two viable options: take the reversible one. Return each ruling in Turkish as "Seçim: ' +
  '<ne> - <neden> - <yanlışsa maliyeti>". Reviewers: always gamekit:unity-reviewer (it covers per-frame cost); add clarity-reviewer ' +
  'for player-facing text, design-critic for a level or mechanic. WebGL-only code, and PC-player-only code (`#if ' +
  '!UNITY_EDITOR` that phones do not compile, such as Steam), has no compile gate: say so in a ruling.',
  { label: 'plan', phase: 'Plan', schema: PLAN })
if (!plan || (!plan.units.length && !check.done.length)) {
  return { stopped: 'Plan', reason: 'Plan çıkmadı: `devam` yaz, Claude planı burada yapar', context }
}
plan.rulings.forEach(r => log(r))
const reviewers = Array.from(new Set(['gamekit:unity-reviewer'].concat(plan.reviewers)))

phase('Yap')
const built = []
for (let i = 0; i < plan.units.length; i++) {
  const u = plan.units[i]
  const r = await call(
    'Build unit ' + (i + 1) + '/' + plan.units.length + ' of the spec card in ' + SPEC + ': "' + u.title + '" (files: ' +
    u.files + ').' +
    (u.platforms.length ? ' It touches platform #if code: also run ' + u.platforms.map(p => '`gk-bridge compile ' + p + '`').join(', then ') + ', one at a time.' : '') +
    (built.length ? ' Already built: ' + built.map(b => b.commit).join('; ') + '.' : '') + CARDLINE,
    { agentType: 'gamekit:builder', label: 'birim ' + (i + 1), phase: 'Yap', schema: BUILD })
  if (!r) return { stopped: 'Yap', reason: 'Birim ' + (i + 1) + ' cevap vermedi: `devam` yaz', built }
  built.push(r)
  log('Birim ' + (i + 1) + ': ' + r.status + ' ' + r.commit)
  if (r.status !== 'PASS') {
    return { stopped: 'Yap', reason: 'Birim ' + (i + 1) + ' kapısı ' + gateStop(r), note: r.note, built }
  }
}

phase('Doğrula')
const verify = await call(
  'Verify ' + RANGE + ' against the spec card in ' + SPEC + '. Follow the ' +
  'gamekit:implementation-verification skill (load it with the Skill tool): run each Accept line\'s evidence check ' +
  'and tick it in ' + SPEC + ' with its evidence, move Play Mode items to "## Pending Play Mode checks", and do not ' +
  'commit. Do not edit code.',
  { label: 'doğrula', phase: 'Doğrula', schema: VERIFY })
// Accept items whose check failed or could not run: the reviewers score them, Teslim keeps the ones still unticked
const gaps = verify
  ? verify.accept.filter(a => a.state === 'failed' || a.state === 'not run').map(a => a.item + ' - ' + a.state + ': ' + a.evidence)
  : ['verification agent did not answer: no Accept item was checked']
gaps.forEach(g => log('Doğrulanmadı: ' + g))
// the plan picked reviewers before anything was built: text a unit or a fix round adds still gets its reviewer
const needClarity = () => { if (reviewers.indexOf('gamekit:clarity-reviewer') < 0) reviewers.push('gamekit:clarity-reviewer') }
if (built.some(b => b.playerText) || (verify && verify.playerText)) needClarity()

phase('Review')
const rounds = []
// a rerun on a card left "review open" keeps what its earlier rounds disputed (pipeline 6.2)
let disputes = check.disputes || []
let last = []
// every review of every round: a decision or an older problem only round 1 named still reaches Teslim
const everyRound = []
for (let round = 1; round <= MAX_ROUNDS; round++) {
  const reviews = await parallel(reviewers.map(type => () => agent(
    'Score this change with the review rubric. Range: ' + RANGE + '. Spec card: ' + SPEC + ' "## Now". ' +
    'List every deduction as a finding, including missing or unevidenced Accept items.' +
    (gaps.length ? '\nVerification left these Accept items open; one still unticked in the card scores as the rubric ' +
      'says:\n- ' + gaps.join('\n- ') : '') +
    (disputes.length ? '\nDisputed findings from earlier rounds (re-judge each):\n- ' + disputes.join('\n- ') : ''),
    { agentType: type, label: short(type) + ' r' + round, phase: 'Review', schema: SCORE })
    .then(s => s && Object.assign({ reviewer: type }, s, { score: points(s) }, s.score !== points(s) ? { claimed: s.score } : {}))))
  last = reviews.filter(Boolean)
  everyRound.push(...last)
  last.filter(s => 'claimed' in s).forEach(s => log(short(s.reviewer) + ': ' + s.claimed + ' dedi, bulguları ' + s.score + ' ediyor'))
  const silent = reviewers.filter(t => !last.some(s => s.reviewer === t))
  if (silent.length) log('Tur ' + round + ': cevap vermeyen reviewer: ' + silent.join(', '))
  rounds.push(last.map(s => ({ reviewer: s.reviewer, score: s.score })))
  const line = 'r' + round + ' ' + last.map(s => short(s.reviewer) + ' ' + s.score).join(', ')
  log('Tur ' + line)
  if (!silent.length && last.every(s => s.score >= 9)) break
  if (round === MAX_ROUNDS) break
  const findings = last.flatMap(s => s.findings.filter(f => f.severity === 'yüksek' || f.severity === 'orta')
    .map(f => fmt(f, s.reviewer) + ' - ' + f.breaks + ' - düzeltme: ' + f.fix))
  // a score below 9 always has findings (the arithmetic); with none, only a silent reviewer is left: call it again
  if (!findings.length) continue
  const fix = await call(
    'Unit: review fixes, round ' + round + ', for the spec card in ' + SPEC + '. Before fixing, write the round into ' +
    SPEC + ', so a later session can go on from it: set the card\'s "Review:" line to "' + line + '", and under "## ' +
    'Known issues" make each finding below one line "review ' + KEY + ': <finding>", in place of the "review ' + KEY +
    ': " lines from the round before (its "disputed" lines stay; other lines stay). Then judge each finding against ' +
    'the code. Fix the real ones in one commit (gate first) with ' + SPEC + ', and drop their lines; an Accept item you ' +
    'fix gets its evidence check run again and is ticked with it. For a finding that is wrong, change no code: add a ' +
    'dispute with file:line evidence, and its line becomes "review ' + KEY + ': disputed <file:line> - <evidence>".' +
    ' Write the lists after the findings too, each line once (one already there is not added again).' +
    CARDLINE + ' Findings:\n- ' + findings.join('\n- ') + '\n' +
    list('Decisions for "## Next", with their options', uniq(last.flatMap(decided))) +
    list('Known issues lines "review ' + KEY + ': <line>"', uniq(last.filter(s => given(s.older)).map(olderLine))),
    { agentType: 'gamekit:builder', label: 'düzelt r' + round, phase: 'Review', schema: BUILD })
  if (!fix || fix.status !== 'PASS') {
    return { stopped: 'Review', reason: 'Düzeltme turu ' + round + ' ' + (fix ? 'kapısı ' + gateStop(fix) : 'cevap vermedi: `devam` yaz'), rounds, last }
  }
  built.push(fix)
  if (fix.playerText) needClarity()
  disputes = disputes.concat(fix.disputes)
}
const silent = reviewers.filter(t => !last.some(s => s.reviewer === t))
const passed = !silent.length && last.every(s => s.score >= 9)
const open = last.flatMap(s => s.findings.filter(f => f.severity === 'yüksek' || f.severity === 'orta')
  .map(f => fmt(f, s.reviewer) + ' - ' + f.breaks + ' - düzeltme: ' + f.fix))
  .concat(silent.map(t => 'review missing: ' + short(t) + ' did not answer'))
// a decision keeps its options (or the playtest to run), so the user can choose from PLAN.md Next alone; one per
// file:line and question across rounds, the latest options kept (the handoff merges reworded repeats)
const decisions = Array.from(new Map(everyRound.flatMap(s => s.findings.filter(f => f.severity === 'karar')
  .map(f => [f.where + ' | ' + f.what, fmt(f, s.reviewer) + ' - ' + f.fix]))).values())
// Inspector steps from the last round only, so the fix rounds do not write them: each round reads the whole range
// (a step still needed is named again), and a fix may have made an earlier step obsolete (wired in code)
const steps = uniq(last.map(s => s.inspector).filter(given).concat(built.map(b => b.note).filter(given)))
const extras = uniq(built.flatMap(b => b.extras || []).filter(given))
// problems older than the range are not scored, but they are not dropped either
const older = uniq(everyRound.filter(s => given(s.older)).map(olderLine))
const scores = rounds.map((r, i) => 'r' + (i + 1) + ' ' + r.map(s => short(s.reviewer) + ' ' + s.score).join(', '))

phase('Teslim')
// only lines the pipeline wrote are pruned: a Known issue the user reported (a failed Play Mode check) has no prefix
const unticked = 'Every line you add under "## Known issues" starts with "review ' + KEY + ': "; Accept items still ' +
  'unticked in the card that are not Play Mode checks go there too. A "review ' + KEY + ': " line already there that ' +
  'the lists below no longer name leaves the file; other lines (another card\'s key, or the user\'s with no prefix) ' +
  'stay. Lines that say the same thing become one. "## Next" keeps at most 5 items: merge related ones, and list ' +
  'what still does not fit in the commit body, older non-decision items first; a [karar] line always stays in Next ' +
  '(the user looks there), past 5 if it must. '
const handoff = await call(passed
  ? 'Hand off the spec card in ' + SPEC + ' (gamekit:pipeline phase 7). First set the card\'s "Review:" line to "' +
    scores[scores.length - 1] + '" and commit ' + SPEC + ' alone (`git commit -F -`, subject "design: review passed ' +
    check.goal + '", "Card: ' + KEY + '", "Verified: workflow review rounds ' + scores.join('; ') + '"), so the ' +
    'record survives if the rest stops. Then copy the card\'s "Assumptions:" (unless "none") into DESIGN.md "## Decisions", one line each, and ' +
    'return them. ' + unticked + 'Then put "## Now" back to its TODO line (move nothing up from "## Next": a Next item ' +
    'reaches Now only when the user asks for it) and keep "## Pending Play Mode checks" as concrete actions with the ' +
    'expected result for PC and, when input, UI or performance changed, the phone.\n' +
    list('Add these Inspector/scene steps to Pending Play Mode checks', steps) +
    list('Add these under "## Known issues"', open.concat(older)) +
    list('Add these user decisions under "## Next", options included', decisions) +
    list('Add these needed extras under "## Next"', extras) +
    'Commit only PLAN.md and DESIGN.md with `git commit -F -`, subject "design: hand off ' + check.goal + '", a body ' +
    'listing the review scores (' + scores.join('; ') + '), the line "Card: ' + KEY + '", and "Verified: workflow ' +
    'gates as listed in the earlier commits".'
  : 'The review of the spec card in ' + SPEC + ' did not reach 9/10. Do NOT clear "## Now": keep the card, set its ' +
    '"Review:" line to "' + scores[scores.length - 1] + '", and add the open findings under "## Known issues". ' + unticked + 'Return the card\'s Assumptions.\n' + list('Open findings', open.concat(older)) +
    list('Disputes, each kept as its "review ' + KEY + ': disputed" line', disputes) +
    list('Inspector/scene steps for Pending Play Mode checks', steps) +
    list('User decisions for "## Next", options included', decisions) + list('Needed extras for "## Next"', extras) +
    'Commit only PLAN.md with `git commit -F -`, subject "design: review open for ' + check.goal + '", a body listing ' +
    'the scores (' + scores.join('; ') + '), the line "Card: ' + KEY + '", and "Verified: ' +
    'workflow gates as listed in the earlier commits".',
  { label: passed ? 'teslim' : 'kart açık kaldı', phase: 'Teslim', schema: HANDOFF })
// the sha may come wrapped in backticks or after a word; the subject proves the last commit is the handoff, not only
// the "review passed" record before it
if (!handoff || !/\b[0-9a-f]{7,40}\b/i.test(handoff.commit.replace(/`/g, '')) ||
    !/\bdesign: (hand off|review open)\b/.test(handoff.subject)) {
  return {
    stopped: 'Teslim', passed, rounds, open, older, decisions, extras, inspector: steps, gaps, commits: built.map(b => b.commit),
    reason: 'Teslim commit edilmedi; kart hâlâ PLAN.md Now\'da (' + scores[scores.length - 1] + '): `' +
      (passed ? 'kabul' : 'devam') + '` yaz',
  }
}

return {
  goal: check.goal,
  range: KEY + '..HEAD, commits with "Card: ' + KEY + '"' + (ALIAS ? ' or "Card: ' + ALIAS + '"' : ''),
  passed,
  commits: built.map(b => b.commit).concat(handoff.commit + ' ' + handoff.subject),
  rounds,
  open,
  older,
  decisions,
  extras,
  inspector: steps,
  assumptions: handoff.assumptions,
  gaps,
  unverified: verify ? verify.unverified : ['verification agent did not answer'],
  accept: verify ? verify.accept : [],
  playmode: handoff.playmode,
  rulings: plan.rulings,
}
