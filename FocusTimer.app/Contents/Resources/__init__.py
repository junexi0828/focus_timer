"""
FocusTimer.app Resources Package
알고리즘 시스템 및 기타 리소스 모듈들을 포함하는 패키지
"""

__version__ = "1.0.0"
__author__ = "FocusTimer Team"

# 패키지 초기화 시 필요한 설정
import os
import sys
from pathlib import Path

# 패키지 루트 경로 설정
PACKAGE_ROOT = Path(__file__).parent
ALGORITHM_MODULES_PATH = PACKAGE_ROOT

# 알고리즘 모듈들을 패키지 네임스페이스에 추가
__all__ = [
    'algorithm_tab',
    'gui_algorithm_manager',
    'advanced_challenge_system',
    'user_progress_tracker',
    'problem_data_structures',
    'remote_problem_provider'
]

# 모듈 로드 상태 확인 함수
def check_algorithm_modules():
    """알고리즘 모듈들의 로드 상태를 확인"""
    modules_status = {}

    for module_name in __all__:
        try:
            module = __import__(f"resources.{module_name}", fromlist=[module_name])
            modules_status[module_name] = True
        except ImportError:
            modules_status[module_name] = False

    return modules_status

# 패키지 초기화 시 모듈 상태 출력
if __name__ != "__main__":
    print("📦 FocusTimer Resources 패키지 초기화 중...")
    status = check_algorithm_modules()
    loaded_count = sum(status.values())
    print(f"✅ {loaded_count}/{len(__all__)} 모듈 로드 완료")