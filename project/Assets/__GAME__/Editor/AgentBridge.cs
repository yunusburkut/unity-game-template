using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.Build.Player;
using UnityEditor.Compilation;
using UnityEditor.TestTools.TestRunner.Api;
using UnityEngine;

namespace __GAME__.Editor
{
    /// <summary>
    /// Mirrors compile results, Console errors and test results into small, parseable files under
    /// Logs/agent/ so a coding agent can read them without opening the Editor or the multi-MB
    /// Logs/Editor.log. Editor-only, no runtime cost. See CLAUDE.md for the read/write protocol.
    ///
    /// Compiler messages are taken from the Console log stream rather than from
    /// CompilationPipeline.assemblyCompilationFinished: on Unity 6.6 that callback was observed not
    /// to deliver messages for a failed assembly, while the log stream always carries them.
    /// The report is written once compilation settles, so a domain reload cannot race it, and only after a compile
    /// really ran (or once per Editor session), so a fresh timestamp always means fresh code.
    /// </summary>
    [InitializeOnLoad]
    internal static class AgentBridge
    {
        const string Dir = "Logs/agent";
        const string CompilePath = Dir + "/compile.log";
        const string ConsolePath = Dir + "/console.log";
        const string TestsPath = Dir + "/tests.log";
        const string RequestPath = Dir + "/request.txt";
        const string CapturePath = Dir + "/capture.log";
        const string CaptureDir = Dir + "/capture";
        const string BridgePath = Dir + "/bridge.log";
        const string PlayerCompilePath = Dir + "/compile-player.log";
        const string PlayerCompileDir = "Temp/AgentBridgePlayerScripts";
        const string CapturePendingKey = "AgentBridge.CaptureSeconds";
        const string CompileRanKey = "AgentBridge.CompileRan";
        const string SessionStartedKey = "AgentBridge.SessionStarted";
        const string RefreshAckKey = "AgentBridge.RefreshAck";
        const string PendingBuildKey = "AgentBridge.PendingBuild";
        const double RefreshSettle = 2.0;
        const float DefaultCaptureSeconds = 3f;

        const int ConsoleCapacity = 200;
        const int CompileCapacity = 100;
        const double FlushInterval = 0.5;
        const double PollInterval = 1.0;

        static readonly List<string> CompileLines = new List<string>(CompileCapacity);
        static readonly Queue<string> ConsoleLines = new Queue<string>(ConsoleCapacity);
        static readonly object Gate = new object();
        static readonly StringBuilder Builder = new StringBuilder(4096);
        static readonly List<string> CaptureErrors = new List<string>(32);
        static readonly List<string> PlayerCompileLines = new List<string>(CompileCapacity);

        static bool _consoleDirty;
        static bool _reportPending;
        static volatile bool _compilingPlayer;
        static volatile bool _compilingEditor;
        static double _nextFlush;
        static double _nextPoll;
        static double _refreshAckAt;
        static double _buildNotBefore;
        static TestRunnerApi _testApi;
        static bool _capturing;
        // a capture's errors start counting before Play Mode starts, so the ones the scene's Awake throws count too
        static volatile bool _capturePending;
        static bool _runInBackground;
        static double _captureStart;
        static float _captureSeconds;
        static int _shotsTaken;

        static AgentBridge()
        {
            Directory.CreateDirectory(Dir);

            CompilationPipeline.compilationStarted += OnCompilationStarted;
            Application.logMessageReceivedThreaded += OnLogMessage;
            EditorApplication.update += OnEditorUpdate;

            // Callbacks on a TestRunnerApi do not survive a domain reload (a recompile mid-run, or a PlayMode run in a
            // project with domain reload on), so they are registered on every load rather than when a run starts.
            _testApi = ScriptableObject.CreateInstance<TestRunnerApi>();
            _testApi.RegisterCallbacks(new ResultWriter());

            // A domain reload alone (entering Play Mode, say) must not refresh the OK timestamp: report only after a
            // compile that ran before this reload, or once when the Editor starts. SessionState survives the reload.
            bool editorStarted = !SessionState.GetBool(SessionStartedKey, false);
            _reportPending = SessionState.GetBool(CompileRanKey, false) || editorStarted;
            SessionState.SetBool(SessionStartedKey, true);

            // A restart clears SessionState, so a refresh or build the last session left open would never be answered.
            if (editorStarted)
            {
                if (FirstLineStarts(BridgePath, "REFRESHING"))
                    WriteAllText(BridgePath, "REFRESHED  " + Timestamp() + "  Editor restarted: see compile.log\n");
                if (FirstLineStarts(BuildMenu.LogPath, "PENDING"))
                    WriteAllText(BuildMenu.LogPath, "FAILED  " + Timestamp() + "  Editor restarted before the build finished\n");
                if (FirstLineStarts(CapturePath, "PENDING"))
                    WriteAllText(CapturePath, "FAILED  " + Timestamp() + "  Editor restarted before the capture finished\n");
                if (FirstLineStarts(PlayerCompilePath, "RUNNING"))
                    WriteAllText(PlayerCompilePath, "FAILED  " + Timestamp() + "  Editor restarted during the check\n");
                if (FirstLineStarts(TestsPath, "RUNNING"))
                    WriteAllText(TestsPath, "FAILED  " + Timestamp() + "  Editor restarted during the test run\n");
            }

            // The reload that enters a capture's Play Mode runs this before the scene wakes up.
            _capturePending = SessionState.GetFloat(CapturePendingKey, 0f) > 0f;

            // A reload that was no compile (entering Play Mode) inside a refresh's settle time lost its timer; restart it.
            if (SessionState.GetBool(RefreshAckKey, false) && !SessionState.GetBool(CompileRanKey, false))
                _refreshAckAt = EditorApplication.timeSinceStartup + RefreshSettle;

            // If the Editor cold-started on broken sources, no handler was alive to see the
            // messages. Unity's own log still has them, and this is the only chance to report them.
            if (EditorUtility.scriptCompilationFailed)
            {
                WriteAllText(CompilePath, "FAILED  " + Timestamp() + "\n" + ScrapeEditorLogErrors());
                SessionState.EraseBool(CompileRanKey);
                _reportPending = false;
            }
        }

        // ---- compilation ----

        static void OnCompilationStarted(object _)
        {
            if (_compilingPlayer) return; // a player-script check is not the Editor's compile
            SessionState.SetBool(CompileRanKey, true);
            lock (Gate)
            {
                CompileLines.Clear();
                _reportPending = true;
                _compilingEditor = true;
            }
        }

        /// <summary>Writes the settled compile state. Called once compilation has quiesced.</summary>
        static void WriteCompileReport()
        {
            Builder.Clear();

            lock (Gate)
            {
                if (CompileLines.Count == 0)
                {
                    Builder.Append("OK  ").Append(Timestamp()).Append('\n');
                }
                else
                {
                    int errors = 0;
                    for (int i = 0; i < CompileLines.Count; i++)
                    {
                        if (CompileLines[i].IndexOf("): error ", StringComparison.Ordinal) >= 0) errors++;
                    }

                    Builder.Append(errors).Append(" error(s), ")
                           .Append(CompileLines.Count - errors).Append(" warning(s)  ")
                           .Append(Timestamp()).Append('\n');

                    for (int i = 0; i < CompileLines.Count; i++) Builder.Append(CompileLines[i]).Append('\n');
                }
            }

            WriteAllText(CompilePath, Builder.ToString());
            SessionState.EraseBool(CompileRanKey);
            _compilingEditor = false;
            if (SessionState.GetBool(RefreshAckKey, false)) AckRefresh("compiled: see compile.log");
        }

        static void AckRefresh(string outcome)
        {
            SessionState.EraseBool(RefreshAckKey);
            WriteAllText(BridgePath, "REFRESHED  " + Timestamp() + "  " + outcome + "\n");
        }

        static bool IsCompilerMessage(string message) =>
            message.IndexOf("): error CS", StringComparison.Ordinal) >= 0 ||
            message.IndexOf("): warning CS", StringComparison.Ordinal) >= 0;

        // ---- console ----

        static void OnLogMessage(string condition, string stackTrace, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert && type != LogType.Warning)
                return;

            if ((_capturing || _capturePending) && type != LogType.Warning)
            {
                lock (Gate)
                {
                    if (CaptureErrors.Count < CompileCapacity)
                        CaptureErrors.Add(type + "  " + condition + (string.IsNullOrEmpty(stackTrace)
                            ? "" : "\n    " + stackTrace.Replace("\n", "\n    ").TrimEnd()));
                }
            }

            // Only the Editor's own compile and a player-script check report compiler messages; any other one (a
            // `script run` or `script eval` snippet, say) is an ordinary Console line.
            if (IsCompilerMessage(condition) && (_compilingPlayer || _compilingEditor))
            {
                lock (Gate)
                {
                    if (_compilingPlayer) // a player-script check reports on its own, not as the Editor's compile
                    {
                        if (!PlayerCompileLines.Contains(condition) && PlayerCompileLines.Count < CompileCapacity)
                            PlayerCompileLines.Add(condition);
                        return;
                    }
                    if (CompileLines.Contains(condition)) return; // Unity repeats each message per target
                    if (CompileLines.Count == CompileCapacity) return; // keep the first ones, usually the cause
                    CompileLines.Add(condition);
                    _reportPending = true;
                }
                return;
            }

            string line = type + "  " + Timestamp() + "  " + condition;
            if (type != LogType.Warning && !string.IsNullOrEmpty(stackTrace))
                line += "\n    " + stackTrace.Replace("\n", "\n    ").TrimEnd();

            lock (Gate)
            {
                if (ConsoleLines.Count >= ConsoleCapacity) ConsoleLines.Dequeue();
                ConsoleLines.Enqueue(line);
                _consoleDirty = true;
            }
        }

        static void FlushConsole()
        {
            Builder.Clear();
            lock (Gate)
            {
                foreach (string line in ConsoleLines) Builder.Append(line).Append('\n');
                _consoleDirty = false;
            }
            WriteAllText(ConsolePath, Builder.ToString());
        }

        // ---- tick ----

        static void OnEditorUpdate()
        {
            if (EditorApplication.isCompiling)
            {
                _reportPending = true;
                return;
            }

            if (_reportPending)
            {
                _reportPending = false;
                WriteCompileReport();
            }

            double now = EditorApplication.timeSinceStartup;
            TickCapture(now);

            // A queued build (SessionState, so the compile its refresh starts cannot lose it) waits out that compile.
            // Until it starts, request.txt is left alone, so "wait until request.txt is gone" also waits for the build.
            string pendingBuild = SessionState.GetString(PendingBuildKey, "");
            if (pendingBuild.Length > 0 && EditorApplication.isPlaying)
            {
                SessionState.EraseString(PendingBuildKey);
                pendingBuild = "";
                WriteAllText(BuildMenu.LogPath, "SKIPPED  " + Timestamp() + "  Play Mode started before the build\n");
            }
            if (pendingBuild.Length > 0 && now >= _buildNotBefore && !EditorApplication.isUpdating &&
                !EditorApplication.isPlayingOrWillChangePlaymode)
            {
                SessionState.EraseString(PendingBuildKey);
                StartBuild(pendingBuild);
                return;
            }

            // A refresh whose compile has not started within the settle time changed no script.
            if (_refreshAckAt > 0 && now >= _refreshAckAt)
            {
                _refreshAckAt = 0;
                if (SessionState.GetBool(RefreshAckKey, false)) AckRefresh("no script changes");
            }

            if (_consoleDirty && now >= _nextFlush)
            {
                _nextFlush = now + FlushInterval;
                FlushConsole();
            }

            if (now < _nextPoll) return;
            _nextPoll = now + PollInterval;

            if (pendingBuild.Length > 0 || EditorApplication.isUpdating || !File.Exists(RequestPath)) return;

            string request;
            try
            {
                request = File.ReadAllText(RequestPath).Trim();
                File.Delete(RequestPath);
            }
            catch (IOException)
            {
                return; // still being written; retry next poll
            }

            HandleRequest(request);
        }

        static void HandleRequest(string request)
        {
            if (request.Equals("refresh", StringComparison.OrdinalIgnoreCase))
            {
                // Auto Refresh waits for focus; a scripted refresh imports changed files without it. Their compile can
                // start a few frames later, so the ack waits: the compile report answers it (in SessionState, since a
                // clean compile reloads the domain), or the settle time runs out with no compile.
                // In Play Mode only "Recompile After Finished Playing" (Preferences > General > Script Changes While
                // Playing, 1) holds the compile until Play ends; Unity's default (0) would reload the domain mid-session.
                if (EditorApplication.isPlaying)
                {
                    if (EditorPrefs.GetInt("ScriptCompilationDuringPlay", 0) == 1)
                    {
                        AssetDatabase.Refresh();
                        WriteAllText(BridgePath, "REFRESHED  " + Timestamp() + "  in Play Mode: compiles after Play ends\n");
                    }
                    else
                        WriteAllText(BridgePath, "SKIPPED  " + Timestamp() + "  in Play Mode: refresh again after Play ends\n");
                    return;
                }
                WriteAllText(BridgePath, "REFRESHING  " + Timestamp() + "\n");
                SessionState.SetBool(RefreshAckKey, true);
                AssetDatabase.Refresh();
                // Timed from the end of the import, so a slow one does not use up the wait for its compile.
                _refreshAckAt = EditorApplication.timeSinceStartup + RefreshSettle;
                return;
            }

            if (request.StartsWith("compile ", StringComparison.OrdinalIgnoreCase))
            {
                // Run straight from the tick: it switches no platform, and delayCall was seen not to fire in an
                // unfocused Editor.
                CompilePlayerScripts(request.Substring("compile ".Length).Trim().ToLowerInvariant());
                return;
            }

            if (request.StartsWith("run-tests", StringComparison.OrdinalIgnoreCase))
            {
                bool playMode = request.IndexOf("playmode", StringComparison.OrdinalIgnoreCase) >= 0;
                RunTests(playMode ? TestMode.PlayMode : TestMode.EditMode);
                return;
            }

            if (request.StartsWith("play-capture", StringComparison.OrdinalIgnoreCase))
            {
                RequestCapture(request.Substring("play-capture".Length).Trim());
                return;
            }

            // "build <target> [dev]"
            string[] words = request.Split((char[])null, StringSplitOptions.RemoveEmptyEntries);
            if (words.Length >= 2 && words.Length <= 3 && words[0].Equals("build", StringComparison.OrdinalIgnoreCase) &&
                BuildMenu.TryParse(words[1], out _, out _) &&
                (words.Length == 2 || words[2].Equals("dev", StringComparison.OrdinalIgnoreCase)))
            {
                if (EditorApplication.isPlayingOrWillChangePlaymode)
                {
                    WriteAllText(BuildMenu.LogPath, "SKIPPED  " + Timestamp() + "  in Play Mode: Unity cannot build while playing\n");
                    return;
                }
                // Import first, so files written while the Editor was unfocused are in the build; the tick starts it
                // once the import's compile has settled (not through delayCall, which was seen not to fire in an
                // unfocused Editor). PENDING tells a queued build from a lost request.
                string build = words[1].ToLowerInvariant() + (words.Length == 3 ? " dev" : "");
                WriteAllText(BuildMenu.LogPath, "PENDING  build " + build + "  " + Timestamp() + "\n");
                SessionState.SetString(PendingBuildKey, build);
                AssetDatabase.Refresh();
                _buildNotBefore = EditorApplication.timeSinceStartup + RefreshSettle;
                return;
            }

            WriteAllText(BridgePath, "Unknown request: '" + request + "'  " + Timestamp() + "\nSupported: refresh, "
                + "compile ios|android, run-tests [playmode], play-capture [seconds], "
                + "build windows|android|aab|ios|webgl [dev]\n");
        }

        /// <summary>Runs a queued "target [dev]" build; build.log always ends up replacing its PENDING line.</summary>
        static void StartBuild(string build)
        {
            string[] words = build.Split(' ');
            if (!BuildMenu.TryParse(words[0], out BuildTarget target, out bool appBundle)) return;
            try
            {
                BuildMenu.Build(target, appBundle, words.Length > 1, askToSave: false);
            }
            catch (Exception e)
            {
                WriteAllText(BuildMenu.LogPath, "FAILED  " + Timestamp() + "  " + e.Message + "\n");
            }
        }

        // ---- player-script check ----
        // "compile ios|android": compiles the player scripts for that target into Temp/ without switching the active
        // target, so code behind UNITY_IOS / UNITY_ANDROID is type-checked while the Editor stays on Windows. The
        // compiler's messages arrive on the log stream, which OnLogMessage diverts here.

        static void CompilePlayerScripts(string platform)
        {
            BuildTarget target;
            BuildTargetGroup group;
            if (platform == "ios") { target = BuildTarget.iOS; group = BuildTargetGroup.iOS; }
            else if (platform == "android") { target = BuildTarget.Android; group = BuildTargetGroup.Android; }
            else
            {
                WriteAllText(PlayerCompilePath, "Unknown platform '" + platform + "'  " + Timestamp() + "  use ios or android\n");
                return;
            }

            if (!BuildPipeline.IsBuildTargetSupported(group, target))
            {
                WriteAllText(PlayerCompilePath, "UNSUPPORTED  " + platform + "  the platform module is not installed  "
                    + Timestamp() + "\n");
                return;
            }

            WriteAllText(PlayerCompilePath, "RUNNING  " + platform + "  " + Timestamp() + "\n");
            // the player compile takes the script set the AssetDatabase knows; files added or deleted while the Editor
            // was unfocused are not in it until an import. In Play Mode the import is skipped unless the prefs hold
            // its compile until Play ends (see refresh).
            if (!EditorApplication.isPlaying || EditorPrefs.GetInt("ScriptCompilationDuringPlay", 0) == 1)
                AssetDatabase.Refresh();
            lock (Gate) PlayerCompileLines.Clear();

            ScriptCompilationResult result;
            _compilingPlayer = true;
            try
            {
                if (Directory.Exists(PlayerCompileDir)) Directory.Delete(PlayerCompileDir, true);
                result = PlayerBuildInterface.CompilePlayerScripts(
                    new ScriptCompilationSettings { target = target, group = group }, PlayerCompileDir);
            }
            finally
            {
                _compilingPlayer = false;
            }

            var sb = new StringBuilder(1024);
            lock (Gate)
            {
                int errors = 0;
                foreach (string line in PlayerCompileLines)
                    if (line.IndexOf("): error ", StringComparison.Ordinal) >= 0) errors++;

                // An empty result is the failure signal Unity's own build pipeline uses; errors may still be unlogged.
                bool failed = errors > 0 || result.assemblies == null || result.assemblies.Count == 0;
                sb.Append(failed ? "FAILED  " : "OK  ").Append(platform).Append("  ")
                  .Append(errors).Append(" error(s), ").Append(PlayerCompileLines.Count - errors).Append(" warning(s), ")
                  .Append(result.assemblies == null ? 0 : result.assemblies.Count).Append(" assemblies  ")
                  .Append(Timestamp()).Append('\n');
                if (failed && errors == 0) sb.Append("No compiler message was logged; see console.log\n");
                foreach (string line in PlayerCompileLines) sb.Append(line).Append('\n');
            }
            WriteAllText(PlayerCompilePath, sb.ToString());
        }

        // ---- play-mode capture ----
        // "play-capture [seconds]": refresh and compile even while the Editor is unfocused, enter Play Mode with
        // runInBackground on (an unfocused Editor would otherwise freeze the game), save three Game view
        // screenshots and every error logged meanwhile, then leave Play Mode. The pending request lives in
        // SessionState so it survives the domain reload a project with reload enabled would do.

        static void RequestCapture(string argument)
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                WriteAllText(CapturePath, "BUSY  already in Play Mode  " + Timestamp() + "\n");
                return;
            }

            float seconds = float.TryParse(argument, System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out float parsed) ? parsed : DefaultCaptureSeconds;
            SessionState.SetFloat(CapturePendingKey, Mathf.Clamp(seconds, 1f, 30f));
            lock (Gate) CaptureErrors.Clear();
            _capturePending = true;
            WriteAllText(CapturePath, "PENDING  " + Timestamp() + "\n");
            AssetDatabase.Refresh();
        }

        static void TickCapture(double now)
        {
            float pending = SessionState.GetFloat(CapturePendingKey, 0f);

            if (pending > 0f && !EditorApplication.isPlayingOrWillChangePlaymode)
            {
                if (EditorUtility.scriptCompilationFailed)
                {
                    SessionState.EraseFloat(CapturePendingKey);
                    _capturePending = false;
                    WriteAllText(CapturePath, "COMPILE FAILED  " + Timestamp() + "  see compile.log\n");
                    return;
                }
                EditorApplication.isPlaying = true;
                return;
            }

            if (pending > 0f && EditorApplication.isPlaying && !_capturing)
            {
                SessionState.EraseFloat(CapturePendingKey);
                Directory.CreateDirectory(CaptureDir);
                foreach (string old in Directory.GetFiles(CaptureDir, "*.png")) File.Delete(old);

                _runInBackground = Application.runInBackground;
                Application.runInBackground = true;
                _captureStart = now;
                _captureSeconds = pending;
                _shotsTaken = 0;
                // the errors kept since the request stay: they include the ones thrown while the scene woke up
                _capturing = true;
                return;
            }

            if (!_capturing) return;

            if (!EditorApplication.isPlaying)
            {
                _capturing = false; // the user left Play Mode first
                _capturePending = false;
                Application.runInBackground = _runInBackground;
                WriteCaptureReport("STOPPED");
                return;
            }

            double elapsed = now - _captureStart;
            if (_shotsTaken < 3 && elapsed >= ShotTime(_shotsTaken))
            {
                _shotsTaken++;
                ScreenCapture.CaptureScreenshot(Path.GetFullPath(CaptureDir + "/shot-" + _shotsTaken + ".png"));
            }

            if (_shotsTaken == 3 && elapsed >= _captureSeconds + 0.5) // the last screenshot is written at frame end
            {
                _capturing = false;
                _capturePending = false;
                WriteCaptureReport(null);
                Application.runInBackground = _runInBackground;
                EditorApplication.isPlaying = false;
            }
        }

        static double ShotTime(int index) => index == 0 ? 0.5 : index == 1 ? _captureSeconds * 0.5 : _captureSeconds;

        static void WriteCaptureReport(string status)
        {
            var sb = new StringBuilder(1024);
            lock (Gate)
            {
                sb.Append(status ?? (CaptureErrors.Count == 0 ? "OK" : "ERRORS")).Append("  ")
                  .Append(_shotsTaken).Append(" shot(s), ").Append(CaptureErrors.Count).Append(" error(s)  ")
                  .Append(Timestamp()).Append('\n');
                for (int i = 0; i < _shotsTaken; i++)
                    sb.Append(CaptureDir).Append("/shot-").Append(i + 1).Append(".png  at ")
                      .Append(ShotTime(i).ToString("0.0", System.Globalization.CultureInfo.InvariantCulture)).Append(" s\n");
                foreach (string error in CaptureErrors) sb.Append(error).Append('\n');
            }
            WriteAllText(CapturePath, sb.ToString());
        }

        // ---- tests ----

        [MenuItem("Tools/Agent Bridge/Run EditMode Tests")]
        static void RunEditModeTestsMenu() => RunTests(TestMode.EditMode);

        static void RunTests(TestMode mode)
        {
            WriteAllText(TestsPath, "RUNNING " + mode + "  " + Timestamp() + "\n");
            _testApi.Execute(new ExecutionSettings(new Filter { testMode = mode }));
        }

        class ResultWriter : ICallbacks
        {
            public void RunStarted(ITestAdaptor testsToRun) { }
            public void TestStarted(ITestAdaptor test) { }
            public void TestFinished(ITestResultAdaptor result) { }

            public void RunFinished(ITestResultAdaptor result)
            {
                var sb = new StringBuilder(2048);
                sb.Append(result.TestStatus).Append("  ")
                  .Append(result.PassCount).Append(" passed, ")
                  .Append(result.FailCount).Append(" failed, ")
                  .Append(result.SkipCount).Append(" skipped  ")
                  .Append(Timestamp()).Append('\n');

                AppendFailures(sb, result);
                WriteAllText(TestsPath, sb.ToString());
            }

            static void AppendFailures(StringBuilder sb, ITestResultAdaptor node)
            {
                if (!node.HasChildren)
                {
                    if (node.TestStatus == TestStatus.Failed)
                    {
                        sb.Append("FAIL  ").Append(node.Test.FullName).Append('\n');
                        if (!string.IsNullOrEmpty(node.Message))
                            sb.Append("    ").Append(node.Message.Replace("\n", "\n    ").TrimEnd()).Append('\n');
                        if (!string.IsNullOrEmpty(node.StackTrace))
                            sb.Append("    ").Append(node.StackTrace.Replace("\n", "\n    ").TrimEnd()).Append('\n');
                    }
                    return;
                }

                foreach (ITestResultAdaptor child in node.Children) AppendFailures(sb, child);
            }
        }

        // ---- io ----

        static string ScrapeEditorLogErrors()
        {
            const string EditorLog = "Logs/Editor.log";
            const int MaxScraped = 40;
            if (!File.Exists(EditorLog)) return string.Empty;

            var found = new List<string>(MaxScraped);
            try
            {
                using (var stream = new FileStream(EditorLog, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                using (var reader = new StreamReader(stream))
                {
                    string line;
                    while ((line = reader.ReadLine()) != null)
                    {
                        if (line.IndexOf("): error CS", StringComparison.Ordinal) < 0) continue;
                        if (found.Contains(line)) continue;
                        if (found.Count == MaxScraped) found.RemoveAt(0);
                        found.Add(line);
                    }
                }
            }
            catch (IOException)
            {
                return string.Empty;
            }

            var sb = new StringBuilder(found.Count * 96);
            for (int i = 0; i < found.Count; i++) sb.Append(found[i]).Append('\n');
            return sb.ToString();
        }

        internal static string Timestamp() => DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");

        static bool FirstLineStarts(string path, string prefix)
        {
            try
            {
                using (var reader = new StreamReader(path))
                    return (reader.ReadLine() ?? "").StartsWith(prefix, StringComparison.Ordinal);
            }
            catch (IOException)
            {
                return false; // missing or locked: nothing left open
            }
        }

        static void WriteAllText(string path, string contents)
        {
            try
            {
                Directory.CreateDirectory(Dir);
                File.WriteAllText(path, contents);
            }
            catch (IOException e)
            {
                Debug.LogWarning("[AgentBridge] could not write " + path + ": " + e.Message);
            }
        }
    }
}
