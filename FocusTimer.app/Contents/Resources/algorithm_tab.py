"""
알고리즘 탭 - FocusTimer.app의 notebook에 삽입될 ttk.Frame 기반 탭
"""
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

        # 추천 문제 버튼들
        rec_buttons_frame = ttk.Frame(recommendations_frame)
        rec_buttons_frame.pack(fill=tk.X)

        ttk.Button(rec_buttons_frame, text="🔄 새로고침",
                  command=self.refresh_recommendations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rec_buttons_frame, text="📅 일일 챌린지",
                  command=self.create_daily_challenge).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rec_buttons_frame, text="📊 주간 챌린지",
                  command=self.create_weekly_challenge).pack(side=tk.LEFT)

        # 챌린지 섹션
        challenges_frame = ttk.LabelFrame(left_panel, text="🏆 활성 챌린지", padding="10")
        challenges_frame.pack(fill=tk.BOTH, expand=True)

        # 챌린지 목록
        self.challenges_tree = ttk.Treeview(challenges_frame,
                                          columns=('name', 'progress', 'remaining'),
                                          show='headings', height=6)
        self.challenges_tree.heading('name', text='챌린지명')
        self.challenges_tree.heading('progress', text='진도')
        self.challenges_tree.heading('remaining', text='남은 시간')
        self.challenges_tree.column('name', width=200)
        self.challenges_tree.column('progress', width=80)
        self.challenges_tree.column('remaining', width=100)
        self.challenges_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 챌린지 버튼들
        chal_buttons_frame = ttk.Frame(challenges_frame)
        chal_buttons_frame.pack(fill=tk.X)

        ttk.Button(chal_buttons_frame, text="🔄 새로고침",
                  command=self.refresh_challenges).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(chal_buttons_frame, text="➕ 커스텀 챌린지",
                  command=self.create_custom_challenge).pack(side=tk.LEFT)

        # 우측 패널 (문제 풀이 및 통계)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 문제 풀이 섹션
        problem_frame = ttk.LabelFrame(right_panel, text="💻 문제 풀이", padding="10")
        problem_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 문제 정보
        self.problem_title_label = ttk.Label(problem_frame, text="문제를 선택하세요",
                                           font=('Helvetica', 12, 'bold'))
        self.problem_title_label.pack(anchor=tk.W, pady=(0, 5))

        self.problem_description_text = tk.Text(problem_frame, height=6, wrap=tk.WORD)
        self.problem_description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 코드 입력
        code_label = ttk.Label(problem_frame, text="코드 입력:")
        code_label.pack(anchor=tk.W, pady=(0, 5))

        self.code_text = tk.Text(problem_frame, height=10, wrap=tk.NONE, font=('Courier', 10))
        code_scrollbar = ttk.Scrollbar(problem_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=code_scrollbar.set)

        code_frame = ttk.Frame(problem_frame)
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 풀이 버튼들
        solve_buttons_frame = ttk.Frame(problem_frame)
        solve_buttons_frame.pack(fill=tk.X)

        ttk.Button(solve_buttons_frame, text="▶️ 실행",
                  command=self.run_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(solve_buttons_frame, text="💾 저장",
                  command=self.save_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(solve_buttons_frame, text="📂 불러오기",
                  command=self.load_code).pack(side=tk.LEFT)

        # 통계 섹션
        stats_frame = ttk.LabelFrame(right_panel, text="📊 학습 통계", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # 통계 정보
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)

        stats_text_frame = ttk.Frame(stats_frame)
        stats_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 통계 버튼들
        stats_buttons_frame = ttk.Frame(stats_frame)
        stats_buttons_frame.pack(fill=tk.X)

        ttk.Button(stats_buttons_frame, text="🔄 새로고침",
                  command=self.refresh_stats).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(stats_buttons_frame, text="📈 상세 통계",
                  command=self.show_detailed_stats).pack(side=tk.LEFT)

        # 이벤트 바인딩
        self.recommendations_tree.bind('<<TreeviewSelect>>', self.on_problem_select)

        # 초기 상태 표시
        if not ALGORITHM_MODULES_LOADED:
            self._show_error_message("알고리즘 모듈을 로드할 수 없습니다.\nResources 폴더의 모듈을 확인해주세요.")

    def _show_error_message(self, message):
        """오류 메시지 표시"""
        error_label = ttk.Label(self.frame, text=message,
                              font=('Helvetica', 12), foreground='red')
        error_label.pack(pady=50)

    def _init_algorithm_system(self):
        """알고리즘 시스템 초기화"""
        try:
            if ALGORITHM_MODULES_LOADED:
                # MockProblemProvider 초기화
                self.problem_provider = MockProblemProvider()

                # UserProgressTracker 초기화
                self.user_progress = UserProgressTracker("focus_timer_user")

                # AdvancedChallengeSystem 초기화
                self.challenge_system = AdvancedChallengeSystem(
                    "focus_timer_user", self.problem_provider
                )

                self.algorithm_system_ready = True
                print("✅ 알고리즘 시스템 초기화 성공")

                # 초기 데이터 로드
                self.refresh_recommendations()
                self.refresh_challenges()
                self.refresh_stats()
            else:
                self.algorithm_system_ready = False
                print("❌ 알고리즘 모듈이 로드되지 않았습니다.")

        except Exception as e:
            self.algorithm_system_ready = False
            print(f"❌ 알고리즘 시스템 초기화 실패: {e}")

    def refresh_recommendations(self):
        """추천 문제 새로고침"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        try:
            # 기존 항목 삭제
            for item in self.recommendations_tree.get_children():
                self.recommendations_tree.delete(item)

            # 추천 문제 가져오기
            recommendations = self.challenge_system.get_personalized_recommendations(5)

            for problem in recommendations:
                tags_str = ', '.join([tag.name for tag in list(problem.tags)[:3]])
                self.recommendations_tree.insert('', 'end', values=(
                    problem.title,
                    problem.difficulty.name,
                    tags_str
                ), tags=(problem.id,))

        except Exception as e:
            print(f"❌ 추천 문제 새로고침 실패: {e}")
            messagebox.showerror("오류", f"추천 문제 로드 실패: {e}")

    def refresh_challenges(self):
        """챌린지 새로고침"""
        if not self.algorithm_system_ready:
            return

        try:
            # 기존 항목 삭제
            for item in self.challenges_tree.get_children():
                self.challenges_tree.delete(item)

            # 활성 챌린지 가져오기
            active_challenges = self.challenge_system.get_active_challenges()

            for challenge in active_challenges:
                progress = challenge.get_progress_percentage()
                remaining = challenge.get_remaining_days()
                self.challenges_tree.insert('', 'end', values=(
                    challenge.name,
                    f"{progress:.1f}%",
                    f"{remaining}일"
                ), tags=(challenge.challenge_id,))

        except Exception as e:
            print(f"❌ 챌린지 새로고침 실패: {e}")

    def refresh_stats(self):
        """통계 새로고침"""
        if not self.algorithm_system_ready:
            return

        try:
            stats = self.challenge_system.get_user_statistics()

            stats_text = f"""📊 학습 통계

🎯 사용자 레벨: {stats['user_level']}
✅ 해결한 문제: {stats['total_problems_solved']}개
📈 성공률: {stats['success_rate']:.1%}
🔥 현재 연속 해결: {stats['current_streak']}일
🏆 최장 연속 해결: {stats['longest_streak']}일

📚 난이도별 해결:
• 쉬움: {stats['easy_solved']}개
• 보통: {stats['medium_solved']}개
• 어려움: {stats['hard_solved']}개
• 전문가: {stats['expert_solved']}개

🎯 추천 난이도: {stats['recommended_difficulty'].name}
"""

            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)

        except Exception as e:
            print(f"❌ 통계 새로고침 실패: {e}")

    def create_daily_challenge(self):
        """일일 챌린지 생성"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        try:
            challenge = self.challenge_system.create_daily_challenge()
            messagebox.showinfo("일일 챌린지",
                              f"새로운 일일 챌린지가 생성되었습니다!\n\n"
                              f"제목: {challenge.name}\n"
                              f"설명: {challenge.description}\n"
                              f"목표: {challenge.target_problems}문제\n"
                              f"보상: {challenge.reward_points}포인트")
            self.refresh_challenges()

        except Exception as e:
            print(f"❌ 일일 챌린지 생성 실패: {e}")
            messagebox.showerror("오류", f"일일 챌린지 생성 실패: {e}")

    def create_weekly_challenge(self):
        """주간 챌린지 생성"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        try:
            challenge = self.challenge_system.create_weekly_challenge()
            messagebox.showinfo("주간 챌린지",
                              f"새로운 주간 챌린지가 생성되었습니다!\n\n"
                              f"제목: {challenge.name}\n"
                              f"설명: {challenge.description}\n"
                              f"목표: {challenge.target_problems}문제\n"
                              f"보상: {challenge.reward_points}포인트")
            self.refresh_challenges()

        except Exception as e:
            print(f"❌ 주간 챌린지 생성 실패: {e}")
            messagebox.showerror("오류", f"주간 챌린지 생성 실패: {e}")

    def create_custom_challenge(self):
        """커스텀 챌린지 생성"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        # 커스텀 챌린지 다이얼로그
        dialog = tk.Toplevel(self.frame)
        dialog.title("커스텀 챌린지 생성")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()

        # 입력 필드들
        ttk.Label(dialog, text="챌린지 이름:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(dialog, text="설명:").pack(anchor=tk.W, padx=10, pady=(0, 5))
        desc_text = tk.Text(dialog, height=3, wrap=tk.WORD)
        desc_text.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(dialog, text="목표 문제 수:").pack(anchor=tk.W, padx=10, pady=(0, 5))
        target_var = tk.StringVar(value="5")
        target_entry = ttk.Entry(dialog, textvariable=target_var, width=10)
        target_entry.pack(anchor=tk.W, padx=10, pady=(0, 10))

        ttk.Label(dialog, text="기간 (일):").pack(anchor=tk.W, padx=10, pady=(0, 5))
        days_var = tk.StringVar(value="7")
        days_entry = ttk.Entry(dialog, textvariable=days_var, width=10)
        days_entry.pack(anchor=tk.W, padx=10, pady=(0, 10))

        def create_challenge():
            try:
                name = name_entry.get().strip()
                description = desc_text.get(1.0, tk.END).strip()
                target_problems = int(target_var.get())
                days = int(days_var.get())

                if not name or not description:
                    messagebox.showwarning("경고", "이름과 설명을 입력해주세요.")
                    return

                challenge = self.challenge_system.create_custom_challenge(
                    name=name,
                    description=description,
                    target_difficulty=self.challenge_system.get_next_recommended_difficulty(),
                    target_problems=target_problems,
                    time_limit_days=days
                )

                messagebox.showinfo("성공", f"커스텀 챌린지가 생성되었습니다!\n보상: {challenge.reward_points}포인트")
                dialog.destroy()
                self.refresh_challenges()

            except ValueError:
                messagebox.showerror("오류", "숫자를 올바르게 입력해주세요.")
            except Exception as e:
                print(f"❌ 커스텀 챌린지 생성 실패: {e}")
                messagebox.showerror("오류", f"챌린지 생성 실패: {e}")

        # 버튼들
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="생성", command=create_challenge).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(side=tk.RIGHT)

    def run_code(self):
        """코드 실행"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        # 선택된 문제 확인
        selected_items = self.recommendations_tree.selection()
        if not selected_items:
            messagebox.showwarning("경고", "문제를 선택해주세요.")
            return

        problem_id = self.recommendations_tree.item(selected_items[0], 'tags')[0]
        code = self.code_text.get(1.0, tk.END).strip()

        if not code:
            messagebox.showwarning("경고", "코드를 입력해주세요.")
            return

        try:
            # 문제 정보 가져오기
            problem = self.problem_provider.get_problem_by_id(problem_id)

            # 테스트 케이스 준비
            test_cases = []
            for tc in problem.test_cases:
                test_cases.append({
                    'input': tc.input_data,
                    'output': tc.expected_output
                })

            # 코드 실행
            is_correct, test_results, performance = self.challenge_system.submit_solution(
                problem_id, code, "python", test_cases
            )

            # 결과 표시
            result_message = f"실행 결과:\n\n"
            result_message += f"정답 여부: {'✅ 정답' if is_correct else '❌ 오답'}\n"
            result_message += f"테스트 통과: {performance.passed_test_cases}/{performance.total_test_cases}\n"
            result_message += f"성공률: {performance.calculate_success_rate():.1%}\n"
            result_message += f"평균 실행 시간: {performance.average_execution_time:.4f}초\n"
            result_message += f"코드 품질 점수: {performance.code_quality_score:.1f}/100"

            if is_correct:
                messagebox.showinfo("성공!", result_message)
                self.refresh_stats()
                self.refresh_challenges()
            else:
                # 실패한 테스트 케이스 상세 정보
                failed_cases = [r for r in test_results if not r.is_passed]
                if failed_cases:
                    result_message += "\n\n실패한 테스트 케이스:"
                    for i, case in enumerate(failed_cases[:3], 1):
                        result_message += f"\n{i}. 입력: {case.input_data}"
                        result_message += f"\n   기대: {case.expected_output}"
                        result_message += f"\n   실제: {case.actual_output}"
                        if case.error_message:
                            result_message += f"\n   오류: {case.error_message}"

                messagebox.showwarning("실패", result_message)

        except Exception as e:
            print(f"❌ 코드 실행 실패: {e}")
            messagebox.showerror("오류", f"코드 실행 실패: {e}")

    def save_code(self):
        """코드 저장"""
        code = self.code_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("경고", "저장할 코드가 없습니다.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("성공", "코드가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"코드 저장 실패: {e}")

    def load_code(self):
        """코드 불러오기"""
        filename = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(1.0, code)
                messagebox.showinfo("성공", "코드가 불러와졌습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"코드 불러오기 실패: {e}")

    def show_detailed_stats(self):
        """상세 통계 표시"""
        if not self.algorithm_system_ready:
            messagebox.showwarning("경고", "알고리즘 시스템이 초기화되지 않았습니다.")
            return

        try:
            # 약점/강점 분석
            weak_areas = self.challenge_system.get_weak_areas(5)
            strong_areas = self.challenge_system.get_strong_areas(5)

            stats_text = "📈 상세 학습 분석\n\n"

            stats_text += "📉 약점 영역:\n"
            for tag, count in weak_areas:
                stats_text += f"• {tag}: {count}문제 해결\n"

            stats_text += "\n📈 강점 영역:\n"
            for tag, count in strong_areas:
                stats_text += f"• {tag}: {count}문제 해결\n"

            # 최근 활동
            recent_activity = self.challenge_system.get_recent_activity(7)
            if recent_activity:
                stats_text += f"\n📅 최근 7일 활동:\n"
                for submission in recent_activity[:5]:
                    status_emoji = "✅" if submission.status.name == "CORRECT" else "❌"
                    stats_text += f"• {status_emoji} {submission.submission_time.strftime('%m-%d %H:%M')}\n"

            messagebox.showinfo("상세 통계", stats_text)

        except Exception as e:
            print(f"❌ 상세 통계 표시 실패: {e}")
            messagebox.showerror("오류", f"상세 통계 표시 실패: {e}")

    def on_problem_select(self, event):
        """문제 선택 시 호출"""
        if not self.algorithm_system_ready:
            return

        selected_items = self.recommendations_tree.selection()
        if not selected_items:
            return

        try:
            problem_id = self.recommendations_tree.item(selected_items[0], 'tags')[0]
            problem = self.problem_provider.get_problem_by_id(problem_id)

            # 문제 정보 표시
            self.problem_title_label.config(text=problem.title)
            self.problem_description_text.delete(1.0, tk.END)
            self.problem_description_text.insert(1.0, problem.description)

            # 기본 코드 템플릿 제공
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, f"""# {problem.title}
# 난이도: {problem.difficulty.name}
# 태그: {', '.join([tag.name for tag in problem.tags])}

def solve():
    # 여기에 해결 코드를 작성하세요
    pass

if __name__ == "__main__":
    solve()
""")

        except Exception as e:
            print(f"❌ 문제 선택 처리 실패: {e}")