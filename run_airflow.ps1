# Simple PowerShell helper to start your Airflow Docker Compose stack.
#
# Usage:
#   .\run_airflow.ps1           # start detached, open UI when ready
#   .\run_airflow.ps1 -Foreground  # run in foreground (attach to logs)

param(
    [switch]$Foreground
)

function ExitWithError($msg, $code=1) {
    Write-Error $msg
    exit $code
}

Write-Host "[run_airflow] Script directory: $PSScriptRoot"

# Check Docker cli
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    ExitWithError "Docker CLI not found. Install Docker Desktop and ensure 'docker' is in PATH."
}

# Check Docker daemon
try {
    docker info > $null 2>&1
} catch {
    ExitWithError "Docker daemon doesn't appear to be running. Start Docker Desktop and try again."
}

# Move to script directory (project root)
Set-Location $PSScriptRoot

# Make sure compose file exists
if (-not (Test-Path "docker-compose.yaml")) {
    ExitWithError "docker-compose.yaml not found in $PSScriptRoot. Ensure the file exists in the project root."
}

if ($Foreground) {
    Write-Host "[run_airflow] Starting Docker Compose in foreground (attached). Press Ctrl+C to stop."
    & docker compose up
    if ($LASTEXITCODE -ne 0) {
        ExitWithError "'docker compose up' failed with exit code $LASTEXITCODE" $LASTEXITCODE
    }
    exit 0
}

# Detached mode
Write-Host "[run_airflow] Starting Docker Compose in detached mode..."
& docker compose up -d
if ($LASTEXITCODE -ne 0) {
    ExitWithError "'docker compose up -d' failed with exit code $LASTEXITCODE" $LASTEXITCODE
}

# Wait for Airflow webserver to be available
$port = 8080
$timeoutSeconds = 180
$start = Get-Date
$ready = $false
Write-Host "[run_airflow] Waiting up to $timeoutSeconds seconds for http://localhost:$port ..."
while (((Get-Date) - $start).TotalSeconds -lt $timeoutSeconds) {
    try {
        if (Test-NetConnection -ComputerName "localhost" -Port $port -InformationLevel Quiet) {
            $ready = $true
            break
        }
    } catch {
        # ignore transient errors
    }
    Start-Sleep -Seconds 2
}

if ($ready) {
    Write-Host "[run_airflow] Airflow webserver is reachable at http://localhost:$port - opening browser..."
    Start-Process "http://localhost:$port"
    Write-Host "[run_airflow] To trigger the DAG from this machine:"
    Write-Host "    docker compose exec airflow airflow dags trigger etl_sales"
} else {
    Write-Warning "[run_airflow] Timed out waiting for http://localhost:$port. Check container status and logs:"
    Write-Host "    docker compose ps"
    Write-Host "    docker compose logs --tail 200"
    Write-Host "Or run in foreground for real-time logs: .\run_airflow.ps1 -Foreground"
}

Write-Host "[run_airflow] Done."
