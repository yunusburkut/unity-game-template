using UnityEngine;

namespace GameKit
{
    /// <summary>
    /// Fits its RectTransform to <see cref="Screen.safeArea"/>, so HUD and buttons stay clear of notches,
    /// camera cut-outs and the home indicator. Put it on a full-stretch child of the Canvas and parent the
    /// interactive UI under it; backgrounds stay outside it. On PC the safe area is the whole screen.
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public sealed class SafeAreaFitter : MonoBehaviour
    {
        RectTransform _rect;
        Rect _applied;
        Vector2Int _screen;

        void Awake() => _rect = (RectTransform)transform;

        void OnEnable() => Apply();

        // rotation and window resizes change the safe area without an event
        void Update()
        {
            if (Screen.safeArea != _applied || Screen.width != _screen.x || Screen.height != _screen.y) Apply();
        }

        void Apply()
        {
            _applied = Screen.safeArea;
            _screen = new Vector2Int(Screen.width, Screen.height);
            if (_screen.x == 0 || _screen.y == 0) return;

            var min = _applied.position;
            var max = _applied.position + _applied.size;
            _rect.anchorMin = new Vector2(min.x / _screen.x, min.y / _screen.y);
            _rect.anchorMax = new Vector2(max.x / _screen.x, max.y / _screen.y);
            _rect.offsetMin = Vector2.zero;
            _rect.offsetMax = Vector2.zero;
        }
    }
}
