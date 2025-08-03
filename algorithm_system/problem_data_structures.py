"""
알고리즘 문제 데이터 구조 모듈

이 모듈은 표준화된 알고리즘 문제 데이터 구조를 정의합니다.
대기업 코딩테스트 수준의 알고리즘 문제 시스템을 위한 핵심 데이터 클래스들을 포함합니다.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
import json
import uuid


class ProblemDifficulty(Enum):
    """문제 난이도 정의"""
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    EXPERT = auto()

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, difficulty_str: str) -> 'ProblemDifficulty':
        """문자열로부터 난이도 객체 생성"""
        try:
            return cls[difficulty_str.upper()]
        except KeyError:
            return cls.MEDIUM  # 기본값

    def get_numeric_value(self) -> int:
        """난이도를 숫자 값으로 변환 (1-4)"""
        return {
            ProblemDifficulty.EASY: 1,
            ProblemDifficulty.MEDIUM: 2,
            ProblemDifficulty.HARD: 3,
            ProblemDifficulty.EXPERT: 4
        }[self]


class ProblemPlatform(Enum):
    """문제 플랫폼 정의"""
    CODEFORCES = auto()
    LEETCODE = auto()
    KAGGLE = auto()
    BOJ = auto()  # 백준 온라인 저지
    ATCODER = auto()
    HACKERRANK = auto()
    LOCAL = auto()  # 로컬 문제

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, platform_str: str) -> 'ProblemPlatform':
        """문자열로부터 플랫폼 객체 생성"""
        try:
            return cls[platform_str.upper()]
        except KeyError:
            return cls.LOCAL  # 기본값


class ProblemTag(Enum):
    """알고리즘 문제 태그 정의"""
    # 기본 알고리즘
    BRUTE_FORCE = auto()
    GREEDY = auto()
    DYNAMIC_PROGRAMMING = auto()
    DIVIDE_AND_CONQUER = auto()
    BACKTRACKING = auto()

    # 자료구조
    ARRAY = auto()
    STRING = auto()
    LINKED_LIST = auto()
    STACK = auto()
    QUEUE = auto()
    HEAP = auto()
    TREE = auto()
    GRAPH = auto()
    HASH_TABLE = auto()
    TRIE = auto()

    # 그래프 알고리즘
    DFS = auto()
    BFS = auto()
    DIJKSTRA = auto()
    FLOYD_WARSHALL = auto()
    BELLMAN_FORD = auto()
    KRUSKAL = auto()
    PRIM = auto()
    TOPOLOGICAL_SORT = auto()

    # 수학
    MATH = auto()
    NUMBER_THEORY = auto()
    COMBINATORICS = auto()
    GEOMETRY = auto()

    # 기타
    BINARY_SEARCH = auto()
    TWO_POINTERS = auto()
    SLIDING_WINDOW = auto()
    SORTING = auto()
    BIT_MANIPULATION = auto()
    UNION_FIND = auto()
    SEGMENT_TREE = auto()
    BINARY_INDEXED_TREE = auto()

    def __str__(self):
        return self.name.replace('_', ' ').title()

    @classmethod
    def from_string(cls, tag_str: str) -> Optional['ProblemTag']:
        """문자열로부터 태그 객체 생성"""
        try:
            return cls[tag_str.upper()]
        except KeyError:
            return None


@dataclass
class ProblemMetadata:
    """문제 메타데이터"""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    solved_count: int = 0
    submission_count: int = 0
    success_rate: float = 0.0
    average_solve_time: Optional[float] = None  # 분 단위
    tags: Set[ProblemTag] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'solved_count': self.solved_count,
            'submission_count': self.submission_count,
            'success_rate': self.success_rate,
            'average_solve_time': self.average_solve_time,
            'tags': [tag.name for tag in self.tags]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProblemMetadata':
        """딕셔너리로부터 객체 생성"""
        return cls(
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            solved_count=data.get('solved_count', 0),
            submission_count=data.get('submission_count', 0),
            success_rate=data.get('success_rate', 0.0),
            average_solve_time=data.get('average_solve_time'),
            tags={tag for tag in (ProblemTag.from_string(t) for t in data.get('tags', [])) if tag is not None}
        )


@dataclass
class ProblemTestCase:
    """문제 테스트 케이스"""
    input_data: str
    expected_output: str
    description: Optional[str] = None
    is_hidden: bool = False
    time_limit: Optional[float] = None  # 초 단위
    memory_limit: Optional[int] = None  # MB 단위

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'description': self.description,
            'is_hidden': self.is_hidden,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProblemTestCase':
        """딕셔너리로부터 객체 생성"""
        return cls(
            input_data=data['input_data'],
            expected_output=data['expected_output'],
            description=data.get('description'),
            is_hidden=data.get('is_hidden', False),
            time_limit=data.get('time_limit'),
            memory_limit=data.get('memory_limit')
        )


@dataclass
class AlgorithmProblem:
    """표준화된 알고리즘 문제 데이터 구조"""

    # 기본 정보
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    difficulty: ProblemDifficulty = ProblemDifficulty.MEDIUM
    platform: ProblemPlatform = ProblemPlatform.LOCAL

    # 플랫폼별 식별자
    platform_problem_id: Optional[str] = None  # 플랫폼에서의 문제 ID
    platform_url: Optional[str] = None  # 플랫폼 문제 URL

    # 제약 조건
    time_limit: Optional[float] = None  # 초 단위
    memory_limit: Optional[int] = None  # MB 단위

    # 문제 내용
    problem_statement: str = ""
    input_format: str = ""
    output_format: str = ""
    constraints: str = ""
    examples: List[Dict[str, str]] = field(default_factory=list)

    # 테스트 케이스
    test_cases: List[ProblemTestCase] = field(default_factory=list)

    # 메타데이터
    metadata: ProblemMetadata = field(default_factory=ProblemMetadata)

    # 추가 정보
    tags: Set[ProblemTag] = field(default_factory=set)
    notes: str = ""
    is_active: bool = True

    def __post_init__(self):
        """초기화 후 처리"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.metadata:
            self.metadata = ProblemMetadata()

    def add_tag(self, tag: ProblemTag):
        """태그 추가"""
        self.tags.add(tag)
        self.metadata.tags.add(tag)

    def remove_tag(self, tag: ProblemTag):
        """태그 제거"""
        self.tags.discard(tag)
        self.metadata.tags.discard(tag)

    def add_test_case(self, test_case: ProblemTestCase):
        """테스트 케이스 추가"""
        self.test_cases.append(test_case)

    def get_difficulty_score(self) -> int:
        """난이도 점수 반환 (1-4)"""
        return self.difficulty.get_numeric_value()

    def is_suitable_for_user(self, user_level: int) -> bool:
        """사용자 레벨에 적합한 문제인지 확인"""
        problem_level = self.get_difficulty_score()
        return abs(problem_level - user_level) <= 1

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 직렬화 가능)"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty.name,
            'platform': self.platform.name,
            'platform_problem_id': self.platform_problem_id,
            'platform_url': self.platform_url,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'problem_statement': self.problem_statement,
            'input_format': self.input_format,
            'output_format': self.output_format,
            'constraints': self.constraints,
            'examples': self.examples,
            'test_cases': [tc.to_dict() for tc in self.test_cases],
            'metadata': self.metadata.to_dict(),
            'tags': [tag.name for tag in self.tags],
            'notes': self.notes,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlgorithmProblem':
        """딕셔너리로부터 객체 생성"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', ''),
            description=data.get('description', ''),
            difficulty=ProblemDifficulty.from_string(data.get('difficulty', 'MEDIUM')),
            platform=ProblemPlatform.from_string(data.get('platform', 'LOCAL')),
            platform_problem_id=data.get('platform_problem_id'),
            platform_url=data.get('platform_url'),
            time_limit=data.get('time_limit'),
            memory_limit=data.get('memory_limit'),
            problem_statement=data.get('problem_statement', ''),
            input_format=data.get('input_format', ''),
            output_format=data.get('output_format', ''),
            constraints=data.get('constraints', ''),
            examples=data.get('examples', []),
            test_cases=[ProblemTestCase.from_dict(tc) for tc in data.get('test_cases', [])],
            metadata=ProblemMetadata.from_dict(data.get('metadata', {})),
            tags={tag for tag in (ProblemTag.from_string(t) for t in data.get('tags', [])) if tag is not None},
            notes=data.get('notes', ''),
            is_active=data.get('is_active', True)
        )

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AlgorithmProblem':
        """JSON 문자열로부터 객체 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """문자열 표현"""
        return f"[{self.platform.name}] {self.title} ({self.difficulty.name})"

    def __repr__(self) -> str:
        """표현식"""
        return f"AlgorithmProblem(id='{self.id}', title='{self.title}', difficulty={self.difficulty})"


class ProblemCollection:
    """문제 컬렉션 관리 클래스"""

    def __init__(self, name: str = "Default Collection"):
        self.name = name
        self.problems: Dict[str, AlgorithmProblem] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_problem(self, problem: AlgorithmProblem) -> bool:
        """문제 추가"""
        if problem.id in self.problems:
            return False
        self.problems[problem.id] = problem
        self.updated_at = datetime.now()
        return True

    def remove_problem(self, problem_id: str) -> bool:
        """문제 제거"""
        if problem_id in self.problems:
            del self.problems[problem_id]
            self.updated_at = datetime.now()
            return True
        return False

    def get_problem(self, problem_id: str) -> Optional[AlgorithmProblem]:
        """문제 조회"""
        return self.problems.get(problem_id)

    def get_problems_by_difficulty(self, difficulty: ProblemDifficulty) -> List[AlgorithmProblem]:
        """난이도별 문제 조회"""
        return [p for p in self.problems.values() if p.difficulty == difficulty]

    def get_problems_by_platform(self, platform: ProblemPlatform) -> List[AlgorithmProblem]:
        """플랫폼별 문제 조회"""
        return [p for p in self.problems.values() if p.platform == platform]

    def get_problems_by_tag(self, tag: ProblemTag) -> List[AlgorithmProblem]:
        """태그별 문제 조회"""
        return [p for p in self.problems.values() if tag in p.tags]

    def get_all_problems(self) -> List[AlgorithmProblem]:
        """모든 문제 조회"""
        return list(self.problems.values())

    def get_problem_count(self) -> int:
        """문제 개수 반환"""
        return len(self.problems)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'problems': {pid: problem.to_dict() for pid, problem in self.problems.items()},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProblemCollection':
        """딕셔너리로부터 객체 생성"""
        collection = cls(data.get('name', 'Default Collection'))
        collection.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        collection.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))

        for pid, problem_data in data.get('problems', {}).items():
            problem = AlgorithmProblem.from_dict(problem_data)
            collection.problems[pid] = problem

        return collection

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'ProblemCollection':
        """JSON 문자열로부터 객체 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)