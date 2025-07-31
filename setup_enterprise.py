#!/usr/bin/env python3
"""
Focus Timer Enterprise - 설정 도구
Enterprise 버전의 집중 모드 설정을 대화형으로 구성합니다.
"""

import json
import os
import sys
import datetime
from pathlib import Path

# 설정 파일 경로
STATE_PATH = "/Library/Application Support/FocusTimer/state.json"

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

def setup_focus_mode():
    """집중 모드 설정"""
    print("🔒 Focus Timer Enterprise 설정")
    print("=" * 50)

    # 집중 모드 활성화 여부
    enable_focus = input("집중 모드를 활성화하시겠습니까? (y/n): ").lower() == 'y'

    if not enable_focus:
        print("ℹ️ 집중 모드가 비활성화되었습니다.")
        return create_state_file(False)

    print("\n⏰ 집중 시간 설정")
    print("-" * 30)

    # 시작 시간 입력
    start_input = input("집중 시작 시간 (24시간 기준, 예: 9 또는 9:30): ").strip()
    start_hour, start_minute = parse_time_input(start_input)

    # 종료 시간 입력
    end_input = input("집중 종료 시간 (예: 18 또는 18:30): ").strip()
    end_hour, end_minute = parse_time_input(end_input)

    # 난이도 설정
    print("\n🧮 알고리즘 문제 난이도 설정")
    print("-" * 30)
    print("1: 기본 사칙연산 (2자리 수)")
    print("2: 3자리 수 연산")
    print("3: 복합 연산 (괄호 포함)")
    print("4: 피보나치 수열")
    print("5: 정렬 알고리즘")

    try:
        difficulty = int(input("난이도를 선택하세요 (1-5): "))
        if not (1 <= difficulty <= 5):
            difficulty = 1
    except:
        difficulty = 1

    # 추가 설정
    print("\n⚙️ 추가 설정")
    print("-" * 30)

    # 브라우저 강제 재시작
    force_restart = input("집중 모드 시작 시 브라우저를 강제 재시작하시겠습니까? (y/n): ").lower() == 'y'

    # 웹 관리 인터페이스
    web_interface = input("웹 관리 인터페이스를 활성화하시겠습니까? (y/n): ").lower() == 'y'

    # 설정 요약
    print("\n📋 설정 요약")
    print("=" * 50)
    print(f"집중 모드: {'활성화' if enable_focus else '비활성화'}")
    if enable_focus:
        print(f"집중 시간: {start_hour:02d}:{start_minute:02d} ~ {end_hour:02d}:{end_minute:02d}")
        print(f"문제 난이도: {difficulty}")
        print(f"브라우저 강제 재시작: {'예' if force_restart else '아니오'}")
        print(f"웹 관리 인터페이스: {'예' if web_interface else '아니오'}")

    # 설정 확인
    confirm = input("\n이 설정으로 진행하시겠습니까? (y/n): ").lower() == 'y'
    if not confirm:
        print("❌ 설정이 취소되었습니다.")
        return False

    # 상태 파일 생성
    return create_state_file(True, start_hour, start_minute, end_hour, end_minute, difficulty, force_restart, web_interface)

def create_state_file(is_focus_mode, start_hour=9, start_minute=0, end_hour=18, end_minute=0, difficulty=1, force_restart=True, web_interface=True):
    """상태 파일 생성"""
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

        # 현재 시간 기준으로 날짜 설정
        now = datetime.datetime.now()
        focus_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        focus_end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

        # 상태 데이터
        state_data = {
            "is_focus_mode": is_focus_mode,
            "focus_start_time": focus_start_time.isoformat() if is_focus_mode else None,
            "focus_end_time": focus_end_time.isoformat() if is_focus_mode else None,
            "is_blocked": False,
            "block_count": 0,
            "bypass_attempts": 0,
            "difficulty_level": difficulty,
            "failed_attempts": 0,
            "force_browser_restart": force_restart,
            "web_interface_enabled": web_interface,
            "last_check": datetime.datetime.now().isoformat()
        }

        # 파일에 저장
        with open(STATE_PATH, "w") as f:
            json.dump(state_data, f, indent=2)

        print("✅ 설정이 저장되었습니다!")
        return True

    except Exception as e:
        print(f"❌ 설정 저장 실패: {e}")
        return False

def show_current_settings():
    """현재 설정 표시"""
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH, "r") as f:
                state = json.load(f)

            print("📋 현재 설정")
            print("=" * 50)
            print(f"집중 모드: {'활성화' if state.get('is_focus_mode') else '비활성화'}")

            if state.get('is_focus_mode'):
                if state.get('focus_start_time'):
                    start_time = datetime.datetime.fromisoformat(state['focus_start_time'])
                    print(f"시작 시간: {start_time.strftime('%H:%M')}")

                if state.get('focus_end_time'):
                    end_time = datetime.datetime.fromisoformat(state['focus_end_time'])
                    print(f"종료 시간: {end_time.strftime('%H:%M')}")

                print(f"문제 난이도: {state.get('difficulty_level', 1)}")
                print(f"브라우저 강제 재시작: {'예' if state.get('force_browser_restart') else '아니오'}")
                print(f"웹 관리 인터페이스: {'예' if state.get('web_interface_enabled') else '아니오'}")
                print(f"차단 횟수: {state.get('block_count', 0)}")
                print(f"우회 시도: {state.get('bypass_attempts', 0)}")
        else:
            print("ℹ️ 설정 파일이 없습니다.")

    except Exception as e:
        print(f"❌ 설정 읽기 실패: {e}")

def main():
    """메인 함수"""
    if os.geteuid() != 0:
        print("⚠️ 관리자 권한으로 실행해야 합니다: sudo python3 setup_enterprise.py")
        sys.exit(1)

    print("🔧 Focus Timer Enterprise 설정 도구")
    print("=" * 50)

    while True:
        print("\n📋 메뉴")
        print("1. 집중 모드 설정")
        print("2. 현재 설정 확인")
        print("3. 설정 초기화")
        print("4. 종료")

        choice = input("\n선택하세요 (1-4): ").strip()

        if choice == "1":
            setup_focus_mode()
        elif choice == "2":
            show_current_settings()
        elif choice == "3":
            if os.path.exists(STATE_PATH):
                os.remove(STATE_PATH)
                print("✅ 설정이 초기화되었습니다.")
            else:
                print("ℹ️ 설정 파일이 없습니다.")
        elif choice == "4":
            print("👋 설정 도구를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()