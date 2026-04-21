﻿# =============================================================================
# tuanzii marketplace 注册脚本 (Windows PowerShell)
#
# 将本项目注册为 Claude Code 的本地 Marketplace。
# 运行后在 Claude Code 中通过 /plugins 即可看到并安装本插件。
#
# 用法：
#   cd tuanzii
#   .\setup.ps1
#
# 注意：Windows 创建符号链接需要管理员权限（或开启开发者模式）。
#   如果遇到权限错误，请以管理员身份运行 PowerShell，
#   或在 Windows 设置 > 开发者选项中启用"开发人员模式"。
# =============================================================================

$ErrorActionPreference = "Stop"

# ── 常量 ──────────────────────────────────────────────────────────────────────
$MARKETPLACE_NAME = "tuanzii"
$PROJECT_DIR = $PSScriptRoot
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$PLUGINS_DIR = Join-Path $CLAUDE_DIR "plugins"
$MARKETPLACES_DIR = Join-Path $PLUGINS_DIR "marketplaces"
$SYMLINK_PATH = Join-Path $MARKETPLACES_DIR $MARKETPLACE_NAME
$SETTINGS_FILE = Join-Path $CLAUDE_DIR "settings.json"
$KNOWN_MARKETPLACES_FILE = Join-Path $PLUGINS_DIR "known_marketplaces.json"

# ── 辅助函数 ──────────────────────────────────────────────────────────────────
function Info($msg)  { Write-Host "[OK] $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Fail($msg)  { Write-Host "[X] $msg" -ForegroundColor Red; exit 1 }

function Is-Symlink($path) {
    if (-not (Test-Path $path)) { return $false }
    $item = Get-Item $path
    return $item.Attributes -band [System.IO.FileAttributes]::ReparsePoint
}

function Create-Symlink($target, $link) {
    $linkDir = Split-Path $link -Parent
    if (-not (Test-Path $linkDir)) {
        New-Item -ItemType Directory -Path $linkDir -Force | Out-Null
    }
    New-Item -ItemType SymbolicLink -Target $target -Path $link | Out-Null
}

# ── 前置检查 ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=================================================="
Write-Host "  tuanzii - Claude Code Marketplace "
Write-Host "=================================================="
Write-Host ""

# 检查 .claude-plugin/plugin.json
$pluginJsonPath = Join-Path $PROJECT_DIR ".claude-plugin\plugin.json"
if (-not (Test-Path $pluginJsonPath -PathType Leaf)) {
    Fail "当前目录不是有效的 tuanzii 项目（缺少 .claude-plugin/plugin.json）"
}

# 检查 ~/.claude 目录
if (-not (Test-Path $CLAUDE_DIR -PathType Container)) {
    Fail "未找到 $CLAUDE_DIR 目录。请确认已安装 Claude Code。"
}

# ── 第 1 步：创建符号链接 ────────────────────────────────────────────────────
if (-not (Test-Path $MARKETPLACES_DIR)) {
    New-Item -ItemType Directory -Path $MARKETPLACES_DIR -Force | Out-Null
}

if (Is-Symlink $SYMLINK_PATH) {
    $existingTarget = (Get-Item $SYMLINK_PATH).Target
    if ($existingTarget -eq $PROJECT_DIR) {
        Info "symbolic link already exists: $SYMLINK_PATH -> $PROJECT_DIR"
    } else {
        Warn "symbolic link points to different dir: $existingTarget"
        Remove-Item -Force $SYMLINK_PATH
        Create-Symlink $PROJECT_DIR $SYMLINK_PATH
        Info "updated symbolic link: $SYMLINK_PATH -> $PROJECT_DIR"
    }
} elseif (Test-Path $SYMLINK_PATH) {
    Warn "$SYMLINK_PATH exists but is not a symlink, replacing..."
    Remove-Item -Recurse -Force $SYMLINK_PATH
    Create-Symlink $PROJECT_DIR $SYMLINK_PATH
    Info "replaced with symbolic link: $SYMLINK_PATH -> $PROJECT_DIR"
} else {
    Create-Symlink $PROJECT_DIR $SYMLINK_PATH
    Info "created symbolic link: $SYMLINK_PATH -> $PROJECT_DIR"
}

# ── 第 2 步：注册到 settings.json ────────────────────────────────────────────
if (-not (Test-Path $SETTINGS_FILE -PathType Leaf)) {
    @{} | ConvertTo-Json -Depth 10 | Set-Content $SETTINGS_FILE -Encoding UTF8
    Warn "settings.json not found, created empty file"
}

$settings = Get-Content $SETTINGS_FILE -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $settings.extraKnownMarketplaces) {
    $settings | Add-Member -NotePropertyName "extraKnownMarketplaces" -NotePropertyValue @{} -Force
}
if (-not $settings.extraKnownMarketplaces.$MARKETPLACE_NAME) {
    $settings.extraKnownMarketplaces | Add-Member -NotePropertyName $MARKETPLACE_NAME -NotePropertyValue @{} -Force
}
$settings.extraKnownMarketplaces.$MARKETPLACE_NAME | Add-Member -NotePropertyName "source" -NotePropertyValue @{
    source = "directory"
    path   = $PROJECT_DIR
} -Force

$settings | ConvertTo-Json -Depth 10 | Set-Content $SETTINGS_FILE -Encoding UTF8
Info "registered in settings.json (extraKnownMarketplaces)"

# ── 第 3 步：注册到 known_marketplaces.json ──────────────────────────────────
if (-not (Test-Path $KNOWN_MARKETPLACES_FILE -PathType Leaf)) {
    @{} | ConvertTo-Json -Depth 10 | Set-Content $KNOWN_MARKETPLACES_FILE -Encoding UTF8
    Warn "known_marketplaces.json not found, created empty file"
}

$known = Get-Content $KNOWN_MARKETPLACES_FILE -Raw -Encoding UTF8 | ConvertFrom-Json
$known | Add-Member -NotePropertyName $MARKETPLACE_NAME -NotePropertyValue @{
    source          = @{
        source = "directory"
        path   = $PROJECT_DIR
    }
    installLocation = $SYMLINK_PATH
    lastUpdated     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} -Force

$known | ConvertTo-Json -Depth 10 | Set-Content $KNOWN_MARKETPLACES_FILE -Encoding UTF8
Info "registered in known_marketplaces.json"

# ── 第 4 步：创建插件缓存符号链接 ────────────────────────────────────────────
$pluginJson = Get-Content $pluginJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$pluginName = $pluginJson.name
$pluginVersion = $pluginJson.version
$cacheDir = Join-Path $PLUGINS_DIR "cache\$MARKETPLACE_NAME\$pluginName"
$cacheVersionPath = Join-Path $cacheDir $pluginVersion

if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
}

if (Is-Symlink $cacheVersionPath) {
    $existingCacheTarget = (Get-Item $cacheVersionPath).Target
    if ($existingCacheTarget -eq $PROJECT_DIR) {
        Info "cache symlink already exists: $cacheVersionPath -> $PROJECT_DIR"
    } else {
        Warn "cache symlink points to different dir: $existingCacheTarget"
        Remove-Item -Force $cacheVersionPath
        Create-Symlink $PROJECT_DIR $cacheVersionPath
        Info "updated cache symlink: $cacheVersionPath -> $PROJECT_DIR"
    }
} elseif (Test-Path $cacheVersionPath -PathType Container) {
    Warn "cache dir is not a symlink, replacing..."
    Remove-Item -Recurse -Force $cacheVersionPath
    Create-Symlink $PROJECT_DIR $cacheVersionPath
    Info "replaced cache with symlink: $cacheVersionPath -> $PROJECT_DIR"
} else {
    Create-Symlink $PROJECT_DIR $cacheVersionPath
    Info "created cache symlink: $cacheVersionPath -> $PROJECT_DIR"
}

# ── 第 5 步：安装输出风格到 ~/.claude/output-styles/ ─────────────────────────
$OUTPUT_STYLES_SRC = Join-Path $PROJECT_DIR "output-styles"
$OUTPUT_STYLES_DST = Join-Path $CLAUDE_DIR "output-styles"

if (Test-Path $OUTPUT_STYLES_SRC -PathType Container) {
    if (-not (Test-Path $OUTPUT_STYLES_DST)) {
        New-Item -ItemType Directory -Path $OUTPUT_STYLES_DST -Force | Out-Null
    }
    $styleCount = 0

    Get-ChildItem -Path $OUTPUT_STYLES_SRC -Filter "*.md" | ForEach-Object {
        $srcFile = $_.FullName
        $dstFile = Join-Path $OUTPUT_STYLES_DST $_.Name

        if (Is-Symlink $dstFile) {
            $existingTarget = (Get-Item $dstFile).Target
            if ($existingTarget -eq $srcFile) {
                $script:styleCount++
                return
            } else {
                Remove-Item -Force $dstFile
            }
        } elseif (Test-Path $dstFile -PathType Leaf) {
            Remove-Item -Force $dstFile
        }

        Create-Symlink $srcFile $dstFile
        $script:styleCount++
    }

    Info "installed $styleCount output styles to $OUTPUT_STYLES_DST (symlinks)"
} else {
    Warn "output-styles directory not found, skipping"
}

# ── 完成 ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  Done!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:"
Write-Host "  1. Restart Claude Code"
Write-Host "  2. Type /plugins"
Write-Host "  3. Find $pluginName and install"
Write-Host ""
Write-Host "  Tips:"
Write-Host "  - Cache is symlinked to source dir,"
Write-Host "    adding/editing skills does not require reinstall."
Write-Host "  - Output styles are linked to ~/.claude/output-styles/,"
Write-Host "    switch styles via /output-style command."
Write-Host ""
