using UnityEditor;

namespace __GAME__.Editor
{
    /// <summary>The coop-multiplayer pack's setup step, run by ProjectSetup after its own.</summary>
    static class CoopSetup
    {
        [ProjectSetupStep]
        public static void Run()
        {
            // a host whose window loses focus must keep ticking, or every client freezes with it; two builds on one
            // machine (the network test) only work this way
            PlayerSettings.runInBackground = true;
        }
    }
}
