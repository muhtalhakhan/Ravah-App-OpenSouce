param(
    [string]$Repo = "anthropics/skills",
    [Parameter(Mandatory = $true)]
    [string]$Skill,
    [string]$PathPrefix = "skills",
    [switch]$Experimental,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$installer = "C:\Users\Muhammad Talha Khan\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py"

if (-not (Test-Path $installer)) {
    throw "Installer script not found at: $installer"
}

$basePath = if ($Experimental) { "$PathPrefix/.experimental" } else { $PathPrefix }
$skillPath = "$basePath/$Skill"

$args = @(
    $installer,
    "--repo", $Repo,
    "--path", $skillPath
)

Write-Host "Installing skill '$Skill' from '$Repo' (path: $skillPath)..."
Write-Host "Command: python $($args -join ' ')"

if ($DryRun) {
    Write-Host "Dry run complete. No changes were made."
    exit 0
}

python @args
