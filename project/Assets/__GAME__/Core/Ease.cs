namespace __GAME__.Core
{
    /// <summary>
    /// Shaping curve for a normalised 0→1 progress value. Serialized as an int and evaluated
    /// arithmetically rather than through an <c>AnimationCurve</c>, so the simulation stays a plain
    /// value type: no managed reference in the tuning, no allocation,
    /// and the same result on every machine.
    /// </summary>
    public enum Ease
    {
        /// <summary>No shaping. Every eased value behaves exactly as it did before eases existed.</summary>
        Linear = 0,

        SineIn,
        SineOut,
        SineInOut,

        QuadIn,
        QuadOut,
        QuadInOut,

        CubicIn,
        CubicOut,
        CubicInOut,

        QuartIn,
        QuartOut,

        QuintIn,
        QuintOut,

        ExpoIn,
        ExpoOut,
        ExpoInOut,

        CircIn,
        CircOut,

        /// <summary>Overshoots backwards before moving off. Good for wind-ups.</summary>
        BackIn,

        /// <summary>Overshoots past the target and settles back. Good for snappy arrivals.</summary>
        BackOut,

        ElasticOut,
        BounceOut,
    }
}
