"""
FocusTimer Resources Package Setup
알고리즘 시스템 및 기타 리소스 모듈들을 Python 패키지로 설치
"""

from setuptools import setup, find_packages
from pathlib import Path

# 패키지 정보
PACKAGE_NAME = "focustimer_resources"
VERSION = "1.0.0"
DESCRIPTION = "FocusTimer.app Resources Package - Algorithm System and Utilities"
AUTHOR = "FocusTimer Team"

# 패키지 루트 디렉토리
PACKAGE_ROOT = Path(__file__).parent

# 패키지 설정
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    packages=find_packages(),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        'tkinter',  # GUI (일반적으로 Python에 포함됨)
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)

if __name__ == "__main__":
    print("📦 FocusTimer Resources 패키지 설치 중...")
    print(f"📁 패키지 루트: {PACKAGE_ROOT}")
    print(f"📋 패키지 이름: {PACKAGE_NAME}")
    print(f"📋 버전: {VERSION}")