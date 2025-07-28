import time
import datetime
import os
import sys
import signal

# ----- 설정 -----
WEBSITES_TO_BLOCK = [
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "youtube.googleapis.com",
    "www.youtube.googleapis.com",
    "youtubei.googleapis.com",
    "www.youtubei.googleapis.com",
    "yt3.ggpht.com",
    "i.ytimg.com",
    "ytimg.com",
    "www.ytimg.com",
    "googlevideo.com",
    "www.googlevideo.com",
    "shorts.youtube.com",
    "www.shorts.youtube.com",
    "music.youtube.com",
    "www.music.youtube.com",
    "studio.youtube.com",
    "www.studio.youtube.com",
    "creator.youtube.com",
    "www.creator.youtube.com",
    "gaming.youtube.com",
    "www.gaming.youtube.com",
    "kids.youtube.com",
    "www.kids.youtube.com",
    "tv.youtube.com",
    "www.tv.youtube.com"
]
HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BACKUP_PATH = os.path.expanduser("~/hosts_backup")  # 홈 디렉토리에 저장
STATE_PATH = os.path.expanduser("~/focus_timer_state")  # 상태 파일 경로

# 전역 상태 추적 변수
was_unblocked = False  # 한 번이라도 해제된 적이 있는지 추적

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

def simple_dns_flush():
    """DNS 캐시만 초기화 (가장 안전하고 빠른 방법)"""
    try:
        os.system("sudo dscacheutil -flushcache")
        os.system("sudo killall -HUP mDNSResponder")
        print("🔄 DNS 캐시 초기화 완료")
    except Exception as e:
        print(f"⚠️ DNS 캐시 초기화 중 오류: {e}")

def simple_browser_refresh():
    """실행 중인 브라우저에만 간단한 새로고침 신호 전송"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🔄 브라우저 새로고침 중... ({', '.join(running_browsers)})")

        for browser in running_browsers:
            try:
                # 브라우저 활성화 후 강제 새로고침 (Cmd+Shift+R)
                os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
                time.sleep(0.5)
                os.system("osascript -e 'tell application \"System Events\" to keystroke \"r\" using {command down, shift down}' 2>/dev/null")
                print(f"✅ {browser} 새로고침 완료")

            except Exception as e:
                print(f"⚠️ {browser} 새로고침 중 오류: {e}")

        print("✅ 브라우저 새로고침 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 새로고침 중 오류: {e}")

def youtube_specific_cache_clear():
    """YouTube 관련 캐시만 선택적으로 초기화"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        print(f"🧹 YouTube 관련 캐시 초기화 중... ({', '.join(running_browsers)})")

        for browser in running_browsers:
            try:
                if browser == "Google Chrome":
                    # Chrome의 YouTube 관련 캐시만 초기화
                    chrome_cache_paths = [
                        os.path.expanduser("~/Library/Caches/Google/Chrome/Default/Cache"),
                        os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cache")
                    ]
                    for path in chrome_cache_paths:
                        if os.path.exists(path):
                            # YouTube 관련 파일만 삭제
                            os.system(f"find {path} -name '*youtube*' -delete 2>/dev/null")
                            os.system(f"find {path} -name '*ytimg*' -delete 2>/dev/null")
                            os.system(f"find {path} -name '*googlevideo*' -delete 2>/dev/null")

                elif browser == "Safari":
                    # Safari의 YouTube 관련 캐시만 초기화
                    safari_cache_path = os.path.expanduser("~/Library/Caches/com.apple.Safari")
                    if os.path.exists(safari_cache_path):
                        os.system(f"find {safari_cache_path} -name '*youtube*' -delete 2>/dev/null")

                elif browser == "Firefox":
                    # Firefox의 YouTube 관련 캐시만 초기화
                    firefox_cache_path = os.path.expanduser("~/Library/Caches/Firefox/Profiles")
                    if os.path.exists(firefox_cache_path):
                        os.system(f"find {firefox_cache_path} -name '*youtube*' -delete 2>/dev/null")

                print(f"✅ {browser} YouTube 캐시 초기화 완료")

            except Exception as e:
                print(f"⚠️ {browser} YouTube 캐시 초기화 중 오류: {e}")

        print("✅ YouTube 관련 캐시 초기화 완료")

    except Exception as e:
        print(f"⚠️ YouTube 캐시 초기화 중 오류: {e}")



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

        # 새로운 차단 설정이 있거나, 이전에 해제된 적이 있으면 DNS 초기화
        if new_entries or was_unblocked:
            if new_entries:
                file.writelines(new_entries)
                file.flush()  # 버퍼 강제 쓰기
                os.fsync(file.fileno())  # 디스크에 강제 기록
                print("📝 hosts 파일에 차단 설정 추가")

            # DNS 캐시 초기화
            simple_dns_flush()

            # 브라우저 새로고침 및 YouTube 캐시 초기화
            simple_browser_refresh()
            youtube_specific_cache_clear()

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

            # DNS 캐시 초기화
            simple_dns_flush()

            # 브라우저 새로고침 및 YouTube 캐시 초기화
            simple_browser_refresh()
            youtube_specific_cache_clear()

            was_unblocked = True  # 해제 상태로 설정 (다음 차단 시 DNS 초기화 보장)
            save_state()  # 상태 저장
            print("✅ YouTube 차단 해제 완료")
        else:
            print("ℹ️ 차단 설정이 없습니다.")

def signal_handler(sig, frame):
    print("\n🛑 프로그램 종료 감지됨. 복구 중...")
    unblock_websites()
    restore_hosts()
    print("✅ 안전한 종료 완료")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ----- 모드 선택 -----
def choose_mode():
    # 프로그램 시작 시 이전 상태 불러오기
    load_state()

    print("📚 집중 모드 실행")
    print("1. 매일 지정한 시간에 차단 (예: 오전 9시 ~ 오후 6시)")
    print("2. 지금부터 N시간 차단")
    mode = input("모드를 선택하세요 (1 또는 2): ")

    backup_hosts()

    if mode == "1":
        start_hour = int(input("차단 시작 시간 (24시간 기준, 예: 9): "))
        end_hour = int(input("차단 종료 시간 (예: 18): "))
        print("⏳ 매일 시간대 차단 모드 실행 중... Ctrl+C로 종료")

        current_blocked = None  # 현재 차단 상태 추적

        try:
            while True:
                now = datetime.datetime.now()
                should_be_blocked = start_hour <= now.hour < end_hour

                # 상태가 변경될 때만 파일 I/O 수행
                if current_blocked != should_be_blocked:
                    if should_be_blocked:
                        block_websites()
                        print(f"🔒 {now.strftime('%H:%M')} - YouTube 차단 시작")
                    else:
                        unblock_websites()
                        print(f"🔓 {now.strftime('%H:%M')} - YouTube 차단 해제")
                    current_blocked = should_be_blocked

                time.sleep(60)
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

        # 한 번만 차단 설정
        block_websites()
        current_blocked = True

        try:
            while datetime.datetime.now() < end_time:
                time.sleep(60)  # 1분마다 체크만
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨.")
        finally:
            unblock_websites()
            restore_hosts()
            print("✅ 타이머 종료")
    else:
        print("❌ 잘못된 입력입니다.")
        restore_hosts()

# ----- 실행 -----
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️ 관리자 권한으로 실행해야 합니다: sudo python3 focus_timer.py")
        sys.exit(1)
    choose_mode()