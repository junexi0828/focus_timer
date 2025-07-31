#!/usr/bin/env python3
"""
설정 관리 GUI
JSON 설정 파일을 GUI로 편집할 수 있는 도구입니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from config_manager import ConfigManager

class ConfigGUI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.root = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        """GUI 설정"""
        self.root.title("Focus Timer Enterprise - 설정 관리")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목
        title_label = ttk.Label(main_frame, text="⚙️ 설정 관리",
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 노트북 (탭) 생성
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 탭 생성
        self.create_general_tab()
        self.create_websites_tab()
        self.create_focus_mode_tab()
        self.create_security_tab()
        self.create_gui_tab()
        self.create_advanced_tab()

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        # 버튼들
        ttk.Button(button_frame, text="💾 저장", command=self.save_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 새로고침", command=self.refresh_config).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="📤 내보내기", command=self.export_config).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="📥 가져오기", command=self.import_config).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 기본값으로 초기화", command=self.reset_to_defaults).grid(row=0, column=4, padx=(0, 10))
        ttk.Button(button_frame, text="❌ 닫기", command=self.root.destroy).grid(row=0, column=5)

        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def create_general_tab(self):
        """일반 설정 탭"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="일반")

        # 앱 정보
        app_frame = ttk.LabelFrame(general_frame, text="앱 정보", padding="10")
        app_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(app_frame, text="앱 이름:").grid(row=0, column=0, sticky=tk.W)
        self.app_name_var = tk.StringVar(value=self.config_manager.get('app_info.name', ''))
        ttk.Entry(app_frame, textvariable=self.app_name_var, width=30).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        ttk.Label(app_frame, text="버전:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.version_var = tk.StringVar(value=self.config_manager.get('app_info.version', ''))
        ttk.Entry(app_frame, textvariable=self.version_var, width=30).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # 시스템 경로
        paths_frame = ttk.LabelFrame(general_frame, text="시스템 경로", padding="10")
        paths_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        paths = [
            ("hosts_file", "Hosts 파일:"),
            ("state_path", "상태 파일:"),
            ("log_path", "로그 파일:"),
            ("backup_path", "백업 경로:")
        ]

        for i, (key, label) in enumerate(paths):
            ttk.Label(paths_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            var = tk.StringVar(value=self.config_manager.get_system_path(key))
            setattr(self, f"{key}_var", var)
            ttk.Entry(paths_frame, textvariable=var, width=50).grid(row=i, column=1, padx=(10, 0), sticky=tk.W)

    def create_websites_tab(self):
        """웹사이트 설정 탭"""
        websites_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(websites_frame, text="웹사이트")

        # 카테고리별 웹사이트 관리
        categories = ["youtube", "social_media", "gaming", "entertainment"]
        category_names = ["YouTube", "소셜 미디어", "게임", "엔터테인먼트"]

        for i, (category, name) in enumerate(zip(categories, category_names)):
            cat_frame = ttk.LabelFrame(websites_frame, text=name, padding="10")
            cat_frame.grid(row=i//2, column=i%2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10), pady=(0, 10))

            # 웹사이트 목록
            sites = self.config_manager.get(f'blocked_websites.{category}', [])
            sites_text = '\n'.join(sites)

            text_widget = tk.Text(cat_frame, height=8, width=30)
            text_widget.insert('1.0', sites_text)
            text_widget.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

            # 스크롤바
            scrollbar = ttk.Scrollbar(cat_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))

            setattr(self, f"{category}_text", text_widget)

        # 그리드 가중치
        websites_frame.columnconfigure(0, weight=1)
        websites_frame.columnconfigure(1, weight=1)

    def create_focus_mode_tab(self):
        """집중 모드 설정 탭"""
        focus_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(focus_frame, text="집중 모드")

        # 기본 시간 설정
        time_frame = ttk.LabelFrame(focus_frame, text="기본 시간 설정", padding="10")
        time_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(time_frame, text="기본 시작 시간:").grid(row=0, column=0, sticky=tk.W)
        self.default_start_time_var = tk.StringVar(value=self.config_manager.get_focus_mode_setting('default_start_time', '09:00'))
        ttk.Entry(time_frame, textvariable=self.default_start_time_var, width=10).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        ttk.Label(time_frame, text="기본 종료 시간:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.default_end_time_var = tk.StringVar(value=self.config_manager.get_focus_mode_setting('default_end_time', '18:00'))
        ttk.Entry(time_frame, textvariable=self.default_end_time_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # 난이도 설정
        difficulty_frame = ttk.LabelFrame(focus_frame, text="알고리즘 문제 설정", padding="10")
        difficulty_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(difficulty_frame, text="기본 난이도:").grid(row=0, column=0, sticky=tk.W)
        self.default_difficulty_var = tk.IntVar(value=self.config_manager.get_focus_mode_setting('default_difficulty', 1))
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.default_difficulty_var,
                                       values=[1, 2, 3, 4, 5], width=10, state="readonly")
        difficulty_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        ttk.Label(difficulty_frame, text="최대 시도 횟수:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.max_attempts_var = tk.IntVar(value=self.config_manager.get_focus_mode_setting('max_attempts', 3))
        ttk.Entry(difficulty_frame, textvariable=self.max_attempts_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # 추가 설정
        options_frame = ttk.LabelFrame(focus_frame, text="추가 설정", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.auto_restart_browser_var = tk.BooleanVar(value=self.config_manager.get_focus_mode_setting('auto_restart_browser', True))
        ttk.Checkbutton(options_frame, text="집중 모드 시작 시 브라우저 자동 재시작",
                       variable=self.auto_restart_browser_var).grid(row=0, column=0, sticky=tk.W)

        self.force_browser_restart_var = tk.BooleanVar(value=self.config_manager.get_focus_mode_setting('force_browser_restart', True))
        ttk.Checkbutton(options_frame, text="브라우저 강제 재시작",
                       variable=self.force_browser_restart_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

    def create_security_tab(self):
        """보안 설정 탭"""
        security_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(security_frame, text="보안")

        # 보안 기능 설정
        features_frame = ttk.LabelFrame(security_frame, text="보안 기능", padding="10")
        features_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        security_options = [
            ("enable_system_protection", "시스템 레벨 보호"),
            ("enable_file_monitoring", "파일 모니터링"),
            ("enable_firewall_rules", "방화벽 규칙"),
            ("enable_dns_cache_flush", "DNS 캐시 초기화"),
            ("enable_browser_cache_clear", "브라우저 캐시 초기화"),
            ("lock_hosts_file", "hosts 파일 잠금"),
            ("monitor_hosts_changes", "hosts 파일 변경 감지")
        ]

        for i, (key, label) in enumerate(security_options):
            var = tk.BooleanVar(value=self.config_manager.get_security_setting(key))
            setattr(self, f"{key}_var", var)
            ttk.Checkbutton(features_frame, text=label, variable=var).grid(row=i, column=0, sticky=tk.W)

    def create_gui_tab(self):
        """GUI 설정 탭"""
        gui_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(gui_frame, text="GUI")

        # 창 크기 설정
        window_frame = ttk.LabelFrame(gui_frame, text="창 크기", padding="10")
        window_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(window_frame, text="너비:").grid(row=0, column=0, sticky=tk.W)
        self.window_width_var = tk.IntVar(value=self.config_manager.get_gui_setting('window_size', {}).get('width', 800))
        ttk.Entry(window_frame, textvariable=self.window_width_var, width=10).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        ttk.Label(window_frame, text="높이:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.window_height_var = tk.IntVar(value=self.config_manager.get_gui_setting('window_size', {}).get('height', 600))
        ttk.Entry(window_frame, textvariable=self.window_height_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # 테마 설정
        theme_frame = ttk.LabelFrame(gui_frame, text="테마", padding="10")
        theme_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(theme_frame, text="테마:").grid(row=0, column=0, sticky=tk.W)
        self.theme_var = tk.StringVar(value=self.config_manager.get_gui_setting('theme', 'clam'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                  values=['clam', 'alt', 'default', 'classic'], width=15, state="readonly")
        theme_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        # 자동 새로고침
        refresh_frame = ttk.LabelFrame(gui_frame, text="자동 새로고침", padding="10")
        refresh_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        ttk.Label(refresh_frame, text="새로고침 간격 (초):").grid(row=0, column=0, sticky=tk.W)
        self.refresh_interval_var = tk.IntVar(value=self.config_manager.get_gui_setting('auto_refresh_interval', 5))
        ttk.Entry(refresh_frame, textvariable=self.refresh_interval_var, width=10).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        ttk.Label(refresh_frame, text="로그 표시 줄 수:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.log_lines_var = tk.IntVar(value=self.config_manager.get_gui_setting('log_lines_to_show', 20))
        ttk.Entry(refresh_frame, textvariable=self.log_lines_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

    def create_advanced_tab(self):
        """고급 설정 탭"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="고급")

        # 로깅 설정
        logging_frame = ttk.LabelFrame(advanced_frame, text="로깅 설정", padding="10")
        logging_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(logging_frame, text="로그 레벨:").grid(row=0, column=0, sticky=tk.W)
        self.log_level_var = tk.StringVar(value=self.config_manager.get('logging.log_level', 'INFO'))
        log_level_combo = ttk.Combobox(logging_frame, textvariable=self.log_level_var,
                                      values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], width=15, state="readonly")
        log_level_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)

        self.log_to_file_var = tk.BooleanVar(value=self.config_manager.get('logging.log_to_file', True))
        ttk.Checkbutton(logging_frame, text="파일에 로그 저장", variable=self.log_to_file_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        self.log_to_console_var = tk.BooleanVar(value=self.config_manager.get('logging.log_to_console', True))
        ttk.Checkbutton(logging_frame, text="콘솔에 로그 출력", variable=self.log_to_console_var).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        ttk.Label(logging_frame, text="최대 로그 크기 (MB):").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.max_log_size_var = tk.IntVar(value=self.config_manager.get('logging.max_log_size_mb', 10))
        ttk.Entry(logging_frame, textvariable=self.max_log_size_var, width=10).grid(row=3, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # 설정 검증
        validation_frame = ttk.LabelFrame(advanced_frame, text="설정 검증", padding="10")
        validation_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        ttk.Button(validation_frame, text="🔍 설정 유효성 검사", command=self.validate_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(validation_frame, text="📊 설정 요약 보기", command=self.show_config_summary).grid(row=0, column=1)

    def save_config(self):
        """설정 저장"""
        try:
            # 일반 설정
            self.config_manager.set('app_info.name', self.app_name_var.get())
            self.config_manager.set('app_info.version', self.version_var.get())

            # 시스템 경로
            self.config_manager.set('system_paths.hosts_file', self.hosts_file_var.get())
            self.config_manager.set('system_paths.state_path', self.state_path_var.get())
            self.config_manager.set('system_paths.log_path', self.log_path_var.get())
            self.config_manager.set('system_paths.backup_path', self.backup_path_var.get())

            # 웹사이트 설정
            categories = ["youtube", "social_media", "gaming", "entertainment"]
            for category in categories:
                text_widget = getattr(self, f"{category}_text")
                sites = text_widget.get('1.0', tk.END).strip().split('\n')
                sites = [site.strip() for site in sites if site.strip()]
                self.config_manager.set(f'blocked_websites.{category}', sites)

            # 집중 모드 설정
            self.config_manager.set('focus_mode.default_start_time', self.default_start_time_var.get())
            self.config_manager.set('focus_mode.default_end_time', self.default_end_time_var.get())
            self.config_manager.set('focus_mode.default_difficulty', self.default_difficulty_var.get())
            self.config_manager.set('focus_mode.max_attempts', self.max_attempts_var.get())
            self.config_manager.set('focus_mode.auto_restart_browser', self.auto_restart_browser_var.get())
            self.config_manager.set('focus_mode.force_browser_restart', self.force_browser_restart_var.get())

            # 보안 설정
            security_options = [
                "enable_system_protection", "enable_file_monitoring", "enable_firewall_rules",
                "enable_dns_cache_flush", "enable_browser_cache_clear", "lock_hosts_file",
                "monitor_hosts_changes"
            ]
            for option in security_options:
                var = getattr(self, f"{option}_var")
                self.config_manager.set(f'security.{option}', var.get())

            # GUI 설정
            self.config_manager.set('gui_settings.window_size.width', self.window_width_var.get())
            self.config_manager.set('gui_settings.window_size.height', self.window_height_var.get())
            self.config_manager.set('gui_settings.theme', self.theme_var.get())
            self.config_manager.set('gui_settings.auto_refresh_interval', self.refresh_interval_var.get())
            self.config_manager.set('gui_settings.log_lines_to_show', self.log_lines_var.get())

            # 로깅 설정
            self.config_manager.set('logging.log_level', self.log_level_var.get())
            self.config_manager.set('logging.log_to_file', self.log_to_file_var.get())
            self.config_manager.set('logging.log_to_console', self.log_to_console_var.get())
            self.config_manager.set('logging.max_log_size_mb', self.max_log_size_var.get())

            # 저장
            if self.config_manager.save_config():
                messagebox.showinfo("성공", "설정이 저장되었습니다!")
            else:
                messagebox.showerror("오류", "설정 저장에 실패했습니다!")

        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다:\n{e}")

    def refresh_config(self):
        """설정 새로고침"""
        self.config_manager.load_config()
        messagebox.showinfo("완료", "설정이 새로고침되었습니다!")

    def export_config(self):
        """설정 내보내기"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.config_manager.export_config(file_path):
                messagebox.showinfo("성공", f"설정이 내보내기되었습니다:\n{file_path}")
            else:
                messagebox.showerror("오류", "설정 내보내기에 실패했습니다!")

    def import_config(self):
        """설정 가져오기"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.config_manager.import_config(file_path):
                messagebox.showinfo("성공", f"설정이 가져와졌습니다:\n{file_path}")
                self.refresh_config()
            else:
                messagebox.showerror("오류", "설정 가져오기에 실패했습니다!")

    def reset_to_defaults(self):
        """기본값으로 초기화"""
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 초기화하시겠습니까?"):
            if self.config_manager.reset_to_defaults():
                messagebox.showinfo("성공", "설정이 기본값으로 초기화되었습니다!")
                self.refresh_config()
            else:
                messagebox.showerror("오류", "설정 초기화에 실패했습니다!")

    def validate_config(self):
        """설정 유효성 검사"""
        errors = self.config_manager.validate_config()
        if errors:
            error_text = "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("설정 오류", f"다음 설정에 문제가 있습니다:\n\n{error_text}")
        else:
            messagebox.showinfo("검증 완료", "모든 설정이 유효합니다!")

    def show_config_summary(self):
        """설정 요약 보기"""
        summary = self.config_manager.get_config_summary()
        summary_text = f"""
앱 이름: {summary['app_name']}
버전: {summary['version']}
차단할 웹사이트 수: {summary['blocked_websites_count']}
집중 모드 활성화: {'예' if summary['focus_mode_enabled'] else '아니오'}
보안 기능: {', '.join(summary['security_features'])}
GUI 테마: {summary['gui_theme']}
창 크기: {summary['window_size']['width']}x{summary['window_size']['height']}
"""
        messagebox.showinfo("설정 요약", summary_text)

    def run(self):
        """GUI 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ConfigGUI()
    app.run()