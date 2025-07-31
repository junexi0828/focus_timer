# Focus Timer - 설정 관리 시스템

## ⚙️ 설정 관리 도구

모든 Focus Timer 버전의 설정을 중앙에서 관리하는 시스템입니다.

## 📁 파일 구조

```
config/
├── config.json        # 메인 설정 파일
├── config_manager.py  # 설정 관리 클래스
├── config_gui.py      # 설정 GUI 도구
└── README.md          # 이 파일
```

## 🚀 빠른 시작

### 설정 GUI 실행
```bash
python3 config_gui.py
```

### 설정 파일 직접 편집
```bash
# 설정 파일 열기
open config.json

# 또는 텍스트 에디터로 편집
nano config.json
```

## 📋 설정 카테고리

### 1. 앱 정보 (`app_info`)
```json
{
  "app_info": {
    "name": "Focus Timer Enterprise GUI",
    "version": "2.0.0",
    "description": "상업용 집중 모드 시스템"
  }
}
```

### 2. 시스템 경로 (`system_paths`)
```json
{
  "system_paths": {
    "hosts_file": "/etc/hosts",
    "redirect_ip": "127.0.0.1",
    "state_path": "/Library/Application Support/FocusTimer/state.json",
    "log_path": "/var/log/FocusTimer/focus_timer.log"
  }
}
```

### 3. 차단할 웹사이트 (`blocked_websites`)
```json
{
  "blocked_websites": {
    "youtube": ["youtube.com", "www.youtube.com"],
    "social_media": ["facebook.com", "instagram.com"],
    "gaming": ["twitch.tv", "discord.com"],
    "entertainment": ["netflix.com", "spotify.com"]
  }
}
```

### 4. 집중 모드 설정 (`focus_mode`)
```json
{
  "focus_mode": {
    "default_start_time": "09:00",
    "default_end_time": "18:00",
    "default_difficulty": 1,
    "max_attempts": 3
  }
}
```

### 5. 보안 설정 (`security`)
```json
{
  "security": {
    "enable_system_protection": true,
    "enable_file_monitoring": true,
    "enable_dns_cache_flush": true,
    "lock_hosts_file": true
  }
}
```

### 6. GUI 설정 (`gui_settings`)
```json
{
  "gui_settings": {
    "window_size": {"width": 800, "height": 600},
    "theme": "clam",
    "auto_refresh_interval": 5
  }
}
```

## 🖥️ GUI 설정 도구

### 탭 구성
1. **일반**: 앱 정보, 시스템 경로
2. **웹사이트**: 차단할 사이트 관리
3. **집중 모드**: 시간, 난이도 설정
4. **보안**: 보안 기능 활성화
5. **GUI**: 인터페이스 설정
6. **고급**: 로깅, 검증 설정

### 주요 기능
- **💾 저장**: 설정 변경사항 저장
- **🔄 새로고침**: 설정 파일 다시 로드
- **📤 내보내기**: 설정 백업
- **📥 가져오기**: 설정 복원
- **🔄 기본값으로 초기화**: 기본 설정으로 복원
- **🔍 설정 유효성 검사**: 설정 오류 확인
- **📊 설정 요약 보기**: 현재 설정 요약

## 🔧 설정 관리 클래스

### 기본 사용법
```python
from config_manager import ConfigManager

# 설정 관리자 생성
config = ConfigManager()

# 설정값 가져오기
app_name = config.get('app_info.name')
start_time = config.get_focus_mode_setting('default_start_time')

# 설정값 변경
config.set('focus_mode.default_start_time', '08:00')
config.save_config()
```

### 주요 메서드
- `get(key, default=None)`: 설정값 가져오기
- `set(key, value)`: 설정값 변경
- `save_config()`: 설정 파일 저장
- `load_config()`: 설정 파일 로드
- `validate_config()`: 설정 유효성 검사
- `export_config(path)`: 설정 내보내기
- `import_config(path)`: 설정 가져오기

## 🔄 파일 연동

### 설정 파일 공유
```
config/config.json
├── enterprise/focus_timer_enterprise.py
├── enterprise_gui/focus_timer_enterprise_gui.py
└── enterprise_web/focus_timer_enterprise_web.py
```

### 설정 변경 시 영향
1. **즉시 적용**: GUI 버전에서 즉시 반영
2. **재시작 필요**: CLI/웹 버전에서 재시작 시 반영
3. **백업 권장**: 중요한 설정 변경 전 백업

## 📊 설정 유효성 검사

### 검사 항목
- 필수 시스템 경로 존재 여부
- 시간 형식 유효성
- 웹사이트 URL 형식
- 권한 설정 유효성

### 오류 처리
```python
# 설정 검증
errors = config.validate_config()
if errors:
    print("설정 오류:", errors)
else:
    print("모든 설정이 유효합니다")
```

## 🔒 보안 고려사항

### 설정 파일 권한
```bash
# 설정 파일 권한 설정
chmod 600 config.json
chown root:wheel config.json
```

### 민감한 정보
- 시스템 경로 정보
- 보안 설정
- 사용자 정의 웹사이트 목록

## 📞 지원

### 문제 해결
1. **설정 파일 손상**: 기본값으로 초기화
2. **권한 문제**: 파일 권한 확인
3. **연동 오류**: 경로 설정 확인

### 로그 확인
```bash
# 설정 관련 로그
grep "config" /var/log/FocusTimer/focus_timer.log
```

## 🎯 사용 팁

1. **정기적 백업**: 설정 변경 전 백업
2. **단계적 변경**: 한 번에 하나씩 변경
3. **테스트 환경**: 변경 전 테스트
4. **문서화**: 커스텀 설정 문서화