# l-gevity-skills uninstaller (every agent)
# Usage: iwr -useb https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/uninstall.ps1 | iex
#
# Run from the project root. Removes what the installers wrote, from the
# records they left, and needs no network:
#   1. the agent-team adapters, through the installed init_workspace.py --uninstall;
#   2. the instruction file the lock names, while its digest still matches;
#   3. every file in each skills tree's lock whose sha256 still matches, then the lock.
# An edited file is kept and reported. A step that cannot run stops the
# uninstall before the skills trees, which hold the adapter remover, are touched.
$ErrorActionPreference = 'Stop'

$Target         = (Get-Location).Path
$LockName       = 'l-gevity-skills.lock.json'
$KnownSkillDirs = @('.claude/skills', '.agents/skills')
$KnownMemFiles  = @('CLAUDE.md', 'AGENTS.md', 'GEMINI.md', 'GROK.md')
$ProfileName    = 'alchemy-workspace.json'
$InitRel        = 'alchemy-orchestrate/scripts/init_workspace.py'

# Digest of a text file with line endings ignored, as the installers record it.
function Get-TextDigest($Path) {
    $text = ([string](Get-Content -Raw -Encoding UTF8 -LiteralPath $Path) -replace "`r", '').TrimEnd("`n")
    $bytes = (New-Object System.Text.UTF8Encoding $false).GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $hash = $sha.ComputeHash($bytes) } finally { $sha.Dispose() }
    return 'sha256:' + (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}

# The lock lives in the consumer's repo and drives a delete. Treat its keys as
# untrusted: a hand-edited or corrupted lock must not reach outside the tree.
function Test-SafeRelPath($Rel) {
    if ([string]::IsNullOrWhiteSpace($Rel)) { return $false }
    if ($Rel -match '^[\\/]' -or $Rel -match '^[A-Za-z]:' -or $Rel.Contains('\') -or $Rel.Contains(':')) { return $false }
    if (('/' + $Rel + '/') -match '/\.\./') { return $false }
    return $true
}

# Python 3 under any of its usual names, or $null. A stock Windows has a
# `python` stub that only prints an install hint. Its stderr, redirected under
# 'Stop', would end the run in Windows PowerShell 5.1, hence the local
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

# A function, so that returning early or failing never closes the session
# that piped this script into iex.
function Invoke-Uninstall {
    $Locked = @($KnownSkillDirs | Where-Object { Test-Path -LiteralPath (Join-Path (Join-Path $Target $_) $LockName) })
    if ($Locked.Count -eq 0) {
        Write-Host "Nothing to uninstall: no $LockName in $($KnownSkillDirs -join ' ') under $Target."
        return
    }
    $Locks = @{}
    foreach ($d in $Locked) {
        $Locks[$d] = Get-Content -Raw -LiteralPath (Join-Path (Join-Path $Target $d) $LockName) | ConvertFrom-Json
    }

    # --- 1. Agent-team adapters ---
    $Init = $Locked | ForEach-Object { "$_/$InitRel" } |
        Where-Object { Test-Path -LiteralPath (Join-Path $Target $_) } | Select-Object -First 1
    $Python = Find-Python3
    $AdapterReport = "none recorded (no $ProfileName)"
    if ($Init -and $Python) {
        Write-Host "Removing agent-team adapters..."
        # Under 'Stop', Windows PowerShell 5.1 turns a redirected stderr line into a
        # terminating error, so the child's own report would be lost.
        $lines = @(& {
            $ErrorActionPreference = 'Continue'
            & $Python (Join-Path $Target $Init) --uninstall --runtime all --root $Target 2>&1 |
                ForEach-Object { "$_" }
        })
        $code = $LASTEXITCODE
        $lines | ForEach-Object { Write-Host "  $_" }
        if ($code -ne 0) {
            throw ("$Init --uninstall failed (see above); nothing else was removed. An install older " +
                   "than v5.7.0 has no --uninstall: run the installer once to update, then uninstall again.")
        }
        $keptAdapters = @($lines | Where-Object { $_ -match ': kept' }).Count
        $AdapterReport = if ($keptAdapters -gt 0) { "removed; $keptAdapters kept (listed above)" } else { 'removed' }
    } elseif (Test-Path -LiteralPath (Join-Path $Target $ProfileName)) {
        # The adapters were installed, and only init_workspace.py knows which files
        # they are. Removing the skills now would delete the one tool that can tell.
        if (-not $Python) {
            throw "Python 3 not found; it is needed to remove the agent-team adapters. Nothing was removed."
        }
        throw "$InitRel not found in $($Locked -join ' '); cannot remove the agent-team adapters. Nothing was removed."
    }

    # --- 2. The instruction file each lock names ---
    $MemReport = 'not recorded (installed before v5.7.0); delete it by hand if you did not edit it'
    $Seen = @()
    foreach ($d in $Locked) {
        $record = $Locks[$d].instructionFile
        if (-not $record) { continue }
        $path = [string]$record.path
        $allowed = $KnownMemFiles | Where-Object { $path -ceq $_ -or $path -ceq "$_.l-gevity" }
        if (-not $allowed) {
            Write-Host "Refused to remove instruction file named by $d/${LockName}: $path"
            continue
        }
        if ($Seen -contains $path) { continue }
        $Seen += $path
        $file = Join-Path $Target $path
        if (-not (Test-Path -LiteralPath $file)) {
            $MemReport = "$path (already gone)"
        } elseif ((Get-TextDigest $file) -ceq [string]$record.digest) {
            Remove-Item -LiteralPath $file -Force -Confirm:$false
            $MemReport = "removed $path"
        } else {
            $MemReport = "kept $path (edited since install)"
        }
    }

    # --- 3. Skills trees ---
    $RemovedTotal = 0
    $KeptTotal = 0
    $KeptTrees = @()
    foreach ($d in $Locked) {
        $DestAbs = Join-Path $Target $d
        $entries = @()
        if ($Locks[$d].files) { $entries = @($Locks[$d].files.PSObject.Properties) }
        if ($entries.Count -eq 0) {
            Write-Host "Kept ${d}: its lock records no file hashes (a v1 lock). Run the installer once to update it, then uninstall again."
            $KeptTrees += $d
            continue
        }
        foreach ($entry in $entries) {
            $rel = $entry.Name
            if (-not (Test-SafeRelPath $rel)) {
                Write-Host "Refused to remove unsafe path from lock: $rel"
                continue
            }
            $file = Join-Path $DestAbs $rel
            if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { continue }
            $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actual -ceq [string]$entry.Value) {
                Remove-Item -LiteralPath $file -Force -Confirm:$false
                $RemovedTotal++
            } else {
                Write-Host "Kept (edited since install): $d/$rel"
                $KeptTotal++
            }
        }
        Remove-Item -LiteralPath (Join-Path $DestAbs $LockName) -Force -Confirm:$false
        # Bytecode caches are regenerated on demand and keep a directory from
        # emptying. Then remove what is left empty, deepest first.
        Get-ChildItem -LiteralPath $DestAbs -Recurse -Directory -Force -Filter '__pycache__' |
            Remove-Item -Recurse -Force -Confirm:$false
        $dirs = @(Get-ChildItem -LiteralPath $DestAbs -Recurse -Directory -Force |
            Sort-Object { $_.FullName.Length } -Descending)
        foreach ($dir in $dirs + @(Get-Item -LiteralPath $DestAbs) + @(Get-Item -LiteralPath (Split-Path -Parent $DestAbs))) {
            if ((Test-Path -LiteralPath $dir.FullName) -and -not (Get-ChildItem -LiteralPath $dir.FullName -Force)) {
                Remove-Item -LiteralPath $dir.FullName -Force -Confirm:$false
            }
        }
    }

    Write-Host "Removed $RemovedTotal file(s) from: $($Locked -join ' ')"
    if ($KeptTotal -gt 0) { Write-Host "Kept $KeptTotal edited file(s), listed above." }
    if ($KeptTrees.Count -gt 0) { Write-Host "Not uninstalled: $($KeptTrees -join ' ')" }
    Write-Host "Instruction file: $MemReport"
    Write-Host "Agent-team adapters: $AdapterReport"
}

# A thrown error does not set a reliable exit status for a -File run: the
# hosted Windows runners report 0. Run as a file, exit 1 explicitly; piped
# into iex, rethrow, since exit would close the session that ran it.
try {
    Invoke-Uninstall
} catch {
    if (-not $PSCommandPath) { throw }
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}
