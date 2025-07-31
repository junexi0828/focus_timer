#!/usr/bin/env python3
"""
Focus Timer Enterprise GUI - 상업용 집중 모드 시스템
통합 GUI 인터페이스 + 시스템 레벨 보호 + 지속적 모니터링
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import datetime
import os
import sys
import signal
import random
import subprocess
import json
import hashlib
import fcntl
import stat
import socket
import urllib.request
import urllib.error
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil

# ----- 설정 -----
VERSION = "2.0.0"
PRODUCT_NAME = "Focus Timer Enterprise GUI"

# 시스템 경로
HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BACKUP_PATH = "/Library/Application Support/FocusTimer/hosts_backup"
STATE_PATH = "/Library/Application Support/FocusTimer/state.json"
LOCK_FILE = "/Library/Application Support/FocusTimer/focus_timer.lock"
LOG_PATH = "/var/log/FocusTimer/focus_timer.log"
PID_FILE = "/var/run/focus_timer.pid"

# 다중 차단 레이어 설정
WEBSITES_TO_BLOCK = [
    # YouTube 핵심 도메인
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
    "youtube-nocookie.com", "www.youtube-nocookie.com",

    # YouTube API 및 서비스
    "youtube.googleapis.com", "www.youtube.googleapis.com",
    "youtubei.googleapis.com", "www.youtubei.googleapis.com",

    # YouTube 미디어
    "yt3.ggpht.com", "i.ytimg.com", "ytimg.com", "www.ytimg.com",
    "googlevideo.com", "www.googlevideo.com",

    # YouTube Shorts
    "shorts.youtube.com", "www.shorts.youtube.com",

    # 추가 소셜 미디어 (선택적)
    "facebook.com", "www.facebook.com", "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "tiktok.com", "www.tiktok.com", "reddit.com", "www.reddit.com"
]

# 전역 상태
class FocusTimerState:
    def __init__(self):
        self.is_focus_mode = False
        self.focus_start_time = None
        self.focus_end_time = None
        self.is_blocked = False
        self.hosts_hash = None
        self.last_check = None
        self.block_count = 0
        self.bypass_attempts = 0
        self.difficulty_level = 1
        self.failed_attempts = 0

# 전역 인스턴스
state = FocusTimerState()
challenge = None

# ----- 로깅 시스템 -----
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.ensure_log_directory()

    def ensure_log_directory(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log(self, level, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        # 콘솔 출력
        print(log_entry)

        # 파일 로깅
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except:
            pass

logger = Logger(LOG_PATH)

# ----- 시스템 레벨 보호 -----
class SystemProtection:
    def __init__(self):
        self.original_hosts_permissions = None
        self.firewall_rules = []

    def backup_hosts_permissions(self):
        """hosts 파일 원본 권한 백업"""
        try:
            stat_info = os.stat(HOSTS_PATH)
            self.original_hosts_permissions = stat_info.st_mode
            logger.log("INFO", "hosts 파일 권한 백업 완료")
        except Exception as e:
            logger.log("ERROR", f"hosts 파일 권한 백업 실패: {e}")

    def lock_hosts_file(self):
        """hosts 파일을 읽기 전용으로 잠금"""
        try:
            os.chmod(HOSTS_PATH, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # 444
            logger.log("INFO", "hosts 파일 잠금 완료")
        except Exception as e:
            logger.log("ERROR", f"hosts 파일 잠금 실패: {e}")

    def unlock_hosts_file(self):
        """hosts 파일 잠금 해제"""
        try:
            if self.original_hosts_permissions:
                os.chmod(HOSTS_PATH, self.original_hosts_permissions)
            else:
                os.chmod(HOSTS_PATH, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 644
            logger.log("INFO", "hosts 파일 잠금 해제 완료")
        except Exception as e:
            logger.log("ERROR", f"hosts 파일 잠금 해제 실패: {e}")

# ----- 지속적 모니터링 -----
class HostsFileMonitor(FileSystemEventHandler):
    def __init__(self, focus_timer):
        self.focus_timer = focus_timer
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path == HOSTS_PATH:
            current_time = time.time()
            if current_time - self.last_modified > 1:  # 중복 이벤트 방지
                self.last_modified = current_time
                logger.log("WARNING", "hosts 파일 변경 감지됨")
                self.focus_timer.handle_hosts_modification()

class FocusTimerMonitor:
    def __init__(self):
        self.observer = None
        self.monitoring = False
        self.system_protection = SystemProtection()

    def start_monitoring(self):
        """파일 시스템 모니터링 시작"""
        try:
            self.observer = Observer()
            event_handler = HostsFileMonitor(self)
            self.observer.schedule(event_handler, path="/etc", recursive=False)
            self.observer.start()
            self.monitoring = True
            logger.log("INFO", "파일 시스템 모니터링 시작")
        except Exception as e:
            logger.log("ERROR", f"모니터링 시작 실패: {e}")

    def stop_monitoring(self):
        """파일 시스템 모니터링 중지"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.monitoring = False
            logger.log("INFO", "파일 시스템 모니터링 중지")

    def handle_hosts_modification(self):
        """hosts 파일 수정 처리"""
        if state.is_focus_mode and state.is_blocked:
            logger.log("WARNING", "집중 모드 중 hosts 파일 수정 시도 감지")
            state.bypass_attempts += 1

            # 자동으로 차단 재적용
            self.reapply_blocking()

            # 보안 강화
            self.enhance_security()

    def reapply_blocking(self):
        """차단 재적용"""
        try:
            # hosts 파일 잠금 해제
            self.system_protection.unlock_hosts_file()

            # 차단 설정 재적용
            block_websites()

            # hosts 파일 다시 잠금
            self.system_protection.lock_hosts_file()

            # DNS 캐시 초기화
            self.flush_dns_cache()

            logger.log("INFO", "차단 재적용 완료")

        except Exception as e:
            logger.log("ERROR", f"차단 재적용 실패: {e}")

    def enhance_security(self):
        """보안 강화"""
        try:
            # 브라우저 강제 재시작
            self.restart_browsers()

            # 시스템 알림
            self.send_system_notification("보안 경고", "집중 모드 중 차단 해제 시도가 감지되었습니다.")

            logger.log("INFO", "보안 강화 완료")

        except Exception as e:
            logger.log("ERROR", f"보안 강화 실패: {e}")

    def flush_dns_cache(self):
        """DNS 캐시 초기화"""
        try:
            subprocess.run(["sudo", "dscacheutil", "-flushcache"], check=True)
            subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], check=True)
            logger.log("INFO", "DNS 캐시 초기화 완료")
        except Exception as e:
            logger.log("ERROR", f"DNS 캐시 초기화 실패: {e}")

    def restart_browsers(self):
        """브라우저 강제 재시작"""
        browsers = ["Google Chrome", "Safari", "Firefox", "Whale", "Microsoft Edge"]

        for browser in browsers:
            try:
                # 브라우저 종료
                subprocess.run(["osascript", "-e", f'quit app "{browser}"'],
                             capture_output=True, timeout=5)
                time.sleep(2)

                # 강제 종료
                subprocess.run(["pkill", "-f", browser], capture_output=True)
                time.sleep(1)

                # 재시작
                subprocess.run(["open", "-a", browser], capture_output=True)
                time.sleep(3)

                logger.log("INFO", f"{browser} 재시작 완료")

            except Exception as e:
                logger.log("ERROR", f"{browser} 재시작 실패: {e}")

    def send_system_notification(self, title, message):
        """시스템 알림 전송"""
        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], capture_output=True)
        except:
            pass

# ----- 알고리즘 문제 시스템 -----
class AlgorithmChallenge:
    def __init__(self):
        self.difficulty_level = 1
        self.max_attempts = 3
        self.failed_attempts = 0

    def generate_problem(self):
        """난이도에 따른 알고리즘 문제 생성"""
        if self.difficulty_level == 1:
            # 기본 사칙연산
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            operation = random.choice(["+", "-", "*"])

            if operation == "+":
                answer = a + b
            elif operation == "-":
                answer = a - b
            else:
                answer = a * b

            return f"{a} {operation} {b} = ?", answer

        elif self.difficulty_level == 2:
            # 3자리 수 연산
            a = random.randint(100, 999)
            b = random.randint(10, 99)
            operation = random.choice(["+", "-", "*"])

            if operation == "+":
                answer = a + b
            elif operation == "-":
                answer = a - b
            else:
                answer = a * b

            return f"{a} {operation} {b} = ?", answer

        elif self.difficulty_level == 3:
            # 복합 연산
            a = random.randint(10, 50)
            b = random.randint(5, 20)
            c = random.randint(2, 10)

            answer = (a + b) * c
            return f"({a} + {b}) × {c} = ?", answer

        elif self.difficulty_level == 4:
            # 피보나치 수열
            n = random.randint(5, 10)
            fib_sequence = [0, 1]
            for i in range(2, n + 1):
                fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
            answer = fib_sequence[n]
            return f"피보나치 수열의 {n}번째 수는? (F(0)=0, F(1)=1)", answer

        else:  # 난이도 5
            # 정렬 알고리즘 문제
            numbers = [random.randint(1, 100) for _ in range(5)]
            sorted_numbers = sorted(numbers)
            answer = sorted_numbers[2]  # 중간값
            return f"숫자 {numbers}를 오름차순으로 정렬했을 때 중간값은?", answer

    def increase_difficulty(self):
        """난이도 증가"""
        if self.difficulty_level < 5:
            self.difficulty_level += 1
            logger.log("INFO", f"난이도가 {self.difficulty_level}로 증가")

    def ask_challenge(self):
        """알고리즘 문제 출제 및 정답 확인"""
        logger.log("INFO", f"난이도 {self.difficulty_level} 문제 출제")

        attempts = 0
        while attempts < self.max_attempts:
            problem, answer = self.generate_problem()
            print(f"\n📝 문제: {problem}")

            try:
                user_input = input("답: ").strip()

                if user_input.isdigit():
                    user_answer = int(user_input)
                else:
                    print("⚠️ 숫자를 입력해주세요.")
                    attempts += 1
                    continue

                if user_answer == answer:
                    logger.log("INFO", "문제 해결 성공")
                    return True
                else:
                    attempts += 1
                    remaining = self.max_attempts - attempts
                    print(f"❌ 오답입니다. 정답: {answer}")
                    if remaining > 0:
                        print(f"🔄 남은 시도: {remaining}")
                    else:
                        print("🚫 모든 시도 실패!")

            except KeyboardInterrupt:
                print("\n⚠️ 문제 풀이를 중단할 수 없습니다!")
                attempts += 1
            except:
                print("⚠️ 올바른 숫자를 입력해주세요.")
                attempts += 1

        # 모든 시도 실패
        self.failed_attempts += 1
        if self.failed_attempts >= 2:
            self.increase_difficulty()
            self.failed_attempts = 0

        logger.log("WARNING", "문제 해결 실패 - 종료 거부")
        return False

# ----- 다중 차단 레이어 -----
def block_websites():
    """다중 레이어 차단 적용"""
    try:
        # 1. hosts 파일 차단
        block_hosts_file()

        # 2. DNS 캐시 초기화
        flush_dns_cache()

        # 3. 브라우저 캐시 초기화
        clear_browser_cache()

        state.is_blocked = True
        state.block_count += 1
        logger.log("INFO", "다중 레이어 차단 적용 완료")

    except Exception as e:
        logger.log("ERROR", f"차단 적용 실패: {e}")

def unblock_websites():
    """다중 레이어 차단 해제"""
    try:
        # 1. hosts 파일 복구
        restore_hosts_file()

        # 2. DNS 캐시 초기화
        flush_dns_cache()

        state.is_blocked = False
        logger.log("INFO", "다중 레이어 차단 해제 완료")

    except Exception as e:
        logger.log("ERROR", f"차단 해제 실패: {e}")

def block_hosts_file():
    """hosts 파일에 차단 설정 추가"""
    try:
        with open(HOSTS_PATH, "r+") as file:
            lines = file.readlines()

            # FocusTimer 블록 시작/끝 마커
            block_start = "# FocusTimer Enterprise Block Start\n"
            block_end = "# FocusTimer Enterprise Block End\n"

            # 기존 블록 제거
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if line == block_start:
                    start_idx = i
                elif line == block_end:
                    end_idx = i
                    break

            if start_idx != -1 and end_idx != -1:
                lines = lines[:start_idx] + lines[end_idx + 1:]

            # 새로운 차단 설정 추가
            new_entries = [block_start]
            for site in WEBSITES_TO_BLOCK:
                new_entries.append(f"{REDIRECT_IP} {site}\n")
            new_entries.append(block_end)

            # 파일에 쓰기
            file.seek(0)
            file.writelines(lines + new_entries)
            file.truncate()
            file.flush()
            os.fsync(file.fileno())

            logger.log("INFO", "hosts 파일 차단 설정 완료")

    except Exception as e:
        logger.log("ERROR", f"hosts 파일 차단 실패: {e}")

def restore_hosts_file():
    """hosts 파일에서 차단 설정 제거"""
    try:
        with open(HOSTS_PATH, "r+") as file:
            lines = file.readlines()

            block_start = "# FocusTimer Enterprise Block Start\n"
            block_end = "# FocusTimer Enterprise Block End\n"

            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if line == block_start:
                    start_idx = i
                elif line == block_end:
                    end_idx = i
                    break

            if start_idx != -1 and end_idx != -1:
                new_lines = lines[:start_idx] + lines[end_idx + 1:]
                file.seek(0)
                file.writelines(new_lines)
                file.truncate()
                file.flush()
                os.fsync(file.fileno())

                logger.log("INFO", "hosts 파일 복구 완료")
            else:
                logger.log("INFO", "차단 설정이 없습니다.")

    except Exception as e:
        logger.log("ERROR", f"hosts 파일 복구 실패: {e}")

def flush_dns_cache():
    """DNS 캐시 초기화"""
    try:
        subprocess.run(["sudo", "dscacheutil", "-flushcache"], check=True)
        subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], check=True)
        logger.log("INFO", "DNS 캐시 초기화 완료")
    except Exception as e:
        logger.log("ERROR", f"DNS 캐시 초기화 실패: {e}")

def clear_browser_cache():
    """브라우저 캐시 초기화"""
    browsers = ["Google Chrome", "Safari", "Firefox", "Whale", "Microsoft Edge"]

    for browser in browsers:
        try:
            if browser == "Google Chrome":
                cache_paths = [
                    os.path.expanduser("~/Library/Caches/Google/Chrome/Default/Cache"),
                    os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cache")
                ]
            elif browser == "Safari":
                cache_paths = [
                    os.path.expanduser("~/Library/Caches/com.apple.Safari"),
                    os.path.expanduser("~/Library/Safari/LocalStorage")
                ]
            else:
                continue

            for path in cache_paths:
                if os.path.exists(path):
                    subprocess.run(["rm", "-rf", f"{path}/*"], capture_output=True)

            logger.log("INFO", f"{browser} 캐시 초기화 완료")

        except Exception as e:
            logger.log("ERROR", f"{browser} 캐시 초기화 실패: {e}")

# ----- 상태 관리 -----
def save_state():
    """상태 저장"""
    try:
        state_data = {
            "is_focus_mode": state.is_focus_mode,
            "focus_start_time": state.focus_start_time.isoformat() if state.focus_start_time else None,
            "focus_end_time": state.focus_end_time.isoformat() if state.focus_end_time else None,
            "is_blocked": state.is_blocked,
            "block_count": state.block_count,
            "bypass_attempts": state.bypass_attempts,
            "difficulty_level": challenge.difficulty_level if challenge else 1,
            "failed_attempts": challenge.failed_attempts if challenge else 0,
            "last_check": datetime.datetime.now().isoformat()
        }

        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w") as f:
            json.dump(state_data, f, indent=2)

        logger.log("INFO", "상태 저장 완료")

    except Exception as e:
        logger.log("ERROR", f"상태 저장 실패: {e}")

def load_state():
    """상태 불러오기"""
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH, "r") as f:
                state_data = json.load(f)

            state.is_focus_mode = state_data.get("is_focus_mode", False)
            state.is_blocked = state_data.get("is_blocked", False)
            state.block_count = state_data.get("block_count", 0)
            state.bypass_attempts = state_data.get("bypass_attempts", 0)

            if state_data.get("focus_start_time"):
                state.focus_start_time = datetime.datetime.fromisoformat(state_data["focus_start_time"])
            if state_data.get("focus_end_time"):
                state.focus_end_time = datetime.datetime.fromisoformat(state_data["focus_end_time"])

            if challenge:
                challenge.difficulty_level = state_data.get("difficulty_level", 1)
                challenge.failed_attempts = state_data.get("failed_attempts", 0)

            logger.log("INFO", "상태 불러오기 완료")

    except Exception as e:
        logger.log("ERROR", f"상태 불러오기 실패: {e}")

# ----- GUI 애플리케이션 -----
class FocusTimerGUI:
    def __init__(self):
        global challenge
        challenge = AlgorithmChallenge()
        self.monitor = FocusTimerMonitor()
        self.running = False
        self.monitor_thread = None

        # GUI 초기화
        self.root = tk.Tk()
        self.setup_gui()

        # 상태 불러오기
        load_state()

        # 시스템 보호 초기화
        self.monitor.system_protection.backup_hosts_permissions()

    def setup_gui(self):
        """GUI 설정"""
        self.root.title(f"{PRODUCT_NAME} v{VERSION}")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')

        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목
        title_label = ttk.Label(main_frame, text=f"🔒 {PRODUCT_NAME}",
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 상태 표시
        self.setup_status_frame(main_frame)

        # 제어 패널
        self.setup_control_frame(main_frame)

        # 통계 패널
        self.setup_stats_frame(main_frame)

        # 로그 패널
        self.setup_log_frame(main_frame)

        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def setup_status_frame(self, parent):
        """상태 프레임 설정"""
        status_frame = ttk.LabelFrame(parent, text="📊 현재 상태", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 상태 표시
        self.status_var = tk.StringVar(value="집중 모드 비활성화")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                font=('Helvetica', 12))
        status_label.grid(row=0, column=0, sticky=tk.W)

        # 시간 표시
        self.time_var = tk.StringVar(value="")
        time_label = ttk.Label(status_frame, textvariable=self.time_var,
                              font=('Helvetica', 10))
        time_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

    def setup_control_frame(self, parent):
        """제어 프레임 설정"""
        control_frame = ttk.LabelFrame(parent, text="🎯 집중 모드 제어", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))

        # 시작 시간
        ttk.Label(control_frame, text="시작 시간:").grid(row=0, column=0, sticky=tk.W)
        self.start_time_var = tk.StringVar(value="09:00")
        start_time_entry = ttk.Entry(control_frame, textvariable=self.start_time_var, width=10)
        start_time_entry.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)

        # 종료 시간
        ttk.Label(control_frame, text="종료 시간:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.end_time_var = tk.StringVar(value="18:00")
        end_time_entry = ttk.Entry(control_frame, textvariable=self.end_time_var, width=10)
        end_time_entry.grid(row=1, column=1, padx=(5, 0), pady=(5, 0), sticky=tk.W)

        # 난이도
        ttk.Label(control_frame, text="문제 난이도:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.difficulty_var = tk.IntVar(value=1)
        difficulty_combo = ttk.Combobox(control_frame, textvariable=self.difficulty_var,
                                       values=[1, 2, 3, 4, 5], width=7, state="readonly")
        difficulty_combo.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky=tk.W)

        # 버튼들
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        self.start_button = ttk.Button(button_frame, text="🚀 집중 모드 시작",
                                      command=self.start_focus_mode)
        self.start_button.grid(row=0, column=0, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="⏹️ 집중 모드 중지",
                                     command=self.stop_focus_mode)
        self.stop_button.grid(row=0, column=1, padx=(0, 5))

        self.manual_block_button = ttk.Button(button_frame, text="🔒 즉시 차단",
                                             command=self.manual_block)
        self.manual_block_button.grid(row=0, column=2, padx=(0, 5))

        self.manual_unblock_button = ttk.Button(button_frame, text="🔓 즉시 해제",
                                               command=self.manual_unblock)
        self.manual_unblock_button.grid(row=0, column=3)

    def setup_stats_frame(self, parent):
        """통계 프레임 설정"""
        stats_frame = ttk.LabelFrame(parent, text="📈 통계", padding="10")
        stats_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 10))

        # 차단 횟수
        ttk.Label(stats_frame, text="차단 횟수:").grid(row=0, column=0, sticky=tk.W)
        self.block_count_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.block_count_var,
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=1, padx=(10, 0))

        # 우회 시도
        ttk.Label(stats_frame, text="우회 시도:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.bypass_attempts_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.bypass_attempts_var,
                 font=('Helvetica', 12, 'bold')).grid(row=1, column=1, padx=(10, 0), pady=(5, 0))

        # 현재 난이도
        ttk.Label(stats_frame, text="현재 난이도:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.current_difficulty_var = tk.StringVar(value="1")
        ttk.Label(stats_frame, textvariable=self.current_difficulty_var,
                 font=('Helvetica', 12, 'bold')).grid(row=2, column=1, padx=(10, 0), pady=(5, 0))

    def setup_log_frame(self, parent):
        """로그 프레임 설정"""
        log_frame = ttk.LabelFrame(parent, text="📝 시스템 로그", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 로그 텍스트
        self.log_text = tk.Text(log_frame, height=10, width=80, font=('Courier', 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 로그 프레임 그리드 가중치
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def update_status(self):
        """상태 업데이트"""
        if state.is_focus_mode:
            if state.is_blocked:
                self.status_var.set("집중 모드 활성화 (차단 중)")
            else:
                self.status_var.set("집중 모드 활성화 (대기 중)")
        else:
            self.status_var.set("집중 모드 비활성화")

        # 시간 표시
        if state.focus_start_time and state.focus_end_time:
            start_str = state.focus_start_time.strftime("%H:%M")
            end_str = state.focus_end_time.strftime("%H:%M")
            self.time_var.set(f"설정 시간: {start_str} ~ {end_str}")
        else:
            self.time_var.set("")

        # 통계 업데이트
        self.block_count_var.set(str(state.block_count))
        self.bypass_attempts_var.set(str(state.bypass_attempts))
        self.current_difficulty_var.set(str(challenge.difficulty_level if challenge else 1))

    def update_log(self):
        """로그 업데이트"""
        try:
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, 'r') as f:
                    logs = f.readlines()[-20:]  # 최근 20줄

                self.log_text.delete(1.0, tk.END)
                for log in logs:
                    self.log_text.insert(tk.END, log)

                self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"로그 읽기 실패: {e}\n")

    def start_focus_mode(self):
        """집중 모드 시작"""
        try:
            # 시간 파싱
            start_time = self.start_time_var.get()
            end_time = self.end_time_var.get()

            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))

            # 상태 설정
            now = datetime.datetime.now()
            state.focus_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            state.focus_end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            state.is_focus_mode = True

            if challenge:
                challenge.difficulty_level = self.difficulty_var.get()

            save_state()

            # 모니터링 시작
            if not self.running:
                self.start_monitoring()

            messagebox.showinfo("성공", "집중 모드가 시작되었습니다!")
            self.update_status()

        except Exception as e:
            messagebox.showerror("오류", f"집중 모드 시작 실패: {e}")

    def stop_focus_mode(self):
        """집중 모드 중지"""
        try:
            state.is_focus_mode = False
            state.is_blocked = False

            # 차단 해제
            unblock_websites()

            save_state()

            messagebox.showinfo("성공", "집중 모드가 중지되었습니다!")
            self.update_status()

        except Exception as e:
            messagebox.showerror("오류", f"집중 모드 중지 실패: {e}")

    def manual_block(self):
        """수동 차단"""
        try:
            block_websites()
            messagebox.showinfo("성공", "웹사이트가 차단되었습니다!")
            self.update_status()
        except Exception as e:
            messagebox.showerror("오류", f"수동 차단 실패: {e}")

    def manual_unblock(self):
        """수동 해제"""
        try:
            unblock_websites()
            messagebox.showinfo("성공", "웹사이트 차단이 해제되었습니다!")
            self.update_status()
        except Exception as e:
            messagebox.showerror("오류", f"수동 해제 실패: {e}")

    def start_monitoring(self):
        """모니터링 시작"""
        if not self.running:
            self.running = True
            self.monitor.start_monitoring()

            # 모니터링 스레드 시작
            self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitor_thread.start()

    def monitoring_loop(self):
        """모니터링 루프"""
        while self.running:
            try:
                self.check_focus_time()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.log("ERROR", f"모니터링 루프 오류: {e}")

    def check_focus_time(self):
        """집중 시간 체크"""
        if not state.is_focus_mode:
            return

        now = datetime.datetime.now()
        current_time = now.time()

        if state.focus_start_time and state.focus_end_time:
            start_time = state.focus_start_time.time()
            end_time = state.focus_end_time.time()

            # 시간대 비교
            if start_time <= end_time:
                should_be_blocked = start_time <= current_time <= end_time
            else:
                should_be_blocked = current_time >= start_time or current_time <= end_time

            # 상태 변경 처리
            if state.is_blocked != should_be_blocked:
                if should_be_blocked:
                    block_websites()
                    self.monitor.system_protection.lock_hosts_file()
                    logger.log("INFO", "집중 모드 시작 - 차단 적용")
                else:
                    unblock_websites()
                    self.monitor.system_protection.unlock_hosts_file()
                    logger.log("INFO", "집중 모드 종료 - 차단 해제")

                state.is_blocked = should_be_blocked
                save_state()

    def run(self):
        """GUI 실행"""
        # 주기적 업데이트
        def update_loop():
            while True:
                try:
                    self.update_status()
                    self.update_log()
                    time.sleep(5)  # 5초마다 업데이트
                except:
                    break

        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

        # GUI 실행
        self.root.mainloop()

    def cleanup(self):
        """정리 작업"""
        try:
            self.running = False

            # 차단 해제
            if state.is_blocked:
                unblock_websites()

            # hosts 파일 잠금 해제
            self.monitor.system_protection.unlock_hosts_file()

            # 모니터링 중지
            self.monitor.stop_monitoring()

            # 상태 저장
            save_state()

            logger.log("INFO", "정리 작업 완료")

        except Exception as e:
            logger.log("ERROR", f"정리 작업 실패: {e}")

# ----- 메인 실행 -----
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️ 관리자 권한으로 실행해야 합니다: sudo python3 focus_timer_enterprise_gui.py")
        sys.exit(1)

    # 디렉토리 생성
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # GUI 애플리케이션 시작
    app = FocusTimerGUI()

    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.cleanup()