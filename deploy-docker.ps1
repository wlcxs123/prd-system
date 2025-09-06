# 问卷数据管理系统 Docker 部署脚本 (Windows PowerShell)
# 使用方法: .\deploy-docker.ps1 [命令] [环境]
# 环境选项: dev, staging, prod

param(
    [Parameter(Position=0)]
    [string]$Command = "deploy",
    [Parameter(Position=1)]
    [string]$Environment = "prod"
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查系统依赖..."
    
    # 检查 Docker
    try {
        $dockerVersion = docker --version
        Write-Info "Docker 版本: $dockerVersion"
    }
    catch {
        Write-Error "Docker 未安装或未启动，请先安装并启动 Docker Desktop"
        exit 1
    }
    
    # 检查 Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Info "Docker Compose 版本: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    }
    
    Write-Success "依赖检查完成"
}

# 设置环境变量
function Set-Environment {
    param([string]$Env)
    
    Write-Info "设置 $Env 环境变量..."
    
    # 检查 .env 文件
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Warning ".env 文件不存在，从 .env.example 复制"
            Copy-Item ".env.example" ".env"
            Write-Warning "请编辑 .env 文件并设置正确的配置值"
        }
        else {
            Write-Error ".env.example 文件不存在"
            exit 1
        }
    }
    
    # 生成随机密钥（如果需要）
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your-super-secret-key-change-this-in-production") {
        Write-Info "生成随机 SECRET_KEY..."
        $secretKey = [System.Web.Security.Membership]::GeneratePassword(64, 0)
        $envContent = $envContent -replace "your-super-secret-key-change-this-in-production", $secretKey
        Set-Content ".env" $envContent
    }
    
    Write-Success "环境变量设置完成"
}

# 创建必要的目录
function New-Directories {
    Write-Info "创建必要的目录..."
    
    $directories = @("ssl", "data\backups", "logs")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "目录创建完成"
}

# 生成自签名SSL证书（用于测试）
function New-SslCertificate {
    if (-not (Test-Path "ssl\cert.pem") -or -not (Test-Path "ssl\key.pem")) {
        Write-Info "生成自签名 SSL 证书（仅用于测试）..."
        
        try {
            # 使用 OpenSSL 生成证书（如果可用）
            & openssl req -x509 -newkey rsa:4096 -keyout ssl\key.pem -out ssl\cert.pem -days 365 -nodes -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
            Write-Warning "已生成自签名证书，生产环境请使用正式证书"
        }
        catch {
            Write-Warning "OpenSSL 不可用，跳过 SSL 证书生成"
            Write-Warning "请手动生成 SSL 证书或使用 HTTP 模式"
        }
    }
}

# 构建镜像
function Build-Image {
    Write-Info "构建 Docker 镜像..."
    
    & docker-compose build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Error "镜像构建失败"
        exit 1
    }
    
    Write-Success "镜像构建完成"
}

# 启动服务
function Start-Services {
    Write-Info "启动服务..."
    
    & docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Error "服务启动失败"
        exit 1
    }
    
    Write-Success "服务启动完成"
}

# 等待服务就绪
function Wait-ForServices {
    Write-Info "等待服务就绪..."
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "服务已就绪"
                return
            }
        }
        catch {
            # 忽略错误，继续等待
        }
        
        Write-Info "等待服务启动... ($attempt/$maxAttempts)"
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    Write-Error "服务启动超时"
    exit 1
}

# 显示服务状态
function Show-Status {
    Write-Info "服务状态:"
    & docker-compose ps
    
    Write-Host ""
    Write-Info "服务日志:"
    & docker-compose logs --tail=20
    
    Write-Host ""
    Write-Info "访问地址:"
    Write-Host "  HTTP:  http://localhost" -ForegroundColor White
    Write-Host "  HTTPS: https://localhost" -ForegroundColor White
    Write-Host "  管理后台: http://localhost/admin" -ForegroundColor White
}

# 停止服务
function Stop-Services {
    Write-Info "停止服务..."
    & docker-compose down
    Write-Success "服务已停止"
}

# 清理资源
function Remove-Resources {
    Write-Info "清理 Docker 资源..."
    & docker-compose down -v --rmi all
    & docker system prune -f
    Write-Success "清理完成"
}

# 备份数据
function Backup-Data {
    Write-Info "备份数据..."
    
    $backupDir = "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # 备份数据库
    $containerId = & docker-compose ps -q app
    & docker-compose exec -T app sqlite3 /app/data/questionnaires.db ".backup /app/backups/db_backup.db"
    & docker cp "${containerId}:/app/backups/db_backup.db" "$backupDir\"
    
    # 备份配置文件
    Copy-Item ".env" "$backupDir\"
    
    Write-Success "数据备份完成: $backupDir"
}

# 恢复数据
function Restore-Data {
    param([string]$BackupFile)
    
    if (-not $BackupFile) {
        Write-Error "请指定备份文件路径"
        exit 1
    }
    
    if (-not (Test-Path $BackupFile)) {
        Write-Error "备份文件不存在: $BackupFile"
        exit 1
    }
    
    Write-Info "恢复数据: $BackupFile"
    
    $containerId = & docker-compose ps -q app
    & docker cp $BackupFile "${containerId}:/app/data/questionnaires.db"
    & docker-compose restart app
    
    Write-Success "数据恢复完成"
}

# 显示帮助信息
function Show-Help {
    Write-Host "问卷数据管理系统 Docker 部署脚本 (Windows)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "使用方法:"
    Write-Host "  .\deploy-docker.ps1 [命令] [选项]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  deploy [env]    部署系统 (env: dev|staging|prod, 默认: prod)"
    Write-Host "  start           启动服务"
    Write-Host "  stop            停止服务"
    Write-Host "  restart         重启服务"
    Write-Host "  status          显示服务状态"
    Write-Host "  logs            显示服务日志"
    Write-Host "  backup          备份数据"
    Write-Host "  restore <file>  恢复数据"
    Write-Host "  cleanup         清理 Docker 资源"
    Write-Host "  help            显示帮助信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\deploy-docker.ps1 deploy prod    # 部署生产环境"
    Write-Host "  .\deploy-docker.ps1 start          # 启动服务"
    Write-Host "  .\deploy-docker.ps1 backup         # 备份数据"
}

# 主函数
function Main {
    param(
        [string]$Cmd,
        [string]$Env
    )
    
    switch ($Cmd.ToLower()) {
        "deploy" {
            Test-Dependencies
            Set-Environment $Env
            New-Directories
            New-SslCertificate
            Build-Image
            Start-Services
            Wait-ForServices
            Show-Status
        }
        "start" {
            Start-Services
            Wait-ForServices
            Show-Status
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Stop-Services
            Start-Services
            Wait-ForServices
            Show-Status
        }
        "status" {
            Show-Status
        }
        "logs" {
            & docker-compose logs -f
        }
        "backup" {
            Backup-Data
        }
        "restore" {
            Restore-Data $Env
        }
        "cleanup" {
            Remove-Resources
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "未知命令: $Cmd"
            Show-Help
            exit 1
        }
    }
}

# 执行主函数
try {
    Main $Command $Environment
}
catch {
    Write-Error "执行失败: $($_.Exception.Message)"
    exit 1
}