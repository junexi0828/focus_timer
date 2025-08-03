"""
GUI 알고리즘 관리 인터페이스

이 모듈은 고급 알고리즘 챌린지 시스템을 사용자 친화적인 GUI로 제공합니다.
tkinter를 사용하여 직관적이고 기능적인 인터페이스를 구현합니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading
import queue

try:
    from .advanced_challenge_system import (
        AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
        CodeTestResult, PerformanceMetrics
    )
    from .problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
    from .remote_problem_provider import RemoteProblemProvider
except ImportError:
    from advanced_challenge_system import (
        AdvancedChallengeSystem, Challenge, ChallengeType, ChallengeStatus,
        CodeTestResult, PerformanceMetrics
    )
    from problem_data_structures import (
        AlgorithmProblem, ProblemDifficulty, ProblemPlatform, ProblemTag
    )
    from remote_problem_provider import RemoteProblemProvider


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
                from problem_data_structures import ProblemTestCase
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


class AlgorithmManagerGUI:
    """알고리즘 관리 GUI 메인 클래스"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("알고리즘 문제 풀이 시스템")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # 시스템 초기화
        self.problem_provider = MockProblemProvider()
        self.challenge_system = AdvancedChallengeSystem("gui_user", self.problem_provider)

        # 현재 선택된 문제
        self.current_problem: Optional[AlgorithmProblem] = None
        self.current_challenge: Optional[Challenge] = None

        # GUI 구성
        self.setup_gui()
        self.load_initial_data()

        # 주기적 업데이트
        self.schedule_updates()

    def setup_gui(self):
        """GUI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 상단 통계 패널
        self.setup_statistics_panel(main_frame)

        # 메인 컨텐츠 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # 왼쪽 패널 (문제 목록, 챌린지)
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 오른쪽 패널 (문제 상세, 코드 편집)
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 왼쪽 패널 구성
        self.setup_left_panel(left_panel)

        # 오른쪽 패널 구성
        self.setup_right_panel(right_panel)

    def setup_statistics_panel(self, parent):
        """상단 통계 패널 구성"""
        stats_frame = ttk.LabelFrame(parent, text="사용자 통계", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # 통계 정보 표시
        self.stats_labels = {}
        stats_data = [
            ("level", "레벨"),
            ("difficulty", "추천 난이도"),
            ("solved", "해결한 문제"),
            ("streak", "연속 해결"),
            ("success_rate", "성공률")
        ]

        for i, (key, label) in enumerate(stats_data):
            frame = ttk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, padx=(0, 20))

            ttk.Label(frame, text=f"{label}:", font=('Arial', 10, 'bold')).pack()
            self.stats_labels[key] = ttk.Label(frame, text="로딩...", font=('Arial', 10))
            self.stats_labels[key].pack()

        # 새로고침 버튼
        ttk.Button(stats_frame, text="새로고침", command=self.refresh_statistics).pack(side=tk.RIGHT)

    def setup_left_panel(self, parent):
        """왼쪽 패널 구성"""
        # 노트북 (탭) 생성
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 문제 추천 탭
        self.setup_recommendations_tab(notebook)

        # 챌린지 탭
        self.setup_challenges_tab(notebook)

        # 학습 경로 탭
        self.setup_learning_path_tab(notebook)

        # 통계 탭
        self.setup_statistics_tab(notebook)

    def setup_recommendations_tab(self, notebook):
        """문제 추천 탭 구성"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="문제 추천")

        # 상단 버튼들
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="추천 새로고침", command=self.refresh_recommendations).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="일일 챌린지 생성", command=self.create_daily_challenge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="주간 챌린지 생성", command=self.create_weekly_challenge).pack(side=tk.LEFT)

        # 추천 문제 목록
        list_frame = ttk.LabelFrame(frame, text="추천 문제", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('title', 'difficulty', 'tags')
        self.recommendations_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.recommendations_tree.heading('title', text='제목')
        self.recommendations_tree.heading('difficulty', text='난이도')
        self.recommendations_tree.heading('tags', text='태그')

        self.recommendations_tree.column('title', width=200)
        self.recommendations_tree.column('difficulty', width=80)
        self.recommendations_tree.column('tags', width=150)

        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        self.recommendations_tree.configure(yscrollcommand=scrollbar.set)

        self.recommendations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.recommendations_tree.bind('<Double-1>', self.on_problem_select)

    def setup_challenges_tab(self, notebook):
        """챌린지 탭 구성"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="챌린지")

        # 상단 버튼들
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="커스텀 챌린지 생성", command=self.create_custom_challenge_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="챌린지 새로고침", command=self.refresh_challenges).pack(side=tk.LEFT)

        # 챌린지 목록
        list_frame = ttk.LabelFrame(frame, text="활성 챌린지", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('name', 'type', 'progress', 'remaining', 'reward')
        self.challenges_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.challenges_tree.heading('name', text='챌린지명')
        self.challenges_tree.heading('type', text='유형')
        self.challenges_tree.heading('progress', text='진도')
        self.challenges_tree.heading('remaining', text='남은 시간')
        self.challenges_tree.heading('reward', text='보상')

        self.challenges_tree.column('name', width=200)
        self.challenges_tree.column('type', width=80)
        self.challenges_tree.column('progress', width=80)
        self.challenges_tree.column('remaining', width=100)
        self.challenges_tree.column('reward', width=80)

        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.challenges_tree.yview)
        self.challenges_tree.configure(yscrollcommand=scrollbar.set)

        self.challenges_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.challenges_tree.bind('<Double-1>', self.on_challenge_select)

    def setup_learning_path_tab(self, notebook):
        """학습 경로 탭 구성"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="학습 경로")

        # 상단 컨트롤
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="목표:").pack(side=tk.LEFT)
        self.goal_var = tk.StringVar(value="기초 알고리즘 마스터")
        goal_entry = ttk.Entry(control_frame, textvariable=self.goal_var, width=30)
        goal_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(control_frame, text="기간(일):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="30")
        duration_entry = ttk.Entry(control_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(control_frame, text="학습 경로 생성", command=self.generate_learning_path).pack(side=tk.LEFT)

        # 학습 경로 목록
        list_frame = ttk.LabelFrame(frame, text="생성된 학습 경로", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 트리뷰 생성
        columns = ('title', 'difficulty', 'tags', 'status')
        self.learning_path_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # 컬럼 설정
        self.learning_path_tree.heading('title', text='문제 제목')
        self.learning_path_tree.heading('difficulty', text='난이도')
        self.learning_path_tree.heading('tags', text='태그')
        self.learning_path_tree.heading('status', text='상태')

        self.learning_path_tree.column('title', width=200)
        self.learning_path_tree.column('difficulty', width=80)
        self.learning_path_tree.column('tags', width=150)
        self.learning_path_tree.column('status', width=80)

        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.learning_path_tree.yview)
        self.learning_path_tree.configure(yscrollcommand=scrollbar.set)

        self.learning_path_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭 이벤트
        self.learning_path_tree.bind('<Double-1>', self.on_problem_select)

    def setup_statistics_tab(self, notebook):
        """통계 탭 구성"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="통계")

        # 통계 정보 표시
        stats_frame = ttk.LabelFrame(frame, text="상세 통계", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # 약점/강점 분석
        analysis_frame = ttk.Frame(stats_frame)
        analysis_frame.pack(fill=tk.BOTH, expand=True)

        # 약점 영역
        weak_frame = ttk.LabelFrame(analysis_frame, text="약점 영역", padding=10)
        weak_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.weak_text = scrolledtext.ScrolledText(weak_frame, height=10, width=40)
        self.weak_text.pack(fill=tk.BOTH, expand=True)

        # 강점 영역
        strong_frame = ttk.LabelFrame(analysis_frame, text="강점 영역", padding=10)
        strong_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.strong_text = scrolledtext.ScrolledText(strong_frame, height=10, width=40)
        self.strong_text.pack(fill=tk.BOTH, expand=True)

        # 새로고침 버튼
        ttk.Button(stats_frame, text="통계 새로고침", command=self.refresh_detailed_statistics).pack(pady=10)

    def setup_right_panel(self, parent):
        """오른쪽 패널 구성"""
        # 문제 상세 정보
        detail_frame = ttk.LabelFrame(parent, text="문제 상세", padding=10)
        detail_frame.pack(fill=tk.X, pady=(0, 10))

        self.problem_title_label = ttk.Label(detail_frame, text="문제를 선택하세요", font=('Arial', 12, 'bold'))
        self.problem_title_label.pack(anchor=tk.W)

        self.problem_description_text = scrolledtext.ScrolledText(detail_frame, height=6, width=60)
        self.problem_description_text.pack(fill=tk.X, pady=(5, 0))

        # 코드 편집 영역
        code_frame = ttk.LabelFrame(parent, text="코드 편집", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 언어 선택
        lang_frame = ttk.Frame(code_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(lang_frame, text="언어:").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="python")
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                    values=["python", "java", "cpp", "javascript"],
                                    state="readonly", width=15)
        language_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 코드 에디터
        self.code_editor = scrolledtext.ScrolledText(code_frame, height=20, width=60, font=('Consolas', 10))
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        # 하단 버튼들
        button_frame = ttk.Frame(code_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="코드 실행", command=self.run_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="코드 저장", command=self.save_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="코드 불러오기", command=self.load_code).pack(side=tk.LEFT)

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(parent, text="실행 결과", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, width=60)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def load_initial_data(self):
        """초기 데이터 로드"""
        self.refresh_statistics()
        self.refresh_recommendations()
        self.refresh_challenges()
        self.refresh_detailed_statistics()

        # 기본 코드 템플릿 로드
        self.load_code_template()

    def load_code_template(self):
        """기본 코드 템플릿 로드"""
        template = '''def solve():
    # 여기에 해결 코드를 작성하세요
    pass

if __name__ == "__main__":
    solve()
'''
        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(1.0, template)

    def refresh_statistics(self):
        """통계 새로고침"""
        try:
            stats = self.challenge_system.get_user_statistics()

            self.stats_labels['level'].config(text=str(stats['user_level']))
            self.stats_labels['difficulty'].config(text=stats['recommended_difficulty'])
            self.stats_labels['solved'].config(text=str(stats['total_problems_solved']))
            self.stats_labels['streak'].config(text=f"{stats['current_streak']}일")
            self.stats_labels['success_rate'].config(text=f"{stats['success_rate']:.1%}")

        except Exception as e:
            messagebox.showerror("오류", f"통계 로드 실패: {e}")

    def refresh_recommendations(self):
        """추천 문제 새로고침"""
        try:
            # 기존 항목 삭제
            for item in self.recommendations_tree.get_children():
                self.recommendations_tree.delete(item)

            # 새로운 추천 문제 로드
            recommendations = self.challenge_system.get_personalized_recommendations(10)

            for problem in recommendations:
                tags_str = ', '.join(tag.name for tag in problem.tags)
                self.recommendations_tree.insert('', 'end',
                                               values=(problem.title, problem.difficulty.name, tags_str),
                                               tags=(problem.id,))

        except Exception as e:
            messagebox.showerror("오류", f"추천 문제 로드 실패: {e}")

    def refresh_challenges(self):
        """챌린지 새로고침"""
        try:
            # 기존 항목 삭제
            for item in self.challenges_tree.get_children():
                self.challenges_tree.delete(item)

            # 활성 챌린지 로드
            active_challenges = self.challenge_system.get_active_challenges()

            for challenge in active_challenges:
                progress = challenge.get_progress_percentage()
                remaining = challenge.get_remaining_days()

                self.challenges_tree.insert('', 'end',
                                          values=(challenge.name,
                                                 challenge.challenge_type.name,
                                                 f"{progress:.1f}%",
                                                 f"{remaining}일",
                                                 f"{challenge.reward_points}점"),
                                          tags=(challenge.challenge_id,))

        except Exception as e:
            messagebox.showerror("오류", f"챌린지 로드 실패: {e}")

    def refresh_detailed_statistics(self):
        """상세 통계 새로고침"""
        try:
            # 약점 영역
            weak_areas = self.challenge_system.get_weak_areas(10)
            weak_text = "약점 영역 (해결한 문제 수 기준):\n\n"
            for tag, count in weak_areas:
                weak_text += f"• {tag}: {count}문제 해결\n"

            self.weak_text.delete(1.0, tk.END)
            self.weak_text.insert(1.0, weak_text)

            # 강점 영역
            strong_areas = self.challenge_system.get_strong_areas(10)
            strong_text = "강점 영역 (해결한 문제 수 기준):\n\n"
            for tag, count in strong_areas:
                strong_text += f"• {tag}: {count}문제 해결\n"

            self.strong_text.delete(1.0, tk.END)
            self.strong_text.insert(1.0, strong_text)

        except Exception as e:
            messagebox.showerror("오류", f"상세 통계 로드 실패: {e}")

    def on_problem_select(self, event):
        """문제 선택 이벤트"""
        try:
            selection = self.recommendations_tree.selection()
            if not selection:
                return

            item = self.recommendations_tree.item(selection[0])
            problem_id = item['tags'][0]

            # 문제 정보 로드
            self.current_problem = self.problem_provider.get_problem_by_id(problem_id)

            # 문제 상세 정보 표시
            self.problem_title_label.config(text=f"{self.current_problem.title} ({self.current_problem.difficulty.name})")

            description = f"설명: {self.current_problem.description}\n\n"
            description += f"입력 형식: {self.current_problem.input_format}\n"
            description += f"출력 형식: {self.current_problem.output_format}\n\n"
            description += "태그: " + ', '.join(tag.name for tag in self.current_problem.tags)

            self.problem_description_text.delete(1.0, tk.END)
            self.problem_description_text.insert(1.0, description)

            # 코드 템플릿 로드
            self.load_code_template()

        except Exception as e:
            messagebox.showerror("오류", f"문제 로드 실패: {e}")

    def on_challenge_select(self, event):
        """챌린지 선택 이벤트"""
        try:
            selection = self.challenges_tree.selection()
            if not selection:
                return

            item = self.challenges_tree.item(selection[0])
            challenge_id = item['tags'][0]

            # 챌린지 정보 로드
            self.current_challenge = self.challenge_system.get_challenge_progress(challenge_id)

            if self.current_challenge:
                messagebox.showinfo("챌린지 정보",
                                  f"챌린지: {self.current_challenge.name}\n"
                                  f"설명: {self.current_challenge.description}\n"
                                  f"진도: {self.current_challenge.get_progress_percentage():.1f}%\n"
                                  f"남은 시간: {self.current_challenge.get_remaining_days()}일\n"
                                  f"보상: {self.current_challenge.reward_points}점")

        except Exception as e:
            messagebox.showerror("오류", f"챌린지 로드 실패: {e}")

    def create_daily_challenge(self):
        """일일 챌린지 생성"""
        try:
            challenge = self.challenge_system.create_daily_challenge()
            messagebox.showinfo("성공", f"일일 챌린지가 생성되었습니다!\n\n"
                                       f"이름: {challenge.name}\n"
                                       f"목표 문제 수: {challenge.target_problems}\n"
                                       f"보상: {challenge.reward_points}점")
            self.refresh_challenges()
        except Exception as e:
            messagebox.showerror("오류", f"일일 챌린지 생성 실패: {e}")

    def create_weekly_challenge(self):
        """주간 챌린지 생성"""
        try:
            challenge = self.challenge_system.create_weekly_challenge()
            messagebox.showinfo("성공", f"주간 챌린지가 생성되었습니다!\n\n"
                                       f"이름: {challenge.name}\n"
                                       f"목표 문제 수: {challenge.target_problems}\n"
                                       f"보상: {challenge.reward_points}점")
            self.refresh_challenges()
        except Exception as e:
            messagebox.showerror("오류", f"주간 챌린지 생성 실패: {e}")

    def create_custom_challenge_dialog(self):
        """커스텀 챌린지 생성 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title("커스텀 챌린지 생성")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 입력 필드들
        ttk.Label(dialog, text="챌린지 이름:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="설명:").pack(pady=5)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="난이도:").pack(pady=5)
        difficulty_var = tk.StringVar(value="MEDIUM")
        difficulty_combo = ttk.Combobox(dialog, textvariable=difficulty_var,
                                      values=["EASY", "MEDIUM", "HARD", "EXPERT"],
                                      state="readonly")
        difficulty_combo.pack(pady=5)

        ttk.Label(dialog, text="목표 문제 수:").pack(pady=5)
        target_var = tk.StringVar(value="5")
        ttk.Entry(dialog, textvariable=target_var, width=20).pack(pady=5)

        ttk.Label(dialog, text="기간(일):").pack(pady=5)
        days_var = tk.StringVar(value="7")
        ttk.Entry(dialog, textvariable=days_var, width=20).pack(pady=5)

        def create_challenge():
            try:
                from problem_data_structures import ProblemDifficulty
                difficulty = ProblemDifficulty[difficulty_var.get()]

                challenge = self.challenge_system.create_custom_challenge(
                    name=name_var.get(),
                    description=desc_var.get(),
                    target_difficulty=difficulty,
                    target_problems=int(target_var.get()),
                    time_limit_days=int(days_var.get())
                )

                messagebox.showinfo("성공", "커스텀 챌린지가 생성되었습니다!")
                dialog.destroy()
                self.refresh_challenges()

            except Exception as e:
                messagebox.showerror("오류", f"챌린지 생성 실패: {e}")

        ttk.Button(dialog, text="생성", command=create_challenge).pack(pady=20)

    def generate_learning_path(self):
        """학습 경로 생성"""
        try:
            goal = self.goal_var.get()
            duration = int(self.duration_var.get())

            # 기존 항목 삭제
            for item in self.learning_path_tree.get_children():
                self.learning_path_tree.delete(item)

            # 학습 경로 생성
            learning_path = self.challenge_system.generate_learning_path(goal, duration)

            for problem in learning_path:
                tags_str = ', '.join(tag.name for tag in problem.tags)
                solved_problems = set(self.challenge_system.progress_tracker.get_solved_problems())
                status = "완료" if problem.id in solved_problems else "미완료"

                self.learning_path_tree.insert('', 'end',
                                             values=(problem.title,
                                                    problem.difficulty.name,
                                                    tags_str, status),
                                             tags=(problem.id,))

            messagebox.showinfo("성공", f"학습 경로가 생성되었습니다!\n총 {len(learning_path)}개 문제")

        except Exception as e:
            messagebox.showerror("오류", f"학습 경로 생성 실패: {e}")

    def run_code(self):
        """코드 실행"""
        if not self.current_problem:
            messagebox.showwarning("경고", "먼저 문제를 선택하세요.")
            return

        try:
            # 코드 가져오기
            code = self.code_editor.get(1.0, tk.END).strip()
            language = self.language_var.get()

            if not code:
                messagebox.showwarning("경고", "코드를 입력하세요.")
                return

            # 테스트 케이스 준비
            test_cases = []
            for tc in self.current_problem.test_cases:
                test_cases.append({
                    'input': tc.input_data,
                    'output': tc.expected_output
                })

            # 코드 실행
            is_correct, test_results, performance = self.challenge_system.submit_solution(
                self.current_problem.id, code, language, test_cases
            )

            # 결과 표시
            result_text = f"실행 결과:\n"
            result_text += f"정답 여부: {'✓ 정답' if is_correct else '✗ 오답'}\n"
            result_text += f"테스트 통과: {performance.passed_test_cases}/{performance.total_test_cases}\n"
            result_text += f"성공률: {performance.calculate_success_rate():.1f}%\n"
            result_text += f"평균 실행 시간: {performance.average_execution_time:.4f}초\n"
            result_text += f"코드 품질 점수: {performance.code_quality_score:.1f}/100\n\n"

            if not is_correct:
                result_text += "실패한 테스트 케이스:\n"
                for result in test_results:
                    if not result.is_passed:
                        result_text += f"입력: {result.input_data}\n"
                        result_text += f"기대: {result.expected_output}\n"
                        result_text += f"실제: {result.actual_output}\n"
                        if result.error_message:
                            result_text += f"오류: {result.error_message}\n"
                        result_text += "-" * 30 + "\n"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result_text)

            # 통계 업데이트
            if is_correct:
                self.refresh_statistics()
                self.refresh_challenges()
                messagebox.showinfo("축하합니다!", "문제를 성공적으로 해결했습니다!")

        except Exception as e:
            messagebox.showerror("오류", f"코드 실행 실패: {e}")

    def save_code(self):
        """코드 저장"""
        if not self.current_problem:
            messagebox.showwarning("경고", "먼저 문제를 선택하세요.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                initialfile=f"{self.current_problem.id}.py"
            )

            if filename:
                code = self.code_editor.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("성공", "코드가 저장되었습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"코드 저장 실패: {e}")

    def load_code(self):
        """코드 불러오기"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, code)
                messagebox.showinfo("성공", "코드가 불러와졌습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"코드 불러오기 실패: {e}")

    def schedule_updates(self):
        """주기적 업데이트 스케줄링"""
        # 30초마다 통계 업데이트
        self.root.after(30000, self.auto_refresh)

    def auto_refresh(self):
        """자동 새로고침"""
        try:
            self.refresh_statistics()
            self.refresh_challenges()
        except:
            pass
        finally:
            # 다음 업데이트 스케줄링
            self.root.after(30000, self.auto_refresh)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = AlgorithmManagerGUI(root)

    # 창 닫기 이벤트 처리
    def on_closing():
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # GUI 실행
    root.mainloop()


if __name__ == "__main__":
    main()