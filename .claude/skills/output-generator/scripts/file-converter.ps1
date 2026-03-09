param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

if (-not (Test-Path $InputPath)) {
    throw "Input file not found: $InputPath"
}

$ext = [System.IO.Path]::GetExtension($OutputPath).ToLowerInvariant()

switch ($ext) {
    ".md" { Copy-Item $InputPath $OutputPath -Force }
    ".txt" { Copy-Item $InputPath $OutputPath -Force }
    ".html" { Copy-Item $InputPath $OutputPath -Force }
    ".pdf" { throw "converter stub: add PDF generator runtime" }
    ".docx" { throw "converter stub: add DOCX generator runtime" }
    ".pptx" { throw "converter stub: add PPTX generator runtime" }
    default { throw "Unsupported extension: $ext" }
}

Write-Output "written: $OutputPath"
