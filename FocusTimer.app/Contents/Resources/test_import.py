#!/usr/bin/env python3
"""
FocusTimer Resources Import Test
알고리즘 모듈들이 제대로 import되는지 테스트
"""

import sys
import os
from pathlib import Path

def test_imports():
    """모든 모듈의 import를 테스트"""

    # 현재 파일의 디렉토리를 Python 경로에 추가
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    print(f"📁 테스트 경로: {current_dir}")
    print(f"📋 Python 경로: {sys.path[:3]}...")

    # 테스트할 모듈들
    test_modules = [
        'algorithm_tab',
        'gui_algorithm_manager',
        'advanced_challenge_system',
        'user_progress_tracker',
        'problem_data_structures',
        'import_utils'
    ]

    results = {}

    for module_name in test_modules:
        try:
            module = __import__(module_name)
            results[module_name] = True
            print(f"✅ {module_name} import 성공")

            # AlgorithmTab 클래스 특별 테스트
            if module_name == 'algorithm_tab':
                if hasattr(module, 'AlgorithmTab'):
                    print(f"  ✅ AlgorithmTab 클래스 발견")
                else:
                    print(f"  ❌ AlgorithmTab 클래스 없음")

        except ImportError as e:
            results[module_name] = False
            print(f"❌ {module_name} import 실패: {e}")
        except Exception as e:
            results[module_name] = False
            print(f"❌ {module_name} 예상치 못한 오류: {e}")

    # 결과 요약
    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n📊 테스트 결과: {success_count}/{total_count} 성공")

    if success_count >= 3:
        print("✅ 알고리즘 시스템 사용 가능")
        return True
    else:
        print("⚠️ 일부 모듈이 누락되었습니다")
        return False

def test_algorithm_tab_creation():
    """AlgorithmTab 인스턴스 생성 테스트"""
    try:
        import tkinter as tk
        from tkinter import ttk

        # 임시 루트 윈도우 생성
        root = tk.Tk()
        root.withdraw()  # 숨기기

        # notebook 생성
        notebook = ttk.Notebook(root)

        # AlgorithmTab import 및 생성
        from algorithm_tab import AlgorithmTab

        # AlgorithmTab 인스턴스 생성
        algorithm_tab = AlgorithmTab(notebook)

        # frame 속성 확인
        if hasattr(algorithm_tab, 'frame'):
            print("✅ AlgorithmTab 인스턴스 생성 성공")
            print("✅ frame 속성 확인됨")

            # notebook에 추가 테스트
            notebook.add(algorithm_tab.frame, text="테스트")
            print("✅ notebook.add() 성공")

            root.destroy()
            return True
        else:
            print("❌ AlgorithmTab에 frame 속성이 없습니다")
            root.destroy()
            return False

    except ImportError as e:
        print(f"❌ AlgorithmTab import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ AlgorithmTab 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("🧪 FocusTimer Resources Import Test 시작...")
    print("=" * 50)

    # 기본 import 테스트
    import_success = test_imports()

    print("\n" + "=" * 50)

    # AlgorithmTab 생성 테스트
    if import_success:
        creation_success = test_algorithm_tab_creation()

        if creation_success:
            print("\n🎉 모든 테스트 통과! 알고리즘 탭 통합 준비 완료")
        else:
            print("\n⚠️ AlgorithmTab 생성에 문제가 있습니다")
    else:
        print("\n❌ 기본 import에 실패했습니다")

    print("=" * 50)