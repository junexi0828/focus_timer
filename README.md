# Focus Timer - 집중 모드 시스템

<div align="center">

![Focus Timer Logo](https://img.shields.io/badge/Focus%20Timer-Enterprise-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.13+-green?style=for-the-badge&logo=python)
![macOS](https://img.shields.io/badge/macOS-Supported-orange?style=for-the-badge&logo=apple)
![License](https://img.shields.io/badge/License-Commercial-red?style=for-the-badge)

**생산성 향상을 위한 강력한 집중 모드 시스템**

[개인용](#personal-edition) • [macOS 앱](#-macos-앱) • [기업용 CLI](#enterprise-cli-edition) • [기업용 GUI](#enterprise-gui-edition) • [기업용 웹](#enterprise-web-edition)

**[English Version](README_EN.md)**

</div>

---

## 🎯 제품 라인업

<div align="center">

| 제품 | 타겟 | 특징 | 가격 |
|------|------|------|------|
| **[Personal Edition](#personal-edition)** | 개인 사용자 | 간단한 터미널 기반 | **무료** |
| **[macOS App](#-macos-앱)** | macOS 사용자 | 네이티브 앱 번들 | **$6/월** |
| **[Enterprise CLI Edition](#enterprise-cli-edition)** | 기업/조직 | 시스템 서비스 + CLI | **$4/월** |
| **[Enterprise GUI Edition](#enterprise-gui-edition)** | 기업/조직 | GUI + 시스템 서비스 | **$4/월** |
| **[Enterprise Web Edition](#enterprise-web-edition)** | 기업/조직 | 웹 인터페이스 + 클라우드 | **$7/월** |

</div>

---

## 📱 Personal Edition

<div align="center">

![Personal Edition](https://img.shields.io/badge/Personal-Edition-green?style=for-the-badge)

**간단하고 효과적인 개인용 집중 모드**

</div>

### ✨ 주요 기능
- 🚫 **YouTube 완전 차단** - 핵심 도메인 및 API 서비스 차단
- 🔐 **알고리즘 문제 기반 종료 방지** - 난이도별 문제 해결 필요
- 🔄 **브라우저 강제 재시작** - 집중 모드 시작 시 자동 재시작
- 🚀 **자동 시작 시스템** - 시스템 부팅 시 자동 실행
- ⏰ **유연한 시간 설정** - 시간대별/타이머별 차단

### 🎮 사용 모드
1. **시간대 차단 모드** - 매일 지정한 시간에 차단
2. **타이머 차단 모드** - 지금부터 N시간 동안 차단
3. **집중 모드 (강화)** - 완전한 종료 방지 + 브라우저 재시작

### 🚀 빠른 시작
```bash
cd personal/
sudo python3 focus_timer.py
```

### 📁 파일 구조
```
personal/
├── focus_timer.py              # 메인 프로그램
├── install_focus_timer.sh      # 자동 시작 설치
├── uninstall_focus_timer.sh    # 자동 시작 제거
└── README.md                   # 상세 문서
```

**[📖 Personal Edition 상세 문서 →](personal/README.md)**

---

## 🍎 macOS App

<div align="center">

![macOS App](https://img.shields.io/badge/macOS-App%20Bundle-blue?style=for-the-badge&logo=apple)

**macOS 네이티브 앱으로 구현된 통합 집중 모드 시스템**

</div>

### ✨ 주요 기능
- 🍎 **macOS 네이티브 앱** - 시스템과 완벽 통합
- 🖥️ **통합 GUI 인터페이스** - 직관적인 사용자 경험
- 💻 **CLI 명령줄 도구** - 고급 사용자를 위한 터미널 제어
- 🔄 **백그라운드 서비스** - 지속적인 모니터링 및 보호
- ⚙️ **중앙화된 설정 관리** - JSON 기반 설정 시스템
- 🛡️ **시스템 레벨 보호** - hosts 파일 권한 관리
- 🚀 **독립 실행 파일** - PyInstaller로 완전 독립적인 앱 번들
- 🔄 **자동 재시작 시스템** - LaunchAgent 기반 백그라운드 서비스
- 🖥️ **시스템 부팅 시 자동 시작** - 전원 재시동 후 자동 실행
- 🛡️ **파일 모니터링** - hosts 파일 무단 수정 방지 및 자동 복구

### 🎮 사용 모드
1. **GUI 모드** - 마우스 클릭으로 모든 제어
2. **CLI 모드** - 터미널에서 고급 제어
3. **백그라운드 모드** - 자동 모니터링 및 보호

### 🚀 빠른 시작
```bash
# 앱 실행 (더블클릭 또는 터미널)
open /Applications/FocusTimer.app

# CLI 모드
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI

# 백그라운드 서비스 상태 확인
launchctl list | grep focustimer

# 로그 확인
tail -f /var/log/FocusTimer/focus_timer.log
```

### 📁 파일 구조
```
FocusTimer.app/
├── Contents/
│   ├── Info.plist                    # 앱 번들 정보
│   ├── MacOS/
│   │   ├── FocusTimer               # 메인 GUI 애플리케이션 (독립 실행 파일)
│   │   ├── FocusTimerCLI            # 명령줄 인터페이스
│   │   └── FocusTimerHelper         # 백그라운드 서비스
│   └── Resources/
│       ├── config.json              # 앱 설정 파일
│       ├── com.focustimer.helper.plist  # LaunchAgent 설정
│       ├── FocusTimer.icns          # 앱 아이콘
│       ├── algorithm_tab.py         # 알고리즘 시스템
│       ├── gui_algorithm_manager.py # 알고리즘 GUI 관리
│       └── user_data/               # 사용자 데이터
```

**[📖 macOS App 상세 문서 →](FocusTimer.app/README.md)**

---

## 💻 Enterprise CLI Edition

<div align="center">

![Enterprise CLI](https://img.shields.io/badge/Enterprise-CLI-blue?style=for-the-badge)

**시스템 레벨 보호와 지속적 모니터링**

</div>

### ✨ 주요 기능
- 🛡️ **시스템 레벨 보호** - hosts 파일 권한 관리
- 👁️ **지속적 파일 모니터링** - 실시간 변경 감지
- 🔒 **다중 차단 레이어** - hosts + DNS + 브라우저 캐시
- 🧮 **알고리즘 문제 시스템** - 5단계 난이도
- 📊 **실시간 로깅** - 상세한 시스템 이벤트 기록
- 💾 **상태 지속성 관리** - 설정 및 상태 자동 저장

### 🔧 시스템 서비스
- **LaunchDaemon 등록** - 백그라운드 자동 실행
- **자동 복구** - 차단 해제 시도 시 자동 재적용
- **보안 강화** - 우회 시도 감지 시 자동 대응

### 🚀 빠른 시작
```bash
cd enterprise/
sudo python3 setup_enterprise.py      # 설정
sudo python3 focus_timer_enterprise.py # 실행
```

### 📁 파일 구조
```
enterprise/
├── focus_timer_enterprise.py  # 메인 프로그램
├── setup_enterprise.py        # 설정 도구
└── README.md                  # 상세 문서
```

**[📖 Enterprise CLI Edition 상세 문서 →](enterprise/README.md)**

---

## 🖥️ Enterprise GUI Edition

<div align="center">

![Enterprise GUI](https://img.shields.io/badge/Enterprise-GUI-purple?style=for-the-badge)

**GUI 인터페이스와 시스템 서비스의 완벽한 결합**

</div>

### ✨ 주요 기능
- 🖥️ **직관적인 GUI 인터페이스** - 마우스 클릭으로 모든 제어
- 📊 **실시간 상태 모니터링** - 현재 상태를 한눈에 확인
- 🎛️ **통합 제어 패널** - 집중 모드 시작/중지, 즉시 차단/해제
- 📈 **통계 대시보드** - 차단 횟수, 우회 시도, 난이도 표시
- 📝 **실시간 로그 뷰어** - 시스템 이벤트 실시간 확인
- ⚙️ **원클릭 설정** - 시간, 난이도, 보안 옵션 설정

### 🎮 GUI 구성
- **상태 표시 패널** - 현재 집중 모드 상태 및 시간
- **제어 패널** - 집중 모드 시작/중지, 즉시 차단/해제
- **통계 대시보드** - 차단 횟수, 우회 시도, 현재 난이도
- **실시간 로그 뷰어** - 시스템 이벤트, 보안 경고, 오류 메시지

### 🚀 빠른 시작
```bash
cd enterprise_gui/
sudo python3 focus_timer_enterprise_gui.py
```

### 📁 파일 구조
```
enterprise_gui/
├── focus_timer_enterprise_gui.py  # GUI 메인 프로그램
└── README.md                      # 상세 문서
```

**[📖 Enterprise GUI Edition 상세 문서 →](enterprise_gui/README.md)**

---

## 🌐 Enterprise Web Edition

<div align="center">

![Enterprise Web](https://img.shields.io/badge/Enterprise-Web-orange?style=for-the-badge)

**웹 인터페이스와 클라우드 기반 원격 관리**

</div>

### ✨ 주요 기능
- 🌐 **웹 기반 인터페이스** - 브라우저에서 접근 가능
- ☁️ **클라우드 관리** - 원격에서 시스템 제어
- 📱 **반응형 디자인** - 모바일, 태블릿, 데스크톱 지원
- 🔐 **다중 사용자 지원** - 팀 단위 관리
- 📊 **고급 분석** - 사용 패턴 및 생산성 분석
- 🔄 **실시간 동기화** - 여러 기기 간 설정 동기화

### 🎯 사용 시나리오
- **기업 환경** - IT 관리자가 중앙에서 관리
- **팀 협업** - 팀원들의 집중 모드 통합 관리
- **원격 근무** - 재택근무 환경에서 집중 모드 관리
- **교육 기관** - 학생들의 학습 환경 관리

### 🚀 빠른 시작
```bash
cd enterprise_web/
sudo python3 focus_timer_enterprise_web.py
```

### 📁 파일 구조
```
enterprise_web/
├── focus_timer_enterprise_web.py  # 웹 서버 프로그램
└── README.md                      # 상세 문서
```

**[📖 Enterprise Web Edition 상세 문서 →](enterprise_web/README.md)**

---

## ⚙️ 설정 관리 시스템

<div align="center">

![Config Management](https://img.shields.io/badge/Config-Management-gray?style=for-the-badge)

**중앙화된 설정 관리 및 GUI 편집 도구**

</div>

### ✨ 주요 기능
- 📝 **JSON 기반 설정** - 구조화된 설정 파일 관리
- 🖥️ **GUI 설정 편집기** - 6개 탭으로 분류된 설정 관리
- 🔄 **실시간 설정 변경** - 설정 변경 시 즉시 적용
- 📤 **설정 백업/복원** - 설정 내보내기/가져오기
- ✅ **설정 유효성 검사** - 설정 오류 자동 감지
- 📊 **설정 요약 보기** - 현재 설정 상태 한눈에 확인

### 🎛️ 설정 카테고리
1. **일반** - 앱 정보, 시스템 경로
2. **웹사이트** - 차단할 사이트 관리
3. **집중 모드** - 시간, 난이도 설정
4. **보안** - 보안 기능 활성화
5. **GUI** - 인터페이스 설정
6. **고급** - 로깅, 검증 설정

### 🚀 빠른 시작
```bash
cd config/
python3 config_gui.py
```

### 📁 파일 구조
```
config/
├── config.json        # 메인 설정 파일
├── config_manager.py  # 설정 관리 클래스
├── config_gui.py      # 설정 GUI 도구
└── README.md          # 상세 문서
```

**[📖 설정 관리 시스템 상세 문서 →](config/README.md)**

---

## 🧮 알고리즘 시스템 (Phase 4)

<div align="center">

![Algorithm System](https://img.shields.io/badge/Algorithm-System-blue?style=for-the-badge)

**대기업 코딩테스트 수준의 알고리즘 문제 시스템**

</div>

### ✨ 주요 기능
- 🏗️ **표준화된 데이터 구조** - 플랫폼별 문제 통합 관리
- 🌐 **외부 플랫폼 연동** - Codeforces, LeetCode, Kaggle 지원
- 📊 **고급 난이도 체계** - Easy, Medium, Hard, Expert
- 🏷️ **알고리즘 태그 시스템** - 30+ 알고리즘 카테고리
- 💾 **JSON 직렬화** - 완전한 데이터 저장 및 복원
- 🔄 **문제 컬렉션 관리** - 체계적인 문제 분류 및 검색

### 🎯 Phase 4 계획
- **4-1단계**: ✅ 표준 문제 데이터 구조 설계 (완료)
- **4-2단계**: ✅ 외부 플랫폼 연동 시스템 (완료)
- **4-3단계**: 📋 고급 알고리즘 챌린지 시스템 (예정)
- **4-4단계**: 🖥️ GUI 알고리즘 관리 인터페이스 (예정)

### 📁 파일 구조
```
algorithm_system/
├── problem_data_structures.py      # 핵심 데이터 구조
├── remote_problem_provider.py      # 외부 플랫폼 연동 시스템
├── example_problems.py             # 데이터 구조 사용 예시
├── remote_provider_example.py      # 외부 플랫폼 연동 예시
├── __init__.py                     # 패키지 초기화
└── README.md                       # 상세 문서
```

### 🚀 빠른 시작
```bash
# 데이터 구조 예시
cd algorithm_system
python3 example_problems.py

# 외부 플랫폼 연동 예시
python3 remote_provider_example.py
```

**[📖 알고리즘 시스템 상세 문서 →](algorithm_system/README.md)**

---



## 📦 설치 및 배포

<div align="center">

![Installation](https://img.shields.io/badge/Installation-Scripts-yellow?style=for-the-badge)

**자동화된 설치 및 배포 스크립트**

</div>

### 🚀 설치 스크립트
- **Personal Edition**: `personal/install_focus_timer.sh`
- **macOS App**: `installers/install_focustimer_app.sh`
- **Enterprise Edition**: `installers/install_enterprise.sh`
- **제거 스크립트**: 각 버전별 uninstall 스크립트

### 📋 시스템 요구사항
- **OS**: macOS 10.15+
- **Python**: 3.13+
- **권한**: 관리자 권한 (sudo)
- **패키지**: watchdog, psutil (Enterprise 버전)

### 🔧 의존성 설치
```bash
# Python 가상환경 생성
python3 -m venv focus_timer_env
source focus_timer_env/bin/activate

# 필수 패키지 설치
pip install watchdog psutil

# Tkinter 설치 (GUI 버전용)
brew install python-tk@3.13
```

### 📁 설치 파일 구조
```
installers/
├── install_focustimer_app.sh  # macOS 앱 설치
├── uninstall_focustimer_app.sh # macOS 앱 제거
├── update_focustimer_app.sh   # macOS 앱 업데이트
├── install_enterprise.sh      # Enterprise 버전 설치
├── uninstall_enterprise.sh    # Enterprise 버전 제거
└── README.md                  # 설치 가이드
```

---

## 📊 기능 비교표

<div align="center">

| 기능 | Personal | macOS App | Enterprise CLI | Enterprise GUI | Enterprise Web |
|------|----------|-----------|----------------|----------------|----------------|
| **기본 차단** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **알고리즘 문제** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **고급 알고리즘 시스템** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **시스템 서비스** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **GUI 인터페이스** | ❌ | ✅ | ❌ | ✅ | ❌ |
| **CLI 인터페이스** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **웹 인터페이스** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **설정 관리** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **로그 시스템** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **다중 차단 레이어** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **파일 모니터링** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **자동 복구** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **원격 관리** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **다중 사용자** | ❌ | ❌ | ❌ | ❌ | ✅ |

</div>

---

## 🎯 사용 시나리오

### 👤 개인 사용자
- **추천 제품**: Personal Edition
- **사용 목적**: 개인 생산성 향상
- **주요 기능**: YouTube 차단, 종료 방지
- **설치 방법**: 단일 파일 실행

### 🍎 macOS 사용자
- **추천 제품**: macOS App
- **사용 목적**: macOS 최적화된 집중 모드
- **주요 기능**: 네이티브 앱, GUI/CLI 통합
- **설치 방법**: 앱 번들 설치

### 🏢 소규모 기업
- **추천 제품**: Enterprise CLI Edition
- **사용 목적**: 직원 생산성 관리
- **주요 기능**: 시스템 서비스, 로깅
- **설치 방법**: 자동 설치 스크립트

### 🏢 중대규모 기업
- **추천 제품**: Enterprise GUI Edition
- **사용 목적**: IT 관리자 편의성
- **주요 기능**: GUI 관리, 실시간 모니터링
- **설치 방법**: 자동 설치 스크립트

### 🌐 클라우드 기업
- **추천 제품**: Enterprise Web Edition
- **사용 목적**: 원격 관리, 팀 협업
- **주요 기능**: 웹 인터페이스, 다중 사용자
- **설치 방법**: 자동 설치 스크립트

---

## 📞 지원 및 문의

<div align="center">

![Support](https://img.shields.io/badge/Support-Available-green?style=for-the-badge)

</div>

### 📧 연락처
- **개발자**: juns
- **이메일**: junexi0828@gmail.com
- **GitHub**: [Focus Timer Repository](https://github.com/your-repo/focus-timer)

### 📚 문서
- **[Personal Edition](personal/README.md)** - 개인용 상세 문서
- **[macOS App](FocusTimer.app/README.md)** - macOS 앱 상세 문서
- **[Enterprise CLI Edition](enterprise/README.md)** - 기업용 CLI 상세 문서
- **[Enterprise GUI Edition](enterprise_gui/README.md)** - 기업용 GUI 상세 문서
- **[Enterprise Web Edition](enterprise_web/README.md)** - 기업용 웹 상세 문서
- **[설정 관리](config/README.md)** - 설정 관리 상세 문서
- **[알고리즘 시스템](algorithm_system/README.md)** - Phase 4 알고리즘 시스템
- **[라이선스](docs/LICENSE)** - 라이선스 정보

### 🐛 문제 해결
1. **로그 확인**: `/var/log/FocusTimer/focus_timer.log`
2. **권한 확인**: `ls -la /etc/hosts`
3. **서비스 상태**: `sudo launchctl list | grep focustimer`
4. **설정 확인**: `config/config.json`
5. **앱 번들 상태**: `file /Applications/FocusTimer.app/Contents/MacOS/FocusTimer`
6. **LaunchAgent 상태**: `launchctl list | grep focustimer`

---

<div align="center">

**💡 Focus Timer는 생산성 향상과 자기 통제력을 기르는 데 도움을 주기 위해 만들어졌습니다.**

![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

</div>