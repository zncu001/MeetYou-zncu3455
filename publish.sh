#!/bin/bash
# GitHub Pages 手动发布：本地确认 OK 后执行 ./publish.sh
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "❌ 当前目录不是 git 仓库"
  exit 1
fi

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "✓ 没有变更，跳过发布"
  exit 0
fi

git add -A
MSG="更新站点 $(date '+%Y-%m-%d %H:%M')"
git commit -m "$MSG"
git push

REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
echo ""
echo "✓ 已发布"
if [[ "$REMOTE" =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
  USER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  echo "  https://${USER}.github.io/${REPO}/"
fi
