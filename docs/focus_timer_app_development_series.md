# 🍎 스크립트에서 네이티브 앱으로: FocusTimer.app 개발기 (Part 1 앱 번들 개발편)

## 📋 목차

- [개발 동기](#-개발-동기)
- [앱 번들 아키텍처 설계](#-앱-번들-아키텍처-설계)
- [PyInstaller 통합의 도전](#-pyinstaller-통합의-도전)
- [모듈 Import 시스템 혁신](#-모듈-import-시스템-혁신)
- [GUI 통합 및 최적화](#-gui-통합-및-최적화)
- [백그라운드 서비스 구현](#-백그라운드-서비스-구현)
- [배포 및 설치 시스템](#-배포-및-설치-시스템)
- [결론 및 다음 편 예고](#-결론-및-다음-편-예고)

---

## 🎯 개발 동기

### **스크립트 기반의 한계점**

이전 버전의 FocusTimer는 Python 스크립트로 구현되어 있었습니다. 이는 개발과 테스트에는 편리했지만, 실제 사용자에게 배포할 때 여러 한계점이 드러났습니다:

#### **문제점 1: 의존성 관리의 복잡성**

```bash
# 사용자가 직접 해야 하는 작업들
pip install tkinter
pip install psutil
pip install pygame
pip install numpy
# ... 수십 개의 의존성 패키지들
```

#### **문제점 2: Python 환경 설정의 번거로움**

- Python 3.7+ 설치 필요
- 가상환경 설정 필요
- PATH 환경변수 설정 필요
- 권한 문제 해결 필요

#### **문제점 3: 배포의 어려움**

- 소스 코드 노출
- 사용자별 환경 차이로 인한 호환성 문제
- 업데이트 시 재설치 필요
- 전문 지식이 필요한 설치 과정

### **해결 방향**

> **macOS 네이티브 앱 번들(.app)로 완전한 독립 실행 파일 개발**

---

## 🏗️ 앱 번들 아키텍처 설계

### **1단계: 앱 번들 구조 설계**

#### **표준 macOS 앱 번들 구조**

```
FocusTimer.app/
├── Contents/
│   ├── Info.plist                    # 앱 메타데이터
│   ├── MacOS/
│   │   ├── FocusTimer               # 메인 GUI 실행 파일
│   │   ├── FocusTimerCLI            # CLI 도구
│   │   └── FocusTimerHelper         # 백그라운드 서비스
│   └── Resources/
│       ├── FocusTimer.icns          # 앱 아이콘
│       ├── config.json              # 설정 파일
│       ├── com.focustimer.helper.plist  # LaunchAgent 설정
│       ├── algorithm_tab.py         # 알고리즘 시스템
│       ├── gui_algorithm_manager.py # GUI 관리자
│       ├── integrated_focus_timer.py # 통합 타이머
│       └── user_data/               # 사용자 데이터
```

#### **Info.plist 설계**

```xml
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

    <key>CFBundleVersion</key>
    <string>2.0.0</string>

    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>

    <key>NSHighResolutionCapable</key>
    <true/>

    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>

    <key>NSAppleEventsUsageDescription</key>
    <string>FocusTimer는 브라우저 제어를 위해 Apple Events에 접근합니다.</string>

    <key>NSSystemAdministrationUsageDescription</key>
    <string>FocusTimer는 시스템 레벨 보호를 위해 관리자 권한이 필요합니다.</string>
</dict>
</plist>
```

### **2단계: 실행 파일 분리 설계**

#### **메인 GUI 애플리케이션 (FocusTimer)**

```python
# 메인 GUI의 역할
class FocusTimerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_macos_style()
        self.setup_gui()
        self.integrate_algorithm_system()

    def setup_macos_style(self):
        """macOS 네이티브 스타일 적용"""
        # macOS 특화 UI 스타일링
        # 네이티브 메뉴바 통합
        # 시스템 알림 통합

    def integrate_algorithm_system(self):
        """알고리즘 시스템을 GUI에 통합"""
        # algorithm_tab.py를 notebook에 삽입
        # 실시간 데이터 연동
        # 사용자 상호작용 처리
```

#### **CLI 도구 (FocusTimerCLI)**

```python
# CLI의 역할
class FocusTimerCLI:
    def __init__(self):
        self.setup_argument_parser()

    def setup_argument_parser(self):
        """명령줄 인수 파서 설정"""
        parser = argparse.ArgumentParser(description='FocusTimer CLI')
        parser.add_argument('--start', action='store_true', help='집중 모드 시작')
        parser.add_argument('--stop', action='store_true', help='집중 모드 중지')
        parser.add_argument('--status', action='store_true', help='현재 상태 확인')
        parser.add_argument('--config', help='설정 파일 경로')

    def run(self):
        """CLI 실행"""
        args = self.parser.parse_args()

        if args.start:
            self.start_focus_mode()
        elif args.stop:
            self.stop_focus_mode()
        elif args.status:
            self.show_status()
```

#### **백그라운드 서비스 (FocusTimerHelper)**

```python
# 백그라운드 서비스의 역할
class FocusTimerHelper:
    def __init__(self):
        self.setup_launch_agent()
        self.start_monitoring()

    def setup_launch_agent(self):
        """LaunchAgent 설정"""
        # com.focustimer.helper.plist 생성
        # 시스템 부팅 시 자동 시작 설정
        # 백그라운드 실행 설정

    def start_monitoring(self):
        """시스템 모니터링 시작"""
        # hosts 파일 변경 감지
        # 자동 복구 메커니즘
        # 로그 기록
```

---

## 🔧 PyInstaller 통합의 도전

### **1단계: PyInstaller 설정 파일 설계**

#### **FocusTimerStandalone.spec 파일**

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 메인 GUI 애플리케이션
a = Analysis(
    ['integrated_focus_timer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('algorithm_tab.py', '.'),
        ('gui_algorithm_manager.py', '.'),
        ('advanced_challenge_system.py', '.'),
        ('user_progress_tracker.py', '.'),
        ('problem_data_structures.py', '.'),
        ('config.json', '.'),
        ('FocusTimer.icns', '.'),
        ('com.focustimer.helper.plist', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'psutil',
        'pygame',
        'numpy',
        'sqlite3',
        'json',
        'threading',
        'subprocess',
        'platform',
        'datetime',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FocusTimer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 모드
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='FocusTimer.icns',
)
```

### **2단계: 모듈 Import 문제 해결**

#### **문제: 앱 번들 내 모듈 Import 실패**

```python
# 문제 상황
import algorithm_tab  # ❌ ImportError: No module named 'algorithm_tab'
import gui_algorithm_manager  # ❌ ImportError: No module named 'gui_algorithm_manager'
```

#### **해결책: SafeImporter 시스템 개발**

```python
class SafeImporter:
    """안전한 모듈 import를 위한 클래스"""

    def __init__(self, package_root: Path):
        self.package_root = package_root
        self._setup_paths()

    def _setup_paths(self):
        """Python 경로 설정"""
        # Resources 폴더를 Python 경로에 추가
        if str(self.package_root) not in sys.path:
            sys.path.insert(0, str(self.package_root))

        # 상위 디렉토리도 추가 (절대경로 import를 위해)
        parent_dir = self.package_root.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))

    def import_module(self, module_name: str, fallback_names: List[str] = None) -> Optional[Any]:
        """안전한 모듈 import"""
        # 1. 절대경로 import 시도
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"✅ 절대경로 import 성공: {module_name}")
            return module
        except ImportError as e:
            print(f"⚠️ 절대경로 import 실패: {module_name} - {e}")

        # 2. 상대경로 import 시도
        try:
            module = __import__(module_name.split('.')[-1], fromlist=['*'])
            print(f"✅ 상대경로 import 성공: {module_name}")
            return module
        except ImportError as e:
            print(f"⚠️ 상대경로 import 실패: {module_name} - {e}")

        # 3. 대체 모듈들 시도
        if fallback_names:
            for fallback_name in fallback_names:
                try:
                    module = __import__(fallback_name, fromlist=['*'])
                    print(f"✅ 대체 import 성공: {fallback_name}")
                    return module
                except ImportError as e:
                    print(f"⚠️ 대체 import 실패: {fallback_name} - {e}")

        print(f"❌ 모든 import 시도 실패: {module_name}")
        return None
```

### **3단계: import_utils.py 시스템**

#### **자동 Import 관리 시스템**

```python
def setup_focustimer_resources() -> SafeImporter:
    """FocusTimer Resources 패키지 설정"""
    # 현재 파일의 위치를 기준으로 Resources 폴더 찾기
    current_file = Path(__file__)
    resources_path = current_file.parent

    print(f"📦 FocusTimer Resources 설정 중...")
    print(f"📁 Resources 경로: {resources_path}")

    # SafeImporter 인스턴스 생성
    importer = SafeImporter(resources_path)

    return importer

def get_importer() -> SafeImporter:
    """전역 SafeImporter 인스턴스 반환"""
    global _importer
    if _importer is None:
        _importer = setup_focustimer_resources()
    return _importer

def safe_import(module_name: str) -> Optional[Any]:
    """안전한 모듈 import"""
    importer = get_importer()
    return importer.import_module(module_name)
```

---

## 🎨 GUI 통합 및 최적화

### **1단계: macOS 네이티브 스타일 적용**

#### **macOS 특화 UI 스타일링**

```python
def setup_macos_style(self):
    """macOS 네이티브 스타일 적용"""
    if platform.system() == "Darwin":
        # macOS 네이티브 메뉴바 설정
        self.root.createcommand('tk::mac::Quit', self.on_closing)
        self.root.createcommand('tk::mac::About', self.show_about)
        self.root.createcommand('tk::mac::OpenPreferences', self.show_preferences)

        # macOS 네이티브 스타일 적용
        style = ttk.Style()
        style.theme_use('aqua')  # macOS 네이티브 테마

        # 고해상도 디스플레이 지원
        self.root.tk.call('tk', 'scaling', 2.0)

        # macOS 네이티브 창 스타일
        self.root.tk.call('tk', 'unsupported1', '::tk::unsupported::MacWindowStyle', 'style', self.root, 'document', 'closeBox')
```

#### **알고리즘 탭 통합**

```python
def integrate_algorithm_system(self):
    """알고리즘 시스템을 GUI에 통합"""
    try:
        # SafeImporter를 통한 안전한 import
        from import_utils import get_importer
        importer = get_importer()

        # 알고리즘 모듈들 import
        algorithm_modules = importer.import_algorithm_modules()

        if 'algorithm_tab' in algorithm_modules:
            # 알고리즘 탭을 notebook에 삽입
            algorithm_tab = algorithm_modules['algorithm_tab'].AlgorithmTab(self.notebook)
            self.notebook.add(algorithm_tab.frame, text="🧮 알고리즘")
            print("✅ 알고리즘 탭이 성공적으로 통합되었습니다.")
        else:
            print("⚠️ 알고리즘 탭 로드 실패")

    except Exception as e:
        print(f"❌ 알고리즘 시스템 통합 실패: {e}")
```

### **2단계: 메모리 최적화 시스템**

#### **메모리 모니터링 시스템**

```python
class MemoryMonitor:
    """메모리 사용량 모니터링 및 최적화"""

    def __init__(self):
        self.memory_threshold = 100 * 1024 * 1024  # 100MB
        self.optimization_callbacks = []
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """메모리 모니터링 시작"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self):
        """메모리 모니터링 루프"""
        while self.monitoring:
            try:
                memory_usage = self.get_memory_usage()

                if memory_usage > self.memory_threshold:
                    print(f"⚠️ 메모리 사용량 높음: {memory_usage / 1024 / 1024:.1f}MB")
                    self._trigger_optimization()

                time.sleep(30)  # 30초마다 체크

            except Exception as e:
                print(f"⚠️ 메모리 모니터링 오류: {e}")
                time.sleep(60)

    def get_memory_usage(self) -> float:
        """현재 프로세스의 메모리 사용량 반환 (bytes)"""
        try:
            if psutil:
                process = psutil.Process()
                return process.memory_info().rss
            else:
                return 0
        except:
            return 0
```

#### **백그라운드 작업 최적화**

```python
class BackgroundTaskOptimizer:
    """백그라운드 작업 최적화"""

    def __init__(self):
        self.task_queue = queue.PriorityQueue()
        self.workers = []
        self.max_workers = 3
        self.running = False

    def start_workers(self):
        """워커 스레드 시작"""
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self, worker_id: int):
        """워커 스레드 루프"""
        while self.running:
            try:
                # 우선순위가 높은 작업부터 처리
                priority, task_id, task_func, callback = self.task_queue.get(timeout=1)
                task_func()

                if callback:
                    callback()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ 워커 {worker_id} 오류: {e}")
```

### **3단계: 데이터베이스 최적화**

#### **SQLite 데이터베이스 최적화**

```python
class DatabaseOptimizer:
    """데이터베이스 성능 최적화"""

    def __init__(self, db_path: str = "focus_timer.db"):
        self.db_path = db_path
        self.connection_cache = {}
        self.query_cache = {}
        self.initialize_database()

    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.execute("PRAGMA synchronous=NORMAL")  # 성능 최적화
                conn.execute("PRAGMA cache_size=10000")  # 캐시 크기 증가
                conn.execute("PRAGMA temp_store=MEMORY")  # 임시 테이블을 메모리에 저장

                self._create_tables(conn)

        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")

    def _create_tables(self, conn):
        """테이블 생성"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER,
                problem_id TEXT,
                status TEXT DEFAULT 'active'
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id TEXT NOT NULL,
                status TEXT NOT NULL,
                solved_at TEXT,
                attempts INTEGER DEFAULT 0
            )
        """)

        conn.commit()
```

---

## 🔄 백그라운드 서비스 구현

### **1단계: LaunchAgent 설정**

#### **com.focustimer.helper.plist 파일**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.helper</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Applications/FocusTimer.app/Contents/MacOS/FocusTimerHelper</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/focustimer_helper.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/focustimer_helper_error.log</string>

    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
```

### **2단계: 백그라운드 서비스 구현**

#### **FocusTimerHelper 서비스**

```python
class FocusTimerHelper:
    """백그라운드 서비스"""

    def __init__(self):
        self.setup_logging()
        self.setup_launch_agent()
        self.start_monitoring()

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/tmp/focustimer_helper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_launch_agent(self):
        """LaunchAgent 설정"""
        try:
            # LaunchAgent plist 파일 복사
            plist_source = os.path.join(os.path.dirname(__file__), 'com.focustimer.helper.plist')
            plist_dest = os.path.expanduser('~/Library/LaunchAgents/com.focustimer.helper.plist')

            # LaunchAgents 디렉토리 생성
            os.makedirs(os.path.dirname(plist_dest), exist_ok=True)

            # plist 파일 복사
            shutil.copy2(plist_source, plist_dest)

            # LaunchAgent 로드
            subprocess.run(['launchctl', 'load', plist_dest], check=True)

            self.logger.info("✅ LaunchAgent 설정 완료")

        except Exception as e:
            self.logger.error(f"❌ LaunchAgent 설정 실패: {e}")

    def start_monitoring(self):
        """시스템 모니터링 시작"""
        self.logger.info("🔄 시스템 모니터링 시작")

        # hosts 파일 모니터링
        self.monitor_hosts_file()

        # 메모리 사용량 모니터링
        self.monitor_memory_usage()

        # 자동 복구 메커니즘
        self.start_auto_recovery()

    def monitor_hosts_file(self):
        """hosts 파일 변경 감지"""
        hosts_path = "/etc/hosts"
        last_modified = os.path.getmtime(hosts_path)

        while True:
            try:
                current_modified = os.path.getmtime(hosts_path)

                if current_modified != last_modified:
                    self.logger.warning("⚠️ hosts 파일 변경 감지")
                    self.restore_hosts_file()
                    last_modified = current_modified

                time.sleep(5)  # 5초마다 체크

            except Exception as e:
                self.logger.error(f"❌ hosts 파일 모니터링 오류: {e}")
                time.sleep(30)

    def restore_hosts_file(self):
        """hosts 파일 복구"""
        try:
            backup_path = os.path.expanduser("~/hosts_backup")

            if os.path.exists(backup_path):
                subprocess.run(['sudo', 'cp', backup_path, '/etc/hosts'], check=True)
                self.logger.info("✅ hosts 파일 복구 완료")
            else:
                self.logger.warning("⚠️ 백업 파일이 없습니다")

        except Exception as e:
            self.logger.error(f"❌ hosts 파일 복구 실패: {e}")
```

### **3단계: 자동 재시작 시스템**

#### **오류 감지 및 자동 재시작**

```python
def start_auto_recovery(self):
    """자동 복구 시스템 시작"""
    def recovery_loop():
        while True:
            try:
                # 메인 프로세스 상태 확인
                if not self.check_main_process():
                    self.logger.warning("⚠️ 메인 프로세스 비정상 종료 감지")
                    self.restart_main_process()

                # 메모리 사용량 확인
                memory_usage = self.get_memory_usage()
                if memory_usage > 500 * 1024 * 1024:  # 500MB
                    self.logger.warning("⚠️ 메모리 사용량 과다")
                    self.optimize_memory()

                time.sleep(60)  # 1분마다 체크

            except Exception as e:
                self.logger.error(f"❌ 자동 복구 루프 오류: {e}")
                time.sleep(300)  # 5분 대기 후 재시도

    recovery_thread = threading.Thread(target=recovery_loop, daemon=True)
    recovery_thread.start()
```

---

## 📦 배포 및 설치 시스템

### **1단계: 앱 번들 생성**

#### **PyInstaller 빌드 스크립트**

```bash
#!/bin/bash
# build_app.sh

echo "🚀 FocusTimer.app 빌드 시작..."

# 1. 기존 빌드 정리
rm -rf build/
rm -rf dist/

# 2. PyInstaller로 앱 번들 생성
pyinstaller FocusTimerStandalone.spec

# 3. 앱 번들 최적화
echo "📦 앱 번들 최적화 중..."

# 불필요한 파일 제거
find dist/FocusTimer.app -name "*.pyc" -delete
find dist/FocusTimer.app -name "__pycache__" -type d -exec rm -rf {} +

# 4. 권한 설정
chmod +x dist/FocusTimer.app/Contents/MacOS/FocusTimer
chmod +x dist/FocusTimer.app/Contents/MacOS/FocusTimerCLI
chmod +x dist/FocusTimer.app/Contents/MacOS/FocusTimerHelper

# 5. 앱 번들 검증
echo "🔍 앱 번들 검증 중..."
codesign --verify --deep --strict dist/FocusTimer.app

echo "✅ FocusTimer.app 빌드 완료!"
```

### **2단계: 설치 스크립트**

#### **install_focustimer_app.sh**

```bash
#!/bin/bash
# install_focustimer_app.sh

echo "🚀 FocusTimer.app 설치 시작..."

# 1. 관리자 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "❌ 관리자 권한이 필요합니다. sudo를 사용해주세요."
    exit 1
fi

# 2. 기존 설치 제거
if [ -d "/Applications/FocusTimer.app" ]; then
    echo "🗑️ 기존 FocusTimer.app 제거 중..."
    rm -rf "/Applications/FocusTimer.app"
fi

# 3. 앱 번들 복사
echo "📦 FocusTimer.app 설치 중..."
cp -R "FocusTimer.app" "/Applications/"

# 4. 권한 설정
chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimer"
chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI"
chmod +x "/Applications/FocusTimer.app/Contents/MacOS/FocusTimerHelper"

# 5. LaunchAgent 설정
echo "🔄 백그라운드 서비스 설정 중..."
plist_source="/Applications/FocusTimer.app/Contents/Resources/com.focustimer.helper.plist"
plist_dest="$HOME/Library/LaunchAgents/com.focustimer.helper.plist"

# LaunchAgents 디렉토리 생성
mkdir -p "$HOME/Library/LaunchAgents"

# plist 파일 복사
cp "$plist_source" "$plist_dest"

# LaunchAgent 로드
launchctl load "$plist_dest"

# 6. hosts 파일 백업
if [ ! -f "$HOME/hosts_backup" ]; then
    echo "💾 hosts 파일 백업 중..."
    cp /etc/hosts "$HOME/hosts_backup"
fi

echo "✅ FocusTimer.app 설치 완료!"
echo "🎉 이제 Applications 폴더에서 FocusTimer.app을 실행할 수 있습니다."
```

### **3단계: 제거 스크립트**

#### **uninstall_focustimer_app.sh**

```bash
#!/bin/bash
# uninstall_focustimer_app.sh

echo "🗑️ FocusTimer.app 제거 시작..."

# 1. LaunchAgent 제거
echo "🔄 백그라운드 서비스 중지 중..."
plist_dest="$HOME/Library/LaunchAgents/com.focustimer.helper.plist"

if [ -f "$plist_dest" ]; then
    launchctl unload "$plist_dest"
    rm "$plist_dest"
fi

# 2. 앱 번들 제거
if [ -d "/Applications/FocusTimer.app" ]; then
    echo "📦 FocusTimer.app 제거 중..."
    rm -rf "/Applications/FocusTimer.app"
fi

# 3. 로그 파일 정리
echo "🧹 로그 파일 정리 중..."
rm -f /tmp/focustimer_helper.log
rm -f /tmp/focustimer_helper_error.log

# 4. 사용자 데이터 정리 (선택사항)
read -p "사용자 데이터도 삭제하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/Library/Application Support/FocusTimer"
    rm -f "$HOME/hosts_backup"
    rm -f "$HOME/focus_timer_state"
fi

echo "✅ FocusTimer.app 제거 완료!"
```

---

## 🎯 핵심 기술적 성과

### **1. 완전한 독립 실행 파일**

- ✅ **PyInstaller 통합**: 모든 의존성을 포함한 단일 실행 파일
- ✅ **크로스 플랫폼 호환성**: macOS 10.15+ 완전 지원
- ✅ **즉시 실행**: Python 설치나 가상환경 불필요
- ✅ **배포 용이성**: 앱 번들 형태로 간편한 배포

### **2. 안전한 모듈 Import 시스템**

- ✅ **SafeImporter**: 절대경로 → 상대경로 → 대체 모듈 순으로 안전한 import
- ✅ **자동 경로 설정**: Resources 폴더가 자동으로 Python 경로에 추가
- ✅ **오류 처리**: import 실패 시 자동으로 대체 방법 시도
- ✅ **모듈 가용성 확인**: 필요한 모듈들이 모두 로드되었는지 자동 확인

### **3. macOS 네이티브 통합**

- ✅ **네이티브 UI**: macOS Aqua 테마 완전 지원
- ✅ **시스템 메뉴바**: 네이티브 메뉴바 통합
- ✅ **고해상도 디스플레이**: Retina 디스플레이 완전 지원
- ✅ **시스템 알림**: macOS 네이티브 알림 시스템 활용

### **4. 백그라운드 서비스**

- ✅ **LaunchAgent**: 시스템 부팅 시 자동 시작
- ✅ **파일 모니터링**: hosts 파일 무단 수정 방지
- ✅ **자동 복구**: 오류 발생 시 자동 재시작
- ✅ **로그 시스템**: 상세한 시스템 이벤트 기록

### **5. 성능 최적화**

- ✅ **메모리 모니터링**: 실시간 메모리 사용량 추적
- ✅ **백그라운드 작업**: 우선순위 기반 작업 큐
- ✅ **데이터베이스 최적화**: SQLite WAL 모드 및 캐시 최적화
- ✅ **자동 정리**: 불필요한 리소스 자동 정리

---

## 💡 개발 과정에서의 교훈

### **1. 앱 번들 개발의 복잡성**

- **PyInstaller 한계**: 모든 의존성을 완벽하게 포함하는 것이 어려움
- **모듈 Import 문제**: 앱 번들 내에서의 상대경로 import 문제
- **macOS 권한**: 시스템 레벨 접근을 위한 권한 관리의 복잡성

### **2. 해결책의 진화**

- **SafeImporter 시스템**: 점진적으로 발전한 안전한 import 시스템
- **LaunchAgent 통합**: 백그라운드 서비스의 안정성 확보
- **성능 최적화**: 메모리 사용량과 응답성의 균형점 찾기

### **3. 사용자 경험 우선**

- **즉시 실행**: 설치 후 바로 사용 가능한 편의성
- **자동 설정**: 사용자가 신경 쓸 필요 없는 자동화
- **안정성**: 오류 발생 시 자동 복구 시스템

---

## 🎯 결론 및 다음 편 예고

스크립트에서 네이티브 앱으로의 변환을 통해 FocusTimer는 완전히 새로운 차원의 제품이 되었습니다. 이번 개발 과정에서:

- **완전한 독립 실행 파일**: Python 환경 설정 없이 즉시 실행 가능
- **macOS 네이티브 통합**: 시스템과 완벽하게 통합된 사용자 경험
- **백그라운드 서비스**: 지속적인 모니터링 및 자동 복구 시스템
- **성능 최적화**: 메모리 사용량과 응답성의 최적화
- **배포 용이성**: 앱 번들 형태로 간편한 배포 및 설치

이제 FocusTimer는 진정한 macOS 네이티브 앱으로서 사용자에게 최적의 경험을 제공할 수 있게 되었습니다! 🚀

---

## 📚 다음 편 예고

### **Part 2: 엔터프라이즈 기능 개발기**

- **웹 대시보드**: 원격 모니터링 및 제어 시스템
- **다중 사용자 지원**: 조직 내 여러 사용자 관리
- **고급 통계**: 사용 패턴 분석 및 리포트
- **API 통합**: 외부 시스템과의 연동
- **보안 강화**: 권한 관리 및 접근 제어

### **Part 3: 알고리즘 시스템 통합기**

- **알고리즘 탭**: GUI에 완전히 통합된 알고리즘 문제 시스템
- **실시간 문제 제공**: LeetCode, CodeForces 연동
- **진행도 추적**: 사용자의 문제 풀이 진행도 관리
- **학습 경로**: 개인화된 알고리즘 학습 경로 제공
- **성과 분석**: 문제 풀이 통계 및 성과 분석

### **Part 4: 성능 최적화 및 확장성**

- **메모리 최적화**: 대용량 데이터 처리 최적화
- **데이터베이스 최적화**: SQLite 성능 튜닝
- **백그라운드 작업**: 비동기 작업 처리 시스템
- **크로스 플랫폼**: Windows, Linux 지원 확장
- **모바일 연동**: iOS, Android 앱 개발

---

**#FocusTimer #macOS #앱개발 #PyInstaller #네이티브앱 #백그라운드서비스 #성능최적화**
