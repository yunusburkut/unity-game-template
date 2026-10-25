using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
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
    /// The report is written once compilation settles, so a domain reload cannot race it.
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
        const string CapturePendingKey = "AgentBridge.CaptureSeconds";
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

        static bool _consoleDirty;
        static bool _reportPending = true;
        static double _nextFlush;
        static double _nextPoll;
        static TestRunnerApi _testApi;
        static bool _capturing;
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

            // If the Editor cold-started on broken sources, no handler was alive to see the
            // messages. Unity's own log still has them, and this is the only chance to report them.
            if (EditorUtility.scriptCompilationFailed)
            {
                WriteAllText(CompilePath, "FAILED  " + Timestamp() + "\n" + ScrapeEditorLogErrors());
                _reportPending = false;
            }
        }

        // ---- compilation ----

        static void OnCompilationStarted(object _)
        {
            lock (Gate)
            {
                CompileLines.Clear();
                _reportPending = true;
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
        }

        static bool IsCompilerMessage(string message) =>
            message.IndexOf("): error CS", StringComparison.Ordinal) >= 0 ||
            message.IndexOf("): warning CS", StringComparison.Ordinal) >= 0;

        // ---- console ----

        static void OnLogMessage(string condition, string stackTrace, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert && type != LogType.Warning)
                return;

            if (_capturing && type != LogType.Warning)
            {
                lock (Gate)
                {
                    if (CaptureErrors.Count < CompileCapacity)
                        CaptureErrors.Add(type + "  " + condition + (string.IsNullOrEmpty(stackTrace)
                            ? "" : "\n    " + stackTrace.Replace("\n", "\n    ").TrimEnd()));
                }
            }

            if (IsCompilerMessage(condition))
            {
                lock (Gate)
                {
                    if (CompileLines.Contains(condition)) return; // Unity repeats each message per target
                    if (CompileLines.Count == CompileCapacity) CompileLines.RemoveAt(0);
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

            if (_consoleDirty && now >= _nextFlush)
            {
                _nextFlush = now + FlushInterval;
                FlushConsole();
            }

            if (now < _nextPoll) return;
            _nextPoll = now + PollInterval;

            if (EditorApplication.isUpdating || !File.Exists(RequestPath)) return;

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

            if (request.StartsWith("build ", StringComparison.OrdinalIgnoreCase) &&
                BuildMenu.TryParse(request.Substring(6), out BuildTarget target))
            {
                // a build switches platforms and reimports; never start one from inside the update tick
                EditorApplication.delayCall += () => BuildMenu.Build(target);
                return;
            }

            WriteAllText(TestsPath, "Unknown request: '" + request + "'. Supported: run-tests [playmode], play-capture [seconds], build windows|android|ios|webgl\n");
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
                lock (Gate) CaptureErrors.Clear();
                _capturing = true;
                return;
            }

            if (!_capturing) return;

            if (!EditorApplication.isPlaying)
            {
                _capturing = false; // the user left Play Mode first
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
            if (_testApi == null)
            {
                _testApi = ScriptableObject.CreateInstance<TestRunnerApi>();
                _testApi.RegisterCallbacks(new ResultWriter());
            }

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

        static string Timestamp() => DateTime.Now.ToString("HH:mm:ss");

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
