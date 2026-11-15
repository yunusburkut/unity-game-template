#!/usr/bin/env bash
# Deterministic check of sync.sh against a throwaway template and game in a temp folder (no Unity, no network).
#   bash plugin/skills/sync-template/scripts/test-sync.sh   -> "sync.sh: all checks passed" or the first failure
set -euo pipefail
SYNC="$(cd "$(dirname "$0")" && pwd)/sync.sh"
W=$(mktemp -d); trap '[ -n "${KEEP:-}" ] || rm -rf "$W"' EXIT; echo "$W" >&2
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t GIT_CONFIG_NOSYSTEM=1
fail() { echo "FAIL: $*" >&2; exit 1; }
g() { git -c core.autocrlf=false -c init.defaultBranch=main "$@"; }
manifest() { printf '{\n  "dependencies": {\n    "com.yunusburkut.gamekit": "https://example.invalid/x.git?path=/packages/com.yunusburkut.gamekit#%s",\n    "com.unity.ugui": "2.6.0"\n  }\n}\n' "$1"; }

# template at its first commit, with the steam pack (the game has it) and the linear pack (it does not)
g init -q --bare "$W/origin.git"; g clone -q "$W/origin.git" "$W/t" 2>/dev/null; cd "$W/t"
mkdir -p project/Assets/__GAME__/Core project/Packages project/ProjectSettings packs/steam/Assets/__GAME__/Game packs/linear/.claude packages/com.yunusburkut.gamekit
echo '{ "name": "__GAME__.Core" }' > project/Assets/__GAME__/Core/__GAME__.Core.asmdef
printf 'one\ntwo\nthree\nfour\nfive\n' > project/notes.txt
manifest gamekit-v0.1.0 > project/Packages/manifest.json
echo '  companyName: __COMPANY__' > project/ProjectSettings/ProjectSettings.asset
echo '// __GAME__ steam' > packs/steam/Assets/__GAME__/Game/Steam.cs
echo '{}' > packs/steam/packages.json; echo 'linear' > packs/linear/.claude/agent.md; echo 1 > packages/com.yunusburkut.gamekit/v
g add -A; g commit -qm 'start'; g tag -a gamekit-v0.1.0 -m k; g push -q --tags origin main 2>/dev/null
B0=$(g rev-parse --short HEAD)

# the game new-game.ps1 would make from it
mkdir "$W/game"; cp -r project/. "$W/game/"; cp -r packs/steam/Assets "$W/game/"
cd "$W/game"; mv Assets/__GAME__/Core/__GAME__.Core.asmdef Assets/__GAME__/Core/Foo.Core.asmdef; mv Assets/__GAME__ Assets/Foo
sed -i 's/__GAME__/Foo/g' Assets/Foo/Core/Foo.Core.asmdef Assets/Foo/Game/Steam.cs; rm -rf ProjectSettings
echo 'Unity -gameCompany Acme' > README.md
g init -q; g add -A; g commit -qm "Start Foo from unity-game-template@$B0"

# template commits after it: A (taken), B (skipped, same file as A), C (settings + GameKit release)
cd "$W/t"
sed -i 's/^one$/ONE/' project/notes.txt; echo '// __GAME__ by __COMPANY__' >> packs/steam/Assets/__GAME__/Game/Steam.cs
echo 'linear 2' >> packs/linear/.claude/agent.md; g commit -qam 'A: take'; A=$(g rev-parse --short HEAD)
sed -i 's/^five$/FIVE/' project/notes.txt; echo new > project/skipped.txt; g add -A; g commit -qm 'B: skip'
echo 2 > packages/com.yunusburkut.gamekit/v; g commit -qam 'gamekit: 0.2.0'; g tag -a gamekit-v0.2.0 -m k
echo '  companyName: x' >> project/ProjectSettings/ProjectSettings.asset; manifest gamekit-v0.2.0 > project/Packages/manifest.json
g commit -qam 'C: settings and tag'; g push -q --tags origin main 2>/dev/null; HEAD_T=$(g rev-parse --short HEAD)

cd "$W/game"
out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts: $out"
echo "$out" | grep -q "game=Foo company=Acme base=$B0 (marker) template=$HEAD_T" || fail "facts line: $out"
echo "$out" | grep -q 'packs=steam gamekit=gamekit-v0.1.0 -> gamekit-v0.2.0' || fail "packs/tag line: $out"
[ "$(echo "$out" | grep -c ': ')" -ge 4 ] || fail "commit list: $out"

bash "$SYNC" patch "$A" > /dev/null || fail "patch"
[ "$(sed -n 1p notes.txt)" = ONE ] || fail "taken hunk missing"
[ "$(sed -n 5p notes.txt)" = five ] || fail "skipped commit's hunk applied"
[ ! -e skipped.txt ] || fail "skipped commit's file added"
grep -q '^// Foo by Acme$' Assets/Foo/Game/Steam.cs || fail "pack hunk or placeholders: $(cat Assets/Foo/Game/Steam.cs)"
[ ! -e .claude/agent.md ] || fail "a pack the game lacks was patched"
! grep -rq '__GAME__\|__COMPANY__' Assets notes.txt || fail "placeholder left"

out=$(bash "$SYNC" excluded); echo "$out" | grep -q 'project/ProjectSettings/ProjectSettings.asset' || fail "excluded list"
out=$(bash "$SYNC" tag); echo "$out" | grep -q 'gamekit-v0.1.0 -> gamekit-v0.2.0' || fail "tag output"
grep -q '#gamekit-v0.2.0"' Packages/manifest.json || fail "manifest tag not moved"
grep -q '"com.unity.ugui": "2.6.0"' Packages/manifest.json || fail "manifest other lines changed"

# a later commit whose body quotes the marker must not move BASE
g add -A; g commit -qm "template: sync to unity-game-template@$HEAD_T" -m "Packs: steam, linear"; g commit -q --allow-empty -m 'fix' -m "see unity-game-template@$B0"
out=$(TEMPLATE="$W/t" bash "$SYNC" facts) || fail "facts after sync: $out"
echo "$out" | grep -q "base=$HEAD_T (marker)" || fail "base after sync: $out"
echo "$out" | grep -q "packs=steam  *linear gamekit" || fail "Packs: line ignored: $out"
echo "sync.sh: all checks passed"
