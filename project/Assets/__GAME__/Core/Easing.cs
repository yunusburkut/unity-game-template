using UnityEngine;

namespace __GAME__.Core
{
    /// <summary>
    /// Evaluates an <see cref="Ease"/>. Pure, allocation-free and branch-only, so it is safe to call
    /// from inside the solver every step.
    /// </summary>
    public static class Easing
    {
        const float BackOvershoot = 1.70158f;
        const float ElasticPeriod = 2f * Mathf.PI / 3f;

        /// <summary>
        /// Shapes <paramref name="t"/>, which is clamped to 0→1 first. The result is normally 0→1 too,
        /// but the Back and Elastic curves deliberately overshoot outside it.
        /// </summary>
        public static float Evaluate(Ease ease, float t)
        {
            t = Mathf.Clamp01(t);

            switch (ease)
            {
                case Ease.Linear: return t;

                case Ease.SineIn: return 1f - Mathf.Cos(t * Mathf.PI * 0.5f);
                case Ease.SineOut: return Mathf.Sin(t * Mathf.PI * 0.5f);
                case Ease.SineInOut: return -(Mathf.Cos(Mathf.PI * t) - 1f) * 0.5f;

                case Ease.QuadIn: return t * t;
                case Ease.QuadOut: return 1f - Flip(t, 2);
                case Ease.QuadInOut: return t < 0.5f ? 2f * t * t : 1f - Flip(t, 2) * 2f;

                case Ease.CubicIn: return t * t * t;
                case Ease.CubicOut: return 1f - Flip(t, 3);
                case Ease.CubicInOut: return t < 0.5f ? 4f * t * t * t : 1f - Flip(t, 3) * 4f;

                case Ease.QuartIn: return t * t * t * t;
                case Ease.QuartOut: return 1f - Flip(t, 4);

                case Ease.QuintIn: return t * t * t * t * t;
                case Ease.QuintOut: return 1f - Flip(t, 5);

                case Ease.ExpoIn: return t <= 0f ? 0f : Mathf.Pow(2f, 10f * t - 10f);
                case Ease.ExpoOut: return t >= 1f ? 1f : 1f - Mathf.Pow(2f, -10f * t);
                case Ease.ExpoInOut:
                    if (t <= 0f) return 0f;
                    if (t >= 1f) return 1f;
                    return t < 0.5f
                        ? Mathf.Pow(2f, 20f * t - 10f) * 0.5f
                        : (2f - Mathf.Pow(2f, -20f * t + 10f)) * 0.5f;

                case Ease.CircIn: return 1f - Mathf.Sqrt(1f - t * t);
                case Ease.CircOut: return Mathf.Sqrt(1f - (t - 1f) * (t - 1f));

                case Ease.BackIn:
                    return (BackOvershoot + 1f) * t * t * t - BackOvershoot * t * t;
                case Ease.BackOut:
                {
                    float u = t - 1f;
                    return 1f + (BackOvershoot + 1f) * u * u * u + BackOvershoot * u * u;
                }

                case Ease.ElasticOut:
                    if (t <= 0f) return 0f;
                    if (t >= 1f) return 1f;
                    return Mathf.Pow(2f, -10f * t) * Mathf.Sin((t * 10f - 0.75f) * ElasticPeriod) + 1f;

                case Ease.BounceOut: return BounceOut(t);

                default: return t;
            }
        }

        /// <summary>(1 - t) raised to <paramref name="power"/>; the shared tail of every Out curve.</summary>
        static float Flip(float t, int power)
        {
            float u = 1f - t;
            float result = u;
            for (int i = 1; i < power; i++) result *= u;
            return result;
        }

        static float BounceOut(float t)
        {
            const float n = 7.5625f;
            const float d = 2.75f;

            if (t < 1f / d) return n * t * t;
            if (t < 2f / d) { t -= 1.5f / d; return n * t * t + 0.75f; }
            if (t < 2.5f / d) { t -= 2.25f / d; return n * t * t + 0.9375f; }
            t -= 2.625f / d;
            return n * t * t + 0.984375f;
        }
    }
}
