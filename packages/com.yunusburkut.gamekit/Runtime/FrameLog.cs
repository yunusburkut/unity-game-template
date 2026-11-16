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
    /// Frame-time log for development players: it makes itself, writes one CSV line per second to
    /// <c>persistentDataPath/frame-log-*.csv</c> on PC and phone (not on WebGL, which keeps only the overlay) and shows fps, frame times, GC, draw/SetPass and
    /// CPU/GPU ms on F3 or a three-finger tap (position and memory are CSV-only).
    /// <para>
    /// A line holds the second's average FPS, the p99 frame of the last 10 s, the second's worst frame and how
    /// many of its frames ran past 17 ms, the
    /// scene and camera position at the worst frame (where to go and look), GC bytes per frame, draw
    /// calls, SetPass calls, the second's average CPU main-thread work ms (without the Present / vSync wait, so a capped
    /// frame rate does not hide the load) and GPU frame ms (gpu reads 0 where the graphics API has no timer queries), and
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
        double _cpuMs;
        double _gpuMs;
        int _timedFrames;
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

            // WebGL's persistentDataPath is the browser's IndexedDB file system: a CSV there could not be opened, so a
            // WebGL development build keeps only the overlay
            if (Application.platform == RuntimePlatform.WebGLPlayer)
                Debug.Log("FrameLog: no CSV on WebGL (F3 or a three-finger tap shows the numbers)");
            else
            {
                var path = Path.Combine(Application.persistentDataPath, $"frame-log-{DateTime.Now:yyyyMMdd-HHmmss}.csv");
                _file = new StreamWriter(path, false, Encoding.UTF8) { AutoFlush = true };
                _file.WriteLine(Header);
                Debug.Log($"FrameLog: {path} (F3 or a three-finger tap shows the numbers)");
            }

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

            // every frame, so cpu_ms and gpu_ms are the second's average like fps; the latest timing Unity has
            // is a few frames old (the GPU finishes later), so a window lags by those frames
            FrameTimingManager.CaptureFrameTimings();
            if (FrameTimingManager.GetLatestTimings(1, _timing) > 0)
            {
                // main-thread work without its wait for Present (vSync, a full GPU queue); cpuFrameTime also
                // counts the targetFrameRate / vSync wait, so a capped phone would read ~16.7 ms whatever the load
                _cpuMs += _timing[0].cpuMainThreadFrameTime - _timing[0].cpuMainThreadPresentWaitTime;
                _gpuMs += _timing[0].gpuFrameTime;
                _timedFrames++;
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
            var p99 = P99(_recent, _recentNext, Mathf.Min(n, _recentFilled), _sorted);
            var fps = _count / _windowTime;
            var gcPerFrame = _gcFrames > 0 ? _gcBytes / _gcFrames : 0;

            double cpu = _timedFrames > 0 ? _cpuMs / _timedFrames : 0;
            double gpu = _timedFrames > 0 ? _gpuMs / _timedFrames : 0;

            if (_file != null)
            {
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
            }

            if (_show)
                _overlay.Text = $"{fps:F0} fps   p99 (10 s) {p99:F1} ms   max {_worstMs:F1} ms   >17ms: {_slow}\n" +
                           $"GC {gcPerFrame} B/frame   draw {_draws.LastValue}   setpass {_setPass.LastValue}   cpu {cpu:F1}   gpu {gpu:F1}";

            _windowTime = 0f;
            _count = 0;
            _slow = 0;
            _worstMs = 0f;
            _gcBytes = 0;
            _gcFrames = 0;
            _cpuMs = 0;
            _gpuMs = 0;
            _timedFrames = 0;
            _skipGc = true;
        }

        /// <summary>
        /// The 99th-percentile frame time of the newest <paramref name="count"/> entries of a ring buffer, which end
        /// just before <paramref name="next"/> and may wrap round it; <paramref name="scratch"/> (as long as the ring)
        /// is sorted in place. 0 for an empty window.
        /// </summary>
        public static float P99(float[] ring, int next, int count, float[] scratch)
        {
            count = Mathf.Min(count, ring.Length);
            if (count <= 0) return 0f;
            int start = (next - count + ring.Length) % ring.Length;
            int head = Mathf.Min(count, ring.Length - start);
            Array.Copy(ring, start, scratch, 0, head);
            Array.Copy(ring, 0, scratch, head, count - head);
            Array.Sort(scratch, 0, count);
            return scratch[Mathf.Min(count - 1, (int)(count * 0.99f))];
        }
    }
}
