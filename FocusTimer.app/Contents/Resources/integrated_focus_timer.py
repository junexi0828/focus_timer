"""
통합 FocusTimer - 타이머 + 알고리즘 문제 풀이 시스템

이 모듈은 기존 FocusTimer의 타이머 기능과
새로운 알고리즘 문제 풀이 시스템을 통합한 GUI를 제공합니다.
집중 시간 동안 다른 프로그램을 차단하고,
프로그램 종료 시 알고리즘 문제를 해결해야만 종료할 수 있습니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import time
import threading
import subprocess
try:
    import psutil
except ImportError:
    psutil = None
import platform
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import queue
import sys
import gc
import weakref
import sqlite3
from collections import deque
import logging
try:
    import winsound  # Windows 소리
except ImportError:
    winsound = None

try:
    import pygame   # 크로스 플랫폼 소리
except ImportError:
    pygame = None

try:
    import numpy as np
except ImportError:
    np = None

# macOS 특정 임포트
if platform.system() == "Darwin":
    try:
        # macOS 관련 모듈들은 선택적으로 임포트
        pass
    except ImportError:
        pass

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('focus_timer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 알고리즘 시스템 임포트
try:
    from advanced_challenge_system import (
        AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
        CodeTestResult, PerformanceMetrics
    )
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
    from gui_algorithm_manager import MockProblemProvider
except ImportError:
    # 상대 경로로 임포트 시도
    try:
        from .advanced_challenge_system import (
            AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
            CodeTestResult, PerformanceMetrics
        )
        from .problem_data_structures import (
            AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
        )
        from .gui_algorithm_manager import MockProblemProvider
    except ImportError:
        # 절대 경로로 임포트 시도
        import sys
        sys.path.append(os.path.dirname(__file__))
        from advanced_challenge_system import (
            AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
            CodeTestResult, PerformanceMetrics
        )
        from problem_data_structures import (
            AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
        )
        from gui_algorithm_manager import MockProblemProvider


class MemoryMonitor:
    """메모리 사용량 모니터링 클래스"""

    def __init__(self):
        self.memory_history = deque(maxlen=100)  # 최근 100개 메모리 측정값
        self.memory_threshold = 0.8  # 80% 메모리 사용량 임계값
        self.monitoring_active = False
        self.monitor_thread = None
        self.optimization_callbacks = []

    def start_monitoring(self):
        """메모리 모니터링 시작"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("메모리 모니터링 시작")

    def stop_monitoring(self):
        """메모리 모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("메모리 모니터링 중지")

    def _monitor_loop(self):
        """메모리 모니터링 루프"""
        while self.monitoring_active:
            try:
                memory_usage = self.get_memory_usage()
                self.memory_history.append(memory_usage)

                # 메모리 사용량이 임계값을 초과하면 최적화 실행
                if memory_usage > self.memory_threshold:
                    self._trigger_optimization()

                time.sleep(30)  # 30초마다 체크

            except Exception as e:
                logger.error(f"메모리 모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (0.0 ~ 1.0)"""
        try:
            if psutil:
                memory = psutil.virtual_memory()
                return memory.percent / 100.0
            else:
                # psutil이 없을 경우 간단한 추정
                return 0.5  # 기본값
        except Exception as e:
            logger.error(f"메모리 사용량 측정 오류: {e}")
            return 0.0

    def get_memory_stats(self) -> Dict[str, Any]:
        """메모리 통계 반환"""
        try:
            if psutil:
                memory = psutil.virtual_memory()
                return {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'average': np.mean(list(self.memory_history)) if self.memory_history and np else 0.0
                }
            else:
                return {'error': 'psutil not available'}
        except Exception as e:
            logger.error(f"메모리 통계 오류: {e}")
            return {'error': str(e)}

    def add_optimization_callback(self, callback):
        """메모리 최적화 콜백 추가"""
        self.optimization_callbacks.append(callback)

    def _trigger_optimization(self):
        """메모리 최적화 트리거"""
        logger.warning(f"메모리 사용량 임계값 초과: {self.get_memory_usage():.2%}")
        for callback in self.optimization_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"최적화 콜백 오류: {e}")


class BackgroundTaskOptimizer:
    """백그라운드 작업 최적화 클래스"""

    def __init__(self):
        self.task_queue = queue.PriorityQueue()
        self.worker_threads = []
        self.max_workers = 3
        self.running = False
        self.task_results = {}
        self.task_callbacks = {}

    def start_workers(self):
        """워커 스레드 시작"""
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.worker_threads.append(worker)
        logger.info(f"백그라운드 워커 {self.max_workers}개 시작")

    def stop_workers(self):
        """워커 스레드 중지"""
        self.running = False
        for worker in self.worker_threads:
            worker.join(timeout=1)
        self.worker_threads.clear()
        logger.info("백그라운드 워커 중지")

    def add_task(self, task_id: str, task_func, priority: int = 5, callback=None):
        """작업 추가 (우선순위: 1=높음, 10=낮음)"""
        self.task_queue.put((priority, task_id, task_func))
        if callback:
            self.task_callbacks[task_id] = callback
        logger.debug(f"백그라운드 작업 추가: {task_id} (우선순위: {priority})")

    def _worker_loop(self, worker_id: int):
        """워커 스레드 루프"""
        while self.running:
            try:
                # 작업 큐에서 작업 가져오기 (1초 타임아웃)
                priority, task_id, task_func = self.task_queue.get(timeout=1)

                logger.debug(f"워커 {worker_id}: 작업 {task_id} 실행")
                start_time = time.time()

                # 작업 실행
                result = task_func()
                execution_time = time.time() - start_time

                # 결과 저장
                self.task_results[task_id] = {
                    'result': result,
                    'execution_time': execution_time,
                    'worker_id': worker_id,
                    'completed_at': datetime.now()
                }

                # 콜백 실행
                if task_id in self.task_callbacks:
                    try:
                        self.task_callbacks[task_id](result)
                    except Exception as e:
                        logger.error(f"작업 콜백 오류 {task_id}: {e}")

                logger.debug(f"워커 {worker_id}: 작업 {task_id} 완료 ({execution_time:.2f}초)")

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"워커 {worker_id} 오류: {e}")
                time.sleep(1)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 반환"""
        return self.task_results.get(task_id)

    def get_queue_size(self) -> int:
        """큐 크기 반환"""
        return self.task_queue.qsize()


class DatabaseOptimizer:
    """데이터베이스 쿼리 최적화 클래스"""

    def __init__(self, db_path: str = "focus_timer.db"):
        self.db_path = db_path
        self.connection = None
        self.query_cache = {}
        self.cache_size = 100
        self.query_stats = {}
        self.connection_pool = []
        self.max_connections = 5

    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            self.connection.execute("PRAGMA synchronous=NORMAL")  # 성능 최적화
            self.connection.execute("PRAGMA cache_size=10000")  # 캐시 크기 증가
            self.connection.execute("PRAGMA temp_store=MEMORY")  # 임시 테이블을 메모리에 저장

            # 테이블 생성
            self._create_tables()
            logger.info("데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")

    def _create_tables(self):
        """테이블 생성"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER NOT NULL,
                problem_id TEXT,
                completed BOOLEAN DEFAULT FALSE,
                interruptions INTEGER DEFAULT 0,
                actual_focus_time REAL DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id TEXT NOT NULL,
                submission_time TEXT NOT NULL,
                status TEXT NOT NULL,
                execution_time REAL,
                memory_used INTEGER,
                code TEXT,
                UNIQUE(problem_id, submission_time)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                memory_usage REAL,
                cpu_usage REAL,
                query_count INTEGER DEFAULT 0,
                cache_hit_rate REAL DEFAULT 0
            )
            """
        ]

        for table_sql in tables:
            self.connection.execute(table_sql)
        self.connection.commit()

    def get_connection(self):
        """데이터베이스 연결 반환"""
        if not self.connection:
            self.initialize_database()
        return self.connection

    def execute_query(self, query: str, params: tuple = (), cache: bool = True) -> List[tuple]:
        """쿼리 실행 (캐시 지원)"""
        start_time = time.time()

        # 캐시 확인
        cache_key = f"{query}_{hash(params)}"
        if cache and cache_key in self.query_cache:
            self.query_stats[cache_key] = self.query_stats.get(cache_key, 0) + 1
            logger.debug(f"캐시 히트: {cache_key}")
            return self.query_cache[cache_key]

        try:
            cursor = self.get_connection().cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()

            # 캐시에 저장
            if cache and len(self.query_cache) < self.cache_size:
                self.query_cache[cache_key] = result

            # 통계 업데이트
            execution_time = time.time() - start_time
            self.query_stats[cache_key] = {
                'execution_time': execution_time,
                'result_count': len(result),
                'cache_hits': 0
            }

            logger.debug(f"쿼리 실행: {query[:50]}... ({execution_time:.3f}초)")
            return result

        except Exception as e:
            logger.error(f"쿼리 실행 오류: {e}")
            return []

    def batch_insert(self, table: str, data: List[tuple], batch_size: int = 1000):
        """배치 삽입 (성능 최적화)"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                placeholders = ','.join(['?' * len(batch[0])])
                query = f"INSERT INTO {table} VALUES ({placeholders})"

                cursor.executemany(query, batch)

            connection.commit()
            logger.info(f"배치 삽입 완료: {table} ({len(data)}개 레코드)")

        except Exception as e:
            logger.error(f"배치 삽입 오류: {e}")

    def optimize_database(self):
        """데이터베이스 최적화"""
        try:
            connection = self.get_connection()

            # 인덱스 생성
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_focus_sessions_start_time ON focus_sessions(start_time)",
                "CREATE INDEX IF NOT EXISTS idx_user_progress_problem_id ON user_progress(problem_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_progress_submission_time ON user_progress(submission_time)",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp)"
            ]

            for index_sql in indexes:
                connection.execute(index_sql)

            # VACUUM 실행 (데이터베이스 정리)
            connection.execute("VACUUM")
            connection.commit()

            # 캐시 정리
            self._cleanup_cache()

            logger.info("데이터베이스 최적화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 최적화 오류: {e}")

    def _cleanup_cache(self):
        """캐시 정리"""
        if len(self.query_cache) > self.cache_size * 0.8:
            # 가장 오래된 캐시 항목들 제거
            items_to_remove = len(self.query_cache) - int(self.cache_size * 0.5)
            for _ in range(items_to_remove):
                if self.query_cache:
                    self.query_cache.popitem()

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            # 테이블 크기 조회
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            stats = {
                'cache_size': len(self.query_cache),
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'tables': {}
            }

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats['tables'][table_name] = count

            return stats

        except Exception as e:
            logger.error(f"성능 통계 조회 오류: {e}")
            return {'error': str(e)}

    def _calculate_cache_hit_rate(self) -> float:
        """캐시 히트율 계산"""
        total_queries = sum(stats.get('cache_hits', 0) for stats in self.query_stats.values())
        total_executions = len(self.query_stats)

        if total_executions == 0:
            return 0.0
        return total_queries / total_executions

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            self.connection = None


class NotificationBanner:
    """배너 알림 클래스"""

    def __init__(self, parent):
        self.parent = parent
        self.banner_window = None
        self.notification_queue = queue.Queue()
        self.notification_thread = None
        self.is_running = False

        # 소리 시스템 초기화
        self.init_sound_system()

    def init_sound_system(self):
        """소리 시스템 초기화"""
        try:
            if pygame:
                pygame.mixer.init()
                # 기본 알림음 생성 (비프음)
                self.create_beep_sound()
        except Exception as e:
            print(f"소리 시스템 초기화 류: {e}")

    def create_beep_sound(self):
        """비프음 생성"""
        try:
            if pygame:
                # 간단한 비프음 생성
                sample_rate = 44100
                duration = 0.5  # 0.5초
                frequency = 800  # 800Hz

                # 사인파 생성
                import numpy as np
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sin(2 * np.pi * frequency * t)

                # pygame 사운드로 변환
                wave = (wave * 32767).astype(np.int16)
                sound_array = pygame.sndarray.make_sound(wave)
                self.beep_sound = sound_array
        except Exception as e:
            print(f"비프음 생성 오류: {e}")
            self.beep_sound = None

    def start_notification_system(self):
        """알림 시스템 시작"""
        self.is_running = True
        self.notification_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.notification_thread.start()

    def stop_notification_system(self):
        """알림 시스템 중지"""
        self.is_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1)

    def _notification_worker(self):
        """알림 워커 스레드"""
        while self.is_running:
            try:
                # 알림 큐에서 메시지 가져오기
                notification = self.notification_queue.get(timeout=1)
                if notification:
                    self._show_banner(notification)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"알림 워커 오류: {e}")

    def show_notification(self, title: str, message: str, notification_type: str = "info", duration: int = 5):
        """알림 표시"""
        notification = {
            'title': title,
            'message': message,
            'type': notification_type,
            'duration': duration
        }
        self.notification_queue.put(notification)

    def _show_banner(self, notification: dict):
        """배너 창 표시"""
        try:
            # 기존 배너가 있으면 제거
            if self.banner_window:
                try:
                    self.banner_window.destroy()
                except:
                    pass

            # 새 배너 창 생성
            self.banner_window = tk.Toplevel()
            self.banner_window.title("FocusTimer 알림")

            # 창 설정
            self.banner_window.geometry("400x150")
            self.banner_window.attributes('-topmost', True)
            self.banner_window.overrideredirect(True)  # 타이틀바 제거

            # 화면 우상단에 배치
            screen_width = self.banner_window.winfo_screenwidth()
            screen_height = self.banner_window.winfo_screenheight()
            x = screen_width - 420
            y = 50
            self.banner_window.geometry(f"400x150+{x}+{y}")

            # 배경색 설정 (알림 타입에 따라)
            bg_color = {
                'info': '#4CAF50',      # 초록색
                'warning': '#FF9800',   # 주황색
                'error': '#F44336',     # 빨간색
                'success': '#2196F3'    # 파란색
            }.get(notification['type'], '#4CAF50')

            self.banner_window.configure(bg=bg_color)

            # 제목
            title_label = tk.Label(
                self.banner_window,
                text=notification['title'],
                font=('Arial', 14, 'bold'),
                bg=bg_color,
                fg='white'
            )
            title_label.pack(pady=(20, 10))

            # 메시지
            message_label = tk.Label(
                self.banner_window,
                text=notification['message'],
                font=('Arial', 11),
                bg=bg_color,
                fg='white',
                wraplength=350
            )
            message_label.pack(pady=(0, 20))

            # 닫기 버튼
            close_button = tk.Button(
                self.banner_window,
                text="닫기",
                command=self.banner_window.destroy,
                bg='white',
                fg=bg_color,
                font=('Arial', 10, 'bold'),
                relief='flat',
                padx=20
            )
            close_button.pack(pady=(0, 15))

            # 소리 재생
            self._play_notification_sound()

            # 자동 닫기 타이머
            self.banner_window.after(notification['duration'] * 1000, self.banner_window.destroy)

            # 애니메이션 효과 (슬라이드 인)
            self._animate_banner_in()

        except Exception as e:
            print(f"배너 표시 오류: {e}")

    def _animate_banner_in(self):
        """배너 슬라이드 인 애니메이션"""
        try:
            if not self.banner_window:
                return

            # 초기 위치 (화면 밖)
            screen_width = self.banner_window.winfo_screenwidth()
            x = screen_width
            y = 50
            self.banner_window.geometry(f"400x150+{x}+{y}")

            # 목표 위치
            target_x = screen_width - 420

            # 애니메이션
            def animate():
                nonlocal x
                if x > target_x:
                    x -= 20
                    self.banner_window.geometry(f"400x150+{x}+{y}")
                    self.banner_window.after(10, animate)

            animate()

        except Exception as e:
            print(f"애니메이션 오류: {e}")

    def _play_notification_sound(self):
        """알림 소리 재생"""
        try:
            # Windows 소리
            if winsound:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            # pygame 소리
            elif pygame and hasattr(self, 'beep_sound') and self.beep_sound:
                self.beep_sound.play()

            # macOS 소리
            elif platform.system() == "Darwin":
                os.system("afplay /System/Library/Sounds/Glass.aiff")

            # Linux 소리
            elif platform.system() == "Linux":
                os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga")

        except Exception as e:
            print(f"소리 재생 오류: {e}")


class FocusSession:
    """포커스 세션 추적 클래스"""

    def __init__(self, start_time: datetime, duration: int, problem_id: Optional[str] = None):
        self.start_time = start_time
        self.duration = duration
        self.problem_id = problem_id
        self.completed = False
        self.break_taken = False
        self.interruptions = 0
        self.actual_focus_time = 0
        self.end_time = None

    def complete(self, end_time: datetime):
        """세션 완료"""
        self.end_time = end_time
        self.completed = True
        self.actual_focus_time = (end_time - self.start_time).total_seconds()

    def add_interruption(self):
        """방해 횟수 증가"""
        self.interruptions += 1


class ApplicationBlocker:
    """애플리케이션 차단 관리자"""

    def __init__(self):
        self.blocked_apps = [
            #"Safari", "Chrome", "Firefox", "Opera", "Edge",  # 브라우저
            "Messages", "Mail", "Discord", "Telegram",  # 메신저
            "YouTube", "Netflix", "Spotify", "iTunes",  # 엔터테인먼트
            "Facebook", "Instagram", "Twitter", "TikTok",  # 소셜미디어
            "Steam", "Battle.net", "Epic Games",  # 게임
            #"Finder", "Terminal", "Activity Monitor"  # 시스템 도구
        ]
        self.blocking_active = False
        self.blocking_thread = None
        self.overlay_window = None
        self.click_blocking = False
        self.parent_window = None

    def start_blocking(self, parent_window=None):
        """차단 시작"""
        self.blocking_active = True
        self.click_blocking = True
        self.parent_window = parent_window

        # 오버레이 창 생성 (클릭 차단용)
        self._create_overlay_window()

        # 차단 스레드 시작
        self.blocking_thread = threading.Thread(target=self._blocking_loop, daemon=True)
        self.blocking_thread.start()

    def stop_blocking(self):
        """차단 중지"""
        self.blocking_active = False
        self.click_blocking = False

        # 오버레이 창 제거
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
                self.overlay_window = None
            except:
                pass

        if self.blocking_thread:
            self.blocking_thread.join(timeout=1)

    def _create_overlay_window(self):
        """클릭 차단용 오버레이 창 생성"""
        try:
            # 전체 화면 오버레이 창 생성
            self.overlay_window = tk.Toplevel()
            self.overlay_window.title("FocusTimer - 집중 모드")
            self.overlay_window.geometry("100x100")  # 작은 창으로 시작

            # 창을 항상 위에 유지
            self.overlay_window.attributes('-topmost', True)
            self.overlay_window.attributes('-alpha', 0.01)  # 거의 투명하게

            # 창 크기를 화면 전체로 확장
            screen_width = self.overlay_window.winfo_screenwidth()
            screen_height = self.overlay_window.winfo_screenheight()
            self.overlay_window.geometry(f"{screen_width}x{screen_height}+0+0")

            # 마우스 이벤트 차단
            self.overlay_window.bind('<Button-1>', lambda e: 'break')
            self.overlay_window.bind('<Button-2>', lambda e: 'break')
            self.overlay_window.bind('<Button-3>', lambda e: 'break')
            self.overlay_window.bind('<Key>', lambda e: 'break')

            # 창을 숨김 (백그라운드에서 작동)
            self.overlay_window.withdraw()

        except Exception as e:
            print(f"오버레이 창 생성 오류: {e}")
            self.overlay_window = None

    def _blocking_loop(self):
        """차단 루프"""
        while self.blocking_active:
            try:
                if platform.system() == "Darwin":
                    self._block_macos_apps()
                else:
                    self._block_generic_apps()

                # 주기적으로 FocusTimer 창을 앞으로 가져오기
                if self.click_blocking and self.parent_window:
                    self._bring_focus_timer_to_front()

                time.sleep(2)  # 2초마다 체크
            except Exception as e:
                print(f"차단 중 오류: {e}")
                time.sleep(5)

    def _block_macos_apps(self):
        """macOS 앱 차단"""
        try:
            # 현재 활성 앱 확인
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            if active_app and 'NSApplicationName' in active_app:
                app_name = active_app['NSApplicationName']

                # 차단된 앱인지 확인
                if any(blocked in app_name for blocked in self.blocked_apps):
                    # FocusTimer로 포커스 이동
                    self._bring_focus_timer_to_front()

        except Exception as e:
            print(f"macOS 앱 차단 오류: {e}")

    def _block_generic_apps(self):
        """일반적인 앱 차단 (Windows/Linux)"""
        if psutil is None:
            print("psutil 모듈이 없어서 앱 차단 기능을 사용할 수 없습니다.")
            return

        try:
            # 현재 활성 프로세스 확인
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if any(blocked.lower() in proc_name.lower() for blocked in self.blocked_apps):
                        # 프로세스 종료 시도
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"일반 앱 차단 오류: {e}")

    def _bring_focus_timer_to_front(self):
        """FocusTimer를 앞으로 가져오기"""
        try:
            if platform.system() == "Darwin":
                # macOS에서 FocusTimer 앱 활성화
                os.system("osascript -e 'tell application \"FocusTimer\" to activate'")
        except Exception as e:
            print(f"앱 포커스 오류: {e}")


class IntegratedFocusTimer:
    """통합 FocusTimer GUI 클래스"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FocusTimer - 통합 학습 시스템")
        self.root.geometry("1600x1000")

        # macOS 네이티브 스타일 설정
        self.setup_macos_style()

        # 창을 항상 위에 유지 (사용자 설정에 따라)
        self.root.attributes('-topmost', False)  # 기본값은 False

        # 타이머 관련 변수
        self.timer_running = False
        self.timer_thread = None
        self.remaining_time = 0  # 초 단위
        self.timer_duration = 25 * 60  # 기본 25분
        self.break_duration = 5 * 60   # 기본 5분
        self.is_break_time = False

        # 포커스 세션 추적
        self.focus_sessions = []
        self.current_session = None

        # 차단 시스템
        self.app_blocker = ApplicationBlocker()

        # 종료 제어
        self.exit_problem_solved = False
        self.exit_problem = None

        # 알고리즘 시스템 초기화
        self.problem_provider = MockProblemProvider()
        self.challenge_system = AdvancedChallengeSystem("integrated_user", self.problem_provider)

        # 현재 선택된 문제
        self.current_problem: Optional[AlgorithmProblem] = None
        self.current_challenge: Optional[Challenge] = None

                # 사용자 설정
        self.user_preferences = self.load_user_preferences()

        # 성능 최적화 시스템 초기화
        self.memory_monitor = MemoryMonitor()
        self.background_optimizer = BackgroundTaskOptimizer()
        self.database_optimizer = DatabaseOptimizer()

        # 메모리 모니터링 시작
        self.memory_monitor.start_monitoring()

        # 백그라운드 작업 최적화 시작
        self.background_optimizer.start_workers()

        # 데이터베이스 초기화
        self.database_optimizer.initialize_database()

        # 메모리 최적화 콜백 등록
        self.memory_monitor.add_optimization_callback(self._perform_memory_optimization)

        # 알림 시스템 초기화
        self.notification_system = NotificationBanner(self.root)
        self.notification_system.start_notification_system()

        # GUI 구성
        self.setup_gui()
        self.load_initial_data()

        # 주기적 업데이트
        self.schedule_updates()

        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_macos_style(self):
        """macOS 네이티브 스타일 설정"""
        try:
            # macOS 시스템 색상 팔레트
            self.colors = {
                'primary': '#007AFF',      # iOS Blue
                'secondary': '#5856D6',    # iOS Purple
                'success': '#34C759',      # iOS Green
                'warning': '#FF9500',      # iOS Orange
                'error': '#FF3B30',        # iOS Red
                'background': '#F2F2F7',   # iOS Light Gray
                'surface': '#FFFFFF',      # White
                'text_primary': '#000000', # Black
                'text_secondary': '#8E8E93', # iOS Gray
                'border': '#C6C6C8',       # iOS Light Gray
                'accent': '#007AFF',       # iOS Blue
                'card': '#FFFFFF',         # White
                'shadow': '#000000'        # Black for shadows
            }

            # 폰트 설정
            self.fonts = {
                'title': ('SF Pro Display', 24, 'bold'),
                'heading': ('SF Pro Display', 18, 'bold'),
                'subheading': ('SF Pro Display', 14, 'bold'),
                'body': ('SF Pro Text', 12, 'normal'),
                'caption': ('SF Pro Text', 10, 'normal'),
                'button': ('SF Pro Text', 12, 'medium'),
                'timer': ('SF Pro Display', 48, 'bold'),
                'code': ('SF Mono', 11, 'normal')
            }

            # 스타일 설정
            self.styles = {
                'border_radius': 8,
                'padding': 16,
                'margin': 8,
                'shadow_offset': 2
            }

            # 루트 윈도우 스타일
            self.root.configure(bg=self.colors['background'])

            # ttk 스타일 설정
            self.setup_ttk_styles()

        except Exception as e:
            logger.error(f"macOS 스타일 설정 오류: {e}")
            # 폴백 스타일
            self.colors = {
                'primary': '#007AFF', 'secondary': '#5856D6', 'success': '#34C759',
                'warning': '#FF9500', 'error': '#FF3B30', 'background': '#F2F2F7',
                'surface': '#FFFFFF', 'text_primary': '#000000', 'text_secondary': '#8E8E93',
                'border': '#C6C6C8', 'accent': '#007AFF', 'card': '#FFFFFF', 'shadow': '#000000'
            }
            self.fonts = {
                'title': ('Arial', 24, 'bold'), 'heading': ('Arial', 18, 'bold'),
                'subheading': ('Arial', 14, 'bold'), 'body': ('Arial', 12, 'normal'),
                'caption': ('Arial', 10, 'normal'), 'button': ('Arial', 12, 'bold'),
                'timer': ('Arial', 48, 'bold'), 'code': ('Consolas', 11, 'normal')
            }
            self.styles = {'border_radius': 8, 'padding': 16, 'margin': 8, 'shadow_offset': 2}

    def setup_ttk_styles(self):
        """ttk 스타일 설정"""
        try:
            style = ttk.Style()

            # 테마 설정
            style.theme_use('clam')

            # 버튼 스타일
            style.configure('Primary.TButton',
                background=self.colors['primary'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                font=self.fonts['button'],
                padding=(20, 10)
            )

            style.map('Primary.TButton',
                background=[('active', self.colors['secondary']), ('pressed', self.colors['secondary'])]
            )

            # 보조 버튼 스타일
            style.configure('Secondary.TButton',
                background=self.colors['surface'],
                foreground=self.colors['text_primary'],
                borderwidth=1,
                bordercolor=self.colors['border'],
                focuscolor='none',
                font=self.fonts['button'],
                padding=(16, 8)
            )

            # 성공 버튼 스타일
            style.configure('Success.TButton',
                background=self.colors['success'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                font=self.fonts['button'],
                padding=(20, 10)
            )

            # 경고 버튼 스타일
            style.configure('Warning.TButton',
                background=self.colors['warning'],
                foreground='white',
                borderwidth=0,
                focuscolor='none',
                font=self.fonts['button'],
                padding=(20, 10)
            )

            # 프레임 스타일
            style.configure('Card.TFrame',
                background=self.colors['card'],
                borderwidth=1,
                relief='solid'
            )

            # 라벨 스타일
            style.configure('Title.TLabel',
                background=self.colors['background'],
                foreground=self.colors['text_primary'],
                font=self.fonts['title']
            )

            style.configure('Heading.TLabel',
                background=self.colors['background'],
                foreground=self.colors['text_primary'],
                font=self.fonts['heading']
            )

            style.configure('Body.TLabel',
                background=self.colors['background'],
                foreground=self.colors['text_primary'],
                font=self.fonts['body']
            )

            # 노트북 스타일
            style.configure('TNotebook',
                background=self.colors['background'],
                borderwidth=0
            )

            style.configure('TNotebook.Tab',
                background=self.colors['surface'],
                foreground=self.colors['text_primary'],
                padding=(20, 10),
                font=self.fonts['body']
            )

            style.map('TNotebook.Tab',
                background=[('selected', self.colors['primary']), ('active', self.colors['secondary'])],
                foreground=[('selected', 'white'), ('active', 'white')]
            )

        except Exception as e:
            logger.error(f"ttk 스타일 설정 오류: {e}")

    def create_card_frame(self, parent, title=None, padding=16):
        """카드 스타일 프레임 생성"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill=tk.BOTH, expand=True, padx=self.styles['margin'], pady=self.styles['margin'])

        if title:
            title_label = ttk.Label(card, text=title, style='Heading.TLabel')
            title_label.pack(anchor=tk.W, padx=padding, pady=(padding, 8))

        content_frame = ttk.Frame(card)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=(0, padding))

        return content_frame

    def setup_gui(self):
        """GUI 구성 - macOS 네이티브 스타일"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 헤더 섹션
        self.setup_header_section(main_container)

        # 메인 컨텐츠 영역
        content_container = ttk.Frame(main_container)
        content_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # 좌측 패널 (타이머 + 통계)
        left_panel = ttk.Frame(content_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 우측 패널 (알고리즘 시스템)
        right_panel = ttk.Frame(content_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # 좌측 패널 구성
        self.setup_left_panel_modern(left_panel)

        # 우측 패널 구성
        self.setup_right_panel_modern(right_panel)

    def setup_header_section(self, parent):
        """헤더 섹션 구성"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # 앱 제목
        title_label = ttk.Label(header_frame, text="FocusTimer", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        # 상태 표시
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(status_frame, text="준비됨", style='Body.TLabel')
        self.status_label.pack(side=tk.RIGHT, padx=(10, 0))

        # 차단 상태 표시
        self.blocking_status_label = ttk.Label(status_frame, text="차단 비활성",
                                             foreground=self.colors['text_secondary'], style='Body.TLabel')
        self.blocking_status_label.pack(side=tk.RIGHT)

    def setup_left_panel_modern(self, parent):
        """현대적인 좌측 패널 구성"""
        # 타이머 카드
        timer_card = self.create_card_frame(parent, "포커스 타이머")
        self.setup_timer_panel_modern(timer_card)

        # 통계 카드
        stats_card = self.create_card_frame(parent, "학습 통계")
        self.setup_statistics_panel_modern(stats_card)

    def setup_right_panel_modern(self, parent):
        """현대적인 우측 패널 구성"""
        # 탭 컨테이너
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 알고리즘 시스템 탭들
        self.setup_recommendations_tab_modern(notebook)
        self.setup_challenges_tab_modern(notebook)
        self.setup_learning_path_tab_modern(notebook)
        self.setup_statistics_tab_modern(notebook)
        self.setup_focus_sessions_tab_modern(notebook)
        self.setup_performance_monitoring_tab_modern(notebook)

    def setup_timer_panel_modern(self, parent):
        """현대적인 타이머 패널"""
        # 타이머 표시
        timer_display_frame = ttk.Frame(parent)
        timer_display_frame.pack(fill=tk.X, pady=20)

        self.timer_label = ttk.Label(timer_display_frame, text="25:00",
                                   font=self.fonts['timer'], foreground=self.colors['primary'])
        self.timer_label.pack()

        # 타이머 설정
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.X, pady=(0, 20))

        # 포커스 시간 설정
        focus_frame = ttk.Frame(settings_frame)
        focus_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(focus_frame, text="포커스 시간 (분)", style='Body.TLabel').pack(anchor=tk.W)
        self.focus_duration_var = tk.StringVar(value="25")
        focus_entry = ttk.Entry(focus_frame, textvariable=self.focus_duration_var, width=10)
        focus_entry.pack(pady=(5, 0))

        # 휴식 시간 설정
        break_frame = ttk.Frame(settings_frame)
        break_frame.pack(side=tk.LEFT)

        ttk.Label(break_frame, text="휴식 시간 (분)", style='Body.TLabel').pack(anchor=tk.W)
        self.break_duration_var = tk.StringVar(value="5")
        break_entry = ttk.Entry(break_frame, textvariable=self.break_duration_var, width=10)
        break_entry.pack(pady=(5, 0))

        # 설정 적용 버튼
        apply_button = ttk.Button(settings_frame, text="설정 적용",
                                style='Secondary.TButton', command=self.apply_timer_settings)
        apply_button.pack(side=tk.RIGHT, padx=(20, 0))

        # 타이머 컨트롤
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=20)

        self.start_button = ttk.Button(control_frame, text="시작",
                                     style='Primary.TButton', command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.pause_button = ttk.Button(control_frame, text="일시정지",
                                     style='Secondary.TButton', command=self.pause_timer)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))

        self.reset_button = ttk.Button(control_frame, text="리셋",
                                     style='Secondary.TButton', command=self.reset_timer)
        self.reset_button.pack(side=tk.LEFT)

        # 초기 상태 설정
        self.pause_button.config(state='disabled')

    def setup_statistics_panel_modern(self, parent):
        """현대적인 통계 패널"""
        # 통계 그리드
        stats_grid = ttk.Frame(parent)
        stats_grid.pack(fill=tk.BOTH, expand=True)

        # 오늘의 통계
        today_frame = ttk.Frame(stats_grid)
        today_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(today_frame, text="오늘의 학습", style='Subheading.TLabel').pack(anchor=tk.W)
        self.today_focus_label = ttk.Label(today_frame, text="0시간", style='Body.TLabel')
        self.today_focus_label.pack(anchor=tk.W, pady=(5, 0))
        self.today_problems_label = ttk.Label(today_frame, text="0문제 해결", style='Body.TLabel')
        self.today_problems_label.pack(anchor=tk.W)

        # 총 통계
        total_frame = ttk.Frame(stats_grid)
        total_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(total_frame, text="총 학습", style='Subheading.TLabel').pack(anchor=tk.W)
        self.total_focus_label = ttk.Label(total_frame, text="0시간", style='Body.TLabel')
        self.total_focus_label.pack(anchor=tk.W, pady=(5, 0))
        self.total_problems_label = ttk.Label(total_frame, text="0문제 해결", style='Body.TLabel')
        self.total_problems_label.pack(anchor=tk.W)

    def setup_timer_panel(self, parent):
        """상단 타이머 패널 구성"""
        timer_frame = ttk.LabelFrame(parent, text="포커스 타이머", padding=10)
        timer_frame.pack(fill=tk.X, pady=(0, 10))

        # 타이머 표시
        self.timer_label = ttk.Label(timer_frame, text="25:00", font=('Arial', 24, 'bold'))
        self.timer_label.pack(pady=10)

        # 타이머 컨트롤 버튼들
        control_frame = ttk.Frame(timer_frame)
        control_frame.pack(pady=10)

        self.start_button = ttk.Button(control_frame, text="시작", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(control_frame, text="일시정지", command=self.pause_timer, state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(control_frame, text="리셋", command=self.reset_timer)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 타이머 설정
        settings_frame = ttk.Frame(timer_frame)
        settings_frame.pack(pady=10)

        ttk.Label(settings_frame, text="포커스 시간(분):").pack(side=tk.LEFT)
        self.focus_duration_var = tk.StringVar(value="25")
        focus_entry = ttk.Entry(settings_frame, textvariable=self.focus_duration_var, width=5)
        focus_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="휴식 시간(분):").pack(side=tk.LEFT, padx=(10, 0))
        self.break_duration_var = tk.StringVar(value="5")
        break_entry = ttk.Entry(settings_frame, textvariable=self.break_duration_var, width=5)
        break_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(settings_frame, text="설정 적용", command=self.apply_timer_settings).pack(side=tk.LEFT, padx=10)

        # 상태 표시
        self.status_label = ttk.Label(timer_frame, text="준비됨", font=('Arial', 10))
        self.status_label.pack(pady=5)

        # 차단 상태 표시
        self.blocking_status_label = ttk.Label(timer_frame, text="차단 비활성", font=('Arial', 9), foreground='gray')
        self.blocking_status_label.pack(pady=2)

    def setup_statistics_panel(self, parent):
        """상단 통계 패널 구성"""
        stats_frame = ttk.LabelFrame(parent, text="학습 통계", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # 통계 정보 표시
        self.stats_labels = {}
        stats_data = [
            ("level", "레벨"),
            ("difficulty", "추천 난이도"),
            ("solved", "해결한 문제"),
            ("streak", "연속 해결"),
            ("success_rate", "성공률"),
            ("focus_time", "총 포커스 시간")
        ]

        for i, (key, label) in enumerate(stats_data):
            frame = ttk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, padx=(0, 15))

            ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold')).pack()
            self.stats_labels[key] = ttk.Label(frame, text="로딩...", font=('Arial', 9))
            self.stats_labels[key].pack()

        # 새로고침 버튼
        ttk.Button(stats_frame, text="새로고침", command=self.refresh_statistics).pack(side=tk.RIGHT)

    def setup_left_panel(self, parent):
        """왼쪽 패널 구성"""
        # 노트북 (탭) 생성
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 문제 추천 탭
        self.setup_recommendations_tab(notebook)

        # 챌린지 탭
        self.setup_challenges_tab(notebook)

        # 학습 경로 탭
        self.setup_learning_path_tab(notebook)

        # 통계 탭
        self.setup_statistics_tab(notebook)

        # 포커스 세션 탭
        self.setup_focus_sessions_tab(notebook)

        # 성능 모니터링 탭
        self.setup_performance_monitoring_tab(notebook)

    def setup_recommendations_tab_modern(self, notebook):
        """현대적인 문제 추천 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="문제 추천")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 새로고침 버튼
        refresh_button = ttk.Button(action_bar, text="🔄 새로고침",
                                  style='Secondary.TButton', command=self.refresh_recommendations)
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # 챌린지 생성 버튼들
        daily_button = ttk.Button(action_bar, text="📅 일일 챌린지",
                                style='Primary.TButton', command=self.create_daily_challenge)
        daily_button.pack(side=tk.LEFT, padx=(0, 10))

        weekly_button = ttk.Button(action_bar, text="📊 주간 챌린지",
                                 style='Primary.TButton', command=self.create_weekly_challenge)
        weekly_button.pack(side=tk.LEFT)

        # 추천 문제 카드
        recommendations_card = self.create_card_frame(frame, "추천 문제")

        # 트리뷰 컨테이너
        tree_container = ttk.Frame(recommendations_card)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('title', 'difficulty', 'tags', 'platform')
        self.recommendations_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.recommendations_tree.heading('title', text='제목')
        self.recommendations_tree.heading('difficulty', text='난이도')
        self.recommendations_tree.heading('tags', text='태그')
        self.recommendations_tree.heading('platform', text='플랫폼')

        self.recommendations_tree.column('title', width=250, minwidth=200)
        self.recommendations_tree.column('difficulty', width=80, minwidth=80)
        self.recommendations_tree.column('tags', width=150, minwidth=100)
        self.recommendations_tree.column('platform', width=100, minwidth=80)

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        self.recommendations_tree.configure(yscrollcommand=scrollbar.set)

        self.recommendations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.recommendations_tree.bind('<Double-1>', self.on_problem_select)

        # 선택된 문제 정보
        self.setup_problem_info_panel(frame)

    def setup_problem_info_panel(self, parent):
        """선택된 문제 정보 패널"""
        info_card = self.create_card_frame(parent, "문제 정보")

        # 문제 제목
        self.problem_title_label = ttk.Label(info_card, text="문제를 선택하세요",
                                           style='Subheading.TLabel', foreground=self.colors['text_secondary'])
        self.problem_title_label.pack(anchor=tk.W, pady=(0, 10))

        # 문제 설명
        description_frame = ttk.Frame(info_card)
        description_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(description_frame, text="설명:", style='Body.TLabel').pack(anchor=tk.W)
        self.problem_description_text = scrolledtext.ScrolledText(description_frame, height=6,
                                                                font=self.fonts['body'], wrap=tk.WORD)
        self.problem_description_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 문제 메타데이터
        metadata_frame = ttk.Frame(info_card)
        metadata_frame.pack(fill=tk.X, pady=(10, 0))

        # 난이도
        difficulty_frame = ttk.Frame(metadata_frame)
        difficulty_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(difficulty_frame, text="난이도:", style='Body.TLabel').pack(anchor=tk.W)
        self.difficulty_label = ttk.Label(difficulty_frame, text="-", style='Body.TLabel')
        self.difficulty_label.pack(anchor=tk.W)

        # 플랫폼
        platform_frame = ttk.Frame(metadata_frame)
        platform_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(platform_frame, text="플랫폼:", style='Body.TLabel').pack(anchor=tk.W)
        self.platform_label = ttk.Label(platform_frame, text="-", style='Body.TLabel')
        self.platform_label.pack(anchor=tk.W)

        # 태그
        tags_frame = ttk.Frame(metadata_frame)
        tags_frame.pack(side=tk.LEFT)

        ttk.Label(tags_frame, text="태그:", style='Body.TLabel').pack(anchor=tk.W)
        self.tags_label = ttk.Label(tags_frame, text="-", style='Body.TLabel')
        self.tags_label.pack(anchor=tk.W)

    def setup_challenges_tab_modern(self, notebook):
        """현대적인 챌린지 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="챌린지")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 커스텀 챌린지 생성 버튼
        custom_button = ttk.Button(action_bar, text="🎯 커스텀 챌린지",
                                 style='Primary.TButton', command=self.create_custom_challenge_dialog)
        custom_button.pack(side=tk.LEFT, padx=(0, 10))

        # 새로고침 버튼
        refresh_button = ttk.Button(action_bar, text="🔄 새로고침",
                                  style='Secondary.TButton', command=self.refresh_challenges)
        refresh_button.pack(side=tk.LEFT)

        # 챌린지 목록 카드
        challenges_card = self.create_card_frame(frame, "활성 챌린지")

        # 트리뷰 컨테이너
        tree_container = ttk.Frame(challenges_card)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('name', 'type', 'progress', 'remaining', 'reward', 'status')
        self.challenges_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.challenges_tree.heading('name', text='챌린지명')
        self.challenges_tree.heading('type', text='유형')
        self.challenges_tree.heading('progress', text='진도')
        self.challenges_tree.heading('remaining', text='남은 시간')
        self.challenges_tree.heading('reward', text='보상')
        self.challenges_tree.heading('status', text='상태')

        self.challenges_tree.column('name', width=200, minwidth=150)
        self.challenges_tree.column('type', width=80, minwidth=80)
        self.challenges_tree.column('progress', width=80, minwidth=80)
        self.challenges_tree.column('remaining', width=100, minwidth=100)
        self.challenges_tree.column('reward', width=80, minwidth=80)
        self.challenges_tree.column('status', width=80, minwidth=80)

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.challenges_tree.yview)
        self.challenges_tree.configure(yscrollcommand=scrollbar.set)

        self.challenges_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.challenges_tree.bind('<Double-1>', self.on_challenge_select)

        # 챌린지 상세 정보
        self.setup_challenge_info_panel(frame)

    def setup_challenge_info_panel(self, parent):
        """챌린지 상세 정보 패널"""
        info_card = self.create_card_frame(parent, "챌린지 정보")

        # 챌린지 제목
        self.challenge_title_label = ttk.Label(info_card, text="챌린지를 선택하세요",
                                             style='Subheading.TLabel', foreground=self.colors['text_secondary'])
        self.challenge_title_label.pack(anchor=tk.W, pady=(0, 10))

        # 챌린지 설명
        description_frame = ttk.Frame(info_card)
        description_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(description_frame, text="설명:", style='Body.TLabel').pack(anchor=tk.W)
        self.challenge_description_text = scrolledtext.ScrolledText(description_frame, height=4,
                                                                  font=self.fonts['body'], wrap=tk.WORD)
        self.challenge_description_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 챌린지 메타데이터
        metadata_frame = ttk.Frame(info_card)
        metadata_frame.pack(fill=tk.X, pady=(10, 0))

        # 진행률
        progress_frame = ttk.Frame(metadata_frame)
        progress_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(progress_frame, text="진행률:", style='Body.TLabel').pack(anchor=tk.W)
        self.progress_label = ttk.Label(progress_frame, text="-", style='Body.TLabel')
        self.progress_label.pack(anchor=tk.W)

        # 남은 시간
        remaining_frame = ttk.Frame(metadata_frame)
        remaining_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(remaining_frame, text="남은 시간:", style='Body.TLabel').pack(anchor=tk.W)
        self.remaining_label = ttk.Label(remaining_frame, text="-", style='Body.TLabel')
        self.remaining_label.pack(anchor=tk.W)

        # 보상
        reward_frame = ttk.Frame(metadata_frame)
        reward_frame.pack(side=tk.LEFT)

        ttk.Label(reward_frame, text="보상:", style='Body.TLabel').pack(anchor=tk.W)
        self.reward_label = ttk.Label(reward_frame, text="-", style='Body.TLabel')
        self.reward_label.pack(anchor=tk.W)

    def setup_learning_path_tab_modern(self, notebook):
        """현대적인 학습 경로 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="학습 경로")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 목표 설정
        goal_frame = ttk.Frame(action_bar)
        goal_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(goal_frame, text="목표:", style='Body.TLabel').pack(side=tk.LEFT)
        self.goal_var = tk.StringVar(value="기초 알고리즘 마스터")
        goal_entry = ttk.Entry(goal_frame, textvariable=self.goal_var, width=30)
        goal_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 기간 설정
        duration_frame = ttk.Frame(action_bar)
        duration_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(duration_frame, text="기간(일):", style='Body.TLabel').pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="30")
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 학습 경로 생성 버튼
        generate_button = ttk.Button(action_bar, text="🎯 학습 경로 생성",
                                   style='Primary.TButton', command=self.generate_learning_path)
        generate_button.pack(side=tk.LEFT)

        # 학습 경로 카드
        path_card = self.create_card_frame(frame, "생성된 학습 경로")

        # 트리뷰 컨테이너
        tree_container = ttk.Frame(path_card)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('title', 'difficulty', 'tags', 'status', 'progress')
        self.learning_path_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.learning_path_tree.heading('title', text='문제 제목')
        self.learning_path_tree.heading('difficulty', text='난이도')
        self.learning_path_tree.heading('tags', text='태그')
        self.learning_path_tree.heading('status', text='상태')
        self.learning_path_tree.heading('progress', text='진행률')

        self.learning_path_tree.column('title', width=250, minwidth=200)
        self.learning_path_tree.column('difficulty', width=80, minwidth=80)
        self.learning_path_tree.column('tags', width=150, minwidth=100)
        self.learning_path_tree.column('status', width=80, minwidth=80)
        self.learning_path_tree.column('progress', width=80, minwidth=80)

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.learning_path_tree.yview)
        self.learning_path_tree.configure(yscrollcommand=scrollbar.set)

        self.learning_path_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.learning_path_tree.bind('<Double-1>', self.on_problem_select)

        # 학습 경로 정보 패널
        self.setup_learning_path_info_panel(frame)

    def setup_learning_path_info_panel(self, parent):
        """학습 경로 정보 패널"""
        info_card = self.create_card_frame(parent, "학습 경로 정보")

        # 경로 제목
        self.path_title_label = ttk.Label(info_card, text="학습 경로를 생성하세요",
                                        style='Subheading.TLabel', foreground=self.colors['text_secondary'])
        self.path_title_label.pack(anchor=tk.W, pady=(0, 10))

        # 경로 설명
        description_frame = ttk.Frame(info_card)
        description_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(description_frame, text="설명:", style='Body.TLabel').pack(anchor=tk.W)
        self.path_description_text = scrolledtext.ScrolledText(description_frame, height=6,
                                                             font=self.fonts['body'], wrap=tk.WORD)
        self.path_description_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 경로 메타데이터
        metadata_frame = ttk.Frame(info_card)
        metadata_frame.pack(fill=tk.X, pady=(10, 0))

        # 목표
        goal_frame = ttk.Frame(metadata_frame)
        goal_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(goal_frame, text="목표:", style='Body.TLabel').pack(anchor=tk.W)
        self.path_goal_label = ttk.Label(goal_frame, text="-", style='Body.TLabel')
        self.path_goal_label.pack(anchor=tk.W)

        # 예상 완료 시간
        completion_frame = ttk.Frame(metadata_frame)
        completion_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(completion_frame, text="예상 완료:", style='Body.TLabel').pack(anchor=tk.W)
        self.path_completion_label = ttk.Label(completion_frame, text="-", style='Body.TLabel')
        self.path_completion_label.pack(anchor=tk.W)

        # 총 문제 수
        total_frame = ttk.Frame(metadata_frame)
        total_frame.pack(side=tk.LEFT)

        ttk.Label(total_frame, text="총 문제:", style='Body.TLabel').pack(anchor=tk.W)
        self.path_total_label = ttk.Label(total_frame, text="-", style='Body.TLabel')
        self.path_total_label.pack(anchor=tk.W)

    def setup_statistics_tab_modern(self, notebook):
        """현대적인 통계 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="통계")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 새로고침 버튼
        refresh_button = ttk.Button(action_bar, text="🔄 통계 새로고침",
                                  style='Secondary.TButton', command=self.refresh_detailed_statistics)
        refresh_button.pack(side=tk.LEFT)

        # 통계 카드들
        stats_container = ttk.Frame(frame)
        stats_container.pack(fill=tk.BOTH, expand=True)

        # 약점/강점 분석
        analysis_frame = ttk.Frame(stats_container)
        analysis_frame.pack(fill=tk.BOTH, expand=True)

        # 약점 영역 카드
        weak_card = self.create_card_frame(analysis_frame, "📉 약점 영역")
        self.weak_text = scrolledtext.ScrolledText(weak_card, height=8,
                                                 font=self.fonts['body'], wrap=tk.WORD)
        self.weak_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 강점 영역 카드
        strong_card = self.create_card_frame(analysis_frame, "📈 강점 영역")
        self.strong_text = scrolledtext.ScrolledText(strong_card, height=8,
                                                   font=self.fonts['body'], wrap=tk.WORD)
        self.strong_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_focus_sessions_tab_modern(self, notebook):
        """현대적인 포커스 세션 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="포커스 세션")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 새로고침 버튼
        refresh_button = ttk.Button(action_bar, text="🔄 세션 기록 새로고침",
                                  style='Secondary.TButton', command=self.refresh_focus_sessions)
        refresh_button.pack(side=tk.LEFT)

        # 세션 목록 카드
        sessions_card = self.create_card_frame(frame, "📊 포커스 세션 기록")

        # 트리뷰 컨테이너
        tree_container = ttk.Frame(sessions_card)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('date', 'duration', 'problem', 'completed', 'interruptions', 'efficiency')
        self.sessions_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.sessions_tree.heading('date', text='날짜')
        self.sessions_tree.heading('duration', text='지속시간')
        self.sessions_tree.heading('problem', text='문제')
        self.sessions_tree.heading('completed', text='완료')
        self.sessions_tree.heading('interruptions', text='방해')
        self.sessions_tree.heading('efficiency', text='효율성')

        self.sessions_tree.column('date', width=150, minwidth=120)
        self.sessions_tree.column('duration', width=100, minwidth=80)
        self.sessions_tree.column('problem', width=200, minwidth=150)
        self.sessions_tree.column('completed', width=80, minwidth=60)
        self.sessions_tree.column('interruptions', width=80, minwidth=60)
        self.sessions_tree.column('efficiency', width=80, minwidth=60)

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)

        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 세션 통계 패널
        self.setup_session_stats_panel(frame)

    def setup_session_stats_panel(self, parent):
        """세션 통계 패널"""
        stats_card = self.create_card_frame(parent, "📈 세션 통계")

        # 통계 그리드
        stats_grid = ttk.Frame(stats_card)
        stats_grid.pack(fill=tk.BOTH, expand=True)

        # 총 세션 수
        total_frame = ttk.Frame(stats_grid)
        total_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(total_frame, text="총 세션", style='Subheading.TLabel').pack(anchor=tk.W)
        self.total_sessions_label = ttk.Label(total_frame, text="0", style='Body.TLabel')
        self.total_sessions_label.pack(anchor=tk.W, pady=(5, 0))

        # 총 포커스 시간
        focus_frame = ttk.Frame(stats_grid)
        focus_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(focus_frame, text="총 포커스 시간", style='Subheading.TLabel').pack(anchor=tk.W)
        self.total_focus_time_label = ttk.Label(focus_frame, text="0시간", style='Body.TLabel')
        self.total_focus_time_label.pack(anchor=tk.W, pady=(5, 0))

        # 평균 효율성
        efficiency_frame = ttk.Frame(stats_grid)
        efficiency_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(efficiency_frame, text="평균 효율성", style='Subheading.TLabel').pack(anchor=tk.W)
        self.avg_efficiency_label = ttk.Label(efficiency_frame, text="0%", style='Body.TLabel')
        self.avg_efficiency_label.pack(anchor=tk.W, pady=(5, 0))

        # 완료율
        completion_frame = ttk.Frame(stats_grid)
        completion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(completion_frame, text="완료율", style='Subheading.TLabel').pack(anchor=tk.W)
        self.completion_rate_label = ttk.Label(completion_frame, text="0%", style='Body.TLabel')
        self.completion_rate_label.pack(anchor=tk.W, pady=(5, 0))

    def setup_performance_monitoring_tab_modern(self, notebook):
        """현대적인 성능 모니터링 탭"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="성능 모니터링")

        # 상단 액션 바
        action_bar = ttk.Frame(frame)
        action_bar.pack(fill=tk.X, pady=(0, 20))

        # 전체 성능 최적화 버튼
        optimize_button = ttk.Button(action_bar, text="⚡ 전체 성능 최적화",
                                   style='Primary.TButton', command=self.optimize_performance)
        optimize_button.pack(side=tk.LEFT, padx=(0, 10))

        # 성능 통계 새로고침 버튼
        refresh_button = ttk.Button(action_bar, text="🔄 성능 통계 새로고침",
                                  style='Secondary.TButton', command=self.refresh_performance_stats)
        refresh_button.pack(side=tk.LEFT)

        # 성능 모니터링 카드들
        monitoring_container = ttk.Frame(frame)
        monitoring_container.pack(fill=tk.BOTH, expand=True)

        # 메모리 사용량 카드
        memory_card = self.create_card_frame(monitoring_container, "💾 메모리 사용량")
        self.memory_info_label = ttk.Label(memory_card, text="메모리 정보 로딩 중...", style='Body.TLabel')
        self.memory_info_label.pack(anchor=tk.W, pady=(0, 10))

        memory_button = ttk.Button(memory_card, text="🧹 메모리 최적화",
                                 style='Secondary.TButton', command=self._perform_memory_optimization)
        memory_button.pack(anchor=tk.W)

        # 데이터베이스 성능 카드
        db_card = self.create_card_frame(monitoring_container, "🗄️ 데이터베이스 성능")
        self.db_info_label = ttk.Label(db_card, text="데이터베이스 정보 로딩 중...", style='Body.TLabel')
        self.db_info_label.pack(anchor=tk.W, pady=(0, 10))

        db_button = ttk.Button(db_card, text="🔧 데이터베이스 최적화",
                             style='Secondary.TButton', command=self.database_optimizer.optimize_database)
        db_button.pack(anchor=tk.W)

        # 백그라운드 작업 카드
        bg_card = self.create_card_frame(monitoring_container, "⚙️ 백그라운드 작업")
        self.bg_info_label = ttk.Label(bg_card, text="백그라운드 작업 정보 로딩 중...", style='Body.TLabel')
        self.bg_info_label.pack(anchor=tk.W, pady=(0, 10))

        # 실시간 성능 그래프 (향후 구현 가능)
        graph_card = self.create_card_frame(monitoring_container, "📊 실시간 성능 그래프")
        graph_info = ttk.Label(graph_card, text="실시간 성능 모니터링 그래프가 여기에 표시됩니다.",
                              style='Body.TLabel', foreground=self.colors['text_secondary'])
        graph_info.pack(anchor=tk.W)

    def refresh_performance_stats(self):
        """성능 통계 새로고침"""
        try:
            # 메모리 정보 업데이트
            memory_stats = self.memory_monitor.get_memory_stats()
            if 'error' not in memory_stats:
                memory_text = f"총 메모리: {memory_stats['total'] / (1024**3):.1f}GB\n"
                memory_text += f"사용 중: {memory_stats['used'] / (1024**3):.1f}GB ({memory_stats['percent']:.1f}%)\n"
                memory_text += f"사용 가능: {memory_stats['available'] / (1024**3):.1f}GB\n"
                memory_text += f"평균 사용량: {memory_stats.get('average', 0) * 100:.1f}%"
            else:
                memory_text = "메모리 정보를 가져올 수 없습니다."

            self.memory_info_label.config(text=memory_text)

            # 데이터베이스 정보 업데이트
            db_stats = self.database_optimizer.get_performance_stats()
            if 'error' not in db_stats:
                db_text = f"캐시 크기: {db_stats['cache_size']}개\n"
                db_text += f"캐시 히트율: {db_stats['cache_hit_rate'] * 100:.1f}%\n"
                db_text += f"테이블 수: {len(db_stats['tables'])}개"
                for table, count in db_stats['tables'].items():
                    db_text += f"\n  - {table}: {count}개 레코드"
            else:
                db_text = "데이터베이스 정보를 가져올 수 없습니다."

            self.db_info_label.config(text=db_text)

            # 백그라운드 작업 정보 업데이트
            bg_text = f"활성 워커: {len(self.background_optimizer.worker_threads)}개\n"
            bg_text += f"큐 크기: {self.background_optimizer.get_queue_size()}개 작업\n"
            bg_text += f"완료된 작업: {len(self.background_optimizer.task_results)}개"

            self.bg_info_label.config(text=bg_text)

        except Exception as e:
            logger.error(f"성능 통계 새로고침 오류: {e}")

    def setup_right_panel(self, parent):
        """오른쪽 패널 구성"""
        # 문제 상세 정보
        detail_frame = ttk.LabelFrame(parent, text="문제 상세", padding=10)
        detail_frame.pack(fill=tk.X, pady=(0, 10))

        self.problem_title_label = ttk.Label(detail_frame, text="문제를 선택하세요", font=('Arial', 12, 'bold'))
        self.problem_title_label.pack(anchor=tk.W)

        self.problem_description_text = scrolledtext.ScrolledText(detail_frame, height=6, width=60)
        self.problem_description_text.pack(fill=tk.X, pady=(5, 0))

        # 코드 편집 영역
        code_frame = ttk.LabelFrame(parent, text="코드 편집", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 언어 선택
        lang_frame = ttk.Frame(code_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(lang_frame, text="언어:").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="python")
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                    values=["python", "java", "cpp", "javascript"],
                                    state="readonly", width=15)
        language_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 코드 에디터
        self.code_editor = scrolledtext.ScrolledText(code_frame, height=15, width=60, font=('Consolas', 10))
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        # 하단 버튼들
        button_frame = ttk.Frame(code_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="코드 실행", command=self.run_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="코드 저장", command=self.save_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="코드 불러오기", command=self.load_code).pack(side=tk.LEFT)

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(parent, text="실행 결과", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=6, width=60)
        self.result_text.pack(fill=tk.BOTH, expand=True)



    # 알고리즘 시스템 관련 메서드들 (기존 GUI와 동일)
    def load_initial_data(self):
        """초기 데이터 로드"""
        self.refresh_statistics()
        self.refresh_recommendations()
        self.refresh_challenges()
        self.refresh_detailed_statistics()
        self.refresh_performance_stats()  # 성능 통계 로드
        self.load_code_template()

    def load_code_template(self):
        """기본 코드 템플릿 로드"""
        template = '''def solve():
    # 여기에 해결 코드를 작성하세요
    pass

if __name__ == "__main__":
    solve()
'''
        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(1.0, template)

    def refresh_statistics(self):
        """통계 새로고침"""
        try:
            stats = self.challenge_system.get_user_statistics()

            self.stats_labels['level'].config(text=str(stats['user_level']))
            self.stats_labels['difficulty'].config(text=stats['recommended_difficulty'])
            self.stats_labels['solved'].config(text=str(stats['total_problems_solved']))
            self.stats_labels['streak'].config(text=f"{stats['current_streak']}일")
            self.stats_labels['success_rate'].config(text=f"{stats['success_rate']:.1%}")
            self.stats_labels['focus_time'].config(text="계산 중...")  # TODO: 포커스 시간 계산

        except Exception as e:
            messagebox.showerror("오류", f"통계 로드 실패: {e}")

    def refresh_recommendations(self):
        """추천 문제 새로고침"""
        try:
            # 기존 항목 삭제
            for item in self.recommendations_tree.get_children():
                self.recommendations_tree.delete(item)

            # 새로운 추천 문제 로드
            recommendations = self.challenge_system.get_personalized_recommendations(10)

            for problem in recommendations:
                tags_str = ', '.join(tag.name for tag in problem.tags)
                self.recommendations_tree.insert('', 'end',
                                               values=(problem.title, problem.difficulty.name, tags_str),
                                               tags=(problem.id,))

        except Exception as e:
            messagebox.showerror("오류", f"추천 문제 로드 실패: {e}")

    def refresh_challenges(self):
        """챌린지 새로고침"""
        try:
            # 기존 항목 삭제
            for item in self.challenges_tree.get_children():
                self.challenges_tree.delete(item)

            # 활성 챌린지 로드
            active_challenges = self.challenge_system.get_active_challenges()

            for challenge in active_challenges:
                progress = challenge.get_progress_percentage()
                remaining = challenge.get_remaining_days()

                self.challenges_tree.insert('', 'end',
                                          values=(challenge.name,
                                                 challenge.challenge_type.name,
                                                 f"{progress:.1f}%",
                                                 f"{remaining}일",
                                                 f"{challenge.reward_points}점"),
                                          tags=(challenge.challenge_id,))

        except Exception as e:
            messagebox.showerror("오류", f"챌린지 로드 실패: {e}")

    def refresh_detailed_statistics(self):
        """상세 통계 새로고침"""
        try:
            # 약점 영역
            weak_areas = self.challenge_system.get_weak_areas(10)
            weak_text = "약점 영역 (해결한 문제 수 기준):\n\n"
            for tag, count in weak_areas:
                weak_text += f"• {tag}: {count}문제 해결\n"

            self.weak_text.delete(1.0, tk.END)
            self.weak_text.insert(1.0, weak_text)

            # 강점 영역
            strong_areas = self.challenge_system.get_strong_areas(10)
            strong_text = "강점 영역 (해결한 문제 수 기준):\n\n"
            for tag, count in strong_areas:
                strong_text += f"• {tag}: {count}문제 해결\n"

            self.strong_text.delete(1.0, tk.END)
            self.strong_text.insert(1.0, strong_text)

        except Exception as e:
            messagebox.showerror("오류", f"상세 통계 로드 실패: {e}")

    def on_problem_select(self, event):
        """문제 선택 이벤트"""
        try:
            # 트리뷰에서 선택된 항목 확인
            tree = event.widget
            selection = tree.selection()
            if not selection:
                return

            item = tree.item(selection[0])
            problem_id = item['tags'][0]

            # 문제 정보 로드
            self.current_problem = self.problem_provider.get_problem_by_id(problem_id)

            # 문제 상세 정보 표시
            self.problem_title_label.config(text=f"{self.current_problem.title} ({self.current_problem.difficulty.name})")

            description = f"설명: {self.current_problem.description}\n\n"
            description += f"입력 형식: {self.current_problem.input_format}\n"
            description += f"출력 형식: {self.current_problem.output_format}\n\n"
            description += "태그: " + ', '.join(tag.name for tag in self.current_problem.tags)

            self.problem_description_text.delete(1.0, tk.END)
            self.problem_description_text.insert(1.0, description)

            # 코드 템플릿 로드
            self.load_code_template()

        except Exception as e:
            messagebox.showerror("오류", f"문제 로드 실패: {e}")

    def on_challenge_select(self, event):
        """챌린지 선택 이벤트"""
        try:
            selection = self.challenges_tree.selection()
            if not selection:
                return

            item = self.challenges_tree.item(selection[0])
            challenge_id = item['tags'][0]

            # 챌린지 정보 로드
            self.current_challenge = self.challenge_system.get_challenge_progress(challenge_id)

            if self.current_challenge:
                messagebox.showinfo("챌린지 정보",
                                  f"챌린지: {self.current_challenge.name}\n"
                                  f"설명: {self.current_challenge.description}\n"
                                  f"진도: {self.current_challenge.get_progress_percentage():.1f}%\n"
                                  f"남은 시간: {self.current_challenge.get_remaining_days()}일\n"
                                  f"보상: {self.current_challenge.reward_points}점")

        except Exception as e:
            messagebox.showerror("오류", f"챌린지 로드 실패: {e}")

    def create_daily_challenge(self):
        """일일 챌린지 생성"""
        try:
            challenge = self.challenge_system.create_daily_challenge()
            messagebox.showinfo("성공", f"일일 챌린지가 생성되었습니다!\n\n"
                                       f"이름: {challenge.name}\n"
                                       f"목표 문제 수: {challenge.target_problems}\n"
                                       f"보상: {challenge.reward_points}점")
            self.refresh_challenges()
        except Exception as e:
            messagebox.showerror("오류", f"일일 챌린지 생성 실패: {e}")

    def create_weekly_challenge(self):
        """주간 챌린지 생성"""
        try:
            challenge = self.challenge_system.create_weekly_challenge()
            messagebox.showinfo("성공", f"주간 챌린지가 생성되었습니다!\n\n"
                                       f"이름: {challenge.name}\n"
                                       f"목표 문제 수: {challenge.target_problems}\n"
                                       f"보상: {challenge.reward_points}점")
            self.refresh_challenges()
        except Exception as e:
            messagebox.showerror("오류", f"주간 챌린지 생성 실패: {e}")

    def create_custom_challenge_dialog(self):
        """커스텀 챌린지 생성 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title("커스텀 챌린지 생성")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 입력 필드들
        ttk.Label(dialog, text="챌린지 이름:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="설명:").pack(pady=5)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="난이도:").pack(pady=5)
        difficulty_var = tk.StringVar(value="MEDIUM")
        difficulty_combo = ttk.Combobox(dialog, textvariable=difficulty_var,
                                      values=["EASY", "MEDIUM", "HARD", "EXPERT"],
                                      state="readonly")
        difficulty_combo.pack(pady=5)

        ttk.Label(dialog, text="목표 문제 수:").pack(pady=5)
        target_var = tk.StringVar(value="5")
        ttk.Entry(dialog, textvariable=target_var, width=20).pack(pady=5)

        ttk.Label(dialog, text="기간(일):").pack(pady=5)
        days_var = tk.StringVar(value="7")
        ttk.Entry(dialog, textvariable=days_var, width=20).pack(pady=5)

        def create_challenge():
            try:
                from problem_data_structures import ProblemDifficulty
                difficulty = ProblemDifficulty[difficulty_var.get()]

                challenge = self.challenge_system.create_custom_challenge(
                    name=name_var.get(),
                    description=desc_var.get(),
                    target_difficulty=difficulty,
                    target_problems=int(target_var.get()),
                    time_limit_days=int(days_var.get())
                )

                messagebox.showinfo("성공", "커스텀 챌린지가 생성되었습니다!")
                dialog.destroy()
                self.refresh_challenges()

            except Exception as e:
                messagebox.showerror("오류", f"챌린지 생성 실패: {e}")

        ttk.Button(dialog, text="생성", command=create_challenge).pack(pady=20)

    def generate_learning_path(self):
        """학습 경로 생성"""
        try:
            goal = self.goal_var.get()
            duration = int(self.duration_var.get())

            # 기존 항목 삭제
            for item in self.learning_path_tree.get_children():
                self.learning_path_tree.delete(item)

            # 학습 경로 생성
            learning_path = self.challenge_system.generate_learning_path(goal, duration)

            for problem in learning_path:
                tags_str = ', '.join(tag.name for tag in problem.tags)
                solved_problems = set(self.challenge_system.progress_tracker.get_solved_problems())
                status = "완료" if problem.id in solved_problems else "미완료"

                self.learning_path_tree.insert('', 'end',
                                             values=(problem.title,
                                                    problem.difficulty.name,
                                                    tags_str, status),
                                             tags=(problem.id,))

            messagebox.showinfo("성공", f"학습 경로가 생성되었습니다!\n총 {len(learning_path)}개 문제")

        except Exception as e:
            messagebox.showerror("오류", f"학습 경로 생성 실패: {e}")

    def run_code(self):
        """코드 실행"""
        if not self.current_problem:
            messagebox.showwarning("경고", "먼저 문제를 선택하세요.")
            return

        try:
            # 코드 가져오기
            code = self.code_editor.get(1.0, tk.END).strip()
            language = self.language_var.get()

            if not code:
                messagebox.showwarning("경고", "코드를 입력하세요.")
                return

            # 테스트 케이스 준비
            test_cases = []
            for tc in self.current_problem.test_cases:
                test_cases.append({
                    'input': tc.input_data,
                    'output': tc.expected_output
                })

            # 코드 실행
            is_correct, test_results, performance = self.challenge_system.submit_solution(
                self.current_problem.id, code, language, test_cases
            )

            # 결과 표시
            result_text = f"실행 결과:\n"
            result_text += f"정답 여부: {'✓ 정답' if is_correct else '✗ 오답'}\n"
            result_text += f"테스트 통과: {performance.passed_test_cases}/{performance.total_test_cases}\n"
            result_text += f"성공률: {performance.calculate_success_rate():.1f}%\n"
            result_text += f"평균 실행 시간: {performance.average_execution_time:.4f}초\n"
            result_text += f"코드 품질 점수: {performance.code_quality_score:.1f}/100\n\n"

            if not is_correct:
                result_text += "실패한 테스트 케이스:\n"
                for result in test_results:
                    if not result.is_passed:
                        result_text += f"입력: {result.input_data}\n"
                        result_text += f"기대: {result.expected_output}\n"
                        result_text += f"실제: {result.actual_output}\n"
                        if result.error_message:
                            result_text += f"오류: {result.error_message}\n"
                        result_text += "-" * 30 + "\n"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result_text)

            # 통계 업데이트
            if is_correct:
                self.refresh_statistics()
                self.refresh_challenges()
                self.notification_system.show_notification(
                    "축하합니다!",
                    "문제를 성공적으로 해결했습니다!",
                    "success",
                    5
                )

        except Exception as e:
            messagebox.showerror("오류", f"코드 실행 실패: {e}")

    def save_code(self):
        """코드 저장"""
        if not self.current_problem:
            messagebox.showwarning("경고", "먼저 문제를 선택하세요.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                initialfile=f"{self.current_problem.id}.py"
            )

            if filename:
                code = self.code_editor.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("성공", "코드가 저장되었습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"코드 저장 실패: {e}")

    def load_code(self):
        """코드 불러오기"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, code)
                messagebox.showinfo("성공", "코드가 불러와졌습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"코드 불러오기 실패: {e}")

    def schedule_updates(self):
        """주기적 업데이트 스케줄링"""
        # 30초마다 통계 업데이트
        self.root.after(30000, self.auto_refresh)

    def auto_refresh(self):
        """자동 새로고침"""
        try:
            self.refresh_statistics()
            self.refresh_challenges()
        except:
            pass
        finally:
            # 다음 업데이트 스케줄링
            self.root.after(30000, self.auto_refresh)

    def load_user_preferences(self):
        """사용자 설정 로드"""
        default_preferences = {
            'focus_duration': 25,
            'break_duration': 5,
            'blocking_enabled': True,
            'topmost_enabled': False,  # 창 최상위 유지 옵션
            'overlay_blocking': True,  # 오버레이 차단 모드 (고도화된 차단)
            'exit_problem_required': True,
            'auto_save': True,
            'notifications': True
        }

        try:
            config_file = os.path.join(os.path.dirname(__file__), 'user_preferences.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"설정 로드 오류: {e}")

        return default_preferences

    def save_user_preferences(self):
        """사용자 설정 저장"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'user_preferences.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 저장 오류: {e}")

    def refresh_focus_sessions(self):
        """포커스 세션 기록 새로고침"""
        try:
            # 기존 항목 삭제
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)

            # 세션 기록 표시
            for session in self.focus_sessions[-20:]:  # 최근 20개만 표시
                date_str = session.start_time.strftime("%Y-%m-%d %H:%M")
                duration_str = f"{session.duration // 60}분"
                problem_name = session.problem_id if session.problem_id else "일반 공부"
                completed_str = "완료" if session.completed else "미완료"

                self.sessions_tree.insert('', 'end',
                                        values=(date_str, duration_str, problem_name,
                                               completed_str, session.interruptions))

        except Exception as e:
            messagebox.showerror("오류", f"세션 기록 로드 실패: {e}")

    def suggest_next_problem(self):
        """다음 문제 추천"""
        try:
            if not self.current_problem:
                # 현재 문제가 없으면 추천 문제 중에서 선택
                recommendations = self.challenge_system.get_personalized_recommendations(1)
                if recommendations:
                    self.current_problem = recommendations[0]
                    self.load_problem_details()
                    messagebox.showinfo("다음 문제", f"다음 문제를 추천합니다:\n{self.current_problem.title}")
        except Exception as e:
            print(f"문제 추천 오류: {e}")

    def update_learning_progress(self):
        """학습 진도 업데이트"""
        try:
            if self.current_session and self.current_session.completed:
                # 세션 완료 시 학습 진도 업데이트
                self.refresh_statistics()
                self.refresh_challenges()

                # 성취도 체크
                stats = self.challenge_system.get_user_statistics()
                if stats['total_problems_solved'] % 10 == 0:  # 10문제마다
                    messagebox.showinfo("축하!", f"{stats['total_problems_solved']}문제를 해결했습니다!")
        except Exception as e:
            print(f"학습 진도 업데이트 오류: {e}")

    def load_problem_details(self):
        """문제 상세 정보 로드"""
        if not self.current_problem:
            return

        try:
            # 문제 상세 정보 표시
            self.problem_title_label.config(text=f"{self.current_problem.title} ({self.current_problem.difficulty.name})")

            description = f"설명: {self.current_problem.description}\n\n"
            description += f"입력 형식: {self.current_problem.input_format}\n"
            description += f"출력 형식: {self.current_problem.output_format}\n\n"
            description += "태그: " + ', '.join(tag.name for tag in self.current_problem.tags)

            self.problem_description_text.delete(1.0, tk.END)
            self.problem_description_text.insert(1.0, description)

            # 코드 템플릿 로드
            self.load_code_template()

        except Exception as e:
            messagebox.showerror("오류", f"문제 상세 정보 로드 실패: {e}")

    def on_closing(self):
        """창 닫기 이벤트 처리"""
        if self.user_preferences.get('exit_problem_required', True):
            # 종료 문제 생성
            self.exit_problem = self._create_exit_problem()
            if self.exit_problem:
                self._show_exit_problem_dialog()
            else:
                self._force_exit()
        else:
            self._force_exit()

    def _create_exit_problem(self):
        """종료용 문제 생성"""
        try:
            # 간단한 문제 생성
            problems = self.problem_provider.get_all_problems()
            if problems:
                return problems[0]  # 첫 번째 문제 사용
        except Exception as e:
            print(f"종료 문제 생성 오류: {e}")
        return None

    def _show_exit_problem_dialog(self):
        """종료 문제 다이얼로그 표시"""
        if not self.exit_problem:
            self._force_exit()
            return

        # 종료 문제 창 생성
        exit_window = tk.Toplevel(self.root)
        exit_window.title("프로그램 종료 - 문제 해결 필요")
        exit_window.geometry("600x500")
        exit_window.transient(self.root)
        exit_window.grab_set()
        exit_window.attributes('-topmost', True)

        # 문제 정보
        ttk.Label(exit_window, text="프로그램을 종료하려면 다음 문제를 해결하세요:",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Label(exit_window, text=f"문제: {self.exit_problem.title}",
                 font=('Arial', 10, 'bold')).pack(pady=5)

        # 문제 설명
        desc_frame = ttk.LabelFrame(exit_window, text="문제 설명", padding=10)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)

        desc_text = scrolledtext.ScrolledText(desc_frame, height=4, width=60)
        desc_text.pack(fill=tk.X)
        desc_text.insert(1.0, self.exit_problem.description)
        desc_text.config(state='disabled')

        # 코드 입력
        code_frame = ttk.LabelFrame(exit_window, text="해결 코드", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        code_editor = scrolledtext.ScrolledText(code_frame, height=8, width=60, font=('Consolas', 10))
        code_editor.pack(fill=tk.BOTH, expand=True)

        # 기본 코드 템플릿
        template = '''def solve():
    # 여기에 해결 코드를 작성하세요
    pass

if __name__ == "__main__":
    solve()
'''
        code_editor.insert(1.0, template)

        # 결과 표시
        result_frame = ttk.LabelFrame(exit_window, text="실행 결과", padding=10)
        result_frame.pack(fill=tk.X, padx=10, pady=5)

        result_text = scrolledtext.ScrolledText(result_frame, height=3, width=60)
        result_text.pack(fill=tk.X)

        def check_solution():
            """해결 확인"""
            try:
                code = code_editor.get(1.0, tk.END).strip()
                if not code:
                    messagebox.showwarning("경고", "코드를 입력하세요.")
                    return

                # 테스트 케이스 준비
                test_cases = []
                for tc in self.exit_problem.test_cases:
                    test_cases.append({
                        'input': tc.input_data,
                        'output': tc.expected_output
                    })

                # 코드 실행
                is_correct, test_results, performance = self.challenge_system.submit_solution(
                    self.exit_problem.id, code, "python", test_cases
                )

                if is_correct:
                    result_text.delete(1.0, tk.END)
                    result_text.insert(1.0, "✓ 정답입니다! 프로그램을 종료합니다.")
                    messagebox.showinfo("성공!", "문제를 해결했습니다. 프로그램을 종료합니다.")
                    self.exit_problem_solved = True
                    exit_window.destroy()
                    self._force_exit()
                else:
                    result_text.delete(1.0, tk.END)
                    result_text.insert(1.0, "✗ 오답입니다. 다시 시도하세요.")

            except Exception as e:
                messagebox.showerror("오류", f"코드 실행 실패: {e}")

        def skip_problem():
            """문제 건너뛰기"""
            if messagebox.askyesno("확인", "정말로 문제를 건너뛰고 종료하시겠습니까?"):
                exit_window.destroy()
                self._force_exit()

        # 버튼들
        button_frame = ttk.Frame(exit_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="해결 확인", command=check_solution).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="건너뛰기", command=skip_problem).pack(side=tk.LEFT, padx=5)

    def _force_exit(self):
        """강제 종료"""
        try:
            # 성능 최적화 시스템 정리
            self.memory_monitor.stop_monitoring()
            self.background_optimizer.stop_workers()
            self.database_optimizer.close()

            # 앱 차단 중지
            self.app_blocker.stop_blocking()

            # 알림 시스템 정리
            self.notification_system.stop_notification_system()

            # 사용자 설정 저장
            self.save_user_preferences()

            logger.info("FocusTimer 정상 종료")

        except Exception as e:
            logger.error(f"종료 중 오류: {e}")
        finally:
            self.root.destroy()

    # 타이머 관련 메서드들
    def start_timer(self):
        """타이머 시작"""
        if not self.timer_running:
            self.timer_running = True
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self.status_label.config(text="포커스 시간 진행 중..." if not self.is_break_time else "휴식 시간 진행 중...")

            # 포커스 세션 시작
            if not self.is_break_time:
                self.current_session = FocusSession(
                    datetime.now(),
                    self.timer_duration,
                    self.current_problem.id if self.current_problem else None
                )

                # 차단 시작
                if self.user_preferences.get('blocking_enabled', True):
                    self.app_blocker.start_blocking(self.root)
                    self.blocking_status_label.config(text="차단 활성", foreground='red')
                    # 사용자 설정에 따라 창을 최상위로 설정
                    if self.user_preferences.get('topmost_enabled', False):
                        self.root.attributes('-topmost', True)

            # 타이머 스레드 시작
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()

    def pause_timer(self):
        """타이머 일시정지"""
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(state='normal')
            self.pause_button.config(state='disabled')
            self.status_label.config(text="일시정지됨")

            # 차단 일시정지
            if not self.is_break_time:
                self.app_blocker.stop_blocking()
                self.blocking_status_label.config(text="차단 일시정지", foreground='orange')
                # 창 최상위 해제
                self.root.attributes('-topmost', False)

    def reset_timer(self):
        """타이머 리셋"""
        self.timer_running = False
        self.is_break_time = False
        self.remaining_time = self.timer_duration
        self.update_timer_display()
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.status_label.config(text="준비됨")

        # 차단 중지
        self.app_blocker.stop_blocking()
        self.blocking_status_label.config(text="차단 비활성", foreground='gray')

    def apply_timer_settings(self):
        """타이머 설정 적용"""
        try:
            focus_minutes = int(self.focus_duration_var.get())
            break_minutes = int(self.break_duration_var.get())

            self.timer_duration = focus_minutes * 60
            self.break_duration = break_minutes * 60

            # 사용자 설정 업데이트
            self.user_preferences['focus_duration'] = focus_minutes
            self.user_preferences['break_duration'] = break_minutes

            if not self.timer_running:
                self.remaining_time = self.timer_duration

            self.update_timer_display()
            self.notification_system.show_notification(
                "설정 완료",
                "타이머 설정이 적용되었습니다.",
                "success",
                3
            )

        except ValueError:
            self.notification_system.show_notification(
                "입력 오류",
                "올바른 숫자를 입력하세요.",
                "error",
                3
            )

    def timer_loop(self):
        """타이머 루프"""
        while self.timer_running and self.remaining_time > 0:
            time.sleep(1)
            self.remaining_time -= 1
            self.update_timer_display()

        if self.timer_running:  # 타이머가 완료됨
            self.timer_completed()

    def update_timer_display(self):
        """타이머 표시 업데이트"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # GUI 업데이트는 메인 스레드에서 실행
        self.root.after(0, lambda: self.timer_label.config(text=time_str))

    def timer_completed(self):
        """타이머 완료 처리"""
        self.timer_running = False

        if not self.is_break_time:
            # 포커스 시간 완료
            if self.current_session:
                self.current_session.complete(datetime.now())
                self.focus_sessions.append(self.current_session)

            self.is_break_time = True
            self.remaining_time = self.break_duration
            self.status_label.config(text="휴식 시간 시작!")

            # 차단 중지
            self.app_blocker.stop_blocking()
            self.blocking_status_label.config(text="휴식 중", foreground='green')

            self.notification_system.show_notification(
                "포커스 완료!",
                "포커스 시간이 완료되었습니다. 휴식 시간을 시작합니다.",
                "success",
                5
            )

            # 다음 문제 추천
            self.suggest_next_problem()

            # 휴식 타이머 자동 시작
            self.start_timer()
        else:
            # 휴식 시간 완료
            self.is_break_time = False
            self.remaining_time = self.timer_duration
            self.status_label.config(text="포커스 시간 준비!")

            # 차단 상태 초기화
            self.blocking_status_label.config(text="차단 비활성", foreground='gray')

            self.notification_system.show_notification(
                "휴식 완료!",
                "휴식 시간이 완료되었습니다. 다음 포커스 세션을 준비하세요.",
                "info",
                5
            )

            # 학습 진도 업데이트
            self.update_learning_progress()

            # 포커스 타이머 자동 시작
            self.start_timer()

        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')

    def _perform_memory_optimization(self):
        """메모리 최적화 수행"""
        try:
            logger.info("메모리 최적화 시작")

            # 가비지 컬렉션 실행
            collected = gc.collect()
            logger.info(f"가비지 컬렉션 완료: {collected}개 객체 정리")

            # 데이터베이스 캐시 정리
            self.database_optimizer._cleanup_cache()

            # 백그라운드 작업 큐 정리
            queue_size = self.background_optimizer.get_queue_size()
            if queue_size > 50:
                logger.warning(f"백그라운드 작업 큐가 큽니다: {queue_size}개")

            # 메모리 사용량 통계 로깅
            memory_stats = self.memory_monitor.get_memory_stats()
            logger.info(f"메모리 사용량: {memory_stats.get('percent', 0):.1f}%")

            # 알림 표시
            self.notification_system.show_notification(
                "메모리 최적화",
                f"메모리 최적화 완료 (사용량: {memory_stats.get('percent', 0):.1f}%)",
                "info"
            )

        except Exception as e:
            logger.error(f"메모리 최적화 오류: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        try:
            stats = {
                'memory': self.memory_monitor.get_memory_stats(),
                'database': self.database_optimizer.get_performance_stats(),
                'background_tasks': {
                    'queue_size': self.background_optimizer.get_queue_size(),
                    'active_workers': len(self.background_optimizer.worker_threads)
                },
                'focus_sessions': len(self.focus_sessions),
                'current_session': self.current_session is not None
            }
            return stats
        except Exception as e:
            logger.error(f"성능 통계 조회 오류: {e}")
            return {'error': str(e)}

    def optimize_performance(self):
        """전체 성능 최적화"""
        try:
            logger.info("전체 성능 최적화 시작")

            # 메모리 최적화
            self._perform_memory_optimization()

            # 데이터베이스 최적화
            self.database_optimizer.optimize_database()

            # 백그라운드 작업 정리
            queue_size = self.background_optimizer.get_queue_size()
            if queue_size > 20:
                logger.info(f"백그라운드 작업 큐 정리: {queue_size}개 작업")

            # 성능 통계 수집
            stats = self.get_performance_stats()

            # 알림 표시
            self.notification_system.show_notification(
                "성능 최적화",
                "전체 성능 최적화가 완료되었습니다.",
                "success"
            )

            logger.info("전체 성능 최적화 완료")
            return stats

        except Exception as e:
            logger.error(f"성능 최적화 오류: {e}")
            return {'error': str(e)}

    def save_focus_session_to_db(self, session: FocusSession):
        """포커스 세션을 데이터베이스에 저장"""
        try:
            data = [
                (session.start_time.isoformat(),
                 session.end_time.isoformat() if session.end_time else None,
                 session.duration,
                 session.problem_id,
                 session.completed,
                 session.interruptions,
                 session.actual_focus_time)
            ]

            # 백그라운드 작업으로 저장
            self.background_optimizer.add_task(
                "save_focus_session",
                lambda: self.database_optimizer.batch_insert("focus_sessions", data),
                priority=3
            )

        except Exception as e:
            logger.error(f"포커스 세션 저장 오류: {e}")

    def load_focus_sessions_from_db(self) -> List[FocusSession]:
        """데이터베이스에서 포커스 세션 로드"""
        try:
            query = """
                SELECT start_time, end_time, duration, problem_id, completed,
                       interruptions, actual_focus_time
                FROM focus_sessions
                ORDER BY start_time DESC
                LIMIT 100
            """

            results = self.database_optimizer.execute_query(query)
            sessions = []

            for row in results:
                session = FocusSession(
                    start_time=datetime.fromisoformat(row[0]),
                    duration=row[2],
                    problem_id=row[3]
                )
                session.completed = row[4]
                session.interruptions = row[5]
                session.actual_focus_time = row[6]

                if row[1]:  # end_time
                    session.end_time = datetime.fromisoformat(row[1])

                sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"포커스 세션 로드 오류: {e}")
            return []


def main():
    """메인 함수"""
    root = tk.Tk()
    app = IntegratedFocusTimer(root)

    # GUI 실행
    root.mainloop()


if __name__ == "__main__":
    main()