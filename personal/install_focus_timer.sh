#!/bin/bash

# Focus Timer 자동 시작 설치 스크립트
# macOS용

echo "🔧 Focus Timer 자동 시작 설치를 시작합니다..."

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FOCUS_TIMER_PATH="$SCRIPT_DIR/focus_timer.py"

# 스크립트가 존재하는지 확인
if [ ! -f "$FOCUS_TIMER_PATH" ]; then
    echo "❌ focus_timer.py 파일을 찾을 수 없습니다."
    echo "💡 이 스크립트를 focus_timer.py와 같은 디렉토리에 위치시켜주세요."
    exit 1
fi

# LaunchAgents 디렉토리 생성
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

# plist 파일 생성
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.focustimer.startup.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$FOCUS_TIMER_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/focus_timer.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/focus_timer_error.log</string>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
</dict>
</plist>
EOF

# 권한 설정
chmod 644 "$PLIST_FILE"

# 로그 디렉토리 생성
mkdir -p "$HOME/Library/Logs"

# LaunchAgent 등록
launchctl load "$PLIST_FILE"

echo "✅ Focus Timer 자동 시작이 설치되었습니다!"
echo "📁 설정 파일: $PLIST_FILE"
echo "📝 로그 파일: $HOME/Library/Logs/focus_timer.log"
echo ""
echo "🔄 시스템 재시작 후 자동으로 실행됩니다."
echo "💡 수동으로 시작하려면: launchctl start com.focustimer.startup"
echo "💡 수동으로 중지하려면: launchctl stop com.focustimer.startup"
echo "💡 제거하려면: launchctl unload $PLIST_FILE"