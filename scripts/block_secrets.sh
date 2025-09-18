#!/bin/bash
if git diff --cached --name-only | grep -E '\.env|config\.json|\.pem|\.key|\.crt|\.sqlite'; then
  echo "❌ 機密ファイルが含まれています。コミットできません。"
  exit 1
fi
