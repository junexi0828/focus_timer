# Focus Timer - Enterprise GUI Edition

## 🖥️ 기업용 GUI 집중 모드 시스템

GUI 인터페이스와 시스템 서비스를 결합한 완전한 상업용 집중 모드 시스템입니다.

## 🚀 빠른 시작

```bash
# GUI 프로그램 실행
sudo python3 focus_timer_enterprise_gui.py
```

## 📋 주요 기능

- ✅ GUI 인터페이스
- ✅ 실시간 상태 모니터링
- ✅ 시스템 레벨 보호
- ✅ 지속적 파일 모니터링
- ✅ 다중 차단 레이어
- ✅ 알고리즘 문제 시스템
- ✅ 실시간 로깅
- ✅ 통계 대시보드

## 🖥️ GUI 구성

### 1. 상태 표시 패널
- 현재 집중 모드 상태
- 설정된 시간 범위
- 실시간 상태 업데이트

### 2. 제어 패널
- 집중 모드 시작/중지
- 즉시 차단/해제
- 시간 및 난이도 설정

### 3. 통계 대시보드
- 차단 횟수
- 우회 시도 횟수
- 현재 난이도

### 4. 실시간 로그 뷰어
- 시스템 이벤트
- 보안 경고
- 오류 메시지

## ⚙️ 설정

### GUI에서 설정
1. **시간 설정**: 시작/종료 시간 입력
2. **난이도 설정**: 알고리즘 문제 난이도 선택
3. **즉시 적용**: 설정 변경 시 즉시 적용

### 설정 파일 연동
GUI는 `../config/config.json` 파일과 연동됩니다:

```json
{
  "focus_mode": {
    "default_start_time": "09:00",
    "default_end_time": "18:00",
    "default_difficulty": 1
  },
  "gui_settings": {
    "window_size": {"width": 800, "height": 600},
    "theme": "clam",
    "auto_refresh_interval": 5
  }
}
```

## 🔧 시스템 요구사항

### 필수 패키지
```bash
# Python 가상환경 생성
python3 -m venv focus_timer_env
source focus_timer_env/bin/activate

# 필수 패키지 설치
pip install watchdog psutil

# Tkinter 설치 (GUI용)
brew install python-tk@3.13
```

### 권한 요구사항
- 관리자 권한 (sudo)
- hosts 파일 수정 권한
- 시스템 서비스 등록 권한

## 📁 파일 구조

```
enterprise_gui/
├── focus_timer_enterprise_gui.py  # GUI 메인 프로그램
└── README.md                      # 이 파일
```

## 🎯 사용법

### 1. 기본 실행
```bash
# 가상환경 활성화
source focus_timer_env/bin/activate

# GUI 실행
sudo python3 focus_timer_enterprise_gui.py
```

### 2. 집중 모드 설정
1. **시작 시간 입력**: 예) `09:00` 또는 `9.5`
2. **종료 시간 입력**: 예) `18:00` 또는 `18.5`
3. **난이도 선택**: 1-5단계
4. **집중 모드 시작** 버튼 클릭

### 3. 실시간 모니터링
- **상태 패널**: 현재 집중 모드 상태 확인
- **통계 패널**: 차단 횟수 및 우회 시도 확인
- **로그 패널**: 실시간 시스템 로그 확인

## 🔒 보안 기능

### 시스템 레벨 보호
- hosts 파일 권한 관리
- 파일 시스템 모니터링
- 자동 차단 재적용

### GUI 보안
- 실시간 상태 모니터링
- 보안 경고 알림
- 자동 복구 기능

## 📊 로깅 및 모니터링

### 로그 위치
```
/var/log/FocusTimer/focus_timer.log
```

### GUI에서 로그 확인
- 실시간 로그 뷰어에서 확인
- 최근 20줄 자동 표시
- 5초마다 자동 새로고침

## 🎮 GUI 기능

### 제어 버튼
- **🚀 집중 모드 시작**: 설정된 시간에 집중 모드 활성화
- **⏹️ 집중 모드 중지**: 집중 모드 비활성화
- **🔒 즉시 차단**: 웹사이트 즉시 차단
- **🔓 즉시 해제**: 웹사이트 차단 즉시 해제

### 설정 옵션
- **시간 형식**: 24시간 형식 또는 소수점 형식
- **난이도**: 1-5단계 알고리즘 문제
- **자동 새로고침**: 5초 간격으로 상태 업데이트

## ⚠️ 주의사항

1. **관리자 권한**: GUI 실행 시 sudo 권한이 필요합니다.
2. **가상환경**: Python 가상환경에서 실행해야 합니다.
3. **Tkinter**: GUI 표시를 위해 Tkinter가 설치되어야 합니다.
4. **실시간 모니터링**: 백그라운드에서 지속적으로 실행됩니다.

## 🔧 문제 해결

### GUI가 실행되지 않는 경우
```bash
# Tkinter 설치 확인
python3 -c "import tkinter; print('Tkinter OK')"

# 가상환경 확인
which python3
pip list | grep tkinter
```

### 권한 문제
```bash
# 관리자 권한으로 실행
sudo python3 focus_timer_enterprise_gui.py

# hosts 파일 권한 확인
ls -la /etc/hosts
```

### 로그 확인
```bash
# 실시간 로그 확인
tail -f /var/log/FocusTimer/focus_timer.log

# GUI 로그 확인
grep "GUI" /var/log/FocusTimer/focus_timer.log
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **GUI 로그**: GUI 내 로그 뷰어
2. **시스템 로그**: `/var/log/FocusTimer/focus_timer.log`
3. **설정 파일**: `../config/config.json`
4. **가상환경**: `focus_timer_env` 활성화 상태