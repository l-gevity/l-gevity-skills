# l-gevity-skills installer (Codex CLI / AGENTS.md)
# Usage: iwr -useb https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-codex.ps1 | iex
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$RepoZip = 'https://github.com/l-gevity/l-gevity-skills/archive/refs/heads/main.zip'
$MemFile = 'AGENTS.md'
$Target  = (Get-Location).Path

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Tmp | Out-Null

try {
    Write-Host 'Downloading l-gevity-skills...'
    $Zip = Join-Path $Tmp 'skills.zip'
    Invoke-WebRequest -Uri $RepoZip -OutFile $Zip -UseBasicParsing
    Expand-Archive -Path $Zip -DestinationPath $Tmp -Force

    $Src = Join-Path $Tmp 'l-gevity-skills-main'

    $SkillsDest = Join-Path $Target '.claude\skills'
    New-Item -ItemType Directory -Path $SkillsDest -Force | Out-Null
    Copy-Item -Path (Join-Path $Src '.claude\skills\*') -Destination $SkillsDest -Recurse -Force

    $SkillCount = (Get-ChildItem $SkillsDest -Directory).Count

    $MemDest = Join-Path $Target $MemFile
    if (Test-Path $MemDest) {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination "$MemDest.l-gevity" -Force
        Write-Host "Existing $MemFile kept. Upstream version written to $MemFile.l-gevity - review and merge manually."
    } else {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination $MemDest -Force
    }

    Write-Host "Installed $SkillCount skills + $MemFile."
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
