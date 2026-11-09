using System;
using System.Globalization;
using System.IO;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace __GAME__.Game
{
    /// <summary>
    /// Frame-time log for development players (PC and phone): it makes itself, writes one CSV line per
    /// second to <c>persistentDataPath/frame-log-*.csv</c> and shows fps, frame times, GC, draw/SetPass and
    /// CPU/GPU ms on F3 or a three-finger tap (position and memory are CSV-only).
    /// <para>
    /// A line holds the window's average FPS, p99 and worst frame, how many frames ran past 17 ms, the
    /// scene and camera position at the worst frame (where to go and look), GC bytes per frame, draw
    /// calls, SetPass calls, CPU and GPU ms (gpu reads 0 where the graphics API has no timer queries), and
    /// system-used and GC-reserved memory in MB.
    /// </para>
    /// The once-a-second string work allocates; the frame after a write is left out of the GC column so
    /// the log does not report its own cost.
    /// </summary>
    public sealed class FrameLog : MonoBehaviour
    {
        const float WindowSeconds = 1f;
        const float SlowMs = 17f;
        const int Capacity = 1024;
        const string Header = "t_s,scene,fps,p99_ms,max_ms,slow_frames,worst_x,worst_y,worst_z,gc_bytes_per_frame,draw_calls,setpass_calls,cpu_ms,gpu_ms,sys_mb,gc_reserved_mb";
        // a Turkish locale writes 12.5 as "12,5" and shifts every CSV column
        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        readonly float[] _frames = new float[Capacity];
        readonly FrameTiming[] _timing = new FrameTiming[1];
        readonly StringBuilder _line = new StringBuilder(160);

        ProfilerRecorder _gc;
        ProfilerRecorder _draws;
        ProfilerRecorder _setPass;
        ProfilerRecorder _sysMem;
        ProfilerRecorder _gcReserved;
        StreamWriter _file;
        string _scene = "";
        string _overlay = "FrameLog…";
        bool _show;
        bool _skipGc;
        float _windowTime;
        float _total;
        float _worstMs;
        Vector3 _worstAt;
        int _count;
        int _slow;
        long _gcBytes;
        int _gcFrames;
        Camera _camera;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Create()
        {
            if (!Debug.isDebugBuild || Application.isEditor) return;
            var go = new GameObject("FrameLog") { hideFlags = HideFlags.HideAndDontSave };
            DontDestroyOnLoad(go);
            go.AddComponent<FrameLog>();
        }

        void Awake()
        {
            _gc = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
            _draws = ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count");
            _setPass = ProfilerRecorder.StartNew(ProfilerCategory.Render, "SetPass Calls Count");
            _sysMem = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "System Used Memory");
            _gcReserved = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Reserved Memory");

            var path = Path.Combine(Application.persistentDataPath, $"frame-log-{DateTime.Now:yyyyMMdd-HHmmss}.csv");
            _file = new StreamWriter(path, false, Encoding.UTF8) { AutoFlush = true };
            _file.WriteLine(Header);
            Debug.Log($"FrameLog: {path} (F3 or a three-finger tap shows the numbers)");

            SceneManager.activeSceneChanged += OnSceneChanged;
            _scene = SceneManager.GetActiveScene().name;
        }

        void OnDestroy()
        {
            SceneManager.activeSceneChanged -= OnSceneChanged;
            _gc.Dispose();
            _draws.Dispose();
            _setPass.Dispose();
            _sysMem.Dispose();
            _gcReserved.Dispose();
            _file?.Dispose();
        }

        void OnSceneChanged(Scene from, Scene to) => _scene = to.name;

        void Update()
        {
            if (Keyboard.current != null && Keyboard.current.f3Key.wasPressedThisFrame) _show = !_show;
            if (Touchscreen.current != null && Touchscreen.current.touches[2].press.wasPressedThisFrame) _show = !_show;

            var dt = Time.unscaledDeltaTime;
            var ms = dt * 1000f;
            if (_count < Capacity) _frames[_count++] = ms;
            _total += dt;
            _windowTime += dt;
            if (ms > SlowMs) _slow++;
            if (ms > _worstMs)
            {
                _worstMs = ms;
                if (_camera == null) _camera = Camera.main;
                if (_camera != null) _worstAt = _camera.transform.position;
            }

            if (_gc.Valid)
            {
                if (_skipGc) _skipGc = false;
                else { _gcBytes += _gc.LastValue; _gcFrames++; }
            }

            if (_windowTime >= WindowSeconds) Flush();
        }

        void Flush()
        {
            Array.Sort(_frames, 0, _count);
            var p99 = _frames[Mathf.Min(_count - 1, (int)(_count * 0.99f))];
            var fps = _count / _windowTime;
            var gcPerFrame = _gcFrames > 0 ? _gcBytes / _gcFrames : 0;

            double cpu = 0, gpu = 0;
            FrameTimingManager.CaptureFrameTimings();
            if (FrameTimingManager.GetLatestTimings(1, _timing) > 0)
            {
                cpu = _timing[0].cpuFrameTime;
                gpu = _timing[0].gpuFrameTime;
            }

            _line.Clear()
                .Append(_total.ToString("F1", Inv)).Append(',').Append(_scene).Append(',')
                .Append(fps.ToString("F1", Inv)).Append(',').Append(p99.ToString("F1", Inv)).Append(',')
                .Append(_worstMs.ToString("F1", Inv)).Append(',').Append(_slow).Append(',')
                .Append(_worstAt.x.ToString("F1", Inv)).Append(',').Append(_worstAt.y.ToString("F1", Inv)).Append(',')
                .Append(_worstAt.z.ToString("F1", Inv)).Append(',')
                .Append(gcPerFrame).Append(',').Append(_draws.LastValue).Append(',').Append(_setPass.LastValue).Append(',')
                .Append(cpu.ToString("F1", Inv)).Append(',').Append(gpu.ToString("F1", Inv)).Append(',')
                .Append((_sysMem.LastValue / 1048576f).ToString("F0", Inv)).Append(',')
                .Append((_gcReserved.LastValue / 1048576f).ToString("F0", Inv));
            _file.WriteLine(_line.ToString());

            if (_show)
                _overlay = $"{fps:F0} fps   p99 {p99:F1} ms   max {_worstMs:F1} ms   >17ms: {_slow}\n" +
                           $"GC {gcPerFrame} B/frame   draw {_draws.LastValue}   setpass {_setPass.LastValue}   cpu {cpu:F1}   gpu {gpu:F1}";

            _windowTime = 0f;
            _count = 0;
            _slow = 0;
            _worstMs = 0f;
            _gcBytes = 0;
            _gcFrames = 0;
            _skipGc = true;
        }

        void OnGUI()
        {
            if (_show) GUI.Label(new Rect(10f, 10f, 900f, 50f), _overlay);
        }
    }
}
