#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR/android"

echo "📱 Building SwarmDroid Android Debug APK..."

export JAVA_HOME="/usr/local/sdkman/candidates/java/21.0.13.0+2-ms"
export ANDROID_HOME="${ANDROID_HOME:-/home/codespace/android-sdk}"

./gradlew assembleDebug

APK_SRC="$DIR/android/app/build/outputs/apk/debug/app-debug.apk"
APK_DEST="$DIR/app-debug.apk"

if [ -f "$APK_SRC" ]; then
    cp "$APK_SRC" "$APK_DEST"
    echo "✓ APK built successfully:"
    ls -lh "$APK_DEST"
else
    echo "❌ APK build failed or output not found at $APK_SRC"
    exit 1
fi
