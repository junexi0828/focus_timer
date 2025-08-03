"""
사용자 성취도 추적 및 학습 진도 관리 시스템

이 모듈은 사용자의 알고리즘 문제 풀이 성취도를 추적하고,
개인화된 문제 추천 및 학습 경로를 생성하는 기능을 제공합니다.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import statistics
import math

try:
    from .problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
except ImportError:
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProblemSubmission':
        """딕셔너리로부터 객체 생성"""
        return cls(
            problem_id=data['problem_id'],
            submission_time=datetime.fromisoformat(data['submission_time']),
            status=SubmissionStatus[data['status']],
            execution_time=data.get('execution_time'),
            memory_used=data.get('memory_used'),
            code_language=data.get('code_language'),
            code_length=data.get('code_length'),
            attempt_count=data.get('attempt_count', 1),
            notes=data.get('notes', '')
        )


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

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_problems_solved': self.total_problems_solved,
            'total_submissions': self.total_submissions,
            'correct_submissions': self.correct_submissions,
            'average_attempts_per_problem': self.average_attempts_per_problem,
            'average_solve_time': self.average_solve_time,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_solved_date': self.last_solved_date.isoformat() if self.last_solved_date else None,
            'easy_solved': self.easy_solved,
            'medium_solved': self.medium_solved,
            'hard_solved': self.hard_solved,
            'expert_solved': self.expert_solved,
            'tag_achievements': self.tag_achievements
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAchievement':
        """딕셔너리로부터 객체 생성"""
        return cls(
            total_problems_solved=data.get('total_problems_solved', 0),
            total_submissions=data.get('total_submissions', 0),
            correct_submissions=data.get('correct_submissions', 0),
            average_attempts_per_problem=data.get('average_attempts_per_problem', 0.0),
            average_solve_time=data.get('average_solve_time', 0.0),
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            last_solved_date=datetime.fromisoformat(data['last_solved_date']) if data.get('last_solved_date') else None,
            easy_solved=data.get('easy_solved', 0),
            medium_solved=data.get('medium_solved', 0),
            hard_solved=data.get('hard_solved', 0),
            expert_solved=data.get('expert_solved', 0),
            tag_achievements=data.get('tag_achievements', {})
        )


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningPath':
        """딕셔너리로부터 객체 생성"""
        return cls(
            path_id=data['path_id'],
            name=data['name'],
            description=data['description'],
            target_difficulty=ProblemDifficulty[data['target_difficulty']],
            estimated_duration_days=data['estimated_duration_days'],
            problems=data.get('problems', []),
            completed_problems=data.get('completed_problems', []),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
            is_active=data.get('is_active', True)
        )


class UserProgressTracker:
    """사용자 진도 추적 시스템"""

    def __init__(self, user_id: str, data_dir: str = "user_data"):
        self.user_id = user_id
        self.data_dir = data_dir
        self.user_data_file = os.path.join(data_dir, f"{user_id}_progress.json")

        # 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)

        # 사용자 데이터 로드
        self.achievement = UserAchievement()
        self.submissions: List[ProblemSubmission] = []
        self.learning_paths: List[LearningPath] = []

        self._load_user_data()

    def _load_user_data(self):
        """사용자 데이터 로드"""
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.achievement = UserAchievement.from_dict(data.get('achievement', {}))
                self.submissions = [ProblemSubmission.from_dict(s) for s in data.get('submissions', [])]
                self.learning_paths = [LearningPath.from_dict(lp) for lp in data.get('learning_paths', [])]

            except Exception as e:
                print(f"사용자 데이터 로드 실패: {e}")

    def _save_user_data(self):
        """사용자 데이터 저장"""
        try:
            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'achievement': self.achievement.to_dict(),
                'submissions': [s.to_dict() for s in self.submissions],
                'learning_paths': [lp.to_dict() for lp in self.learning_paths]
            }

            with open(self.user_data_file, 'w', encoding='utf-8') as f:
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

            # 문제 해결 통계 업데이트
            problem_submissions = [s for s in self.submissions if s.problem_id == submission.problem_id]
            if len(problem_submissions) == 1:  # 처음 해결한 문제
                self.achievement.total_problems_solved += 1
                self.achievement.last_solved_date = submission.submission_time

                # 연속 해결 일수 업데이트
                self._update_streak(submission.submission_time)

        # 평균 시도 횟수 업데이트
        problem_attempts = {}
        for s in self.submissions:
            if s.problem_id not in problem_attempts:
                problem_attempts[s.problem_id] = 0
            problem_attempts[s.problem_id] += 1

        if problem_attempts:
            self.achievement.average_attempts_per_problem = statistics.mean(problem_attempts.values())

        # 평균 해결 시간 업데이트
        correct_submissions = [s for s in self.submissions if s.status == SubmissionStatus.CORRECT and s.execution_time is not None]
        if correct_submissions:
            avg_time = statistics.mean(s.execution_time for s in correct_submissions)
            self.achievement.average_solve_time = avg_time / 60  # 분 단위로 변환

    def _update_streak(self, solve_date: datetime):
        """연속 해결 일수 업데이트"""
        if not self.achievement.last_solved_date:
            self.achievement.current_streak = 1
            return

        # 마지막 해결일과의 차이 계산
        days_diff = (solve_date.date() - self.achievement.last_solved_date.date()).days

        if days_diff == 1:  # 연속 해결
            self.achievement.current_streak += 1
        elif days_diff == 0:  # 같은 날 해결
            pass  # 스트릭 유지
        else:  # 스트릭 끊김
            self.achievement.current_streak = 1

        # 최장 스트릭 업데이트
        self.achievement.longest_streak = max(
            self.achievement.longest_streak,
            self.achievement.current_streak
        )

    def update_problem_difficulty_stats(self, problem: AlgorithmProblem, solved: bool):
        """문제 난이도별 통계 업데이트"""
        if solved:
            if problem.difficulty == ProblemDifficulty.EASY:
                self.achievement.easy_solved += 1
            elif problem.difficulty == ProblemDifficulty.MEDIUM:
                self.achievement.medium_solved += 1
            elif problem.difficulty == ProblemDifficulty.HARD:
                self.achievement.hard_solved += 1
            elif problem.difficulty == ProblemDifficulty.EXPERT:
                self.achievement.expert_solved += 1

            # 태그별 성취도 업데이트
            for tag in problem.tags:
                tag_name = tag.name
                self.achievement.tag_achievements[tag_name] = self.achievement.tag_achievements.get(tag_name, 0) + 1

    def get_user_level(self) -> int:
        """사용자 레벨 반환 (1-10)"""
        return self.achievement.calculate_difficulty_level()

    def get_recommended_difficulty(self) -> ProblemDifficulty:
        """추천 난이도 반환"""
        user_level = self.get_user_level()

        # 레벨에 따른 난이도 매핑
        if user_level <= 3:
            return ProblemDifficulty.EASY
        elif user_level <= 6:
            return ProblemDifficulty.MEDIUM
        elif user_level <= 8:
            return ProblemDifficulty.HARD
        else:
            return ProblemDifficulty.EXPERT

    def get_weak_tags(self, limit: int = 5) -> List[Tuple[str, int]]:
        """약한 태그 목록 반환 (해결한 문제 수 기준)"""
        tag_counts = self.achievement.tag_achievements.copy()

        # 모든 태그에 대해 기본값 설정
        for tag in ProblemTag:
            if tag.name not in tag_counts:
                tag_counts[tag.name] = 0

        # 해결한 문제 수가 적은 순으로 정렬
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1])
        return sorted_tags[:limit]

    def get_strong_tags(self, limit: int = 5) -> List[Tuple[str, int]]:
        """강한 태그 목록 반환 (해결한 문제 수 기준)"""
        tag_counts = self.achievement.tag_achievements.copy()

        # 해결한 문제 수가 많은 순으로 정렬
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]

    def get_recent_submissions(self, days: int = 7) -> List[ProblemSubmission]:
        """최근 제출 기록 반환"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.submissions if s.submission_time >= cutoff_date]

    def get_solved_problems(self) -> List[str]:
        """해결한 문제 ID 목록 반환"""
        solved_problems = set()
        for submission in self.submissions:
            if submission.status == SubmissionStatus.CORRECT:
                solved_problems.add(submission.problem_id)
        return list(solved_problems)

    def get_attempted_problems(self) -> List[str]:
        """시도한 문제 ID 목록 반환"""
        return list(set(s.problem_id for s in self.submissions))

    def create_learning_path(self, name: str, description: str,
                           target_difficulty: ProblemDifficulty,
                           estimated_days: int) -> LearningPath:
        """학습 경로 생성"""
        import uuid

        path = LearningPath(
            path_id=str(uuid.uuid4()),
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

    def get_active_learning_paths(self) -> List[LearningPath]:
        """활성 학습 경로 반환"""
        return [path for path in self.learning_paths if path.is_active]

    def get_statistics(self) -> Dict[str, Any]:
        """사용자 통계 반환"""
        return {
            'user_level': self.get_user_level(),
            'recommended_difficulty': self.get_recommended_difficulty().name,
            'success_rate': self.achievement.calculate_success_rate(),
            'current_streak': self.achievement.current_streak,
            'longest_streak': self.achievement.longest_streak,
            'total_problems_solved': self.achievement.total_problems_solved,
            'average_solve_time': self.achievement.average_solve_time,
            'weak_tags': self.get_weak_tags(),
            'strong_tags': self.get_strong_tags(),
            'recent_activity': len(self.get_recent_submissions(7))
        }