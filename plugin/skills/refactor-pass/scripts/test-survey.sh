#!/usr/bin/env bash
# Fixture test for survey.sh: builds a throwaway game repo with one known hit per section and checks
# the survey prints each one (and nothing from Prototypes). Deterministic, needs only git and bash;
# run under Git Bash:  bash plugin/skills/refactor-pass/scripts/test-survey.sh
# Exit 0 = all checks passed, 1 = a check failed (each failure is printed).

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAIL=0

G="$TMP/Assets/Fixture"
mkdir -p "$G/Core" "$G/Game" "$G/Prototypes/Spike" "$G/Tests"
echo '{ "name": "Fixture.Core" }' > "$G/Core/Fixture.Core.asmdef"

cat > "$G/Game/Literal.cs" <<'EOF'
[DefaultExecutionOrder(-100)]
public sealed class Literal : MonoBehaviour
{
    static int s_Count;
    static readonly int Fixed = 1;
    void Update() { var body = GetComponent<Rigidbody>(); var cam = Camera.main; }
}
EOF
cat > "$G/Game/Symbolic.cs" <<'EOF'
[DefaultExecutionOrder(Order.Input)]
public sealed class Symbolic : MonoBehaviour { }
EOF
cat > "$G/Game/Named.cs" <<'EOF'
[DefaultExecutionOrder(order: 50)]
public sealed class Named : MonoBehaviour { }
EOF
# One line per name in unity-code-review SKILL.md item 11; add a line here when a rename is added there.
cat > "$G/Game/Obsolete.cs" <<'EOF'
body.velocity = v;
body.drag = 1f;
body.angularDrag = 1f;
PhysicMaterial m;
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
public override void OnCameraSetup(CommandBuffer cmd, ref RenderingData data) { }
public override void Execute(ScriptableRenderContext context, ref RenderingData data) { }
var target = renderer.cameraColorTargetHandle;
var www = new WWW(url);
Application.LoadLevel(1);
EOF
cat > "$G/Prototypes/Spike/Spike.cs" <<'EOF'
public sealed class Spike : MonoBehaviour { void Update() { var cam = Camera.main; } }
EOF

git -C "$TMP" init -q
OUT="$(cd "$TMP" && bash "$HERE/survey.sh" --all 2>&1)"
STATUS=$?

check() { # label, fixed string that must appear
  if ! printf '%s\n' "$OUT" | grep -qF -- "$2"; then echo "FAIL: $1 (missing: $2)"; FAIL=1; fi
}
refuse() { # label, fixed string that must not appear
  if printf '%s\n' "$OUT" | grep -qF -- "$2"; then echo "FAIL: $1 (present: $2)"; FAIL=1; fi
}

[ "$STATUS" -eq 0 ] || { echo "FAIL: survey.sh exited $STATUS"; FAIL=1; }
check  'literal order sorted'        "  -100  Assets/Fixture/Game/Literal.cs"
check  'named-argument order sorted' "    50  Assets/Fixture/Game/Named.cs"
check  'symbolic order listed apart' "symbolic order: resolve by hand"
check  'symbolic order value'        "Order.Input  Assets/Fixture/Game/Symbolic.cs"
check  'mutable static'              "Assets/Fixture/Game/Literal.cs:4:"
refuse 'readonly static'             "Assets/Fixture/Game/Literal.cs:5:"
check  'GetComponent hit'            "Assets/Fixture/Game/Literal.cs:6:"
refuse 'Prototypes skipped'          "Prototypes/Spike"
# Only the obsolete-API section counts here: several of these names also hit the scene-scan smell.
OBS="$(printf '%s\n' "$OUT" | awk '/^--- obsolete API/{on=1; next} on&&/^$/{on=0} on')"
LINES="$(wc -l < "$G/Game/Obsolete.cs")"
for n in $(seq 1 "$LINES"); do
  printf '%s\n' "$OBS" | grep -qF "Assets/Fixture/Game/Obsolete.cs:$n:" \
    || { echo "FAIL: obsolete API line $n not matched: $(sed -n "${n}p" "$G/Game/Obsolete.cs")"; FAIL=1; }
done

[ "$FAIL" -eq 0 ] && echo "test-survey: all checks passed"
exit "$FAIL"
