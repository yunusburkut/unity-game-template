using System;
using System.Globalization;
using System.IO;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace GameKit
{
    /// <summary>
    /// Frame-time log for development players (PC and phone): it makes itself, writes one CSV line per
    /// second to <c>persistentDataPath/frame-log-*.csv</c> and shows fps, frame times, GC, draw/SetPass and
    /// CPU/GPU ms on F3 or a three-finger tap (position and memory are CSV-only).
    /// <para>
    /// A line holds the second's average FPS, the p99 frame of the last 10 s, the second's worst frame and how
    /// many of its frames ran past 17 ms, the
    /// scene and camera position at the worst frame (where to go and look), GC bytes per frame, draw
    /// calls, SetPass calls, CPU and GPU ms (gpu reads 0 where the graphics API has no timer queries), and
    /// system-used and GC-reserved memory in MB.
    /// p99 spans 10 s because one second holds about 60 frames at 60 fps, where the 99th percentile is the
    /// worst frame itself: p99_ms is the sustained tail (the 6th-worst of 600 frames), max_ms the single
    /// worst hitch of the second.
    /// </para>
    /// The once-a-second string work allocates; the frame after a write is left out of the GC column so
    /// the log does not report its own cost.
    /// </summary>
    public sealed class FrameLog : MonoBehaviour
    {
        const float WindowSeconds = 1f;
        const float SlowMs = 17f;
        // p99 window: the last 10 one-second windows; 4096 frames hold 10 s up to 400 fps, above that the
        // window is the last 4096 frames
        const int RecentWindows = 10;
        const int RecentCapacity = 4096;
        const string Header = "t_s,scene,fps,p99_ms,max_ms,slow_frames,worst_x,worst_y,worst_z,gc_bytes_per_frame,draw_calls,setpass_calls,cpu_ms,gpu_ms,sys_mb,gc_reserved_mb";
        // a Turkish locale writes 12.5 as "12,5" and shifts every CSV column
        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        readonly float[] _recent = new float[RecentCapacity];
        readonly float[] _sorted = new float[RecentCapacity];
        readonly int[] _windowCounts = new int[RecentWindows];
        readonly FrameTiming[] _timing = new FrameTiming[1];
        readonly StringBuilder _line = new StringBuilder(160);

        ProfilerRecorder _gc;
        ProfilerRecorder _draws;
        ProfilerRecorder _setPass;
        ProfilerRecorder _sysMem;
        ProfilerRecorder _gcReserved;
        StreamWriter _file;
        string _scene = "";
        FrameLogOverlay _overlay;
        bool _show;
        bool _skipGc;
        float _windowTime;
        float _total;
        float _worstMs;
        Vector3 _worstAt;
        int _count;
        int _recentNext;
        int _recentFilled;
        int _window;
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

            // IMGUI dispatches its events every frame to any enabled component with OnGUI, so the overlay is its own
            // component, enabled only while shown: a hidden overlay adds nothing to the frames being measured
            _overlay = gameObject.AddComponent<FrameLogOverlay>();
            _overlay.enabled = false;

            SceneManager.activeSceneChanged += OnSceneChanged;
            _scene = CsvField(SceneManager.GetActiveScene().name);
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

        void OnSceneChanged(Scene from, Scene to) => _scene = CsvField(to.name);

        // a comma in a scene name ("Level 1, Boss") would shift every later column of the line
        static string CsvField(string value) => value.Replace(',', ';');

        void Update()
        {
            if ((Keyboard.current != null && Keyboard.current.f3Key.wasPressedThisFrame) ||
                (Touchscreen.current != null && Touchscreen.current.touches[2].press.wasPressedThisFrame))
            {
                _show = !_show;
                _overlay.enabled = _show;
            }

            var dt = Time.unscaledDeltaTime;
            var ms = dt * 1000f;
            _count++;
            _recent[_recentNext] = ms;
            _recentNext = (_recentNext + 1) % RecentCapacity;
            if (_recentFilled < RecentCapacity) _recentFilled++;
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
            _windowCounts[_window] = _count;
            _window = (_window + 1) % RecentWindows;
            int n = 0;
            foreach (int frames in _windowCounts) n += frames;
            n = Mathf.Min(n, _recentFilled);
            // the newest n frames end just before _recentNext and may wrap round the ring
            int start = (_recentNext - n + RecentCapacity) % RecentCapacity;
            int head = Mathf.Min(n, RecentCapacity - start);
            Array.Copy(_recent, start, _sorted, 0, head);
            Array.Copy(_recent, 0, _sorted, head, n - head);
            Array.Sort(_sorted, 0, n);
            var p99 = _sorted[Mathf.Min(n - 1, (int)(n * 0.99f))];
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
                _overlay.Text = $"{fps:F0} fps   p99 (10 s) {p99:F1} ms   max {_worstMs:F1} ms   >17ms: {_slow}\n" +
                           $"GC {gcPerFrame} B/frame   draw {_draws.LastValue}   setpass {_setPass.LastValue}   cpu {cpu:F1}   gpu {gpu:F1}";

            _windowTime = 0f;
            _count = 0;
            _slow = 0;
            _worstMs = 0f;
            _gcBytes = 0;
            _gcFrames = 0;
            _skipGc = true;
        }
    }
}
