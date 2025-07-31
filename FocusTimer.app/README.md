# FocusTimer.app - macOS 네이티브 앱

<div align="center">

![FocusTimer.app](https://img.shields.io/badge/FocusTimer.app-Native%20macOS%20App-blue?style=for-the-badge&logo=apple)
![Python](https://img.shields.io/badge/Python-3.13+-green?style=for-the-badge&logo=python)
![macOS](https://img.shields.io/badge/macOS-10.15+-orange?style=for-the-badge&logo=apple)
![License](https://img.shields.io/badge/License-Commercial-red?style=for-the-badge)

**macOS 네이티브 앱으로 구현된 통합 집중 모드 시스템**

[📖 상세 문서](#-상세-기능) • [🚀 설치 가이드](#-설치-가이드) • [⚙️ 설정 관리](#-설정-관리) • [🔧 문제 해결](#-문제-해결)

</div>

---

## 🎯 제품 개요

FocusTimer.app은 macOS 네이티브 앱 번들(.app) 형태로 구현된 통합 집중 모드 시스템입니다. GUI, CLI, 백그라운드 서비스를 하나의 앱에 통합하여 사용자에게 최적의 경험을 제공합니다.

### ✨ 주요 특징
- 🍎 **macOS 네이티브 앱** - 시스템과 완벽 통합
- 🖥️ **통합 GUI 인터페이스** - 직관적인 사용자 경험
- 💻 **CLI 명령줄 도구** - 고급 사용자를 위한 터미널 제어
- 🔄 **백그라운드 서비스** - 지속적인 모니터링 및 보호
- ⚙️ **중앙화된 설정 관리** - JSON 기반 설정 시스템
- 🛡️ **시스템 레벨 보호** - hosts 파일 권한 관리

---

## 📱 앱 구조

```
FocusTimer.app/
├── Contents/
│   ├── Info.plist                    # 앱 번들 정보
│   ├── MacOS/
│   │   ├── FocusTimer               # 메인 GUI 애플리케이션
│   │   ├── FocusTimerCLI            # 명령줄 인터페이스
│   │   └── FocusTimerHelper         # 백그라운드 서비스
│   └── Resources/
│       ├── config.json              # 앱 설정 파일
│       └── com.focustimer.helper.plist  # LaunchAgent 설정
```

### 🔧 구성 요소

#### 1. **FocusTimer (메인 GUI)**
- **역할**: 메인 그래픽 사용자 인터페이스
- **기능**:
  - 실시간 상태 모니터링
  - 집중 모드 제어 (시작/중지)
  - 설정 관리 및 편집
  - 통계 대시보드
  - 로그 뷰어
  - 알고리즘 문제 시스템

#### 2. **FocusTimerCLI (명령줄 도구)**
- **역할**: 터미널 기반 제어 도구
- **기능**:
  - 집중 모드 시작/중지
  - 즉시 차단/해제
  - 상태 확인
  - 설정 변경
  - 도움말 및 사용법

#### 3. **FocusTimerHelper (백그라운드 서비스)**
- **역할**: 시스템 레벨 백그라운드 서비스
- **기능**:
  - 지속적인 모니터링
  - 자동 시간 체크
  - 파일 변경 감지
  - 자동 복구 시스템
  - Enterprise 로직 연동

---

## 🚀 설치 가이드

### 📋 시스템 요구사항
- **OS**: macOS 10.15 (Catalina) 이상
- **Python**: 3.13 이상
- **권한**: 관리자 권한 (sudo)
- **패키지**: watchdog, psutil

### 🔧 설치 방법

#### 1. **자동 설치 (권장)**
```bash
# 설치 스크립트 실행
sudo ./installers/install_focustimer_app.sh
```

#### 2. **수동 설치**
```bash
# 1. 앱을 Applications 폴더로 복사
sudo cp -R FocusTimer.app /Applications/

# 2. 권한 설정
sudo chown -R root:wheel /Applications/FocusTimer.app
sudo chmod -R 755 /Applications/FocusTimer.app

# 3. Python 가상환경 생성
python3 -m venv /Applications/FocusTimer.app/../focus_timer_env

# 4. 필수 패키지 설치
source /Applications/FocusTimer.app/../focus_timer_env/bin/activate
pip install watchdog psutil

# 5. LaunchAgent 등록
sudo cp /Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.focustimer.helper.plist
```

### 🗑️ 제거 방법
```bash
# 제거 스크립트 실행
sudo ./installers/uninstall_focustimer_app.sh
```

---

## 🎮 사용 방법

### 🖥️ GUI 모드
```bash
# GUI 앱 실행
open /Applications/FocusTimer.app
```

**주요 기능:**
- **상태 패널**: 현재 집중 모드 상태 확인
- **제어 패널**: 집중 모드 시작/중지, 즉시 차단/해제
- **설정 탭**: 시간, 난이도, 보안 옵션 설정
- **통계 탭**: 차단 횟수, 우회 시도, 난이도 통계
- **로그 탭**: 실시간 시스템 이벤트 확인

### 💻 CLI 모드
```bash
# CLI 도구 실행
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI

# 사용 가능한 명령어
focus-timer start [--start-time TIME] [--end-time TIME] [--difficulty LEVEL]
focus-timer stop
focus-timer block
focus-timer unblock
focus-timer status
focus-timer help
```

### 🔄 백그라운드 서비스
```bash
# 서비스 상태 확인
launchctl list | grep focustimer

# 서비스 수동 시작/중지
launchctl start com.focustimer.helper
launchctl stop com.focustimer.helper
```

---

## ⚙️ 설정 관리

### 📝 설정 파일 구조
```json
{
    "app_info": {
        "name": "FocusTimer",
        "version": "2.0.0",
        "description": "hybrid 구조 통합 집중 모드 시스템"
    },
    "system_paths": {
        "hosts_file": "/etc/hosts",
        "redirect_ip": "127.0.0.1",
        "backup_path": "/Library/Application Support/FocusTimer/hosts_backup",
        "lock_file": "/Library/Application Support/FocusTimer/focus_timer.lock",
        "log_path": "/var/log/FocusTimer/focus_timer.log",
        "pid_file": "/var/run/focus_timer.pid"
    },
    "blocked_websites": {
        "youtube": [...],
        "social_media": [...],
        "gaming": [...],
        "entertainment": [...]
    },
    "focus_mode": {
        "default_start_time": "09:00",
        "default_end_time": "18:00",
        "default_difficulty": 1,
        "max_difficulty": 5,
        "max_attempts": 3
    },
    "security": {
        "enable_system_protection": true,
        "enable_file_monitoring": true,
        "enable_dns_cache_flush": true,
        "enable_browser_cache_clear": true,
        "lock_hosts_file": true,
        "monitor_hosts_changes": true,
        "enable_auto_recovery": true
    }
}
```

### 🎛️ 설정 편집 방법

#### 1. **GUI 설정 편집기**
```bash
# 설정 GUI 실행
python3 config/config_gui.py
```

#### 2. **직접 편집**
```bash
# 설정 파일 편집
sudo nano /Applications/FocusTimer.app/Contents/Resources/config.json
```

#### 3. **CLI 설정**
```bash
# CLI를 통한 설정 변경
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI start --start-time 08:30 --end-time 17:30 --difficulty 3
```

---

## 🔧 문제 해결

### 📋 일반적인 문제들

#### 1. **권한 오류**
```bash
# 권한 확인
ls -la /etc/hosts
sudo chmod 644 /etc/hosts

# 앱 권한 확인
ls -la /Applications/FocusTimer.app
```

#### 2. **서비스 시작 실패**
```bash
# 서비스 상태 확인
launchctl list | grep focustimer

# 로그 확인
tail -f /var/log/FocusTimer/helper.log

# 서비스 재시작
launchctl unload ~/Library/LaunchAgents/com.focustimer.helper.plist
launchctl load ~/Library/LaunchAgents/com.focustimer.helper.plist
```

#### 3. **Python 경로 문제**
```bash
# Python 경로 확인
which python3
/Applications/FocusTimer.app/../focus_timer_env/bin/python --version

# 가상환경 재생성
rm -rf /Applications/FocusTimer.app/../focus_timer_env
python3 -m venv /Applications/FocusTimer.app/../focus_timer_env
source /Applications/FocusTimer.app/../focus_timer_env/bin/activate
pip install watchdog psutil
```

#### 4. **설정 파일 오류**
```bash
# 설정 파일 유효성 검사
python3 -m json.tool /Applications/FocusTimer.app/Contents/Resources/config.json

# 백업에서 복원
sudo cp /Applications/FocusTimer.app/Contents/Resources/config.json.backup /Applications/FocusTimer.app/Contents/Resources/config.json
```

### 📊 로그 확인
```bash
# 메인 로그
tail -f /var/log/FocusTimer/focus_timer.log

# 헬퍼 서비스 로그
tail -f /var/log/FocusTimer/helper.log

# 시스템 로그
log show --predicate 'process == "FocusTimer"' --last 1h
```

### 🔍 디버깅 모드
```bash
# 디버그 모드로 실행
sudo /Applications/FocusTimer.app/Contents/MacOS/FocusTimer --debug

# 상세 로깅 활성화
export FOCUSTIMER_DEBUG=1
sudo /Applications/FocusTimer.app/Contents/MacOS/FocusTimer
```

---

## 📊 기능 비교

| 기능 | FocusTimer.app | Personal | Enterprise CLI | Enterprise GUI | Enterprise Web |
|------|----------------|----------|----------------|----------------|----------------|
| **macOS 네이티브 앱** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **통합 GUI/CLI/서비스** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **시스템 서비스** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **설정 관리** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **로그 시스템** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **다중 차단 레이어** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **파일 모니터링** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **자동 복구** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **알고리즘 문제** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **웹 인터페이스** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔄 업데이트

### 📦 자동 업데이트
```bash
# 업데이트 확인
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI update

# 자동 업데이트 활성화
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI update --auto
```

### 🔧 수동 업데이트
```bash
# 1. 기존 앱 백업
sudo cp -R /Applications/FocusTimer.app /Applications/FocusTimer.app.backup

# 2. 새 버전 설치
sudo cp -R FocusTimer.app /Applications/

# 3. 권한 설정
sudo chown -R root:wheel /Applications/FocusTimer.app
sudo chmod -R 755 /Applications/FocusTimer.app

# 4. 서비스 재시작
launchctl unload ~/Library/LaunchAgents/com.focustimer.helper.plist
launchctl load ~/Library/LaunchAgents/com.focustimer.helper.plist
```

---

## 📞 지원 및 문의

### 📧 연락처
- **개발자**: juns
- **이메일**: junexi0828@gmail.com
- **GitHub**: [Focus Timer Repository](https://github.com/your-repo/focus-timer)

### 📚 관련 문서
- **[메인 README](../README.md)** - 전체 제품 라인업
- **[Personal Edition](../personal/README.md)** - 개인용 버전
- **[Enterprise CLI Edition](../enterprise/README.md)** - 기업용 CLI 버전
- **[Enterprise GUI Edition](../enterprise_gui/README.md)** - 기업용 GUI 버전
- **[Enterprise Web Edition](../enterprise_web/README.md)** - 기업용 웹 버전
- **[설정 관리](../config/README.md)** - 설정 관리 시스템

### 🐛 버그 리포트
문제가 발생했을 때 다음 정보를 포함하여 리포트해주세요:
1. **macOS 버전**: `sw_vers`
2. **Python 버전**: `python3 --version`
3. **앱 버전**: `/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI --version`
4. **오류 로그**: `/var/log/FocusTimer/focus_timer.log`
5. **시스템 로그**: `log show --predicate 'process == "FocusTimer"' --last 1h`

---

<div align="center">

**💡 FocusTimer.app은 macOS 사용자를 위한 최적화된 집중 모드 시스템입니다.**

![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

</div>