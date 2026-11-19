# l-gevity-skills installer (Grok CLI / GROK.md)
# Usage: iwr -useb https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-grok.ps1 | iex
# Pin a version: $env:L_GEVITY_SKILLS_REF = '<branch|tag|commit>' before running
#
# Lock format v2 records a sha256 for every file it writes, and a later run
# removes files that upstream has since dropped. That pruning reads the file
# map from the lock already on disk, so upgrading FROM a v1 lock (which has no
# map) prunes nothing on that first run - removals begin from the second.
#
# Test seam: $env:L_GEVITY_SKILLS_ARCHIVE = '<path or url>' installs from that
# archive instead of GitHub, and skips commit resolution.
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# --- agent profile ---
$Agent            = 'grok'
$MemFile          = 'GROK.md'
$PrimarySkillsDir = '.agents/skills'
$AdapterRuntime   = ''
# --- end agent profile ---

$Repo           = 'l-gevity/l-gevity-skills'
$Ref            = if ($env:L_GEVITY_SKILLS_REF) { $env:L_GEVITY_SKILLS_REF } else { 'main' }
$RepoZip        = "https://github.com/$Repo/archive/$Ref.zip"
$Target         = (Get-Location).Path
$LockName       = 'l-gevity-skills.lock.json'
$KnownSkillDirs = @('.claude/skills', '.agents/skills')
$KnownMemFiles  = @('CLAUDE.md', 'AGENTS.md', 'GEMINI.md', 'GROK.md')

# Files this installer recorded in a previous run, from that run's lock.
function Get-PreviousFiles($DestAbs) {
    $lock = Join-Path $DestAbs $LockName
    if (-not (Test-Path $lock)) { return @() }
    $text = Get-Content -Raw -Path $lock
    $matched = [regex]::Matches($text, '"([^"]+)"\s*:\s*"[0-9a-f]{64}"')
    return @($matched | ForEach-Object { $_.Groups[1].Value })
}

# The lock lives in the consumer's repo and drives a delete. Treat its keys as
# untrusted: a hand-edited or corrupted lock must not reach outside the tree.
function Test-SafeRelPath($Rel) {
    if ([string]::IsNullOrWhiteSpace($Rel)) { return $false }
    if ($Rel -match '^[\\/]' -or $Rel -match '^[A-Za-z]:' -or $Rel.Contains('\')) { return $false }
    if (('/' + $Rel + '/') -match '/\.\./') { return $false }
    return $true
}

# Python 3 under any of its usual names, or $null. A stock Windows has a
# `python` stub that only prints an install hint. Its stderr, redirected under
# 'Stop', would end the install in Windows PowerShell 5.1, hence the local
# preference.
function Find-Python3 {
    $ErrorActionPreference = 'Continue'
    foreach ($candidate in @('python3', 'python', 'py')) {
        if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
        try {
            $null = & $candidate -c 'import sys; sys.exit(sys.version_info[0] != 3)' 2>&1
            if ($LASTEXITCODE -eq 0) { return $candidate }
        } catch { }
    }
    return $null
}

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Tmp | Out-Null

try {
    $Zip = Join-Path $Tmp 'skills.zip'
    $Archive = $env:L_GEVITY_SKILLS_ARCHIVE
    if ($Archive -and (Test-Path -LiteralPath $Archive)) {
        Write-Host "Installing l-gevity-skills from $Archive..."
        Copy-Item -LiteralPath $Archive -Destination $Zip -Force
    } else {
        Write-Host "Downloading l-gevity-skills@$Ref..."
        $Uri = if ($Archive) { $Archive } else { $RepoZip }
        Invoke-WebRequest -Uri $Uri -OutFile $Zip -UseBasicParsing
    }
    Expand-Archive -Path $Zip -DestinationPath $Tmp -Force

    $Src = (Get-ChildItem -Path $Tmp -Directory -Filter 'l-gevity-skills-*' | Select-Object -First 1).FullName
    $SrcSkills = Join-Path $Src '.claude/skills'

    $Commit = $null
    if (-not $Archive) {
        try {
            $Commit = (Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/$Ref").sha
        } catch {
            Write-Host "Warning: could not resolve $Ref to a commit; lock will record the ref only."
        }
    }

    # Report what upstream ships, never what the target happens to contain.
    $SrcFiles = @(Get-ChildItem -Path $SrcSkills -Recurse -File |
        Where-Object { $_.Extension -notin @('.pyc', '.pyo') } |
        ForEach-Object { $_.FullName.Substring($SrcSkills.Length + 1).Replace('\', '/') })
    [System.Array]::Sort($SrcFiles, [System.StringComparer]::Ordinal)

    $SrcSkillNames = @(Get-ChildItem -Path $SrcSkills -Directory | ForEach-Object Name)
    [System.Array]::Sort($SrcSkillNames, [System.StringComparer]::Ordinal)

    $Hashes = [ordered]@{}
    foreach ($rel in $SrcFiles) {
        $Hashes[$rel] = (Get-FileHash -Path (Join-Path $SrcSkills $rel) -Algorithm SHA256).Hash.ToLowerInvariant()
    }

    # Install into the profile's tree, plus any sibling tree the consumer already keeps.
    $Dests = @($PrimarySkillsDir)
    foreach ($d in $KnownSkillDirs) {
        if ($d -ne $PrimarySkillsDir -and (Test-Path (Join-Path $Target $d))) {
            $Dests += $d
        }
    }

    $SyncedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $RemovedTotal = 0

    foreach ($d in $Dests) {
        $DestAbs = Join-Path $Target $d
        $Old = Get-PreviousFiles $DestAbs
        New-Item -ItemType Directory -Path $DestAbs -Force | Out-Null
        Copy-Item -Path (Join-Path $SrcSkills '*') -Destination $DestAbs -Recurse -Force

        # Anything this installer wrote before and upstream has since dropped.
        foreach ($rel in $Old) {
            if ($SrcFiles -notcontains $rel) {
                if (-not (Test-SafeRelPath $rel)) {
                    Write-Warning "Refused to remove unsafe path from lock: $rel"
                    continue
                }
                $Stale = Join-Path $DestAbs $rel
                if (Test-Path $Stale) {
                    Remove-Item -Path $Stale -Force -Confirm:$false
                    Write-Host "Removed (dropped upstream): $d/$rel"
                    $RemovedTotal++
                    $Parent = Split-Path -Parent $Stale
                    while ($Parent -and $Parent -ne $DestAbs -and $Parent.StartsWith($DestAbs) -and
                           -not (Get-ChildItem -Path $Parent -Force)) {
                        Remove-Item -Path $Parent -Force -Confirm:$false
                        $Parent = Split-Path -Parent $Parent
                    }
                }
            }
        }

        $Lock = [ordered]@{
            version     = 2
            source      = [ordered]@{
                repository = "https://github.com/$Repo.git"
                ref        = $Ref
                commit     = $Commit
                path       = '.claude/skills'
            }
            agent       = $Agent
            installedTo = $Dests
            syncedAt    = $SyncedAt
            skills      = $SrcSkillNames
            files       = $Hashes
        }
        $Lock | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $DestAbs $LockName) -Encoding utf8
    }

    # Honor whichever instruction file the project already uses, whatever its name.
    $ExistingMem = $KnownMemFiles | Where-Object { Test-Path (Join-Path $Target $_) } | Select-Object -First 1
    if ($ExistingMem) {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination (Join-Path $Target "$ExistingMem.l-gevity") -Force
        $MemReport = "$ExistingMem.l-gevity (existing $ExistingMem kept; review and merge manually)"
    } else {
        Copy-Item -Path (Join-Path $Src 'CLAUDE.md') -Destination (Join-Path $Target $MemFile) -Force
        $MemReport = $MemFile
    }

    # Agent-team adapters. The skill's own installer renders them and never
    # overwrites a file the project already has. Single-agent runs need none of
    # them, so a missing interpreter or a refused profile is reported, not fatal.
    #
    # Unstoppable Code runs a Claude Code or Codex harness and adds a pipeline
    # of its own, so its adapter is installed beside the harness's. It is
    # recognised by the project's .unstoppable-code directory, or by the
    # variables the app sets in the sessions it starts.
    $AdapterRuntimes = @()
    if ($AdapterRuntime) { $AdapterRuntimes += $AdapterRuntime }
    if ((Test-Path (Join-Path $Target '.unstoppable-code')) -or
        (Get-ChildItem env: | Where-Object { $_.Name -match '^(UNSTOPPABLE_CODE|CANOPY)_' })) {
        $AdapterRuntimes += 'unstoppable'
    }

    $AdapterReport = "none shipped for $Agent; runs stay single-agent"
    if ($AdapterRuntimes.Count -gt 0) {
        $Init = "$PrimarySkillsDir/alchemy-orchestrate/scripts/init_workspace.py"
        $Python = Find-Python3
        $Installed = @()
        $Manual = @()
        foreach ($runtime in $AdapterRuntimes) {
            if ($Python) {
                Write-Host "Installing agent-team adapters ($runtime)..."
                & $Python (Join-Path $Target $Init) --runtime $runtime --root $Target |
                    ForEach-Object { Write-Host "  $_" }
                if ($LASTEXITCODE -eq 0) {
                    $Installed += $runtime
                    continue
                }
            }
            $Manual += "python $Init --runtime $runtime"
        }
        if (-not $Python) {
            $AdapterReport = "not installed (Python 3 not found); run: $($Manual -join '; ')"
        } elseif ($Manual.Count -gt 0) {
            $Prefix = if ($Installed.Count -gt 0) { "$($Installed -join ' '); " } else { '' }
            $AdapterReport = "${Prefix}not installed (init_workspace.py failed, see above); fix and run: $($Manual -join '; ')"
        } else {
            $AdapterReport = $Installed -join ' '
        }
    }

    Write-Host "Installed $($SrcSkillNames.Count) skills ($($SrcFiles.Count) files) into: $($Dests -join ' ')"
    if ($RemovedTotal -gt 0) {
        Write-Host "Removed $RemovedTotal file(s) dropped upstream."
    }
    Write-Host "Instruction file: $MemReport"
    Write-Host "Agent-team adapters: $AdapterReport"
    $CommitNote = if ($Commit) { " (commit $($Commit.Substring(0, 7)))" } else { '' }
    Write-Host "Source: $Ref$CommitNote; per-file hashes recorded in $LockName."
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
