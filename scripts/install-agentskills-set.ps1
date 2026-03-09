param(
    [string]$Repo = "CaseMark/skills",
    [string]$Dest = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Dest)) {
    $Dest = Join-Path $projectRoot ".claude/skills"
}

$installer = "C:/Users/kplee/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py"
if (-not (Test-Path $installer)) {
    throw "Installer not found: $installer"
}

$paths = @(
    "skills/legal/legal-research",
    "skills/legal/legal-research-summary",
    "skills/legal/regulatory-summary",
    "skills/legal/compliance-summaries",
    "skills/legal/gambling-law-summary",
    "skills/legal/privacy-law-updates",
    "skills/legal/antitrust-investigation-summary",
    "skills/legal/ip-infringement-analysis",
    "skills/legal/terms-of-service",
    "skills/legal/api-acceptable-use-policy",
    "skills/legal/client-memo",
    "skills/legal/judgment-summary",
    "skills/legal/case-briefs",
    "skills/legal/cyber-law-compliance-summary"
)

$missingPaths = @()
foreach ($path in $paths) {
    $skillName = Split-Path -Leaf $path
    $target = Join-Path $Dest $skillName
    if (-not (Test-Path $target)) {
        $missingPaths += $path
    }
}

if ($missingPaths.Count -eq 0) {
    Write-Output "All selected AgentSkills are already installed."
    exit 0
}

$args = @(
    $installer,
    "--repo", $Repo,
    "--path"
) + $missingPaths + @(
    "--dest", $Dest
)

python @args
