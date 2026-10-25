using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace __GAME__.Tests.PlayMode
{
    // Loads the real first scene and lets it run. An exception or error log from any Awake, Start or Update fails the
    // test, so this catches the "throws on start" class of bugs without anyone pressing Play.
    public class MainSceneTests
    {
        const string Scene = "Main";
        const float RunSeconds = 2f;

        [UnityTest]
        public IEnumerator MainScene_RunsWithoutErrors()
        {
            yield return SceneManager.LoadSceneAsync(Scene);
            Assert.AreEqual(Scene, SceneManager.GetActiveScene().name, "Main scene did not load; is it in the build settings?");

            var end = Time.realtimeSinceStartup + RunSeconds;
            while (Time.realtimeSinceStartup < end) yield return null;
        }
    }
}
