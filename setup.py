"""
Setup script for MarkdownForge-Pro
"""

from setuptools import setup, find_packages

setup(
    name="markdownforge-pro",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
