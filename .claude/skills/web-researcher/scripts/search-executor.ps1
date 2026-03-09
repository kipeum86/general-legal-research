param(
    [Parameter(Mandatory = $true)]
    [string]$Query
)

# MCP wrapper (tavily -> brave -> fetch).
# Configure commands via env vars:
# - TAVILY_MCP_SERVER_CMD
# - BRAVE_MCP_SERVER_CMD
# - FETCH_MCP_SERVER_CMD

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "search-executor.py"

if (Get-Command python -ErrorAction SilentlyContinue) {
    python $pythonScript $Query
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 $pythonScript $Query
    exit $LASTEXITCODE
}

throw "Python runtime not found. Install Python 3 or update PATH."
