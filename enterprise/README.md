# Focus Timer - Enterprise CLI Edition

## 🏢 기업용 CLI 집중 모드 시스템

시스템 레벨 보호와 지속적 모니터링을 제공하는 기업용 CLI 버전입니다.

## 🚀 빠른 시작

```bash
# 설정 도구 실행
sudo python3 setup_enterprise.py

# 메인 프로그램 실행
sudo python3 focus_timer_enterprise.py
```

## 📋 주요 기능

- ✅ 시스템 레벨 보호
- ✅ 지속적 파일 모니터링
- ✅ 다중 차단 레이어
- ✅ 알고리즘 문제 시스템
- ✅ 실시간 로깅
- ✅ 상태 지속성 관리

## ⚙️ 설정

### 설정 도구 사용
```bash
sudo python3 setup_enterprise.py
```

### 설정 옵션
- 집중 모드 활성화/비활성화
- 시작/종료 시간 설정
- 알고리즘 문제 난이도
- 브라우저 강제 재시작
- 웹 관리 인터페이스

## 🔧 시스템 서비스

### 서비스 등록
```bash
# LaunchDaemon으로 등록
sudo launchctl load /Library/LaunchDaemons/com.focustimer.enterprise.plist
```

### 서비스 관리
```bash
# 서비스 시작
sudo launchctl start com.focustimer.enterprise

# 서비스 중지
sudo launchctl stop com.focustimer.enterprise

# 서비스 상태 확인
sudo launchctl list | grep focustimer
```

## 📁 파일 구조

```
enterprise/
├── focus_timer_enterprise.py  # 메인 프로그램
├── setup_enterprise.py        # 설정 도구
└── README.md                  # 이 파일
```

## 🔒 보안 기능

### 시스템 레벨 보호
- hosts 파일 권한 관리
- 파일 시스템 모니터링
- 자동 차단 재적용

### 다중 차단 레이어
- hosts 파일 차단
- DNS 캐시 초기화
- 브라우저 캐시 초기화

### 지속적 모니터링
- hosts 파일 변경 감지
- 자동 보안 강화
- 브라우저 강제 재시작

## 📊 로깅

### 로그 위치
```
/var/log/FocusTimer/focus_timer.log
```

### 로그 확인
```bash
# 실시간 로그 확인
tail -f /var/log/FocusTimer/focus_timer.log

# 최근 로그 확인
tail -20 /var/log/FocusTimer/focus_timer.log
```

## 🎯 사용 시나리오

### 1. 기업 환경 설정
```bash
# 설정 도구로 초기 설정
sudo python3 setup_enterprise.py

# 시스템 서비스로 등록
sudo launchctl load /Library/LaunchDaemons/com.focustimer.enterprise.plist
```

### 2. 일상적인 사용
```bash
# 서비스 상태 확인
sudo launchctl list | grep focustimer

# 로그 확인
tail -f /var/log/FocusTimer/focus_timer.log
```

### 3. 문제 해결
```bash
# 서비스 재시작
sudo launchctl stop com.focustimer.enterprise
sudo launchctl start com.focustimer.enterprise

# 로그 분석
grep "ERROR" /var/log/FocusTimer/focus_timer.log
```

## ⚠️ 주의사항

1. **관리자 권한 필요**: 시스템 레벨 작업을 위해 sudo 권한이 필요합니다.
2. **시스템 서비스**: LaunchDaemon으로 등록되어 백그라운드에서 실행됩니다.
3. **파일 모니터링**: hosts 파일 변경을 실시간으로 감지합니다.
4. **자동 복구**: 차단 해제 시도 시 자동으로 차단을 재적용합니다.

## 🔄 설정 파일 연동

이 버전은 `../config/config.json` 파일과 연동됩니다:

```json
{
  "system_paths": {
    "hosts_file": "/etc/hosts",
    "state_path": "/Library/Application Support/FocusTimer/state.json",
    "log_path": "/var/log/FocusTimer/focus_timer.log"
  },
  "security": {
    "enable_system_protection": true,
    "enable_file_monitoring": true
  }
}
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 파일**: `/var/log/FocusTimer/focus_timer.log`
2. **서비스 상태**: `sudo launchctl list | grep focustimer`
3. **설정 파일**: `../config/config.json`
4. **권한 확인**: `ls -la /etc/hosts`