"""
알고리즘 시스템 패키지

대기업 코딩테스트 수준의 알고리즘 문제 시스템을 위한 표준화된 데이터 구조와 관리 시스템
"""

from .problem_data_structures import (
    AlgorithmProblem,
    ProblemDifficulty,
    ProblemPlatform,
    ProblemTag,
    ProblemTestCase,
    ProblemMetadata,
    ProblemCollection
)

from .remote_problem_provider import (
    RemoteProblemProvider,
    CodeforcesProvider,
    LeetCodeProvider,
    KaggleProvider,
    RemoteProblemManager
)

__version__ = "1.0.0"
__author__ = "Focus Timer Team"

__all__ = [
    "AlgorithmProblem",
    "ProblemDifficulty",
    "ProblemPlatform",
    "ProblemTag",
    "ProblemTestCase",
    "ProblemMetadata",
    "ProblemCollection",
    "RemoteProblemProvider",
    "CodeforcesProvider",
    "LeetCodeProvider",
    "KaggleProvider",
    "RemoteProblemManager"
]