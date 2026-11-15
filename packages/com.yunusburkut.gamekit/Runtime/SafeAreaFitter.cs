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

            var anchors = Anchors(_applied, _screen.x, _screen.y);
            _rect.anchorMin = anchors.min;
            _rect.anchorMax = anchors.max;
            _rect.offsetMin = Vector2.zero;
            _rect.offsetMax = Vector2.zero;
        }

        /// <summary>The safe area in pixels as normalized anchors (min, max) of a screen width x height.</summary>
        public static Rect Anchors(Rect safeArea, int width, int height) =>
            Rect.MinMaxRect(safeArea.xMin / width, safeArea.yMin / height, safeArea.xMax / width, safeArea.yMax / height);
    }
}
