#!/usr/bin/env bash
# Survey for the refactor-pass skill.
#
#   survey.sh                 scope = commits since `last-pass:` in docs/refactor-pass-log.md
#   survey.sh <git-ref>       scope = commits since <git-ref>
#   survey.sh --all           scope = every .cs under the game folder (Editor and Tests included)
#   survey.sh ... --editor    include the game's Editor folder in the smell grep (readability only)
#
# The game folder is the one under Assets/ that holds the *.Core.asmdef (Assets/<Game>), found at
# run time so the script needs no renaming. Prints, in order: the scope (commits + files), the
# execution-order pipeline, mutable statics, platform branches, and per-frame smell hits. Hits are
# questions for the reader — grep cannot see which method a line sits in. Runs under Git Bash on
# Windows; needs only git, find and grep.

set -u
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1

LEDGER="docs/refactor-pass-log.md"
CORE_ASMDEF="$(find Assets -maxdepth 4 -name '*.Core.asmdef' -not -path 'Assets/Feel/*' -not -path 'Assets/Plugins/*' 2>/dev/null | head -1)"
if [ -z "$CORE_ASMDEF" ]; then
  echo "No *.Core.asmdef under Assets/; run from the game repository." >&2
  exit 2
fi
ROOT="$(dirname "$(dirname "$CORE_ASMDEF")")"   # Assets/<Game>/Core/<Game>.Core.asmdef -> Assets/<Game>
ALL=0
EDITOR=0
REF=""

for arg in "$@"; do
  case "$arg" in
    --all) ALL=1 ;;
    --editor) EDITOR=1 ;;
    *) REF="$arg" ;;
  esac
done

# An explicit ref that does not resolve is a typo, not a reason to survey something else.
if [ -n "$REF" ] && ! git rev-parse --verify --quiet "$REF^{commit}" >/dev/null; then
  echo "Unknown ref: $REF" >&2
  exit 2
fi

if [ "$ALL" -eq 0 ] && [ -z "$REF" ]; then
  if [ -f "$LEDGER" ]; then
    REF="$(grep -m1 -E '^last-pass:' "$LEDGER" | sed -E 's/^last-pass:[[:space:]]*//; s/[[:space:]]*$//' | tr -d '\r')"
  fi
  # 15 commits is an arbitrary "recent work" window, used only when the ledger has no usable sha
  # (the first pass creates the ledger); pass an explicit ref when it is the wrong size.
  if [ -z "$REF" ] || ! git rev-parse --verify --quiet "$REF^{commit}" >/dev/null; then
    COUNT="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
    if [ "$COUNT" -gt 15 ]; then REF="HEAD~15"; else REF="$(git rev-list --max-parents=0 HEAD | tail -1)"; fi
    echo "No usable last-pass sha in $LEDGER; falling back to $REF." >&2
  fi
fi

echo "================ SCOPE  ($ROOT)"
if [ "$ALL" -eq 1 ]; then
  echo "Whole tree: $ROOT"
  FILES="$(find "$ROOT" -name '*.cs' | sort)"
else
  echo "Since: $REF  ($(git rev-parse --short "$REF" 2>/dev/null))"
  echo
  echo "--- commits"
  git log --oneline "$REF..HEAD" -- "$ROOT" | sed 's/^/  /'
  echo
  # Ref against the working tree, so uncommitted edits count; renames list their new path and
  # untracked files come one by one, never as a bare directory.
  FILES="$( { git diff --name-only --diff-filter=AMR "$REF" -- "$ROOT"; \
              git ls-files --others --exclude-standard -- "$ROOT"; } | grep -E '\.cs$' | sort -u || true)"
fi

FILES="$(printf '%s\n' "$FILES" | grep -v '^$' || true)"
if [ -z "$FILES" ]; then
  echo "  (no .cs files in scope)"
  exit 0
fi

echo "--- files (lines)"
printf '%s\n' "$FILES" | while read -r f; do
  [ -f "$f" ] && printf '  %5d  %s\n' "$(wc -l < "$f")" "$f"
done

# Runtime scope for the smell grep: drop Tests always, Editor unless asked, deleted files always.
RUNTIME="$(printf '%s\n' "$FILES" | grep -v "$ROOT/Tests/" || true)"
if [ "$EDITOR" -eq 0 ]; then RUNTIME="$(printf '%s\n' "$RUNTIME" | grep -v "$ROOT/Editor/" || true)"; fi
RUNTIME="$(printf '%s\n' "$RUNTIME" | while read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done)"

echo
echo "================ EXECUTION ORDER (whole Game assembly)"
if [ -d "$ROOT/Game" ]; then
  grep -rn --include='*.cs' -E '\[DefaultExecutionOrder\(' "$ROOT/Game" \
    | sed -E 's/^([^:]+):([0-9]+):.*DefaultExecutionOrder\(([-0-9]+)\).*/\3\t\1/' \
    | sort -n | awk -F'\t' '{printf "  %6s  %s\n", $1, $2}'
fi
echo "  (unlisted MonoBehaviours run at 0)"

if [ -z "$RUNTIME" ]; then
  echo
  echo "No runtime files in scope; smell grep skipped."
  exit 0
fi

# grep helper: pattern, label, [exclude pattern]. Strips comment-only lines so doc comments do
# not trigger; the optional third argument drops known-benign shapes for that smell.
smell() {
  local pattern="$1" label="$2" exclude="${3:-}" hits
  hits="$(printf '%s\n' "$RUNTIME" | tr '\n' '\0' | xargs -0 grep -nH -E "$pattern" 2>/dev/null \
          | grep -vE '^[^:]+:[0-9]+:[[:space:]]*(//|/\*|\*)' || true)"
  if [ -n "$exclude" ] && [ -n "$hits" ]; then
    hits="$(printf '%s\n' "$hits" | grep -vE "$exclude" || true)"
  fi
  if [ -n "$hits" ]; then
    echo
    echo "--- $label"
    printf '%s\n' "$hits" | sed 's/^/  /'
  fi
}

echo
echo "================ MUTABLE STATICS (need a SubsystemRegistration reset unless readonly/const)"
printf '%s\n' "$RUNTIME" | tr '\n' '\0' | xargs -0 grep -nH -E '^\s*(public|private|protected|internal)?\s*static\s+[][A-Za-z_<>, ]+\s+[A-Za-z_][A-Za-z0-9_]*\s*(=([^>=]|$)|;|\{)' 2>/dev/null \
  | grep -vE 'readonly|const|static\s+(void|class|bool|int|float|string|[A-Za-z<>]+)\s+[A-Za-z_]+\s*\(' \
  | sed 's/^/  /' || true

echo
echo "================ PLATFORM (works on one target only — see platform-targets)"
smell 'Mouse\.current|Touchscreen\.current|Keyboard\.current'          'Device reads — gameplay binds <Pointer> actions; Keyboard only as a PC extra or the Android back key'
smell 'UnityEngine\.Input\.|\bInput\.(GetKey|GetMouse|GetAxis|GetButton|GetTouch|touches|touchCount|mousePosition)' 'Old Input manager — switched off, throws at runtime'
smell '#if\s+.*UNITY_(ANDROID|IOS|STANDALONE|WEBGL)'                   'Platform branches — a real platform API only, never a rule'
smell 'OnApplicationQuit'                                                'OnApplicationQuit — phones rarely call it; save in OnApplicationPause(true)'
smell 'Application\.Quit\('                                              'Application.Quit — never on iOS'

echo
echo "================ SMELL HITS (read the enclosing method before acting)"
smell 'GetComponent(s)?(InChildren|InParent)?<'                         'GetComponent family — fine in Awake, cache elsewhere'
smell 'FindFirstObjectByType|FindAnyObjectByType|FindObjectsByType|GameObject\.Find|FindWithTag|Camera\.main' 'Scene scans / Camera.main — Inspector reference instead'
smell '\.tag\s*(==|!=)'                                                  'tag compare — CompareTag'
smell '\.material\b'                                                     'renderer.material — instantiates; use sharedMaterial / MaterialPropertyBlock'
smell '\$"|string\.Format\(|string\.Concat\(|\+\s*"|"\s*\+'              'String building — allocation if per frame (attribute text and const literals already dropped)' \
      '\[(Tooltip|Header|CreateAssetMenu|MenuItem)\(|const\s+string|^[^:]+:[0-9]+:[[:space:]]*"'
smell 'new (List|Dictionary|HashSet|Queue|Stack)<|new [A-Z][A-Za-z0-9_]*\[[^]]*\]' 'Collection / array construction — hoist to a field if per frame'
smell 'using System\.Linq|\.(Select|Where|ToList|ToArray|Any|First|FirstOrDefault|OrderBy|Sum|Count)\(' 'LINQ — banned in hot paths'
smell 'foreach\s*\('                                                     'foreach — fine over arrays/List<T>, boxes over interfaces'
smell 'StartCoroutine|new WaitForSeconds|yield return'                   'Coroutines — prefer Update timers; cache WaitForSeconds if one stays'
smell 'Debug\.Log(Warning)?\('                                           'Debug.Log in runtime code — remove or gate'
smell 'Instantiate\(|Destroy\('                                          'Instantiate / Destroy — pooling question only if it recurs during play'
smell 'Invoke\("|SendMessage\(|BroadcastMessage\('                       'String-dispatched calls'
smell '[\(,=]\s*(\(\)|\(?[a-zA-Z_][a-zA-Z0-9_]*\)?)\s*=>'                  'Lambdas (not expression-bodied members) — display-class allocation if in a per-frame path'
smell 'Physics(2D)?\.(Raycast|SphereCast|BoxCast|CapsuleCast|OverlapSphere|OverlapBox|OverlapCapsule|OverlapCircle|OverlapPoint)\(' 'Physics queries — confirm NonAlloc / preallocated buffer'
smell 'Time\.deltaTime'                                                  'deltaTime reads — SimulationStep.Delta where a simulation steps?'
smell '\bin\s+[A-Z][A-Za-z]*Tuning\b'                                    'in-tuning parameters — every computed member on the struct must be readonly'
smell '\.(velocity|drag|angularDrag)\b|\bPhysicMaterial\b|FindObjectsOfType|FindObjectOfType|FindFirstObjectByType|FindObjectsSortMode|GetInstanceID|InstanceIDToObject|CinemachineVirtualCamera|OnCameraSetup|Execute\(ScriptableRenderContext' 'obsolete API, pre-Unity-6 or obsoleted by 6000.6 (.velocity/.drag only on Rigidbody/Rigidbody2D; CharacterController/NavMeshAgent .velocity are fine) — see unity-code-review item 11'

echo
echo "================ DONE"
echo "Next: read every file in scope in full, then references/refactor-catalog.md."
