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

# The installers add the Unstoppable adapter when the session shows the app.
# Clear its variables, so every run here starts outside it wherever the suite
# itself is run.
Get-ChildItem env: | Where-Object { $_.Name -match '^(UNSTOPPABLE_CODE|CANOPY)_' } |
    ForEach-Object { Remove-Item -LiteralPath "env:$($_.Name)" }

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

function Adapter-RuntimeFor($Agent) {
    switch ($Agent) {
        'claude' { 'claude-code' }
        'codex'  { 'codex' }
        default  { '' }
    }
}

function Adapter-FileFor($Agent) {
    switch ($Agent) {
        'claude' { '.claude/agents/alchemy-analyst.md' }
        'codex'  { '.codex/agents/alchemy-analyst.toml' }
    }
}

# The adapter step needs Python 3, found by the probe the installers use. A
# host without it still runs every check: the installers must then say so.
function Test-Python3 {
    $ErrorActionPreference = 'Continue'
    foreach ($candidate in @('python3', 'python', 'py')) {
        if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
        try {
            $null = & $candidate -c 'import sys; sys.exit(sys.version_info[0] != 3)' 2>&1
            if ($LASTEXITCODE -eq 0) { return $true }
        } catch { }
    }
    return $false
}

# A directory that answers every Python name with a failure, to put first on
# PATH: the installer then sees a host without Python 3.
function New-NoPythonDir($WorkDir) {
    $dir = Join-Path $WorkDir 'no-python'
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    foreach ($name in @('python3', 'python', 'py')) {
        if ($IsWindows -or $null -eq $IsWindows) {
            Set-Content -LiteralPath (Join-Path $dir "$name.cmd") -Value '@exit /b 1' -Encoding ascii
        } else {
            $file = Join-Path $dir $name
            [System.IO.File]::WriteAllText($file, "#!/bin/sh`nexit 1`n")
            & chmod +x $file
        }
    }
    return $dir
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

function Invoke-Installer($Exe, $Agent, $ConsumerDir, $Archive, $PathPrefix) {
    $installer = Join-Path $RepoRoot ".install/install-$Agent.ps1"
    $argv = @('-NoProfile')
    if ($IsWindows -or $null -eq $IsWindows) { $argv += @('-ExecutionPolicy', 'Bypass') }
    $argv += @('-File', $installer)

    $previous = $env:L_GEVITY_SKILLS_ARCHIVE
    $previousPath = $env:PATH
    $env:L_GEVITY_SKILLS_ARCHIVE = $Archive
    if ($PathPrefix) { $env:PATH = $PathPrefix + [System.IO.Path]::PathSeparator + $env:PATH }
    Push-Location $ConsumerDir
    try {
        $output = (& $Exe @argv 2>&1 | Out-String)
        return [pscustomobject]@{ Output = $output; ExitCode = $LASTEXITCODE }
    } finally {
        Pop-Location
        $env:L_GEVITY_SKILLS_ARCHIVE = $previous
        $env:PATH = $previousPath
    }
}

function Invoke-Uninstaller($Exe, $ConsumerDir, $PathPrefix) {
    $uninstaller = Join-Path $RepoRoot '.install/uninstall.ps1'
    $argv = @('-NoProfile')
    if ($IsWindows -or $null -eq $IsWindows) { $argv += @('-ExecutionPolicy', 'Bypass') }
    $argv += @('-File', $uninstaller)

    $previousPath = $env:PATH
    if ($PathPrefix) { $env:PATH = $PathPrefix + [System.IO.Path]::PathSeparator + $env:PATH }
    Push-Location $ConsumerDir
    try {
        $output = (& $Exe @argv 2>&1 | Out-String)
        return [pscustomobject]@{ Output = $output; ExitCode = $LASTEXITCODE }
    } finally {
        Pop-Location
        $env:PATH = $previousPath
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
        $havePython = Test-Python3
        Write-Host "Python 3: $(if ($havePython) { 'found' } else { 'not found' })"

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

            $runtime = Adapter-RuntimeFor $agent
            if (-not $runtime) {
                Check "says no adapter ships for $agent" `
                    ($run.Output -match "(?m)^Agent-team adapters: none shipped for $agent") $true
                Check "no workspace profile written" `
                    (Test-Path (Join-Path $consumer 'alchemy-workspace.json')) $false
            } elseif ($havePython) {
                Check "reports the $runtime adapters" `
                    ($run.Output -match "(?m)^Agent-team adapters: $runtime\r?$") $true
                Check "agent definition rendered" `
                    (Test-Path (Join-Path $consumer (Adapter-FileFor $agent))) $true
                Check "workspace profile written" `
                    (Test-Path (Join-Path $consumer 'alchemy-workspace.json')) $true
                Check "no Unstoppable files outside Unstoppable" `
                    (Test-Path (Join-Path $consumer '.unstoppable-code')) $false
            } else {
                Check "reports the adapters as not installed" `
                    ($run.Output -match '(?m)^Agent-team adapters: not installed \(Python 3 not found\)') $true
            }
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

        # --- An instruction file that differs only in line endings is current ---
        Write-Host ""
        Write-Host "== a CRLF copy of the current CLAUDE.md gets no sidecar =="
        $consumer = Join-Path $work 'consumer-crlf-claude-md'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        $lf = [IO.File]::ReadAllText((Join-Path $RepoRoot 'CLAUDE.md')) -replace "`r", ''
        [IO.File]::WriteAllText((Join-Path $consumer 'CLAUDE.md'), ($lf -replace "`n", "`r`n"))
        Set-Content -LiteralPath (Join-Path $consumer 'CLAUDE.md.l-gevity') -Value 'stale sidecar'
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        Check "no sidecar for a line-ending-only difference" `
            (Test-Path (Join-Path $consumer 'CLAUDE.md.l-gevity')) $false

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
        Check "second run renders no adapter file again" ($again.Output -match ': (created|kept)') $false

        # --- The adapter step never overwrites what the project already has ---
        Write-Host ""
        Write-Host "== an existing settings file is kept, the rendered one written beside it =="
        $consumer = Join-Path $work 'consumer-settings'
        New-Item -ItemType Directory -Path (Join-Path $consumer '.claude') -Force | Out-Null
        $settings = Join-Path $consumer '.claude/settings.json'
        Set-Content -LiteralPath $settings -Value '{"mine": true}'
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        Check "existing settings untouched" (Get-Content -Raw -LiteralPath $settings).Trim() '{"mine": true}'
        if ($havePython) {
            Check "rendered settings sidecarred" (Test-Path "$settings.l-gevity") $true
        }

        # --- Unstoppable Code gets its pipeline beside the harness's adapter ---
        if ($havePython) {
            $pipeline = '.unstoppable-code/pipelines/alchemy-multi-agent.yaml'

            Write-Host ""
            Write-Host "== a project with an .unstoppable-code directory gets the pipeline =="
            $consumer = Join-Path $work 'consumer-unstoppable-dir'
            New-Item -ItemType Directory -Path (Join-Path $consumer '.unstoppable-code') -Force | Out-Null
            $byDir = Invoke-Installer $Exe 'codex' $consumer $archive
            Check "reports both adapters" `
                ($byDir.Output -match '(?m)^Agent-team adapters: codex unstoppable\r?$') $true
            Check "pipeline installed" (Test-Path (Join-Path $consumer $pipeline)) $true
            Check "harness agent rendered" `
                (Test-Path (Join-Path $consumer '.codex/agents/alchemy-analyst.toml')) $true

            Write-Host ""
            Write-Host "== a session started by Unstoppable Code gets the pipeline =="
            $consumer = Join-Path $work 'consumer-unstoppable-env'
            New-Item -ItemType Directory -Path $consumer -Force | Out-Null
            $env:UNSTOPPABLE_CODE_SESSION = '1'
            try {
                $byEnv = Invoke-Installer $Exe 'claude' $consumer $archive
            } finally {
                Remove-Item -LiteralPath 'env:UNSTOPPABLE_CODE_SESSION'
            }
            Check "reports both adapters" `
                ($byEnv.Output -match '(?m)^Agent-team adapters: claude-code unstoppable\r?$') $true
            Check "pipeline installed" (Test-Path (Join-Path $consumer $pipeline)) $true
        }

        $manual = [regex]::Escape('python .claude/skills/alchemy-orchestrate/scripts/init_workspace.py --runtime claude-code')

        # --- A profile the adapter installer refuses is reported; the skills stay ---
        if ($havePython) {
            Write-Host ""
            Write-Host "== a refused workspace profile does not fail the install =="
            $consumer = Join-Path $work 'consumer-bad-profile'
            New-Item -ItemType Directory -Path $consumer -Force | Out-Null
            Set-Content -LiteralPath (Join-Path $consumer 'alchemy-workspace.json') `
                -Value '{"schema": "alchemy-workspace/1", "execution": {"max_parallel_agents": 0}}'
            $refused = Invoke-Installer $Exe 'claude' $consumer $archive
            Check "exit status" $refused.ExitCode 0
            Check "failure reported with the command to rerun" `
                ($refused.Output -match "(?m)^Agent-team adapters: not installed \(init_workspace\.py failed, see above\); fix and run: $manual\r?$") $true
            Check "no agent definition rendered" (Test-Path (Join-Path $consumer '.claude/agents')) $false
            Check "skills installed" `
                (Test-Path (Join-Path $consumer '.claude/skills/alchemy/SKILL.md')) $true
        }

        # --- Without Python 3 the skills install and the gap is named ---
        Write-Host ""
        Write-Host "== a host without Python 3 still installs the skills =="
        $consumer = Join-Path $work 'consumer-no-python'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        $bare = Invoke-Installer $Exe 'claude' $consumer $archive (New-NoPythonDir $work)
        Check "exit status" $bare.ExitCode 0
        Check "gap reported with the command to run" `
            ($bare.Output -match "(?m)^Agent-team adapters: not installed \(Python 3 not found\); run: $manual\r?$") $true
        Check "no agent definition rendered" (Test-Path (Join-Path $consumer '.claude/agents')) $false
        Check "skills installed" `
            (Test-Path (Join-Path $consumer '.claude/skills/alchemy/SKILL.md')) $true

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

        # --- The uninstaller removes an unedited install and nothing else ---
        Write-Host ""
        Write-Host "== an unedited install is removed completely =="
        $consumer = Join-Path $work 'uninstall-clean'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        $gone = Invoke-Uninstaller $Exe $consumer
        Check "exit status" $gone.ExitCode 0
        Check "nothing left in the project" @(Get-ChildItem -LiteralPath $consumer -Force).Count 0
        Check "instruction file reported removed" `
            ($gone.Output -match '(?m)^Instruction file: removed CLAUDE\.md\r?$') $true
        Check "every installed file reported removed" (Match-One $gone.Output 'Removed (\d+) file') $expectFiles
        $again = Invoke-Uninstaller $Exe $consumer
        Check "second run exits 0" $again.ExitCode 0
        Check "second run finds nothing" ($again.Output -match '(?m)^Nothing to uninstall') $true

        Write-Host ""
        Write-Host "== edited files and the project's own instruction file are kept =="
        $consumer = Join-Path $work 'uninstall-edited'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $consumer 'AGENTS.md') -Value 'project instructions'
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        $lock = Get-Content -Raw -LiteralPath (Join-Path $consumer '.claude/skills/l-gevity-skills.lock.json') |
            ConvertFrom-Json
        Check "lock names the sidecar it wrote" $lock.instructionFile.path 'AGENTS.md.l-gevity'
        Add-Content -LiteralPath (Join-Path $consumer '.claude/skills/alchemy/SKILL.md') -Value 'local note'
        $edited = Invoke-Uninstaller $Exe $consumer
        Check "exit status" $edited.ExitCode 0
        Check "project instruction file untouched" `
            (Get-Content -Raw -LiteralPath (Join-Path $consumer 'AGENTS.md')).Trim() 'project instructions'
        Check "installed sidecar removed" (Test-Path (Join-Path $consumer 'AGENTS.md.l-gevity')) $false
        Check "edited skill file kept" (Test-Path (Join-Path $consumer '.claude/skills/alchemy/SKILL.md')) $true
        Check "edited skill file reported" `
            ($edited.Output -match 'Kept \(edited since install\): \.claude/skills/alchemy/SKILL\.md') $true
        Check "lock removed" (Test-Path (Join-Path $consumer '.claude/skills/l-gevity-skills.lock.json')) $false

        Write-Host ""
        Write-Host "== an edited instruction file is kept =="
        $consumer = Join-Path $work 'uninstall-edited-memfile'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Invoke-Installer $Exe 'codex' $consumer $archive | Out-Null
        Add-Content -LiteralPath (Join-Path $consumer 'AGENTS.md') -Value 'my rule'
        $memKept = Invoke-Uninstaller $Exe $consumer
        Check "instruction file kept" (Test-Path (Join-Path $consumer 'AGENTS.md')) $true
        Check "kept file reported" `
            ($memKept.Output -match '(?m)^Instruction file: kept AGENTS\.md \(edited since install\)\r?$') $true

        Write-Host ""
        Write-Host "== a CRLF copy of an unedited instruction file is removed =="
        $consumer = Join-Path $work 'uninstall-crlf'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
        $memPath = Join-Path $consumer 'CLAUDE.md'
        $crlf = [IO.File]::ReadAllText($memPath) -replace "`r", '' -replace "`n", "`r`n"
        [IO.File]::WriteAllText($memPath, $crlf)
        Invoke-Uninstaller $Exe $consumer | Out-Null
        Check "instruction file removed" (Test-Path $memPath) $false

        Write-Host ""
        Write-Host "== a lock path outside the tree is refused, even with a matching hash =="
        $consumer = Join-Path $work 'uninstall-traversal'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Invoke-Installer $Exe 'gemini' $consumer $archive | Out-Null
        $canary = Join-Path $consumer 'CANARY.md'
        Set-Content -LiteralPath $canary -Value 'do not delete me'
        $lockPath = Join-Path $consumer '.agents/skills/l-gevity-skills.lock.json'
        $lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
        $lock.files | Add-Member -NotePropertyName '../../CANARY.md' -Force `
            -NotePropertyValue (Get-FileHash -LiteralPath $canary -Algorithm SHA256).Hash.ToLowerInvariant()
        $lock | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $lockPath -Encoding utf8
        $refused = Invoke-Uninstaller $Exe $consumer
        Check "file outside the tree survives" (Test-Path $canary) $true
        Check "refusal reported" `
            ($refused.Output -match 'Refused to remove unsafe path from lock: \.\./\.\./CANARY\.md') $true

        Write-Host ""
        Write-Host "== a lock written before v5.7.0 leaves the instruction file to the user =="
        $consumer = Join-Path $work 'uninstall-old-lock'
        New-Item -ItemType Directory -Path $consumer -Force | Out-Null
        Invoke-Installer $Exe 'grok' $consumer $archive | Out-Null
        $lockPath = Join-Path $consumer '.agents/skills/l-gevity-skills.lock.json'
        $lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
        $lock.PSObject.Properties.Remove('instructionFile')
        $lock | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $lockPath -Encoding utf8
        $old = Invoke-Uninstaller $Exe $consumer
        Check "exit status" $old.ExitCode 0
        Check "instruction file kept" (Test-Path (Join-Path $consumer 'GROK.md')) $true
        Check "gap reported" ($old.Output -match '(?m)^Instruction file: not recorded') $true
        Check "skills removed" (Test-Path (Join-Path $consumer '.agents')) $false

        if ($havePython) {
            Write-Host ""
            Write-Host "== without Python 3, installed adapters stop the uninstall before any removal =="
            $consumer = Join-Path $work 'uninstall-no-python'
            New-Item -ItemType Directory -Path $consumer -Force | Out-Null
            Invoke-Installer $Exe 'claude' $consumer $archive | Out-Null
            $stopped = Invoke-Uninstaller $Exe $consumer (New-NoPythonDir $work)
            Check "exit status" $stopped.ExitCode 1
            if ($stopped.ExitCode -ne 1) { Write-Host $stopped.Output }
            Check "cause named" ($stopped.Output -match 'Python 3 not found') $true
            Check "skills untouched" (Test-Path (Join-Path $consumer '.claude/skills/alchemy/SKILL.md')) $true
            Check "adapters untouched" (Test-Path (Join-Path $consumer '.claude/agents/alchemy-analyst.md')) $true

            Write-Host ""
            Write-Host "== an edited adapter file is kept =="
            Add-Content -LiteralPath (Join-Path $consumer '.claude/agents/alchemy-analyst.md') -Value '# mine'
            $adapter = Invoke-Uninstaller $Exe $consumer
            Check "exit status" $adapter.ExitCode 0
            Check "edited adapter kept" (Test-Path (Join-Path $consumer '.claude/agents/alchemy-analyst.md')) $true
            Check "unedited adapter removed" `
                (Test-Path (Join-Path $consumer '.claude/agents/alchemy-implementer.md')) $false
            Check "adapter summary counts the kept file" `
                ($adapter.Output -match '(?m)^Agent-team adapters: removed; 1 kept \(listed above\)\r?$') $true
            Check "workspace profile removed" (Test-Path (Join-Path $consumer 'alchemy-workspace.json')) $false
        }

        # --- With no ref set, an installer installs the release it ships with ---
        Write-Host ""
        Write-Host "== the default source is this checkout's release tag =="
        $release = 'v' + (Get-Content -Raw -LiteralPath (Join-Path $RepoRoot 'package.json') | ConvertFrom-Json).version
        $lock = Get-Content -Raw -LiteralPath (Join-Path $work 'consumer-claude/.claude/skills/l-gevity-skills.lock.json') |
            ConvertFrom-Json
        Check "lock records the release tag as ref" $lock.source.ref $release
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
