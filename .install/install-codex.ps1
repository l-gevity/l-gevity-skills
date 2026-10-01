# l-gevity-skills installer (Codex CLI / AGENTS.md)
# Usage: iwr -useb https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-codex.ps1 | iex
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
$Agent            = 'codex'
$MemFile          = 'AGENTS.md'
$PrimarySkillsDir = '.agents/skills'
# --- end agent profile ---

$Repo           = 'l-gevity/l-gevity-skills'
$Ref            = if ($env:L_GEVITY_SKILLS_REF) { $env:L_GEVITY_SKILLS_REF } else { 'main' }
$RepoZip        = "https://github.com/$Repo/archive/$Ref.zip"
$Target         = (Get-Location).Path
$LockName       = 'l-gevity-skills.lock.json'
$KnownSkillDirs = @('.claude/skills', '.agents/skills')
$GuidanceBegin  = '<!-- BEGIN L-GEVITY MANAGED GUIDANCE -->'
$GuidanceEnd    = '<!-- END L-GEVITY MANAGED GUIDANCE -->'

function Update-ManagedGuidance([string] $Destination, [string] $Source, [string] $Staged) {
    $current = ''
    $encoding = [System.Text.UTF8Encoding]::new($false, $true)
    if (Test-Path -LiteralPath $Destination) {
        $reader = [System.IO.StreamReader]::new($Destination, $encoding, $true)
        try {
            $current = $reader.ReadToEnd()
            $encoding = $reader.CurrentEncoding
        } finally { $reader.Dispose() }
    }
    $begins = [regex]::Matches($current, [regex]::Escape($GuidanceBegin)).Count
    $ends = [regex]::Matches($current, [regex]::Escape($GuidanceEnd)).Count
    $beginLines = [regex]::Matches($current, '(?m)^' + [regex]::Escape($GuidanceBegin) + '\r?$')
    $endLines = [regex]::Matches($current, '(?m)^' + [regex]::Escape($GuidanceEnd) + '\r?$')
    if ($begins -ne $ends -or $begins -gt 1 -or
        $beginLines.Count -ne $begins -or $endLines.Count -ne $ends -or
        ($begins -eq 1 -and $beginLines[0].Index -ge $endLines[0].Index)) {
        throw "Refused to update malformed L-GEVITY guidance markers in $Destination"
    }
    $newline = if ($current.Contains("`r`n")) { "`r`n" } else { "`n" }
    $guidance = [System.IO.File]::ReadAllText($Source).TrimEnd("`r", "`n")
    $guidance = $guidance.Replace('.claude/skills', $PrimarySkillsDir)
    $guidance = [regex]::Replace($guidance, '\r\n|\r|\n', $newline)
    $block = $GuidanceBegin + $newline + $guidance + $newline + $GuidanceEnd
    if ($begins -eq 1) {
        $start = $current.IndexOf($GuidanceBegin, [System.StringComparison]::Ordinal)
        $end = $current.IndexOf($GuidanceEnd, $start, [System.StringComparison]::Ordinal) + $GuidanceEnd.Length
        $current = $current.Substring(0, $start) + $block + $current.Substring($end)
    } elseif ($current) {
        $separator = if ($current.EndsWith("`n")) { $newline } else { $newline + $newline }
        $current += $separator + $block + $newline
    } else {
        $current = $block + $newline
    }
    [System.IO.File]::WriteAllText($Staged, $current, $encoding)
}

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

    # The profile owns its root file. Stage guidance before changing skills or locks.
    $MemDest = Join-Path $Target $MemFile
    $StagedGuidance = Join-Path $Tmp 'guidance.md'
    Update-ManagedGuidance $MemDest (Join-Path $Src 'CLAUDE.md') $StagedGuidance

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

    Move-Item -LiteralPath $StagedGuidance -Destination $MemDest -Force
    $MemReport = "$MemFile (managed L-GEVITY block updated; project guidance kept)"

    Write-Host "Installed $($SrcSkillNames.Count) skills ($($SrcFiles.Count) files) into: $($Dests -join ' ')"
    if ($RemovedTotal -gt 0) {
        Write-Host "Removed $RemovedTotal file(s) dropped upstream."
    }
    Write-Host "Instruction file: $MemReport"
    $CommitNote = if ($Commit) { " (commit $($Commit.Substring(0, 7)))" } else { '' }
    Write-Host "Source: $Ref$CommitNote; per-file hashes recorded in $LockName."
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
