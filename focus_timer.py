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

def save_browser_sessions():
    """브라우저 세션 정보를 저장"""
    try:
        running_browsers = get_running_browsers()

        if not running_browsers:
            return

        session_info = {}

        for browser in running_browsers:
            try:
                if browser == "Google Chrome":
                    # Chrome 세션 파일 경로
                    chrome_session = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Session")
                    if os.path.exists(chrome_session):
                        session_info[browser] = chrome_session

                elif browser == "Safari":
                    # Safari 세션 파일 경로
                    safari_session = os.path.expanduser("~/Library/Safari/LastSession.plist")
                    if os.path.exists(safari_session):
                        session_info[browser] = safari_session

                elif browser == "Firefox":
                    # Firefox 세션 파일 경로
                    firefox_profile = os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
                    if os.path.exists(firefox_profile):
                        session_info[browser] = firefox_profile

            except Exception as e:
                print(f"⚠️ {browser} 세션 저장 중 오류: {e}")

        # 세션 정보를 파일에 저장
        if session_info:
            with open(os.path.expanduser("~/focus_timer_sessions.json"), "w") as f:
                import json
                json.dump(session_info, f)

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
                time.sleep(1)

                if browser == "Google Chrome":
                    # Chrome 세션 복구 (Cmd+Shift+T로 탭 복구)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"t\" using {command down, shift down}' 2>/dev/null")

                elif browser == "Safari":
                    # Safari 세션 복구 (Cmd+Shift+T로 탭 복구)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"t\" using {command down, shift down}' 2>/dev/null")

                elif browser == "Firefox":
                    # Firefox 세션 복구 (Cmd+Shift+T로 탭 복구)
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"t\" using {command down, shift down}' 2>/dev/null")

                else:
                    # 다른 브라우저도 동일한 단축키 시도
                    os.system("osascript -e 'tell application \"System Events\" to keystroke \"t\" using {command down, shift down}' 2>/dev/null")

                print(f"✅ {browser} 세션 복구 완료")

            except Exception as e:
                print(f"⚠️ {browser} 세션 복구 중 오류: {e}")

        print("✅ 브라우저 세션 복구 완료")

    except Exception as e:
        print(f"⚠️ 브라우저 세션 복구 중 오류: {e}")

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
        time.sleep(3)  # 브라우저 완전 로딩 대기
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
            # 브라우저가 실행 중이면 새로고침 신호 전송
            os.system(f"osascript -e 'tell application \"{browser}\" to activate' 2>/dev/null")
            time.sleep(0.5)  # 잠시 대기
            os.system(f"osascript -e 'tell application \"System Events\" to key code 124 using {{command down, shift down}}' 2>/dev/null")

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

        # 새로운 차단 설정이 있거나, 이전에 해제된 적이 있으면 DNS 초기화
        if new_entries or was_unblocked:
            if new_entries:
                file.writelines(new_entries)
                file.flush()  # 버퍼 강제 쓰기
                os.fsync(file.fileno())  # 디스크에 강제 기록
                print("📝 hosts 파일에 차단 설정 추가")

            # DNS 캐시 초기화
            try:
                os.system("sudo dscacheutil -flushcache")
                os.system("sudo killall -HUP mDNSResponder")
                print("🔄 DNS 캐시 초기화 완료")
            except:
                pass

            # 브라우저 캐시 자동 초기화
            clear_browser_cache()

            # 브라우저 강제 새로고침 신호 전송
            force_browser_refresh()

            # 브라우저 재시작 (세션 보존)
            force_browser_restart()

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
            try:
                os.system("sudo dscacheutil -flushcache")
                os.system("sudo killall -HUP mDNSResponder")
                print("🔄 DNS 캐시 초기화 완료")
            except:
                pass

            # 브라우저 캐시 자동 초기화
            clear_browser_cache()

            # 브라우저 강제 새로고침 신호 전송
            force_browser_refresh()

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

        try:
            while datetime.datetime.now() < end_time:
                block_websites()
                time.sleep(60)
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