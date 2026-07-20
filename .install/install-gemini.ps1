# l-gevity-skills installer (Gemini CLI / GEMINI.md)
# Usage: iwr -useb https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-gemini.ps1 | iex
# Pin a version: $env:L_GEVITY_SKILLS_REF = '<branch|tag|commit>' before running
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo    = 'l-gevity/l-gevity-skills'
$Ref     = if ($env:L_GEVITY_SKILLS_REF) { $env:L_GEVITY_SKILLS_REF } else { 'main' }
$RepoZip = "https://github.com/$Repo/archive/$Ref.zip"
$MemFile = 'GEMINI.md'
$Target  = (Get-Location).Path

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Tmp | Out-Null

try {
    Write-Host "Downloading l-gevity-skills@$Ref..."
    $Zip = Join-Path $Tmp 'skills.zip'
    Invoke-WebRequest -Uri $RepoZip -OutFile $Zip -UseBasicParsing
    Expand-Archive -Path $Zip -DestinationPath $Tmp -Force

    $Src = (Get-ChildItem -Path $Tmp -Directory -Filter 'l-gevity-skills-*' | Select-Object -First 1).FullName

    $Commit = $null
    try {
        $Commit = (Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/$Ref").sha
    } catch {
        Write-Host "Warning: could not resolve $Ref to a commit; lock will record the ref only."
    }

    $SkillsDest = Join-Path $Target '.claude\skills'
    New-Item -ItemType Directory -Path $SkillsDest -Force | Out-Null
    Copy-Item -Path (Join-Path $Src '.claude\skills\*') -Destination $SkillsDest -Recurse -Force

    $SkillCount = (Get-ChildItem $SkillsDest -Directory).Count

    $UpstreamSkills = @(Get-ChildItem (Join-Path $Src '.claude\skills') -Directory | ForEach-Object Name)
    [System.Array]::Sort($UpstreamSkills, [System.StringComparer]::Ordinal)
    $Lock = [ordered]@{
        version  = 1
        source   = [ordered]@{
            repository = "https://github.com/$Repo.git"
            ref        = $Ref
            commit     = $Commit
            path       = '.claude/skills'
        }
        syncedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        skills   = $UpstreamSkills
    }
    $Lock | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $SkillsDest 'l-gevity-skills.lock.json') -Encoding utf8

    $MemDest = Join-Path $Target $MemFile
    if (Test-Path $MemDest) {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination "$MemDest.l-gevity" -Force
        Write-Host "Existing $MemFile kept. Upstream version written to $MemFile.l-gevity - review and merge manually."
    } else {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination $MemDest -Force
    }

    $CommitNote = if ($Commit) { ", commit $($Commit.Substring(0, 7))" } else { '' }
    Write-Host "Installed $SkillCount skills + $MemFile (ref $Ref$CommitNote)."
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
