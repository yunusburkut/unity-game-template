using UnityEngine;

namespace GameKit
{
    /// <summary>
    /// FrameLog's on-screen numbers. A component of its own so FrameLog can disable it while hidden: Unity sends
    /// IMGUI events every frame to each enabled component that has OnGUI, and that cost would land in the frame
    /// times FrameLog measures.
    /// </summary>
    [AddComponentMenu("")]
    internal sealed class FrameLogOverlay : MonoBehaviour
    {
        const float Margin = 10f;
        const float Padding = 6f;

        readonly GUIContent _content = new GUIContent("FrameLog...");
        Vector2 _size; // measured in OnGUI (GUI.skin is only there), again after each new text

        internal string Text
        {
            get => _content.text;
            set { _content.text = value; _size = Vector2.zero; }
        }

        // GUI.Label is not GUILayout, so the Layout event pass is not needed
        void Awake() => useGUILayout = false;

        void OnGUI()
        {
            if (_size == Vector2.zero) _size = GUI.skin.label.CalcSize(_content) + new Vector2(2f * Padding, 2f * Padding);

            // the default skin is a fixed pixel size: scale it to about the same physical size as on a 160 dpi
            // screen, but never wider than the screen (a phone at 460 dpi would be ~3x); Screen.dpi is 0 when unknown
            float fit = (Screen.width - 2f * Margin) / _size.x;
            float scale = Mathf.Max(1f, Mathf.Min(Screen.dpi / 160f, fit));
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));

            // inside the safe area (notch, camera cut-out), on the skin's dark box so it reads on a bright scene
            Rect safe = Screen.safeArea;
            var box = new Rect(safe.x / scale + Margin, (Screen.height - safe.yMax) / scale + Margin, _size.x, _size.y);
            GUI.Box(box, GUIContent.none);
            GUI.Label(new Rect(box.x + Padding, box.y + Padding, box.width - 2f * Padding, box.height - 2f * Padding),
                      _content);
        }
    }
}
