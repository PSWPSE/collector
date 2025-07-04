from setuptools import setup, find_packages

# requirements.txt에서 의존성 읽기
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# README.md에서 설명 읽기
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="news-collector",
    version="1.0.0",
    author="PSWPSE",
    description="뉴스 기사 수집 및 변환 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PSWPSE/collector",
    # 패키지와 모듈 모두 포함
    packages=find_packages(),
    py_modules=["converter"],  # 루트 디렉토리의 스크립트 파일
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="MIT",  # SPDX 라이선스 표현 방식
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "news-convert=converter_runner:main",
            "news-extract=tools.extractor_runner:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
) 