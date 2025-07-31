# FocusTimer.app 관리 명령어 가이드

이 문서는 FocusTimer.app의 관리 및 유지보수를 위한 명령어들을 제공합니다.

## 📋 목차
- [기본 관리](#-기본-관리)
- [서비스 관리](#-서비스-관리)
- [로그 관리](#-로그-관리)
- [설정 관리](#-설정-관리)
- [버전 관리](#-버전-관리)
- [문제 해결](#-문제-해결)
- [백업 및 복구](#-백업-및-복구)

---

## 🚀 기본 관리

### 앱 실행
```bash
# GUI 앱 실행
open /Applications/FocusTimer.app

# CLI 도구 실행
focus-timer --help

# CLI 도구 직접 실행
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI --help
```

### 앱 정보 확인
```bash
# 버전 확인
defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString

# 앱 번들 정보 확인
defaults read /Applications/FocusTimer.app/Contents/Info.plist

# 앱 크기 확인
du -sh /Applications/FocusTimer.app

# 앱 권한 확인
ls -la /Applications/FocusTimer.app
```

---

## 🔧 서비스 관리

### 서비스 상태 확인
```bash
# 모든 서비스 목록에서 FocusTimer 확인
sudo launchctl list | grep focustimer

# 특정 서비스 상태 확인
sudo launchctl list com.focustimer.helper

# 서비스 파일 확인
ls -la /Library/LaunchAgents/com.focustimer.helper.plist
```

### 서비스 시작/중지
```bash
# 서비스 시작
sudo launchctl load /Library/LaunchAgents/com.focustimer.helper.plist

# 서비스 중지
sudo launchctl unload /Library/LaunchAgents/com.focustimer.helper.plist

# 서비스 재시작
sudo launchctl unload /Library/LaunchAgents/com.focustimer.helper.plist
sudo launchctl load /Library/LaunchAgents/com.focustimer.helper.plist
```

### 서비스 강제 종료
```bash
# 프로세스 ID 확인
ps aux | grep FocusTimer

# 프로세스 강제 종료
sudo pkill -f FocusTimer
sudo pkill -f FocusTimerHelper
```

---

## 📊 로그 관리

### 실시간 로그 모니터링
```bash
# 메인 로그 실시간 확인
tail -f /var/log/FocusTimer/focus_timer.log

# 헬퍼 서비스 로그 실시간 확인
tail -f /var/log/FocusTimer/helper.log

# 오류 로그 확인
tail -f /var/log/FocusTimer/helper_error.log

# 모든 로그 파일 확인
ls -la /var/log/FocusTimer/
```

### 로그 파일 관리
```bash
# 로그 파일 크기 확인
du -sh /var/log/FocusTimer/*

# 로그 파일 내용 확인 (최근 50줄)
tail -50 /var/log/FocusTimer/focus_timer.log

# 로그 파일 검색
grep "ERROR" /var/log/FocusTimer/focus_timer.log
grep "WARN" /var/log/FocusTimer/focus_timer.log

# 로그 파일 정리 (30일 이상 된 로그 삭제)
find /var/log/FocusTimer/ -name "*.log" -mtime +30 -delete
```

### 시스템 로그 확인
```bash
# Console 앱에서 로그 확인
log show --predicate 'process == "FocusTimer"' --last 1h

# 시스템 로그에서 FocusTimer 관련 이벤트 확인
log show --predicate 'subsystem == "com.focustimer"' --last 1d
```

---

## ⚙️ 설정 관리

### 설정 파일 편집
```bash
# 설정 파일 확인
cat /Applications/FocusTimer.app/Contents/Resources/config.json

# 설정 파일 편집 (nano)
sudo nano /Applications/FocusTimer.app/Contents/Resources/config.json

# 설정 파일 편집 (vim)
sudo vim /Applications/FocusTimer.app/Contents/Resources/config.json

# 설정 파일 백업
sudo cp /Applications/FocusTimer.app/Contents/Resources/config.json /Applications/FocusTimer.app/Contents/Resources/config.json.backup
```

### 설정 유효성 검사
```bash
# JSON 형식 검증
python3 -m json.tool /Applications/FocusTimer.app/Contents/Resources/config.json

# 설정 파일 권한 확인
ls -la /Applications/FocusTimer.app/Contents/Resources/config.json
```

### 상태 파일 관리
```bash
# 상태 파일 확인
cat "/Library/Application Support/FocusTimer/state.json"

# 상태 파일 백업
cp "/Library/Application Support/FocusTimer/state.json" "/Library/Application Support/FocusTimer/state.json.backup"

# 상태 파일 초기화
rm "/Library/Application Support/FocusTimer/state.json"
```

---

## 🔄 버전 관리

### 현재 버전 확인
```bash
# 앱 버전 확인
defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString

# 빌드 버전 확인
defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleVersion

# Python 스크립트 버전 확인
grep "VERSION" /Applications/FocusTimer.app/Contents/MacOS/FocusTimer
```

### 업데이트 관리
```bash
# 원격 최신 버전 확인
curl -s https://api.github.com/repos/your-repo/focus-timer/releases/latest | grep tag_name

# 업데이트 스크립트 실행
sudo ./installers/update_focustimer_app.sh

# 업데이트 확인 (자동)
curl -s https://api.github.com/repos/your-repo/focus-timer/releases/latest | python3 -c "
import sys, json
data = json.load(sys.stdin)
latest = data['tag_name'].replace('v', '')
current = '2.0.0'
print(f'Current: {current}, Latest: {latest}')
if latest > current:
    print('Update available!')
else:
    print('Already up to date.')
"
```

### 버전 비교
```bash
# 로컬 버전과 원격 버전 비교
LOCAL_VERSION=$(defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString)
REMOTE_VERSION=$(curl -s https://api.github.com/repos/your-repo/focus-timer/releases/latest | grep tag_name | cut -d'"' -f4 | sed 's/v//')
echo "Local: $LOCAL_VERSION, Remote: $REMOTE_VERSION"
```

---

## 🔍 문제 해결

### 권한 문제 해결
```bash
# hosts 파일 권한 확인
ls -la /etc/hosts

# hosts 파일 권한 수정
sudo chmod 644 /etc/hosts
sudo chown root:wheel /etc/hosts

# 앱 권한 수정
sudo chown -R root:wheel /Applications/FocusTimer.app
sudo chmod -R 755 /Applications/FocusTimer.app
```

### 네트워크 문제 해결
```bash
# DNS 캐시 초기화
sudo dscacheutil -flushcache

# 네트워크 설정 확인
netstat -rn | grep default

# hosts 파일 내용 확인
cat /etc/hosts | grep -i focus
```

### 프로세스 문제 해결
```bash
# 관련 프로세스 확인
ps aux | grep -i focus

# 포트 사용 확인
lsof -i :8080  # 웹 인터페이스 포트

# 메모리 사용량 확인
top -pid $(pgrep -f FocusTimer)
```

### 파일 시스템 문제 해결
```bash
# 디스크 공간 확인
df -h /Applications

# 파일 무결성 확인
md5 /Applications/FocusTimer.app/Contents/MacOS/FocusTimer

# 손상된 파일 확인
find /Applications/FocusTimer.app -type f -exec file {} \;
```

---

## 💾 백업 및 복구

### 자동 백업 확인
```bash
# 백업 파일 목록 확인
ls -la /Applications/FocusTimer.app.backup.*
ls -la /Library/LaunchAgents/com.focustimer.helper.plist.backup.*
ls -la /usr/local/bin/focus-timer.backup.*

# 백업 파일 크기 확인
du -sh /Applications/FocusTimer.app.backup.*
```

### 수동 백업 생성
```bash
# 전체 앱 백업
sudo cp -R /Applications/FocusTimer.app /Applications/FocusTimer.app.backup.$(date +%Y%m%d_%H%M%S)

# 설정 파일 백업
sudo cp /Applications/FocusTimer.app/Contents/Resources/config.json /Applications/FocusTimer.app/Contents/Resources/config.json.backup.$(date +%Y%m%d_%H%M%S)

# 상태 파일 백업
cp "/Library/Application Support/FocusTimer/state.json" "/Library/Application Support/FocusTimer/state.json.backup.$(date +%Y%m%d_%H%M%S)"
```

### 복구 작업
```bash
# 앱 복구 (최신 백업에서)
sudo cp -R /Applications/FocusTimer.app.backup.* /Applications/FocusTimer.app

# 설정 파일 복구
sudo cp /Applications/FocusTimer.app/Contents/Resources/config.json.backup.* /Applications/FocusTimer.app/Contents/Resources/config.json

# 상태 파일 복구
cp "/Library/Application Support/FocusTimer/state.json.backup.*" "/Library/Application Support/FocusTimer/state.json"
```

### 백업 정리
```bash
# 30일 이상 된 백업 삭제
find /Applications -name "FocusTimer.app.backup.*" -mtime +30 -exec rm -rf {} \;
find /Library/LaunchAgents -name "com.focustimer.helper.plist.backup.*" -mtime +30 -delete
find /usr/local/bin -name "focus-timer.backup.*" -mtime +30 -delete
```

---

## 🛠️ 고급 관리

### 성능 모니터링
```bash
# CPU 사용량 모니터링
top -pid $(pgrep -f FocusTimer) -l 1

# 메모리 사용량 확인
ps -o pid,ppid,%cpu,%mem,command -p $(pgrep -f FocusTimer)

# 디스크 I/O 모니터링
sudo iostat 1 5
```

### 보안 검사
```bash
# 파일 권한 검사
find /Applications/FocusTimer.app -type f -exec ls -la {} \;

# 실행 파일 검사
file /Applications/FocusTimer.app/Contents/MacOS/*

# 코드 서명 확인
codesign -dv /Applications/FocusTimer.app
```

### 개발자 도구
```bash
# 디버그 모드 실행
sudo FOCUSTIMER_DEBUG=1 /Applications/FocusTimer.app/Contents/MacOS/FocusTimer

# 상세 로깅 활성화
sudo /Applications/FocusTimer.app/Contents/MacOS/FocusTimer --verbose

# 프로파일링
sudo /Applications/FocusTimer.app/Contents/MacOS/FocusTimer --profile
```

---

## 📞 지원 및 문의

문제가 발생했을 때 다음 정보를 수집하여 지원팀에 문의하세요:

```bash
# 시스템 정보 수집
echo "=== 시스템 정보 ==="
sw_vers
echo "=== Python 버전 ==="
python3 --version
echo "=== 앱 버전 ==="
defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString
echo "=== 서비스 상태 ==="
sudo launchctl list | grep focustimer
echo "=== 최근 로그 ==="
tail -20 /var/log/FocusTimer/focus_timer.log
echo "=== 디스크 공간 ==="
df -h /Applications
```

---

**💡 팁**: 자주 사용하는 명령어는 별칭(alias)으로 설정하여 편리하게 사용할 수 있습니다.

```bash
# ~/.zshrc 또는 ~/.bash_profile에 추가
alias focustimer='open /Applications/FocusTimer.app'
alias focus-cli='focus-timer'
alias focus-logs='tail -f /var/log/FocusTimer/focus_timer.log'
alias focus-status='sudo launchctl list | grep focustimer'
alias focus-version='defaults read /Applications/FocusTimer.app/Contents/Info.plist CFBundleShortVersionString'
```