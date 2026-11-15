using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using __GAME__.Core;
using NUnit.Framework;
using UnityEngine;

namespace __GAME__.Tests.EditMode
{
    /// <summary>
    /// Core is the deterministic simulation (CLAUDE.md, Assembly boundary). The compiler cannot tell a
    /// <c>Time.deltaTime</c> in Core from one in Game, so these checks make a breach fail the EditMode run
    /// instead of waiting for a reviewer to notice it.
    /// Ceiling: the source scan is a token list, not a parser. It ignores // comments but not strings or
    /// block comments; a new banned API goes into <see cref="Banned"/>.
    /// </summary>
    public sealed class CoreBoundaryTests
    {
        static readonly System.Reflection.Assembly Core = typeof(Ease).Assembly;

        // Engine assemblies Core must never link against: physics, the old input manager, the Input System,
        // the Editor. Mathf, vectors and data-only ScriptableObject configs live in CoreModule and stay allowed.
        static readonly string[] BannedAssemblies =
        {
            "UnityEngine.PhysicsModule", "UnityEngine.Physics2DModule", "UnityEngine.InputLegacyModule",
            "UnityEngine.InputModule", "Unity.InputSystem", "UnityEditor",
        };

        // The APIs CLAUDE.md bans from Core. Time, GameObject and SceneManager live in CoreModule, so only
        // the source can show them. The lookbehind lets a Core field named Time (state.Time) through.
        static readonly Regex Banned = new Regex(
            @"\b(MonoBehaviour|GameObject|SceneManager|SceneManagement)\b" +
            @"|(?<![\w.])(Time|Input|Physics|Physics2D)\.\w" +
            @"|\bUnityEngine\.(Time|Input|Physics|Physics2D)\b",
            RegexOptions.Compiled);

        [Test]
        public void Core_DeclaresNoComponent()
        {
            var components = Core.GetTypes().Where(t => typeof(Component).IsAssignableFrom(t)).ToArray();
            Assert.IsEmpty(components, "Core bileşen (MonoBehaviour) tanımlamamalı: " +
                                       string.Join(", ", components.Select(t => t.FullName)));
        }

        [Test]
        public void Core_LinksNoSceneOrInputAssembly()
        {
            var linked = Core.GetReferencedAssemblies().Select(a => a.Name)
                             .Where(n => BannedAssemblies.Any(b => n == b || n.StartsWith(b + ".")))
                             .ToArray();
            Assert.IsEmpty(linked, "Core bu assembly'lere bağlanmamalı: " + string.Join(", ", linked));
        }

        [Test]
        public void CoreSource_UsesNoSceneOrFrameApi()
        {
            string folder = Path.Combine(Application.dataPath, "__GAME__", "Core");
            Assert.IsTrue(Directory.Exists(folder), "Core klasörü bulunamadı: " + folder);

            var hits = Directory.GetFiles(folder, "*.cs", SearchOption.AllDirectories)
                .SelectMany(file => File.ReadAllLines(file).Select((line, i) => new { file, line, i }))
                .Select(x => new { x.file, x.i, code = StripLineComment(x.line) })
                .Where(x => Banned.IsMatch(x.code))
                .Select(x => Path.GetFileName(x.file) + ":" + (x.i + 1) + "  " + x.code.Trim())
                .ToArray();

            Assert.IsEmpty(hits, "Core sahne/kare API'si kullanmamalı (Time, Input, Physics ve " +
                                 "sahne tipleri Game'e ait; dt parametre olarak gelir):\n" + string.Join("\n", hits));
        }

        static string StripLineComment(string line)
        {
            int at = line.IndexOf("//", System.StringComparison.Ordinal);
            return at < 0 ? line : line.Substring(0, at);
        }
    }
}
