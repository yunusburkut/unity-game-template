using UnityEngine;

namespace GameKit
{
    /// <summary>
    /// Fits its RectTransform to <see cref="Screen.safeArea"/>, so HUD and buttons stay clear of notches,
    /// camera cut-outs and the home indicator. Put it on a full-stretch child of the Canvas and parent the
    /// interactive UI under it; backgrounds stay outside it. On PC the safe area is the whole screen.
    /// A Screen Space - Camera canvas whose camera is letterboxed (Camera.rect smaller than the screen) sets
    /// <c>_camera</c> to that camera: the canvas then covers only its pixelRect, and a notch inset that falls
    /// inside the side bars no longer pushes the HUD in. Leave it empty for Screen Space - Overlay.
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public sealed class SafeAreaFitter : MonoBehaviour
    {
        [SerializeField, Tooltip("Only for a Screen Space - Camera canvas with a letterboxed camera; empty = whole screen.")]
        Camera _camera;

        RectTransform _rect;
        Rect _applied;
        Rect _viewport;

        void Awake() => _rect = (RectTransform)transform;

        void OnEnable() => Apply();

        // rotation, window resizes and letterbox changes move the safe area or viewport without an event
        void Update()
        {
            if (Screen.safeArea != _applied || Viewport() != _viewport) Apply();
        }

        Rect Viewport() => _camera ? _camera.pixelRect : new Rect(0, 0, Screen.width, Screen.height);

        void Apply()
        {
            _applied = Screen.safeArea;
            _viewport = Viewport();
            if (_viewport.width <= 0 || _viewport.height <= 0) return;

            var anchors = Anchors(_applied, _viewport);
            _rect.anchorMin = anchors.min;
            _rect.anchorMax = anchors.max;
            _rect.offsetMin = Vector2.zero;
            _rect.offsetMax = Vector2.zero;
        }

        /// <summary>
        /// The safe area in screen pixels, clipped to <paramref name="viewport"/> (the screen, or a letterboxed
        /// camera's pixelRect), as normalized anchors (min, max) of that viewport.
        /// </summary>
        public static Rect Anchors(Rect safeArea, Rect viewport)
        {
            float xMin = Mathf.Clamp(safeArea.xMin, viewport.xMin, viewport.xMax);
            float yMin = Mathf.Clamp(safeArea.yMin, viewport.yMin, viewport.yMax);
            float xMax = Mathf.Clamp(safeArea.xMax, xMin, viewport.xMax);
            float yMax = Mathf.Clamp(safeArea.yMax, yMin, viewport.yMax);
            return Rect.MinMaxRect(
                (xMin - viewport.x) / viewport.width, (yMin - viewport.y) / viewport.height,
                (xMax - viewport.x) / viewport.width, (yMax - viewport.y) / viewport.height);
        }
    }
}
