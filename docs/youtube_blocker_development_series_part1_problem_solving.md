# 🚫 스크린타임 한계를 넘어선 완벽한 YouTube 차단 프로그램 개발기 (Part 1 문제 해결편)

## 📋 목차
- [문제 정의](#-문제-정의)
- [DNS 캐시의 3단계 구조](#dns-캐시의-3단계-구조)
- [시도한 해결책들](#-시도한-해결책들)
- [핵심 과제 분석](#-핵심-과제-분석)
- [가능한 해결 방향들](#-가능한-해결-방향들)
- [최종 해결책](#-최종-해결책)
- [결론 및 교훈](#-결론-및-교훈)

---

## 🎯 문제 정의

YouTube 차단 프로그램을 개발하면서 가장 큰 기술적 도전은 **브라우저 DNS 캐시 초기화**였습니다. 단순히 `/etc/hosts` 파일을 수정하는 것만으로는 완벽한 차단 효과를 얻을 수 없었고, 브라우저가 이미 캐시된 DNS 정보를 사용하여 YouTube에 접근하는 문제가 발생했습니다.

### **핵심 문제**
> **브라우저가 이미 캐시된 DNS 정보를 사용하여 hosts 파일 차단을 우회하는 현상**

---

## 🔍 DNS 캐시의 3단계 구조

브라우저의 DNS 캐시는 3단계로 구성되어 있으며, 각 단계별로 초기화 방법과 효과가 다릅니다:

```
1. 브라우저 메모리 DNS 캐시 (가장 강력) ← 핵심 문제!
   ├── 위치: 브라우저 프로세스 메모리 내부
   ├── 특성: 프로세스가 살아있는 한 유지됨
   └── 영향: hosts 파일 차단을 무시하고 기존 IP 사용

2. 브라우저 파일 캐시 (중간)
   ├── 위치: 브라우저 캐시 디렉토리
   ├── 특성: 파일 시스템에 저장됨
   └── 영향: 브라우저 재시작 시 초기화됨

3. 시스템 DNS 캐시 (가장 약함)
   ├── 위치: macOS DNS 캐시 시스템
   ├── 특성: 시스템 레벨에서 관리됨
   └── 영향: dscacheutil 명령어로 쉽게 초기화
```

### **문제의 핵심**
브라우저 메모리 DNS 캐시가 가장 강력하고 지속적이어서, 이 부분을 초기화하지 않으면 hosts 파일 차단이 무효화됩니다.

---

## 🛠️ 시도한 해결책들

### **1. AppleScript UI 조작 방식**

#### **시도한 방법**
```python
def force_browser_cache_clear():
    """실행 중인 브라우저의 캐시만 초기화 (브라우저 종료 없이)"""
    try:
        running_browsers = get_running_browsers()

        for browser in running_browsers:
            try:
                # 브라우저에 캐시 초기화 신호 전송
                if browser == "Google Chrome":
                    # Chrome 개발자 도구를 통한 캐시 초기화
                    os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                    time.sleep(0.5)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"i\" using {command down, option down}' 2>/dev/null")
                    time.sleep(1)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"r\" using {command down, shift down}' 2>/dev/null")

                elif browser == "Safari":
                    # Safari 개발자 도구를 통한 캐시 초기화
                    os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                    time.sleep(0.5)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"r\" using {command down, option down}' 2>/dev/null")

                else:
                    # 다른 브라우저는 강제 새로고침
                    os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                    time.sleep(0.5)
                    os.system(f"osascript -e 'tell application \"System Events\" to key code 124 using {{command down, shift down}}' 2>/dev/null")

                print(f"✅ {browser} 캐시 초기화 완료")

            except Exception as e:
                print(f"⚠️ {browser} 캐시 초기화 중 오류: {e}")

    except Exception as e:
        print(f"⚠️ 브라우저 캐시 초기화 중 오류: {e}")
```

#### **문제점**
- ❌ **사이드바/툴바가 있으면 AppleScript 실패**: 브라우저 UI 상태에 따라 불안정
- ❌ **브라우저별 콘솔 단축키가 다름**: Chrome, Safari, Firefox마다 다른 단축키
- ❌ **UI 상태에 따라 불안정**: 개발자 도구가 이미 열려있거나 다른 상태일 때 실패

#### **실패 원인 분석**
```python
# AppleScript의 한계
# 1. UI 요소의 정확한 위치 파악 어려움
# 2. 브라우저별 다른 UI 구조
# 3. 사용자 설정에 따른 UI 변화
```

### **2. 강제 새로고침 방식**

#### **시도한 방법**
```python
def force_browser_refresh():
    """실행 중인 브라우저에만 강제 새로고침 신호 전송"""
    try:
        running_browsers = get_running_browsers()

        for browser in running_browsers:
            try:
                # 브라우저 활성화
                os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                time.sleep(1)  # 브라우저 활성화 대기

                # 올바른 새로고침 단축키 사용 (Cmd+R) - key code 15 사용
                os.system("osascript -e 'tell application \"System Events\" to key code 15 using {command down}' 2>/dev/null")

                print(f"✅ {browser} 새로고침 완료")

            except Exception as e:
                print(f"⚠️ {browser} 새로고침 중 오류: {e}")

        print("✅ 브라우저 새로고침 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 새로고침 중 오류: {e}")
```

#### **문제점**
- ❌ **브라우저 메모리 DNS 캐시는 여전히 유지**: 새로고침만으로는 메모리 캐시 초기화 불가
- ❌ **이미 연결된 브라우저에서는 차단 효과 없음**: 기존 연결은 그대로 유지

#### **실패 원인 분석**
```python
# 새로고침의 한계
# 1. 페이지 콘텐츠만 새로고침
# 2. DNS 캐시는 프로세스 메모리에 유지
# 3. 기존 네트워크 연결은 그대로 유지
```

### **3. 캐시 파일 삭제 방식**

#### **시도한 방법**
```python
def clear_browser_cache():
    """실행 중인 브라우저의 캐시만 자동으로 초기화"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🧹 브라우저 캐시 초기화 중... ({', '.join(running_browsers)})")

        # Chrome 캐시 초기화
        if "Google Chrome" in running_browsers:
            chrome_paths = [
                os.path.expanduser("~/Library/Caches/Google/Chrome/Default/Cache"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cache"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Code Cache"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/GPUCache")
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    os.system(f"rm -rf {path}/*")

        # Safari 캐시 초기화
        if "Safari" in running_browsers:
            safari_paths = [
                os.path.expanduser("~/Library/Caches/com.apple.Safari"),
                os.path.expanduser("~/Library/Safari/LocalStorage"),
                os.path.expanduser("~/Library/Safari/WebpageIcons.db")
            ]
            for path in safari_paths:
                if os.path.exists(path):
                    os.system(f"rm -rf {path}/*")

        # 시스템 DNS 캐시 초기화
        os.system("sudo dscacheutil -flushcache")
        os.system("sudo killall -HUP mDNSResponder")

        print("✅ 브라우저 캐시 초기화 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 캐시 초기화 중 오류: {e}")
```

#### **문제점**
- ❌ **브라우저 메모리 DNS 캐시는 그대로 유지**: 파일 캐시만 삭제됨
- ❌ **하드코딩된 경로로 개인별 설치 위치 대응 불가**: 사용자별 다른 설치 경로

#### **실패 원인 분석**
```python
# 파일 캐시 삭제의 한계
# 1. 메모리 DNS 캐시는 파일과 별개
# 2. 브라우저가 실행 중이면 메모리 캐시 유지
# 3. 경로가 브라우저 버전별로 다를 수 있음
```

### **4. 프로세스 시그널 방식**

#### **시도한 방법**
```python
def force_browser_restart_with_signal():
    """프로세스 시그널을 통한 브라우저 재시작"""
    try:
        running_browsers = get_running_browsers()

        for browser in running_browsers:
            try:
                # HUP 시그널로 프로세스 재시작 시도
                os.system(f"killall -HUP '{browser}' 2>/dev/null")
                time.sleep(2)

                print(f"✅ {browser} 시그널 재시작 완료")

            except Exception as e:
                print(f"⚠️ {browser} 시그널 재시작 중 오류: {e}")

    except Exception as e:
        print(f"⚠️ 프로세스 시그널 재시작 중 오류: {e}")
```

#### **문제점**
- ❌ **브라우저가 완전히 종료됨 (세션 손실)**: 의도와 다른 결과
- ❌ **의도한 "DNS 초기화"가 아닌 "브라우저 재시작"**: 너무 강력한 방법

#### **실패 원인 분석**
```python
# 프로세스 시그널의 한계
# 1. HUP 시그널이 브라우저에서 예상과 다르게 동작
# 2. 브라우저가 완전 종료되어 세션 손실
# 3. 세션 보존이 목표였으나 반대 결과
```

### **5. 현재 방식 (브라우저 재시작 + 세션 복구)**

#### **최종 해결책**
```python
def force_browser_restart():
    """실행 중인 브라우저를 안전하게 재시작하고 세션 복구"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🔄 브라우저 재시작 중... ({', '.join(running_browsers)})")

        # 브라우저 세션 저장
        save_browser_sessions()

        for browser in running_browsers:
            try:
                # 브라우저를 안전하게 종료 (AppleScript 사용)
                os.system(f"osascript -e 'tell application \"{browser}\" to quit' 2>/dev/null")
                time.sleep(2)  # 안전한 종료 대기

                # 여전히 실행 중이면 강제 종료
                result = os.system(f"pgrep -f '{browser}' >/dev/null 2>&1")
                if result == 0:
                    os.system(f"pkill -f '{browser}' 2>/dev/null")
                    time.sleep(1)

                # 브라우저 재시작
                os.system(f"open -a '{browser}' 2>/dev/null")
                print(f"✅ {browser} 재시작 완료")

            except Exception as e:
                print(f"⚠️ {browser} 재시작 중 오류: {e}")

        # 브라우저 재시작 후 세션 복구
        time.sleep(5)  # 브라우저 완전 로딩 대기
        restore_browser_sessions()

        print("✅ 브라우저 재시작 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 재시작 중 오류: {e}")
```

#### **세션 복구 시스템**
```python
def restore_browser_sessions():
    """브라우저 세션을 자동으로 복구"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🔄 브라우저 세션 복구 중... ({', '.join(running_browsers)})")

        for browser in running_browsers:
            try:
                # 브라우저 활성화
                os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                time.sleep(0.5)

                # 새 창 닫기 (Cmd+W)
                for _ in range(3):
                    os.system("osascript -e 'tell application \"System Events\" to key code 13 using {command down}' 2>/dev/null")
                    time.sleep(0.1)

                time.sleep(1.5)

                # Cmd+Shift+T로 세션 복구
                os.system("osascript -e 'tell application \"System Events\" to key code 17 using {command down, shift down}' 2>/dev/null")

                print(f"✅ {browser} 세션 복구 완료")

            except Exception as e:
                print(f"⚠️ {browser} 세션 복구 중 오류: {e}")

        print("✅ 브라우저 세션 복구 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 세션 복구 중 오류: {e}")
```

#### **장점**
- ✅ **완벽한 DNS 캐시 초기화**: 브라우저 재시작으로 메모리 캐시 완전 초기화
- ✅ **세션 보존**: 세션 복구로 사용자 경험 유지
- ✅ **안정적 동작**: AppleScript 기반으로 안정적

#### **단점**
- ❌ **브라우저 종료 필요**: 원래 목표인 "종료 없이" 해결은 미달성
- ❌ **시간 소요**: 재시작과 세션 복구에 시간 필요

---

## 🎯 핵심 과제 분석

### **진짜 해결해야 할 문제**

#### **핵심 과제: 브라우저 메모리 DNS 캐시 초기화**
- **위치**: 브라우저 프로세스 메모리 내부
- **특성**: 프로세스가 살아있는 한 유지됨
- **영향**: hosts 파일 차단을 무시하고 기존 IP 사용

#### **제약 조건**
- ✅ 브라우저 종료 없이 해결
- ✅ 세션 유지 (로그인, 탭 등)
- ✅ UI 조작 없이 해결
- ✅ 안정적으로 작동

---

## 🔬 가능한 해결 방향들

### **방향 1: 브라우저 API 직접 호출**

#### **개념**
```python
# 브라우저의 내장 API를 직접 호출
# 예: Chrome의 chrome://net-internals/#dns API
def call_browser_api():
    """브라우저 내장 API를 통한 DNS 캐시 초기화"""
    # Chrome의 경우 chrome://net-internals/#dns 접근
    # Firefox의 경우 about:networking 접근
    # Safari의 경우 개발자 도구 API 접근
```

#### **장점**
- ✅ 브라우저 내장 기능 사용
- ✅ 안정적이고 신뢰할 수 있음

#### **단점**
- ❌ 브라우저별 API가 다름
- ❌ 구현이 복잡함
- ❌ API 접근 방법이 브라우저마다 상이

### **방향 2: 네트워크 연결 강제 끊기**

#### **개념**
```python
# 브라우저의 네트워크 연결을 강제로 끊어서 DNS 재확인 유도
def force_network_disconnect():
    """특정 포트나 연결을 차단했다가 해제"""
    # YouTube 관련 포트 일시 차단
    # 브라우저가 DNS 재확인하도록 유도
    # 차단 해제
```

#### **장점**
- ✅ 메모리 DNS 캐시를 우회할 수 있음
- ✅ 브라우저 종료 없이 가능

#### **단점**
- ❌ 네트워크 레벨에서의 복잡한 조작 필요
- ❌ 다른 네트워크 연결에 영향 가능
- ❌ 구현이 매우 복잡함

### **방향 3: 브라우저 설정 파일 조작**

#### **개념**
```python
# 브라우저의 설정 파일을 직접 수정하여 DNS 캐시 비활성화
def modify_browser_settings():
    """브라우저 설정 파일 조작"""
    for browser in running_browsers:
        if browser == "Google Chrome":
            # Chrome의 DNS 캐시 설정 파일 찾기
            chrome_settings_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Preferences")
            # DNS 캐시 관련 설정을 비활성화하거나 초기화
```

#### **장점**
- ✅ 브라우저 종료 없이 가능
- ✅ 세션 유지
- ✅ UI 조작 없음
- ✅ 안정적

#### **단점**
- ❌ 브라우저별 설정 파일 구조가 다름
- ❌ 설정 파일 형식이 복잡함
- ❌ 안전한 수정 방법 구현 필요

### **방향 4: 네트워크 인터페이스 조작**

#### **개념**
```python
# 네트워크 인터페이스를 일시적으로 재시작하여 DNS 캐시 무효화
def restart_network_interface():
    """네트워크 인터페이스 down/up"""
    # 네트워크 인터페이스 일시 중단
    # DNS 캐시 무효화
    # 네트워크 인터페이스 재시작
```

#### **장점**
- ✅ 시스템 레벨에서 강력한 효과
- ✅ 모든 브라우저에 동일하게 적용

#### **단점**
- ❌ 전체 네트워크에 영향
- ❌ 권한 필요
- ❌ 다른 네트워크 연결 중단

---

## 🏆 최종 해결책

### **현재 채택한 방법: 브라우저 재시작 + 세션 복구**

#### **왜 이 방법을 선택했는가?**

1. **완벽한 DNS 캐시 초기화**: 브라우저 재시작으로 메모리 캐시 완전 초기화
2. **사용자 경험 보존**: 세션 복구로 탭, 로그인 상태 유지
3. **안정성**: AppleScript 기반으로 안정적 동작
4. **구현 용이성**: 복잡한 API나 네트워크 조작 없이 구현 가능

#### **구현된 최종 시스템**
```python
def force_dns_cache_clear():
    """브라우저 메모리 DNS 캐시까지 완전 초기화 (세션 보존 재시작)"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🌐 브라우저 메모리 DNS 캐시 완전 초기화 중... ({', '.join(running_browsers)})")

        for browser in running_browsers:
            try:
                # 1단계: 캐시 파일 삭제
                # 2단계: 시스템 DNS 캐시 초기화
                # 3단계: 브라우저 메모리 DNS 캐시 초기화 (세션 보존 재시작)

                # 브라우저 종료 (세션 보존)
                os.system(f"osascript -e 'tell application \"{browser}\" to quit' 2>/dev/null")
                time.sleep(2)

                # 브라우저 재시작
                os.system(f"open -a '{browser}' 2>/dev/null")
                time.sleep(3)

                # 세션 복구 (Cmd+Shift+T)
                os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                time.sleep(1)
                os.system("osascript -e 'tell application \"System Events\" to key code 17 using {command down, shift down}' 2>/dev/null")

                print(f"✅ {browser} DNS 캐시 완전 초기화 완료")

            except Exception as e:
                print(f"⚠️ {browser} DNS 캐시 초기화 중 오류: {e}")

        print("✅ 브라우저 메모리 DNS 캐시 완전 초기화 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 메모리 DNS 캐시 초기화 중 오류: {e}")
```

---

## 💡 결론 및 교훈

### **기술적 교훈**

#### **1. 문제의 본질 파악의 중요성**
- DNS 캐시의 3단계 구조를 이해해야 정확한 해결책 도출 가능
- 표면적 문제가 아닌 근본 원인을 찾는 것이 핵심

#### **2. 점진적 접근의 가치**
- 여러 해결책을 시도하면서 각각의 한계점을 파악
- 실패한 시도들이 최종 해결책의 방향을 제시

#### **3. 사용자 경험과 기술적 완벽함의 균형**
- 완벽한 기술적 해결책보다는 실용적이고 안정적인 해결책 선택
- 세션 보존으로 사용자 경험 우선 고려

### **향후 개선 방향**

#### **1. 브라우저 API 활용 연구**
- 각 브라우저의 내장 API를 활용한 DNS 캐시 초기화 방법 연구
- 브라우저별 특성을 고려한 최적화된 해결책 개발

#### **2. 네트워크 레벨 최적화**
- 네트워크 연결 조작을 통한 DNS 캐시 우회 방법 연구
- 시스템 레벨에서의 더 정교한 제어 방법 개발

#### **3. 크로스 플랫폼 확장**
- Windows, Linux에서의 동일한 문제 해결 방법 연구
- 플랫폼별 특성을 고려한 차별화된 해결책 개발

### **최종 평가**

현재 구현된 브라우저 재시작 + 세션 복구 방식은:

- ✅ **기술적 완성도**: DNS 캐시 완전 초기화 달성
- ✅ **사용자 경험**: 세션 보존으로 불편함 최소화
- ✅ **안정성**: AppleScript 기반으로 안정적 동작
- ✅ **실용성**: 복잡한 구현 없이 효과적 해결

**결론**: 완벽한 해결책은 아니지만, 현재 기술적 제약 내에서 최적의 균형점을 찾은 해결책입니다.

---

## 📚 다음 편 예고

### **Part 2: 엔터프라이즈 제품 개발기**
- **GUI 인터페이스**: 사용자 친화적인 그래픽 인터페이스
- **웹 대시보드**: 원격 모니터링 및 제어 시스템
- **다중 사용자 지원**: 조직 내 여러 사용자 관리
- **고급 통계**: 사용 패턴 분석 및 리포트
- **API 통합**: 외부 시스템과의 연동

### **Part 3: 기술적 도전과 해결 (심화편)**
- **브라우저 API 직접 호출**: 각 브라우저별 내장 API 활용
- **네트워크 레벨 최적화**: 시스템 레벨에서의 정교한 제어
- **크로스 플랫폼 호환성**: Windows, Linux 지원
- **성능 최적화**: 리소스 사용량 최소화

---

**#YouTube차단 #DNS캐시 #문제해결 #개발기 #Python #macOS #브라우저최적화**