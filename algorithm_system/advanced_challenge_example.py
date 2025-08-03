"""
고급 알고리즘 챌린지 시스템 사용 예제

이 모듈은 AdvancedChallengeSystem의 다양한 기능들을
실제로 사용하는 방법을 보여주는 예제입니다.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from .advanced_challenge_system import (
        AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
        CodeTestResult, PerformanceMetrics
    )
    from .problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag,
        ProblemTestCase
    )
    from .remote_problem_provider import RemoteProblemProvider
except ImportError:
    from advanced_challenge_system import (
        AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
        CodeTestResult, PerformanceMetrics
    )
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag,
        ProblemTestCase
    )
    from remote_problem_provider import RemoteProblemProvider


class MockProblemProvider:
    """테스트용 문제 제공자"""

    def __init__(self):
        self.problems = self._create_sample_problems()

    def _create_sample_problems(self) -> List[AlgorithmProblem]:
        """샘플 문제들 생성"""
        problems = []

        # 쉬운 문제들
        easy_problems = [
            {
                'id': 'easy_001',
                'title': '두 수의 합',
                'description': '두 정수를 입력받아 합을 출력하는 프로그램을 작성하세요.',
                'difficulty': ProblemDifficulty.EASY,
                'tags': {ProblemTag.ARRAY, ProblemTag.MATH},
                'test_cases': [
                    {'input': '1 2', 'output': '3'},
                    {'input': '5 3', 'output': '8'},
                    {'input': '-1 1', 'output': '0'}
                ]
            },
            {
                'id': 'easy_002',
                'title': '배열의 최댓값',
                'description': '정수 배열에서 최댓값을 찾는 프로그램을 작성하세요.',
                'difficulty': ProblemDifficulty.EASY,
                'tags': {ProblemTag.ARRAY, ProblemTag.BRUTE_FORCE},
                'test_cases': [
                    {'input': '3\n1 2 3', 'output': '3'},
                    {'input': '5\n5 2 8 1 9', 'output': '9'},
                    {'input': '1\n42', 'output': '42'}
                ]
            }
        ]

        # 중간 난이도 문제들
        medium_problems = [
            {
                'id': 'medium_001',
                'title': '이진 탐색',
                'description': '정렬된 배열에서 특정 값을 이진 탐색으로 찾는 프로그램을 작성하세요.',
                'difficulty': ProblemDifficulty.MEDIUM,
                'tags': {ProblemTag.ARRAY, ProblemTag.BINARY_SEARCH},
                'test_cases': [
                    {'input': '5 3\n1 2 3 4 5', 'output': '2'},
                    {'input': '5 6\n1 2 3 4 5', 'output': '-1'},
                    {'input': '3 1\n1 2 3', 'output': '0'}
                ]
            },
            {
                'id': 'medium_002',
                'title': '문자열 뒤집기',
                'description': '문자열을 뒤집는 프로그램을 작성하세요.',
                'difficulty': ProblemDifficulty.MEDIUM,
                'tags': {ProblemTag.STRING, ProblemTag.TWO_POINTERS},
                'test_cases': [
                    {'input': 'hello', 'output': 'olleh'},
                    {'input': 'algorithm', 'output': 'mhtirogla'},
                    {'input': 'a', 'output': 'a'}
                ]
            }
        ]

        # 어려운 문제들
        hard_problems = [
            {
                'id': 'hard_001',
                'title': '동적 프로그래밍 - 피보나치',
                'description': '피보나치 수열의 n번째 항을 동적 프로그래밍으로 계산하는 프로그램을 작성하세요.',
                'difficulty': ProblemDifficulty.HARD,
                'tags': {ProblemTag.DYNAMIC_PROGRAMMING, ProblemTag.MATH},
                'test_cases': [
                    {'input': '5', 'output': '5'},
                    {'input': '10', 'output': '55'},
                    {'input': '20', 'output': '6765'}
                ]
            }
        ]

        # 모든 문제들을 AlgorithmProblem 객체로 변환
        all_problem_data = easy_problems + medium_problems + hard_problems

        for problem_data in all_problem_data:
            problem = AlgorithmProblem(
                id=problem_data['id'],
                title=problem_data['title'],
                description=problem_data['description'],
                difficulty=problem_data['difficulty'],
                platform=ProblemPlatform.LOCAL,
                tags=problem_data['tags'],
                problem_statement=problem_data['description'],
                input_format="표준 입력",
                output_format="표준 출력"
            )

            # 테스트 케이스 추가
            for i, test_case in enumerate(problem_data['test_cases']):
                tc = ProblemTestCase(
                    input_data=test_case['input'],
                    expected_output=test_case['output'],
                    description=f"테스트 케이스 {i+1}"
                )
                problem.add_test_case(tc)

            problems.append(problem)

        return problems

    def get_all_problems(self) -> List[AlgorithmProblem]:
        """모든 문제 반환"""
        return self.problems

    def get_problem_by_id(self, problem_id: str) -> AlgorithmProblem:
        """ID로 문제 조회"""
        for problem in self.problems:
            if problem.id == problem_id:
                return problem
        raise ValueError(f"문제를 찾을 수 없습니다: {problem_id}")


def run_advanced_challenge_example():
    """고급 챌린지 시스템 예제 실행"""
    print("=== 고급 알고리즘 챌린지 시스템 예제 ===\n")

    # 1. 시스템 초기화
    print("1. 시스템 초기화...")
    problem_provider = MockProblemProvider()
    challenge_system = AdvancedChallengeSystem("test_user", problem_provider)
    print("✓ 시스템 초기화 완료\n")

    # 2. 사용자 통계 확인
    print("2. 사용자 통계 확인...")
    stats = challenge_system.get_user_statistics()
    print(f"사용자 레벨: {stats['user_level']}")
    print(f"추천 난이도: {stats['recommended_difficulty']}")
    print(f"해결한 문제 수: {stats['total_problems_solved']}")
    print(f"현재 연속 해결: {stats['current_streak']}일")
    print(f"최장 연속 해결: {stats['longest_streak']}일")
    print(f"성공률: {stats['success_rate']:.2%}")
    print("✓ 통계 확인 완료\n")

    # 3. 개인화된 문제 추천
    print("3. 개인화된 문제 추천...")
    recommendations = challenge_system.get_personalized_recommendations(3)
    print("추천 문제:")
    for i, problem in enumerate(recommendations, 1):
        print(f"  {i}. {problem.title} ({problem.difficulty.name})")
        print(f"     태그: {', '.join(tag.name for tag in problem.tags)}")
    print("✓ 추천 완료\n")

    # 4. 일일 챌린지 생성
    print("4. 일일 챌린지 생성...")
    daily_challenge = challenge_system.create_daily_challenge()
    print(f"챌린지 이름: {daily_challenge.name}")
    print(f"설명: {daily_challenge.description}")
    print(f"목표 문제 수: {daily_challenge.target_problems}")
    print(f"남은 시간: {daily_challenge.get_remaining_days()}일")
    print("✓ 일일 챌린지 생성 완료\n")

    # 5. 문제 풀이 시뮬레이션
    print("5. 문제 풀이 시뮬레이션...")
    if recommendations:
        problem = recommendations[0]
        print(f"문제: {problem.title}")

        # 샘플 코드 (Python)
        sample_code = """
def solve():
    # 두 수의 합 문제 해결
    a, b = map(int, input().split())
    print(a + b)

if __name__ == "__main__":
    solve()
"""

        # 테스트 케이스 준비
        test_cases = []
        for tc in problem.test_cases:
            test_cases.append({
                'input': tc.input_data,
                'output': tc.expected_output
            })

        # 솔루션 제출
        is_correct, test_results, performance = challenge_system.submit_solution(
            problem.id, sample_code, "python", test_cases
        )

        print(f"정답 여부: {'✓' if is_correct else '✗'}")
        print(f"테스트 통과: {performance.passed_test_cases}/{performance.total_test_cases}")
        print(f"평균 실행 시간: {performance.average_execution_time:.4f}초")
        print(f"코드 품질 점수: {performance.code_quality_score:.1f}/100")
        print("✓ 문제 풀이 시뮬레이션 완료\n")

    # 6. 주간 챌린지 생성
    print("6. 주간 챌린지 생성...")
    weekly_challenge = challenge_system.create_weekly_challenge()
    print(f"챌린지 이름: {weekly_challenge.name}")
    print(f"목표 문제 수: {weekly_challenge.target_problems}")
    print(f"보상 포인트: {weekly_challenge.reward_points}")
    print("✓ 주간 챌린지 생성 완료\n")

    # 7. 학습 경로 생성
    print("7. 학습 경로 생성...")
    learning_path = challenge_system.generate_learning_path("기초 알고리즘 마스터", 30)
    print(f"생성된 학습 경로 문제 수: {len(learning_path)}")
    print("학습 경로 문제들:")
    for i, problem in enumerate(learning_path[:5], 1):  # 처음 5개만 표시
        print(f"  {i}. {problem.title} ({problem.difficulty.name})")
    print("✓ 학습 경로 생성 완료\n")

    # 8. 약점/강점 분석
    print("8. 약점/강점 분석...")
    weak_areas = challenge_system.get_weak_areas(3)
    strong_areas = challenge_system.get_strong_areas(3)

    print("약점 영역:")
    for tag, count in weak_areas:
        print(f"  - {tag}: {count}문제 해결")

    print("강점 영역:")
    for tag, count in strong_areas:
        print(f"  - {tag}: {count}문제 해결")
    print("✓ 분석 완료\n")

    # 9. 커스텀 챌린지 생성
    print("9. 커스텀 챌린지 생성...")
    custom_challenge = challenge_system.create_custom_challenge(
        name="문자열 알고리즘 마스터",
        description="문자열 관련 알고리즘 문제들을 집중적으로 풀어보세요!",
        target_difficulty=ProblemDifficulty.MEDIUM,
        target_problems=5,
        time_limit_days=14
    )
    print(f"챌린지 이름: {custom_challenge.name}")
    print(f"설명: {custom_challenge.description}")
    print(f"목표 문제 수: {custom_challenge.target_problems}")
    print(f"보상 포인트: {custom_challenge.reward_points}")
    print("✓ 커스텀 챌린지 생성 완료\n")

    # 10. 활성 챌린지 확인
    print("10. 활성 챌린지 확인...")
    active_challenges = challenge_system.get_active_challenges()
    print(f"활성 챌린지 수: {len(active_challenges)}")
    for challenge in active_challenges:
        progress = challenge.get_progress_percentage()
        remaining_days = challenge.get_remaining_days()
        print(f"  - {challenge.name}: {progress:.1f}% 완료, {remaining_days}일 남음")
    print("✓ 활성 챌린지 확인 완료\n")

    # 11. 진도 보고서 생성
    print("11. 진도 보고서 생성...")
    progress_report = challenge_system.export_progress_report()
    print("진도 보고서 생성 완료:")
    print(f"  - 사용자 ID: {progress_report['user_id']}")
    print(f"  - 생성 시간: {progress_report['generated_at']}")
    print(f"  - 총 해결 문제: {progress_report['total_problems_solved']}")
    print(f"  - 현재 연속 해결: {progress_report['current_streak']}일")
    print(f"  - 최장 연속 해결: {progress_report['longest_streak']}일")
    print(f"  - 성공률: {progress_report['success_rate']:.2%}")
    print("✓ 진도 보고서 생성 완료\n")

    print("=== 모든 예제 실행 완료 ===")


def demonstrate_code_validation():
    """코드 검증 기능 시연"""
    print("=== 코드 검증 기능 시연 ===\n")

    problem_provider = MockProblemProvider()
    challenge_system = AdvancedChallengeSystem("test_user", problem_provider)

    # 샘플 문제 가져오기
    problem = problem_provider.get_problem_by_id('easy_001')
    print(f"문제: {problem.title}")
    print(f"설명: {problem.description}")

    # 다양한 코드 예제들
    code_examples = [
        {
            'name': '정답 코드',
            'code': '''
def solve():
    a, b = map(int, input().split())
    print(a + b)

if __name__ == "__main__":
    solve()
'''
        },
        {
            'name': '틀린 코드 (곱셈)',
            'code': '''
def solve():
    a, b = map(int, input().split())
    print(a * b)  # 곱셈으로 잘못 구현

if __name__ == "__main__":
    solve()
'''
        },
        {
            'name': '런타임 에러 코드',
            'code': '''
def solve():
    a, b = input().split()  # int 변환 안함
    print(a + b)  # 문자열 연결

if __name__ == "__main__":
    solve()
'''
        }
    ]

    for example in code_examples:
        print(f"\n--- {example['name']} ---")
        print(f"코드:\n{example['code']}")

        # 테스트 케이스 준비
        test_cases = []
        for tc in problem.test_cases:
            test_cases.append({
                'input': tc.input_data,
                'output': tc.expected_output
            })

        try:
            # 코드 검증
            is_correct, test_results, performance = challenge_system.submit_solution(
                problem.id, example['code'], "python", test_cases
            )

            print(f"결과: {'✓ 정답' if is_correct else '✗ 오답'}")
            print(f"테스트 통과: {performance.passed_test_cases}/{performance.total_test_cases}")
            print(f"성공률: {performance.calculate_success_rate():.1f}%")
            print(f"평균 실행 시간: {performance.average_execution_time:.4f}초")
            print(f"코드 품질 점수: {performance.code_quality_score:.1f}/100")

            # 실패한 테스트 케이스 상세 정보
            if not is_correct:
                print("실패한 테스트 케이스:")
                for result in test_results:
                    if not result.is_passed:
                        print(f"  - 입력: {result.input_data}")
                        print(f"    기대: {result.expected_output}")
                        print(f"    실제: {result.actual_output}")
                        if result.error_message:
                            print(f"    오류: {result.error_message}")

        except Exception as e:
            print(f"실행 오류: {e}")

    print("\n=== 코드 검증 시연 완료 ===")


if __name__ == "__main__":
    # 메인 예제 실행
    run_advanced_challenge_example()

    print("\n" + "="*50 + "\n")

    # 코드 검증 시연
    demonstrate_code_validation()