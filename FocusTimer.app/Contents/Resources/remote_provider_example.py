"""
외부 플랫폼 연동 시스템 사용 예시

이 모듈은 외부 플랫폼 연동 시스템의 사용 방법을 보여줍니다.
Codeforces, LeetCode, Kaggle에서 문제를 가져오는 기능을 시연합니다.
"""

import logging
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithm_system.remote_problem_provider import (
    RemoteProblemManager, CodeforcesProvider, LeetCodeProvider, KaggleProvider
)
from algorithm_system.problem_data_structures import (
    ProblemPlatform, ProblemDifficulty, ProblemTag
)


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('remote_provider.log', encoding='utf-8')
        ]
    )


def demonstrate_codeforces():
    """Codeforces 연동 시연"""
    print("\n=== Codeforces 연동 시연 ===")

    try:
        # Codeforces 프로바이더 생성
        cf_provider = CodeforcesProvider(cache_dir="cache/codeforces")

        # 문제 목록 가져오기 (최대 10개)
        print("Codeforces에서 문제 목록 가져오는 중...")
        problems = cf_provider.get_problems(limit=10)

        print(f"가져온 문제 수: {len(problems)}")

        for i, problem in enumerate(problems, 1):
            print(f"{i}. {problem.title}")
            print(f"   난이도: {problem.difficulty}")
            print(f"   태그: {', '.join(str(tag) for tag in problem.tags)}")
            print(f"   URL: {problem.platform_url}")
            print()

        # 난이도별 문제 가져오기
        print("=== 난이도별 문제 ===")
        for difficulty in ProblemDifficulty:
            problems = cf_provider.get_problems(limit=5)
            filtered_problems = [p for p in problems if p.difficulty == difficulty]
            if filtered_problems:
                print(f"{difficulty.name}: {len(filtered_problems)}개")
                for problem in filtered_problems[:3]:  # 최대 3개만 표시
                    print(f"  - {problem.title}")
                print()

        return True

    except Exception as e:
        print(f"Codeforces 연동 실패: {e}")
        return False


def demonstrate_leetcode():
    """LeetCode 연동 시연"""
    print("\n=== LeetCode 연동 시연 ===")

    try:
        # LeetCode 프로바이더 생성
        lc_provider = LeetCodeProvider(cache_dir="cache/leetcode")

        # 문제 목록 가져오기 (최대 10개)
        print("LeetCode에서 문제 목록 가져오는 중...")
        problems = lc_provider.get_problems(limit=10)

        print(f"가져온 문제 수: {len(problems)}")

        for i, problem in enumerate(problems, 1):
            print(f"{i}. {problem.title}")
            print(f"   난이도: {problem.difficulty}")
            print(f"   태그: {', '.join(str(tag) for tag in problem.tags)}")
            print(f"   URL: {problem.platform_url}")
            print()

        # 태그별 문제 가져오기
        print("=== 태그별 문제 ===")
        for tag in [ProblemTag.ARRAY, ProblemTag.DYNAMIC_PROGRAMMING, ProblemTag.BINARY_SEARCH]:
            problems = lc_provider.get_problems(limit=20)
            filtered_problems = [p for p in problems if tag in p.tags]
            if filtered_problems:
                print(f"{tag}: {len(filtered_problems)}개")
                for problem in filtered_problems[:3]:  # 최대 3개만 표시
                    print(f"  - {problem.title}")
                print()

        return True

    except Exception as e:
        print(f"LeetCode 연동 실패: {e}")
        return False


def demonstrate_kaggle():
    """Kaggle 연동 시연"""
    print("\n=== Kaggle 연동 시연 ===")

    try:
        # Kaggle 프로바이더 생성
        kaggle_provider = KaggleProvider(cache_dir="cache/kaggle")

        # 문제 목록 가져오기 (최대 5개)
        print("Kaggle에서 데이터셋 목록 가져오는 중...")
        problems = kaggle_provider.get_problems(limit=5)

        print(f"가져온 데이터셋 수: {len(problems)}")

        for i, problem in enumerate(problems, 1):
            print(f"{i}. {problem.title}")
            print(f"   난이도: {problem.difficulty}")
            print(f"   태그: {', '.join(str(tag) for tag in problem.tags)}")
            print(f"   URL: {problem.platform_url}")
            print(f"   설명: {problem.description[:100]}...")
            print()

        return True

    except Exception as e:
        print(f"Kaggle 연동 실패: {e}")
        return False


def demonstrate_remote_manager():
    """RemoteProblemManager 시연"""
    print("\n=== RemoteProblemManager 시연 ===")

    try:
        # RemoteProblemManager 생성
        manager = RemoteProblemManager(cache_dir="cache")

        # 지원하는 플랫폼 확인
        supported_platforms = manager.get_supported_platforms()
        print(f"지원하는 플랫폼: {', '.join(p.name for p in supported_platforms)}")

        # 각 플랫폼에서 문제 가져오기
        for platform in supported_platforms:
            print(f"\n--- {platform.name} ---")

            # 모든 문제 가져오기 (최대 5개)
            problems = manager.get_all_problems(platform, limit=5)
            print(f"총 문제 수: {len(problems)}")

            if problems:
                # 난이도별 분포
                difficulty_count = {}
                for problem in problems:
                    difficulty = problem.difficulty
                    difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1

                print("난이도별 분포:")
                for difficulty, count in difficulty_count.items():
                    print(f"  {difficulty.name}: {count}개")

                # 첫 번째 문제 상세 정보
                first_problem = problems[0]
                print(f"\n첫 번째 문제 상세:")
                print(f"  제목: {first_problem.title}")
                print(f"  플랫폼: {first_problem.platform}")
                print(f"  난이도: {first_problem.difficulty}")
                print(f"  태그: {', '.join(str(tag) for tag in first_problem.tags)}")
                print(f"  URL: {first_problem.platform_url}")

        return True

    except Exception as e:
        print(f"RemoteProblemManager 시연 실패: {e}")
        return False


def demonstrate_cache_management():
    """캐시 관리 시연"""
    print("\n=== 캐시 관리 시연 ===")

    try:
        manager = RemoteProblemManager(cache_dir="cache")

        # 캐시 새로고침
        print("캐시 새로고침 중...")
        for platform in manager.get_supported_platforms():
            success = manager.refresh_cache(platform)
            print(f"{platform.name}: {'성공' if success else '실패'}")

        # 새로고침 후 문제 가져오기
        print("\n새로고침 후 문제 가져오기:")
        for platform in manager.get_supported_platforms():
            problems = manager.get_all_problems(platform, limit=3)
            print(f"{platform.name}: {len(problems)}개 문제")

        return True

    except Exception as e:
        print(f"캐시 관리 시연 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("=== 외부 플랫폼 연동 시스템 시연 ===\n")

    # 로깅 설정
    setup_logging()

    # 각 플랫폼별 시연
    results = {
        "Codeforces": demonstrate_codeforces(),
        "LeetCode": demonstrate_leetcode(),
        "Kaggle": demonstrate_kaggle(),
        "RemoteManager": demonstrate_remote_manager(),
        "CacheManagement": demonstrate_cache_management()
    }

    # 결과 요약
    print("\n=== 시연 결과 요약 ===")
    for platform, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{platform}: {status}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    if success_count > 0:
        print("\n🎉 외부 플랫폼 연동 시스템이 성공적으로 작동합니다!")
        print("\n사용 가능한 기능:")
        print("- Codeforces: 공식 API를 통한 문제 목록 가져오기")
        print("- LeetCode: GraphQL API를 통한 문제 목록 가져오기")
        print("- Kaggle: 데이터셋 검색 및 정보 가져오기")
        print("- 캐시 시스템: 효율적인 데이터 관리")
        print("- 통합 관리: RemoteProblemManager를 통한 일관된 인터페이스")
    else:
        print("\n⚠️ 일부 플랫폼 연동에 실패했습니다.")
        print("네트워크 연결과 API 상태를 확인해주세요.")


if __name__ == "__main__":
    main()