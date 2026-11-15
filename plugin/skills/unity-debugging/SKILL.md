---
name: unity-debugging
description: Finding a bug's root cause before changing code — it throws, works on PC but not the phone (or in the Editor but not a build), breaks only on the second Play session, or stopped working after a change. Use when a bug report, error, stack trace or "X doesn't work" arrives. A Feel feedback that does nothing is feel-troubleshooting.
---

# Debugging

Root cause first; a fix aimed at the symptom is a second bug. Play Mode cannot be driven from here
(`unity-editor-cli`), so the user runs the repro and the probes report back through the Console mirror.

## 1. Build the loop

One repro that shows *this* bug, the same way every time. In order of preference:

1. **Core seam.** Core is value types and static steps that take `dt`, so a Core bug replays deterministically as an
   EditMode test. Propose it; write or run it only with permission (`unity-testing`).
2. **Live Editor probe.** `unity command script run` reads scene, asset and component state without Play Mode;
   entering Play Mode smoke-tests `Awake` / `OnEnable` / `Start`.
3. **The user's repro, instrumented.** It names: scene or level and the exact steps; expected vs actual; PC, phone or
   WebGL; Editor or build (version or sha); first or second Play session; how often (always, mostly, sometimes, rare);
   regression or not (last good sha if known). Ask once for a missing field, then mark it `?` rather than guess. Probes
   land in `Logs/agent/console.log` (step 4), so read the result there instead of asking for a paste.
4. **Device.** A Development Build on the phone logs to `adb logcat -s Unity` (Android) or the Xcode console (iOS).
   Editor-only bugs and device-only bugs have different causes; find out which first.
5. **Regression.** Read `git log` / `git diff` for the area first. A bisect costs the user one Play Mode check per
   step: offer it, don't assume it.

If none of these shows the bug, say so, list what was tried and ask for a recording, the Console text or a device log.
No loop, no theory.

## 2. Read the evidence

The whole error and stack trace, not the first line. `Logs/agent/compile.log` (one older than the edit means no compile
has run since; `gk-bridge refresh` compiles without focus) and `Logs/agent/console.log`; never the multi-MB
`Logs/Editor.log`. Recent commits that touched the area.

## 3. Check the known failure classes

| Symptom | Usual cause |
|---|---|
| Breaks only on the second Play session | A mutable `static` without its `SubsystemRegistration` reset (domain reload is off) |
| Works with the mouse, not with touch (or the reverse) | Input read from `Mouse.current` / `Touchscreen.current` instead of `Pointer.current` or an action bound to `<Pointer>` |
| UI tap does nothing on the phone | No `EventSystem` with `InputSystemUIInputModule`, a raycast-blocking image on top, or the button is under a notch outside the safe area |
| Runs at 30 fps on the phone | `Application.targetFrameRate` overwritten, or the Mobile tier is GPU bound (`unity-performance`) |
| Fine in the Editor, missing or pink in the build | A shader variant stripped, an asset loaded by path from outside `Resources`, or an `#if UNITY_EDITOR` path |
| Type or member missing only in an IL2CPP build | Code stripping removed it: a `link.xml` entry or `[Preserve]` |
| Keys do nothing in the Editor | Game View not focused |
| Memory grows over a session or with each reload | An event subscribed with no unsubscribe (often a static event holding a destroyed view), a static cache that never evicts, an Addressables handle never released, `Instantiate` without `Destroy`, a `RenderTexture` or `Texture2D` never released or destroyed |

A leak is measured before code changes: take a baseline (FrameLog `sys_mb` / `gc_reserved_mb`, or the Memory Profiler
in a Development Build), repeat the suspect cycle 5-10 times (load and unload the level, open and close the screen),
and compare. The report names the mechanism; the fix is shown by the same cycle returning to baseline.

## 4. Hypothesise, then probe

Write 3–5 ranked, falsifiable hypotheses ("if X is the cause, changing Y makes it disappear") and show them to the
user before probing; they often re-rank at once.

Probe one variable at a time with `Debug.LogWarning("[DBG-a4f2] …")`: warnings reach `Logs/agent/console.log` and plain
`Debug.Log` does not, and one prefix makes cleanup a single grep. Log at the boundaries that separate the hypotheses,
never unconditionally inside a per-frame path.

Trace backward: from where the bad value shows up, to what passed it in, to where it was born. Fix it there.

## 5. Fix and clean up

One change at the root cause, no "while I'm here". A regression test only at a seam that reproduces the real pattern,
and only with permission. Remove every `[DBG-` line. Name the confirmed cause in the handoff and the commit message,
hand the runtime check back as a Play Mode checklist (`implementation-verification`), and call anything checked only by
reading unverified.

**Same bug twice: look for the pattern.** When `git log` shows this bug class fixed before, or three or more PLAN.md
Known issues lines sit in one system, find what they share and fix that once (`unity-architecture`), not one more
instance.

**Three failed fixes: stop.** When each fix exposes a new problem somewhere else, the design is wrong, not the
hypothesis. Take it to the user (`unity-architecture`) before a fourth attempt.

---
Adapted from mattpocock/skills `diagnosing-bugs` (MIT, © 2026 Matt Pocock) and obra/superpowers
`systematic-debugging` and `root-cause-tracing` (MIT, © 2025 Jesse Vincent).
