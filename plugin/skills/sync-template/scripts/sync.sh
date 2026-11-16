#!/usr/bin/env bash
# gamekit:sync-template pipeline, run from the game's root. Each subcommand is its own Bash call, so `facts` writes
# what it found to .git/sync-template.env and every later subcommand reads it back from there.
#   facts             clean-tree check, template fetch, GAME/COMPANY/BASE/HEAD_T/PACKS/TAG; prints the commit list
#   patch <sha>...    applies only the template commits the user took, oldest first, placeholders filled in
#   excluded          template commits since BASE that touched files no patch may carry, with their paths
#   tag               moves the GameKit git tag to the one the template's manifest names
# TEMPLATE overrides the template checkout (default /c/GitHub/unity-game-template).
set -euo pipefail

ENV="$(git rev-parse --git-dir)/sync-template.env"
die() { echo "sync-template: $*" >&2; exit 1; }
# facts are only valid for the HEAD they were taken at: a sync commit (or any other) since then means a stale BASE
load() {
  [ -f "$ENV" ] || die "run 'facts' first"; . "$ENV"
  [ "$(git rev-parse HEAD)" = "${GHEAD:-}" ] || die "HEAD moved since 'facts' (a sync already recorded?): run facts again"
}
# a replacement text safe for sed: & / and \ escaped
sedesc() { printf '%s' "$1" | sed 's/[&/\]/\\&/g'; }
# the GameKit tag a manifest names; empty for a file: entry or no GameKit
manifest_tag() { sed -n 's/.*"com\.yunusburkut\.gamekit": *"[^"]*#\(gamekit-v[0-9][0-9.]*\)".*/\1/p'; }

cmd_facts() {
  [ "$(git symbolic-ref --short -q HEAD)" = main ] || die "not on main"
  [ -z "$(git status --short)" ] || die "working tree not clean; commit or stash first"
  T="${TEMPLATE:-/c/GitHub/unity-game-template}"
  [ -d "$T/.git" ] || die "no template checkout at $T; set TEMPLATE (never clone over one)"
  git -C "$T" fetch -q --tags origin
  local d g; GAME=""
  for d in Assets/*/; do g=$(basename "$d"); [ -f "Assets/$g/Core/$g.Core.asmdef" ] && { GAME=$g; break; }; done
  [ -n "$GAME" ] || die "no Assets/<Game>/Core/<Game>.Core.asmdef: not a template game"
  COMPANY=$(sed -n 's/^  companyName: //p' ProjectSettings/ProjectSettings.asset 2>/dev/null || true)
  # before the first ProjectSetup run there is no ProjectSettings.asset; the game's README carries the company
  [ -n "$COMPANY" ] || COMPANY=$(sed -n 's/.*-gameCompany \([A-Za-z0-9]*\).*/\1/p' README.md 2>/dev/null | sed -n 1p || true)
  # the sync point: only the two subjects this pipeline writes count, so a body that quotes the marker does not
  # (git's --grep anchors ^ at every message line, so the commit is picked by its subject here)
  local marker="" msha
  msha=$(git log --format='%H %s' | grep -m1 -E '^[0-9a-f]+ (Start .* from|template: sync to) unity-game-template@[0-9a-f]{7,}' | cut -d' ' -f1 || true)
  [ -z "$msha" ] || marker=$(git log -1 --format=%B "$msha")
  BASE=$(printf '%s\n' "${marker%%$'\n'*}" | sed -n 's/.*unity-game-template@\([0-9a-f]\{7,\}\).*/\1/p')
  # new-game.ps1 marks a copy of a template with uncommitted edits as @<sha>-dirty and lists those files in the body
  local dirty=""
  case "${marker%%$'\n'*}" in *unity-game-template@*-dirty*)
    dirty=$(printf '%s\n' "$marker" | sed -n '/^The template had uncommitted/,$p' | sed 1d) ;; esac
  BASE_FROM=marker
  if [ -z "$BASE" ]; then
    # games made before the marker existed: the template's last main commit before the game's first commit
    BASE=$(git -C "$T" rev-list -1 --before="$(git log --reverse --format=%cI | head -1)" origin/main)
    BASE_FROM="date of the game's first commit (no marker commit): confirm with the user"
  fi
  git -C "$T" cat-file -e "$BASE^{commit}" 2>/dev/null || die "base $BASE is not in the template (an unpushed template commit?)"
  BASE=$(git -C "$T" rev-parse --short "$BASE")
  HEAD_T=$(git -C "$T" rev-parse --short origin/main)
  # packs: the start commit's "Packs:" line when it has one; otherwise each pack whose files at BASE exist here
  # (counting only what new-game.ps1 copies: not README.md, packages.json or examples/, as in held())
  PACKS=$(printf '%s\n' "$marker" | sed -n 's/^Packs: *//p' | tr ',' ' ')
  local p f have total
  if [ -z "$PACKS" ]; then
    for p in $(git -C "$T" ls-tree --name-only "$BASE" packs/ | sed 's|^packs/||'); do
      have=0; total=0
      while IFS= read -r f; do
        total=$((total + 1)); f="${f#packs/$p/}"; [ -e "${f//__GAME__/$GAME}" ] && have=$((have + 1))
      done < <(git -C "$T" ls-tree -r --name-only "$BASE" -- "packs/$p" |
               grep -v -e "^packs/$p/README.md$" -e "^packs/$p/packages.json$" -e "^packs/$p/examples/")
      [ "$total" -gt 0 ] && echo "pack $p: $have/$total files present"
      [ "$have" -gt 0 ] && PACKS="$PACKS $p"
    done
  fi
  PACKS="${PACKS# }"
  OLD_TAG=$(manifest_tag < Packages/manifest.json)
  TAG=$(git -C "$T" show origin/main:project/Packages/manifest.json | manifest_tag)
  printf 'T=%q\nGAME=%q\nCOMPANY=%q\nBASE=%q\nHEAD_T=%q\nPACKS=%q\nOLD_TAG=%q\nTAG=%q\nGHEAD=%q\n' \
    "$T" "$GAME" "$COMPANY" "$BASE" "$HEAD_T" "$PACKS" "$OLD_TAG" "$TAG" "$(git rev-parse HEAD)" > "$ENV"
  echo "game=$GAME company=$COMPANY base=$BASE ($BASE_FROM) template=$HEAD_T"
  echo "packs=${PACKS:-none} gamekit=${OLD_TAG:-none or file:} -> ${TAG:-none}"
  [ -z "$dirty" ] || printf 'DIRTY: copied from a template with uncommitted edits; base does not describe these files:\n%s\n' "$dirty"
  [ -n "$COMPANY" ] || echo "WARNING: company not found; __COMPANY__ would stay unfilled: ask the user" >&2
  git -C "$T" log --oneline "$BASE..origin/main" -- project packs packages/com.yunusburkut.gamekit
}

# The one list of template paths no patch carries (glob pathspecs). diff_one leaves them out and `excluded` lists the
# commits that touched them, so the agent hands each over by other means. The pack entries mirror what new-game.ps1
# does at copy time: README.md and packages.json are never copied (new-game.ps1 lifts the README's CLAUDE.md block or
# section and merges packages.json into the manifest); keep both in step when new-game.ps1 gains a copy-time exception.
held() {
  local p
  HELD=('project/ProjectSettings/**' 'project/Packages/**' 'project/**/*.unity' 'project/**/*.prefab' 'project/**/*.asset')
  for p in $PACKS; do
    HELD+=("packs/$p/README.md" "packs/$p/packages.json" "packs/$p/**/*.unity" "packs/$p/**/*.prefab" "packs/$p/**/*.asset")
  done
}

# the paths a patch carries: the project and the game's packs minus HELD and each pack's examples/ (never copied)
diff_one() {
  local c=$1 p
  git -C "$T" diff --binary --relative=project "$c^" "$c" -- project "${HELD[@]/#/:(exclude,glob)}"
  for p in $PACKS; do
    git -C "$T" diff --binary --relative="packs/$p" "$c^" "$c" -- "packs/$p" ":(exclude,glob)packs/$p/examples/**" \
      "${HELD[@]/#/:(exclude,glob)}"
  done
}

cmd_patch() {
  load; held
  [ $# -gt 0 ] || die "name the template commits the user took"
  local want="" range c full P rej
  range=" $(git -C "$T" rev-list "$BASE..origin/main" | tr '\n' ' ')"
  # every sha is checked before anything is applied, so a wrong one never leaves a half-patched tree
  for c in "$@"; do
    full=$(git -C "$T" rev-parse -q --verify "$c^{commit}") || die "unknown template commit $c"
    case "$range" in *" $full "*) ;; *) die "$c is not in $BASE..origin/main; nothing applied" ;; esac
    case "$want " in *" $full "*) die "$c named twice; nothing applied" ;; esac
    want="$want $full"
  done
  [ -z "$(find . -path ./Library -prune -o -name '*.rej' -print | head -1)" ] || die "old .rej files present; merge or delete them first"
  P=$(mktemp)
  # oldest first
  for c in $(git -C "$T" rev-list --reverse "$BASE..origin/main"); do
    case "$want " in *" $c "*) ;; *) continue ;; esac
    diff_one "$c" | sed "s/__GAME__/$(sedesc "$GAME")/g; s/__COMPANY__/$(sedesc "$COMPANY")/g" > "$P"
    if [ ! -s "$P" ]; then echo "$(git -C "$T" log -1 --format='%h %s' "$c"): nothing patchable (see 'excluded')"; continue; fi
    echo "== $(git -C "$T" log -1 --format='%h %s' "$c")"
    git apply --stat "$P"
    git apply --reject --whitespace=nowarn "$P" || echo "git apply reported failures for ${c:0:7}: each REJECT below; an error above with no REJECT is a file the game deleted, renamed or already has (apply that change by hand)"
    # a later commit's reject for the same file would overwrite this one: name each after its commit
    while IFS= read -r rej; do mv "$rej" "${rej%.rej}.${c:0:7}.rej"; echo "REJECT ${rej%.rej}.${c:0:7}.rej"; done \
      < <(find . -path ./Library -prune -o -name '*.rej' ! -name '*.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].rej' -print)
  done
  rm -f "$P"
}

cmd_excluded() {
  load; held
  git -C "$T" log --format='== %h %s' --name-only "$BASE..origin/main" -- "${HELD[@]/#/:(glob)}"
}

cmd_tag() {
  load
  [ -n "$TAG" ] || die "the template's manifest names no GameKit tag"
  if [ -z "$OLD_TAG" ]; then
    grep -q '"com.yunusburkut.gamekit"' Packages/manifest.json && echo "GameKit is a file: entry (a local experiment): left as it is" \
      || echo "no GameKit in this game: see 'Moving a game made before GameKit'"
    return 0
  fi
  [ "$OLD_TAG" = "$TAG" ] && { echo "GameKit already at $TAG"; return 0; }
  # a game moved ahead by hand (a fix tested before the template's pin caught up) is never downgraded
  [ "$(printf '%s\n%s\n' "${OLD_TAG#gamekit-v}" "${TAG#gamekit-v}" | sort -V | tail -1)" = "${TAG#gamekit-v}" ] ||
    { echo "GameKit $OLD_TAG is newer than the template's $TAG: left as it is"; return 0; }
  [ -n "$(git -C "$T" ls-remote --tags origin "refs/tags/$TAG")" ] || die "$TAG is not pushed to the template's origin"
  sed -i "s|#$OLD_TAG\"|#$TAG\"|" Packages/manifest.json
  echo "GameKit $OLD_TAG -> $TAG"
  git -C "$T" log --oneline "$OLD_TAG..$TAG" -- packages/com.yunusburkut.gamekit
}

case "${1:-}" in
  facts) cmd_facts ;;
  patch) shift; cmd_patch "$@" ;;
  excluded) cmd_excluded ;;
  tag) cmd_tag ;;
  *) die "usage: sync.sh facts | patch <sha>... | excluded | tag" ;;
esac
