using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.Build.Player;
using UnityEditor.Compilation;
using UnityEditor.TestTools.TestRunner.Api;
using UnityEngine;

namespace GameKit.Editor
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
    ///
    /// Status-line contract: plugin/bin/gk-bridge turns the first line of each log into a PASS / FAIL / UNKNOWN gate,
    /// and plugin/test-hooks.ps1 feeds it fixed lines. It matches these prefixes and fragments, so rewording one here
    /// needs the same change in both readers (and a GameKit release): "REFRESHED", "no script changes",
    /// "in Play Mode", "SKIPPED", "Editor restarted", "Unknown request", "OK  " / "FAILED  " (compile-player.log
    /// adds the platform: "OK  ios"), "module is not installed", and tests.log's "&lt;TestStatus&gt;  &lt;n&gt; passed,".
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
        const string CaptureErrorsKey = "AgentBridge.CaptureErrors";
        const char CaptureErrorSeparator = '\u001e'; // ASCII record separator: never in a log message
        const string CompileRanKey = "AgentBridge.CompileRan";
        const string CompileLinesKey = "AgentBridge.CompileLines";
        const string SessionStartedKey = "AgentBridge.SessionStarted";
        const string RefreshAckKey = "AgentBridge.RefreshAck";
        const string PendingBuildKey = "AgentBridge.PendingBuild";
        const string PlayerCheckedKey = "AgentBridge.PlayerChecked";
        const string CapturePlayAskedKey = "AgentBridge.CapturePlayAsked";
        const string RunInBackgroundKey = "AgentBridge.RunInBackground"; // 0 none kept, 1 false, 2 true
        const double RefreshSettle = 2.0;
        // a script newer than compile.log waits this much longer once: a large project's compile can start late
        const double RefreshSlowSettle = 8.0;
        // from the first Play Mode request after the last compile: a capture Unity keeps refusing ends FAILED
        const double PlayModeStartTimeout = 30.0;
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
        static bool _refreshExtended;
        static double _buildNotBefore;
        static double _captureNotBefore;
        static TestRunnerApi _testApi;
        static bool _capturing;
        // a capture's errors start counting before Play Mode starts, so the ones the scene's Awake throws count too
        static volatile bool _capturePending;
        static double _captureStart;
        static float _captureSeconds;
        static int _shotsTaken;

        static AgentBridge()
        {
            // An Asset Import Worker loads this assembly too, with a fresh SessionState: it would take requests and
            // close the main Editor's open refresh, build or test run as "Editor restarted".
            if (AssetDatabase.IsAssetImportWorkerProcess()) return;
            Directory.CreateDirectory(Dir);
            // bridge.log marks a bridge that knows refresh: gk-bridge and the plugin's hooks look for it, so a fresh
            // game needs it before its first refresh
            if (!File.Exists(BridgePath))
                WriteAllText(BridgePath, "READY  " + Timestamp() + "  send refresh to import and compile\n");

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
            // A clean compile reloads the domain before the report is written, and the statics go with it: its
            // warnings come back from SessionState (KeepAcrossReload), or compile.log would read a bare OK.
            string keptCompile = SessionState.GetString(CompileLinesKey, "");
            SessionState.EraseString(CompileLinesKey);
            if (_reportPending && keptCompile.Length > 0)
                lock (Gate) CompileLines.AddRange(keptCompile.Split(CaptureErrorSeparator));

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
            // A capture's errors from before a reload (the refresh's compile, entering Play Mode with domain reload on)
            // come back from SessionState, so capture.log holds every error since the request.
            AssemblyReloadEvents.beforeAssemblyReload += KeepAcrossReload;
            string kept = SessionState.GetString(CaptureErrorsKey, "");
            SessionState.EraseString(CaptureErrorsKey);
            // A reload after the capture started (a script saved mid-Play with Unity's default "Recompile And Continue
            // Playing") lost its state, which lives in statics: close it, or capture.log stays PENDING and gk-bridge
            // refuses every request until a restart.
            bool captureLost = !editorStarted && !_capturePending && FirstLineStarts(CapturePath, "PENDING");
            if ((_capturePending || captureLost) && kept.Length > 0)
                lock (Gate) CaptureErrors.InsertRange(0, kept.Split(CaptureErrorSeparator));
            if (captureLost)
            {
                RestoreRunInBackground();
                WriteCaptureReport("STOPPED", "a domain reload (script recompile) ended the capture; capture again");
            }

            // A reload that was no compile (entering Play Mode) inside a refresh's settle time lost its timer; restart it.
            if (SessionState.GetBool(RefreshAckKey, false) && !SessionState.GetBool(CompileRanKey, false))
                _refreshAckAt = EditorApplication.timeSinceStartup + RefreshSettle;

            // If the Editor cold-started on broken sources, no handler was alive to see the
            // messages. Unity's own log still has them, and this is the only chance to report them.
            if (FlagIsEditors && EditorUtility.scriptCompilationFailed)
            {
                WriteAllText(CompilePath, "FAILED  " + Timestamp() + "\n" + ScrapeEditorLogErrors());
                SessionState.EraseBool(CompileRanKey);
                _reportPending = false;
            }
        }

        static void KeepAcrossReload()
        {
            lock (Gate)
            {
                // the reload that ends a clean compile: its warnings are reported after it
                if (SessionState.GetBool(CompileRanKey, false) && CompileLines.Count > 0)
                    SessionState.SetString(CompileLinesKey, string.Join(CaptureErrorSeparator.ToString(), CompileLines));
                if (_capturePending && CaptureErrors.Count > 0)
                    SessionState.SetString(CaptureErrorsKey, string.Join(CaptureErrorSeparator.ToString(), CaptureErrors));
            }
        }

        // ---- compilation ----

        static void OnCompilationStarted(object _)
        {
            if (_compilingPlayer) return; // a player-script check is not the Editor's compile
            SessionState.SetBool(CompileRanKey, true);
            SessionState.EraseFloat(CapturePlayAskedKey); // a pending capture's Play Mode wait starts after this compile
            SessionState.EraseBool(PlayerCheckedKey); // this compile overwrites the flag a check left
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
                        if (IsError(CompileLines[i])) errors++;
                    }

                    Builder.Append(errors).Append(" error(s), ")
                           .Append(CompileLines.Count - errors).Append(" warning(s)  ")
                           .Append(Timestamp()).Append('\n');

                    // errors first, so the head of the log (what gk-bridge prints) holds what to fix
                    for (int i = 0; i < CompileLines.Count; i++)
                        if (IsError(CompileLines[i])) Builder.Append(CompileLines[i]).Append('\n');
                    for (int i = 0; i < CompileLines.Count; i++)
                        if (!IsError(CompileLines[i])) Builder.Append(CompileLines[i]).Append('\n');
                }
            }

            WriteAllText(CompilePath, Builder.ToString());
            ReportSilentFailure();
            SessionState.EraseBool(CompileRanKey);
            _compilingEditor = false;
            if (SessionState.GetBool(RefreshAckKey, false)) AckRefresh("compiled: see compile.log");
        }

        static void AckRefresh(string outcome)
        {
            _refreshExtended = false;
            SessionState.EraseBool(RefreshAckKey);
            WriteAllText(BridgePath, "REFRESHED  " + Timestamp() + "  " + outcome + "\n");
        }

        // An assembly-level failure (cyclic asmdef references, a duplicate assembly name) logs no "): error CS" line
        // and can stop the compile before it starts, so a clean compile.log would hide it; Unity's flag still knows.
        static void ReportSilentFailure()
        {
            if (!FlagIsEditors || !EditorUtility.scriptCompilationFailed || !CompileLogClean()) return;
            WriteAllText(CompilePath, "FAILED  " + Timestamp() + "  compile failed without a CS error: see console.log\n");
        }

        // Unity's flag holds the last compile's result, and a player-script check is a compile too (probed on 6000.6:
        // a failed `compile android` sets it, a passed one clears it, the next Editor compile overwrites it; a failed
        // BuildPlayer leaves it unset). A check that flipped it requests that compile, which runs with no script changed
        // too (probed on 6000.6: started, reloaded, flag back); until it starts, compile.log is the Editor's state.
        static bool FlagIsEditors => !SessionState.GetBool(PlayerCheckedKey, false);

        static bool CompileLogClean() => FirstLineStarts(CompilePath, "OK") || FirstLineStarts(CompilePath, "0 error(s)");

        static bool IsCompilerMessage(string message) =>
            message.IndexOf("): error CS", StringComparison.Ordinal) >= 0 ||
            message.IndexOf("): warning CS", StringComparison.Ordinal) >= 0;

        static bool IsError(string compilerLine) => compilerLine.IndexOf("): error ", StringComparison.Ordinal) >= 0;

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
                    if (CompileLines.Count == CompileCapacity)
                    {
                        // keep the first ones, usually the cause; an error still takes the place of the last warning
                        // kept, so a full recompile's vendored warnings cannot push every error out
                        if (!IsError(condition)) return;
                        int warning = CompileLines.FindLastIndex(kept => !IsError(kept));
                        if (warning < 0) return;
                        CompileLines.RemoveAt(warning);
                    }
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
            // FlagIsEditors: BuildMenu reads Unity's flag, so a build waits for the Editor compile a player-script check
            // requested (it starts within seconds; probed on 6000.6).
            if (pendingBuild.Length > 0 && now >= _buildNotBefore && !EditorApplication.isUpdating &&
                !EditorApplication.isPlayingOrWillChangePlaymode && FlagIsEditors)
            {
                SessionState.EraseString(PendingBuildKey);
                StartBuild(pendingBuild);
                return;
            }

            // A refresh whose compile has not started within the settle time changed no script. A script newer than
            // compile.log (gk-bridge's own freshness test) waits once more, since a large project's compile can start
            // late. Ceiling: a compile that starts after both waits, or a file touched without a change (no compile
            // follows, so each refresh pays the second wait until the next compile), still reads as no script changes.
            if (_refreshAckAt > 0 && now >= _refreshAckAt)
            {
                _refreshAckAt = 0;
                if (SessionState.GetBool(RefreshAckKey, false))
                {
                    if (!_refreshExtended && ScriptNewerThanCompileLog())
                    {
                        _refreshExtended = true;
                        _refreshAckAt = now + RefreshSlowSettle;
                    }
                    else
                    {
                        ReportSilentFailure();
                        AckRefresh("no script changes");
                    }
                }
            }

            if (_consoleDirty && now >= _nextFlush)
            {
                _nextFlush = now + FlushInterval;
                FlushConsole();
            }

            if (now < _nextPoll) return;
            _nextPoll = now + PollInterval;

            // A refresh's settle time holds the next request too, until its compile starts or the time runs out (the
            // timer always clears itself above, so nothing waits on it for good). So does a capture from its request to
            // its report: a test run or a compile check inside it would cut its Play Mode short or hitch its shots
            // (a capture always ends: compile failed, its report, the user leaving Play Mode, Play Mode not starting
            // within PlayModeStartTimeout, a domain reload mid-capture, or a restart).
            if (pendingBuild.Length > 0 || _refreshAckAt > 0 || EditorApplication.isUpdating || !File.Exists(RequestPath) ||
                TestRunOpen() || _capturing || SessionState.GetFloat(CapturePendingKey, 0f) > 0f) return;

            string request;
            try
            {
                request = File.ReadAllText(RequestPath).Trim();
                // read between a writer's truncate and its write: retry next poll; a file a crash left empty is dropped
                if (request.Length == 0 && (DateTime.Now - File.GetLastWriteTime(RequestPath)).TotalSeconds < 5) return;
                File.Delete(RequestPath);
                if (request.Length == 0) return;
            }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
            {
                return; // still being written (or held by a sync tool or antivirus); retry next poll
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
                _refreshExtended = false;
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
                + "compile ios|android|webgl, run-tests [playmode], play-capture [seconds], "
                + "build " + BuildMenu.TargetNames + " [dev]\n");
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
        // "compile ios|android|webgl": compiles the player scripts for that target into Temp/ without switching the
        // active target, so code behind UNITY_IOS / UNITY_ANDROID / UNITY_WEBGL is type-checked while the Editor stays on Windows. The
        // compiler's messages arrive on the log stream, which OnLogMessage diverts here.

        static void CompilePlayerScripts(string platform)
        {
            BuildTarget target;
            BuildTargetGroup group;
            if (platform == "ios") { target = BuildTarget.iOS; group = BuildTargetGroup.iOS; }
            else if (platform == "android") { target = BuildTarget.Android; group = BuildTargetGroup.Android; }
            else if (platform == "webgl") { target = BuildTarget.WebGL; group = BuildTargetGroup.WebGL; }
            else
            {
                WriteAllText(PlayerCompilePath, "Unknown platform '" + platform + "'  " + Timestamp() + "  use ios, android or webgl\n");
                return;
            }

            if (!BuildPipeline.IsBuildTargetSupported(group, target))
            {
                WriteAllText(PlayerCompilePath, "UNSUPPORTED  " + platform + "  the platform module is not installed  "
                    + Timestamp() + "\n");
                return;
            }

            // the player compile takes the script set the AssetDatabase knows; files added or deleted while the Editor
            // was unfocused are not in it until an import. In Play Mode that import would reload the domain unless the
            // prefs hold its compile until Play ends (see refresh), so without them the check is not run at all.
            if (EditorApplication.isPlaying && EditorPrefs.GetInt("ScriptCompilationDuringPlay", 0) != 1)
            {
                WriteAllText(PlayerCompilePath, "SKIPPED  " + platform + "  in Play Mode: compile again after Play ends  "
                    + Timestamp() + "\n");
                return;
            }
            WriteAllText(PlayerCompilePath, "RUNNING  " + platform + "  " + Timestamp() + "\n");
            AssetDatabase.Refresh();
            lock (Gate) PlayerCompileLines.Clear();

            ScriptCompilationResult result = default;
            string error = null;
            bool editorFailed = EditorUtility.scriptCompilationFailed;
            _compilingPlayer = true;
            try
            {
                if (Directory.Exists(PlayerCompileDir)) Directory.Delete(PlayerCompileDir, true);
                result = PlayerBuildInterface.CompilePlayerScripts(
                    new ScriptCompilationSettings { target = target, group = group }, PlayerCompileDir);
            }
            catch (Exception e) // a locked file in Temp/: answer now, not with RUNNING until the Editor restarts
            {
                error = e.Message;
            }
            finally
            {
                _compilingPlayer = false;
            }
            // BuildMenu and Unity's own Play button read the flag too: an Editor compile gives it back to the Editor.
            if (EditorUtility.scriptCompilationFailed != editorFailed)
            {
                SessionState.SetBool(PlayerCheckedKey, true);
                CompilationPipeline.RequestScriptCompilation();
            }
            if (error != null) // not FAILED: the code was never checked, so gk-bridge reads it as UNKNOWN
            {
                WriteAllText(PlayerCompilePath, "ERROR  " + platform + "  " + error + "  " + Timestamp() + "\n");
                return;
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

        /// <summary>
        /// Batch entry for a CI job or a script, with the Editor closed: <c>Unity -batchmode -projectPath &lt;game&gt; -executeMethod
        /// GameKit.Editor.AgentBridge.CompilePlayerScriptsBatch -platform ios|android|webgl</c>. Runs the same check as
        /// "compile &lt;platform&gt;", leaves its report in compile-player.log and exits 0 on OK, 2 on UNSUPPORTED (the
        /// platform module is not installed: a skip, not a pass) and 1 on anything else. No -quit: it exits itself.
        /// A caller (test-template.ps1, the ci-github pack's workflow) reads these exit codes: change it with them.
        /// </summary>
        static void CompilePlayerScriptsBatch()
        {
            string[] args = Environment.GetCommandLineArgs();
            int at = Array.IndexOf(args, "-platform");
            string platform = at >= 0 && at + 1 < args.Length ? args[at + 1].Trim().ToLowerInvariant() : "";
            CompilePlayerScripts(platform);
            int code = FirstLineStarts(PlayerCompilePath, "OK  ") ? 0 : FirstLineStarts(PlayerCompilePath, "UNSUPPORTED") ? 2 : 1;
            try { Console.Write(File.ReadAllText(PlayerCompilePath)); } // the report in Unity's -logFile too
            catch (IOException) { }
            EditorApplication.Exit(code);
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
            SessionState.EraseFloat(CapturePlayAskedKey);
            lock (Gate) CaptureErrors.Clear();
            _capturePending = true;
            WriteAllText(CapturePath, "PENDING  " + Timestamp() + "\n");
            AssetDatabase.Refresh();
            // the import's compile can start a few frames later (see refresh): Play Mode waits for it, not old code
            _captureNotBefore = EditorApplication.timeSinceStartup + RefreshSettle;
        }

        static void TickCapture(double now)
        {
            float pending = SessionState.GetFloat(CapturePendingKey, 0f);

            if (pending > 0f && !EditorApplication.isPlayingOrWillChangePlaymode)
            {
                if (now < _captureNotBefore) return;
                if (FlagIsEditors ? EditorUtility.scriptCompilationFailed : !CompileLogClean())
                {
                    EndPendingCapture("COMPILE FAILED  " + Timestamp() + "  see compile.log\n");
                    return;
                }
                // Unity can keep refusing Play Mode (a playModeStateChanged handler that cancels it, a modal dialog,
                // a scene that fails to load); without a deadline the capture would hold every request until a restart
                float asked = SessionState.GetFloat(CapturePlayAskedKey, 0f);
                if (asked <= 0f) SessionState.SetFloat(CapturePlayAskedKey, (float)now);
                else if (now - asked > PlayModeStartTimeout)
                {
                    EndPendingCapture("FAILED  " + Timestamp() + "  Play Mode did not start within "
                        + PlayModeStartTimeout + " s (a handler or dialog refused it?): see console.log\n");
                    return;
                }
                EditorApplication.isPlaying = true;
                return;
            }

            if (pending > 0f && EditorApplication.isPlaying && !_capturing)
            {
                SessionState.EraseFloat(CapturePendingKey);
                SessionState.EraseFloat(CapturePlayAskedKey);
                Directory.CreateDirectory(CaptureDir);
                foreach (string old in Directory.GetFiles(CaptureDir, "*.png")) File.Delete(old);

                // in SessionState, so the reload that loses this capture can still put it back
                SessionState.SetInt(RunInBackgroundKey, Application.runInBackground ? 2 : 1);
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
                RestoreRunInBackground();
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
                RestoreRunInBackground();
                EditorApplication.isPlaying = false;
            }
        }

        static void EndPendingCapture(string report)
        {
            SessionState.EraseFloat(CapturePendingKey);
            SessionState.EraseFloat(CapturePlayAskedKey);
            _capturePending = false;
            WriteAllText(CapturePath, report);
        }

        static void RestoreRunInBackground()
        {
            int kept = SessionState.GetInt(RunInBackgroundKey, 0);
            SessionState.EraseInt(RunInBackgroundKey);
            if (kept > 0) Application.runInBackground = kept == 2;
        }

        static double ShotTime(int index) => index == 0 ? 0.5 : index == 1 ? _captureSeconds * 0.5 : _captureSeconds;

        static void WriteCaptureReport(string status, string why = null)
        {
            var sb = new StringBuilder(1024);
            lock (Gate)
            {
                sb.Append(status ?? (CaptureErrors.Count == 0 ? "OK" : "ERRORS")).Append("  ")
                  .Append(_shotsTaken).Append(" shot(s), ").Append(CaptureErrors.Count).Append(" error(s)  ")
                  .Append(Timestamp()).Append(why == null ? "" : "  " + why).Append('\n');
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
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                WriteAllText(TestsPath, "SKIPPED  " + Timestamp() + "  in Play Mode: run the tests again after Play ends\n");
                return;
            }

            // The test runner asks to save dirty scenes first; in an unfocused Editor no one answers that dialog, and
            // its Cancel ends the run with no callback (tests.log would stay RUNNING), so every run refuses instead.
            var unsaved = new List<string>();
            for (int i = 0; i < UnityEditor.SceneManagement.EditorSceneManager.sceneCount; i++)
            {
                var open = UnityEditor.SceneManagement.EditorSceneManager.GetSceneAt(i);
                if (open.isDirty) unsaved.Add(string.IsNullOrEmpty(open.path) ? "(untitled)" : open.path);
            }
            if (unsaved.Count > 0)
            {
                string skipped = "unsaved scene(s): " + string.Join(", ", unsaved) + "; save them first";
                WriteAllText(TestsPath, "SKIPPED  " + Timestamp() + "  " + skipped + "\n");
                Debug.LogWarning("[AgentBridge] tests not run, " + skipped);
                return;
            }
            WriteAllText(TestsPath, "RUNNING " + mode + "  " + Timestamp() + "\n");
            try
            {
                _testApi.Execute(new ExecutionSettings(new Filter { testMode = mode }));
            }
            catch (Exception e) // a synchronous throw gets no callback: RUNNING would hold every request for 10 minutes
            {
                WriteAllText(TestsPath, "FAILED  " + Timestamp() + "  the test run did not start: " + e.Message + "\n");
            }
        }

        // A request taken under a running test job, the agent's or one started from the Test Runner window (RunStarted),
        // would recompile (a refresh queued by an edit) or enter Play Mode (a capture) mid-run, so requests wait in request.txt until RunFinished or OnError rewrites tests.log. Each finished
        // test touches tests.log (ResultWriter.TestFinished), so the 10 minutes count from the last progress and a long
        // suite stays open. Ceiling: a run cancelled from the Test Runner window gets no callback (UTF's
        // TestRunnerApi.IsRunActive is internal), so it holds them for 10 minutes after its last test (gk-bridge reads
        // the same write time); one test running over 10 minutes is taken for that, and a restart turns RUNNING into FAILED.
        // gk-bridge holds for the same time ($hold, plugin/bin/gk-bridge); change both together.
        static bool TestRunOpen() =>
            FirstLineStarts(TestsPath, "RUNNING") && File.GetLastWriteTime(TestsPath) > DateTime.Now.AddMinutes(-10);

        class ResultWriter : IErrorCallbacks
        {
            static DateTime _lastBeat;

            // A run started from the Test Runner window (or -runTests) holds requests too: a refresh an edit queued
            // would otherwise recompile mid-run. RunTests already wrote RUNNING for its own runs.
            public void RunStarted(ITestAdaptor testsToRun)
            {
                if (!FirstLineStarts(TestsPath, "RUNNING"))
                    WriteAllText(TestsPath, "RUNNING " + testsToRun.TestMode + "  " + Timestamp() + "\n");
            }
            public void TestStarted(ITestAdaptor test) { }

            public void TestFinished(ITestResultAdaptor result)
            {
                if ((DateTime.Now - _lastBeat).TotalSeconds < 10) return; // a heartbeat, not a write per test
                _lastBeat = DateTime.Now;
                try
                {
                    if (FirstLineStarts(TestsPath, "RUNNING")) File.SetLastWriteTime(TestsPath, _lastBeat);
                }
                catch (Exception e) when (e is IOException || e is UnauthorizedAccessException) { }
            }

            // A build error or a failing IPrebuildSetup ends the run here, and RunFinished never comes.
            public void OnError(string message) =>
                WriteAllText(TestsPath, "FAILED  " + Timestamp() + "  " + message + "\n");

            public void RunFinished(ITestResultAdaptor result)
            {
                // One [Ignore]d test marks the whole suite Skipped (NUnit); UTF's own window calls that Passed too.
                bool clean = result.FailCount == 0 && result.PassCount > 0 && result.TestStatus == TestStatus.Skipped;
                var sb = new StringBuilder(2048);
                sb.Append(clean ? TestStatus.Passed : result.TestStatus).Append("  ")
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

        // Unity 6 writes the project's Logs/Editor.log early in boot; an Editor that does not (an older one, or a launch
        // with another -logFile) leaves it in the per-user log
        static string EditorLogPath()
        {
            const string ProjectLog = "Logs/Editor.log";
            if (File.Exists(ProjectLog)) return ProjectLog;
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            switch (Application.platform)
            {
                case RuntimePlatform.OSXEditor: return Path.Combine(home, "Library/Logs/Unity/Editor.log");
                case RuntimePlatform.LinuxEditor: return Path.Combine(home, ".config/unity3d/Editor.log");
                default:
                    return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                        "Unity", "Editor", "Editor.log");
            }
        }

        static string ScrapeEditorLogErrors()
        {
            string log = EditorLogPath();
            string found = ScrapeErrors(log);
            // FAILED with no line would leave nothing to fix from: say where the errors were looked for
            return found.Length > 0 ? found : "No CS error line found in " + log + "; see console.log or the Console\n";
        }

        static string ScrapeErrors(string path)
        {
            const int MaxScraped = 40;
            if (!File.Exists(path)) return string.Empty;

            var found = new List<string>(MaxScraped);
            try
            {
                using (var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
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
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
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
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
            {
                return false; // missing, locked or denied: nothing left open
            }
        }

        // gk-bridge's freshness test, mirrored: a .cs/.asmdef/.asmref under Assets (Feel left out) or Packages
        // written after compile.log
        static bool ScriptNewerThanCompileLog()
        {
            if (!File.Exists(CompilePath)) return false;
            DateTime compiled = File.GetLastWriteTime(CompilePath);
            return NewerScript("Assets", compiled) || NewerScript("Packages", compiled);
        }

        static bool NewerScript(string dir, DateTime than)
        {
            try
            {
                foreach (string file in Directory.GetFiles(dir))
                {
                    string ext = Path.GetExtension(file);
                    if ((ext == ".cs" || ext == ".asmdef" || ext == ".asmref") && File.GetLastWriteTime(file) > than)
                        return true;
                }
                foreach (string sub in Directory.GetDirectories(dir))
                    if (!sub.Replace('\\', '/').Equals("Assets/Feel", StringComparison.OrdinalIgnoreCase) && NewerScript(sub, than))
                        return true;
            }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException) { }
            return false;
        }

        static void WriteAllText(string path, string contents)
        {
            try
            {
                Directory.CreateDirectory(Dir);
                File.WriteAllText(path, contents);
            }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
            {
                Debug.LogWarning("[AgentBridge] could not write " + path + ": " + e.Message);
            }
        }
    }
}
