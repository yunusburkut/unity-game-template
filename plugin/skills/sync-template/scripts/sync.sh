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
load() { [ -f "$ENV" ] || die "run 'facts' first"; . "$ENV"; }
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
  local marker
  marker=$(git log -1 --format=%B -E --grep='^(Start .* from|template: sync to) unity-game-template@[0-9a-f]{7,}' || true)
  BASE=$(printf '%s\n' "${marker%%$'\n'*}" | sed -n 's/.*unity-game-template@\([0-9a-f]\{7,\}\).*/\1/p')
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
  printf 'T=%q\nGAME=%q\nCOMPANY=%q\nBASE=%q\nHEAD_T=%q\nPACKS=%q\nOLD_TAG=%q\nTAG=%q\n' \
    "$T" "$GAME" "$COMPANY" "$BASE" "$HEAD_T" "$PACKS" "$OLD_TAG" "$TAG" > "$ENV"
  echo "game=$GAME company=$COMPANY base=$BASE ($BASE_FROM) template=$HEAD_T"
  echo "packs=${PACKS:-none} gamekit=${OLD_TAG:-none or file:} -> ${TAG:-none}"
  [ -n "$COMPANY" ] || echo "WARNING: company not found; __COMPANY__ would stay unfilled: ask the user" >&2
  git -C "$T" log --oneline "$BASE..origin/main" -- project packs packages/com.yunusburkut.gamekit
}

# the paths a patch carries; everything else is listed by `excluded`
diff_one() {
  local c=$1 p
  git -C "$T" diff --binary --relative=project "$c^" "$c" -- project \
    ':(exclude)project/**/*.unity' ':(exclude)project/**/*.prefab' ':(exclude)project/**/*.asset' \
    ':(exclude)project/ProjectSettings/**' ':(exclude)project/Packages/**'
  for p in $PACKS; do
    git -C "$T" diff --binary --relative="packs/$p" "$c^" "$c" -- "packs/$p" \
      ":(exclude)packs/$p/README.md" ":(exclude)packs/$p/examples/**" ":(exclude)packs/$p/packages.json" \
      ":(exclude)packs/$p/**/*.unity" ":(exclude)packs/$p/**/*.prefab" ":(exclude)packs/$p/**/*.asset"
  done
}

cmd_patch() {
  load
  [ $# -gt 0 ] || die "name the template commits the user took"
  local want="" c full P rej n=0
  for c in "$@"; do
    full=$(git -C "$T" rev-parse -q --verify "$c^{commit}") || die "unknown template commit $c"
    want="$want $full"
  done
  [ -z "$(find . -path ./Library -prune -o -name '*.rej' -print | head -1)" ] || die "old .rej files present; merge or delete them first"
  P=$(mktemp)
  # oldest first, and only commits inside BASE..origin/main
  for c in $(git -C "$T" rev-list --reverse "$BASE..origin/main"); do
    case " $want " in *" $c "*) ;; *) continue ;; esac
    n=$((n + 1))
    diff_one "$c" | sed "s/__GAME__/$(sedesc "$GAME")/g; s/__COMPANY__/$(sedesc "$COMPANY")/g" > "$P"
    if [ ! -s "$P" ]; then echo "$(git -C "$T" log -1 --format='%h %s' "$c"): nothing patchable (see 'excluded')"; continue; fi
    echo "== $(git -C "$T" log -1 --format='%h %s' "$c")"
    git apply --stat "$P"
    git apply --reject --whitespace=nowarn "$P" || echo "git apply reported failures for ${c:0:7}: rejects below, or the message above"
    # a later commit's reject for the same file would overwrite this one: name each after its commit
    while IFS= read -r rej; do mv "$rej" "${rej%.rej}.${c:0:7}.rej"; echo "REJECT ${rej%.rej}.${c:0:7}.rej"; done \
      < <(find . -path ./Library -prune -o -name '*.rej' ! -name '*.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].rej' -print)
  done
  rm -f "$P"
  [ "$n" -eq $# ] || die "only $n of $# commits are in $BASE..origin/main"
}

cmd_excluded() {
  load
  local spec=(':(glob)project/ProjectSettings/**' ':(glob)project/Packages/**' ':(glob)project/**/*.unity'
              ':(glob)project/**/*.prefab' ':(glob)project/**/*.asset') p
  for p in $PACKS; do
    spec+=("packs/$p/packages.json" ":(glob)packs/$p/**/*.unity" ":(glob)packs/$p/**/*.prefab" ":(glob)packs/$p/**/*.asset")
  done
  git -C "$T" log --format='== %h %s' --name-only "$BASE..origin/main" -- "${spec[@]}"
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
