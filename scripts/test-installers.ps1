#!/usr/bin/env pwsh
# Functional tests for .install/install-*.ps1 — the PowerShell mirror of
# scripts/test-installers.sh, asserting the same behaviour.
#
# Hermetic: builds a zip from the working tree and points the installers at it
# through L_GEVITY_SKILLS_ARCHIVE, so the code under test is the checkout's and
# the run needs no network.
#
# Runs the whole suite once per available PowerShell host. Windows PowerShell
# 5.1 is the one consumers most often pipe `iwr | iex` into, and it rejects
# constructs pwsh 7 accepts, so both are exercised where both exist.

param(
    [string[]] $PsHosts = @()
)

$ErrorActionPreference = 'Stop'
$LASTEXITCODE = 0

$RepoRoot = Split-Path -Parent $PSScriptRoot
$script:Fails = 0
$script:Checks = 0

function Check($Name, $Got, $Want) {
    $script:Checks++
    if ("$Got" -eq "$Want") {
        Write-Host "  PASS $Name"
    } else {
        Write-Host "  FAIL $Name : expected [$Want] got [$Got]"
        $script:Fails++
    }
}

function Primary-DirFor($Agent) {
    if ($Agent -eq 'claude') { return '.claude/skills' } else { return '.agents/skills' }
}

function MemFile-For($Agent) {
    switch ($Agent) {
        'claude' { 'CLAUDE.md' }
        'codex'  { 'AGENTS.md' }
        'gemini' { 'GEMINI.md' }
        'grok'   { 'GROK.md' }
    }
}

function New-SourceArchive($WorkDir) {
    $stage = Join-Path $WorkDir 'l-gevity-skills-test'
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    Copy-Item -Path (Join-Path $RepoRoot '.claude') -Destination $stage -Recurse -Force
    Copy-Item -Path (Join-Path $RepoRoot '.agents') -Destination $stage -Recurse -Force
    Copy-Item -Path (Join-Path $RepoRoot 'CLAUDE.md') -Destination $stage -Force
    $zip = Join-Path $WorkDir 'skills.zip'
    Compress-Archive -Path $stage -DestinationPath $zip -Force
    return $zip
}

function Invoke-Installer($Exe, $Agent, $ConsumerDir, $Archive) {
    $installer = Join-Path $RepoRoot ".install/install-$Agent.ps1"
    $argv = @('-NoProfile')
    if ($IsWindows -or $null -eq $IsWindows) { $argv += @('-ExecutionPolicy', 'Bypass') }
    $argv += @('-File', $installer)

    $previous = $env:L_GEVITY_SKILLS_ARCHIVE
    $env:L_GEVITY_SKILLS_ARCHIVE = $Archive
    Push-Location $ConsumerDir
    try {
        $output = (& $Exe @argv 2>&1 | Out-String)
        return [pscustomobject]@{ Output = $output; ExitCode = $LASTEXITCODE }
    } finally {
        Pop-Location
        $env:L_GEVITY_SKILLS_ARCHIVE = $previous
    }
}

function Get-LockHashCount($Path) {
    $text = Get-Content -Raw -LiteralPath $Path
    return ([regex]::Matches($text, '"[^"]+"\s*:\s*"[0-9a-f]{64}"')).Count
}

function Add-LockEntry($Path, $Rel) {
    $lock = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    $lock.files | Add-Member -NotePropertyName $Rel -NotePropertyValue ('0' * 64) -Force
    $lock | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Path -Encoding utf8
}

# Relative path + content hash for every file except the lock, so two trees or
# two runs can be compared without caring about order or absolute location.
function Get-TreeHashes($Dir) {
    $root = (Resolve-Path -LiteralPath $Dir).Path
    Get-ChildItem -LiteralPath $root -Recurse -File -Force |
        Where-Object { $_.Name -ne 'l-gevity-skills.lock.json' } |
        ForEach-Object {
            $rel = $_.FullName.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
            "$rel  $((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash)"
        } | Sort-Object
}

function Match-One($Text, $Pattern) {
    $m = [regex]::Match($Text, $Pattern)
    if ($m.Success) { return $m.Groups[1].Value }
    return ''
}

function Invoke-Suite($Exe, $ExeLabel) {
    Write-Host ""
    Write-Host "######## host: $ExeLabel ########"

    $work = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $work -Force | Out-Null
    try {
        $archive = New-SourceArchive $work

        $srcSkills = Join-Path $RepoRoot '.claude/skills'
        $expectSkills = (Get-ChildItem -LiteralPath $srcSkills -Directory -Force).Count
        $expectFiles = (Get-ChildItem -LiteralPath $srcSkills -Recurse -File -Force |
            Where-Object { $_.Extension -notin @('.pyc', '.pyo') }).Count
        Write-Host "Source tree: $expectSkills skills, $expectFiles files"

        # --- Every installer lands in its own agent's tree ---
        foreach ($agent in @('claude', 'codex', 'gemini', 'grok')) {
            Write-Host ""
            Write-Host "== $agent : installs into its own tree =="
            $primary = Primary-DirFor $agent
            $memfile = MemFile-For $agent
            $other = if ($primary -eq '.claude/skills') { '.agents/skills' } else { '.claude/skills' }

            $consumer = Join-Path $work "consumer-$agent"
            New-Item -ItemType Directory -Path $consumer -Force | Out-Null
            $run = Invoke-Installer $Exe $agent $consumer $archive

            Check "exit status" $run.ExitCode 0
            Check "skills in $primary" `
                (Test-Path (Join-Path $consumer "$primary/alchemy/SKILL.md")) $true
            Check "nothing written to $other" `
                (Test-Path (Join-Path $consumer $other)) $false
            Check "created $memfile" (Test-Path (Join-Path $consumer $memfile)) $true
            Check "reported skill count" `
                (Match-One $run.Output 'Installed (\d+) skills') $expectSkills
            Check "reported file count" `
                (Match-One $run.Output '\((\d+) files\)') $expectFiles

            $lockPath = Join-Path $consumer "$primary/l-gevity-skills.lock.json"
            $lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
            Check "lock version 2" $lock.version 2
            Check "lock names the agent" $lock.agent $agent
            Check "one hash per installed file" (Get-LockHashCount $lockPath) $expectFiles
        }

        # --- Recorded hashes describe the installed bytes ---
        Write-Host ""
        Write-Host "== recorded hashes describe the installed bytes =="
        $claudeSkills = Join-Path $work 'consumer-claude/.claude/skills'
        $lockPath = Join-Path $claudeSkills 'l-gevity-skills.lock.json'
        $lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
        $mismatch = 0
        foreach ($property in $lock.files.PSObject.Properties) {
            $actual = (Get-FileHash -LiteralPath (Join-Path $claudeSkills $property.Name) `
                -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actual -ne $property.Value) { $mismatch++ }
        }
        Check "hash mismatches across every file" $mismatch 0

        # --- An existing instruction file of any name is honored ---
        Write-Host ""
        Write-Host "== an existing AGENTS.md is honored by the Claude installer =="
        $consumer = Join-Path $work 'consumer-agents-md'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $consumer 'AGENTS.md') -Value 'project instructions'
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        Check "existing file untouched" `
            (Get-Content -Raw -LiteralPath (Join-Path $consumer 'AGENTS.md')).Trim() 'project instructions'
        Check "upstream copy sidecarred" `
            (Test-Path (Join-Path $consumer 'AGENTS.md.l-gevity')) $true
        Check "no second instruction file invented" `
            (Test-Path (Join-Path $consumer 'CLAUDE.md')) $false

        # --- A consumer keeping both trees gets both, identically ---
        Write-Host ""
        Write-Host "== a dual-tree consumer keeps its mirror =="
        $both = Join-Path $work 'consumer-both'
        New-Item -ItemType Directory -Path (Join-Path $both '.claude/skills') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $both '.agents/skills') -Force | Out-Null
        Invoke-Installer $Exe 'claude' $both $archive | Out-Null
        Check "primary tree filled" `
            (Test-Path (Join-Path $both '.claude/skills/alchemy/SKILL.md')) $true
        Check "mirror tree filled" `
            (Test-Path (Join-Path $both '.agents/skills/alchemy/SKILL.md')) $true
        $left = (Get-TreeHashes (Join-Path $both '.claude/skills')) -join "`n"
        $right = (Get-TreeHashes (Join-Path $both '.agents/skills')) -join "`n"
        Check "trees byte-identical" ($left -eq $right) $true

        # --- Re-running changes nothing ---
        Write-Host ""
        Write-Host "== the installer is idempotent =="
        $before = (Get-TreeHashes (Join-Path $both '.claude/skills')) -join "`n"
        $again = Invoke-Installer $Exe 'claude' $both $archive
        $after = (Get-TreeHashes (Join-Path $both '.claude/skills')) -join "`n"
        Check "second run leaves the tree unchanged" ($before -eq $after) $true
        Check "second run removes nothing" ($again.Output -match 'Removed') $false

        # --- A file upstream no longer ships is removed and reported ---
        Write-Host ""
        Write-Host "== a dropped file is pruned on the next run =="
        $stale = Join-Path $both '.claude/skills/alchemy/RETIRED.md'
        Set-Content -LiteralPath $stale -Value 'gone upstream'
        Add-LockEntry (Join-Path $both '.claude/skills/l-gevity-skills.lock.json') 'alchemy/RETIRED.md'
        $prune = Invoke-Installer $Exe 'claude' $both $archive
        Check "stale file removed" (Test-Path $stale) $false
        Check "removal reported" `
            ($prune.Output -match 'Removed \(dropped upstream\): \.claude/skills/alchemy/RETIRED\.md') $true
        Check "sibling files survive" `
            (Test-Path (Join-Path $both '.claude/skills/alchemy/SKILL.md')) $true

        # --- A lock naming a path outside the tree must not delete anything ---
        Write-Host ""
        Write-Host "== path traversal in the lock is refused =="
        $canary = Join-Path $both 'CANARY.md'
        Set-Content -LiteralPath $canary -Value 'do not delete me'
        Add-LockEntry (Join-Path $both '.claude/skills/l-gevity-skills.lock.json') '../../CANARY.md'
        $traversal = Invoke-Installer $Exe 'claude' $both $archive
        Check "file outside the tree survives" (Test-Path $canary) $true
        Check "refusal reported" `
            ($traversal.Output -match 'Refused to remove unsafe path from lock: \.\./\.\./CANARY\.md') $true
        Check "install still succeeds" ($traversal.Output -match 'Installed \d+ skills') $true
    } finally {
        Remove-Item -Recurse -Force -LiteralPath $work -ErrorAction SilentlyContinue
    }
}

if ($PsHosts.Count -eq 0) {
    foreach ($candidate in @('pwsh', 'powershell')) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { $PsHosts += $command.Source }
    }
}
if ($PsHosts.Count -eq 0) {
    Write-Host "No PowerShell host found."
    exit 1
}

foreach ($exe in $PsHosts) {
    Invoke-Suite $exe $exe
}

Write-Host ""
Write-Host "$script:Checks checks run across $($PsHosts.Count) host(s)"
if ($script:Fails -eq 0) {
    Write-Host "PowerShell installers verified"
    exit 0
}
Write-Host "$script:Fails check(s) failed"
exit 1
