#!/usr/bin/env bash
# Fixture test for survey.sh: builds a throwaway game repo with one known hit per section and checks
# the survey prints each one (and nothing from Prototypes or Tests), first with --all, then in the
# default ledger mode (CRLF ledger, a modified and an untracked file) and with an unknown ref.
# Deterministic, needs only git and bash; run under Git Bash:
#   bash plugin/skills/refactor-pass/scripts/test-survey.sh
# Exit 0 = all checks passed, 1 = a check failed (each failure is printed).

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAIL=0

G="$TMP/Assets/Fixture"
mkdir -p "$G/Core" "$G/Game" "$G/Editor" "$G/Prototypes/Spike" "$G/Tests"
echo '{ "name": "Fixture.Core" }' > "$G/Core/Fixture.Core.asmdef"

cat > "$G/Game/Literal.cs" <<'CS'
[DefaultExecutionOrder(-100)]
public sealed class Literal : MonoBehaviour
{
    static int s_Count;
    static readonly int Fixed = 1;
    static readonly List<int> s_Live = new List<int>();
    static Vector3 s_V;
    static int? s_N;
    protected internal static int s_P;
    private static Dictionary<int, Vector2> s_Map = new();
    static System.Action s_A;
    static readonly Vector3 Up = Vector3.up;
    static readonly int? NoBest = null;
    void Update() { var body = GetComponent<Rigidbody>(); var cam = Camera.main; renderer.materials[0].color = c; }
}
CS
cat > "$G/Game/Symbolic.cs" <<'CS'
[DefaultExecutionOrder(Order.Input)]
public sealed class Symbolic : MonoBehaviour { }
CS
cat > "$G/Game/Named.cs" <<'CS'
[DefaultExecutionOrder(order: 50)]
public sealed class Named : MonoBehaviour { }
CS
cat > "$G/Game/OldInput.cs" <<'CS'
bool held = Input.GetKey(KeyCode.A);
Vector3 at = Input.mousePosition;
if (Input.anyKeyDown) { }
var keyboard = UnityEngine.InputSystem.Keyboard.current; PlayerInput pi; InputAction a;
CS
# One line per name in unity-code-review SKILL.md item 11; add a line here when a rename is added there.
cat > "$G/Game/Obsolete.cs" <<'CS'
body.velocity = v;
body.drag = 1f;
body.angularDrag = 1f;
PhysicMaterial m;
PhysicMaterialCombine combine;
FindObjectOfType<Foo>();
FindObjectsOfType<Foo>();
FindFirstObjectByType<Foo>();
FindObjectsByType<Foo>(FindObjectsSortMode.None);
GetInstanceID();
EditorUtility.InstanceIDToObject(id);
CinemachineVirtualCamera vcam;
CinemachineTransposer t;
CinemachineFramingTransposer ft;
CinemachineComposer c;
CinemachineFreeLook fl;
vcam.m_Follow = t;
using Cinemachine;
CinemachineOrbitalTransposer ot;
CinemachinePOV pov;
CinemachineTrackedDolly td;
CinemachineCollider col;
vcam.m_LookAt = t;
vcam.m_Lens = lens;
public override void OnCameraSetup(CommandBuffer cmd, ref RenderingData data) { }
public override void Execute(ScriptableRenderContext context, ref RenderingData data) { }
var target = renderer.cameraColorTargetHandle;
var www = new WWW(url);
Application.LoadLevel(1);
CS
# Editor code: obsolete API is reported without --editor, the per-frame smells are not.
cat > "$G/Editor/Tool.cs" <<'CS'
var all = FindObjectsOfType<Foo>();
var body = GetComponent<Rigidbody>();
CS
cat > "$G/Tests/LiteralTests.cs" <<'CS'
var cam = Camera.main;
CS
cat > "$G/Prototypes/Spike/Spike.cs" <<'CS'
public sealed class Spike : MonoBehaviour { void Update() { var cam = Camera.main; } }
CS

git -C "$TMP" init -q
OUT="$(cd "$TMP" && bash "$HERE/survey.sh" --all 2>&1)"
STATUS=$?

check() { # label, fixed string that must appear
  if ! printf '%s\n' "$OUT" | grep -qF -- "$2"; then echo "FAIL: $1 (missing: $2)"; FAIL=1; fi
}
refuse() { # label, fixed string that must not appear
  if printf '%s\n' "$OUT" | grep -qF -- "$2"; then echo "FAIL: $1 (present: $2)"; FAIL=1; fi
}
section() { # header prefix -> the lines under it, up to the next blank line
  printf '%s\n' "$OUT" | awk -v h="$1" 'index($0, h) == 1 {on=1; next} on && /^$/ {on=0} on'
}

[ "$STATUS" -eq 0 ] || { echo "FAIL: survey.sh --all exited $STATUS"; FAIL=1; }
check  'literal order sorted'        "  -100  Assets/Fixture/Game/Literal.cs"
check  'named-argument order sorted' "    50  Assets/Fixture/Game/Named.cs"
check  'symbolic order listed apart' "symbolic order: resolve by hand"
check  'symbolic order value'        "Order.Input  Assets/Fixture/Game/Symbolic.cs"
check  'mutable static'              "Assets/Fixture/Game/Literal.cs:4:"
refuse 'readonly scalar static'      "Assets/Fixture/Game/Literal.cs:5:"
check  'readonly collection static'  "Assets/Fixture/Game/Literal.cs:6:    static readonly List<int> s_Live = new List<int>();   <- readonly reference, mutable contents"
for n in 7 8 9 10 11; do
  check "mutable static line $n"     "Assets/Fixture/Game/Literal.cs:$n:"
done
refuse 'readonly Vector3 static'     "Assets/Fixture/Game/Literal.cs:12:"
refuse 'readonly nullable static'    "Assets/Fixture/Game/Literal.cs:13:"
check  'GetComponent hit'            "Assets/Fixture/Game/Literal.cs:14:"
MATS="$(section '--- renderer.material(s)')"
printf '%s\n' "$MATS" | grep -qF "Assets/Fixture/Game/Literal.cs:14:" \
  || { echo "FAIL: renderer.materials not smelled"; FAIL=1; }
refuse 'Prototypes skipped'          "Prototypes/Spike"
refuse 'Tests listed, never smelled' "Assets/Fixture/Tests/LiteralTests.cs:"
refuse 'Editor smell needs --editor' "Assets/Fixture/Editor/Tool.cs:2:"
INPUT="$(section '--- Old Input manager')"
for n in 1 2 3; do
  printf '%s\n' "$INPUT" | grep -qF "Assets/Fixture/Game/OldInput.cs:$n:" \
    || { echo "FAIL: Old Input manager line $n not matched: $(sed -n "${n}p" "$G/Game/OldInput.cs")"; FAIL=1; }
done
printf '%s\n' "$INPUT" | grep -qF "Assets/Fixture/Game/OldInput.cs:4:" \
  && { echo "FAIL: Input System types matched as Old Input manager"; FAIL=1; }
# Only the obsolete-API section counts here: several of these names also hit the scene-scan smell.
OBS="$(section '--- obsolete API')"
printf '%s\n' "$OBS" | grep -qF "Assets/Fixture/Editor/Tool.cs:1:" \
  || { echo "FAIL: obsolete API in Editor code not reported without --editor"; FAIL=1; }
LINES="$(wc -l < "$G/Game/Obsolete.cs")"
for n in $(seq 1 "$LINES"); do
  printf '%s\n' "$OBS" | grep -qF "Assets/Fixture/Game/Obsolete.cs:$n:" \
    || { echo "FAIL: obsolete API line $n not matched: $(sed -n "${n}p" "$G/Game/Obsolete.cs")"; FAIL=1; }
done

# Default mode: last-pass read from a CRLF ledger; scope = diff since it plus untracked files.
gitc() { git -C "$TMP" -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false -c core.autocrlf=false "$@"; }
gitc add -A && gitc commit -qm one
echo '// touched' >> "$G/Game/Literal.cs"
gitc commit -qam two
PASS_SHA="$(git -C "$TMP" rev-parse HEAD)"
mkdir -p "$TMP/docs"
printf '# Refactor pass log\r\nlast-pass: %s\r\n' "$PASS_SHA" > "$TMP/docs/refactor-pass-log.md"
echo 'public sealed class Extra { }' >> "$G/Game/Named.cs"
echo 'public sealed class Fresh : MonoBehaviour { void Update() { var cam = Camera.main; } }' > "$G/Game/Fresh.cs"
OUT="$(cd "$TMP" && bash "$HERE/survey.sh" 2>&1)"
STATUS=$?
[ "$STATUS" -eq 0 ] || { echo "FAIL: survey.sh (ledger mode) exited $STATUS"; FAIL=1; }
refuse 'ledger sha read through CRLF' "No usable last-pass sha"
check  'ledger sha used'              "Since: $PASS_SHA"
SCOPE="$(section '--- files (lines)')"
for f in Named.cs Fresh.cs; do
  printf '%s\n' "$SCOPE" | grep -qF "Assets/Fixture/Game/$f" \
    || { echo "FAIL: ledger mode missed $f"; FAIL=1; }
done
printf '%s\n' "$SCOPE" | grep -qF "Assets/Fixture/Game/Literal.cs" \
  && { echo "FAIL: ledger mode listed Literal.cs, committed before last-pass"; FAIL=1; }
check  'untracked file smelled'       "Assets/Fixture/Game/Fresh.cs:1:"

(cd "$TMP" && bash "$HERE/survey.sh" nosuchref >/dev/null 2>&1)
[ $? -eq 2 ] || { echo "FAIL: survey.sh nosuchref did not exit 2"; FAIL=1; }

[ "$FAIL" -eq 0 ] && echo "test-survey: all checks passed"
exit "$FAIL"
