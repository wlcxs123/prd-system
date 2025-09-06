# PowerShell 远程服务器自动部署脚本
# 编码: UTF-8

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 显示标题
Clear-Host
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "🚀 远程服务器自动部署脚本" "Green"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""
Write-ColorOutput "📡 目标服务器: 115.190.103.114" "Yellow"
Write-ColorOutput "📁 部署目录: /usr/share/nginx-after" "Yellow"
Write-ColorOutput "🌐 应用端口: 8081" "Yellow"
Write-Host ""
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

try {
    # 检查Python环境
    Write-ColorOutput "🔍 检查Python环境..." "Blue"
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ 错误: 未找到Python环境" "Red"
        Write-ColorOutput "请确保已安装Python并添加到PATH" "Red"
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-ColorOutput "✅ Python环境检查通过: $pythonVersion" "Green"
    
    # 检查依赖包
    Write-ColorOutput "📦 检查依赖包..." "Blue"
    $importTest = python -c "import paramiko, scp; print('Dependencies OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "⚠️ 依赖包未安装，正在安装..." "Yellow"
        
        # 安装依赖
        Write-ColorOutput "正在安装 paramiko 和 scp..." "Blue"
        pip install -r deploy_requirements.txt
        
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "❌ 依赖安装失败" "Red"
            Read-Host "按Enter键退出"
            exit 1
        }
        
        Write-ColorOutput "✅ 依赖安装完成" "Green"
    } else {
        Write-ColorOutput "✅ 依赖包检查通过" "Green"
    }
    
    # 确认部署
    Write-Host ""
    Write-ColorOutput "⚠️ 即将开始部署到生产服务器" "Yellow"
    Write-ColorOutput "📡 服务器: 115.190.103.114" "Yellow"
    Write-ColorOutput "📁 目录: /usr/share/nginx-after" "Yellow"
    Write-Host ""
    
    do {
        $confirm = Read-Host "确认开始部署？(y/N)"
        $confirm = $confirm.ToLower()
    } while ($confirm -notin @("y", "yes", "n", "no", ""))
    
    if ($confirm -notin @("y", "yes")) {
        Write-ColorOutput "❌ 部署已取消" "Yellow"
        Read-Host "按Enter键退出"
        exit 0
    }
    
    # 执行部署
    Write-Host ""
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "🚀 开始部署..." "Green"
    Write-ColorOutput "========================================" "Cyan"
    Write-Host ""
    
    # 运行Python部署脚本
    python deploy_remote.py
    
    # 检查部署结果
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-ColorOutput "========================================" "Green"
        Write-ColorOutput "✅ 部署成功完成！" "Green"
        Write-ColorOutput "🌐 应用地址: http://115.190.103.114:8081" "Cyan"
        Write-ColorOutput "📋 健康检查: http://115.190.103.114:8081/health" "Cyan"
        Write-ColorOutput "📝 查看日志: tail -f /usr/share/nginx-after/logs/app.log" "Yellow"
        Write-ColorOutput "========================================" "Green"
    } else {
        Write-Host ""
        Write-ColorOutput "========================================" "Red"
        Write-ColorOutput "❌ 部署失败！" "Red"
        Write-ColorOutput "📝 请查看 deploy.log 获取详细信息" "Yellow"
        Write-ColorOutput "========================================" "Red"
    }
    
} catch {
    Write-ColorOutput "❌ 发生未预期的错误: $($_.Exception.Message)" "Red"
    Write-ColorOutput "📝 请查看错误详情并重试" "Yellow"
} finally {
    Write-Host ""
    Read-Host "按任意键退出"
}