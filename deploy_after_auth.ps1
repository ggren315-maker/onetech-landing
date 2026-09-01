# Waits for GitHub auth, then pushes repo and opens Render
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root
$gh = "$env:ProgramFiles\GitHub CLI\gh.exe"

Write-Host 'Waiting for GitHub authorization...' -ForegroundColor Yellow
$authed = $false
for ($i = 0; $i -lt 60; $i++) {
    $null = & $gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) { $authed = $true; break }
    Start-Sleep -Seconds 5
}

if (-not $authed) {
    Write-Host 'GitHub auth timeout. Run deploy.ps1 again after login.' -ForegroundColor Red
    exit 1
}

Write-Host 'GitHub OK. Creating repo and pushing...' -ForegroundColor Green
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    & $gh repo create onetech-landing --public --source=. --remote=origin --push --description 'OneTech heat pumps landing'
} else {
    git push -u origin main
}

$repoUrl = (& $gh repo view --json url -q .url)
Write-Host "GitHub: $repoUrl" -ForegroundColor Green

$envContent = Get-Content .env -Raw
$token = if ($envContent -match 'TELEGRAM_BOT_TOKEN=(.+)') { $Matches[1].Trim() } else { '' }
$chat = if ($envContent -match 'TELEGRAM_CHAT_ID=(.+)') { $Matches[1].Trim() } else { '' }

Write-Host ''
Write-Host 'Open Render Blueprint (connect repo onetech-landing):' -ForegroundColor Cyan
Start-Process 'https://dashboard.render.com/blueprint/new'
Write-Host "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID=$chat on Render"

Set-Content DEPLOY_URL.txt "GitHub: $repoUrl`nRender: https://dashboard.render.com/blueprint/new" -Encoding utf8
