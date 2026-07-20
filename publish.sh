#!/bin/bash
# GitHub Pages 手动发布：只发布指定 demo，不提交整个工作区
# 用法：
#   ./publish.sh demo文件/06-21-券包后台4.0/
#   ./publish.sh demo文件/07-02-述职展示/述职展示2.0.html
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "❌ 当前目录不是 git 仓库"
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "用法: ./publish.sh <路径> [更多路径...]"
  echo ""
  echo "示例:"
  echo "  ./publish.sh demo文件/06-21-券包后台4.0/"
  echo "  ./publish.sh demo文件/07-02-述职展示/述职展示2.0.html"
  exit 1
fi

TARGETS=()
for path in "$@"; do
  if [ ! -e "$path" ]; then
    echo "❌ 路径不存在: $path"
    exit 1
  fi
  TARGETS+=("$path")
done

git add "${TARGETS[@]}"

if git diff --cached --quiet; then
  echo "✓ 指定路径没有变更，跳过发布"
  exit 0
fi

echo "将发布以下变更:"
git diff --cached --stat

MSG="更新 ${TARGETS[*]} $(date '+%Y-%m-%d %H:%M')"
git commit -m "$MSG"
git push

REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
echo ""
echo "✓ 已发布"
if [[ "$REMOTE" =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
  USER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  BASE="https://${USER}.github.io/${REPO}"
  echo "  站点: ${BASE}/"
  for path in "${TARGETS[@]}"; do
    if [[ "$path" == *.html ]]; then
      echo "  链接: ${BASE}/${path}"
    fi
  done
fi
