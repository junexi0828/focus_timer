#!/bin/bash

# FocusTimer Hybrid 구조 설치 스크립트
# 최적화된 .app 패키징 및 배포

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

# 관리자 권한 확인
check_admin() {
    if [[ $EUID -ne 0 ]]; then
        log_error "관리자 권한이 필요합니다: sudo $0"
        exit 1
    fi
}

# 시스템 요구사항 확인
check_requirements() {
    log_step "시스템 요구사항 확인 중..."

    # macOS 확인
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "macOS에서만 실행 가능합니다."
        exit 1
    fi

    # Python 3.13 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되지 않았습니다."
        exit 1
    fi

    # Homebrew 확인
    if ! command -v brew &> /dev/null; then
        log_warn "Homebrew가 설치되지 않았습니다. 설치를 권장합니다."
    fi

    log_info "시스템 요구사항 확인 완료"
}

# 가상환경 설정
setup_virtual_environment() {
    log_step "Python 가상환경 설정 중..."

    VENV_PATH="/Users/juns/focus_timer/focus_timer_env"

    if [[ ! -d "$VENV_PATH" ]]; then
        log_info "가상환경 생성 중..."
        python3 -m venv "$VENV_PATH"
    fi

    # 가상환경 활성화
    source "$VENV_PATH/bin/activate"

    # 필수 패키지 설치
    log_info "필수 패키지 설치 중..."
    pip install --upgrade pip
    pip install watchdog psutil

    # 선택적 패키지 설치
    read -p "웹 인터페이스를 설치하시겠습니까? (y/n): " install_web
    if [[ $install_web == "y" ]]; then
        pip install flask requests
    fi

    log_info "가상환경 설정 완료"
}

# 앱 구조 생성
create_app_structure() {
    log_step "FocusTimer.app 구조 생성 중..."

    APP_PATH="/Applications/FocusTimer.app"

    # 기존 앱 제거
    if [[ -d "$APP_PATH" ]]; then
        log_info "기존 앱 제거 중..."
        rm -rf "$APP_PATH"
    fi

    # 앱 구조 생성
    mkdir -p "$APP_PATH/Contents/MacOS"
    mkdir -p "$APP_PATH/Contents/Resources"
    mkdir -p "$APP_PATH/Contents/Frameworks"

    log_info "앱 구조 생성 완료"
}

# 실행 파일 설치
install_executables() {
    log_step "실행 파일 설치 중..."

    # 메인 GUI 앱 복사
    if [[ -f "FocusTimer.app/Contents/MacOS/FocusTimer" ]]; then
        cp "FocusTimer.app/Contents/MacOS/FocusTimer" "/Applications/FocusTimer.app/Contents/MacOS/"
        chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimer"
        log_info "메인 GUI 앱 설치 완료"
    else
        log_error "메인 GUI 앱 파일을 찾을 수 없습니다."
        exit 1
    fi

    # CLI 도구 복사
    if [[ -f "FocusTimer.app/Contents/MacOS/FocusTimerCLI" ]]; then
        cp "FocusTimer.app/Contents/MacOS/FocusTimerCLI" "/Applications/FocusTimer.app/Contents/MacOS/"
        chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI"
        log_info "CLI 도구 설치 완료"
    fi

    # 백그라운드 헬퍼 복사
    if [[ -f "FocusTimer.app/Contents/MacOS/FocusTimerHelper" ]]; then
        cp "FocusTimer.app/Contents/MacOS/FocusTimerHelper" "/Applications/FocusTimer.app/Contents/MacOS/"
        chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerHelper"
        log_info "백그라운드 헬퍼 설치 완료"
    fi

    log_info "실행 파일 설치 완료"
}

# 리소스 파일 설치
install_resources() {
    log_step "리소스 파일 설치 중..."

    # 설정 파일 복사
    if [[ -f "FocusTimer.app/Contents/Resources/config.json" ]]; then
        cp "FocusTimer.app/Contents/Resources/config.json" "/Applications/FocusTimer.app/Contents/Resources/"
        log_info "설정 파일 설치 완료"
    else
        log_warn "설정 파일을 찾을 수 없습니다. 기본 설정을 생성합니다."
        create_default_config
    fi

    # Info.plist 복사
    if [[ -f "FocusTimer.app/Contents/Info.plist" ]]; then
        cp "FocusTimer.app/Contents/Info.plist" "/Applications/FocusTimer.app/Contents/"
        log_info "Info.plist 설치 완료"
    else
        log_warn "Info.plist를 찾을 수 없습니다. 기본 파일을 생성합니다."
        create_default_info_plist
    fi

    # LaunchAgent 설정 파일 복사
    if [[ -f "FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" ]]; then
        cp "FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" "/Applications/FocusTimer.app/Contents/Resources/"
        log_info "LaunchAgent 설정 파일 설치 완료"
    else
        log_warn "LaunchAgent 설정 파일을 찾을 수 없습니다. 기본 파일을 생성합니다."
        create_default_launch_agent
    fi

    log_info "리소스 파일 설치 완료"
}

# 기본 설정 파일 생성
create_default_config() {
    cat > "/Applications/FocusTimer.app/Contents/Resources/config.json" << 'EOF'
{
  "app_info": {
    "name": "FocusTimer",
    "version": "2.0.0",
    "description": "Hybrid 구조 집중 모드 시스템"
  },
  "system_paths": {
    "hosts_file": "/etc/hosts",
    "redirect_ip": "127.0.0.1",
    "backup_path": "/Library/Application Support/FocusTimer/hosts_backup",
    "lock_file": "/Library/Application Support/FocusTimer/focus_timer.lock",
    "log_path": "/var/log/FocusTimer/focus_timer.log",
    "pid_file": "/var/run/focus_timer.pid"
  },
  "focus_mode": {
    "default_start_time": "09:00",
    "default_end_time": "18:00",
    "default_difficulty": 1,
    "max_difficulty": 5,
    "max_attempts": 3,
    "auto_restart_browser": true,
    "force_browser_restart": true
  },
  "security": {
    "enable_system_protection": true,
    "enable_file_monitoring": true,
    "enable_firewall_rules": false,
    "enable_dns_cache_flush": true,
    "enable_browser_cache_clear": true,
    "lock_hosts_file": true,
    "monitor_hosts_changes": true,
    "enable_auto_recovery": true
  },
  "gui_settings": {
    "window_size": {
      "width": 900,
      "height": 700
    },
    "theme": "clam",
    "auto_refresh_interval": 5,
    "log_lines_to_show": 20,
    "enable_notifications": true
  }
}
EOF
}

# 기본 Info.plist 생성
create_default_info_plist() {
    cat > "/Applications/FocusTimer.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FocusTimer</string>
    <key>CFBundleIdentifier</key>
    <string>com.focustimer.app</string>
    <key>CFBundleName</key>
    <string>FocusTimer</string>
    <key>CFBundleDisplayName</key>
    <string>FocusTimer</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
</dict>
</plist>
EOF
}

# 기본 LaunchAgent 생성
create_default_launch_agent() {
    cat > "/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.helper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/juns/focus_timer/focus_timer_env/bin/python</string>
        <string>/Applications/FocusTimer.app/Contents/MacOS/FocusTimerHelper</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/FocusTimer/helper.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/FocusTimer/helper_error.log</string>
    <key>WorkingDirectory</key>
    <string>/Applications/FocusTimer.app/Contents/MacOS</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>ProcessType</key>
    <string>Background</string>
    <key>ThrottleInterval</key>
    <integer>60</integer>
    <key>ExitTimeOut</key>
    <integer>10</integer>
</dict>
</plist>
EOF
}

# 시스템 디렉토리 생성
create_system_directories() {
    log_step "시스템 디렉토리 생성 중..."

    # 로그 디렉토리
    mkdir -p "/var/log/FocusTimer"
    chmod 755 "/var/log/FocusTimer"

    # 설정 디렉토리
    mkdir -p "/Library/Application Support/FocusTimer"
    chmod 755 "/Library/Application Support/FocusTimer"

    # 백업 디렉토리
    mkdir -p "/Library/Application Support/FocusTimer/hosts_backup"
    chmod 755 "/Library/Application Support/FocusTimer/hosts_backup"

    log_info "시스템 디렉토리 생성 완료"
}

# LaunchAgent 설치
install_launch_agent() {
    log_step "LaunchAgent 설치 중..."

    LAUNCH_AGENT_PATH="/Library/LaunchAgents/com.focustimer.helper.plist"

    # 기존 LaunchAgent 제거
    if [[ -f "$LAUNCH_AGENT_PATH" ]]; then
        log_info "기존 LaunchAgent 제거 중..."
        launchctl unload "$LAUNCH_AGENT_PATH" 2>/dev/null || true
        rm -f "$LAUNCH_AGENT_PATH"
    fi

    # 새로운 LaunchAgent 복사
    cp "/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" "$LAUNCH_AGENT_PATH"
    chmod 644 "$LAUNCH_AGENT_PATH"

    # LaunchAgent 로드
    launchctl load "$LAUNCH_AGENT_PATH"
    log_info "LaunchAgent 설치 완료"
}

# CLI 도구 심볼릭 링크 생성
install_cli_tool() {
    log_step "CLI 도구 설치 중..."

    CLI_LINK="/usr/local/bin/focus-timer"

    # 기존 링크 제거
    if [[ -L "$CLI_LINK" ]]; then
        rm -f "$CLI_LINK"
    fi

    # 새로운 심볼릭 링크 생성
    ln -sf "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI" "$CLI_LINK"
    chmod +x "$CLI_LINK"

    log_info "CLI 도구 설치 완료"
}

# 권한 설정
set_permissions() {
    log_step "권한 설정 중..."

    # 앱 디렉토리 권한
    chmod -R 755 "/Applications/FocusTimer.app"
    chown -R root:wheel "/Applications/FocusTimer.app"

    # 실행 파일 권한
    chmod +x "/Applications/FocusTimer.app/Contents/MacOS/"*

    log_info "권한 설정 완료"
}

# 설치 완료 메시지
show_completion_message() {
    log_step "설치 완료!"
    echo
    echo -e "${GREEN}🎉 FocusTimer Hybrid 구조 설치가 완료되었습니다!${NC}"
    echo
    echo -e "${BLUE}📱 사용 방법:${NC}"
    echo "  • GUI 앱: Applications 폴더에서 FocusTimer 실행"
    echo "  • CLI 도구: 터미널에서 'focus-timer --help' 실행"
    echo "  • 백그라운드 서비스: 자동으로 시작됩니다"
    echo
    echo -e "${BLUE}📁 설치 위치:${NC}"
    echo "  • 앱: /Applications/FocusTimer.app"
    echo "  • 설정: /Applications/FocusTimer.app/Contents/Resources/config.json"
    echo "  • 로그: /var/log/FocusTimer/"
    echo "  • 상태: /Library/Application Support/FocusTimer/"
    echo
    echo -e "${BLUE}🔧 관리 명령어:${NC}"
    echo "  • 서비스 시작: sudo launchctl load /Library/LaunchAgents/com.focustimer.helper.plist"
    echo "  • 서비스 중지: sudo launchctl unload /Library/LaunchAgents/com.focustimer.helper.plist"
    echo "  • 로그 확인: tail -f /var/log/FocusTimer/focus_timer.log"
    echo
    echo -e "${YELLOW}⚠️  주의사항:${NC}"
    echo "  • 관리자 권한으로 실행해야 합니다"
    echo "  • 시스템 보안 설정에서 앱 실행을 허용해야 할 수 있습니다"
    echo
}

# 메인 설치 함수
main() {
    echo -e "${BLUE}🚀 FocusTimer Hybrid 구조 설치 시작${NC}"
    echo

    check_admin
    check_requirements
    setup_virtual_environment
    create_app_structure
    install_executables
    install_resources
    create_system_directories
    install_launch_agent
    install_cli_tool
    set_permissions
    show_completion_message
}

# 스크립트 실행
main "$@"
