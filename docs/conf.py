"""Sphinx configuration for Foundry documentation."""

from __future__ import annotations

import importlib
import inspect
import os
import sys
import ast
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DOCS_HOME = Path(os.environ.get("FOUNDRY_DOCS_HOME", "/tmp/foundry-docs-home"))
os.environ["HOME"] = str(DOCS_HOME)

project = "Foundry"
author = "Foundry contributors"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

autosummary_generate = True
autodoc_typehints = "none"
autodoc_typehints_format = "fully-qualified"
napoleon_google_docstring = False
napoleon_numpy_docstring = True
suppress_warnings = ["ref.python", "config.cache"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "description": "Guides and references for using, understanding, and extending SMB3 Foundry.",
    "fixed_sidebar": True,
    "show_powered_by": False,
    "page_width": "1180px",
    "sidebar_width": "260px",
    "font_family": "Inter, Segoe UI, system-ui, -apple-system, sans-serif",
    "head_font_family": "Inter, Segoe UI, system-ui, -apple-system, sans-serif",
    "code_font_family": "JetBrains Mono, SFMono-Regular, Consolas, monospace",
}
master_doc = "index"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

FRAMEWORK_ATTRIBUTE_NAMES = {
    "staticMetaObject",
}


def _resolve_dotted_object(fullname: str) -> object | None:
    """Resolve a dotted object name for Sphinx template helpers."""
    parts = fullname.split(".")
    for index in range(len(parts) - 1, 0, -1):
        module_name = ".".join(parts[:index])
        object_path = parts[index:]
        try:
            obj: object = importlib.import_module(module_name)
        except Exception:
            continue
        try:
            for attr in object_path:
                obj = getattr(obj, attr)
        except AttributeError:
            return None
        return obj
    return None


def _numpy_attributes(docstring: str | None) -> dict[str, str]:
    """Return attributes documented in a NumPy-style Attributes section."""
    if not docstring:
        return {}

    lines = inspect.cleandoc(docstring).splitlines()
    attributes: dict[str, list[str]] = {}
    in_attributes = False
    current_name: str | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""

        if stripped == "Attributes" and set(next_line) == {"-"}:
            in_attributes = True
            current_name = None
            continue

        if in_attributes and stripped in {
            "Parameters",
            "Returns",
            "Yields",
            "Raises",
            "Notes",
            "See Also",
            "Examples",
        }:
            break

        if not in_attributes or not stripped or set(stripped) == {"-"}:
            continue

        if not line.startswith((" ", "\t")):
            current_name = stripped.split(":", 1)[0].strip()
            attributes.setdefault(current_name, [])
            continue

        if current_name is not None:
            attributes[current_name].append(stripped)

    return {name: " ".join(parts).strip() for name, parts in attributes.items() if " ".join(parts).strip()}


def _source_class_docstring(obj: object) -> str | None:
    """Return a class docstring from source when runtime wrappers replace it."""
    if not inspect.isclass(obj):
        return None

    try:
        source_path = inspect.getsourcefile(obj)
    except TypeError:
        source_path = None
    if source_path is None:
        return None

    try:
        tree = ast.parse(Path(source_path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == obj.__name__:
            return ast.get_docstring(node, clean=True)
    return None


def _project_docstring(fullname: str) -> str | None:
    """Return the project-authored docstring for a generated API object."""
    obj = _resolve_dotted_object(fullname)
    if obj is None:
        return None
    return _source_class_docstring(obj) or inspect.getdoc(obj)


def documented_attributes(attributes: Iterable[str], fullname: str, inherited_members: Iterable[str]) -> list[str]:
    """Return class attributes that have project-owned documentation."""
    inherited = set(inherited_members)
    descriptions = _numpy_attributes(_project_docstring(fullname))

    return [
        attribute
        for attribute in attributes
        if attribute not in inherited
        and attribute not in FRAMEWORK_ATTRIBUTE_NAMES
        and attribute in descriptions
    ]


def attribute_summary(attribute: str, fullname: str) -> str:
    """Return the rendered summary for a documented class attribute."""
    descriptions = _numpy_attributes(_project_docstring(fullname))
    return descriptions.get(attribute, "")


autosummary_context = {
    "documented_attributes": documented_attributes,
    "attribute_summary": attribute_summary,
}
