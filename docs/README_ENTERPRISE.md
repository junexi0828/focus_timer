# 🔒 Focus Timer Enterprise v2.0.0

**Enterprise-grade Focus Mode System**
*상업용 출시 수준의 강력한 집중 모드 시스템*

---

## 🏢 **기업용 솔루션**

Focus Timer Enterprise는 학교,기업 환경에서 학생, 직원들의 생산성 향상과 디지털 웰빙을 위한 **집중 모드 시스템**입니다.

### ✨ **주요 특징**

- **🔐 시스템 레벨 보호**: hosts 파일 잠금 + 방화벽 규칙
- **🔄 지속적 모니터링**: 실시간 파일 변경 감지 및 자동 복구
- **🛡️ 다중 차단 레이어**: hosts + 방화벽 + 브라우저 확장
- **🌐 웹 관리 인터페이스**: 직관적인 관리자 패널
- **📊 상세한 로깅**: 모든 활동의 추적 및 분석
- **🚀 자동 시작**: 시스템 부팅 시 자동 실행

---

## 🏗️ **시스템 아키텍처**

```
┌─────────────────────────────────────────────────────────────┐
│                    Focus Timer Enterprise                   │
├─────────────────────────────────────────────────────────────┤
│  🌐 웹 관리 인터페이스 (Flask)                              │
│  📊 실시간 모니터링 & 로깅                                  │
│  🔧 시스템 서비스 (LaunchDaemon)                           │
├─────────────────────────────────────────────────────────────┤
│  🛡️ 다중 차단 레이어                                        │
│  ├── hosts 파일 차단                                        │
│  ├── 방화벽 규칙 (pfctl)                                    │
│  ├── 브라우저 확장 프로그램                                  │
│  └── DNS 캐시 제어                                          │
├─────────────────────────────────────────────────────────────┤
│  🔄 지속적 모니터링                                         │
│  ├── 파일 시스템 감시 (watchdog)                            │
│  ├── 자동 복구 시스템                                       │
│  └── 보안 강화 메커니즘                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 **설치 및 배포**

### **시스템 요구사항**

- **OS**: macOS 10.15 (Catalina) 이상
- **Python**: 3.7 이상
- **권한**: 관리자 권한 필요
- **메모리**: 최소 512MB RAM
- **저장공간**: 최소 100MB

### **1. 기본 설치**

```bash
# 저장소 클론
git clone https://github.com/focustimer/enterprise.git
cd enterprise

# 실행 권한 부여
chmod +x install_enterprise.sh
chmod +x uninstall_enterprise.sh

# 관리자 권한으로 설치
sudo ./install_enterprise.sh
```

### **2. 설치 옵션**

설치 과정에서 다음 옵션들을 선택할 수 있습니다:

- **🌐 브라우저 확장 프로그램**: Chrome 확장 프로그램 자동 설치
- **🌐 웹 관리 인터페이스**: Flask 기반 웹 관리 패널 설치

---

## 🎯 **주요 기능**

### **1. 시스템 레벨 보호**

#### **hosts 파일 잠금**
```bash
# 집중 모드 활성화 시
sudo chmod 444 /etc/hosts  # 읽기 전용으로 잠금

# 집중 모드 비활성화 시
sudo chmod 644 /etc/hosts  # 쓰기 권한 복구
```

#### **방화벽 규칙**
```bash
# pfctl을 사용한 네트워크 레벨 차단
block drop out proto tcp to youtube.com port 80
block drop out proto tcp to youtube.com port 443
```

### **2. 지속적 모니터링**

#### **파일 시스템 감시**
- hosts 파일 변경 실시간 감지
- 자동 차단 재적용
- 우회 시도 로깅

#### **자동 복구 시스템**
```python
def handle_hosts_modification(self):
    """hosts 파일 수정 처리"""
    if state.is_focus_mode and state.is_blocked:
        logger.log("WARNING", "집중 모드 중 hosts 파일 수정 시도 감지")
        state.bypass_attempts += 1

        # 자동으로 차단 재적용
        self.reapply_blocking()

        # 보안 강화
        self.enhance_security()
```

### **3. 다중 차단 레이어**

#### **Layer 1: hosts 파일**
```
127.0.0.1 youtube.com
127.0.0.1 www.youtube.com
127.0.0.1 m.youtube.com
```

#### **Layer 2: 방화벽**
```
block drop out proto tcp to youtube.com port 80
block drop out proto tcp to youtube.com port 443
```

#### **Layer 3: 브라우저 확장**
```javascript
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    return {cancel: true};
  },
  {urls: ["*://*.youtube.com/*"]},
  ["blocking"]
);
```

### **4. 웹 관리 인터페이스**

#### **실시간 모니터링**
- 집중 모드 상태 실시간 확인
- 차단 횟수 및 우회 시도 통계
- 시스템 로그 실시간 조회

#### **원격 관리**
- 웹 브라우저를 통한 원격 제어
- RESTful API 제공
- JSON 기반 데이터 교환

---

## 🔧 **관리 및 운영**

### **시스템 서비스 관리**

```bash
# 서비스 시작
sudo launchctl start com.focustimer.enterprise

# 서비스 중지
sudo launchctl stop com.focustimer.enterprise

# 서비스 상태 확인
sudo launchctl list | grep focustimer

# 서비스 재시작
sudo launchctl unload /Library/LaunchDaemons/com.focustimer.enterprise.plist
sudo launchctl load /Library/LaunchDaemons/com.focustimer.enterprise.plist
```

### **로그 관리**

```bash
# 실시간 로그 모니터링
tail -f /var/log/FocusTimer/focus_timer.log

# 오류 로그 확인
tail -f /var/log/FocusTimer/focus_timer_error.log

# 로그 파일 크기 확인
ls -lh /var/log/FocusTimer/
```

### **웹 관리 인터페이스**

```bash
# 웹 서비스 시작
sudo launchctl start com.focustimer.web

# 웹 서비스 중지
sudo launchctl stop com.focustimer.web

# 웹 인터페이스 접속
open http://localhost:8080
```

---

## 📊 **모니터링 및 분석**

### **상태 파일 구조**

```json
{
  "is_focus_mode": true,
  "focus_start_time": "2024-01-15T09:00:00",
  "focus_end_time": "2024-01-15T18:00:00",
  "is_blocked": true,
  "block_count": 15,
  "bypass_attempts": 3,
  "difficulty_level": 2,
  "failed_attempts": 1,
  "last_check": "2024-01-15T14:30:00"
}
```

### **로그 분석**

```bash
# 집중 모드 활성화 횟수
grep "집중 모드 시작" /var/log/FocusTimer/focus_timer.log | wc -l

# 우회 시도 횟수
grep "우회 시도" /var/log/FocusTimer/focus_timer.log | wc -l

# 오류 발생 횟수
grep "ERROR" /var/log/FocusTimer/focus_timer.log | wc -l
```

---

## 🔒 **보안 기능**

### **1. 프로세스 보호**
- 락 파일을 통한 중복 실행 방지
- 시그널 핸들러를 통한 안전한 종료 처리
- 상태 파일을 통한 설정 지속성

### **2. 파일 시스템 보호**
- hosts 파일 권한 제어
- 실시간 파일 변경 감지
- 자동 복구 메커니즘

### **3. 네트워크 보호**
- 방화벽 규칙을 통한 네트워크 레벨 차단
- DNS 캐시 제어
- 브라우저 레벨 차단

### **4. 우회 방지**
- 다중 레이어 차단으로 우회 난이도 증가
- 실시간 모니터링으로 즉시 감지
- 자동 보안 강화 메커니즘

---

## 🛠️ **문제 해결**

### **일반적인 문제**

#### **1. 서비스가 시작되지 않음**
```bash
# 로그 확인
tail -f /var/log/FocusTimer/focus_timer_error.log

# 권한 확인
ls -la /Applications/FocusTimer/
ls -la /Library/LaunchDaemons/com.focustimer.enterprise.plist

# 수동 실행 테스트
sudo python3 /Applications/FocusTimer/focus_timer_enterprise.py
```

#### **2. 웹 인터페이스 접속 불가**
```bash
# 웹 서비스 상태 확인
sudo launchctl list | grep focustimer.web

# 포트 확인
lsof -i :8080

# Flask 앱 수동 실행
cd /Applications/FocusTimer/web
sudo python3 app.py
```

#### **3. 차단이 작동하지 않음**
```bash
# hosts 파일 확인
cat /etc/hosts | grep FocusTimer

# 방화벽 상태 확인
sudo pfctl -s rules

# DNS 캐시 초기화
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### **고급 문제 해결**

#### **완전 재설치**
```bash
# 기존 설치 제거
sudo ./uninstall_enterprise.sh

# 시스템 재시작
sudo reboot

# 새로 설치
sudo ./install_enterprise.sh
```

---

## 📈 **성능 최적화**

### **리소스 사용량**

- **CPU**: 평균 0.1-0.5% (모니터링 모드)
- **메모리**: 약 50-100MB
- **디스크**: 로그 파일당 최대 10MB
- **네트워크**: 최소한의 트래픽

### **최적화 팁**

1. **로그 로테이션 설정**
```bash
# logrotate 설정 추가
sudo nano /etc/logrotate.d/focustimer
```

2. **모니터링 간격 조정**
```bash
# plist 파일에서 ThrottleInterval 수정
sudo nano /Library/LaunchDaemons/com.focustimer.enterprise.plist
```

---

## 🔄 **업데이트 및 유지보수**

### **버전 업데이트**

```bash
# 백업 생성
sudo cp -r /Applications/FocusTimer /Applications/FocusTimer.backup

# 새 버전 설치
sudo ./install_enterprise.sh

# 설정 마이그레이션
sudo cp /Applications/FocusTimer.backup/state.json /Library/Application\ Support/FocusTimer/
```

### **정기 유지보수**

```bash
# 로그 파일 정리
sudo find /var/log/FocusTimer -name "*.log" -mtime +30 -delete

# 캐시 정리
sudo rm -rf /tmp/focus_timer_*

# 상태 파일 백업
sudo cp /Library/Application\ Support/FocusTimer/state.json /backup/
```

---

## 📞 **지원 및 문의**

### **기술 지원**

- **이메일**: support@focustimer.com
- **전화**: +1-555-0123
- **온라인**: https://support.focustimer.com
- **문서**: https://docs.focustimer.com

### **라이센스 문의**

- **이메일**: licensing@focustimer.com
- **전화**: +1-555-0124
- **온라인**: https://focustimer.com/licensing

### **기업 문의**

- **이메일**: enterprise@focustimer.com
- **전화**: +1-555-0125
- **온라인**: https://focustimer.com/enterprise

---

## 📄 **라이센스**

이 소프트웨어는 상업용 라이센스 하에 제공됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

**© 2024 FocusTimer Inc. All rights reserved.**

*Focus Timer Enterprise - Empowering Productivity Through Technology*