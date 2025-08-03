#!/bin/bash

# FocusTimer App 구조 설치 스크립트
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

# 버전 정보
CURRENT_VERSION="2.0.0"
MINIMUM_SYSTEM_VERSION="10.15"

# 버전 비교 함수
compare_versions() {
    local version1=$1
    local version2=$2

    # 버전을 점으로 분리
    IFS='.' read -ra v1 <<< "$version1"
    IFS='.' read -ra v2 <<< "$version2"

    # 각 부분을 비교
    for i in "${!v1[@]}"; do
        if [[ ${v1[$i]} -gt ${v2[$i]} ]]; then
            return 1  # version1이 더 큼
        elif [[ ${v1[$i]} -lt ${v2[$i]} ]]; then
            return 2  # version2가 더 큼
        fi
    done

    return 0  # 동일
}

# 버전 확인 함수
check_version() {
    local version=$1
    local min_version=$2

    compare_versions "$version" "$min_version"
    local result=$?

    if [[ $result -eq 2 ]]; then
        return 1  # 버전이 낮음
    fi
    return 0  # 버전이 충분함
}

# 업데이트 확인 함수
check_for_updates() {
    log_step "업데이트 확인 중..."

    # 원격 버전 확인 (향후 확장 가능)
    local remote_version=""
    local update_url="https://api.github.com/repos/your-repo/focus-timer/releases/latest"

    if command -v curl &> /dev/null; then
        remote_version=$(curl -s "$update_url" | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//' 2>/dev/null || echo "")
    fi

    if [[ -n "$remote_version" ]]; then
        compare_versions "$remote_version" "$CURRENT_VERSION"
        local result=$?

        if [[ $result -eq 1 ]]; then
            log_info "새로운 버전이 사용 가능합니다: $remote_version"
            read -p "업데이트를 진행하시겠습니까? (y/n): " update_confirm
            if [[ $update_confirm == "y" ]]; then
                log_info "업데이트를 진행합니다..."
                return 0
            else
                log_info "업데이트를 건너뜁니다."
                return 1
            fi
        else
            log_info "이미 최신 버전입니다: $CURRENT_VERSION"
        fi
    else
        log_warn "원격 버전 확인에 실패했습니다. 로컬 설치를 진행합니다."
    fi

    return 0
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

    # macOS 버전 확인
    local macos_version=$(sw_vers -productVersion)
    log_info "macOS 버전: $macos_version"

    if ! check_version "$macos_version" "$MINIMUM_SYSTEM_VERSION"; then
        log_error "macOS $MINIMUM_SYSTEM_VERSION 이상이 필요합니다. 현재 버전: $macos_version"
        exit 1
    fi

    # Python 3.13 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되지 않았습니다."
        exit 1
    fi

    # Python 버전 확인
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python 버전: $python_version"

    if ! check_version "$python_version" "3.13"; then
        log_error "Python 3.13 이상이 필요합니다. 현재 버전: $python_version"
        exit 1
    fi

    # Homebrew 확인
    if ! command -v brew &> /dev/null; then
        log_warn "Homebrew가 설치되지 않았습니다. 설치를 권장합니다."
    fi

    # curl 확인 (업데이트 확인용)
    if ! command -v curl &> /dev/null; then
        log_warn "curl이 설치되지 않았습니다. 업데이트 확인 기능이 제한됩니다."
    fi

    log_info "시스템 요구사항 확인 완료"
}

# 앱 내부 가상환경 설정
setup_virtual_environment() {
    log_step "앱 내부 가상환경 설정 중..."

    # 앱 내부 가상환경 경로 설정
    APP_VENV_PATH="/Applications/FocusTimer.app/Contents/MacOS/venv"

    # 기존 외부 가상환경 경로 (백업용)
    EXTERNAL_VENV_PATH="$SCRIPT_DIR/../focus_timer_env"

    # 앱 내부 가상환경 생성
    if [[ ! -d "$APP_VENV_PATH" ]]; then
        log_info "앱 내부 가상환경 생성 중: $APP_VENV_PATH"
        python3 -m venv "$APP_VENV_PATH"
    else
        log_info "기존 앱 내부 가상환경 발견: $APP_VENV_PATH"
    fi

    # 앱 내부 가상환경 활성화
    source "$APP_VENV_PATH/bin/activate"

    # 필수 패키지 설치
    log_info "필수 패키지 설치 중..."
    pip install --upgrade pip
    pip install watchdog==6.0.0 psutil==6.1.0

    # 선택적 패키지 설치
    read -p "웹 인터페이스를 설치하시겠습니까? (y/n): " install_web
    if [[ $install_web == "y" ]]; then
        pip install flask requests
    fi

    log_info "앱 내부 가상환경 설정 완료"
    log_info "가상환경 위치: $APP_VENV_PATH"
}

# 앱 구조 생성
create_app_structure() {
    log_step "FocusTimer.app 구조 생성 중..."

    APP_PATH="/Applications/FocusTimer.app"
    BACKUP_PATH="/Applications/FocusTimer.app.backup.$(date +%Y%m%d_%H%M%S)"

    # 기존 앱 버전 확인 및 업데이트 처리
    if [[ -d "$APP_PATH" ]]; then
        log_warn "기존 FocusTimer.app이 발견되었습니다."

        # 기존 버전 확인
        local existing_version=""
        if [[ -f "$APP_PATH/Contents/Info.plist" ]]; then
            existing_version=$(defaults read "$APP_PATH/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "unknown")
        else
            existing_version="unknown"
        fi

        log_info "기존 버전: $existing_version"
        log_info "설치할 버전: $CURRENT_VERSION"

        # 버전 비교
        if [[ "$existing_version" != "unknown" ]]; then
            compare_versions "$CURRENT_VERSION" "$existing_version"
            local version_result=$?

            if [[ $version_result -eq 0 ]]; then
                log_info "이미 동일한 버전($CURRENT_VERSION)이 설치되어 있습니다."
                read -p "재설치를 진행하시겠습니까? (y/n): " reinstall_confirm
                if [[ $reinstall_confirm != "y" ]]; then
                    log_info "설치가 취소되었습니다."
                    exit 0
                fi
            elif [[ $version_result -eq 2 ]]; then
                log_warn "기존 버전($existing_version)이 새 버전($CURRENT_VERSION)보다 높습니다."
                read -p "다운그레이드를 진행하시겠습니까? (y/n): " downgrade_confirm
                if [[ $downgrade_confirm != "y" ]]; then
                    log_info "설치가 취소되었습니다."
                    exit 0
                fi
            else
                log_info "업데이트를 진행합니다: $existing_version → $CURRENT_VERSION"
            fi
        fi

        # 사용자 확인
        read -p "기존 앱을 백업하고 새로 설치하시겠습니까? (y/n): " confirm_backup
        if [[ $confirm_backup != "y" ]]; then
            log_error "설치가 취소되었습니다."
            exit 1
        fi

        # 백업 생성
        log_info "기존 앱을 백업 중: $BACKUP_PATH"
        cp -R "$APP_PATH" "$BACKUP_PATH"

        # 백업 성공 확인
        if [[ -d "$BACKUP_PATH" ]]; then
            log_info "백업 완료: $BACKUP_PATH"
        else
            log_error "백업 생성에 실패했습니다."
            exit 1
        fi

        # 기존 앱 제거
        log_info "기존 앱 제거 중..."
        rm -rf "$APP_PATH"

        # 제거 확인
        if [[ -d "$APP_PATH" ]]; then
            log_error "기존 앱 제거에 실패했습니다."
            exit 1
        fi
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
    "description": "App 구조 집중 모드 시스템"
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
    # 앱 내부 가상환경 경로 설정
    APP_VENV_PATH="/Applications/FocusTimer.app/Contents/MacOS/venv"

    cat > "/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.helper</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_VENV_PATH/bin/python</string>
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
    if [[ ! -d "/var/log/FocusTimer" ]]; then
        mkdir -p "/var/log/FocusTimer"
        chmod 755 "/var/log/FocusTimer"
        log_info "로그 디렉토리 생성 완료"
    else
        log_info "로그 디렉토리가 이미 존재합니다"
    fi

    # 설정 디렉토리
    if [[ ! -d "/Library/Application Support/FocusTimer" ]]; then
        mkdir -p "/Library/Application Support/FocusTimer"
        chmod 755 "/Library/Application Support/FocusTimer"
        log_info "설정 디렉토리 생성 완료"
    else
        log_info "설정 디렉토리가 이미 존재합니다"

        # 기존 설정 파일 백업 확인
        if [[ -f "/Library/Application Support/FocusTimer/state.json" ]]; then
            log_info "기존 상태 파일이 발견되었습니다. 백업을 생성합니다."
            cp "/Library/Application Support/FocusTimer/state.json" "/Library/Application Support/FocusTimer/state.json.backup.$(date +%Y%m%d_%H%M%S)"
        fi
    fi

    # 백업 디렉토리
    if [[ ! -d "/Library/Application Support/FocusTimer/hosts_backup" ]]; then
        mkdir -p "/Library/Application Support/FocusTimer/hosts_backup"
        chmod 755 "/Library/Application Support/FocusTimer/hosts_backup"
        log_info "백업 디렉토리 생성 완료"
    else
        log_info "백업 디렉토리가 이미 존재합니다"
    fi

    log_info "시스템 디렉토리 생성 완료"
}

# LaunchAgent 설치
install_launch_agent() {
    log_step "LaunchAgent 설치 중..."

    LAUNCH_AGENT_PATH="/Library/LaunchAgents/com.focustimer.helper.plist"
    LAUNCH_AGENT_BACKUP="/Library/LaunchAgents/com.focustimer.helper.plist.backup.$(date +%Y%m%d_%H%M%S)"

    # 기존 LaunchAgent 백업 및 제거
    if [[ -f "$LAUNCH_AGENT_PATH" ]]; then
        log_info "기존 LaunchAgent 백업 중..."
        cp "$LAUNCH_AGENT_PATH" "$LAUNCH_AGENT_BACKUP"

        # 백업 성공 확인
        if [[ -f "$LAUNCH_AGENT_BACKUP" ]]; then
            log_info "LaunchAgent 백업 완료: $LAUNCH_AGENT_BACKUP"
        else
            log_error "LaunchAgent 백업에 실패했습니다."
            exit 1
        fi

        # 기존 서비스 중지
        log_info "기존 서비스 중지 중..."
        launchctl unload "$LAUNCH_AGENT_PATH" 2>/dev/null || true

        # 기존 파일 제거
        rm -f "$LAUNCH_AGENT_PATH"
    fi

    # 새로운 LaunchAgent 복사
    if [[ -f "/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" ]]; then
        cp "/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist" "$LAUNCH_AGENT_PATH"
        chmod 644 "$LAUNCH_AGENT_PATH"

        # 복사 성공 확인
        if [[ -f "$LAUNCH_AGENT_PATH" ]]; then
            log_info "LaunchAgent 파일 복사 완료"
        else
            log_error "LaunchAgent 파일 복사에 실패했습니다."
            exit 1
        fi
    else
        log_error "LaunchAgent 설정 파일을 찾을 수 없습니다."
        exit 1
    fi

    # LaunchAgent 로드
    log_info "LaunchAgent 로드 중..."
    if launchctl load "$LAUNCH_AGENT_PATH"; then
        log_info "LaunchAgent 설치 완료"
    else
        log_error "LaunchAgent 로드에 실패했습니다."
        exit 1
    fi
}

# CLI 도구 심볼릭 링크 생성
install_cli_tool() {
    log_step "CLI 도구 설치 중..."

    CLI_LINK="/usr/local/bin/focus-timer"
    CLI_BACKUP="/usr/local/bin/focus-timer.backup.$(date +%Y%m%d_%H%M%S)"

    # 기존 CLI 도구 백업 및 제거
    if [[ -L "$CLI_LINK" ]] || [[ -f "$CLI_LINK" ]]; then
        log_info "기존 CLI 도구 백업 중..."

        if [[ -L "$CLI_LINK" ]]; then
            # 심볼릭 링크인 경우
            cp -P "$CLI_LINK" "$CLI_BACKUP" 2>/dev/null || true
        else
            # 일반 파일인 경우
            cp "$CLI_LINK" "$CLI_BACKUP" 2>/dev/null || true
        fi

        # 백업 성공 확인
        if [[ -f "$CLI_BACKUP" ]]; then
            log_info "CLI 도구 백업 완료: $CLI_BACKUP"
        fi

        # 기존 링크/파일 제거
        rm -f "$CLI_LINK"
    fi

    # 새로운 심볼릭 링크 생성
    if [[ -f "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI" ]]; then
        ln -sf "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI" "$CLI_LINK"
        chmod +x "$CLI_LINK"

        # 링크 생성 확인
        if [[ -L "$CLI_LINK" ]]; then
            log_info "CLI 도구 설치 완료"
        else
            log_error "CLI 도구 링크 생성에 실패했습니다."
            exit 1
        fi
    else
        log_error "CLI 도구 파일을 찾을 수 없습니다."
        exit 1
    fi
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
    echo -e "${GREEN}🎉 FocusTimer App 구조 설치가 완료되었습니다!${NC}"
    echo -e "${BLUE}📦 버전: $CURRENT_VERSION${NC}"
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
    echo "  • 서비스 상태: sudo launchctl list | grep focustimer"
    echo "  • 로그 확인: tail -f /var/log/FocusTimer/focus_timer.log"
    echo "  • 헬퍼 로그: tail -f /var/log/FocusTimer/helper.log"
    echo "  • 버전 확인: defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString"
    echo "  • CLI 도구: focus-timer --help"
    echo "  • GUI 앱 실행: open /Applications/FocusTimer.app"
    echo "  • 설정 파일: sudo nano /Applications/FocusTimer.app/Contents/Resources/config.json"
    echo "  • 업데이트 확인: curl -s https://api.github.com/repos/your-repo/focus-timer/releases/latest | grep tag_name"
    echo "  • 업데이트 실행: sudo ./installers/update_focustimer_app.sh"
    echo "  • 완전 제거: sudo ./installers/uninstall_focustimer_app.sh"
    echo
    echo -e "${YELLOW}💾 백업 정보:${NC}"
    echo "  • 앱 백업: /Applications/FocusTimer.app.backup.*"
    echo "  • LaunchAgent 백업: /Library/LaunchAgents/com.focustimer.helper.plist.backup.*"
    echo "  • CLI 도구 백업: /usr/local/bin/focus-timer.backup.*"
    echo "  • 상태 파일 백업: /Library/Application Support/FocusTimer/state.json.backup.*"
    echo
    echo -e "${YELLOW}⚠️  주의사항:${NC}"
    echo "  • 관리자 권한으로 실행해야 합니다"
    echo "  • 시스템 보안 설정에서 앱 실행을 허용해야 할 수 있습니다"
    echo "  • 문제 발생 시 백업 파일을 사용하여 복구할 수 있습니다"
    echo "  • 자동 업데이트 확인 기능이 포함되어 있습니다"
    echo
}

# 메인 설치 함수
main() {
    echo -e "${BLUE}🚀 FocusTimer App 구조 설치 시작${NC}"
    echo

    check_admin
    check_requirements
    check_for_updates
    validate_source_files
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

# 설치 전 검증
validate_source_files() {
    log_step "소스 파일 검증 중..."

    local missing_files=()
    local required_files=(
        "FocusTimer.app/Contents/MacOS/FocusTimer"
        "FocusTimer.app/Contents/MacOS/FocusTimerCLI"
        "FocusTimer.app/Contents/MacOS/FocusTimerHelper"
        "FocusTimer.app/Contents/Resources/config.json"
        "FocusTimer.app/Contents/Info.plist"
        "FocusTimer.app/Contents/Resources/com.focustimer.helper.plist"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "다음 필수 파일들이 누락되었습니다:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        log_error "모든 필수 파일이 있는지 확인하고 다시 실행해주세요."
        exit 1
    fi

    log_info "소스 파일 검증 완료"
}

# 스크립트 실행
main "$@"
