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
        internal string Text = "FrameLog…";

        // GUI.Label is not GUILayout, so the Layout event pass is not needed
        void Awake() => useGUILayout = false;

        void OnGUI() => GUI.Label(new Rect(10f, 10f, 900f, 50f), Text);
    }
}
