<#
.SYNOPSIS
    One-shot installer for the paper-writing skill (OpenAI Codex + DeepSeek Harness).

.DESCRIPTION
    Installs this repository as a standard Agent Skill (SKILL.md at the root) into:
      - Codex:  %CODEX_HOME%\skills\paper-writing      (default: %USERPROFILE%\.codex\skills)
      - DSH:    %USERPROFILE%\.agents\skills\paper-writing

    One-line install (no clone required):

        irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex

    Install for a single host only:

        $env:SKILL_INSTALL_TARGET = 'codex'
        irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex

    Uninstall (both hosts, or one):

        $env:SKILL_UNINSTALL = '1'
        $env:SKILL_INSTALL_TARGET = 'dsh'
        irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex

    Running from a local clone:

        .\install.ps1 [-Target all|codex|dsh] [-Uninstall]

    Re-running the installer updates an existing install:
    git-based installs get "git pull --ff-only"; plain folders are backed up
    to <dir>.bak-<timestamp> and replaced.
#>
[CmdletBinding()]
param(
    [string]$Target = '',
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'

# ---- skill constants ------------------------------------------------------
$SkillName  = 'paper-writing'
$Owner      = 'xiaoxiaomuyu321'
$Repo       = 'paper-writing'
$Branch     = 'main'
$CloneUrl   = "https://github.com/$Owner/$Repo.git"
$TarballUrl = "https://codeload.github.com/$Owner/$Repo/tar.gz/refs/heads/$Branch"

# ---- argument/env handling -------------------------------------------------
$Target = if ($Target) { $Target } elseif ($env:SKILL_INSTALL_TARGET) { $env:SKILL_INSTALL_TARGET } else { 'all' }
if ($Target -notin @('all', 'codex', 'dsh')) { throw "invalid target '$Target' (use all|codex|dsh)" }
$Uninstall = $Uninstall -or ($env:SKILL_UNINSTALL -eq '1')

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$Targets = @()
if ($Target -in @('all', 'codex')) { $Targets += [pscustomobject]@{ Host = 'Codex'; Dir = (Join-Path (Join-Path $CodexHome 'skills') $SkillName) } }
if ($Target -in @('all', 'dsh'))   { $Targets += [pscustomobject]@{ Host = 'DSH';   Dir = (Join-Path (Join-Path $HOME '.agents\skills') $SkillName) } }
if ($Targets.Count -eq 0) { throw 'nothing to do' }

# ---- source resolution ------------------------------------------------------
# Prefer a local clone of this repo (offline installs); otherwise GitHub.
$LocalClone = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'SKILL.md')) -and (Test-Path (Join-Path $PSScriptRoot '.git'))) {
    $LocalClone = $PSScriptRoot
}

function Test-GitAvailable {
    try { (Get-Command git -ErrorAction Stop) -ne $null } catch { $false }
}

function Install-Fresh {
    param([string]$HostLabel, [string]$Dest)
    New-Item -ItemType Directory -Path (Split-Path $Dest -Parent) -Force | Out-Null
    $Done = $false
    if (Test-GitAvailable) {
        Write-Host "[$HostLabel] git clone -> $Dest"
        & git clone -q --depth 1 -b $Branch $(if ($LocalClone) { $LocalClone } else { $CloneUrl }) $Dest 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($LocalClone) { & git -C $Dest remote set-url origin $CloneUrl 2>$null }
            $Done = $true
        } else {
            Write-Warning "[$HostLabel] git clone failed; falling back to tarball."
        }
    }
    if (-not $Done) {
        Write-Host "[$HostLabel] downloading tarball -> $Dest"
        $Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ($SkillName + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
        New-Item -ItemType Directory -Path $Tmp | Out-Null
        try {
            Invoke-WebRequest -Uri $TarballUrl -OutFile (Join-Path $Tmp 'skill.tar.gz') -UseBasicParsing
            & tar -xzf (Join-Path $Tmp 'skill.tar.gz') -C $Tmp 2>$null
            $Inner = Get-ChildItem $Tmp -Directory | Select-Object -First 1
            if (-not (Test-Path (Join-Path $Inner.FullName 'SKILL.md'))) { throw 'SKILL.md missing in archive' }
            Move-Item $Inner.FullName $Dest
        } finally {
            Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if (Test-Path (Join-Path $Dest 'SKILL.md')) {
        Write-Host "[$HostLabel] installed: $Dest"
    } else {
        throw "[$HostLabel] install failed: SKILL.md not found in $Dest"
    }
}

function Install-One {
    param([string]$HostLabel, [string]$Dest)
    if (Test-Path $Dest) {
        if (Test-Path (Join-Path $Dest '.git')) {
            Write-Host "[$HostLabel] updating existing git install at $Dest"
            & git -C $Dest fetch -q origin $Branch 2>$null
            if ($LASTEXITCODE -eq 0) {
                & git -C $Dest pull -q --ff-only 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "[$HostLabel] updated."
                } else {
                    Write-Warning "[$HostLabel] fast-forward failed (local changes?); keeping $Dest as is."
                }
            } else {
                Write-Warning "[$HostLabel] git fetch failed (offline?); keeping $Dest as is."
            }
        } else {
            $Bak = "$Dest.bak-" + (Get-Date -Format 'yyyyMMdd-HHmmss')
            Move-Item $Dest $Bak
            Write-Host "[$HostLabel] previous plain install backed up to $Bak"
            Install-Fresh $HostLabel $Dest
        }
    } else {
        Install-Fresh $HostLabel $Dest
    }
}

# ---- main -------------------------------------------------------------------
foreach ($t in $Targets) {
    if ($Uninstall) {
        if (Test-Path $t.Dir) {
            Remove-Item $t.Dir -Recurse -Force
            Write-Host "[$($t.Host)] uninstalled: $($t.Dir)"
        } else {
            Write-Host "[$($t.Host)] not installed: $($t.Dir)"
        }
    } else {
        Install-One $t.Host $t.Dir
    }
}
Write-Host 'Done.'
