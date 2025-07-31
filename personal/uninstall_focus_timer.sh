#!/bin/bash

# Focus Timer 자동 시작 제거 스크립트
# macOS용

echo "🗑️ Focus Timer 자동 시작 제거를 시작합니다..."

# LaunchAgents 디렉토리
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.focustimer.startup.plist"

# LaunchAgent 중지 및 제거
if [ -f "$PLIST_FILE" ]; then
    echo "🛑 LaunchAgent를 중지하고 제거합니다..."
    launchctl unload "$PLIST_FILE" 2>/dev/null
    rm -f "$PLIST_FILE"
    echo "✅ LaunchAgent가 제거되었습니다."
else
    echo "ℹ️ LaunchAgent가 설치되어 있지 않습니다."
fi

# 로그 파일 정리
LOG_FILE="$HOME/Library/Logs/focus_timer.log"
ERROR_LOG_FILE="$HOME/Library/Logs/focus_timer_error.log"

if [ -f "$LOG_FILE" ]; then
    rm -f "$LOG_FILE"
    echo "✅ 로그 파일이 제거되었습니다."
fi

if [ -f "$ERROR_LOG_FILE" ]; then
    rm -f "$ERROR_LOG_FILE"
    echo "✅ 오류 로그 파일이 제거되었습니다."
fi

# 상태 파일들 정리
STATE_FILES=(
    "$HOME/focus_timer_state"
    "$HOME/focus_timer_focus_state.json"
    "$HOME/focus_timer.lock"
    "$HOME/hosts_backup"
)

echo "🧹 상태 파일들을 정리합니다..."
for file in "${STATE_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "✅ $(basename "$file") 제거됨"
    fi
done

echo "✅ Focus Timer 자동 시작이 완전히 제거되었습니다!"
echo "💡 시스템 재시작 후 자동 실행이 중단됩니다."