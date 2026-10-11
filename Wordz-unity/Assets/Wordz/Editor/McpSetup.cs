using System.IO;
using UnityEditor;
using UnityEngine;
using MCPForUnity.Editor.Services;
using MCPForUnity.Editor.Services.Transport;

namespace Wordz.Editor
{
    public static class McpSetup
    {
        [MenuItem("Wordz/Connect Unity MCP")]
        public static async void Connect()
        {
            EditorPrefs.SetBool("MCPForUnity.UseHttpTransport", true);
            bool connected = await MCPServiceLocator.TransportManager.StartAsync(TransportMode.Http);
            Directory.CreateDirectory("Logs");
            var state = MCPServiceLocator.TransportManager.GetState(TransportMode.Http);
            File.WriteAllText("Logs/wordz-mcp.txt", (connected ? "PASS" : "FAIL") + " session=" + state.SessionId + " project=" + Application.dataPath);
            Debug.Log("Wordz MCP connection: " + (connected ? "PASS" : "FAIL"));
        }
    }
}
