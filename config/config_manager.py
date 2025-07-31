#!/usr/bin/env python3
"""
설정 관리 클래스
JSON 설정 파일을 읽고 쓰는 기능을 제공합니다.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ 설정 파일 로드 완료: {self.config_file}")
            else:
                print(f"⚠️ 설정 파일이 없습니다: {self.config_file}")
                self.create_default_config()
        except Exception as e:
            print(f"❌ 설정 파일 로드 실패: {e}")
            self.create_default_config()

        return self.config

    def save_config(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ 설정 파일 저장 완료: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False

    def create_default_config(self):
        """기본 설정 생성"""
        self.config = {
            "app_info": {
                "name": "Focus Timer Enterprise GUI",
                "version": "2.0.0",
                "description": "상업용 집중 모드 시스템"
            },
            "system_paths": {
                "hosts_file": "/etc/hosts",
                "redirect_ip": "127.0.0.1",
                "backup_path": "/Library/Application Support/FocusTimer/hosts_backup",
                "state_path": "/Library/Application Support/FocusTimer/state.json",
                "lock_file": "/Library/Application Support/FocusTimer/focus_timer.lock",
                "log_path": "/var/log/FocusTimer/focus_timer.log",
                "pid_file": "/var/run/focus_timer.pid"
            },
            "blocked_websites": {
                "youtube": [
                    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"
                ],
                "social_media": [
                    "facebook.com", "www.facebook.com", "instagram.com", "www.instagram.com"
                ]
            },
            "focus_mode": {
                "default_start_time": "09:00",
                "default_end_time": "18:00",
                "default_difficulty": 1,
                "max_difficulty": 5,
                "max_attempts": 3
            },
            "security": {
                "enable_system_protection": True,
                "enable_file_monitoring": True,
                "enable_dns_cache_flush": True
            },
            "gui_settings": {
                "window_size": {"width": 800, "height": 600},
                "theme": "clam",
                "auto_refresh_interval": 5
            }
        }
        self.save_config()

    def get(self, key: str, default: Any = None) -> Any:
        """설정값 가져오기 (점 표기법 지원)"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """설정값 설정 (점 표기법 지원)"""
        try:
            keys = key.split('.')
            config = self.config

            # 마지막 키까지 탐색
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # 마지막 키에 값 설정
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"❌ 설정값 설정 실패: {e}")
            return False

    def get_blocked_websites(self) -> List[str]:
        """차단할 웹사이트 목록 가져오기"""
        websites = []
        blocked_sites = self.get('blocked_websites', {})

        for category, sites in blocked_sites.items():
            websites.extend(sites)

        return websites

    def get_system_path(self, path_name: str) -> str:
        """시스템 경로 가져오기"""
        return self.get(f'system_paths.{path_name}', '')

    def get_focus_mode_setting(self, setting_name: str, default: Any = None) -> Any:
        """집중 모드 설정 가져오기"""
        return self.get(f'focus_mode.{setting_name}', default)

    def get_security_setting(self, setting_name: str, default: bool = False) -> bool:
        """보안 설정 가져오기"""
        return self.get(f'security.{setting_name}', default)

    def get_gui_setting(self, setting_name: str, default: Any = None) -> Any:
        """GUI 설정 가져오기"""
        return self.get(f'gui_settings.{setting_name}', default)

    def update_blocked_websites(self, category: str, websites: List[str]) -> bool:
        """차단할 웹사이트 업데이트"""
        return self.set(f'blocked_websites.{category}', websites)

    def add_blocked_website(self, category: str, website: str) -> bool:
        """차단할 웹사이트 추가"""
        current_sites = self.get(f'blocked_websites.{category}', [])
        if website not in current_sites:
            current_sites.append(website)
            return self.set(f'blocked_websites.{category}', current_sites)
        return True

    def remove_blocked_website(self, category: str, website: str) -> bool:
        """차단할 웹사이트 제거"""
        current_sites = self.get(f'blocked_websites.{category}', [])
        if website in current_sites:
            current_sites.remove(website)
            return self.set(f'blocked_websites.{category}', current_sites)
        return True

    def get_algorithm_challenge_config(self, difficulty: int) -> Dict[str, Any]:
        """알고리즘 문제 설정 가져오기"""
        return self.get(f'algorithm_challenges.difficulty_{difficulty}', {})

    def validate_config(self) -> List[str]:
        """설정 유효성 검사"""
        errors = []

        # 필수 설정 확인
        required_paths = ['hosts_file', 'state_path', 'log_path']
        for path_name in required_paths:
            if not self.get_system_path(path_name):
                errors.append(f"필수 시스템 경로가 없습니다: {path_name}")

        # 집중 모드 설정 확인
        if not self.get_focus_mode_setting('default_start_time'):
            errors.append("기본 시작 시간이 설정되지 않았습니다")

        if not self.get_focus_mode_setting('default_end_time'):
            errors.append("기본 종료 시간이 설정되지 않았습니다")

        return errors

    def export_config(self, export_path: str) -> bool:
        """설정 내보내기"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ 설정 내보내기 완료: {export_path}")
            return True
        except Exception as e:
            print(f"❌ 설정 내보내기 실패: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """설정 가져오기"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)

            # 기존 설정과 병합
            self.merge_configs(self.config, new_config)
            self.save_config()
            print(f"✅ 설정 가져오기 완료: {import_path}")
            return True
        except Exception as e:
            print(f"❌ 설정 가져오기 실패: {e}")
            return False

    def merge_configs(self, base_config: Dict, new_config: Dict):
        """설정 병합"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self.merge_configs(base_config[key], value)
            else:
                base_config[key] = value

    def reset_to_defaults(self) -> bool:
        """기본 설정으로 초기화"""
        try:
            self.create_default_config()
            print("✅ 기본 설정으로 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ 기본 설정 초기화 실패: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """설정 요약 정보"""
        return {
            "app_name": self.get('app_info.name'),
            "version": self.get('app_info.version'),
            "blocked_websites_count": len(self.get_blocked_websites()),
            "focus_mode_enabled": self.get('focus_mode.default_start_time') is not None,
            "security_features": [
                key for key, value in self.get('security', {}).items()
                if value is True
            ],
            "gui_theme": self.get('gui_settings.theme'),
            "window_size": self.get('gui_settings.window_size')
        }

# 사용 예시
if __name__ == "__main__":
    config = ConfigManager()

    # 설정값 가져오기
    print("앱 이름:", config.get('app_info.name'))
    print("차단할 웹사이트:", config.get_blocked_websites())

    # 설정값 변경
    config.set('focus_mode.default_start_time', '08:00')
    config.save_config()

    # 설정 요약
    print("설정 요약:", config.get_config_summary())