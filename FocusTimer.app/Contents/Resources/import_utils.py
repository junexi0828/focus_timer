"""
Import Utilities for FocusTimer Resources
안전하고 확실한 모듈 import를 위한 유틸리티 함수들
"""

import sys
import os
from pathlib import Path
from typing import Optional, Any, Dict, List

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
        """
        안전한 모듈 import

        Args:
            module_name: 기본 모듈 이름
            fallback_names: 대체 모듈 이름들

        Returns:
            import된 모듈 또는 None
        """
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

    def import_algorithm_modules(self) -> Dict[str, Any]:
        """알고리즘 모듈들을 안전하게 import"""
        modules = {}

        # 핵심 알고리즘 모듈들
        algorithm_modules = {
            'gui_algorithm_manager': ['gui_algorithm_manager'],
            'advanced_challenge_system': ['advanced_challenge_system'],
            'user_progress_tracker': ['user_progress_tracker'],
            'problem_data_structures': ['problem_data_structures'],
            'algorithm_tab': ['algorithm_tab']
        }

        for module_name, fallbacks in algorithm_modules.items():
            module = self.import_module(module_name, fallbacks)
            if module:
                modules[module_name] = module

        return modules

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

def check_module_availability(importer: SafeImporter) -> Dict[str, bool]:
    """모듈 가용성 확인"""
    modules = importer.import_algorithm_modules()

    # 핵심 모듈들 확인
    core_modules = [
        'gui_algorithm_manager',
        'advanced_challenge_system',
        'user_progress_tracker'
    ]

    availability = {}
    for module_name in core_modules:
        availability[module_name] = module_name in modules

    # 결과 출력
    print("\n📊 모듈 가용성 확인 결과:")
    for module_name, available in availability.items():
        status = "✅" if available else "❌"
        print(f"  {status} {module_name}")

    return availability

# 전역 importer 인스턴스
_importer = None

def get_importer() -> SafeImporter:
    """전역 importer 인스턴스 반환"""
    global _importer
    if _importer is None:
        _importer = setup_focustimer_resources()
    return _importer

def safe_import(module_name: str) -> Optional[Any]:
    """안전한 모듈 import"""
    importer = get_importer()
    return importer.import_module(module_name)

# 사용 예시
if __name__ == "__main__":
    print("🧪 Import Utils 테스트 중...")

    # importer 설정
    importer = setup_focustimer_resources()

    # 모듈 가용성 확인
    availability = check_module_availability(importer)

    # 결과 요약
    available_count = sum(availability.values())
    total_count = len(availability)

    print(f"\n📈 요약: {available_count}/{total_count} 모듈 사용 가능")

    if available_count >= 2:
        print("✅ 알고리즘 시스템 사용 가능")
    else:
        print("⚠️ 일부 모듈이 누락되었습니다")