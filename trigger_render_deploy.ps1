# OneTech — redeploy on Render (https://onetech-4yk7.onrender.com/)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Read-DotEnv {
    param([string]$Path)
    $vars = @{}
    if (-not (Test-Path $Path)) { return $vars }
    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$') {
            $vars[$matches[1]] = $matches[2].Trim()
        }
    }
    return $vars
}

function Ensure-RenderCli {
    $cli = "$env:TEMP\render-cli\cli_v1.1.0.exe"
    if (-not (Test-Path $cli)) {
        Write-Host 'Installing Render CLI...'
        $zip = "$env:TEMP\render-cli.zip"
        Invoke-WebRequest -Uri 'https://github.com/render-oss/cli/releases/download/v1.1.0/cli_1.1.0_windows_amd64.zip' -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath "$env:TEMP\render-cli" -Force
    }
    return $cli
}

$envVars = Read-DotEnv (Join-Path $Root '.env')
$hook = $envVars['RENDER_DEPLOY_HOOK']
$apiKey = $envVars['RENDER_API_KEY']
$serviceId = $envVars['RENDER_SERVICE_ID']

if ($hook) {
    Write-Host 'Triggering deploy via Deploy Hook...'
    Invoke-RestMethod -Method Post -Uri $hook | Out-Null
    Write-Host 'Deploy started. Wait 2-5 min: https://onetech-4yk7.onrender.com/' -ForegroundColor Green
    exit 0
}

if ($apiKey -and $serviceId) {
    $env:RENDER_API_KEY = $apiKey
    $env:CI = 'true'
    $cli = Ensure-RenderCli
    Write-Host "Deploying service $serviceId..."
    & $cli deploys create $serviceId --confirm --wait --output json
    Write-Host 'Done: https://onetech-4yk7.onrender.com/' -ForegroundColor Green
    exit 0
}

Write-Host ''
Write-Host '=== Render redeploy ===' -ForegroundColor Cyan
Write-Host 'Option A — CLI (one-time login):'
Write-Host '  1. Run: trigger_render_deploy.ps1 -Login'
Write-Host '  2. Approve login in browser'
Write-Host '  3. Run again: trigger_render_deploy.ps1'
Write-Host ''
Write-Host 'Option B — Dashboard (30 sec):'
Write-Host '  1. https://dashboard.render.com/'
Write-Host '  2. Open service onetech → Manual Deploy → Deploy latest commit'
Write-Host ''
Write-Host 'Option C — add to .env for auto-deploy on push:'
Write-Host '  RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-...?key=...'
Write-Host '  (Settings → Deploy Hook in Render dashboard)'
Write-Host ''

if ($args -contains '-Login') {
    $cli = Ensure-RenderCli
    & $cli login
    & $cli services list --output json
}
