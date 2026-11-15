namespace __GAME__.Core
{
    /// <summary>
    /// Shaping curve for a normalised 0→1 progress value. Serialized as an int and evaluated
    /// arithmetically rather than through an <c>AnimationCurve</c>, so the simulation stays a plain
    /// value type: no managed reference in the tuning, no allocation,
    /// and the same result on every machine.
    /// Every member has an explicit number because assets store that number: a new curve takes the next
    /// free number (even when it sits next to its family below), and no existing number ever changes.
    /// <c>EasingTests.SerializedValues_NeverChange</c> fails if one does.
    /// </summary>
    public enum Ease
    {
        /// <summary>No shaping. Every eased value behaves exactly as it did before eases existed.</summary>
        Linear = 0,

        SineIn = 1,
        SineOut = 2,
        SineInOut = 3,

        QuadIn = 4,
        QuadOut = 5,
        QuadInOut = 6,

        CubicIn = 7,
        CubicOut = 8,
        CubicInOut = 9,

        QuartIn = 10,
        QuartOut = 11,

        QuintIn = 12,
        QuintOut = 13,

        ExpoIn = 14,
        ExpoOut = 15,
        ExpoInOut = 16,

        CircIn = 17,
        CircOut = 18,

        /// <summary>Overshoots backwards before moving off. Good for wind-ups.</summary>
        BackIn = 19,

        /// <summary>Overshoots past the target and settles back. Good for snappy arrivals.</summary>
        BackOut = 20,

        ElasticOut = 21,
        BounceOut = 22,

        // Next free number: 23.
    }
}
