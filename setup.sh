#!/bin/bash
# =============================================================================
# tuanzii marketplace 注册脚本
#
# 将本项目注册为 Claude Code 的本地 Marketplace。
# 运行后在 Claude Code 中通过 /plugins 即可看到并安装本插件。
#
# 用法：
#   cd tuanzii
#   ./setup.sh
# =============================================================================

set -euo pipefail

# ── 常量 ──────────────────────────────────────────────────────────────────────
MARKETPLACE_NAME="tuanzii"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
PLUGINS_DIR="$CLAUDE_DIR/plugins"
MARKETPLACES_DIR="$PLUGINS_DIR/marketplaces"
SYMLINK_PATH="$MARKETPLACES_DIR/$MARKETPLACE_NAME"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
KNOWN_MARKETPLACES_FILE="$PLUGINS_DIR/known_marketplaces.json"

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── 前置检查 ──────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════"
echo "  tuanzii — Claude Code Marketplace 注册"
echo "══════════════════════════════════════════════════"
echo ""

# 检查 Node.js（用于 JSON 操作）
if ! command -v node &> /dev/null; then
  error "需要 Node.js 但未找到。请先安装 Node.js。"
fi

# 检查 .claude-plugin/plugin.json 存在
if [ ! -f "$PROJECT_DIR/.claude-plugin/plugin.json" ]; then
  error "当前目录不是有效的 tuanzii 项目（缺少 .claude-plugin/plugin.json）"
fi

# 检查 ~/.claude 目录
if [ ! -d "$CLAUDE_DIR" ]; then
  error "未找到 ~/.claude 目录。请确认已安装 Claude Code。"
fi

# ── 第 1 步：创建符号链接 ────────────────────────────────────────────────────
mkdir -p "$MARKETPLACES_DIR"

if [ -L "$SYMLINK_PATH" ]; then
  EXISTING_TARGET="$(readlink "$SYMLINK_PATH")"
  if [ "$EXISTING_TARGET" = "$PROJECT_DIR" ]; then
    info "符号链接已存在且正确：$SYMLINK_PATH → $PROJECT_DIR"
  else
    warn "符号链接已存在但指向其他目录：$EXISTING_TARGET"
    rm -f "$SYMLINK_PATH"
    ln -s "$PROJECT_DIR" "$SYMLINK_PATH"
    info "已更新符号链接：$SYMLINK_PATH → $PROJECT_DIR"
  fi
elif [ -e "$SYMLINK_PATH" ]; then
  error "$SYMLINK_PATH 已存在且不是符号链接，请手动检查后删除"
else
  ln -s "$PROJECT_DIR" "$SYMLINK_PATH"
  info "已创建符号链接：$SYMLINK_PATH → $PROJECT_DIR"
fi

# ── 第 2 步：注册到 settings.json ────────────────────────────────────────────
if [ ! -f "$SETTINGS_FILE" ]; then
  echo '{}' > "$SETTINGS_FILE"
  warn "settings.json 不存在，已创建空文件"
fi

SETTINGS_PATH="$SETTINGS_FILE" MARKETPLACE="$MARKETPLACE_NAME" PROJ_DIR="$PROJECT_DIR" node -e "
const fs = require('fs');
const settingsPath = process.env.SETTINGS_PATH;
const marketplace = process.env.MARKETPLACE;
const projDir = process.env.PROJ_DIR;
const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));

if (!settings.extraKnownMarketplaces) {
  settings.extraKnownMarketplaces = {};
}
settings.extraKnownMarketplaces[marketplace] = {
  source: {
    source: 'directory',
    path: projDir
  }
};

fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
"
info "已注册到 settings.json（extraKnownMarketplaces）"

# ── 第 3 步：注册到 known_marketplaces.json ──────────────────────────────────
if [ ! -f "$KNOWN_MARKETPLACES_FILE" ]; then
  echo '{}' > "$KNOWN_MARKETPLACES_FILE"
  warn "known_marketplaces.json 不存在，已创建空文件"
fi

KNOWN_FILE="$KNOWN_MARKETPLACES_FILE" MARKETPLACE="$MARKETPLACE_NAME" PROJ_DIR="$PROJECT_DIR" SYMLINK="$SYMLINK_PATH" node -e "
const fs = require('fs');
const filePath = process.env.KNOWN_FILE;
const marketplace = process.env.MARKETPLACE;
const projDir = process.env.PROJ_DIR;
const symlink = process.env.SYMLINK;
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

data[marketplace] = {
  source: {
    source: 'directory',
    path: projDir
  },
  installLocation: symlink,
  lastUpdated: new Date().toISOString()
};

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n');
"
info "已注册到 known_marketplaces.json"

# ── 第 4 步：创建插件缓存符号链接 ────────────────────────────────────────────
PLUGIN_NAME=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$PROJECT_DIR/.claude-plugin/plugin.json','utf8')).name)")
PLUGIN_VERSION=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$PROJECT_DIR/.claude-plugin/plugin.json','utf8')).version)")
CACHE_DIR="$PLUGINS_DIR/cache/$MARKETPLACE_NAME/$PLUGIN_NAME"
CACHE_VERSION_PATH="$CACHE_DIR/$PLUGIN_VERSION"

mkdir -p "$CACHE_DIR"

if [ -L "$CACHE_VERSION_PATH" ]; then
  EXISTING_CACHE_TARGET="$(readlink "$CACHE_VERSION_PATH")"
  if [ "$EXISTING_CACHE_TARGET" = "$PROJECT_DIR" ]; then
    info "缓存符号链接已存在且正确：$CACHE_VERSION_PATH → $PROJECT_DIR"
  else
    warn "缓存符号链接指向其他目录：$EXISTING_CACHE_TARGET"
    rm -f "$CACHE_VERSION_PATH"
    ln -s "$PROJECT_DIR" "$CACHE_VERSION_PATH"
    info "已更新缓存符号链接：$CACHE_VERSION_PATH → $PROJECT_DIR"
  fi
elif [ -d "$CACHE_VERSION_PATH" ]; then
  warn "缓存目录是实体目录（非符号链接），正在替换为符号链接…"
  rm -rf "$CACHE_VERSION_PATH"
  ln -s "$PROJECT_DIR" "$CACHE_VERSION_PATH"
  info "已替换缓存为符号链接：$CACHE_VERSION_PATH → $PROJECT_DIR"
else
  ln -s "$PROJECT_DIR" "$CACHE_VERSION_PATH"
  info "已创建缓存符号链接：$CACHE_VERSION_PATH → $PROJECT_DIR"
fi

# ── 第 5 步：安装输出风格到 ~/.claude/output-styles/ ─────────────────────────
OUTPUT_STYLES_SRC="$PROJECT_DIR/output-styles"
OUTPUT_STYLES_DST="$CLAUDE_DIR/output-styles"

if [ -d "$OUTPUT_STYLES_SRC" ]; then
  mkdir -p "$OUTPUT_STYLES_DST"
  STYLE_COUNT=0

  for style_file in "$OUTPUT_STYLES_SRC"/*.md; do
    [ -f "$style_file" ] || continue
    filename="$(basename "$style_file")"
    dst_path="$OUTPUT_STYLES_DST/$filename"

    if [ -L "$dst_path" ]; then
      existing="$(readlink "$dst_path")"
      if [ "$existing" = "$style_file" ]; then
        STYLE_COUNT=$((STYLE_COUNT + 1))
        continue
      else
        rm -f "$dst_path"
      fi
    elif [ -f "$dst_path" ]; then
      rm -f "$dst_path"
    fi

    ln -s "$style_file" "$dst_path"
    STYLE_COUNT=$((STYLE_COUNT + 1))
  done

  info "已安装 $STYLE_COUNT 个输出风格到 $OUTPUT_STYLES_DST（符号链接）"
else
  warn "未找到 output-styles 目录，跳过输出风格安装"
fi

# ── 完成 ──────────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════"
echo -e "  ${GREEN}注册完成！${NC}"
echo "══════════════════════════════════════════════════"
echo ""
echo "  后续步骤："
echo "  1. 重启 Claude Code"
echo "  2. 输入 /plugins"
echo "  3. 找到 $PLUGIN_NAME 并安装"
echo ""
echo "  提示："
echo "  • 缓存已通过符号链接指向源目录，"
echo "    后续新增/修改 skill 无需重新安装插件。"
echo "  • 输出风格已链接到 ~/.claude/output-styles/，"
echo "    可通过 /output-style 命令切换风格。"
echo ""
