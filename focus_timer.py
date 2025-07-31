import time
import datetime
import os
import sys
import signal
import random
import subprocess
import threading
import json

# ----- 설정 -----
# YouTube 차단 도메인 목록 (최적화된 버전)
#
# 포함된 도메인:
# - 핵심 YouTube 도메인: 실제 콘텐츠 로딩에 필수
# - API 서비스: YouTube 기능 작동에 필요
# - 미디어 서버: 썸네일, 이미지, 비디오 스트리밍
# - Shorts: 모바일 최적화 콘텐츠
#
# 제외된 도메인:
# - music.youtube.com, studio.youtube.com 등: UI/브랜딩용 서브도메인
# - www.youtu.be: 일반적으로 사용되지 않음
# - 기타 서브도메인: 실제 콘텐츠 로딩과 무관
WEBSITES_TO_BLOCK = [
    # 핵심 YouTube 도메인 (실제 콘텐츠 로딩)
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

    # YouTube 미디어 및 이미지
    "yt3.ggpht.com",
    "i.ytimg.com",
    "ytimg.com",
    "www.ytimg.com",

    # YouTube 비디오 스트리밍
    "googlevideo.com",
    "www.googlevideo.com",

    # YouTube Shorts (실제 사용되는 서브도메인)
    "shorts.youtube.com",
    "www.shorts.youtube.com"
]
HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BACKUP_PATH = os.path.expanduser("~/hosts_backup")  # 홈 디렉토리에 저장
STATE_PATH = os.path.expanduser("~/focus_timer_state")  # 상태 파일 경로
LOCK_FILE = os.path.expanduser("~/focus_timer.lock")  # 락 파일 경로

# 전역 상태 추적 변수
was_unblocked = False  # 한 번이라도 해제된 적이 있는지 추적
is_focus_mode = False  # 집중 모드 활성화 상태
focus_start_time = None  # 집중 모드 시작 시간
focus_end_time = None  # 집중 모드 종료 시간
exit_allowed = False  # 종료 허용 상태

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
            else:  # "*"
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
            else:  # "*"
                answer = a * b

            return f"{a} {operation} {b} = ?", answer

        elif self.difficulty_level == 3:
            # 복합 연산
            a = random.randint(10, 50)
            b = random.randint(5, 20)
            c = random.randint(2, 10)

            # (a + b) * c 형태
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
            print(f"🔥 난이도가 {self.difficulty_level}로 증가했습니다!")

    def ask_challenge(self):
        """알고리즘 문제 출제 및 정답 확인"""
        print(f"\n🔐 집중 모드 종료를 위해 난이도 {self.difficulty_level} 문제를 풀어야 합니다!")
        print("💡 정답을 맞추면 종료할 수 있습니다.")

        attempts = 0
        while attempts < self.max_attempts:
            problem, answer = self.generate_problem()
            print(f"\n📝 문제: {problem}")

            try:
                user_input = input("답: ").strip()

                # 숫자만 추출
                if user_input.isdigit():
                    user_answer = int(user_input)
                else:
                    print("⚠️ 숫자를 입력해주세요.")
                    attempts += 1
                    continue

                if user_answer == answer:
                    print("✅ 정답입니다! 집중 모드를 종료합니다.")
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

        print("🚫 종료가 거부되었습니다. 다시 집중하세요!")
        return False

# 전역 알고리즘 문제 인스턴스
challenge = AlgorithmChallenge()

# ----- 프로세스 관리 -----
def create_lock_file():
    """락 파일 생성"""
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except:
        return False

def remove_lock_file():
    """락 파일 제거"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        return True
    except:
        return False

def is_already_running():
    """이미 실행 중인지 확인"""
    if not os.path.exists(LOCK_FILE):
        return False

    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())

        # 프로세스가 실제로 실행 중인지 확인
        try:
            os.kill(pid, 0)  # 프로세스 존재 확인
            return True
        except OSError:
            # 프로세스가 없으면 락 파일 제거
            remove_lock_file()
            return False
    except:
        return False

def restart_browsers():
    """실행 중인 브라우저를 강제로 재시작"""
    browsers = ["Google Chrome", "Safari", "Firefox", "Whale", "Microsoft Edge"]

    print("🔄 브라우저를 강제 재시작합니다...")

    for browser in browsers:
        try:
            # 브라우저가 실행 중인지 확인
            if sys.platform.startswith("darwin"):  # macOS
                result = subprocess.run(["pgrep", "-f", browser], capture_output=True)
                if result.returncode == 0:
                    print(f"🔄 {browser} 재시작 중...")

                    # 브라우저 종료
                    subprocess.run(["osascript", "-e", f'quit app "{browser}"'],
                                 capture_output=True, timeout=5)
                    time.sleep(2)

                    # 브라우저 재시작
                    subprocess.run(["open", "-a", browser], capture_output=True)
                    time.sleep(3)

                    print(f"✅ {browser} 재시작 완료")

        except Exception as e:
            print(f"⚠️ {browser} 재시작 중 오류: {e}")

def force_browser_restart_with_focus():
    """집중 모드용 브라우저 강제 재시작"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🔄 집중 모드: 브라우저 강제 재시작 중... ({', '.join(running_browsers)})")

        for browser in running_browsers:
            try:
                # 브라우저를 강제 종료
                if sys.platform.startswith("darwin"):  # macOS
                    subprocess.run(["osascript", "-e", f'quit app "{browser}"'],
                                 capture_output=True, timeout=5)
                    time.sleep(2)

                    # 여전히 실행 중이면 강제 종료
                    result = subprocess.run(["pgrep", "-f", browser], capture_output=True)
                    if result.returncode == 0:
                        subprocess.run(["pkill", "-f", browser], capture_output=True)
                        time.sleep(1)

                    # 브라우저 재시작
                    subprocess.run(["open", "-a", browser], capture_output=True)
                    time.sleep(3)

                    print(f"✅ {browser} 강제 재시작 완료")

            except Exception as e:
                print(f"⚠️ {browser} 강제 재시작 중 오류: {e}")

        print("✅ 모든 브라우저 강제 재시작 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 강제 재시작 중 오류: {e}")

# ----- 상태 관리 -----
def save_focus_state():
    """집중 모드 상태 저장"""
    try:
        state = {
            "is_focus_mode": is_focus_mode,
            "focus_start_time": focus_start_time.isoformat() if focus_start_time else None,
            "focus_end_time": focus_end_time.isoformat() if focus_end_time else None,
            "difficulty_level": challenge.difficulty_level,
            "failed_attempts": challenge.failed_attempts
        }

        with open(os.path.expanduser("~/focus_timer_focus_state.json"), "w") as f:
            json.dump(state, f)
    except:
        pass

def load_focus_state():
    """집중 모드 상태 불러오기"""
    global is_focus_mode, focus_start_time, focus_end_time

    try:
        with open(os.path.expanduser("~/focus_timer_focus_state.json"), "r") as f:
            state = json.load(f)

        is_focus_mode = state.get("is_focus_mode", False)
        focus_start_time = datetime.datetime.fromisoformat(state["focus_start_time"]) if state.get("focus_start_time") else None
        focus_end_time = datetime.datetime.fromisoformat(state["focus_end_time"]) if state.get("focus_end_time") else None

        if state.get("difficulty_level"):
            challenge.difficulty_level = state["difficulty_level"]
        if state.get("failed_attempts"):
            challenge.failed_attempts = state["failed_attempts"]

    except:
        is_focus_mode = False
        focus_start_time = None
        focus_end_time = None

def parse_time_input(time_input):
    """시간 입력을 파싱하여 시간과 분을 반환"""
    try:
        # 시간:분 형식 (예: 9:30)
        if ":" in time_input:
            parts = time_input.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            # 소수점 형식 (예: 9.5 -> 9:30)
            time_float = float(time_input)
            hour = int(time_float)
            minute = int((time_float - hour) * 60)

        # 유효성 검사
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("시간이 범위를 벗어났습니다.")

        return hour, minute

    except (ValueError, IndexError):
        print("❌ 잘못된 시간 형식입니다. 예: 9, 9:30, 9.5")
        return parse_time_input(input("다시 입력해주세요: ").strip())

def is_within_focus_time():
    """현재 시간이 집중 시간대에 속하는지 확인"""
    if not is_focus_mode or not focus_start_time or not focus_end_time:
        return False

    now = datetime.datetime.now()
    current_time = now.time()
    start_time = focus_start_time.time()
    end_time = focus_end_time.time()

    if start_time <= end_time:
        # 같은 날 내의 시간대 (예: 9시 ~ 18시)
        return start_time <= current_time <= end_time
    else:
        # 자정을 넘는 시간대 (예: 22시 ~ 6시)
        return current_time >= start_time or current_time <= end_time

# ----- 함수 -----
def save_state():
    """상태를 파일에 저장"""
    try:
        with open(STATE_PATH, "w") as f:
            f.write(str(was_unblocked))
    except:
        pass

def load_state():
    """파일에서 상태를 불러옴"""
    global was_unblocked
    try:
        with open(STATE_PATH, "r") as f:
            was_unblocked = f.read().strip() == "True"
    except:
        was_unblocked = False

def get_running_browsers():
    """현재 실행 중인 브라우저 목록을 반환"""
    running_browsers = []

    browsers = [
        "Google Chrome",
        "Safari",
        "Firefox",
        "Whale",
        "Microsoft Edge"
    ]

    for browser in browsers:
        if browser == "Safari":
            # Safari는 실제 브라우저 프로세스만 확인
            result = os.system("pgrep -f 'Safari.app/Contents/MacOS/Safari' >/dev/null 2>&1")
        else:
            # 다른 브라우저는 기존 방식
            result = os.system(f"pgrep -f '{browser}' >/dev/null 2>&1")

        if result == 0:  # 실행 중이면
            running_browsers.append(browser)

    return running_browsers

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

        # Firefox 캐시 초기화
        if "Firefox" in running_browsers:
            firefox_paths = [
                os.path.expanduser("~/Library/Caches/Firefox/Profiles"),
                os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
            ]
            for path in firefox_paths:
                if os.path.exists(path):
                    os.system(f"find {path} -name 'cache2' -type d -exec rm -rf {{}} +")

        # Whale 브라우저 캐시 초기화
        if "Whale" in running_browsers:
            whale_paths = [
                os.path.expanduser("~/Library/Caches/com.naver.whale"),
                os.path.expanduser("~/Library/Application Support/Naver/Whale/Default/Cache")
            ]
            for path in whale_paths:
                if os.path.exists(path):
                    os.system(f"rm -rf {path}/*")

        # Edge 캐시 초기화
        if "Microsoft Edge" in running_browsers:
            edge_paths = [
                os.path.expanduser("~/Library/Caches/com.microsoft.edgemac"),
                os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Cache")
            ]
            for path in edge_paths:
                if os.path.exists(path):
                    os.system(f"rm -rf {path}/*")

        # 시스템 DNS 캐시 초기화
        os.system("sudo dscacheutil -flushcache")
        os.system("sudo killall -HUP mDNSResponder")

        print("✅ 브라우저 캐시 초기화 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 캐시 초기화 중 오류: {e}")

def force_browser_cache_clear():
    """실행 중인 브라우저의 캐시만 초기화 (브라우저 종료 없이)"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🧹 브라우저 캐시 초기화 중... ({', '.join(running_browsers)})")

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

        print("✅ 브라우저 캐시 초기화 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 캐시 초기화 중 오류: {e}")

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
                if browser in ["Google Chrome", "Microsoft Edge", "Whale"]:
                    # Chromium 기반 브라우저: 동적으로 캐시 경로 찾기
                    possible_paths = [
                        os.path.expanduser("~/Library/Caches/Google/Chrome/Default/Cache"),
                        os.path.expanduser("~/Library/Caches/Google/Chrome/Default/Code Cache"),
                        os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cache"),
                        os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Code Cache"),
                        os.path.expanduser("~/Library/Caches/Microsoft/Edge/Default/Cache"),
                        os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Cache"),
                        os.path.expanduser("~/Library/Caches/com.naver.whale"),
                        os.path.expanduser("~/Library/Application Support/Naver/Whale/Default/Cache")
                    ]

                    for path in possible_paths:
                        if os.path.exists(path):
                            os.system(f"rm -rf {path}/* 2>/dev/null")
                            print(f"  📁 {path} 삭제됨")

                elif browser == "Safari":
                    possible_paths = [
                        os.path.expanduser("~/Library/Caches/com.apple.Safari"),
                        os.path.expanduser("~/Library/Safari/LocalStorage"),
                        os.path.expanduser("~/Library/Safari/WebpageIcons.db"),
                        os.path.expanduser("~/Library/Caches/WebKit")
                    ]

                    for path in possible_paths:
                        if os.path.exists(path):
                            if os.path.isfile(path):
                                os.system(f"rm -f {path} 2>/dev/null")
                            else:
                                os.system(f"rm -rf {path}/* 2>/dev/null")
                            print(f"  📁 {path} 삭제됨")

                elif browser == "Firefox":
                    firefox_profiles_path = os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
                    if os.path.exists(firefox_profiles_path):
                        os.system(f"find {firefox_profiles_path} -name 'cache2' -type d -exec rm -rf {{}} + 2>/dev/null")
                        print(f"  📁 Firefox cache2 디렉토리들 삭제됨")

                else:
                    browser_lower = browser.lower().replace(" ", "")
                    possible_paths = [
                        os.path.expanduser(f"~/Library/Caches/{browser_lower}"),
                        os.path.expanduser(f"~/Library/Application Support/{browser_lower}"),
                        os.path.expanduser(f"~/Library/Caches/com.{browser_lower}")
                    ]

                    for path in possible_paths:
                        if os.path.exists(path):
                            os.system(f"rm -rf {path}/* 2>/dev/null")
                            print(f"  📁 {path} 삭제됨")

                # 2단계: 시스템 DNS 캐시 초기화
                os.system("sudo dscacheutil -flushcache 2>/dev/null")
                os.system("sudo killall -HUP mDNSResponder 2>/dev/null")

                # 3단계: 브라우저 메모리 DNS 캐시 초기화 (세션 보존 재시작)
                print(f"  🔄 {browser} 메모리 DNS 캐시 초기화 중...")

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

def save_browser_sessions():
    """브라우저 세션 정보를 저장 (간단한 버전)"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        # 실행 중인 브라우저 목록만 저장
        session_info = {
            "running_browsers": running_browsers,
            "timestamp": datetime.datetime.now().isoformat()
        }

        # 세션 정보를 파일에 저장
        with open(os.path.expanduser("~/focus_timer_sessions.json"), "w") as f:
            import json
            json.dump(session_info, f)

        print(f"✅ 브라우저 세션 정보 저장 완료 ({len(running_browsers)}개 브라우저)")

    except Exception as e:
        print(f"⚠️ 세션 저장 중 오류: {e}")

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
                # 브라우저 활성화 대기
                time.sleep(0.5)
                # 새 창 닫기 (Cmd+W)
                for _ in range(3):
                    os.system("osascript -e 'tell application \"System Events\" to key code 13 using {command down}' 2>/dev/null")
                    time.sleep(0.1)
                # 브라우저 활성화 대기
                time.sleep(1.5)
                # Cmd+Shift+T로 세션 복구
                os.system("osascript -e 'tell application \"System Events\" to key code 17 using {command down, shift down}' 2>/dev/null")

                print(f"✅ {browser} 세션 복구 완료")

            except Exception as e:
                print(f"⚠️ {browser} 세션 복구 중 오류: {e}")

        print("✅ 브라우저 세션 복구 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 세션 복구 중 오류: {e}")

def simple_dns_flush():
    """DNS 캐시만 초기화 (가장 안전하고 빠른 방법)"""
    try:
        os.system("sudo dscacheutil -flushcache")
        os.system("sudo killall -HUP mDNSResponder")
        print("🔄 DNS 캐시 초기화 완료")
    except Exception as e:
        print(f"⚠️ DNS 캐시 초기화 중 오류: {e}")

def optimized_browser_clear():
    """최적화된 브라우저 조작 (DNS + 새로고침만)"""
    try:
        # DNS 캐시 초기화
        simple_dns_flush()

        # 실행 중인 브라우저 새로고침만
        running_browsers = get_running_browsers()
        if running_browsers:
            print(f"🔄 브라우저 새로고침 중... ({', '.join(running_browsers)})")
            for browser in running_browsers:
                try:
                    os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                    time.sleep(1)  # 브라우저 활성화 대기
                    os.system("osascript -e 'tell application \"System Events\" to key code 15 using {command down}' 2>/dev/null")
                    print(f"✅ {browser} 새로고침 완료")
                except Exception as e:
                    print(f"⚠️ {browser} 새로고침 중 오류: {e}")
            print("✅ 브라우저 새로고침 완료")
    except Exception as e:
        print(f"⚠️ 브라우저 조작 중 오류: {e}")

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
        time.sleep(5)  # 브라우저 완전 로딩 대기 (더 긴 대기 시간)
        restore_browser_sessions()

        print("✅ 브라우저 재시작 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 재시작 중 오류: {e}")

def force_browser_refresh():
    """실행 중인 브라우저에만 강제 새로고침 신호 전송"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🔄 브라우저 새로고침 중... ({', '.join(running_browsers)})")

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

def backup_hosts():
    if not os.path.exists(BACKUP_PATH):
        with open(HOSTS_PATH, "r") as original, open(BACKUP_PATH, "w") as backup:
            backup.write(original.read())

def restore_hosts():
    if os.path.exists(BACKUP_PATH):
        with open(BACKUP_PATH, "r") as backup, open(HOSTS_PATH, "w") as original:
            original.write(backup.read())
        print("✅ hosts 파일 복구 완료.")

def block_websites():
    global was_unblocked

    # hosts 파일에 차단 설정 추가
    with open(HOSTS_PATH, "r+") as file:
        lines = file.readlines()
        new_entries = []

        # FocusTimer 블록 시작 주석 추가
        block_start = "# FocusTimer Block Start\n"
        block_end = "# FocusTimer Block End\n"

        # 기존 FocusTimer 블록이 있는지 확인
        has_block = block_start in lines and block_end in lines

        if not has_block:
            new_entries.append(block_start)
            for site in WEBSITES_TO_BLOCK:
                entry = f"{REDIRECT_IP} {site}\n"
                new_entries.append(entry)
            new_entries.append(block_end)

        # 새로운 차단 설정이 있거나, 이전에 해제된 적이 있으면 처리
        if new_entries or was_unblocked:
            if new_entries:
                file.writelines(new_entries)
                file.flush()  # 버퍼 강제 쓰기
                os.fsync(file.fileno())  # 디스크에 강제 기록
                print("📝 hosts 파일에 차단 설정 추가")

            # ========================================
            # 강화된 브라우저 캐시 초기화 (시스템 DNS + 브라우저 DNS + 개발자 도구 + 새로고침)
            # ========================================

            # 1. 시스템 DNS 캐시 초기화
            simple_dns_flush()

            # 2. 브라우저별 DNS 캐시 초기화 (재시작 없이)
            force_dns_cache_clear()

            # 3. 브라우저별 개발자 도구 캐시 초기화
            force_browser_cache_clear()

            # 4. 파일 시스템 캐시 직접 삭제 (필요시 주석 해제)
            # clear_browser_cache()  # 주석 처리됨 - 필요시 활성화

            # 5. 브라우저 강제 새로고침
            force_browser_refresh()

            # 브라우저 재시작 (세션 보존)
            #force_browser_restart()

            was_unblocked = False  # 차단 상태로 리셋
            save_state()  # 상태 저장
            print("✅ YouTube 차단 완료")
        else:
            print("ℹ️ 이미 차단 설정이 적용되어 있습니다.")

def unblock_websites():
    global was_unblocked

    # hosts 파일에서 차단 설정 제거
    with open(HOSTS_PATH, "r+") as file:
        lines = file.readlines()

        # FocusTimer 블록 제거
        block_start = "# FocusTimer Block Start\n"
        block_end = "# FocusTimer Block End\n"

        # 블록 시작과 끝 인덱스 찾기
        start_idx = -1
        end_idx = -1

        for i, line in enumerate(lines):
            if line == block_start:
                start_idx = i
            elif line == block_end:
                end_idx = i
                break

        # FocusTimer 블록이 있으면 제거
        if start_idx != -1 and end_idx != -1:
            new_lines = lines[:start_idx] + lines[end_idx + 1:]
            file.seek(0)
            file.writelines(new_lines)
            file.truncate()
            file.flush()  # 버퍼 강제 쓰기
            os.fsync(file.fileno())  # 디스크에 강제 기록
            print("📝 hosts 파일에서 차단 설정 제거")

            # ========================================
            # 강화된 브라우저 캐시 초기화 (시스템 DNS + 브라우저 DNS + 개발자 도구 + 새로고침)
            # ========================================

            # 1. 시스템 DNS 캐시 초기화
            simple_dns_flush()

            # 2. 브라우저별 DNS 캐시 초기화 (재시작 없이)
            force_dns_cache_clear()

            # 3. 브라우저별 개발자 도구 캐시 초기화
            force_browser_cache_clear()

            # 4. 파일 시스템 캐시 직접 삭제 (필요시 주석 해제)
            # clear_browser_cache()  # 주석 처리됨 - 필요시 활성화

            # 5. 브라우저 강제 새로고침
            force_browser_refresh()

            was_unblocked = True  # 해제 상태로 설정 (다음 차단 시 DNS 초기화 보장)
            save_state()  # 상태 저장
            print("✅ YouTube 차단 해제 완료")
        else:
            print("ℹ️ 차단 설정이 없습니다.")

def signal_handler(sig, frame):
    """강화된 종료 핸들러 - 집중 모드 시간대에는 알고리즘 문제 해결 필요"""
    global exit_allowed

    print("\n🛑 프로그램 종료 시도가 감지되었습니다.")

    # 집중 모드 시간대인지 확인
    if is_focus_mode and is_within_focus_time():
        print("🚫 집중 모드 시간대입니다. 종료하려면 문제를 풀어야 합니다!")

        # 알고리즘 문제 출제
        if challenge.ask_challenge():
            print("✅ 문제 해결 성공! 안전하게 종료합니다.")
            exit_allowed = True
            cleanup_and_exit()
        else:
            print("🚫 종료가 거부되었습니다. 집중 모드를 계속 유지합니다.")
            save_focus_state()  # 상태 저장
            return
    else:
        # 집중 모드 시간대가 아니면 바로 종료
        print("✅ 집중 모드 시간대가 아닙니다. 안전하게 종료합니다.")
        exit_allowed = True
        cleanup_and_exit()

def cleanup_and_exit():
    """프로그램 정리 및 종료"""
    try:
        unblock_websites()
        restore_hosts()
        remove_lock_file()
        save_focus_state()
        print("✅ 안전한 종료 완료")
        sys.exit(0)
    except:
        sys.exit(1)

# 시그널 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ----- 모드 선택 -----
def choose_mode():
    global is_focus_mode, focus_start_time, focus_end_time

    # 프로그램 시작 시 이전 상태 불러오기
    load_state()
    load_focus_state()

    print("📚 집중 모드 실행")
    print("1. 매일 지정한 시간에 차단 (예: 오전 9시 ~ 오후 6시) - 🔒 종료 방지 모드")
    print("2. 지금부터 N시간 차단")
    print("3. 집중 모드 설정 (종료 방지 + 브라우저 강제 재시작)")
    mode = input("모드를 선택하세요 (1, 2, 또는 3): ")

    backup_hosts()

    if mode == "1":
        # 시작 시간 입력 (시간:분 형식 지원)
        start_input = input("차단 시작 시간 (24시간 기준, 예: 9 또는 9:30): ").strip()
        start_hour, start_minute = parse_time_input(start_input)

        # 종료 시간 입력 (시간:분 형식 지원)
        end_input = input("차단 종료 시간 (예: 18 또는 18:30): ").strip()
        end_hour, end_minute = parse_time_input(end_input)

        # 집중 모드 활성화 여부 확인
        enable_focus_mode = input("집중 모드(종료 방지)를 활성화하시겠습니까? (y/n): ").lower() == 'y'

        if enable_focus_mode:
            is_focus_mode = True
            focus_start_time = datetime.datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            focus_end_time = datetime.datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            save_focus_state()
            print("🔒 집중 모드가 활성화되었습니다. 지정된 시간대에는 종료할 수 없습니다!")

        # 테스트 모드 확인
        test_mode = input("테스트 모드입니까? (y/n): ").lower() == 'y'
        if test_mode:
            sleep_time = 10  # 테스트 모드면 10초마다 체크
            print("🧪 테스트 모드: 10초마다 체크")
        else:
            sleep_time = 60  # 일반 모드면 1분마다 체크
            print("📅 일반 모드: 1분마다 체크")

        print("⏳ 매일 시간대 차단 모드 실행 중... Ctrl+C로 종료")

        current_blocked = None  # 현재 차단 상태 추적

        try:
            while True:
                now = datetime.datetime.now()
                current_time = now.time()
                start_time = datetime.time(start_hour, start_minute)
                end_time = datetime.time(end_hour, end_minute)

                # 시간대 비교 (자정을 넘는 경우 고려)
                if start_time <= end_time:
                    should_be_blocked = start_time <= current_time <= end_time
                else:
                    should_be_blocked = current_time >= start_time or current_time <= end_time

                # 상태가 변경될 때만 파일 I/O 수행
                if current_blocked != should_be_blocked:
                    if should_be_blocked:
                        block_websites()
                        print(f"🔒 {now.strftime('%H:%M:%S')} - YouTube 차단 시작")

                        # 집중 모드가 활성화되어 있으면 브라우저 강제 재시작
                        if is_focus_mode:
                            force_browser_restart_with_focus()
                    else:
                        unblock_websites()
                        print(f"🔓 {now.strftime('%H:%M:%S')} - YouTube 차단 해제")
                    current_blocked = should_be_blocked

                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨.")
        finally:
            unblock_websites()
            restore_hosts()
            print("✅ 시간대 차단 모드 종료")

    elif mode == "2":
        hours = float(input("몇 시간 동안 차단할까요? (예: 2.5): "))
        end_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
        print(f"⏳ 타이머 차단 모드 실행 중... 종료 시각: {end_time.strftime('%H:%M:%S')}")

        # 동적 sleep 시간 계산 (최소 10초, 최대 60초)
        total_seconds = hours * 3600
        if total_seconds < 60:
            sleep_time = max(10, int(total_seconds / 6))  # 1분 미만이면 10초마다 체크
        else:
            sleep_time = 60  # 1분 이상이면 1분마다 체크

        print(f"⏱️ 체크 간격: {sleep_time}초")

        # 한 번만 차단 설정
        block_websites()
        current_blocked = True

        try:
            while datetime.datetime.now() < end_time:
                time.sleep(sleep_time)  # 동적 sleep 시간
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨.")
        finally:
            unblock_websites()
            restore_hosts()
            print("✅ 타이머 종료")

    elif mode == "3":
        print("🔒 집중 모드 설정")
        print("이 모드는 지정된 시간대에 프로그램 종료를 완전히 차단합니다.")
        print("종료하려면 알고리즘 문제를 풀어야 하며, 실패 시 난이도가 증가합니다.")

        # 시작 시간 입력 (시간:분 형식 지원)
        start_input = input("집중 시작 시간 (24시간 기준, 예: 9 또는 9:30): ").strip()
        start_hour, start_minute = parse_time_input(start_input)

        # 종료 시간 입력 (시간:분 형식 지원)
        end_input = input("집중 종료 시간 (예: 18 또는 18:30): ").strip()
        end_hour, end_minute = parse_time_input(end_input)

        is_focus_mode = True
        focus_start_time = datetime.datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        focus_end_time = datetime.datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        save_focus_state()

        print(f"🔒 집중 모드가 설정되었습니다!")
        print(f"⏰ 집중 시간: {start_hour:02d}:{start_minute:02d} ~ {end_hour:02d}:{end_minute:02d}")
        print("🚫 이 시간대에는 프로그램을 종료할 수 없습니다!")
        print("💡 종료하려면 알고리즘 문제를 풀어야 합니다.")

        # 브라우저 강제 재시작
        restart_browsers()

        # 차단 설정
        block_websites()

        print("✅ 집중 모드가 활성화되었습니다. 프로그램이 백그라운드에서 실행됩니다.")
        print("💡 종료하려면 Ctrl+C를 누르고 문제를 풀어주세요.")

        # 백그라운드 모니터링
        try:
            while True:
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            print("\n🛑 종료 시도가 감지되었습니다.")
            if challenge.ask_challenge():
                cleanup_and_exit()
            else:
                print("🚫 종료가 거부되었습니다. 집중 모드를 계속 유지합니다.")
                save_focus_state()

    else:
        print("❌ 잘못된 입력입니다.")
        restore_hosts()

# ----- 실행 -----
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️ 관리자 권한으로 실행해야 합니다: sudo python3 focus_timer.py")
        sys.exit(1)

    # 이미 실행 중인지 확인
    if is_already_running():
        print("⚠️ Focus Timer가 이미 실행 중입니다.")
        print("💡 다른 인스턴스를 종료하고 다시 시도해주세요.")
        sys.exit(1)

    # 락 파일 생성
    if not create_lock_file():
        print("⚠️ 락 파일 생성에 실패했습니다.")
        sys.exit(1)

    try:
        choose_mode()
    except Exception as e:
        print(f"⚠️ 프로그램 실행 중 오류 발생: {e}")
        cleanup_and_exit()
    finally:
        remove_lock_file()