using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityGameFramework.Runtime;

namespace Wordz.Editor
{
    public static class ProjectSetup
    {
        private const string ScenePath = "Assets/Wordz/Scenes/Bootstrap.unity";
        private const string PrefabPath = "Assets/Wordz/Prefabs/GameFramework.prefab";

        [MenuItem("Wordz/Configure 2D Project")]
        public static void Configure()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            if (File.Exists(ScenePath) || File.Exists(PrefabPath))
            {
                Debug.Log("Wordz setup already exists; preserving existing assets.");
                return;
            }
            Directory.CreateDirectory("Assets/Wordz/Scenes");
            Directory.CreateDirectory("Assets/Wordz/Prefabs");
            AssetDatabase.Refresh();
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cameraObject = new GameObject("Main Camera", typeof(Camera), typeof(AudioListener));
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0, 0, -10);
            var camera = cameraObject.GetComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 5;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.12f, 0.14f, 0.18f);
            var source = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/ThirdParty/GameFramework/GameFramework.prefab");
            if (source == null) throw new InvalidOperationException("GameFramework prefab is missing.");
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(source);
            var procedure = instance.GetComponentInChildren<ProcedureComponent>(true);
            var serialized = new SerializedObject(procedure);
            var names = serialized.FindProperty("m_AvailableProcedureTypeNames");
            names.arraySize = 1;
            names.GetArrayElementAtIndex(0).stringValue = typeof(Framework.ProcedureBootstrap).FullName;
            serialized.FindProperty("m_EntranceProcedureTypeName").stringValue = typeof(Framework.ProcedureBootstrap).FullName;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            PrefabUtility.RecordPrefabInstancePropertyModifications(procedure);
            PrefabUtility.SaveAsPrefabAssetAndConnect(instance, PrefabPath, InteractionMode.AutomatedAction);
            EditorSettings.defaultBehaviorMode = EditorBehaviorMode.Mode2D;
            EditorSettings.serializationMode = SerializationMode.ForceText;
            PlayerSettings.productName = "Wordz";
            PlayerSettings.companyName = "Wordz";
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Standalone, "com.wordz.game");
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] {new EditorBuildSettingsScene(ScenePath, true)};
            AssetDatabase.SaveAssets();
            Debug.Log("Wordz 2D project configured");
        }

        public static void ConfigureAndExit()
        {
            Configure();
            EditorApplication.Exit(0);
        }

        public static void Smoke()
        {
            Configure();
            if (!File.Exists(ScenePath)) throw new InvalidOperationException("Scene configuration was cancelled.");
            EditorSceneManager.OpenScene(ScenePath);
            SessionState.SetBool("WordzSmokeActive", true);
            SessionState.SetFloat("WordzSmokeDeadline", (float)EditorApplication.timeSinceStartup + 90);
            ResumeSmoke();
            EditorApplication.isPlaying = true;
        }

        [InitializeOnLoadMethod]
        private static void ResumeSmoke()
        {
            if (!SessionState.GetBool("WordzSmokeActive", false)) return;
            Application.logMessageReceived -= OnLog;
            Application.logMessageReceived += OnLog;
            EditorApplication.update -= CheckDeadline;
            EditorApplication.update += CheckDeadline;
        }

        private static void CheckDeadline()
        {
            if (EditorApplication.timeSinceStartup < SessionState.GetFloat("WordzSmokeDeadline", 0)) return;
            SessionState.EraseBool("WordzSmokeActive");
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/wordz-smoke.txt", "FAIL: bootstrap did not enter procedure within 90 seconds");
            FinishSmoke(1);
        }
        private static void OnLog(string message, string trace, LogType type)
        {
            if (message != "Wordz GameFramework ready") return;
            SessionState.EraseBool("WordzSmokeActive");
            Application.logMessageReceived -= OnLog;
            EditorApplication.update -= CheckDeadline;
            var procedure = GameEntry.GetComponent<ProcedureComponent>().CurrentProcedure;
            var camera = Camera.main;
            bool passed = procedure is Framework.ProcedureBootstrap && camera != null && camera.orthographic;
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/wordz-smoke.txt", passed ? "PASS: actual GameFramework procedure entered; orthographic camera ready" : "FAIL: invalid procedure or camera");
            if (passed) SavePreview(camera);
            EditorApplication.delayCall += () => FinishSmoke(passed ? 0 : 1);
        }

        private static void FinishSmoke(int exitCode)
        {
            if (SessionState.GetBool("WordzSmokeLeaveOpen", false))
            {
                SessionState.EraseBool("WordzSmokeLeaveOpen");
                EditorApplication.isPlaying = false;
                return;
            }
            EditorApplication.Exit(exitCode);
        }

        private static void SavePreview(Camera camera)
        {
            var target = new RenderTexture(1280, 720, 24);
            var previousTarget = camera.targetTexture;
            var previousActive = RenderTexture.active;
            var pixels = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            try
            {
                camera.targetTexture = target;
                camera.Render();
                RenderTexture.active = target;
                pixels.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0);
                pixels.Apply();
                string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "production", "qa", "evidence"));
                Directory.CreateDirectory(folder);
                File.WriteAllBytes(Path.Combine(folder, "bootstrap.png"), pixels.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(pixels);
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        [MenuItem("Wordz/Validate Framework Startup")]
        public static void SmokeInEditor()
        {
            SessionState.SetBool("WordzSmokeLeaveOpen", true);
            Smoke();
        }
    }
}
