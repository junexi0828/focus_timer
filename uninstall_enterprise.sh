#!/bin/bash

# Focus Timer Enterprise - 완전 제거 스크립트
# 상업용 출시 버전

set -e

PRODUCT_NAME="Focus Timer Enterprise"
VERSION="2.0.0"

echo "🗑️ $PRODUCT_NAME v$VERSION 완전 제거를 시작합니다..."

# 관리자 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "❌ 관리자 권한이 필요합니다."
    echo "💡 sudo ./uninstall_enterprise.sh로 실행해주세요."
    exit 1
fi

# 서비스 중지
echo "🛑 서비스 중지 중..."

# 메인 서비스 중지
if launchctl list | grep -q "com.focustimer.enterprise"; then
    launchctl unload "/Library/LaunchDaemons/com.focustimer.enterprise.plist" 2>/dev/null || true
    echo "✅ 메인 서비스 중지 완료"
fi

# 웹 서비스 중지
if launchctl list | grep -q "com.focustimer.web"; then
    launchctl unload "/Library/LaunchDaemons/com.focustimer.web.plist" 2>/dev/null || true
    echo "✅ 웹 서비스 중지 완료"
fi

# LaunchDaemon 파일 제거
echo "🗑️ 시스템 서비스 파일 제거 중..."

LAUNCH_FILES=(
    "/Library/LaunchDaemons/com.focustimer.enterprise.plist"
    "/Library/LaunchDaemons/com.focustimer.web.plist"
)

for file in "${LAUNCH_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "✅ $file 제거됨"
    fi
done

# 애플리케이션 디렉토리 제거
APP_DIR="/Applications/FocusTimer"
if [ -d "$APP_DIR" ]; then
    echo "🗑️ 애플리케이션 디렉토리 제거 중..."
    rm -rf "$APP_DIR"
    echo "✅ $APP_DIR 제거됨"
fi

# 설정 디렉토리 제거
CONFIG_DIR="/Library/Application Support/FocusTimer"
if [ -d "$CONFIG_DIR" ]; then
    echo "🗑️ 설정 디렉토리 제거 중..."
    rm -rf "$CONFIG_DIR"
    echo "✅ $CONFIG_DIR 제거됨"
fi

# 로그 디렉토리 제거
LOG_DIR="/var/log/FocusTimer"
if [ -d "$LOG_DIR" ]; then
    echo "🗑️ 로그 디렉토리 제거 중..."
    rm -rf "$LOG_DIR"
    echo "✅ $LOG_DIR 제거됨"
fi

# 사용자 설정 파일들 제거
USER_FILES=(
    "$HOME/focus_timer_state"
    "$HOME/focus_timer_focus_state.json"
    "$HOME/focus_timer.lock"
    "$HOME/hosts_backup"
    "$HOME/Library/Application Support/FocusTimer"
    "$HOME/Library/Logs/FocusTimer"
)

echo "🗑️ 사용자 설정 파일 제거 중..."
for file in "${USER_FILES[@]}"; do
    if [ -e "$file" ]; then
        rm -rf "$file"
        echo "✅ $file 제거됨"
    fi
done

# hosts 파일 복구
echo "🔧 hosts 파일 복구 중..."
if [ -f "$HOME/hosts_backup" ]; then
    cp "$HOME/hosts_backup" "/etc/hosts"
    echo "✅ hosts 파일 백업에서 복구됨"
else
    # FocusTimer 블록 제거
    if [ -f "/etc/hosts" ]; then
        # 임시 파일 생성
        temp_hosts="/tmp/hosts_clean"

        # FocusTimer 블록 제외하고 복사
        grep -v "FocusTimer Enterprise" /etc/hosts > "$temp_hosts"

        # 원본 파일 교체
        cp "$temp_hosts" "/etc/hosts"
        rm -f "$temp_hosts"

        echo "✅ hosts 파일에서 FocusTimer 블록 제거됨"
    fi
fi

# 방화벽 규칙 제거
echo "🔧 방화벽 규칙 제거 중..."
if command -v pfctl &> /dev/null; then
    # 방화벽 비활성화
    pfctl -d 2>/dev/null || true

    # 임시 규칙 파일 제거
    rm -f "/tmp/focus_timer_pf.conf"

    echo "✅ 방화벽 규칙 제거됨"
fi

# DNS 캐시 초기화
echo "🔄 DNS 캐시 초기화 중..."
dscacheutil -flushcache 2>/dev/null || true
killall -HUP mDNSResponder 2>/dev/null || true
echo "✅ DNS 캐시 초기화됨"

# 브라우저 캐시 초기화
echo "🧹 브라우저 캐시 초기화 중..."
browsers=("Google Chrome" "Safari" "Firefox" "Whale" "Microsoft Edge")

for browser in "${browsers[@]}"; do
    case "$browser" in
        "Google Chrome")
            cache_paths=(
                "$HOME/Library/Caches/Google/Chrome/Default/Cache"
                "$HOME/Library/Application Support/Google/Chrome/Default/Cache"
            )
            ;;
        "Safari")
            cache_paths=(
                "$HOME/Library/Caches/com.apple.Safari"
                "$HOME/Library/Safari/LocalStorage"
            )
            ;;
        *)
            continue
            ;;
    esac

    for path in "${cache_paths[@]}"; do
        if [ -d "$path" ]; then
            rm -rf "$path"/* 2>/dev/null || true
        fi
    done
done
echo "✅ 브라우저 캐시 초기화됨"

# 가상환경 제거
VENV_DIR="/Applications/FocusTimer/venv"
if [ -d "$VENV_DIR" ]; then
    echo "🗑️ Python 가상환경 제거 중..."
    rm -rf "$VENV_DIR"
    echo "✅ 가상환경 제거됨"
fi

# 브라우저 확장 프로그램 제거 안내
echo "🌐 브라우저 확장 프로그램 제거 안내"
echo "💡 Chrome에서 chrome://extensions/로 이동하여 'Focus Timer Enterprise' 확장 프로그램을 수동으로 제거해주세요."

# 제거 완료 메시지
echo ""
echo "🎉 $PRODUCT_NAME v$VERSION 완전 제거가 완료되었습니다!"
echo ""
echo "📋 제거된 구성 요소:"
echo "  ✅ 시스템 서비스 (LaunchDaemon)"
echo "  ✅ 애플리케이션 파일"
echo "  ✅ 설정 파일"
echo "  ✅ 로그 파일"
echo "  ✅ hosts 파일 복구"
echo "  ✅ 방화벽 규칙 제거"
echo "  ✅ DNS 캐시 초기화"
echo "  ✅ 브라우저 캐시 초기화"
echo ""
echo "⚠️ 수동 제거 필요:"
echo "  🌐 브라우저 확장 프로그램 (Chrome 확장 프로그램 관리에서 제거)"
echo ""
echo "🔄 시스템 재시작을 권장합니다."
echo "📞 기술 지원: support@focustimer.com"