"""
알고리즘 문제 데이터 구조 사용 예시

이 모듈은 표준화된 알고리즘 문제 데이터 구조의 사용 방법을 보여줍니다.
다양한 난이도와 플랫폼의 예시 문제들을 포함합니다.
"""

from problem_data_structures import (
    AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag,
    ProblemTestCase, ProblemMetadata, ProblemCollection
)


def create_example_problems() -> ProblemCollection:
    """예시 문제들을 생성하여 컬렉션으로 반환"""

    collection = ProblemCollection("예시 알고리즘 문제 모음")

    # 1. 쉬운 문제 예시 - 배열의 두 수 합
    easy_problem = AlgorithmProblem(
        title="Two Sum",
        description="배열에서 두 수의 합이 목표값이 되는 인덱스를 찾는 문제",
        difficulty=ProblemDifficulty.EASY,
        platform=ProblemPlatform.LEETCODE,
        platform_problem_id="1",
        platform_url="https://leetcode.com/problems/two-sum/",
        time_limit=2.0,
        memory_limit=128,
        problem_statement="""
정수 배열 nums와 정수 target이 주어졌을 때, 두 숫자의 합이 target이 되는 인덱스를 반환하세요.
각 입력에는 정확히 하나의 해답이 있다고 가정하며, 같은 요소를 두 번 사용할 수 없습니다.
답은 어떤 순서로든 반환할 수 있습니다.
        """,
        input_format="nums = [2,7,11,15], target = 9",
        output_format="[0,1]",
        constraints="""
2 <= nums.length <= 10^4
-10^9 <= nums[i] <= 10^9
-10^9 <= target <= 10^9
정확히 하나의 유효한 답이 존재합니다.
        """,
        examples=[
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] == 9, return [0, 1]."},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": "nums[1] + nums[2] == 6, return [1, 2]."},
            {"input": "nums = [3,3], target = 6", "output": "[0,1]", "explanation": "nums[0] + nums[1] == 6, return [0, 1]."}
        ]
    )

    # 태그 추가
    easy_problem.add_tag(ProblemTag.ARRAY)
    easy_problem.add_tag(ProblemTag.HASH_TABLE)

    # 테스트 케이스 추가
    easy_problem.add_test_case(ProblemTestCase(
        input_data="[2,7,11,15]\n9",
        expected_output="[0,1]",
        description="기본 테스트 케이스"
    ))

    easy_problem.add_test_case(ProblemTestCase(
        input_data="[3,2,4]\n6",
        expected_output="[1,2]",
        description="중간에 있는 두 수의 합"
    ))

    collection.add_problem(easy_problem)

    # 2. 중간 난이도 문제 예시 - 이진 탐색
    medium_problem = AlgorithmProblem(
        title="Binary Search",
        description="정렬된 배열에서 이진 탐색을 사용하여 목표값을 찾는 문제",
        difficulty=ProblemDifficulty.MEDIUM,
        platform=ProblemPlatform.LEETCODE,
        platform_problem_id="704",
        platform_url="https://leetcode.com/problems/binary-search/",
        time_limit=1.0,
        memory_limit=64,
        problem_statement="""
오름차순으로 정렬된 정수 배열 nums와 정수 target이 주어졌을 때, target이 nums에 있으면 그 인덱스를 반환하고, 없으면 -1을 반환하세요.
O(log n) 시간 복잡도로 작성해야 합니다.
        """,
        input_format="nums = [-1,0,3,5,9,12], target = 9",
        output_format="4",
        constraints="""
1 <= nums.length <= 10^4
-10^4 < nums[i], target < 10^4
모든 정수는 고유합니다.
nums는 오름차순으로 정렬되어 있습니다.
        """,
        examples=[
            {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4", "explanation": "9 exists in nums and its index is 4"},
            {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1", "explanation": "2 does not exist in nums so return -1"}
        ]
    )

    medium_problem.add_tag(ProblemTag.ARRAY)
    medium_problem.add_tag(ProblemTag.BINARY_SEARCH)

    medium_problem.add_test_case(ProblemTestCase(
        input_data="[-1,0,3,5,9,12]\n9",
        expected_output="4",
        description="목표값이 배열에 존재하는 경우"
    ))

    medium_problem.add_test_case(ProblemTestCase(
        input_data="[-1,0,3,5,9,12]\n2",
        expected_output="-1",
        description="목표값이 배열에 존재하지 않는 경우"
    ))

    collection.add_problem(medium_problem)

    # 3. 어려운 문제 예시 - 동적 프로그래밍
    hard_problem = AlgorithmProblem(
        title="Longest Palindromic Substring",
        description="문자열에서 가장 긴 팰린드롬 부분문자열을 찾는 문제",
        difficulty=ProblemDifficulty.HARD,
        platform=ProblemPlatform.LEETCODE,
        platform_problem_id="5",
        platform_url="https://leetcode.com/problems/longest-palindromic-substring/",
        time_limit=3.0,
        memory_limit=256,
        problem_statement="""
문자열 s가 주어졌을 때, s의 가장 긴 팰린드롬 부분문자열을 반환하세요.
        """,
        input_format='s = "babad"',
        output_format='"bab"',
        constraints="""
1 <= s.length <= 1000
s는 숫자와 영문자로만 구성됩니다.
        """,
        examples=[
            {"input": 's = "babad"', "output": '"bab"', "explanation": '"aba" is also a valid answer.'},
            {"input": 's = "cbbd"', "output": '"bb"', "explanation": ""}
        ]
    )

    hard_problem.add_tag(ProblemTag.STRING)
    hard_problem.add_tag(ProblemTag.DYNAMIC_PROGRAMMING)

    hard_problem.add_test_case(ProblemTestCase(
        input_data='"babad"',
        expected_output='"bab"',
        description="홀수 길이 팰린드롬"
    ))

    hard_problem.add_test_case(ProblemTestCase(
        input_data='"cbbd"',
        expected_output='"bb"',
        description="짝수 길이 팰린드롬"
    ))

    collection.add_problem(hard_problem)

    # 4. Codeforces 문제 예시
    cf_problem = AlgorithmProblem(
        title="Watermelon",
        description="수박을 두 명이 나누어 먹을 수 있는지 확인하는 문제",
        difficulty=ProblemDifficulty.EASY,
        platform=ProblemPlatform.CODEFORCES,
        platform_problem_id="4A",
        platform_url="https://codeforces.com/problemset/problem/4/A",
        time_limit=1.0,
        memory_limit=64,
        problem_statement="""
여름의 더운 날, Pete와 그의 친구 Billy는 수박을 사기로 결정했습니다.
그들은 가장 크고 무거운 것을 선택했습니다. 수박의 무게를 측정한 후,
그들은 집으로 돌아가서 수박을 나누기로 했습니다.

그러나 그들은 문제에 직면했습니다:
수박은 너무 무거워서 한 번에 들 수 없고,
그들은 수박을 두 부분으로 나누어야 합니다.
그들은 각각 짝수 무게의 부분을 원합니다.

수박의 무게 w가 주어졌을 때,
Pete와 Billy가 각각 짝수 무게의 부분을 가질 수 있는지 판단하세요.
        """,
        input_format="8",
        output_format="YES",
        constraints="""
1 ≤ w ≤ 100
        """,
        examples=[
            {"input": "8", "output": "YES", "explanation": "8 = 4 + 4"},
            {"input": "2", "output": "NO", "explanation": "2는 두 개의 짝수로 나눌 수 없습니다"}
        ]
    )

    cf_problem.add_tag(ProblemTag.MATH)
    cf_problem.add_tag(ProblemTag.BRUTE_FORCE)

    cf_problem.add_test_case(ProblemTestCase(
        input_data="8",
        expected_output="YES",
        description="짝수 무게로 나눌 수 있는 경우"
    ))

    cf_problem.add_test_case(ProblemTestCase(
        input_data="2",
        expected_output="NO",
        description="짝수 무게로 나눌 수 없는 경우"
    ))

    collection.add_problem(cf_problem)

    # 5. 로컬 문제 예시
    local_problem = AlgorithmProblem(
        title="피보나치 수열 계산",
        description="n번째 피보나치 수를 계산하는 문제",
        difficulty=ProblemDifficulty.MEDIUM,
        platform=ProblemPlatform.LOCAL,
        time_limit=1.0,
        memory_limit=128,
        problem_statement="""
피보나치 수열은 다음과 같이 정의됩니다:
F(0) = 0, F(1) = 1
F(n) = F(n-1) + F(n-2) (n ≥ 2)

n이 주어졌을 때, F(n)을 계산하세요.
        """,
        input_format="10",
        output_format="55",
        constraints="""
0 ≤ n ≤ 45
        """,
        examples=[
            {"input": "0", "output": "0", "explanation": "F(0) = 0"},
            {"input": "1", "output": "1", "explanation": "F(1) = 1"},
            {"input": "10", "output": "55", "explanation": "F(10) = 55"}
        ]
    )

    local_problem.add_tag(ProblemTag.DYNAMIC_PROGRAMMING)
    local_problem.add_tag(ProblemTag.MATH)

    local_problem.add_test_case(ProblemTestCase(
        input_data="0",
        expected_output="0",
        description="F(0) = 0"
    ))

    local_problem.add_test_case(ProblemTestCase(
        input_data="10",
        expected_output="55",
        description="F(10) = 55"
    ))

    collection.add_problem(local_problem)

    return collection


def demonstrate_data_structures():
    """데이터 구조의 기능을 시연"""

    print("=== 알고리즘 문제 데이터 구조 시연 ===\n")

    # 예시 문제 컬렉션 생성
    collection = create_example_problems()

    print(f"컬렉션 이름: {collection.name}")
    print(f"총 문제 수: {collection.get_problem_count()}\n")

    # 모든 문제 출력
    print("=== 모든 문제 목록 ===")
    for i, problem in enumerate(collection.get_all_problems(), 1):
        print(f"{i}. {problem}")
        print(f"   플랫폼: {problem.platform}")
        print(f"   난이도: {problem.difficulty}")
        print(f"   태그: {', '.join(str(tag) for tag in problem.tags)}")
        print()

    # 난이도별 문제 조회
    print("=== 난이도별 문제 조회 ===")
    for difficulty in ProblemDifficulty:
        problems = collection.get_problems_by_difficulty(difficulty)
        print(f"{difficulty.name}: {len(problems)}개")
        for problem in problems:
            print(f"  - {problem.title}")
        print()

    # 플랫폼별 문제 조회
    print("=== 플랫폼별 문제 조회 ===")
    for platform in ProblemPlatform:
        problems = collection.get_problems_by_platform(platform)
        if problems:  # 문제가 있는 플랫폼만 출력
            print(f"{platform.name}: {len(problems)}개")
            for problem in problems:
                print(f"  - {problem.title}")
            print()

    # 태그별 문제 조회
    print("=== 태그별 문제 조회 ===")
    for tag in [ProblemTag.ARRAY, ProblemTag.DYNAMIC_PROGRAMMING, ProblemTag.MATH]:
        problems = collection.get_problems_by_tag(tag)
        print(f"{tag}: {len(problems)}개")
        for problem in problems:
            print(f"  - {problem.title}")
        print()

    # JSON 직렬화/역직렬화 테스트
    print("=== JSON 직렬화 테스트 ===")
    json_str = collection.to_json()
    print(f"JSON 길이: {len(json_str)} 문자")

    # JSON에서 다시 객체 생성
    restored_collection = ProblemCollection.from_json(json_str)
    print(f"복원된 컬렉션 문제 수: {restored_collection.get_problem_count()}")

    # 개별 문제 JSON 테스트
    first_problem = collection.get_all_problems()[0]
    problem_json = first_problem.to_json()
    restored_problem = AlgorithmProblem.from_json(problem_json)
    print(f"복원된 문제: {restored_problem}")

    print("\n=== 시연 완료 ===")


if __name__ == "__main__":
    demonstrate_data_structures()