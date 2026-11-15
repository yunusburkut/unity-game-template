# Core system skeleton

One minimal system with every part of the shape in `../SKILL.md`: a restartable countdown. Copy the layout, not the
timer. Names follow `<System>Input`, `<System>State`, `<System>Tuning`, `<System>Config`, `<System>Solver`; the glue
and the view live in Game.

## Core (`Assets/<Game>/Core/Countdown/`, namespace `<Game>.Core`)

```csharp
using UnityEngine;

namespace __GAME__.Core
{
    /// One frame's intent, built by Game from whatever device pressed it.
    public readonly struct CountdownInput
    {
        public readonly bool Restart;

        public CountdownInput(bool restart) => Restart = restart;
    }

    /// Everything carried between steps. The controller owns the only instance.
    public struct CountdownState
    {
        public float Remaining;
        public bool Running;
        public bool Finished; // one-step edge: true only on the step the countdown ran out
    }

    /// Flattened tunables, passed by `in`. A readonly struct, so `in` makes no defensive copy.
    public readonly struct CountdownTuning
    {
        public readonly float Duration;

        public CountdownTuning(float duration) => Duration = duration;
    }

    /// The designer-facing asset. Data only: no callbacks, no scene references.
    [CreateAssetMenu(menuName = "__GAME__/Countdown Config")]
    public sealed class CountdownConfig : ScriptableObject
    {
        [SerializeField, Min(0f)] private float duration = 3f;

        public CountdownTuning ToTuning() => new CountdownTuning(duration);
    }

    public static class CountdownSolver
    {
        /// Static, allocation-free, no Time. Edge flags are reset first, before anything can set them.
        public static void Step(ref CountdownState state, in CountdownInput input, in CountdownTuning tuning, float dt)
        {
            state.Finished = false;

            if (input.Restart)
            {
                state.Remaining = tuning.Duration;
                state.Running = true;
            }

            if (!state.Running)
                return;

            state.Remaining -= dt;
            if (state.Remaining <= 0f)
            {
                state.Remaining = 0f;
                state.Running = false;
                state.Finished = true;
            }
        }
    }
}
```

One type per file in a real game (`CountdownInput.cs`, ...); they share a block here only to fit on one page.

## Game (`Assets/<Game>/Game/Countdown/`, namespace `<Game>.Game`)

```csharp
using __GAME__.Core;
using UnityEngine;
using UnityEngine.InputSystem;

namespace __GAME__.Game
{
    public sealed class CountdownController : MonoBehaviour
    {
        [SerializeField] private CountdownConfig config;
        [SerializeField] private InputActionReference restart;
        [SerializeField] private CountdownView view;

        private CountdownState state;

        public float Remaining => state.Remaining; // read by the HUD; nothing is pushed at it

        private void OnEnable() => restart.action.Enable();

        private void Update()
        {
            // ToTuning every frame: a struct copy, no allocation, and Inspector edits apply in Play Mode.
            var tuning = config.ToTuning();
            var input = new CountdownInput(restart.action.WasPressedThisFrame());

            // Step every frame, also at time scale 0 (dt is 0), so edge flags are always cleared.
            CountdownSolver.Step(ref state, in input, in tuning, SimulationStep.Delta);

            // Hand the state to the view in the same Update; the view never polls on its own.
            view.Show(in state);
        }
    }

    public sealed class CountdownView : MonoBehaviour
    {
        // Serialized MMF_Player fields live here (feel-authoring), not on the controller.

        public void Show(in CountdownState state)
        {
            if (state.Finished)
            {
                // play the "time up" feedback
            }
        }
    }
}
```

`restart.action.Enable()` is harmless when the action comes from the project-wide actions asset, which the Input
System already enables. A system whose rules need the world (grounded, a hit) adds those query results as fields of
its `Input` and its desired move as a field of its `State`; the controller runs the queries before `Step` and applies
the move after it (`../SKILL.md`, The split).

## Test (EditMode, references Core alone)

```csharp
var tuning = new CountdownTuning(1f);
var state = default(CountdownState);
CountdownSolver.Step(ref state, new CountdownInput(true), tuning, 0.6f);
CountdownSolver.Step(ref state, default, tuning, 0.6f);
Assert.IsTrue(state.Finished);
CountdownSolver.Step(ref state, default, tuning, 0f);
Assert.IsFalse(state.Finished); // the edge lasts one step
```

Building tuning from the asset instead (`ScriptableObject.CreateInstance<CountdownConfig>()`) and the rest of the
test layout are in `unity-testing`.
