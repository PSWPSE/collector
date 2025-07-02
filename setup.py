from setuptools import setup, find_namespace_packages

setup(
    name="collector",
    version="0.1",
    packages=find_namespace_packages(include=["collector", "collector.*"]),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "requests",
    ],
) 