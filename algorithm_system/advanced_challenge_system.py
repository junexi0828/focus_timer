"""
고급 알고리즘 챌린지 시스템

이 모듈은 사용자의 알고리즘 문제 풀이 능력을 향상시키기 위한
고급 기능들을 제공합니다:
- 난이도별 문제 선별 로직
- 사용자 성취도 기반 문제 추천
- 점진적 난이도 상승 알고리즘
- 문제 풀이 검증 시스템
- 코드 실행 및 테스트
- 성능 측정 및 분석
- 학습 경로 생성
- 개인화된 학습 계획
- 진도 추적 및 통계
"""

import json
import os
import time
import subprocess
import tempfile
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import statistics
import math
import random
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError

try:
    from .problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
    from .user_progress_tracker import UserProgressTracker, ProblemSubmission, SubmissionStatus
except ImportError:
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
    from user_progress_tracker import UserProgressTracker, ProblemSubmission, SubmissionStatus


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

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'challenge_id': self.challenge_id,
            'name': self.name,
            'description': self.description,
            'challenge_type': self.challenge_type.name,
            'target_difficulty': self.target_difficulty.name,
            'target_problems': self.target_problems,
            'time_limit_days': self.time_limit_days,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'problems': self.problems,
            'completed_problems': self.completed_problems,
            'status': self.status.name,
            'reward_points': self.reward_points,
            'bonus_conditions': self.bonus_conditions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Challenge':
        """딕셔너리로부터 객체 생성"""
        return cls(
            challenge_id=data['challenge_id'],
            name=data['name'],
            description=data['description'],
            challenge_type=ChallengeType[data['challenge_type']],
            target_difficulty=ProblemDifficulty[data['target_difficulty']],
            target_problems=data['target_problems'],
            time_limit_days=data['time_limit_days'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            problems=data.get('problems', []),
            completed_problems=data.get('completed_problems', []),
            status=ChallengeStatus[data['status']],
            reward_points=data.get('reward_points', 0),
            bonus_conditions=data.get('bonus_conditions', {})
        )


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

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_test_cases': self.total_test_cases,
            'passed_test_cases': self.passed_test_cases,
            'failed_test_cases': self.failed_test_cases,
            'success_rate': self.calculate_success_rate(),
            'average_execution_time': self.average_execution_time,
            'max_execution_time': self.max_execution_time,
            'min_execution_time': self.min_execution_time,
            'average_memory_used': self.average_memory_used,
            'max_memory_used': self.max_memory_used,
            'time_complexity_estimate': self.time_complexity_estimate,
            'space_complexity_estimate': self.space_complexity_estimate,
            'code_quality_score': self.code_quality_score
        }


class ProblemDifficultySelector:
    """난이도별 문제 선별 로직"""

    def __init__(self, problem_provider):
        self.problem_provider = problem_provider

    def select_problems_by_difficulty(self, difficulty: ProblemDifficulty,
                                    count: int = 10,
                                    exclude_solved: Optional[List[str]] = None) -> List[AlgorithmProblem]:
        """난이도별 문제 선별"""
        if exclude_solved is None:
            exclude_solved = []

        all_problems = self.problem_provider.get_all_problems()
        filtered_problems = [
            p for p in all_problems
            if p.difficulty == difficulty and p.id not in exclude_solved
        ]

        # 문제 품질 점수 계산 및 정렬
        scored_problems = []
        for problem in filtered_problems:
            score = self._calculate_problem_quality_score(problem)
            scored_problems.append((problem, score))

        # 점수 순으로 정렬
        scored_problems.sort(key=lambda x: x[1], reverse=True)

        # 상위 문제들 중에서 랜덤 선택
        top_problems = scored_problems[:min(count * 2, len(scored_problems))]
        selected_problems = random.sample(top_problems, min(count, len(top_problems)))

        return [p[0] for p in selected_problems]

    def _calculate_problem_quality_score(self, problem: AlgorithmProblem) -> float:
        """문제 품질 점수 계산"""
        score = 0.0

        # 난이도 가중치
        difficulty_weights = {
            ProblemDifficulty.EASY: 1.0,
            ProblemDifficulty.MEDIUM: 1.5,
            ProblemDifficulty.HARD: 2.0,
            ProblemDifficulty.EXPERT: 2.5
        }
        score += difficulty_weights.get(problem.difficulty, 1.0)

        # 태그 다양성 보너스
        unique_tags = len(set(tag.name for tag in problem.tags))
        score += unique_tags * 0.1

        # 제목 길이 적절성 (너무 짧거나 긴 제목은 감점)
        title_length = len(problem.title)
        if 10 <= title_length <= 50:
            score += 0.5
        elif title_length < 5 or title_length > 100:
            score -= 0.5

        return score


class UserBasedRecommender:
    """사용자 성취도 기반 문제 추천"""

    def __init__(self, progress_tracker: UserProgressTracker, problem_provider):
        self.progress_tracker = progress_tracker
        self.problem_provider = problem_provider

    def get_personalized_recommendations(self, count: int = 5) -> List[AlgorithmProblem]:
        """개인화된 문제 추천"""
        user_level = self.progress_tracker.get_user_level()
        solved_problems = set(self.progress_tracker.get_solved_problems())
        weak_tags = self.progress_tracker.get_weak_tags(3)
        strong_tags = self.progress_tracker.get_strong_tags(3)

        recommendations = []

        # 1. 약한 태그 기반 추천 (40%)
        weak_tag_count = max(1, count // 3)
        weak_tag_problems = self._get_problems_by_tags(
            [tag[0] for tag in weak_tags],
            weak_tag_count,
            solved_problems,
            user_level
        )
        recommendations.extend(weak_tag_problems)

        # 2. 현재 레벨에 적합한 문제 (30%)
        current_level_count = max(1, count // 3)
        current_level_problems = self._get_problems_by_difficulty(
            self.progress_tracker.get_recommended_difficulty(),
            current_level_count,
            solved_problems
        )
        recommendations.extend(current_level_problems)

        # 3. 다음 레벨 준비 문제 (20%)
        next_level_count = max(1, count // 5)
        next_level_problems = self._get_next_level_problems(
            next_level_count,
            solved_problems,
            user_level
        )
        recommendations.extend(next_level_problems)

        # 4. 강한 태그 심화 문제 (10%)
        strong_tag_count = max(1, count // 10)
        strong_tag_problems = self._get_advanced_problems_by_tags(
            [tag[0] for tag in strong_tags],
            strong_tag_count,
            solved_problems
        )
        recommendations.extend(strong_tag_problems)

        # 중복 제거 및 개수 조정
        unique_recommendations = []
        seen_ids = set()
        for problem in recommendations:
            if problem.id not in seen_ids and len(unique_recommendations) < count:
                unique_recommendations.append(problem)
                seen_ids.add(problem.id)

        return unique_recommendations

    def _get_problems_by_tags(self, tags: List[str], count: int,
                             exclude_problems: set, user_level: int) -> List[AlgorithmProblem]:
        """태그 기반 문제 추천"""
        all_problems = self.problem_provider.get_all_problems()
        tagged_problems = []

        for problem in all_problems:
            if problem.id in exclude_problems:
                continue

            problem_tags = {tag.name for tag in problem.tags}
            if any(tag in problem_tags for tag in tags):
                # 사용자 레벨에 맞는 난이도 필터링
                difficulty_score = self._get_difficulty_score(problem.difficulty)
                if abs(difficulty_score - user_level) <= 2:  # 레벨 차이가 2 이하
                    tagged_problems.append(problem)

        return random.sample(tagged_problems, min(count, len(tagged_problems)))

    def _get_problems_by_difficulty(self, difficulty: ProblemDifficulty,
                                   count: int, exclude_problems: set) -> List[AlgorithmProblem]:
        """난이도 기반 문제 추천"""
        all_problems = self.problem_provider.get_all_problems()
        filtered_problems = [
            p for p in all_problems
            if p.difficulty == difficulty and p.id not in exclude_problems
        ]
        return random.sample(filtered_problems, min(count, len(filtered_problems)))

    def _get_next_level_problems(self, count: int, exclude_problems: set,
                                user_level: int) -> List[AlgorithmProblem]:
        """다음 레벨 준비 문제 추천"""
        all_problems = self.problem_provider.get_all_problems()
        next_level_problems = []

        for problem in all_problems:
            if problem.id in exclude_problems:
                continue

            difficulty_score = self._get_difficulty_score(problem.difficulty)
            if user_level + 1 <= difficulty_score <= user_level + 2:
                next_level_problems.append(problem)

        return random.sample(next_level_problems, min(count, len(next_level_problems)))

    def _get_advanced_problems_by_tags(self, tags: List[str], count: int,
                                      exclude_problems: set) -> List[AlgorithmProblem]:
        """강한 태그 심화 문제 추천"""
        all_problems = self.problem_provider.get_all_problems()
        advanced_problems = []

        for problem in all_problems:
            if problem.id in exclude_problems:
                continue

            problem_tags = {tag.name for tag in problem.tags}
            if any(tag in problem_tags for tag in tags):
                # 어려운 난이도만 선택
                if problem.difficulty in [ProblemDifficulty.HARD, ProblemDifficulty.EXPERT]:
                    advanced_problems.append(problem)

        return random.sample(advanced_problems, min(count, len(advanced_problems)))

    def _get_difficulty_score(self, difficulty: ProblemDifficulty) -> int:
        """난이도를 점수로 변환"""
        difficulty_scores = {
            ProblemDifficulty.EASY: 1,
            ProblemDifficulty.MEDIUM: 3,
            ProblemDifficulty.HARD: 6,
            ProblemDifficulty.EXPERT: 9
        }
        return difficulty_scores.get(difficulty, 1)


class ProgressiveDifficultyManager:
    """점진적 난이도 상승 알고리즘"""

    def __init__(self, progress_tracker: UserProgressTracker):
        self.progress_tracker = progress_tracker

    def calculate_next_difficulty(self) -> ProblemDifficulty:
        """다음 추천 난이도 계산"""
        user_level = self.progress_tracker.get_user_level()
        success_rate = self.progress_tracker.achievement.calculate_success_rate()
        recent_submissions = self.progress_tracker.get_recent_submissions(7)

        # 최근 성과 분석
        recent_success_rate = self._calculate_recent_success_rate(recent_submissions)
        difficulty_trend = self._analyze_difficulty_trend(recent_submissions)

        # 난이도 조정 로직
        if recent_success_rate > 0.8 and difficulty_trend >= 0:
            # 성과가 좋으면 난이도 상승
            return self._increase_difficulty(user_level)
        elif recent_success_rate < 0.4:
            # 성과가 나쁘면 난이도 하락
            return self._decrease_difficulty(user_level)
        else:
            # 현재 난이도 유지
            return self.progress_tracker.get_recommended_difficulty()

    def _calculate_recent_success_rate(self, recent_submissions: List[ProblemSubmission]) -> float:
        """최근 성공률 계산"""
        if not recent_submissions:
            return 0.0

        correct_count = sum(1 for s in recent_submissions if s.status == SubmissionStatus.CORRECT)
        return correct_count / len(recent_submissions)

    def _analyze_difficulty_trend(self, recent_submissions: List[ProblemSubmission]) -> int:
        """난이도 트렌드 분석"""
        # 최근 제출의 난이도 변화 추이 분석
        # 실제 구현에서는 문제의 난이도 정보가 필요
        return 0  # 기본값

    def _increase_difficulty(self, current_level: int) -> ProblemDifficulty:
        """난이도 상승"""
        if current_level <= 3:
            return ProblemDifficulty.MEDIUM
        elif current_level <= 6:
            return ProblemDifficulty.HARD
        else:
            return ProblemDifficulty.EXPERT

    def _decrease_difficulty(self, current_level: int) -> ProblemDifficulty:
        """난이도 하락"""
        if current_level <= 2:
            return ProblemDifficulty.EASY
        elif current_level <= 5:
            return ProblemDifficulty.MEDIUM
        else:
            return ProblemDifficulty.HARD


class CodeValidator:
    """문제 풀이 검증 시스템"""

    def __init__(self):
        self.supported_languages = {
            'python': '.py',
            'python3': '.py',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'javascript': '.js',
            'typescript': '.ts'
        }

    def validate_code(self, code: str, language: str,
                     test_cases: List[Dict[str, str]]) -> List[CodeTestResult]:
        """코드 검증"""
        if language not in self.supported_languages:
            raise ValueError(f"지원하지 않는 언어: {language}")

        results = []

        for i, test_case in enumerate(test_cases):
            try:
                result = self._run_test_case(code, language, test_case, f"test_{i}")
                results.append(result)
            except Exception as e:
                # 테스트 실행 실패 시 에러 결과 생성
                results.append(CodeTestResult(
                    test_case_id=f"test_{i}",
                    input_data=test_case.get('input', ''),
                    expected_output=test_case.get('output', ''),
                    actual_output='',
                    is_passed=False,
                    execution_time=0.0,
                    memory_used=0,
                    error_message=str(e)
                ))

        return results

    def _run_test_case(self, code: str, language: str,
                      test_case: Dict[str, str], test_id: str) -> CodeTestResult:
        """개별 테스트 케이스 실행"""
        start_time = time.time()

        try:
            if language in ['python', 'python3']:
                return self._run_python_test(code, test_case, test_id)
            elif language == 'java':
                return self._run_java_test(code, test_case, test_id)
            elif language in ['cpp', 'c']:
                return self._run_cpp_test(code, test_case, test_id)
            else:
                raise ValueError(f"아직 구현되지 않은 언어: {language}")
        finally:
            pass

    def _run_python_test(self, code: str, test_case: Dict[str, str],
                        test_id: str) -> CodeTestResult:
        """Python 코드 테스트"""
        input_data = test_case.get('input', '')
        expected_output = test_case.get('output', '').strip()

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 코드 실행
            process = subprocess.run(
                ['python3', temp_file],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=10  # 10초 타임아웃
            )

            actual_output = process.stdout.strip()
            error_message = process.stderr.strip() if process.stderr else None

            execution_time = time.time() - time.time()  # 실제로는 더 정확한 측정 필요

            is_passed = actual_output == expected_output and process.returncode == 0

            return CodeTestResult(
                test_case_id=test_id,
                input_data=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                is_passed=is_passed,
                execution_time=execution_time,
                memory_used=0,  # 메모리 사용량 측정은 별도 구현 필요
                error_message=error_message
            )

        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def _run_java_test(self, code: str, test_case: Dict[str, str],
                      test_id: str) -> CodeTestResult:
        """Java 코드 테스트"""
        # Java 테스트 구현 (간단한 예시)
        input_data = test_case.get('input', '')
        expected_output = test_case.get('output', '').strip()

        # 임시 파일 생성
        class_name = "Solution"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 컴파일
            compile_process = subprocess.run(
                ['javac', temp_file],
                capture_output=True,
                text=True
            )

            if compile_process.returncode != 0:
                return CodeTestResult(
                    test_case_id=test_id,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output='',
                    is_passed=False,
                    execution_time=0.0,
                    memory_used=0,
                    error_message=compile_process.stderr
                )

            # 실행
            class_file = temp_file.replace('.java', '.class')
            process = subprocess.run(
                ['java', '-cp', os.path.dirname(temp_file), class_name],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=10
            )

            actual_output = process.stdout.strip()
            error_message = process.stderr.strip() if process.stderr else None

            is_passed = actual_output == expected_output and process.returncode == 0

            return CodeTestResult(
                test_case_id=test_id,
                input_data=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                is_passed=is_passed,
                execution_time=0.0,
                memory_used=0,
                error_message=error_message
            )

        finally:
            # 임시 파일들 삭제
            try:
                os.unlink(temp_file)
                if os.path.exists(class_file):
                    os.unlink(class_file)
            except:
                pass

    def _run_cpp_test(self, code: str, test_case: Dict[str, str],
                     test_id: str) -> CodeTestResult:
        """C++ 코드 테스트"""
        # C++ 테스트 구현 (간단한 예시)
        input_data = test_case.get('input', '')
        expected_output = test_case.get('output', '').strip()

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(code)
            temp_file = f.name

        executable = temp_file.replace('.cpp', '')

        try:
            # 컴파일
            compile_process = subprocess.run(
                ['g++', '-o', executable, temp_file],
                capture_output=True,
                text=True
            )

            if compile_process.returncode != 0:
                return CodeTestResult(
                    test_case_id=test_id,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output='',
                    is_passed=False,
                    execution_time=0.0,
                    memory_used=0,
                    error_message=compile_process.stderr
                )

            # 실행
            process = subprocess.run(
                [executable],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=10
            )

            actual_output = process.stdout.strip()
            error_message = process.stderr.strip() if process.stderr else None

            is_passed = actual_output == expected_output and process.returncode == 0

            return CodeTestResult(
                test_case_id=test_id,
                input_data=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                is_passed=is_passed,
                execution_time=0.0,
                memory_used=0,
                error_message=error_message
            )

        finally:
            # 임시 파일들 삭제
            try:
                os.unlink(temp_file)
                if os.path.exists(executable):
                    os.unlink(executable)
            except:
                pass


class PerformanceAnalyzer:
    """성능 측정 및 분석"""

    def __init__(self):
        self.complexity_patterns = {
            'O(1)': ['constant', 'hash', 'direct'],
            'O(log n)': ['binary', 'log', 'divide'],
            'O(n)': ['linear', 'single loop', 'traverse'],
            'O(n log n)': ['sort', 'merge', 'quick'],
            'O(n²)': ['nested loop', 'quadratic', 'bubble'],
            'O(2^n)': ['exponential', 'recursive', 'backtrack'],
            'O(n!)': ['factorial', 'permutation']
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
                time_complexity_estimate='Unknown',
                space_complexity_estimate='Unknown',
                code_quality_score=0.0
            )

        # 기본 통계 계산
        total_cases = len(test_results)
        passed_cases = sum(1 for r in test_results if r.is_passed)
        failed_cases = total_cases - passed_cases

        execution_times = [r.execution_time for r in test_results if r.execution_time > 0]
        memory_usage = [r.memory_used for r in test_results if r.memory_used > 0]

        avg_execution_time = statistics.mean(execution_times) if execution_times else 0.0
        max_execution_time = max(execution_times) if execution_times else 0.0
        min_execution_time = min(execution_times) if execution_times else 0.0

        avg_memory_used = int(statistics.mean(memory_usage)) if memory_usage else 0
        max_memory_used = max(memory_usage) if memory_usage else 0

        # 복잡도 추정
        time_complexity = self._estimate_time_complexity(code, test_results)
        space_complexity = self._estimate_space_complexity(code)

        # 코드 품질 점수
        code_quality = self._calculate_code_quality_score(code, test_results)

        return PerformanceMetrics(
            total_test_cases=total_cases,
            passed_test_cases=passed_cases,
            failed_test_cases=failed_cases,
            average_execution_time=avg_execution_time,
            max_execution_time=max_execution_time,
            min_execution_time=min_execution_time,
            average_memory_used=avg_memory_used,
            max_memory_used=max_memory_used,
            time_complexity_estimate=time_complexity,
            space_complexity_estimate=space_complexity,
            code_quality_score=code_quality
        )

    def _estimate_time_complexity(self, code: str,
                                test_results: List[CodeTestResult]) -> str:
        """시간 복잡도 추정"""
        code_lower = code.lower()

        # 패턴 매칭
        for complexity, patterns in self.complexity_patterns.items():
            if any(pattern in code_lower for pattern in patterns):
                return complexity

        # 기본 추정 (코드 구조 기반)
        if 'for' in code_lower and 'for' in code_lower[code_lower.find('for')+3:]:
            return 'O(n²)'  # 중첩 루프
        elif 'for' in code_lower or 'while' in code_lower:
            return 'O(n)'   # 단일 루프
        else:
            return 'O(1)'   # 기본

    def _estimate_space_complexity(self, code: str) -> str:
        """공간 복잡도 추정"""
        code_lower = code.lower()

        # 배열/리스트 사용량 기반 추정
        array_patterns = ['list', 'array', 'vector', '[]']
        if any(pattern in code_lower for pattern in array_patterns):
            return 'O(n)'
        else:
            return 'O(1)'

    def _calculate_code_quality_score(self, code: str,
                                    test_results: List[CodeTestResult]) -> float:
        """코드 품질 점수 계산"""
        score = 0.0

        # 성공률 (40%)
        success_rate = sum(1 for r in test_results if r.is_passed) / len(test_results)
        score += success_rate * 40

        # 코드 길이 (20%)
        code_length = len(code.strip())
        if 50 <= code_length <= 500:
            score += 20
        elif code_length < 50:
            score += 20 * (code_length / 50)
        else:
            score += 20 * (500 / code_length)

        # 가독성 (20%)
        readability_score = self._calculate_readability_score(code)
        score += readability_score * 20

        # 효율성 (20%)
        efficiency_score = self._calculate_efficiency_score(test_results)
        score += efficiency_score * 20

        return min(100.0, score)

    def _calculate_readability_score(self, code: str) -> float:
        """가독성 점수 계산"""
        score = 0.0

        # 들여쓰기 일관성
        lines = code.split('\n')
        indent_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)

        if indent_levels:
            indent_variance = statistics.variance(indent_levels) if len(indent_levels) > 1 else 0
            if indent_variance < 1:
                score += 0.5

        # 주석 비율
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if len(lines) > 0:
            comment_ratio = comment_lines / len(lines)
            if 0.1 <= comment_ratio <= 0.3:
                score += 0.5

        return score

    def _calculate_efficiency_score(self, test_results: List[CodeTestResult]) -> float:
        """효율성 점수 계산"""
        if not test_results:
            return 0.0

        execution_times = [r.execution_time for r in test_results if r.execution_time > 0]
        if not execution_times:
            return 0.0

        avg_time = statistics.mean(execution_times)

        # 실행 시간이 짧을수록 높은 점수
        if avg_time < 0.001:
            return 1.0
        elif avg_time < 0.01:
            return 0.8
        elif avg_time < 0.1:
            return 0.6
        elif avg_time < 1.0:
            return 0.4
        else:
            return 0.2


class LearningPathGenerator:
    """학습 경로 생성"""

    def __init__(self, progress_tracker: UserProgressTracker, problem_provider):
        self.progress_tracker = progress_tracker
        self.problem_provider = problem_provider

    def generate_personalized_path(self, target_goal: str,
                                 duration_days: int = 30) -> List[AlgorithmProblem]:
        """개인화된 학습 경로 생성"""
        user_level = self.progress_tracker.get_user_level()
        solved_problems = set(self.progress_tracker.get_solved_problems())
        weak_tags = self.progress_tracker.get_weak_tags(5)

        # 목표별 경로 생성
        if '기초' in target_goal or '입문' in target_goal:
            return self._generate_basic_path(user_level, solved_problems, duration_days)
        elif '중급' in target_goal or '심화' in target_goal:
            return self._generate_intermediate_path(user_level, solved_problems, duration_days)
        elif '고급' in target_goal or '전문가' in target_goal:
            return self._generate_advanced_path(user_level, solved_problems, duration_days)
        else:
            return self._generate_custom_path(target_goal, weak_tags, solved_problems, duration_days)

    def _generate_basic_path(self, user_level: int, solved_problems: set,
                           duration_days: int) -> List[AlgorithmProblem]:
        """기초 학습 경로"""
        problems = []
        all_problems = self.problem_provider.get_all_problems()

        # 기초 개념 문제들
        basic_concepts = ['배열', '문자열', '수학', '구현']
        for concept in basic_concepts:
            concept_problems = [
                p for p in all_problems
                if p.id not in solved_problems and
                p.difficulty == ProblemDifficulty.EASY and
                any(concept in tag.name for tag in p.tags)
            ]
            if concept_problems:
                problems.extend(random.sample(concept_problems, min(2, len(concept_problems))))

        return problems[:min(10, len(problems))]

    def _generate_intermediate_path(self, user_level: int, solved_problems: set,
                                  duration_days: int) -> List[AlgorithmProblem]:
        """중급 학습 경로"""
        problems = []
        all_problems = self.problem_provider.get_all_problems()

        # 중급 알고리즘 문제들
        intermediate_concepts = ['정렬', '탐색', '그래프', '동적 프로그래밍']
        for concept in intermediate_concepts:
            concept_problems = [
                p for p in all_problems
                if p.id not in solved_problems and
                p.difficulty in [ProblemDifficulty.MEDIUM, ProblemDifficulty.HARD] and
                any(concept in tag.name for tag in p.tags)
            ]
            if concept_problems:
                problems.extend(random.sample(concept_problems, min(3, len(concept_problems))))

        return problems[:min(15, len(problems))]

    def _generate_advanced_path(self, user_level: int, solved_problems: set,
                              duration_days: int) -> List[AlgorithmProblem]:
        """고급 학습 경로"""
        problems = []
        all_problems = self.problem_provider.get_all_problems()

        # 고급 알고리즘 문제들
        advanced_concepts = ['최적화', '고급 자료구조', '복잡한 알고리즘']
        for concept in advanced_concepts:
            concept_problems = [
                p for p in all_problems
                if p.id not in solved_problems and
                p.difficulty in [ProblemDifficulty.HARD, ProblemDifficulty.EXPERT] and
                any(concept in tag.name for tag in p.tags)
            ]
            if concept_problems:
                problems.extend(random.sample(concept_problems, min(2, len(concept_problems))))

        return problems[:min(20, len(problems))]

    def _generate_custom_path(self, target_goal: str, weak_tags: List[Tuple[str, int]],
                            solved_problems: set, duration_days: int) -> List[AlgorithmProblem]:
        """커스텀 학습 경로"""
        problems = []
        all_problems = self.problem_provider.get_all_problems()

        # 약한 태그 기반 문제 선택
        for tag, count in weak_tags:
            tag_problems = [
                p for p in all_problems
                if p.id not in solved_problems and
                any(tag in tag_obj.name for tag_obj in p.tags)
            ]
            if tag_problems:
                problems.extend(random.sample(tag_problems, min(2, len(tag_problems))))

        return problems[:min(10, len(problems))]


class AdvancedChallengeSystem:
    """고급 알고리즘 챌린지 시스템"""

    def __init__(self, user_id: str, problem_provider, data_dir: str = "user_data"):
        self.user_id = user_id
        self.problem_provider = problem_provider
        self.data_dir = data_dir

        # 컴포넌트 초기화
        self.progress_tracker = UserProgressTracker(user_id, data_dir)
        self.difficulty_selector = ProblemDifficultySelector(problem_provider)
        self.recommender = UserBasedRecommender(self.progress_tracker, problem_provider)
        self.difficulty_manager = ProgressiveDifficultyManager(self.progress_tracker)
        self.code_validator = CodeValidator()
        self.performance_analyzer = PerformanceAnalyzer()
        self.path_generator = LearningPathGenerator(self.progress_tracker, problem_provider)

        # 챌린지 데이터
        self.challenges: List[Challenge] = []
        self._load_challenges()

    def _load_challenges(self):
        """챌린지 데이터 로드"""
        challenges_file = os.path.join(self.data_dir, f"{self.user_id}_challenges.json")
        if os.path.exists(challenges_file):
            try:
                with open(challenges_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.challenges = [Challenge.from_dict(c) for c in data]
            except Exception as e:
                print(f"챌린지 데이터 로드 실패: {e}")

    def _save_challenges(self):
        """챌린지 데이터 저장"""
        challenges_file = os.path.join(self.data_dir, f"{self.user_id}_challenges.json")
        try:
            data = [c.to_dict() for c in self.challenges]
            with open(challenges_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"챌린지 데이터 저장 실패: {e}")

    def create_daily_challenge(self) -> Challenge:
        """일일 챌린지 생성"""
        import uuid

        # 사용자 레벨에 맞는 문제 선택
        recommended_difficulty = self.progress_tracker.get_recommended_difficulty()
        problems = self.difficulty_selector.select_problems_by_difficulty(
            recommended_difficulty, 3, self.progress_tracker.get_solved_problems()
        )

        challenge = Challenge(
            challenge_id=str(uuid.uuid4()),
            name="일일 알고리즘 챌린지",
            description=f"오늘의 {recommended_difficulty.name} 난이도 문제들을 해결해보세요!",
            challenge_type=ChallengeType.DAILY,
            target_difficulty=recommended_difficulty,
            target_problems=len(problems),
            time_limit_days=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1),
            problems=[p.id for p in problems],
            reward_points=100
        )

        self.challenges.append(challenge)
        self._save_challenges()
        return challenge

    def create_weekly_challenge(self) -> Challenge:
        """주간 챌린지 생성"""
        import uuid

        # 다양한 난이도의 문제 선택
        problems = []
        difficulties = [ProblemDifficulty.EASY, ProblemDifficulty.MEDIUM, ProblemDifficulty.HARD]

        for difficulty in difficulties:
            diff_problems = self.difficulty_selector.select_problems_by_difficulty(
                difficulty, 2, self.progress_tracker.get_solved_problems()
            )
            problems.extend(diff_problems)

        challenge = Challenge(
            challenge_id=str(uuid.uuid4()),
            name="주간 알고리즘 챌린지",
            description="이번 주 다양한 난이도의 문제들을 도전해보세요!",
            challenge_type=ChallengeType.WEEKLY,
            target_difficulty=ProblemDifficulty.MEDIUM,
            target_problems=len(problems),
            time_limit_days=7,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            problems=[p.id for p in problems],
            reward_points=500
        )

        self.challenges.append(challenge)
        self._save_challenges()
        return challenge

    def get_personalized_recommendations(self, count: int = 5) -> List[AlgorithmProblem]:
        """개인화된 문제 추천"""
        return self.recommender.get_personalized_recommendations(count)

    def submit_solution(self, problem_id: str, code: str, language: str,
                       test_cases: List[Dict[str, str]]) -> Tuple[bool, List[CodeTestResult], PerformanceMetrics]:
        """솔루션 제출 및 검증"""
        # 코드 검증
        test_results = self.code_validator.validate_code(code, language, test_cases)

        # 성능 분석
        performance_metrics = self.performance_analyzer.analyze_performance(test_results, code)

        # 제출 결과 생성
        is_correct = all(result.is_passed for result in test_results)

        # 성취도 업데이트
        submission = ProblemSubmission(
            problem_id=problem_id,
            submission_time=datetime.now(),
            status=SubmissionStatus.CORRECT if is_correct else SubmissionStatus.WRONG_ANSWER,
            execution_time=performance_metrics.average_execution_time,
            memory_used=performance_metrics.average_memory_used,
            code_language=language,
            code_length=len(code),
            notes=f"성공률: {performance_metrics.calculate_success_rate():.2f}%"
        )

        self.progress_tracker.add_submission(submission)

        # 챌린지 업데이트
        if is_correct:
            self._update_challenge_progress(problem_id)

        return is_correct, test_results, performance_metrics

    def _update_challenge_progress(self, problem_id: str):
        """챌린지 진도 업데이트"""
        for challenge in self.challenges:
            if (challenge.status == ChallengeStatus.ACTIVE and
                problem_id in challenge.problems and
                problem_id not in challenge.completed_problems):

                challenge.completed_problems.append(problem_id)

                # 챌린지 완료 확인
                if len(challenge.completed_problems) == len(challenge.problems):
                    challenge.status = ChallengeStatus.COMPLETED

                self._save_challenges()
                break

    def get_active_challenges(self) -> List[Challenge]:
        """활성 챌린지 목록 반환"""
        return [c for c in self.challenges if c.status == ChallengeStatus.ACTIVE]

    def get_challenge_progress(self, challenge_id: str) -> Optional[Challenge]:
        """챌린지 진도 조회"""
        for challenge in self.challenges:
            if challenge.challenge_id == challenge_id:
                return challenge
        return None

    def create_custom_challenge(self, name: str, description: str,
                              target_difficulty: ProblemDifficulty,
                              target_problems: int, time_limit_days: int,
                              problem_ids: Optional[List[str]] = None) -> Challenge:
        """커스텀 챌린지 생성"""
        import uuid

        if problem_ids is None:
            # 자동으로 문제 선택
            problems = self.difficulty_selector.select_problems_by_difficulty(
                target_difficulty, target_problems, self.progress_tracker.get_solved_problems()
            )
            problem_ids = [p.id for p in problems]

        challenge = Challenge(
            challenge_id=str(uuid.uuid4()),
            name=name,
            description=description,
            challenge_type=ChallengeType.CUSTOM,
            target_difficulty=target_difficulty,
            target_problems=target_problems,
            time_limit_days=time_limit_days,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=time_limit_days),
            problems=problem_ids,
            reward_points=target_problems * 50
        )

        self.challenges.append(challenge)
        self._save_challenges()
        return challenge

    def generate_learning_path(self, target_goal: str, duration_days: int = 30) -> List[AlgorithmProblem]:
        """학습 경로 생성"""
        return self.path_generator.generate_personalized_path(target_goal, duration_days)

    def get_user_statistics(self) -> Dict[str, Any]:
        """사용자 통계 반환"""
        return self.progress_tracker.get_statistics()

    def get_next_recommended_difficulty(self) -> ProblemDifficulty:
        """다음 추천 난이도 반환"""
        return self.difficulty_manager.calculate_next_difficulty()

    def get_weak_areas(self, limit: int = 5) -> List[Tuple[str, int]]:
        """약점 영역 반환"""
        return self.progress_tracker.get_weak_tags(limit)

    def get_strong_areas(self, limit: int = 5) -> List[Tuple[str, int]]:
        """강점 영역 반환"""
        return self.progress_tracker.get_strong_tags(limit)

    def get_recent_activity(self, days: int = 7) -> List[ProblemSubmission]:
        """최근 활동 반환"""
        return self.progress_tracker.get_recent_submissions(days)

    def export_progress_report(self) -> Dict[str, Any]:
        """진도 보고서 내보내기"""
        stats = self.get_user_statistics()
        recent_activity = self.get_recent_activity()
        active_challenges = self.get_active_challenges()

        return {
            'user_id': self.user_id,
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'recent_activity': [s.to_dict() for s in recent_activity],
            'active_challenges': [c.to_dict() for c in active_challenges],
            'total_problems_solved': self.progress_tracker.achievement.total_problems_solved,
            'current_streak': self.progress_tracker.achievement.current_streak,
            'longest_streak': self.progress_tracker.achievement.longest_streak,
            'success_rate': self.progress_tracker.achievement.calculate_success_rate()
        }
