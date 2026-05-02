"""Shared helpers for localization product-contract tests."""

import json
import re

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QGroupBox,
    QLabel,
    QTabWidget,
    QTreeWidget,
    QWidget,
)

from foundry import data_dir

FORMAT_FIELD_RE = re.compile(r"\{[^{}]+\}")
PRINTF_TOKEN_RE = re.compile(r"%(?:\([^)]+\))?[#0 +\-]?(?:\d+|\*)?(?:\.\d+)?[bcdeEfFgGnosxX%]")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
ACCELERATOR_RE = re.compile(r"(?<!&)&(?!&)")
SUPPORTED_LOCALES = ("en", "es", "es_ES", "es_419", "it", "de", "fr", "pt_BR", "pt_PT")
TARGET_LOCALES = tuple(locale for locale in SUPPORTED_LOCALES if locale != "en")


def load_test_catalog(locale: str) -> dict[str, dict[str, str]]:
    return json.loads((data_dir / "translations" / f"{locale}.json").read_text(encoding="utf-8"))


def catalog_value(locale: str, context: str, key: str) -> str:
    return load_test_catalog(locale)[context][key]


def assert_structural_tokens_match(source: str, translated: str) -> None:
    assert FORMAT_FIELD_RE.findall(translated) == FORMAT_FIELD_RE.findall(source)
    assert PRINTF_TOKEN_RE.findall(translated) == PRINTF_TOKEN_RE.findall(source)
    assert HTML_TAG_RE.findall(translated) == HTML_TAG_RE.findall(source)

    if ACCELERATOR_RE.search(source):
        assert ACCELERATOR_RE.search(translated)


def _add_visible_text(texts: set[str], text: str) -> None:
    if text:
        texts.add(text)


def _tree_item_texts(item, texts: set[str]) -> None:
    for column in range(item.columnCount()):
        _add_visible_text(texts, item.text(column))
    for index in range(item.childCount()):
        _tree_item_texts(item.child(index), texts)


def visible_widget_texts(widget: QWidget) -> set[str]:
    texts: set[str] = set()
    _add_visible_text(texts, widget.windowTitle())
    _add_visible_text(texts, widget.toolTip())
    _add_visible_text(texts, widget.whatsThis())

    for label in widget.findChildren(QLabel):
        _add_visible_text(texts, label.text())
        _add_visible_text(texts, label.toolTip())
        _add_visible_text(texts, label.whatsThis())
    for button in widget.findChildren(QAbstractButton):
        _add_visible_text(texts, button.text())
        _add_visible_text(texts, button.toolTip())
        _add_visible_text(texts, button.whatsThis())
    for group_box in widget.findChildren(QGroupBox):
        _add_visible_text(texts, group_box.title())
        _add_visible_text(texts, group_box.toolTip())
        _add_visible_text(texts, group_box.whatsThis())
    for combo_box in widget.findChildren(QComboBox):
        for index in range(combo_box.count()):
            _add_visible_text(texts, combo_box.itemText(index))
    for tab_widget in widget.findChildren(QTabWidget):
        for index in range(tab_widget.count()):
            _add_visible_text(texts, tab_widget.tabText(index))
    for tree_widget in widget.findChildren(QTreeWidget):
        for index in range(tree_widget.topLevelItemCount()):
            _tree_item_texts(tree_widget.topLevelItem(index), texts)
    for action in widget.findChildren(QAction):
        _add_visible_text(texts, action.text())
        _add_visible_text(texts, action.toolTip())
        _add_visible_text(texts, action.whatsThis())

    return texts
