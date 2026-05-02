"""Validate reachability in the rendered Sphinx HTML tree."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

import pytest

DOCS_HTML = Path(__file__).resolve().parents[2] / "docs" / "_build" / "html"


class LinkParser(HTMLParser):
    """Collect anchors and local IDs from a rendered HTML document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        href = attr_map.get("href")

        if href is not None:
            self.hrefs.append(href)

        for attr_name in ("id", "name"):
            attr_value = attr_map.get(attr_name)
            if attr_value:
                self.ids.add(attr_value)


class AutosummaryTableParser(HTMLParser):
    """Collect rendered autosummary rows by rubric."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_rubric = ""
        self.in_rubric = False
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.text = ""
        self.row: list[str] = []
        self.rows: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "p" and attr_map.get("class") == "rubric":
            self.in_rubric = True
            self.text = ""
        elif tag == "table" and self.current_rubric in {
            "Attributes",
            "Methods",
        }:
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.row = []
        elif self.in_row and tag == "td":
            self.in_cell = True
            self.text = ""

    def handle_data(self, data: str) -> None:
        if self.in_rubric or self.in_cell:
            self.text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.in_rubric:
            self.current_rubric = " ".join(self.text.split())
            self.in_rubric = False
        elif tag == "td" and self.in_cell:
            self.row.append(" ".join(self.text.split()))
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row:
                self.rows.append((self.current_rubric, self.row))
            self.in_row = False
        elif tag == "table" and self.in_table:
            self.in_table = False


def docs_html() -> Path:
    if not DOCS_HTML.exists():
        pytest.fail(f"rendered Sphinx HTML is missing: {DOCS_HTML}")

    return DOCS_HTML


def read_page(relative_path: str) -> str:
    page = docs_html() / relative_path
    if not page.exists():
        pytest.fail(f"representative Sphinx HTML page is missing: {page}")

    return page.read_text(encoding="utf-8")


def parse_page(relative_path: str) -> LinkParser:
    parser = LinkParser()
    parser.feed(read_page(relative_path))
    return parser


def assert_links_to(page: str, expected_hrefs: set[str]) -> None:
    hrefs = set(parse_page(page).hrefs)
    missing = expected_hrefs - hrefs

    assert not missing, f"{page} is missing links: {sorted(missing)}"


def assert_page_contains(page: str, expected_text: set[str]) -> None:
    html = read_page(page)
    missing = {text for text in expected_text if text not in html}

    assert not missing, f"{page} is missing expected content: {sorted(missing)}"


def test_top_level_index_links_to_primary_docs_surfaces() -> None:
    assert_links_to(
        "index.html",
        {
            "api/index.html",
            "subsystems/index.html",
            "user_guide.html",
        },
    )


@pytest.mark.parametrize(
    ("landing_page", "generated_module_pages"),
    [
        (
            "api/foundry_game.html",
            {
                "generated/foundry.game.level.Level.html#module-foundry.game.level.Level",
                "generated/foundry.game.File.html#module-foundry.game.File",
            },
        ),
        (
            "api/smb3parse.html",
            {
                "generated/smb3parse.util.parser.html#module-smb3parse.util.parser",
                "generated/smb3parse.levels.world_map.html#module-smb3parse.levels.world_map",
            },
        ),
        (
            "api/scribe_gui.html",
            {
                "generated/scribe.gui.commands.html#module-scribe.gui.commands",
                "generated/scribe.gui.tool_window.tool_window.html#module-scribe.gui.tool_window.tool_window",
            },
        ),
    ],
)
def test_api_landing_pages_link_to_generated_module_pages(landing_page: str, generated_module_pages: set[str]) -> None:
    assert_links_to(landing_page, generated_module_pages)


@pytest.mark.parametrize(
    ("module_page", "member_pages"),
    [
        (
            "api/generated/smb3parse.util.parser.html",
            {
                "smb3parse.util.parser.gen_levels_in_rom.html#smb3parse.util.parser.gen_levels_in_rom",
                "smb3parse.util.parser.FoundLevel.html#smb3parse.util.parser.FoundLevel",
            },
        ),
        (
            "api/generated/foundry.game.level.Level.html",
            {
                "foundry.game.level.Level.Level.html#foundry.game.level.Level.Level",
                "foundry.game.level.Level.world_and_level_for_level_address.html#foundry.game.level.Level.world_and_level_for_level_address",
            },
        ),
    ],
)
def test_generated_module_pages_link_to_generated_members(module_page: str, member_pages: set[str]) -> None:
    assert_links_to(module_page, member_pages)


@pytest.mark.parametrize(
    ("class_page", "expected_text"),
    [
        (
            "api/generated/foundry.game.level.Level.Level.html",
            {
                '<p class="rubric">Attributes</p>',
                '<p class="rubric">Methods</p>',
                'href="#foundry.game.level.Level.Level.add_object"',
                'href="#foundry.game.level.Level.Level.remove_object"',
                'href="#foundry.game.level.Level.Level.save_to_rom"',
            },
        ),
        (
            "api/generated/smb3parse.util.parser.FoundLevel.html",
            {
                '<p class="rubric">Attributes</p>',
                '<p class="rubric">Methods</p>',
                'href="#smb3parse.util.parser.FoundLevel.level_offset_positions"',
                'href="#smb3parse.util.parser.FoundLevel.to_dict"',
            },
        ),
    ],
)
def test_generated_class_pages_include_public_member_navigation(class_page: str, expected_text: set[str]) -> None:
    assert_page_contains(class_page, expected_text)


def test_rendered_local_html_links_are_reachable() -> None:
    html_root = docs_html()
    generated_pages = sorted(html_root.rglob("*.html"))

    if not generated_pages:
        pytest.fail(f"rendered HTML pages are missing under: {html_root}")

    broken_links: list[str] = []
    ids_by_page: dict[Path, set[str]] = {}

    for page in generated_pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        ids_by_page[page] = parser.ids

        for href in parser.hrefs:
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or parsed.path.startswith("_static/"):
                continue

            target_path, fragment = urldefrag(href)
            if not target_path:
                target_file = page
            else:
                if not target_path.endswith(".html"):
                    continue
                target_file = (page.parent / unquote(target_path)).resolve()

            try:
                target_file.relative_to(html_root)
            except ValueError:
                broken_links.append(f"{page.relative_to(html_root)} -> {href} leaves docs HTML")
                continue

            if not target_file.exists():
                broken_links.append(f"{page.relative_to(html_root)} -> {href} missing file")
                continue

            if fragment:
                target_ids = ids_by_page.get(target_file)
                if target_ids is None:
                    target_parser = LinkParser()
                    target_parser.feed(target_file.read_text(encoding="utf-8"))
                    target_ids = target_parser.ids
                    ids_by_page[target_file] = target_ids

                decoded_fragment = unquote(fragment)
                if decoded_fragment not in target_ids:
                    broken_links.append(f"{page.relative_to(html_root)} -> {href} missing fragment")

    assert not broken_links, "broken local rendered links:\n" + "\n".join(broken_links[:100])


def test_generated_api_member_tables_have_defined_project_members() -> None:
    html_root = docs_html()
    generated_root = html_root / "api" / "generated"
    if not generated_root.exists():
        pytest.fail(f"generated API HTML is missing: {generated_root}")

    blank_rows: list[str] = []
    framework_noise: list[str] = []

    for page in sorted(generated_root.glob("*.html")):
        if not page.name.startswith(("foundry.", "scribe.", "smb3parse.")):
            continue

        html = page.read_text(encoding="utf-8")
        if "staticMetaObject" in html:
            framework_noise.append(str(page.relative_to(html_root)))

        parser = AutosummaryTableParser()
        parser.feed(html)
        for rubric, row in parser.rows:
            if rubric not in {"Attributes", "Methods"} or len(row) < 2 or row[1].strip():
                continue
            blank_rows.append(f"{page.relative_to(html_root)} {rubric}: {row[0]}")

    assert not framework_noise, "framework/meta members leaked into project API tables:\n" + "\n".join(
        framework_noise[:100]
    )
    assert not blank_rows, "blank project member rows:\n" + "\n".join(blank_rows[:100])
