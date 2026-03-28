# scripts/setup_env.ps1 - Environment Setup for Windows
# Syncs secrets from Google Drive and prepares the development environment.

$ErrorActionPreference = "Stop"

# --- Configuration ---
$SecretFolderName = "PersonalWebsite-Secrets"
$SecretsFiles = @(".env", "credentials.json", "token.json")

# --- 1. Detect Google Drive ---
Write-Host "--- Detecting Google Drive ---" -ForegroundColor Cyan
$PossibleGDrivePaths = @(
    "G:\My Drive",
    "$HOME\Google Drive",
    "$HOME\My Drive"
)

$GDriveBase = $null
foreach ($Path in $PossibleGDrivePaths) {
    if (Test-Path $Path) {
        $GDriveBase = $Path
        break
    }
}

if ($null -eq $GDriveBase) {
    $GDriveBase = Read-Host "Google Drive not automatically detected. Please enter the path to 'My Drive' (e.g. G:\My Drive)"
}

$GDriveProjects = Join-Path $GDriveBase "Projects"
$GDriveSecretsPath = Join-Path $GDriveProjects $SecretFolderName
Write-Host "Using Google Drive Secrets Path: $GDriveSecretsPath" -ForegroundColor Green

# --- 2. Ensure Secrets Folder exists ---
if (!(Test-Path $GDriveSecretsPath)) {
    Write-Host "Creating secrets folder in Google Drive..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $GDriveSecretsPath -Force | Out-Null
}

# --- 3. Manage Secret Files (Robust Sync via Copy) ---
# Note: Symlinks on Windows require Developer Mode or Admin. 
# We use a timestamp-based copy to ensure cross-drive compatibility without elevation.
foreach ($File in $SecretsFiles) {
    $LocalPath = Join-Path $PSScriptRoot "..\$File"
    $RemotePath = Join-Path $GDriveSecretsPath $File
    
    # If local file doesn't exist but remote does, copy remote -> local
    if (!(Test-Path $LocalPath) -and (Test-Path $RemotePath)) {
        Write-Host "Restoring $File from Google Drive..." -ForegroundColor Cyan
        Copy-Item -Path $RemotePath -Destination $LocalPath -Force
    }
    # If local exists but remote doesn't, copy local -> remote
    elseif ((Test-Path $LocalPath) -and !(Test-Path $RemotePath)) {
        Write-Host "Uploading local $File to Google Drive..." -ForegroundColor Yellow
        Copy-Item -Path $LocalPath -Destination $RemotePath -Force
    }
    # If both exist, compare timestamps
    elseif ((Test-Path $LocalPath) -and (Test-Path $RemotePath)) {
        $LocalTime = (Get-Item $LocalPath).LastWriteTime
        $RemoteTime = (Get-Item $RemotePath).LastWriteTime
        
        if ($LocalTime -gt $RemoteTime.AddSeconds(2)) {
            Write-Host "Local $File is newer. Updating Google Drive..." -ForegroundColor Yellow
            Copy-Item -Path $LocalPath -Destination $RemotePath -Force
        }
        elseif ($RemoteTime -gt $LocalTime.AddSeconds(2)) {
            Write-Host "Google Drive $File is newer. Updating local..." -ForegroundColor Cyan
            Copy-Item -Path $RemotePath -Destination $LocalPath -Force
        }
    }
    # If neither exist
    else {
        if ($File -eq ".env") {
            Write-Host "Warning: .env not found. Initializing from env.example..." -ForegroundColor Yellow
            $ExamplePath = Join-Path $PSScriptRoot "..\env.example"
            Copy-Item -Path $ExamplePath -Destination $LocalPath
            Copy-Item -Path $LocalPath -Destination $RemotePath
            Write-Host "!!! Please update your .env file with real keys !!!" -ForegroundColor Red
        }
    }
}

# --- 4. Python Environment Setup ---
Write-Host "`n--- Checking Python Environment ---" -ForegroundColor Cyan
$VenvPath = Join-Path $PSScriptRoot "..\venv"

if (!(Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv (Join-Path $PSScriptRoot "..\venv")
} else {
    Write-Host "V Virtual environment exists." -ForegroundColor Gray
}

# Install/Update requirements
Write-Host "Installing/Updating requirements..." -ForegroundColor Yellow
$PipPath = Join-Path $PSScriptRoot "..\venv\Scripts\pip.exe"
$RequirementsPath = Join-Path $PSScriptRoot "..\requirements.txt"
if (Test-Path $PipPath) {
    & $PipPath install --upgrade pip | Out-Null
    & $PipPath install -r $RequirementsPath | Out-Null
} else {
    Write-Host "Error: pip not found in venv. Check Python installation." -ForegroundColor Red
}

Write-Host "`nSetup Complete! Your environment is ready." -ForegroundColor Green
Write-Host "Run this script anytime you switch computers to sync your secrets." -ForegroundColor Cyan
