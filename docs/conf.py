"""
Documentation configuration file using zenzical.
"""

from typing import List

project = "flashcard-quizzer"
copyright = "2025"
author = "Student"
release = "0.1.0"

extensions: List[str] = []
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
