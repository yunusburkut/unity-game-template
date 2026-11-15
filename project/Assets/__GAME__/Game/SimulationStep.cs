using UnityEngine;

namespace __GAME__.Game
{
    /// <summary>
    /// The frame step every Update-driven simulation uses. Clamped so a hitch (a GC spike, a phone coming back
    /// from the background) cannot tunnel anything through geometry. Step simulations with this rather than a
    /// clamp of their own.
    /// Ceiling: below 20 fps the simulation runs slower than wall-clock time (at a steady 15 fps, 75% speed),
    /// while timeScale-driven effects such as Feel keep real time. If a game must hold real time on slow
    /// phones, substep instead: step in slices of at most <see cref="Max"/> until the frame's
    /// <c>Time.deltaTime</c> is used up. <c>Time.maximumDeltaTime</c> is the engine's global cap and
    /// also bounds physics catch-up; it is not a replacement for this per-simulation clamp.
    /// </summary>
    public static class SimulationStep
    {
        public const float Max = 1f / 20f;

        public static float Delta => Mathf.Min(Time.deltaTime, Max);
    }
}
