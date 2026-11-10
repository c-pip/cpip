#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=========================================="
echo "🧪 Running SwarmDroid Test Suites"
echo "=========================================="

echo ""
echo "--- 1. Python Multi-Agent Backend Tests ---"
export PYTHONPATH="$DIR"
.venv/bin/pytest tests/backend/ -v

echo ""
echo "--- 2. Android Native Unit Tests ---"
cd "$DIR/android"
export JAVA_HOME="/usr/local/sdkman/candidates/java/21.0.13.0+2-ms"
export ANDROID_HOME="${ANDROID_HOME:-/home/codespace/android-sdk}"
./gradlew testDebugUnitTest

echo ""
echo "=========================================="
echo "✅ All SwarmDroid test suites passed!"
echo "=========================================="
