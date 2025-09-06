# PowerShell Remote Server Auto Deploy Script
# Encoding: UTF-8

# Set console encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Color output function
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Display title
Write-ColorOutput ("=" * 60) "Cyan"
Write-ColorOutput "Remote Server Auto Deploy Script" "Cyan"
Write-ColorOutput "Target Server: 115.190.103.114" "Yellow"
Write-ColorOutput "Deploy Directory: /usr/share/nginx-after" "Yellow"
Write-ColorOutput "Application Port: 8081" "Yellow"
Write-ColorOutput ("=" * 60) "Cyan"
Write-ColorOutput ""

# Check Python environment
Write-ColorOutput "Checking Python environment..." "Blue"
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Python not found. Please install Python first." "Red"
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-ColorOutput "Python not found. Please install Python first." "Red"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput "Python environment check passed: $pythonVersion" "Green"

# Check dependencies
Write-ColorOutput "Checking dependencies..." "Blue"
$importTest = python -c "import paramiko, scp; print('Dependencies OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "Dependencies not installed, installing..." "Yellow"
    
    # Install dependencies
    Write-ColorOutput "Installing paramiko and scp..." "Blue"
    pip install -r deploy_requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Dependency installation failed" "Red"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Verify installation
    $importTest = python -c "import paramiko, scp; print('Dependencies OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Dependency verification failed" "Red"
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-ColorOutput "Dependencies check passed" "Green"
}

Write-ColorOutput ""

# Confirm deployment
Write-ColorOutput "Ready to deploy to remote server" "Green"
Write-ColorOutput "Server: 115.190.103.114" "Yellow"
Write-ColorOutput "Directory: /usr/share/nginx-after" "Yellow"
Write-ColorOutput ""

do {
    $confirm = Read-Host "Confirm deployment? (y/N)"
    $confirm = $confirm.ToLower()
} while ($confirm -notin @("y", "yes", "n", "no", ""))

if ($confirm -notin @("y", "yes")) {
    Write-ColorOutput "Deployment cancelled" "Yellow"
    Read-Host "Press Enter to exit"
    exit 0
}

Write-ColorOutput ""
Write-ColorOutput "Starting deployment..." "Green"
Write-ColorOutput ("=" * 40) "Cyan"

# Execute deployment script
python deploy_remote.py

if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput ("=" * 40) "Cyan"
    Write-ColorOutput "Deployment completed successfully!" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Application should be accessible at:" "Yellow"
    Write-ColorOutput "http://115.190.103.114:8081" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Please verify the deployment manually." "Yellow"
} else {
    Write-ColorOutput "=" * 40 "Cyan"
    Write-ColorOutput "Deployment failed!" "Red"
    Write-ColorOutput "Please check the error messages above." "Yellow"
}

Write-ColorOutput ""
Read-Host "Press Enter to exit"