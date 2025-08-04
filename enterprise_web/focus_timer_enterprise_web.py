#!/usr/bin/env python3
"""
Focus Timer Enterprise Web - 상업용 집중 모드 시스템 (웹 인터페이스 통합)
시스템 레벨 보호 + 지속적 모니터링 + 다중 차단 레이어 + 웹 관리 인터페이스
"""

import time
import datetime
import os
import sys
import signal
import random
import subprocess
import threading
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
from flask import Flask, render_template, jsonify, request, redirect, url_for
import webbrowser

# ----- 설정 -----
VERSION = "2.0.0"
PRODUCT_NAME = "Focus Timer Enterprise Web"

# 시스템 경로
HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BACKUP_PATH = "/Library/Application Support/FocusTimer/hosts_backup"
STATE_PATH = "/Library/Application Support/FocusTimer/state.json"
LOCK_FILE = "/Library/Application Support/FocusTimer/focus_timer.lock"
LOG_PATH = "/var/log/FocusTimer/focus_timer.log"
PID_FILE = "/var/run/focus_timer.pid"

# 웹 인터페이스 설정
WEB_HOST = "127.0.0.1"
WEB_PORT = 8080
WEB_URL = f"http://{WEB_HOST}:{WEB_PORT}"

# 다중 차단 레이어 설정
WEBSITES_TO_BLOCK = [
    # YouTube 핵심 도메인
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    # YouTube API 및 서비스
    "youtube.googleapis.com",
    "www.youtube.googleapis.com",
    "youtubei.googleapis.com",
    "www.youtubei.googleapis.com",
    # YouTube 미디어
    "yt3.ggpht.com",
    "i.ytimg.com",
    "ytimg.com",
    "www.ytimg.com",
    "googlevideo.com",
    "www.googlevideo.com",
    # YouTube Shorts
    "shorts.youtube.com",
    "www.shorts.youtube.com",
    # 추가 소셜 미디어 (선택적)
    "facebook.com",
    "www.facebook.com",
    "instagram.com",
    "www.instagram.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "tiktok.com",
    "www.tiktok.com",
    "reddit.com",
    "www.reddit.com",
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
        self.web_interface_enabled = True


# 전역 인스턴스
state = FocusTimerState()
challenge = None
web_app = None


# ----- Flask 웹 애플리케이션 -----
def create_flask_app():
    """Flask 웹 애플리케이션 생성"""
    template_dir = "/Applications/FocusTimer/web/templates"
    app = Flask(__name__, template_folder=template_dir)

    @app.route("/")
    def index():
        """메인 페이지"""
        return render_template("index.html", product_name=PRODUCT_NAME, version=VERSION)

    @app.route("/api/status")
    def get_status():
        """현재 상태 조회"""
        try:
            status_data = {
                "is_focus_mode": state.is_focus_mode,
                "is_blocked": state.is_blocked,
                "block_count": state.block_count,
                "bypass_attempts": state.bypass_attempts,
                "difficulty_level": challenge.difficulty_level if challenge else 1,
                "failed_attempts": challenge.failed_attempts if challenge else 0,
                "last_check": (
                    state.last_check.isoformat() if state.last_check else None
                ),
            }

            if state.focus_start_time:
                status_data["focus_start_time"] = state.focus_start_time.strftime(
                    "%H:%M"
                )
            if state.focus_end_time:
                status_data["focus_end_time"] = state.focus_end_time.strftime("%H:%M")

            return jsonify(status_data)
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/start", methods=["POST"])
    def start_focus_mode():
        """집중 모드 시작"""
        try:
            data = request.json
            start_time = data.get("start_time", "09:00")
            end_time = data.get("end_time", "18:00")
            difficulty = data.get("difficulty", 1)

            # 시간 파싱
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))

            # 상태 설정
            now = datetime.datetime.now()
            state.focus_start_time = now.replace(
                hour=start_hour, minute=start_minute, second=0, microsecond=0
            )
            state.focus_end_time = now.replace(
                hour=end_hour, minute=end_minute, second=0, microsecond=0
            )
            state.is_focus_mode = True

            if challenge:
                challenge.difficulty_level = difficulty

            save_state()

            return jsonify({"success": True, "message": "집중 모드가 시작되었습니다."})
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/stop", methods=["POST"])
    def stop_focus_mode():
        """집중 모드 중지"""
        try:
            state.is_focus_mode = False
            state.is_blocked = False

            # 차단 해제
            unblock_websites()

            save_state()

            return jsonify({"success": True, "message": "집중 모드가 중지되었습니다."})
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/settings", methods=["GET", "POST"])
    def settings():
        """설정 관리"""
        if request.method == "GET":
            try:
                if os.path.exists(STATE_PATH):
                    with open(STATE_PATH, "r") as f:
                        settings_data = json.load(f)
                    return jsonify(settings_data)
                else:
                    return jsonify({})
            except Exception as e:
                return jsonify({"error": str(e)})
        else:
            try:
                data = request.json
                # 설정 저장 로직
                save_state()
                return jsonify({"success": True, "message": "설정이 저장되었습니다."})
            except Exception as e:
                return jsonify({"error": str(e)})

    @app.route("/api/logs")
    def get_logs():
        """로그 조회"""
        try:
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, "r") as f:
                    logs = f.readlines()[-50:]  # 최근 50줄
                return jsonify({"logs": logs})
            else:
                return jsonify({"logs": []})
        except Exception as e:
            return jsonify({"error": str(e)})

    return app


# ----- HTML 템플릿 -----
def create_html_template():
    """HTML 템플릿 생성"""
    template_dir = "/Applications/FocusTimer/web/templates"
    os.makedirs(template_dir, exist_ok=True)

    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Focus Timer Enterprise - 관리자 패널</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-active { background: #4CAF50; }
        .status-inactive { background: #f44336; }
        .control-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .control-section {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover { background: #45a049; }
        button.danger { background: #f44336; }
        button.danger:hover { background: #da190b; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .logs {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 2px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Focus Timer Enterprise</h1>
            <p>상업용 집중 모드 관리 시스템</p>
        </div>

        <div class="status-card">
            <h3>📊 현재 상태</h3>
            <div id="status-display">
                <span class="status-indicator status-inactive"></span>
                <span id="status-text">로딩 중...</span>
            </div>
        </div>

        <div class="control-panel">
            <div class="control-section">
                <h3>🎯 집중 모드 제어</h3>
                <div class="form-group">
                    <label>시작 시간:</label>
                    <input type="time" id="start-time" value="09:00">
                </div>
                <div class="form-group">
                    <label>종료 시간:</label>
                    <input type="time" id="end-time" value="18:00">
                </div>
                <div class="form-group">
                    <label>문제 난이도:</label>
                    <select id="difficulty">
                        <option value="1">1 - 기본 사칙연산</option>
                        <option value="2">2 - 3자리 수 연산</option>
                        <option value="3">3 - 복합 연산</option>
                        <option value="4">4 - 피보나치 수열</option>
                        <option value="5">5 - 정렬 알고리즘</option>
                    </select>
                </div>
                <button onclick="startFocusMode()">🚀 집중 모드 시작</button>
                <button class="danger" onclick="stopFocusMode()">⏹️ 집중 모드 중지</button>
            </div>

            <div class="control-section">
                <h3>📈 통계</h3>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="block-count">0</div>
                        <div>차단 횟수</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="bypass-attempts">0</div>
                        <div>우회 시도</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="difficulty-level">1</div>
                        <div>현재 난이도</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="control-section">
            <h3>📝 시스템 로그</h3>
            <div class="logs" id="logs-display">
                로그를 불러오는 중...
            </div>
        </div>
    </div>

    <script>
        // 상태 업데이트
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusIndicator = document.querySelector('.status-indicator');
                    const statusText = document.getElementById('status-text');

                    if (data.is_focus_mode && data.is_blocked) {
                        statusIndicator.className = 'status-indicator status-active';
                        statusText.textContent = '집중 모드 활성화 (차단 중)';
                    } else if (data.is_focus_mode) {
                        statusIndicator.className = 'status-indicator status-active';
                        statusText.textContent = '집중 모드 활성화 (대기 중)';
                    } else {
                        statusIndicator.className = 'status-indicator status-inactive';
                        statusText.textContent = '집중 모드 비활성화';
                    }

                    document.getElementById('block-count').textContent = data.block_count || 0;
                    document.getElementById('bypass-attempts').textContent = data.bypass_attempts || 0;
                    document.getElementById('difficulty-level').textContent = data.difficulty_level || 1;
                })
                .catch(error => console.error('상태 업데이트 실패:', error));
        }

        // 집중 모드 시작
        function startFocusMode() {
            const startTime = document.getElementById('start-time').value;
            const endTime = document.getElementById('end-time').value;
            const difficulty = document.getElementById('difficulty').value;

            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    start_time: startTime,
                    end_time: endTime,
                    difficulty: parseInt(difficulty)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('집중 모드가 시작되었습니다!');
                    updateStatus();
                } else {
                    alert('오류: ' + data.error);
                }
            })
            .catch(error => {
                alert('요청 실패: ' + error);
            });
        }

        // 집중 모드 중지
        function stopFocusMode() {
            if (!confirm('정말로 집중 모드를 중지하시겠습니까?')) return;

            fetch('/api/stop', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('집중 모드가 중지되었습니다!');
                    updateStatus();
                } else {
                    alert('오류: ' + data.error);
                }
            })
            .catch(error => {
                alert('요청 실패: ' + error);
            });
        }

        // 로그 업데이트
        function updateLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    const logsDisplay = document.getElementById('logs-display');
                    if (data.logs) {
                        logsDisplay.innerHTML = data.logs.map(log =>
                            `<div class="log-entry">${log}</div>`
                        ).join('');
                        logsDisplay.scrollTop = logsDisplay.scrollHeight;
                    }
                })
                .catch(error => console.error('로그 업데이트 실패:', error));
        }

        // 초기화 및 주기적 업데이트
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus();
            updateLogs();

            // 5초마다 상태 업데이트
            setInterval(updateStatus, 5000);
            setInterval(updateLogs, 10000);
        });
    </script>
</body>
</html>"""

    with open(f"{template_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)


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
                os.chmod(
                    HOSTS_PATH,
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
                )  # 644
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
            self.send_system_notification(
                "보안 경고", "집중 모드 중 차단 해제 시도가 감지되었습니다."
            )

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
                subprocess.run(
                    ["osascript", "-e", f'quit app "{browser}"'],
                    capture_output=True,
                    timeout=5,
                )
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
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'display notification "{message}" with title "{title}"',
                ],
                capture_output=True,
            )
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
                fib_sequence.append(fib_sequence[i - 1] + fib_sequence[i - 2])
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
                lines = lines[:start_idx] + lines[end_idx + 1 :]

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
                new_lines = lines[:start_idx] + lines[end_idx + 1 :]
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
                    os.path.expanduser(
                        "~/Library/Application Support/Google/Chrome/Default/Cache"
                    ),
                ]
            elif browser == "Safari":
                cache_paths = [
                    os.path.expanduser("~/Library/Caches/com.apple.Safari"),
                    os.path.expanduser("~/Library/Safari/LocalStorage"),
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
            "focus_start_time": (
                state.focus_start_time.isoformat() if state.focus_start_time else None
            ),
            "focus_end_time": (
                state.focus_end_time.isoformat() if state.focus_end_time else None
            ),
            "is_blocked": state.is_blocked,
            "block_count": state.block_count,
            "bypass_attempts": state.bypass_attempts,
            "difficulty_level": challenge.difficulty_level if challenge else 1,
            "failed_attempts": challenge.failed_attempts if challenge else 0,
            "web_interface_enabled": state.web_interface_enabled,
            "last_check": datetime.datetime.now().isoformat(),
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
            state.web_interface_enabled = state_data.get("web_interface_enabled", True)

            if state_data.get("focus_start_time"):
                state.focus_start_time = datetime.datetime.fromisoformat(
                    state_data["focus_start_time"]
                )
            if state_data.get("focus_end_time"):
                state.focus_end_time = datetime.datetime.fromisoformat(
                    state_data["focus_end_time"]
                )

            if challenge:
                challenge.difficulty_level = state_data.get("difficulty_level", 1)
                challenge.failed_attempts = state_data.get("failed_attempts", 0)

            logger.log("INFO", "상태 불러오기 완료")

    except Exception as e:
        logger.log("ERROR", f"상태 불러오기 실패: {e}")


# ----- 메인 클래스 -----
class FocusTimerEnterpriseWeb:
    def __init__(self):
        global challenge, web_app
        challenge = AlgorithmChallenge()
        self.monitor = FocusTimerMonitor()
        self.running = False
        self.web_thread = None

    def start_web_interface(self):
        """웹 인터페이스 시작"""
        try:
            # HTML 템플릿 생성
            create_html_template()

            # Flask 앱 생성
            web_app = create_flask_app()

            # 웹 서버 시작
            logger.log("INFO", f"웹 인터페이스 시작: {WEB_URL}")
            web_app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)

        except Exception as e:
            logger.log("ERROR", f"웹 인터페이스 시작 실패: {e}")

    def start(self):
        """Focus Timer Enterprise Web 시작"""
        logger.log("INFO", f"{PRODUCT_NAME} v{VERSION} 시작")

        # 상태 불러오기
        load_state()

        # 시스템 보호 초기화
        self.monitor.system_protection.backup_hosts_permissions()

        # 모니터링 시작
        self.monitor.start_monitoring()

        # 웹 인터페이스 시작 (별도 스레드)
        if state.web_interface_enabled:
            self.web_thread = threading.Thread(
                target=self.start_web_interface, daemon=True
            )
            self.web_thread.start()

            # 브라우저에서 웹 인터페이스 열기
            time.sleep(2)
            try:
                webbrowser.open(WEB_URL)
            except:
                pass

        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.running = True

        # 메인 루프
        try:
            while self.running:
                self.check_focus_time()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

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
                should_be_blocked = (
                    current_time >= start_time or current_time <= end_time
                )

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

    def signal_handler(self, sig, frame):
        """시그널 핸들러"""
        logger.log("INFO", "종료 시도 감지")

        if state.is_focus_mode and state.is_blocked:
            logger.log("WARNING", "집중 모드 중 종료 시도")

            if challenge.ask_challenge():
                logger.log("INFO", "문제 해결 성공 - 종료 허용")
                self.cleanup()
            else:
                logger.log("WARNING", "문제 해결 실패 - 종료 거부")
                save_state()
        else:
            logger.log("INFO", "집중 모드가 아닙니다 - 종료 허용")
            self.cleanup()

    def cleanup(self):
        """정리 작업"""
        try:
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
            self.running = False

        except Exception as e:
            logger.log("ERROR", f"정리 작업 실패: {e}")


# ----- 메인 실행 -----
if __name__ == "__main__":
    if os.geteuid() != 0:
        print(
            "⚠️ 관리자 권한으로 실행해야 합니다: sudo python3 focus_timer_enterprise_web.py"
        )
        sys.exit(1)

    # 디렉토리 생성
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # Focus Timer Enterprise Web 시작
    focus_timer = FocusTimerEnterpriseWeb()
    focus_timer.start()
