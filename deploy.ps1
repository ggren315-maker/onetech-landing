# OneTech — auto deploy to free cloud (Koyeb or Render via GitHub)
param(
    [ValidateSet('koyeb', 'render', 'auto')]
    [string]$Target = 'auto'
)

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

function Ensure-Gh {
    $gh = "$env:ProgramFiles\GitHub CLI\gh.exe"
    if (-not (Test-Path $gh)) {
        Write-Host 'Installing GitHub CLI...'
        winget install --id GitHub.cli -e --accept-source-agreements --accept-package-agreements | Out-Null
    }
    return $gh
}

function Ensure-Koyeb {
    $koyeb = "$env:TEMP\koyeb\koyeb.exe"
    if (-not (Test-Path $koyeb)) {
        Write-Host 'Downloading Koyeb CLI...'
        $zip = "$env:TEMP\koyeb-cli.zip"
        Invoke-WebRequest -Uri 'https://github.com/koyeb/koyeb-cli/releases/download/v5.10.2/koyeb-cli_5.10.2_windows_amd64.zip' -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath "$env:TEMP\koyeb" -Force
    }
    return $koyeb
}

function Deploy-Koyeb {
    param($EnvVars)
    $koyeb = Ensure-Koyeb

    Write-Host ''
    Write-Host '=== Koyeb deploy (no GitHub needed) ===' -ForegroundColor Cyan
    Write-Host 'If browser opens — sign in to Koyeb (Google/GitHub/email).'

    & $koyeb service list 2>$null
    if ($LASTEXITCODE -ne 0) {
        & $koyeb login
        if ($LASTEXITCODE -ne 0) { throw 'Koyeb login failed' }
    }

    $token = $EnvVars['TELEGRAM_BOT_TOKEN']
    $chat = $EnvVars['TELEGRAM_CHAT_ID']
    if (-not $token -or -not $chat) {
        throw 'Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env first'
    }

    $args = @(
        'deploy', '.', 'onetech/onetech',
        '--archive-buildpack-build-command', 'pip install -r requirements.txt',
        '--archive-buildpack-run-command', 'gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120',
        '--port', '8000',
        '--checks', '8000:http:/api/health',
        '--env', "TELEGRAM_BOT_TOKEN=$token",
        '--env', "TELEGRAM_CHAT_ID=$chat",
        '--env', 'PRICE_UPDATE_ENABLED=1',
        '--env', 'PRICE_UPDATE_HOURS=6',
        '--env', 'PRICE_UPDATE_ON_START=1',
        '--wait'
    )

    & $koyeb @args
    if ($LASTEXITCODE -ne 0) { throw 'Koyeb deploy failed' }

    $url = (& $koyeb service get onetech/onetech -o json | ConvertFrom-Json).service.domains[0].name
    if ($url) {
        Write-Host ''
        Write-Host "LIVE: https://$url" -ForegroundColor Green
        Set-Content -Path 'DEPLOY_URL.txt' -Value "https://$url" -Encoding utf8
    }
}

function Deploy-Render {
    param($EnvVars)
    $gh = Ensure-Gh

    Write-Host ''
    Write-Host '=== Render deploy via GitHub ===' -ForegroundColor Cyan
    & $gh auth status 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'GitHub login — approve in browser when it opens.'
        & $gh auth login -h github.com -p https -w
    }

    $remote = git remote get-url origin 2>$null
    if (-not $remote) {
        & $gh repo create onetech-landing --public --source=. --remote=origin --push --description 'OneTech heat pumps landing'
    } else {
        git push -u origin main
    }

    Write-Host ''
    Write-Host 'Code pushed to GitHub.' -ForegroundColor Green
    Write-Host 'Open Render Blueprint and connect the repo:'
    Write-Host '  https://dashboard.render.com/blueprint/new' -ForegroundColor Yellow
    Write-Host ''
    Write-Host 'Set on Render Environment:'
    Write-Host "  TELEGRAM_BOT_TOKEN=$($EnvVars['TELEGRAM_BOT_TOKEN'])"
    Write-Host "  TELEGRAM_CHAT_ID=$($EnvVars['TELEGRAM_CHAT_ID'])"
    Start-Process 'https://dashboard.render.com/blueprint/new'
}

$envVars = Read-DotEnv (Join-Path $Root '.env')

if (-not $envVars['TELEGRAM_CHAT_ID']) {
    Write-Host 'Fetching Telegram chat_id...'
    python get_chat_id.py
    $envVars = Read-DotEnv (Join-Path $Root '.env')
}

if ($Target -eq 'auto') {
    $Target = 'koyeb'
}

switch ($Target) {
    'koyeb' { Deploy-Koyeb $envVars }
    'render' { Deploy-Render $envVars }
}

Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
