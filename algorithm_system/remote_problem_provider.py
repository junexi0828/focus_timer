"""
외부 플랫폼 연동 시스템

이 모듈은 외부 알고리즘 문제 플랫폼과의 연동을 담당합니다.
Codeforces, LeetCode, Kaggle 등의 플랫폼에서 문제를 가져오는 기능을 제공합니다.
"""

import requests
import json
import time
import logging
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import os
import hashlib

try:
    from .problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag,
        ProblemTestCase, ProblemMetadata
    )
except ImportError:
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag,
        ProblemTestCase, ProblemMetadata
    )


class RemoteProblemProvider(ABC):
    """외부 플랫폼 문제 제공자 추상 클래스"""

    def __init__(self, platform: ProblemPlatform, cache_dir: str = "cache"):
        self.platform = platform
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)

        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': 'FocusTimer/2.0.0 (Algorithm System)'
        })

    @abstractmethod
    def get_problems(self, limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """플랫폼에서 문제 목록을 가져옵니다."""
        pass

    @abstractmethod
    def get_problem_details(self, problem_id: str) -> Optional[AlgorithmProblem]:
        """특정 문제의 상세 정보를 가져옵니다."""
        pass

    def _get_cache_path(self, key: str) -> str:
        """캐시 파일 경로를 반환합니다."""
        cache_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{self.platform.name.lower()}_{cache_key}.json")

    def _load_from_cache(self, key: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """캐시에서 데이터를 로드합니다."""
        cache_path = self._get_cache_path(key)

        if not os.path.exists(cache_path):
            return None

        # 캐시 만료 확인
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
        if file_age > timedelta(hours=max_age_hours):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"캐시 로드 실패: {e}")
            return None

    def _save_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """데이터를 캐시에 저장합니다."""
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"캐시 저장 실패: {e}")

    def _make_request(self, url: str, params: Optional[Dict] = None,
                     headers: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """HTTP 요청을 수행합니다."""
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 실패: {e}")
            return None


class CodeforcesProvider(RemoteProblemProvider):
    """Codeforces API 연동"""

    def __init__(self, cache_dir: str = "cache"):
        super().__init__(ProblemPlatform.CODEFORCES, cache_dir)
        self.base_url = "https://codeforces.com/api"

    def get_problems(self, limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """Codeforces에서 문제 목록을 가져옵니다."""
        cache_key = f"problems_list_{limit or 'all'}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=6)

        if cached_data and isinstance(cached_data, dict):
            problems_data = cached_data.get("problems", [])
            return [AlgorithmProblem.from_dict(problem_data) for problem_data in problems_data if isinstance(problem_data, dict)]

        url = f"{self.base_url}/problemset.problems"
        data = self._make_request(url)

        if not data or data.get('status') != 'OK':
            self.logger.error("Codeforces API 응답 오류")
            return []

        problems = []
        problems_data = data.get('result', {}).get('problems', [])

        for problem_data in problems_data[:limit]:
            try:
                problem = self._convert_to_algorithm_problem(problem_data)
                if problem:
                    problems.append(problem)
            except Exception as e:
                self.logger.warning(f"문제 변환 실패: {e}")
                continue

        # 캐시에 저장
        cache_data = {"problems": [problem.to_dict() for problem in problems]}
        self._save_to_cache(cache_key, cache_data)

        return problems

    def get_problem_details(self, problem_id: str) -> Optional[AlgorithmProblem]:
        """특정 문제의 상세 정보를 가져옵니다."""
        cache_key = f"problem_details_{problem_id}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=24)

        if cached_data:
            return AlgorithmProblem.from_dict(cached_data)

        # Codeforces는 개별 문제 API가 없으므로 문제 목록에서 찾기
        problems = self.get_problems(limit=1000)  # 충분한 수의 문제 가져오기

        for problem in problems:
            if problem.platform_problem_id == problem_id:
                self._save_to_cache(cache_key, problem.to_dict())
                return problem

        return None

    def _convert_to_algorithm_problem(self, cf_problem: Dict[str, Any]) -> Optional[AlgorithmProblem]:
        """Codeforces 문제 데이터를 AlgorithmProblem으로 변환합니다."""
        try:
            # 난이도 매핑
            difficulty = self._map_difficulty(cf_problem.get('rating', 0))

            # 태그 매핑
            tags = set()
            for tag_name in cf_problem.get('tags', []):
                tag = self._map_tag(tag_name)
                if tag:
                    tags.add(tag)

            problem = AlgorithmProblem(
                title=cf_problem.get('name', ''),
                description=f"Codeforces 문제: {cf_problem.get('name', '')}",
                difficulty=difficulty,
                platform=ProblemPlatform.CODEFORCES,
                platform_problem_id=f"{cf_problem.get('contestId', '')}{cf_problem.get('index', '')}",
                platform_url=f"https://codeforces.com/problemset/problem/{cf_problem.get('contestId', '')}/{cf_problem.get('index', '')}",
                time_limit=2.0,  # Codeforces 기본값
                memory_limit=256,  # Codeforces 기본값
                problem_statement="",  # 개별 API 호출 필요
                input_format="",
                output_format="",
                constraints="",
                examples=[],
                tags=tags,
                notes=f"Rating: {cf_problem.get('rating', 'Unknown')}"
            )

            return problem

        except Exception as e:
            self.logger.error(f"문제 변환 실패: {e}")
            return None

    def _map_difficulty(self, rating: int) -> ProblemDifficulty:
        """Codeforces rating을 난이도로 매핑합니다."""
        if rating < 1200:
            return ProblemDifficulty.EASY
        elif rating < 1800:
            return ProblemDifficulty.MEDIUM
        elif rating < 2400:
            return ProblemDifficulty.HARD
        else:
            return ProblemDifficulty.EXPERT

    def _map_tag(self, cf_tag: str) -> Optional[ProblemTag]:
        """Codeforces 태그를 ProblemTag로 매핑합니다."""
        tag_mapping = {
            'brute force': ProblemTag.BRUTE_FORCE,
            'greedy': ProblemTag.GREEDY,
            'dp': ProblemTag.DYNAMIC_PROGRAMMING,
            'divide and conquer': ProblemTag.DIVIDE_AND_CONQUER,
            'backtracking': ProblemTag.BACKTRACKING,
            'arrays': ProblemTag.ARRAY,
            'strings': ProblemTag.STRING,
            'stacks': ProblemTag.STACK,
            'queues': ProblemTag.QUEUE,
            'trees': ProblemTag.TREE,
            'graphs': ProblemTag.GRAPH,
            'dfs and similar': ProblemTag.DFS,
            'bfs': ProblemTag.BFS,
            'shortest paths': ProblemTag.DIJKSTRA,
            'math': ProblemTag.MATH,
            'number theory': ProblemTag.NUMBER_THEORY,
            'combinatorics': ProblemTag.COMBINATORICS,
            'geometry': ProblemTag.GEOMETRY,
            'binary search': ProblemTag.BINARY_SEARCH,
            'sortings': ProblemTag.SORTING,
            'bitmasks': ProblemTag.BIT_MANIPULATION,
            'data structures': ProblemTag.HASH_TABLE,
            'two pointers': ProblemTag.TWO_POINTERS,
            'sliding window': ProblemTag.SLIDING_WINDOW
        }

        return tag_mapping.get(cf_tag.lower())


class LeetCodeProvider(RemoteProblemProvider):
    """LeetCode API 연동 (비공식)"""

    def __init__(self, cache_dir: str = "cache"):
        super().__init__(ProblemPlatform.LEETCODE, cache_dir)
        self.base_url = "https://leetcode.com/graphql"

        # LeetCode GraphQL 쿼리
        self.problems_query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    acRate
                    difficulty
                    freqBar
                    frontendQuestionId: questionFrontendId
                    isFavor
                    paidOnly: isPaidOnly
                    status
                    title
                    titleSlug
                    topicTags {
                        name
                        id
                        slug
                    }
                    hasSolution
                    hasVideoSolution
                }
            }
        }
        """

    def get_problems(self, limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """LeetCode에서 문제 목록을 가져옵니다."""
        cache_key = f"problems_list_{limit or 'all'}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=6)

        if cached_data and isinstance(cached_data, dict):
            problems_data = cached_data.get("problems", [])
            return [AlgorithmProblem.from_dict(problem_data) for problem_data in problems_data if isinstance(problem_data, dict)]

        variables = {
            "categorySlug": "",
            "limit": limit or 100,
            "skip": 0,
            "filters": {}
        }

        data = self._make_graphql_request(self.problems_query, variables)

        if not data:
            return []

        problems = []
        questions = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])

        for question in questions:
            try:
                problem = self._convert_to_algorithm_problem(question)
                if problem:
                    problems.append(problem)
            except Exception as e:
                self.logger.warning(f"문제 변환 실패: {e}")
                continue

        # 캐시에 저장
        cache_data = {"problems": [problem.to_dict() for problem in problems]}
        self._save_to_cache(cache_key, cache_data)

        return problems

    def get_problem_details(self, problem_id: str) -> Optional[AlgorithmProblem]:
        """특정 문제의 상세 정보를 가져옵니다."""
        cache_key = f"problem_details_{problem_id}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=24)

        if cached_data:
            return AlgorithmProblem.from_dict(cached_data)

        # 문제 목록에서 찾기
        problems = self.get_problems(limit=1000)

        for problem in problems:
            if problem.platform_problem_id == problem_id:
                self._save_to_cache(cache_key, problem.to_dict())
                return problem

        return None

    def _make_graphql_request(self, query: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """GraphQL 요청을 수행합니다."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FocusTimer/2.0.0 (Algorithm System)'
        }

        payload = {
            'query': query,
            'variables': variables
        }

        try:
            response = self.session.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GraphQL 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 실패: {e}")
            return None

    def _convert_to_algorithm_problem(self, lc_question: Dict[str, Any]) -> Optional[AlgorithmProblem]:
        """LeetCode 문제 데이터를 AlgorithmProblem으로 변환합니다."""
        try:
            # 난이도 매핑
            difficulty = self._map_difficulty(lc_question.get('difficulty', ''))

            # 태그 매핑
            tags = set()
            for topic_tag in lc_question.get('topicTags', []):
                tag = self._map_tag(topic_tag.get('name', ''))
                if tag:
                    tags.add(tag)

            problem = AlgorithmProblem(
                title=lc_question.get('title', ''),
                description=f"LeetCode 문제: {lc_question.get('title', '')}",
                difficulty=difficulty,
                platform=ProblemPlatform.LEETCODE,
                platform_problem_id=lc_question.get('frontendQuestionId', ''),
                platform_url=f"https://leetcode.com/problems/{lc_question.get('titleSlug', '')}/",
                time_limit=1.0,  # LeetCode 기본값
                memory_limit=64,  # LeetCode 기본값
                problem_statement="",  # 개별 API 호출 필요
                input_format="",
                output_format="",
                constraints="",
                examples=[],
                tags=tags,
                notes=f"Acceptance Rate: {lc_question.get('acRate', 0):.1f}%"
            )

            return problem

        except Exception as e:
            self.logger.error(f"문제 변환 실패: {e}")
            return None

    def _map_difficulty(self, lc_difficulty: str) -> ProblemDifficulty:
        """LeetCode 난이도를 ProblemDifficulty로 매핑합니다."""
        mapping = {
            'Easy': ProblemDifficulty.EASY,
            'Medium': ProblemDifficulty.MEDIUM,
            'Hard': ProblemDifficulty.HARD
        }
        return mapping.get(lc_difficulty, ProblemDifficulty.MEDIUM)

    def _map_tag(self, lc_tag: str) -> Optional[ProblemTag]:
        """LeetCode 태그를 ProblemTag로 매핑합니다."""
        tag_mapping = {
            'Array': ProblemTag.ARRAY,
            'String': ProblemTag.STRING,
            'Linked List': ProblemTag.LINKED_LIST,
            'Stack': ProblemTag.STACK,
            'Queue': ProblemTag.QUEUE,
            'Tree': ProblemTag.TREE,
            'Graph': ProblemTag.GRAPH,
            'Hash Table': ProblemTag.HASH_TABLE,
            'Trie': ProblemTag.TRIE,
            'Depth-First Search': ProblemTag.DFS,
            'Breadth-First Search': ProblemTag.BFS,
            'Dynamic Programming': ProblemTag.DYNAMIC_PROGRAMMING,
            'Greedy': ProblemTag.GREEDY,
            'Backtracking': ProblemTag.BACKTRACKING,
            'Binary Search': ProblemTag.BINARY_SEARCH,
            'Two Pointers': ProblemTag.TWO_POINTERS,
            'Sliding Window': ProblemTag.SLIDING_WINDOW,
            'Sorting': ProblemTag.SORTING,
            'Bit Manipulation': ProblemTag.BIT_MANIPULATION,
            'Math': ProblemTag.MATH,
            'Geometry': ProblemTag.GEOMETRY,
            'Combinatorics': ProblemTag.COMBINATORICS
        }

        return tag_mapping.get(lc_tag)


class KaggleProvider(RemoteProblemProvider):
    """Kaggle API 연동"""

    def __init__(self, api_token_path: str = "kaggle.json", cache_dir: str = "cache"):
        super().__init__(ProblemPlatform.KAGGLE, cache_dir)
        self.api_token_path = api_token_path
        self.base_url = "https://www.kaggle.com/api/v1"

        # Kaggle API 토큰 설정
        self._setup_kaggle_auth()

    def _setup_kaggle_auth(self) -> None:
        """Kaggle API 인증을 설정합니다."""
        if not os.path.exists(self.api_token_path):
            self.logger.warning(f"Kaggle API 토큰 파일이 없습니다: {self.api_token_path}")
            return

        try:
            # Kaggle API 토큰을 환경 변수로 설정
            os.environ['KAGGLE_CONFIG_DIR'] = os.path.dirname(os.path.abspath(self.api_token_path))
            self.logger.info("Kaggle API 인증 설정 완료")
        except Exception as e:
            self.logger.error(f"Kaggle API 인증 설정 실패: {e}")

    def get_problems(self, limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """Kaggle에서 알고리즘 관련 데이터셋을 가져옵니다."""
        cache_key = f"problems_list_{limit or 'all'}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=12)

        if cached_data and isinstance(cached_data, dict):
            problems_data = cached_data.get("problems", [])
            return [AlgorithmProblem.from_dict(problem_data) for problem_data in problems_data if isinstance(problem_data, dict)]

        # Kaggle API를 통한 데이터셋 검색
        search_url = f"{self.base_url}/datasets/search"
        params = {
            'search': 'algorithm programming',
            'fileType': 'csv',
            'licenseName': 'CC0-1.0',
            'size': 'small'
        }

        data = self._make_request(search_url, params=params)

        if not data:
            return []

        problems = []
        datasets = data.get('results', [])[:limit]

        for dataset in datasets:
            try:
                problem = self._convert_to_algorithm_problem(dataset)
                if problem:
                    problems.append(problem)
            except Exception as e:
                self.logger.warning(f"문제 변환 실패: {e}")
                continue

        # 캐시에 저장
        cache_data = {"problems": [problem.to_dict() for problem in problems]}
        self._save_to_cache(cache_key, cache_data)

        return problems

    def get_problem_details(self, problem_id: str) -> Optional[AlgorithmProblem]:
        """특정 문제의 상세 정보를 가져옵니다."""
        cache_key = f"problem_details_{problem_id}"
        cached_data = self._load_from_cache(cache_key, max_age_hours=24)

        if cached_data:
            return AlgorithmProblem.from_dict(cached_data)

        # 데이터셋 상세 정보 가져오기
        dataset_url = f"{self.base_url}/datasets/{problem_id}"
        data = self._make_request(dataset_url)

        if not data:
            return None

        problem = self._convert_to_algorithm_problem(data)
        if problem:
            self._save_to_cache(cache_key, problem.to_dict())

        return problem

    def _convert_to_algorithm_problem(self, kaggle_dataset: Dict[str, Any]) -> Optional[AlgorithmProblem]:
        """Kaggle 데이터셋을 AlgorithmProblem으로 변환합니다."""
        try:
            # 태그 매핑
            tags = {ProblemTag.MATH, ProblemTag.ARRAY}

            # 데이터셋 제목에서 태그 추출
            title = kaggle_dataset.get('title', '').lower()
            if 'sort' in title:
                tags.add(ProblemTag.SORTING)
            if 'search' in title:
                tags.add(ProblemTag.BINARY_SEARCH)
            if 'graph' in title:
                tags.add(ProblemTag.GRAPH)
            if 'array' in title:
                tags.add(ProblemTag.ARRAY)

            problem = AlgorithmProblem(
                title=kaggle_dataset.get('title', ''),
                description=kaggle_dataset.get('description', ''),
                difficulty=ProblemDifficulty.MEDIUM,  # Kaggle은 대부분 중간 난이도
                platform=ProblemPlatform.KAGGLE,
                platform_problem_id=kaggle_dataset.get('ref', ''),
                platform_url=f"https://www.kaggle.com/datasets/{kaggle_dataset.get('ref', '')}",
                time_limit=5.0,  # Kaggle은 더 긴 시간 제한
                memory_limit=512,  # Kaggle은 더 큰 메모리 제한
                problem_statement=kaggle_dataset.get('description', ''),
                input_format="CSV 데이터셋",
                output_format="분석 결과",
                constraints="",
                examples=[],
                tags=tags,
                notes=f"Downloads: {kaggle_dataset.get('downloadCount', 0)}, Votes: {kaggle_dataset.get('voteCount', 0)}"
            )

            return problem

        except Exception as e:
            self.logger.error(f"문제 변환 실패: {e}")
            return None


class RemoteProblemManager:
    """외부 플랫폼 문제 관리자"""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.providers = {
            ProblemPlatform.CODEFORCES: CodeforcesProvider(cache_dir),
            ProblemPlatform.LEETCODE: LeetCodeProvider(cache_dir),
            ProblemPlatform.KAGGLE: KaggleProvider(cache_dir=cache_dir)
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_provider(self, platform: ProblemPlatform) -> Optional[RemoteProblemProvider]:
        """플랫폼별 프로바이더를 반환합니다."""
        return self.providers.get(platform)

    def get_all_problems(self, platform: ProblemPlatform, limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """특정 플랫폼에서 모든 문제를 가져옵니다."""
        provider = self.get_provider(platform)
        if not provider:
            self.logger.error(f"지원하지 않는 플랫폼: {platform}")
            return []

        try:
            return provider.get_problems(limit=limit)
        except Exception as e:
            self.logger.error(f"문제 가져오기 실패 ({platform}): {e}")
            return []

    def get_problem_details(self, platform: ProblemPlatform, problem_id: str) -> Optional[AlgorithmProblem]:
        """특정 문제의 상세 정보를 가져옵니다."""
        provider = self.get_provider(platform)
        if not provider:
            self.logger.error(f"지원하지 않는 플랫폼: {platform}")
            return None

        try:
            return provider.get_problem_details(problem_id)
        except Exception as e:
            self.logger.error(f"문제 상세 정보 가져오기 실패 ({platform}): {e}")
            return None

    def get_problems_by_difficulty(self, platform: ProblemPlatform,
                                 difficulty: ProblemDifficulty,
                                 limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """특정 난이도의 문제들을 가져옵니다."""
        all_problems = self.get_all_problems(platform, limit=limit * 3 if limit else None)
        filtered_problems = [p for p in all_problems if p.difficulty == difficulty]

        if limit:
            filtered_problems = filtered_problems[:limit]

        return filtered_problems

    def get_problems_by_tag(self, platform: ProblemPlatform,
                           tag: ProblemTag,
                           limit: Optional[int] = None) -> List[AlgorithmProblem]:
        """특정 태그의 문제들을 가져옵니다."""
        all_problems = self.get_all_problems(platform, limit=limit * 3 if limit else None)
        filtered_problems = [p for p in all_problems if tag in p.tags]

        if limit:
            filtered_problems = filtered_problems[:limit]

        return filtered_problems

    def refresh_cache(self, platform: ProblemPlatform) -> bool:
        """특정 플랫폼의 캐시를 새로고침합니다."""
        provider = self.get_provider(platform)
        if not provider:
            return False

        try:
            # 캐시 파일들 삭제
            import glob
            cache_pattern = os.path.join(provider.cache_dir, f"{platform.name.lower()}_*.json")
            for cache_file in glob.glob(cache_pattern):
                os.remove(cache_file)

            self.logger.info(f"{platform} 캐시 새로고침 완료")
            return True
        except Exception as e:
            self.logger.error(f"캐시 새로고침 실패 ({platform}): {e}")
            return False

    def get_supported_platforms(self) -> List[ProblemPlatform]:
        """지원하는 플랫폼 목록을 반환합니다."""
        return list(self.providers.keys())