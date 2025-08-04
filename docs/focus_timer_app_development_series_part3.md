# 🧮 GUI와 알고리즘의 완벽한 융합: FocusTimer.app 개발기 (Part 3 알고리즘 시스템 통합편)

## 📋 목차

- [알고리즘 시스템 통합의 필요성](#-알고리즘-시스템-통합의-필요성)
- [알고리즘 탭 GUI 설계](#-알고리즘-탭-gui-설계)
- [고급 챌린지 시스템 개발](#-고급-챌린지-시스템-개발)
- [사용자 진행도 추적 시스템](#-사용자-진행도-추적-시스템)
- [코드 실행 및 검증 시스템](#-코드-실행-및-검증-시스템)
- [개인화된 학습 경로 생성](#-개인화된-학습-경로-생성)
- [성능 분석 및 통계 시스템](#-성능-분석-및-통계-시스템)
- [결론 및 다음 편 예고](#-결론-및-다음-편-예고)

---

## 🎯 알고리즘 시스템 통합의 필요성

### **기존 타이머 시스템의 한계**

FocusTimer의 핵심 기능인 집중 모드는 성공적으로 구현되었지만, 사용자들이 실제로 집중 시간 동안 무엇을 할지에 대한 구체적인 가이드가 부족했습니다:

#### **문제점 1: 집중 시간 활용의 불명확성**

```python
# 기존 시스템의 한계
class FocusTimer:
    def start_focus_mode(self):
        # 집중 모드 시작
        # ❌ 구체적인 활동 가이드 없음
        # ❌ 사용자가 무엇을 해야 할지 모름
        # ❌ 단순히 시간만 카운트
```

#### **문제점 2: 학습 효과 측정의 부재**

```python
# 기존 통계의 한계
def get_focus_statistics(self):
    return {
        'total_focus_time': 120,  # 분 단위
        'sessions_completed': 5,
        # ❌ 실제 학습 성과 측정 불가
        # ❌ 문제 해결 능력 향상 추적 불가
        # ❌ 개인화된 피드백 부재
    }
```

#### **문제점 3: 동기 부여 요소 부족**

```python
# 기존 시스템의 한계
def complete_focus_session(self):
    # 집중 세션 완료
    # ❌ 성취감 부족
    # ❌ 구체적인 목표 없음
    # ❌ 지속적인 동기 부여 부재
```

### **해결 방향**

> **알고리즘 문제 풀이 시스템을 통합하여 구체적이고 측정 가능한 학습 경험 제공**

---

## 🎨 알고리즘 탭 GUI 설계

### **1단계: SafeImporter 시스템 개발**

#### **앱 번들 내 모듈 Import 문제 해결**

```python
# algorithm_tab.py - SafeImporter를 사용한 안전한 import
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from pathlib import Path

# SafeImporter를 사용한 안전한 import
try:
    from import_utils import get_importer

    # SafeImporter 인스턴스 가져오기
    importer = get_importer()

    # 알고리즘 모듈들을 안전하게 import
    modules = importer.import_algorithm_modules()

    # 필요한 클래스들 가져오기
    if 'gui_algorithm_manager' in modules:
        MockProblemProvider = modules['gui_algorithm_manager'].MockProblemProvider
    else:
        MockProblemProvider = None

    if 'advanced_challenge_system' in modules:
        AdvancedChallengeSystem = modules['advanced_challenge_system'].AdvancedChallengeSystem
    else:
        AdvancedChallengeSystem = None

    if 'user_progress_tracker' in modules:
        UserProgressTracker = modules['user_progress_tracker'].UserProgressTracker
    else:
        UserProgressTracker = None

    # 핵심 모듈들이 모두 로드되었는지 확인
    ALGORITHM_MODULES_LOADED = all([
        MockProblemProvider is not None,
        AdvancedChallengeSystem is not None,
        UserProgressTracker is not None
    ])

    if ALGORITHM_MODULES_LOADED:
        print("✅ SafeImporter를 통한 알고리즘 모듈 로드 성공")
    else:
        print("⚠️ 일부 알고리즘 모듈이 로드되지 않았습니다")

except ImportError as e:
    print(f"❌ SafeImporter 로드 실패: {e}")
    ALGORITHM_MODULES_LOADED = False
```

#### **알고리즘 탭 클래스 설계**

```python
class AlgorithmTab:
    """알고리즘 시스템 탭 - FocusTimer.app의 notebook에 삽입될 위젯"""

    def __init__(self, master):
        """
        Args:
            master: ttk.Notebook 인스턴스
        """
        self.master = master
        self.frame = ttk.Frame(master, padding="10")

        # 알고리즘 시스템 초기화
        self.algorithm_system_ready = False
        self.problem_provider = None
        self.challenge_system = None
        self.user_progress = None

        # UI 구성
        self._build_ui()

        # 알고리즘 시스템 초기화
        if ALGORITHM_MODULES_LOADED:
            self._init_algorithm_system()

    def _build_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 좌측 패널 (문제 추천 및 챌린지)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 문제 추천 섹션
        recommendations_frame = ttk.LabelFrame(left_panel, text="📚 추천 문제", padding="10")
        recommendations_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 추천 문제 목록
        self.recommendations_tree = ttk.Treeview(recommendations_frame,
                                               columns=('title', 'difficulty', 'tags'),
                                               show='headings', height=8)
        self.recommendations_tree.heading('title', text='제목')
        self.recommendations_tree.heading('difficulty', text='난이도')
        self.recommendations_tree.heading('tags', text='태그')
        self.recommendations_tree.column('title', width=200)
        self.recommendations_tree.column('difficulty', width=80)
        self.recommendations_tree.column('tags', width=120)
        self.recommendations_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
```

### **2단계: MockProblemProvider 시스템**

#### **GUI 테스트용 문제 제공자**

```python
class MockProblemProvider:
    """GUI 테스트용 문제 제공자"""

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

        # 문제 객체 생성
        for problem_data in easy_problems + medium_problems:
            problem = AlgorithmProblem(
                problem_id=problem_data['id'],
                title=problem_data['title'],
                description=problem_data['description'],
                difficulty=problem_data['difficulty'],
                tags=problem_data['tags'],
                test_cases=problem_data['test_cases']
            )
            problems.append(problem)

        return problems

    def get_all_problems(self) -> List[AlgorithmProblem]:
        """모든 문제 반환"""
        return self.problems

    def get_problem_by_id(self, problem_id: str) -> AlgorithmProblem:
        """ID로 문제 조회"""
        for problem in self.problems:
            if problem.problem_id == problem_id:
                return problem
        return None
```

---

## 🏆 고급 챌린지 시스템 개발

### **1단계: 챌린지 데이터 구조 설계**

#### **챌린지 유형 및 상태 정의**

```python
class ChallengeType(Enum):
    """챌린지 유형"""
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    CUSTOM = auto()
    STREAK = auto()  # 연속 해결 챌린지


class ChallengeStatus(Enum):
    """챌린지 상태"""
    ACTIVE = auto()
    COMPLETED = auto()
    FAILED = auto()
    EXPIRED = auto()


@dataclass
class Challenge:
    """챌린지 정보"""
    challenge_id: str
    name: str
    description: str
    challenge_type: ChallengeType
    target_difficulty: ProblemDifficulty
    target_problems: int
    time_limit_days: int
    start_date: datetime
    end_date: datetime
    problems: List[str] = field(default_factory=list)  # problem_id 리스트
    completed_problems: List[str] = field(default_factory=list)
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    reward_points: int = 0
    bonus_conditions: Dict[str, Any] = field(default_factory=dict)

    def get_progress_percentage(self) -> float:
        """진도율 계산"""
        if not self.problems:
            return 0.0
        return len(self.completed_problems) / len(self.problems) * 100

    def get_remaining_days(self) -> int:
        """남은 일수 계산"""
        remaining = self.end_date - datetime.now()
        return max(0, remaining.days)

    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.now() > self.end_date
```

#### **코드 테스트 결과 구조**

```python
@dataclass
class CodeTestResult:
    """코드 테스트 결과"""
    test_case_id: str
    input_data: str
    expected_output: str
    actual_output: str
    is_passed: bool
    execution_time: float
    memory_used: int
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'test_case_id': self.test_case_id,
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'actual_output': self.actual_output,
            'is_passed': self.is_passed,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'error_message': self.error_message
        }


@dataclass
class PerformanceMetrics:
    """성능 지표"""
    total_test_cases: int
    passed_test_cases: int
    failed_test_cases: int
    average_execution_time: float
    max_execution_time: float
    min_execution_time: float
    average_memory_used: int
    max_memory_used: int
    time_complexity_estimate: str
    space_complexity_estimate: str
    code_quality_score: float

    def calculate_success_rate(self) -> float:
        """성공률 계산"""
        if self.total_test_cases == 0:
            return 0.0
        return self.passed_test_cases / self.total_test_cases
```

### **2단계: 문제 난이도 선택 시스템**

#### **난이도별 문제 선별 로직**

```python
class ProblemDifficultySelector:
    """문제 난이도 선택기"""

    def __init__(self, problem_provider):
        self.problem_provider = problem_provider

    def select_problems_by_difficulty(self, difficulty: ProblemDifficulty,
                                    count: int = 10,
                                    exclude_solved: Optional[List[str]] = None) -> List[AlgorithmProblem]:
        """난이도별 문제 선택"""
        all_problems = self.problem_provider.get_all_problems()
        exclude_set = set(exclude_solved or [])

        # 해당 난이도의 문제들 필터링
        filtered_problems = [
            problem for problem in all_problems
            if problem.difficulty == difficulty and problem.problem_id not in exclude_set
        ]

        # 문제 품질 점수로 정렬
        filtered_problems.sort(
            key=lambda p: self._calculate_problem_quality_score(p),
            reverse=True
        )

        return filtered_problems[:count]

    def _calculate_problem_quality_score(self, problem: AlgorithmProblem) -> float:
        """문제 품질 점수 계산"""
        score = 0.0

        # 테스트 케이스 수에 따른 점수
        test_case_count = len(problem.test_cases)
        if test_case_count >= 5:
            score += 10.0
        elif test_case_count >= 3:
            score += 7.0
        elif test_case_count >= 1:
            score += 5.0

        # 태그 다양성에 따른 점수
        tag_count = len(problem.tags)
        if tag_count >= 3:
            score += 5.0
        elif tag_count >= 2:
            score += 3.0
        else:
            score += 1.0

        # 설명 길이에 따른 점수
        description_length = len(problem.description)
        if description_length >= 100:
            score += 3.0
        elif description_length >= 50:
            score += 2.0
        else:
            score += 1.0

        return score
```

### **3단계: 사용자 기반 추천 시스템**

#### **개인화된 문제 추천**

```python
class UserBasedRecommender:
    """사용자 기반 추천 시스템"""

    def __init__(self, progress_tracker: UserProgressTracker, problem_provider):
        self.progress_tracker = progress_tracker
        self.problem_provider = problem_provider

    def get_personalized_recommendations(self, count: int = 5) -> List[AlgorithmProblem]:
        """개인화된 문제 추천"""
        user_level = self.progress_tracker.get_user_level()
        solved_problems = set(self.progress_tracker.get_solved_problems())
        weak_tags = self.progress_tracker.get_weak_tags(limit=3)
        strong_tags = self.progress_tracker.get_strong_tags(limit=2)

        recommendations = []
        exclude_problems = solved_problems.copy()

        # 1. 약점 태그 기반 추천 (40%)
        weak_tag_count = max(1, count // 3)
        for tag, _ in weak_tags[:2]:
            problems = self._get_problems_by_tags([tag], weak_tag_count, exclude_problems, user_level)
            recommendations.extend(problems)
            exclude_problems.update(p.problem_id for p in problems)

        # 2. 현재 레벨에 적합한 문제 추천 (40%)
        current_level_count = max(1, count // 3)
        current_difficulty = self.progress_tracker.get_recommended_difficulty()
        problems = self._get_problems_by_difficulty(current_difficulty, current_level_count, exclude_problems)
        recommendations.extend(problems)
        exclude_problems.update(p.problem_id for p in problems)

        # 3. 다음 레벨 준비를 위한 문제 추천 (20%)
        next_level_count = count - len(recommendations)
        if next_level_count > 0:
            next_problems = self._get_next_level_problems(next_level_count, exclude_problems, user_level)
            recommendations.extend(next_problems)

        return recommendations[:count]

    def _get_problems_by_tags(self, tags: List[str], count: int,
                             exclude_problems: set, user_level: int) -> List[AlgorithmProblem]:
        """태그 기반 문제 조회"""
        all_problems = self.problem_provider.get_all_problems()

        filtered_problems = [
            problem for problem in all_problems
            if problem.problem_id not in exclude_problems and
            any(tag in problem.tags for tag in tags)
        ]

        # 사용자 레벨에 맞는 난이도로 필터링
        filtered_problems = [
            problem for problem in filtered_problems
            if self._is_appropriate_difficulty(problem.difficulty, user_level)
        ]

        return filtered_problems[:count]

    def _get_problems_by_difficulty(self, difficulty: ProblemDifficulty,
                                   count: int, exclude_problems: set) -> List[AlgorithmProblem]:
        """난이도별 문제 조회"""
        all_problems = self.problem_provider.get_all_problems()

        filtered_problems = [
            problem for problem in all_problems
            if problem.problem_id not in exclude_problems and
            problem.difficulty == difficulty
        ]

        return filtered_problems[:count]

    def _get_next_level_problems(self, count: int, exclude_problems: set,
                                user_level: int) -> List[AlgorithmProblem]:
        """다음 레벨 준비 문제 조회"""
        if user_level >= 10:
            return []

        next_level = min(10, user_level + 1)
        next_difficulty = self._get_difficulty_by_level(next_level)

        return self._get_problems_by_difficulty(next_difficulty, count, exclude_problems)

    def _is_appropriate_difficulty(self, difficulty: ProblemDifficulty, user_level: int) -> bool:
        """사용자 레벨에 적합한 난이도인지 확인"""
        difficulty_score = self._get_difficulty_score(difficulty)
        return user_level - 1 <= difficulty_score <= user_level + 1

    def _get_difficulty_score(self, difficulty: ProblemDifficulty) -> int:
        """난이도 점수 반환"""
        difficulty_scores = {
            ProblemDifficulty.EASY: 1,
            ProblemDifficulty.MEDIUM: 3,
            ProblemDifficulty.HARD: 6,
            ProblemDifficulty.EXPERT: 9
        }
        return difficulty_scores.get(difficulty, 1)
```

---

## 📊 사용자 진행도 추적 시스템

### **1단계: 제출 상태 및 성취도 구조**

#### **제출 상태 정의**

```python
class SubmissionStatus(Enum):
    """제출 상태"""
    CORRECT = auto()
    WRONG_ANSWER = auto()
    TIME_LIMIT_EXCEEDED = auto()
    MEMORY_LIMIT_EXCEEDED = auto()
    RUNTIME_ERROR = auto()
    COMPILATION_ERROR = auto()
    PARTIALLY_CORRECT = auto()
    NOT_ATTEMPTED = auto()


@dataclass
class ProblemSubmission:
    """문제 제출 기록"""
    problem_id: str
    submission_time: datetime
    status: SubmissionStatus
    execution_time: Optional[float] = None  # 초 단위
    memory_used: Optional[int] = None  # MB 단위
    code_language: Optional[str] = None
    code_length: Optional[int] = None  # 문자 수
    attempt_count: int = 1
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'problem_id': self.problem_id,
            'submission_time': self.submission_time.isoformat(),
            'status': self.status.name,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'code_language': self.code_language,
            'code_length': self.code_length,
            'attempt_count': self.attempt_count,
            'notes': self.notes
        }
```

#### **사용자 성취도 추적**

```python
@dataclass
class UserAchievement:
    """사용자 성취도"""
    total_problems_solved: int = 0
    total_submissions: int = 0
    correct_submissions: int = 0
    average_attempts_per_problem: float = 0.0
    average_solve_time: float = 0.0  # 분 단위
    current_streak: int = 0  # 연속 해결 일수
    longest_streak: int = 0
    last_solved_date: Optional[datetime] = None

    # 난이도별 성취도
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    expert_solved: int = 0

    # 태그별 성취도
    tag_achievements: Dict[str, int] = field(default_factory=dict)

    def calculate_success_rate(self) -> float:
        """성공률 계산"""
        if self.total_submissions == 0:
            return 0.0
        return self.correct_submissions / self.total_submissions

    def calculate_difficulty_level(self) -> int:
        """현재 난이도 레벨 계산 (1-10)"""
        total_solved = self.total_problems_solved
        if total_solved == 0:
            return 1

        # 난이도별 가중치
        weighted_score = (
            self.easy_solved * 1 +
            self.medium_solved * 2 +
            self.hard_solved * 3 +
            self.expert_solved * 4
        )

        # 기본 레벨 계산
        base_level = min(10, max(1, weighted_score // 10 + 1))

        # 성공률 보정
        success_rate = self.calculate_success_rate()
        if success_rate > 0.8:
            base_level = min(10, base_level + 1)
        elif success_rate < 0.5:
            base_level = max(1, base_level - 1)

        return base_level
```

### **2단계: 진행도 추적기 구현**

#### **UserProgressTracker 클래스**

```python
class UserProgressTracker:
    """사용자 진행도 추적기"""

    def __init__(self, user_id: str, data_dir: str = "user_data"):
        self.user_id = user_id
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, f"{user_id}_progress.json")

        # 사용자 데이터 초기화
        self.achievement = UserAchievement()
        self.submissions: List[ProblemSubmission] = []
        self.learning_paths: List[LearningPath] = []

        # 데이터 로드
        self._load_user_data()

    def _load_user_data(self):
        """사용자 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 성취도 로드
                if 'achievement' in data:
                    self.achievement = UserAchievement.from_dict(data['achievement'])

                # 제출 기록 로드
                if 'submissions' in data:
                    self.submissions = [
                        ProblemSubmission.from_dict(submission_data)
                        for submission_data in data['submissions']
                    ]

                # 학습 경로 로드
                if 'learning_paths' in data:
                    self.learning_paths = [
                        LearningPath.from_dict(path_data)
                        for path_data in data['learning_paths']
                    ]

        except Exception as e:
            print(f"사용자 데이터 로드 실패: {e}")

    def _save_user_data(self):
        """사용자 데이터 저장"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)

            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'achievement': self.achievement.to_dict(),
                'submissions': [submission.to_dict() for submission in self.submissions],
                'learning_paths': [path.to_dict() for path in self.learning_paths]
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"사용자 데이터 저장 실패: {e}")

    def add_submission(self, submission: ProblemSubmission):
        """제출 기록 추가"""
        self.submissions.append(submission)
        self._update_achievement(submission)
        self._save_user_data()

    def _update_achievement(self, submission: ProblemSubmission):
        """성취도 업데이트"""
        # 기본 통계 업데이트
        self.achievement.total_submissions += 1

        if submission.status == SubmissionStatus.CORRECT:
            self.achievement.correct_submissions += 1
            self.achievement.total_problems_solved += 1
            self._update_streak(submission.submission_time)

        # 평균 시도 횟수 업데이트
        problem_submissions = [
            s for s in self.submissions
            if s.problem_id == submission.problem_id
        ]
        self.achievement.average_attempts_per_problem = len(problem_submissions)

        # 평균 해결 시간 업데이트
        if submission.status == SubmissionStatus.CORRECT and submission.execution_time:
            correct_submissions = [
                s for s in self.submissions
                if s.status == SubmissionStatus.CORRECT and s.execution_time
            ]
            if correct_submissions:
                avg_time = sum(s.execution_time for s in correct_submissions) / len(correct_submissions)
                self.achievement.average_solve_time = avg_time / 60  # 분 단위로 변환

    def _update_streak(self, solve_date: datetime):
        """연속 해결 일수 업데이트"""
        if self.achievement.last_solved_date:
            days_diff = (solve_date.date() - self.achievement.last_solved_date.date()).days

            if days_diff == 1:
                # 연속 해결
                self.achievement.current_streak += 1
            elif days_diff > 1:
                # 연속 끊김
                self.achievement.current_streak = 1
            # days_diff == 0인 경우 같은 날 해결이므로 streak 유지
        else:
            # 첫 번째 해결
            self.achievement.current_streak = 1

        # 최장 연속 기록 업데이트
        if self.achievement.current_streak > self.achievement.longest_streak:
            self.achievement.longest_streak = self.achievement.current_streak

        self.achievement.last_solved_date = solve_date

    def get_user_level(self) -> int:
        """사용자 레벨 반환"""
        return self.achievement.calculate_difficulty_level()

    def get_recommended_difficulty(self) -> ProblemDifficulty:
        """추천 난이도 반환"""
        user_level = self.get_user_level()

        if user_level <= 3:
            return ProblemDifficulty.EASY
        elif user_level <= 6:
            return ProblemDifficulty.MEDIUM
        elif user_level <= 9:
            return ProblemDifficulty.HARD
        else:
            return ProblemDifficulty.EXPERT

    def get_weak_tags(self, limit: int = 5) -> List[Tuple[str, int]]:
        """약점 태그 반환"""
        tag_counts = {}

        for submission in self.submissions:
            if submission.status == SubmissionStatus.CORRECT:
                # 해결한 문제의 태그는 제외
                continue

            # 문제 정보 가져오기 (실제 구현에서는 problem_provider 사용)
            # 여기서는 간단히 problem_id 기반으로 추정
            if submission.problem_id.startswith('easy'):
                tags = ['ARRAY', 'MATH']
            elif submission.problem_id.startswith('medium'):
                tags = ['BINARY_SEARCH', 'TWO_POINTERS']
            else:
                tags = ['DYNAMIC_PROGRAMMING', 'GRAPH']

            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 실패 횟수로 정렬
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]

    def get_strong_tags(self, limit: int = 5) -> List[Tuple[str, int]]:
        """강점 태그 반환"""
        tag_counts = {}

        for submission in self.submissions:
            if submission.status == SubmissionStatus.CORRECT:
                # 해결한 문제의 태그만 카운트
                if submission.problem_id.startswith('easy'):
                    tags = ['ARRAY', 'MATH']
                elif submission.problem_id.startswith('medium'):
                    tags = ['BINARY_SEARCH', 'TWO_POINTERS']
                else:
                    tags = ['DYNAMIC_PROGRAMMING', 'GRAPH']

                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 성공 횟수로 정렬
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]
```

---

## 🔧 코드 실행 및 검증 시스템

### **1단계: 코드 검증기 구현**

#### **CodeValidator 클래스**

```python
class CodeValidator:
    """코드 검증기"""

    def __init__(self):
        self.supported_languages = ['python', 'java', 'cpp']
        self.timeout_seconds = 5
        self.memory_limit_mb = 128

    def validate_code(self, code: str, language: str,
                     test_cases: List[Dict[str, str]]) -> List[CodeTestResult]:
        """코드 검증"""
        if language.lower() not in self.supported_languages:
            raise ValueError(f"지원하지 않는 언어: {language}")

        results = []

        for i, test_case in enumerate(test_cases):
            test_id = f"test_{i+1}"
            result = self._run_test_case(code, language, test_case, test_id)
            results.append(result)

        return results

    def _run_test_case(self, code: str, language: str,
                      test_case: Dict[str, str], test_id: str) -> CodeTestResult:
        """개별 테스트 케이스 실행"""
        start_time = time.time()

        try:
            if language.lower() == 'python':
                return self._run_python_test(code, test_case, test_id)
            elif language.lower() == 'java':
                return self._run_java_test(code, test_case, test_id)
            elif language.lower() == 'cpp':
                return self._run_cpp_test(code, test_case, test_id)
            else:
                return CodeTestResult(
                    test_case_id=test_id,
                    input_data=test_case['input'],
                    expected_output=test_case['output'],
                    actual_output="",
                    is_passed=False,
                    execution_time=0.0,
                    memory_used=0,
                    error_message=f"지원하지 않는 언어: {language}"
                )
        except Exception as e:
            execution_time = time.time() - start_time
            return CodeTestResult(
                test_case_id=test_id,
                input_data=test_case['input'],
                expected_output=test_case['output'],
                actual_output="",
                is_passed=False,
                execution_time=execution_time,
                memory_used=0,
                error_message=str(e)
            )

    def _run_python_test(self, code: str, test_case: Dict[str, str],
                        test_id: str) -> CodeTestResult:
        """Python 코드 테스트"""
        start_time = time.time()

        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # 입력 데이터 준비
            input_data = test_case['input']
            expected_output = test_case['output'].strip()

            # 프로세스 실행
            process = subprocess.Popen(
                ['python', temp_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(
                    input=input_data,
                    timeout=self.timeout_seconds
                )

                execution_time = time.time() - start_time
                actual_output = stdout.strip()

                # 결과 비교
                is_passed = actual_output == expected_output

                return CodeTestResult(
                    test_case_id=test_id,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    is_passed=is_passed,
                    execution_time=execution_time,
                    memory_used=0,  # Python에서는 메모리 측정이 복잡하므로 0으로 설정
                    error_message=stderr if stderr else None
                )

            except subprocess.TimeoutExpired:
                process.kill()
                execution_time = time.time() - start_time
                return CodeTestResult(
                    test_case_id=test_id,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output="",
                    is_passed=False,
                    execution_time=execution_time,
                    memory_used=0,
                    error_message="시간 초과"
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return CodeTestResult(
                test_case_id=test_id,
                input_data=input_data,
                expected_output=expected_output,
                actual_output="",
                is_passed=False,
                execution_time=execution_time,
                memory_used=0,
                error_message=str(e)
            )
        finally:
            # 임시 파일 정리
            try:
                os.unlink(temp_file)
            except:
                pass
```

### **2단계: 성능 분석기 구현**

#### **PerformanceAnalyzer 클래스**

```python
class PerformanceAnalyzer:
    """성능 분석기"""

    def __init__(self):
        self.complexity_patterns = {
            'O(1)': ['constant', 'hash', 'direct_access'],
            'O(log n)': ['binary_search', 'logarithmic', 'divide_conquer'],
            'O(n)': ['linear', 'single_loop', 'traversal'],
            'O(n log n)': ['sort', 'merge_sort', 'quick_sort'],
            'O(n²)': ['nested_loop', 'quadratic', 'bubble_sort'],
            'O(2^n)': ['recursive', 'exponential', 'backtracking']
        }

    def analyze_performance(self, test_results: List[CodeTestResult],
                          code: str) -> PerformanceMetrics:
        """성능 분석"""
        if not test_results:
            return PerformanceMetrics(
                total_test_cases=0,
                passed_test_cases=0,
                failed_test_cases=0,
                average_execution_time=0.0,
                max_execution_time=0.0,
                min_execution_time=0.0,
                average_memory_used=0,
                max_memory_used=0,
                time_complexity_estimate="Unknown",
                space_complexity_estimate="Unknown",
                code_quality_score=0.0
            )

        # 기본 통계 계산
        total_test_cases = len(test_results)
        passed_test_cases = sum(1 for result in test_results if result.is_passed)
        failed_test_cases = total_test_cases - passed_test_cases

        # 실행 시간 통계
        execution_times = [result.execution_time for result in test_results if result.execution_time is not None]
        if execution_times:
            average_execution_time = statistics.mean(execution_times)
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
        else:
            average_execution_time = max_execution_time = min_execution_time = 0.0

        # 메모리 사용량 통계
        memory_usage = [result.memory_used for result in test_results if result.memory_used is not None]
        if memory_usage:
            average_memory_used = int(statistics.mean(memory_usage))
            max_memory_used = max(memory_usage)
        else:
            average_memory_used = max_memory_used = 0

        # 복잡도 추정
        time_complexity = self._estimate_time_complexity(code, test_results)
        space_complexity = self._estimate_space_complexity(code)

        # 코드 품질 점수
        code_quality_score = self._calculate_code_quality_score(code, test_results)

        return PerformanceMetrics(
            total_test_cases=total_test_cases,
            passed_test_cases=passed_test_cases,
            failed_test_cases=failed_test_cases,
            average_execution_time=average_execution_time,
            max_execution_time=max_execution_time,
            min_execution_time=min_execution_time,
            average_memory_used=average_memory_used,
            max_memory_used=max_memory_used,
            time_complexity_estimate=time_complexity,
            space_complexity_estimate=space_complexity,
            code_quality_score=code_quality_score
        )

    def _estimate_time_complexity(self, code: str,
                                test_results: List[CodeTestResult]) -> str:
        """시간 복잡도 추정"""
        code_lower = code.lower()

        # 패턴 매칭
        for complexity, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                if pattern in code_lower:
                    return complexity

        # 기본 추정
        if 'for' in code_lower and 'for' in code_lower:
            return 'O(n²)'  # 중첩 루프
        elif 'for' in code_lower or 'while' in code_lower:
            return 'O(n)'   # 단일 루프
        else:
            return 'O(1)'   # 상수 시간

    def _estimate_space_complexity(self, code: str) -> str:
        """공간 복잡도 추정"""
        code_lower = code.lower()

        if 'list(' in code_lower or '[]' in code_lower:
            return 'O(n)'
        elif 'dict(' in code_lower or '{}' in code_lower:
            return 'O(n)'
        else:
            return 'O(1)'

    def _calculate_code_quality_score(self, code: str,
                                    test_results: List[CodeTestResult]) -> float:
        """코드 품질 점수 계산"""
        score = 0.0

        # 가독성 점수 (30%)
        readability_score = self._calculate_readability_score(code)
        score += readability_score * 0.3

        # 효율성 점수 (40%)
        efficiency_score = self._calculate_efficiency_score(test_results)
        score += efficiency_score * 0.4

        # 정확성 점수 (30%)
        accuracy_score = sum(1 for result in test_results if result.is_passed) / len(test_results)
        score += accuracy_score * 0.3

        return min(100.0, score * 100)

    def _calculate_readability_score(self, code: str) -> float:
        """가독성 점수 계산"""
        score = 1.0

        # 주석 비율
        lines = code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        comment_ratio = comment_lines / len(lines) if lines else 0

        if 0.1 <= comment_ratio <= 0.3:
            score += 0.2
        elif comment_ratio > 0.3:
            score += 0.1

        # 함수 길이
        if len(code) < 100:
            score += 0.2
        elif len(code) < 300:
            score += 0.1

        # 변수명 품질
        if 'i' in code and 'j' in code and 'k' in code:
            score -= 0.1  # 너무 단순한 변수명

        return max(0.0, min(1.0, score))

    def _calculate_efficiency_score(self, test_results: List[CodeTestResult]) -> float:
        """효율성 점수 계산"""
        if not test_results:
            return 0.0

        # 실행 시간 기반 점수
        execution_times = [result.execution_time for result in test_results if result.execution_time is not None]
        if not execution_times:
            return 0.5

        avg_time = statistics.mean(execution_times)

        # 실행 시간이 빠를수록 높은 점수
        if avg_time < 0.001:
            return 1.0
        elif avg_time < 0.01:
            return 0.9
        elif avg_time < 0.1:
            return 0.8
        elif avg_time < 1.0:
            return 0.7
        else:
            return 0.5
```

---

## 🛤️ 개인화된 학습 경로 생성

### **1단계: 학습 경로 데이터 구조**

#### **LearningPath 클래스**

```python
@dataclass
class LearningPath:
    """학습 경로"""
    path_id: str
    name: str
    description: str
    target_difficulty: ProblemDifficulty
    estimated_duration_days: int
    problems: List[str] = field(default_factory=list)  # problem_id 리스트
    completed_problems: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    is_active: bool = True

    def get_progress_percentage(self) -> float:
        """진도율 계산"""
        if not self.problems:
            return 0.0
        return len(self.completed_problems) / len(self.problems) * 100

    def get_remaining_problems(self) -> List[str]:
        """남은 문제 목록"""
        return [pid for pid in self.problems if pid not in self.completed_problems]

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'path_id': self.path_id,
            'name': self.name,
            'description': self.description,
            'target_difficulty': self.target_difficulty.name,
            'estimated_duration_days': self.estimated_duration_days,
            'problems': self.problems,
            'completed_problems': self.completed_problems,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'is_active': self.is_active
        }
```

### **2단계: 학습 경로 생성기 구현**

#### **LearningPathGenerator 클래스**

```python
class LearningPathGenerator:
    """학습 경로 생성기"""

    def __init__(self, progress_tracker: UserProgressTracker, problem_provider):
        self.progress_tracker = progress_tracker
        self.problem_provider = problem_provider

    def generate_personalized_path(self, target_goal: str,
                                 duration_days: int = 30) -> List[AlgorithmProblem]:
        """개인화된 학습 경로 생성"""
        user_level = self.progress_tracker.get_user_level()
        solved_problems = set(self.progress_tracker.get_solved_problems())
        weak_tags = self.progress_tracker.get_weak_tags(limit=5)

        if target_goal.lower() == 'basic':
            return self._generate_basic_path(user_level, solved_problems, duration_days)
        elif target_goal.lower() == 'intermediate':
            return self._generate_intermediate_path(user_level, solved_problems, duration_days)
        elif target_goal.lower() == 'advanced':
            return self._generate_advanced_path(user_level, solved_problems, duration_days)
        else:
            return self._generate_custom_path(target_goal, weak_tags, solved_problems, duration_days)

    def _generate_basic_path(self, user_level: int, solved_problems: set,
                           duration_days: int) -> List[AlgorithmProblem]:
        """기초 학습 경로 생성"""
        problems_per_day = max(1, 30 // duration_days)  # 하루에 풀 문제 수
        total_problems = problems_per_day * duration_days

        # 쉬운 문제들로 구성
        all_problems = self.problem_provider.get_all_problems()
        easy_problems = [
            problem for problem in all_problems
            if problem.difficulty == ProblemDifficulty.EASY and
            problem.problem_id not in solved_problems
        ]

        # 기본 알고리즘 순서로 정렬
        basic_order = ['ARRAY', 'MATH', 'STRING', 'BRUTE_FORCE']
        sorted_problems = []

        for tag in basic_order:
            tag_problems = [p for p in easy_problems if tag in p.tags]
            sorted_problems.extend(tag_problems)

        return sorted_problems[:total_problems]

    def _generate_intermediate_path(self, user_level: int, solved_problems: set,
                                  duration_days: int) -> List[AlgorithmProblem]:
        """중급 학습 경로 생성"""
        problems_per_day = max(1, 30 // duration_days)
        total_problems = problems_per_day * duration_days

        all_problems = self.problem_provider.get_all_problems()
        medium_problems = [
            problem for problem in all_problems
            if problem.difficulty == ProblemDifficulty.MEDIUM and
            problem.problem_id not in solved_problems
        ]

        # 중급 알고리즘 순서로 정렬
        intermediate_order = ['BINARY_SEARCH', 'TWO_POINTERS', 'SLIDING_WINDOW', 'STACK', 'QUEUE']
        sorted_problems = []

        for tag in intermediate_order:
            tag_problems = [p for p in medium_problems if tag in p.tags]
            sorted_problems.extend(tag_problems)

        return sorted_problems[:total_problems]

    def _generate_advanced_path(self, user_level: int, solved_problems: set,
                              duration_days: int) -> List[AlgorithmProblem]:
        """고급 학습 경로 생성"""
        problems_per_day = max(1, 20 // duration_days)  # 고급은 더 적게
        total_problems = problems_per_day * duration_days

        all_problems = self.problem_provider.get_all_problems()
        hard_problems = [
            problem for problem in all_problems
            if problem.difficulty in [ProblemDifficulty.HARD, ProblemDifficulty.EXPERT] and
            problem.problem_id not in solved_problems
        ]

        # 고급 알고리즘 순서로 정렬
        advanced_order = ['DYNAMIC_PROGRAMMING', 'GRAPH', 'TREE', 'BACKTRACKING', 'GREEDY']
        sorted_problems = []

        for tag in advanced_order:
            tag_problems = [p for p in hard_problems if tag in p.tags]
            sorted_problems.extend(tag_problems)

        return sorted_problems[:total_problems]

    def _generate_custom_path(self, target_goal: str, weak_tags: List[Tuple[str, int]],
                            solved_problems: set, duration_days: int) -> List[AlgorithmProblem]:
        """커스텀 학습 경로 생성"""
        problems_per_day = max(1, 25 // duration_days)
        total_problems = problems_per_day * duration_days

        all_problems = self.problem_provider.get_all_problems()
        target_problems = []

        # 약점 태그 기반으로 문제 선택
        for tag, _ in weak_tags:
            tag_problems = [
                problem for problem in all_problems
                if tag in problem.tags and problem.problem_id not in solved_problems
            ]
            target_problems.extend(tag_problems)

        # 난이도 순으로 정렬
        target_problems.sort(key=lambda p: p.difficulty.value)

        return target_problems[:total_problems]
```

---

## 📈 성능 분석 및 통계 시스템

### **1단계: 통계 데이터 수집**

#### **통계 수집 및 분석**

```python
def get_user_statistics(self) -> Dict[str, Any]:
    """사용자 통계 반환"""
    achievement = self.achievement

    # 기본 통계
    stats = {
        'total_problems_solved': achievement.total_problems_solved,
        'total_submissions': achievement.total_submissions,
        'success_rate': achievement.calculate_success_rate(),
        'current_streak': achievement.current_streak,
        'longest_streak': achievement.longest_streak,
        'user_level': achievement.calculate_difficulty_level(),
        'average_attempts': achievement.average_attempts_per_problem,
        'average_solve_time': achievement.average_solve_time
    }

    # 난이도별 통계
    difficulty_stats = {
        'easy': achievement.easy_solved,
        'medium': achievement.medium_solved,
        'hard': achievement.hard_solved,
        'expert': achievement.expert_solved
    }
    stats['difficulty_stats'] = difficulty_stats

    # 태그별 통계
    stats['tag_achievements'] = achievement.tag_achievements

    # 최근 활동
    recent_submissions = self.get_recent_submissions(7)
    stats['recent_activity'] = {
        'submissions_last_7_days': len(recent_submissions),
        'solved_last_7_days': sum(1 for s in recent_submissions if s.status == SubmissionStatus.CORRECT)
    }

    return stats

def get_recent_submissions(self, days: int = 7) -> List[ProblemSubmission]:
    """최근 제출 기록 반환"""
    cutoff_date = datetime.now() - timedelta(days=days)
    return [
        submission for submission in self.submissions
        if submission.submission_time >= cutoff_date
    ]

def get_solved_problems(self) -> List[str]:
    """해결한 문제 목록 반환"""
    solved_ids = set()
    for submission in self.submissions:
        if submission.status == SubmissionStatus.CORRECT:
            solved_ids.add(submission.problem_id)
    return list(solved_ids)

def get_attempted_problems(self) -> List[str]:
    """시도한 문제 목록 반환"""
    return list(set(submission.problem_id for submission in self.submissions))
```

### **2단계: 학습 경로 관리**

#### **학습 경로 생성 및 관리**

```python
def create_learning_path(self, name: str, description: str,
                       target_difficulty: ProblemDifficulty,
                       estimated_days: int) -> LearningPath:
    """학습 경로 생성"""
    path_id = f"path_{len(self.learning_paths) + 1}_{int(time.time())}"

    path = LearningPath(
        path_id=path_id,
        name=name,
        description=description,
        target_difficulty=target_difficulty,
        estimated_duration_days=estimated_days,
        start_date=datetime.now()
    )

    self.learning_paths.append(path)
    self._save_user_data()

    return path

def complete_problem_in_path(self, path_id: str, problem_id: str):
    """학습 경로에서 문제 완료"""
    for path in self.learning_paths:
        if path.path_id == path_id and path.is_active:
            if problem_id in path.problems and problem_id not in path.completed_problems:
                path.completed_problems.append(problem_id)

                # 모든 문제 완료 시 경로 완료
                if len(path.completed_problems) == len(path.problems):
                    path.completion_date = datetime.now()
                    path.is_active = False

                self._save_user_data()
                break

def get_active_learning_paths(self) -> List[LearningPath]:
    """활성 학습 경로 반환"""
    return [path for path in self.learning_paths if path.is_active]

def get_statistics(self) -> Dict[str, Any]:
    """전체 통계 반환"""
    return {
        'user_achievement': self.achievement.to_dict(),
        'learning_paths': [path.to_dict() for path in self.learning_paths],
        'recent_submissions': [submission.to_dict() for submission in self.submissions[-10:]]
    }
```

---

## 🎯 핵심 기술적 성과

### **1. 알고리즘 시스템 통합**

- ✅ **SafeImporter**: 앱 번들 내 안전한 모듈 import
- ✅ **AlgorithmTab**: GUI에 완전히 통합된 알고리즘 탭
- ✅ **MockProblemProvider**: 테스트용 문제 제공 시스템

### **2. 고급 챌린지 시스템**

- ✅ **Challenge**: 다양한 유형의 챌린지 지원
- ✅ **CodeValidator**: 다중 언어 코드 검증
- ✅ **PerformanceAnalyzer**: 성능 분석 및 복잡도 추정

### **3. 사용자 진행도 추적**

- ✅ **UserProgressTracker**: 상세한 진행도 추적
- ✅ **UserAchievement**: 성취도 및 통계 관리
- ✅ **ProblemSubmission**: 제출 기록 및 분석

### **4. 개인화된 학습 경로**

- ✅ **LearningPathGenerator**: 개인화된 학습 경로 생성
- ✅ **UserBasedRecommender**: 사용자 기반 문제 추천
- ✅ **ProgressiveDifficultyManager**: 점진적 난이도 조정

### **5. 성능 분석 및 통계**

- ✅ **실시간 통계**: 사용자 활동 실시간 추적
- ✅ **성과 분석**: 문제 풀이 성과 상세 분석
- ✅ **학습 경로 관리**: 개인화된 학습 계획 관리

---

## 💡 개발 과정에서의 교훈

### **1. GUI 통합의 복잡성**

- **SafeImporter 시스템**: 앱 번들 내 모듈 import의 어려움
- **tkinter 통합**: 기존 GUI와의 원활한 통합
- **실시간 업데이트**: GUI와 백엔드 시스템의 동기화

### **2. 알고리즘 시스템 설계**

- **확장성**: 다양한 문제 유형과 난이도 지원
- **개인화**: 사용자별 맞춤형 추천 시스템
- **성능**: 코드 실행 및 검증의 안정성

### **3. 데이터 관리의 중요성**

- **진행도 추적**: 사용자 학습 과정의 상세한 기록
- **통계 분석**: 의미 있는 인사이트 도출
- **학습 경로**: 체계적인 학습 계획 수립

---

## 🎯 결론 및 다음 편 예고

알고리즘 시스템을 FocusTimer GUI에 완전히 통합하여, 사용자들이 집중 시간 동안 구체적이고 측정 가능한 학습을 할 수 있는 완전한 시스템을 구축했습니다. 이번 개발 과정에서:

- **GUI 통합**: SafeImporter를 통한 안전한 모듈 통합
- **고급 챌린지**: 다양한 유형의 알고리즘 챌린지 시스템
- **진행도 추적**: 상세한 사용자 학습 과정 추적
- **개인화**: 사용자 기반 맞춤형 문제 추천
- **성능 분석**: 코드 품질 및 성능 측정

이제 FocusTimer는 단순한 타이머를 넘어서 완전한 알고리즘 학습 플랫폼이 되었습니다! 🚀

---

## 📚 다음 편 예고

### **Part 4: 성능 최적화 및 확장성**

- **메모리 최적화**: 대용량 데이터 처리 최적화
- **데이터베이스 최적화**: SQLite 성능 튜닝
- **백그라운드 작업**: 비동기 작업 처리 시스템
- **크로스 플랫폼**: Windows, Linux 지원 확장
- **모바일 연동**: iOS, Android 앱 개발

### **Part 5: AI 통합 및 미래 계획**

- **머신러닝**: 사용 패턴 학습 및 예측
- **개인화**: AI 기반 개인화된 추천 시스템
- **자동화**: AI 기반 자동 최적화
- **클라우드 서비스**: SaaS 모델로의 확장

---

**#FocusTimer #알고리즘 #GUI통합 #SafeImporter #챌린지시스템 #진행도추적 #개인화추천 #성능분석**
