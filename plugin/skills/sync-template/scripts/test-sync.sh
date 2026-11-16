#!/usr/bin/env bash
# Deterministic check of sync.sh against a throwaway template and game in a temp folder (no Unity, no network).
#   bash plugin/skills/sync-template/scripts/test-sync.sh   -> "sync.sh: all checks passed" or the first failure
set -euo pipefail
SYNC="$(cd "$(dirname "$0")" && pwd)/sync.sh"
W=$(mktemp -d); trap '[ -n "${KEEP:-}" ] || rm -rf "$W"' EXIT; echo "$W" >&2
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t GIT_CONFIG_NOSYSTEM=1
# fixed dates: the fallback for a game without a marker picks the template commit by date
at() { export GIT_COMMITTER_DATE="$1T12:00:00Z" GIT_AUTHOR_DATE="$1T12:00:00Z"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
g() { git -c core.autocrlf=false -c init.defaultBranch=main "$@"; }
manifest() { printf '{\n  "dependencies": {\n    "com.yunusburkut.gamekit": "https://example.invalid/x.git?path=/packages/com.yunusburkut.gamekit#%s",\n    "com.unity.ugui": "2.6.0"\n  }\n}\n' "$1"; }

# template at its first commit, with the steam pack (the game has it) and the linear pack (it does not)
at 2026-01-01
g init -q --bare "$W/origin.git"; g clone -q "$W/origin.git" "$W/t" 2>/dev/null; cd "$W/t"
mkdir -p project/Assets/__GAME__/Core project/Packages project/ProjectSettings packs/steam/Assets/__GAME__/Game packs/linear/.claude packages/com.yunusburkut.gamekit
echo '{ "name": "__GAME__.Core" }' > project/Assets/__GAME__/Core/__GAME__.Core.asmdef
printf 'one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\nnine\n' > project/notes.txt
manifest gamekit-v0.1.0 > project/Packages/manifest.json
echo '  companyName: __COMPANY__' > project/ProjectSettings/ProjectSettings.asset
echo '// __GAME__ steam' > packs/steam/Assets/__GAME__/Game/Steam.cs; echo 'steam readme' > packs/steam/README.md
echo '{}' > packs/steam/packages.json; echo 'linear' > packs/linear/.claude/agent.md; echo 1 > packages/com.yunusburkut.gamekit/v
g add -A; g commit -qm 'start'; g tag -a gamekit-v0.1.0 -m k; g push -q --tags origin main 2>/dev/null
B0=$(g rev-parse --short HEAD)

# the game new-game.ps1 would make from it
at 2026-01-02
mkdir "$W/game"; cp -r project/. "$W/game/"; cp -r packs/steam/Assets "$W/game/"
cd "$W/game"; mv Assets/__GAME__/Core/__GAME__.Core.asmdef Assets/__GAME__/Core/Foo.Core.asmdef; mv Assets/__GAME__ Assets/Foo
sed -i 's/__GAME__/Foo/g' Assets/Foo/Core/Foo.Core.asmdef Assets/Foo/Game/Steam.cs; rm -rf ProjectSettings
echo 'Unity -gameCompany Acme' > README.md
g init -q; g add -A; g commit -qm "Start Foo from unity-game-template@$B0"
# a second game with no marker commit (made before the marker existed), for the date fallback
cp -r "$W/game" "$W/game2"; (cd "$W/game2"; g commit -q --amend -m "first")
# the game's own edit, which template commit D conflicts with
sed -i 's/^eight$/game8/' notes.txt; g commit -qam "game edit"

# template commits after it: A (taken), B (skipped, same file as A), C (settings + GameKit release),
# D (taken, conflicts with the game's edit, and a pack README change that only `excluded` reports)
at 2026-01-03; cd "$W/t"
sed -i 's/^one$/ONE/' project/notes.txt; echo '// __GAME__ by __COMPANY__' >> packs/steam/Assets/__GAME__/Game/Steam.cs
echo 'linear 2' >> packs/linear/.claude/agent.md; g commit -qam 'A: take'; A=$(g rev-parse --short HEAD)
sed -i 's/^five$/FIVE/' project/notes.txt; echo new > project/skipped.txt; g add -A; g commit -qm 'B: skip'
echo 2 > packages/com.yunusburkut.gamekit/v; g commit -qam 'gamekit: 0.2.0'; g tag -a gamekit-v0.2.0 -m k
echo '  companyName: x' >> project/ProjectSettings/ProjectSettings.asset; manifest gamekit-v0.2.0 > project/Packages/manifest.json
g commit -qam 'C: settings and tag'; C=$(g rev-parse --short HEAD)
sed -i 's/^eight$/EIGHT/' project/notes.txt; echo more >> packs/steam/README.md; g commit -qam 'D: conflict'
D=$(g rev-parse --short=7 HEAD); g push -q --tags origin main 2>/dev/null; HEAD_T=$(g rev-parse --short HEAD)

cd "$W/game"
out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts: $out"
echo "$out" | grep -q "game=Foo company=Acme base=$B0 (marker) template=$HEAD_T" || fail "facts line: $out"
echo "$out" | grep -q 'packs=steam gamekit=gamekit-v0.1.0 -> gamekit-v0.2.0' || fail "packs/tag line: $out"
[ "$(echo "$out" | grep -c ': ')" -ge 5 ] || fail "commit list: $out"

# a wrong or repeated sha is refused before anything is applied
! bash "$SYNC" patch "$A" "$B0" 2>/dev/null || fail "a sha outside BASE..origin/main was accepted"
! bash "$SYNC" patch "$A" "$A" 2>/dev/null || fail "a sha named twice was accepted"
[ "$(sed -n 1p notes.txt)" = one ] || fail "a refused patch changed the tree"

out=$(bash "$SYNC" patch "$A" "$C" "$D") || fail "patch: $out"
# C touches only held paths (ProjectSettings, Packages/manifest.json); D's pack README hunk must not reach README.md
echo "$out" | grep -q "C: settings and tag: nothing patchable" || fail "held-only commit patched: $out"
grep -q '#gamekit-v0.1.0"' Packages/manifest.json || fail "manifest patched as text"
[ ! -e ProjectSettings ] || fail "ProjectSettings patched as text"
[ "$(cat README.md)" = 'Unity -gameCompany Acme' ] || fail "pack README hunk leaked into README.md"
[ "$(sed -n 1p notes.txt)" = ONE ] || fail "taken hunk missing"
[ "$(sed -n 5p notes.txt)" = five ] || fail "skipped commit's hunk applied"
[ ! -e skipped.txt ] || fail "skipped commit's file added"
grep -q '^// Foo by Acme$' Assets/Foo/Game/Steam.cs || fail "pack hunk or placeholders: $(cat Assets/Foo/Game/Steam.cs)"
[ ! -e .claude/agent.md ] || fail "a pack the game lacks was patched"
! grep -rq '__GAME__\|__COMPANY__' Assets notes.txt || fail "placeholder left"
# the conflicting hunk: kept out of the file, saved as a reject named after its commit
[ "$(sed -n 8p notes.txt)" = game8 ] || fail "conflicting hunk overwrote the game's edit"
echo "$out" | grep -q "REJECT ./notes.txt.$D.rej" && [ -f "notes.txt.$D.rej" ] || fail "per-commit reject: $out"
! bash "$SYNC" patch "$A" 2>/dev/null || fail "patch ran over old .rej files"
rm "notes.txt.$D.rej"

out=$(bash "$SYNC" excluded)
echo "$out" | grep -q 'project/ProjectSettings/ProjectSettings.asset' || fail "excluded list: $out"
echo "$out" | grep -q 'packs/steam/README.md' || fail "pack README missing from excluded: $out"
out=$(bash "$SYNC" tag); echo "$out" | grep -q 'gamekit-v0.1.0 -> gamekit-v0.2.0' || fail "tag output"
grep -q '#gamekit-v0.2.0"' Packages/manifest.json || fail "manifest tag not moved"
grep -q '"com.unity.ugui": "2.6.0"' Packages/manifest.json || fail "manifest other lines changed"

# a later commit whose body quotes the marker, even at a line start, must not move BASE
g add -A; g commit -qm "template: sync to unity-game-template@$HEAD_T" -m "Packs: steam, linear"
g commit -q --allow-empty -m 'fix' -m "see unity-game-template@$B0" -m "template: sync to unity-game-template@$B0"
# facts from before the sync commit are stale
! bash "$SYNC" patch "$A" 2>/dev/null || fail "patch ran on facts taken before HEAD moved"
out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts after sync: $out"
echo "$out" | grep -q "base=$HEAD_T (marker)" || fail "base after sync: $out"
echo "$out" | grep -q "packs=steam  *linear gamekit" || fail "Packs: line ignored: $out"

# tag: a newer hand-set tag is never downgraded, a file: entry is left, an unpushed tag is refused
sed -i 's/#gamekit-v0.2.0"/#gamekit-v0.10.0"/' Packages/manifest.json; g commit -qam 'gamekit ahead'
TEMPLATE="$W/t" bash "$SYNC" facts >/dev/null; out=$(bash "$SYNC" tag)
echo "$out" | grep -q 'gamekit-v0.10.0 is newer' && grep -q '#gamekit-v0.10.0"' Packages/manifest.json || fail "tag downgraded: $out"
sed -i 's|"https://[^"]*#gamekit-v0.10.0"|"file:../gamekit"|' Packages/manifest.json; g commit -qam 'gamekit local'
TEMPLATE="$W/t" bash "$SYNC" facts >/dev/null; out=$(bash "$SYNC" tag)
echo "$out" | grep -q 'file: entry' && grep -q '"file:../gamekit"' Packages/manifest.json || fail "file: entry: $out"
g checkout -q HEAD~1 -- Packages/manifest.json; sed -i 's/#gamekit-v0.10.0"/#gamekit-v0.2.0"/' Packages/manifest.json; g commit -qam 'gamekit back'
cd "$W/t"; manifest gamekit-v0.3.0 > project/Packages/manifest.json; g commit -qam 'E: unpushed tag'; g tag -a gamekit-v0.3.0 -m k
g push -q origin main 2>/dev/null; cd "$W/game"
TEMPLATE="$W/t" bash "$SYNC" facts >/dev/null
! bash "$SYNC" tag 2>/dev/null || fail "an unpushed tag was accepted"
grep -q '#gamekit-v0.2.0"' Packages/manifest.json || fail "manifest changed by a refused tag"

# a game without a marker commit: BASE from its first commit's date, packs from the files present
cd "$W/game2"; out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts without marker: $out"
echo "$out" | grep -q "base=$B0 (date of the game's first commit" || fail "date fallback base: $out"
echo "$out" | grep -q 'pack steam: 1/1 files present' || fail "pack presence count: $out"
echo "$out" | grep -q 'packs=steam gamekit' || fail "packs from presence: $out"

# a start marker from a dirty template: the base holds, and the files it does not describe are listed
g commit -q --allow-empty -m "Start Foo from unity-game-template@$B0-dirty" \
  -m "The template had uncommitted changes under project/, packs/ or new-game.ps1:
 M project/notes.txt"
out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts with a dirty marker: $out"
echo "$out" | grep -q "base=$B0 (marker)" && echo "$out" | grep -q '^DIRTY:' && echo "$out" | grep -q '^ M project/notes.txt$' ||
  fail "dirty marker: $out"
echo "sync.sh: all checks passed"
