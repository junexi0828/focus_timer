#!/bin/bash

# FocusTimer 업데이트 스크립트
# 기존 설치를 안전하게 업데이트

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

# 관리자 권한 확인
check_admin() {
    if [[ $EUID -ne 0 ]]; then
        log_error "관리자 권한이 필요합니다: sudo $0"
        exit 1
    fi
}

# 기존 설치 확인
check_existing_installation() {
    log_step "기존 설치 확인 중..."

    APP_PATH="/Applications/FocusTimer.app"

    if [[ ! -d "$APP_PATH" ]]; then
        log_error "FocusTimer.app이 설치되지 않았습니다."
        log_info "새 설치를 위해 install_focustimer_app.sh를 실행해주세요."
        exit 1
    fi

    # 기존 버전 확인
    local existing_version=""
    if [[ -f "$APP_PATH/Contents/Info.plist" ]]; then
        existing_version=$(defaults read "$APP_PATH/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "unknown")
    else
        existing_version="unknown"
    fi

    log_info "기존 버전: $existing_version"
    log_info "업데이트 버전: $CURRENT_VERSION"

    if [[ "$existing_version" == "$CURRENT_VERSION" ]]; then
        log_info "이미 최신 버전($CURRENT_VERSION)이 설치되어 있습니다."
        exit 0
    fi

    log_info "업데이트를 진행합니다: $existing_version → $CURRENT_VERSION"
}

# 서비스 중지
stop_services() {
    log_step "기존 서비스 중지 중..."

    # LaunchAgent 중지
    local launch_agent="/Library/LaunchAgents/com.focustimer.helper.plist"
    if [[ -f "$launch_agent" ]]; then
        launchctl unload "$launch_agent" 2>/dev/null || true
        log_info "백그라운드 서비스 중지 완료"
    fi
}

# 백업 생성
create_backup() {
    log_step "기존 설치 백업 중..."

    APP_PATH="/Applications/FocusTimer.app"
    BACKUP_PATH="/Applications/FocusTimer.app.backup.$(date +%Y%m%d_%H%M%S)"

    cp -R "$APP_PATH" "$BACKUP_PATH"

    if [[ -d "$BACKUP_PATH" ]]; then
        log_info "백업 완료: $BACKUP_PATH"
    else
        log_error "백업 생성에 실패했습니다."
        exit 1
    fi
}

# 업데이트 실행
perform_update() {
    log_step "업데이트 실행 중..."

    # 기존 앱 제거
    rm -rf "/Applications/FocusTimer.app"

    # 새 앱 설치 (기존 설치 스크립트 재사용)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    "$SCRIPT_DIR/install_focustimer_app.sh"
}

# 서비스 재시작
restart_services() {
    log_step "서비스 재시작 중..."

    local launch_agent="/Library/LaunchAgents/com.focustimer.helper.plist"
    if [[ -f "$launch_agent" ]]; then
        launchctl load "$launch_agent"
        log_info "백그라운드 서비스 재시작 완료"
    fi
}

# 업데이트 완료 메시지
show_update_completion() {
    log_step "업데이트 완료!"
    echo
    echo -e "${GREEN}🎉 FocusTimer 업데이트가 완료되었습니다!${NC}"
    echo -e "${BLUE}📦 새 버전: $CURRENT_VERSION${NC}"
    echo
    echo -e "${BLUE}📱 사용 방법:${NC}"
    echo "  • GUI 앱: Applications 폴더에서 FocusTimer 실행"
    echo "  • CLI 도구: 터미널에서 'focus-timer --help' 실행"
    echo
    echo -e "${YELLOW}💾 백업 정보:${NC}"
    echo "  • 백업 위치: /Applications/FocusTimer.app.backup.*"
    echo "  • 문제 발생 시 백업에서 복구할 수 있습니다"
    echo
}

# 메인 업데이트 함수
main() {
    echo -e "${BLUE}🔄 FocusTimer 업데이트 시작${NC}"
    echo

    check_admin
    check_existing_installation
    stop_services
    create_backup
    perform_update
    restart_services
    show_update_completion
}

# 스크립트 실행
main "$@"