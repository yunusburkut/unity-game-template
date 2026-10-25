using UnityEngine;

namespace __GAME__.Game
{
    /// <summary>
    /// The frame step every Update-driven simulation uses. Clamped so a hitch (a GC spike, a phone coming back
    /// from the background) cannot tunnel anything through geometry. Step simulations with this rather than a
    /// clamp of their own.
    /// </summary>
    public static class SimulationStep
    {
        public const float Max = 1f / 20f;

        public static float Delta => Mathf.Min(Time.deltaTime, Max);
    }
}
