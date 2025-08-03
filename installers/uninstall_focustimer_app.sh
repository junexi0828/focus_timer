#!/bin/bash

# FocusTimer.app - 완전 제거 스크립트
# macOS 앱 구조 집중 모드 시스템

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 버전 정보
CURRENT_VERSION="2.0.0"
PRODUCT_NAME="FocusTimer.app"

echo -e "${BLUE}🗑️ $PRODUCT_NAME v$CURRENT_VERSION 완전 제거를 시작합니다...${NC}"

# 관리자 권한 확인
if [[ $EUID -ne 0 ]]; then
    log_error "관리자 권한이 필요합니다: sudo $0"
    exit 1
fi

# 서비스 중지
log_step "서비스 중지 중..."

# LaunchAgent 서비스 중지
if launchctl list | grep -q "com.focustimer.helper"; then
    log_info "LaunchAgent 서비스 중지 중..."
    launchctl unload "/Library/LaunchAgents/com.focustimer.helper.plist" 2>/dev/null || true
    log_info "LaunchAgent 서비스 중지 완료"
else
    log_info "실행 중인 LaunchAgent 서비스가 없습니다"
fi

# LaunchDaemon 서비스 중지 (혹시 있을 경우)
if launchctl list | grep -q "com.focustimer.helper"; then
    log_info "LaunchDaemon 서비스 중지 중..."
    launchctl unload "/Library/LaunchDaemons/com.focustimer.helper.plist" 2>/dev/null || true
    log_info "LaunchDaemon 서비스 중지 완료"
fi

# 실행 중인 프로세스 종료
log_step "실행 중인 프로세스 종료 중..."

# FocusTimer 관련 프로세스 종료
if pgrep -f "FocusTimer" > /dev/null; then
    log_info "FocusTimer 프로세스 종료 중..."
    pkill -f "FocusTimer" 2>/dev/null || true
    sleep 2

    # 강제 종료 (필요한 경우)
    if pgrep -f "FocusTimer" > /dev/null; then
        log_warn "일반 종료 실패, 강제 종료 시도..."
        pkill -9 -f "FocusTimer" 2>/dev/null || true
    fi
    log_info "프로세스 종료 완료"
else
    log_info "실행 중인 FocusTimer 프로세스가 없습니다"
fi

# 시스템 서비스 파일 제거
log_step "시스템 서비스 파일 제거 중..."

LAUNCH_FILES=(
    "/Library/LaunchAgents/com.focustimer.helper.plist"
    "/Library/LaunchDaemons/com.focustimer.helper.plist"
)

for file in "${LAUNCH_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        rm -f "$file"
        log_info "$file 제거됨"
    else
        log_info "$file 파일이 없습니다"
    fi
done

# 애플리케이션 제거
log_step "애플리케이션 제거 중..."

APP_PATH="/Applications/FocusTimer.app"
if [[ -d "$APP_PATH" ]]; then
    log_info "FocusTimer.app 제거 중..."
    rm -rf "$APP_PATH"
    log_info "FocusTimer.app 제거 완료"
else
    log_info "FocusTimer.app이 설치되어 있지 않습니다"
fi

# CLI 도구 제거
log_step "CLI 도구 제거 중..."

CLI_LINK="/usr/local/bin/focus-timer"
if [[ -L "$CLI_LINK" ]] || [[ -f "$CLI_LINK" ]]; then
    rm -f "$CLI_LINK"
    log_info "CLI 도구 제거 완료"
else
    log_info "CLI 도구가 설치되어 있지 않습니다"
fi

# CLI 도구 백업 파일 제거
CLI_BACKUP_PATTERN="/usr/local/bin/focus-timer.backup.*"
if ls $CLI_BACKUP_PATTERN 1> /dev/null 2>&1; then
    rm -f $CLI_BACKUP_PATTERN
    log_info "CLI 도구 백업 파일 제거 완료"
fi

# 설정 디렉토리 제거 (선택적)
log_step "설정 파일 정리 중..."

CONFIG_DIR="/Library/Application Support/FocusTimer"
if [[ -d "$CONFIG_DIR" ]]; then
    log_warn "설정 디렉토리가 발견되었습니다: $CONFIG_DIR"
    read -p "설정 파일도 함께 제거하시겠습니까? (y/n): " remove_config
    if [[ $remove_config == "y" ]]; then
        rm -rf "$CONFIG_DIR"
        log_info "설정 디렉토리 제거 완료"
    else
        log_info "설정 디렉토리를 유지합니다"
    fi
else
    log_info "설정 디렉토리가 없습니다"
fi

# 로그 디렉토리 제거 (선택적)
LOG_DIR="/var/log/FocusTimer"
if [[ -d "$LOG_DIR" ]]; then
    log_warn "로그 디렉토리가 발견되었습니다: $LOG_DIR"
    read -p "로그 파일도 함께 제거하시겠습니까? (y/n): " remove_logs
    if [[ $remove_logs == "y" ]]; then
        rm -rf "$LOG_DIR"
        log_info "로그 디렉토리 제거 완료"
    else
        log_info "로그 디렉토리를 유지합니다"
    fi
else
    log_info "로그 디렉토리가 없습니다"
fi

# 사용자 설정 파일 제거 (선택적)
log_step "사용자 설정 파일 정리 중..."

USER_FILES=(
    "$HOME/focus_timer_state"
    "$HOME/focus_timer_focus_state.json"
    "$HOME/focus_timer.lock"
    "$HOME/hosts_backup"
    "$HOME/Library/Application Support/FocusTimer"
    "$HOME/Library/Logs/FocusTimer"
)

found_user_files=false
for file in "${USER_FILES[@]}"; do
    if [[ -e "$file" ]]; then
        found_user_files=true
        break
    fi
done

if [[ $found_user_files == true ]]; then
    log_warn "사용자 설정 파일들이 발견되었습니다"
    read -p "사용자 설정 파일도 함께 제거하시겠습니까? (y/n): " remove_user_files
    if [[ $remove_user_files == "y" ]]; then
        for file in "${USER_FILES[@]}"; do
            if [[ -e "$file" ]]; then
                rm -rf "$file"
                log_info "$file 제거됨"
            fi
        done
        log_info "사용자 설정 파일 제거 완료"
    else
        log_info "사용자 설정 파일을 유지합니다"
    fi
else
    log_info "사용자 설정 파일이 없습니다"
fi

# hosts 파일 복구
log_step "hosts 파일 복구 중..."

if [[ -f "/etc/hosts" ]]; then
    # FocusTimer 블록 제거
    temp_hosts="/tmp/hosts_clean"

    # FocusTimer 블록 제외하고 복사
    if grep -q "FocusTimer" "/etc/hosts"; then
        grep -v "FocusTimer" "/etc/hosts" > "$temp_hosts"

        # 원본 파일 교체
        cp "$temp_hosts" "/etc/hosts"
        rm -f "$temp_hosts"

        log_info "hosts 파일에서 FocusTimer 블록 제거됨"
    else
        log_info "hosts 파일에 FocusTimer 블록이 없습니다"
    fi
else
    log_warn "hosts 파일을 찾을 수 없습니다"
fi

# DNS 캐시 초기화
log_step "DNS 캐시 초기화 중..."

if command -v dscacheutil &> /dev/null; then
    dscacheutil -flushcache 2>/dev/null || true
    log_info "DNS 캐시 초기화 완료"
else
    log_warn "dscacheutil을 찾을 수 없습니다"
fi

if command -v killall &> /dev/null; then
    killall -HUP mDNSResponder 2>/dev/null || true
    log_info "mDNSResponder 재시작 완료"
fi

# 브라우저 캐시 초기화 (선택적)
log_step "브라우저 캐시 정리 중..."

read -p "브라우저 캐시도 초기화하시겠습니까? (y/n): " clear_browser_cache
if [[ $clear_browser_cache == "y" ]]; then
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
            if [[ -d "$path" ]]; then
                rm -rf "$path"/* 2>/dev/null || true
                log_info "$browser 캐시 초기화 완료"
            fi
        done
    done
else
    log_info "브라우저 캐시 초기화를 건너뜁니다"
fi

# 백업 파일 정리
log_step "백업 파일 정리 중..."

# 앱 백업 파일 제거
APP_BACKUP_PATTERN="/Applications/FocusTimer.app.backup.*"
if ls $APP_BACKUP_PATTERN 1> /dev/null 2>&1; then
    log_warn "앱 백업 파일들이 발견되었습니다"
    read -p "백업 파일도 함께 제거하시겠습니까? (y/n): " remove_backups
    if [[ $remove_backups == "y" ]]; then
        rm -rf $APP_BACKUP_PATTERN
        log_info "앱 백업 파일 제거 완료"
    else
        log_info "백업 파일을 유지합니다"
    fi
else
    log_info "앱 백업 파일이 없습니다"
fi

# LaunchAgent 백업 파일 제거
LAUNCH_BACKUP_PATTERN="/Library/LaunchAgents/com.focustimer.helper.plist.backup.*"
if ls $LAUNCH_BACKUP_PATTERN 1> /dev/null 2>&1; then
    rm -f $LAUNCH_BACKUP_PATTERN
    log_info "LaunchAgent 백업 파일 제거 완료"
fi

# 제거 완료 메시지
echo
echo -e "${GREEN}🎉 $PRODUCT_NAME v$CURRENT_VERSION 완전 제거가 완료되었습니다!${NC}"
echo
echo -e "${BLUE}📋 제거된 구성 요소:${NC}"
echo "  ✅ 시스템 서비스 (LaunchAgent)"
echo "  ✅ 애플리케이션 파일 (FocusTimer.app)"
echo "  ✅ CLI 도구 (focus-timer)"
echo "  ✅ hosts 파일 복구"
echo "  ✅ DNS 캐시 초기화"
echo "  ✅ 브라우저 캐시 초기화 (선택적)"
echo "  ✅ 백업 파일 정리"
echo
echo -e "${YELLOW}⚠️ 수동 확인 필요:${NC}"
echo "  🌐 브라우저 확장 프로그램 (Chrome 확장 프로그램 관리에서 제거)"
echo "  🔧 시스템 환경 변수 (필요한 경우)"
echo
echo -e "${BLUE}🔄 시스템 재시작을 권장합니다.${NC}"
echo -e "${BLUE}📞 기술 지원: support@focustimer.com${NC}"
echo