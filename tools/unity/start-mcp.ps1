$ErrorActionPreference = 'Stop'
$wordzRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$wordzProbe = New-Object System.Net.Sockets.TcpClient
try {
    $wordzConnect = $wordzProbe.ConnectAsync('127.0.0.1', 8080)
    if ($wordzConnect.Wait(1000) -and $wordzProbe.Connected) {
        Write-Output 'Local port 8080 is already listening. Reuse the existing MCP server.'
        exit 0
    }
} catch { } finally { $wordzProbe.Dispose() }
$wordzLog = Join-Path $wordzRoot 'production/session-logs'
New-Item -ItemType Directory -Path $wordzLog -Force | Out-Null
Start-Process -FilePath (Get-Command uvx.exe).Source -ArgumentList @('--from','mcpforunityserver==10.2.0','mcp-for-unity','--transport','http','--http-url','http://127.0.0.1:8080','--project-scoped-tools') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $wordzLog 'mcp-out.log') -RedirectStandardError (Join-Path $wordzLog 'mcp-error.log') | Out-Null
Write-Output 'Started the pinned Unity MCP HTTP server. In Unity use Wordz/Connect Unity MCP.'
