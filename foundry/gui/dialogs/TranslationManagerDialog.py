"""Manage user-editable translation catalog overlays.

The Translation Manager is the in-app catalog editor for translators and
community locale maintainers. It reads the same effective catalogs used by
runtime translation, displays the English baseline beside the selected
locale's active value, and writes only partial user overlays. Bundled catalogs
under ``data/translations`` remain immutable from this dialog.

See Also
--------
foundry.gui.localization
    Runtime catalog loading, validation, and live retranslation helpers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import QBrush, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.localization import (
    CatalogValidationIssue,
    available_languages,
    language_display_name,
    load_effective_catalog,
    load_catalog,
    load_user_catalog,
    reload_available_languages,
    remove_user_catalog,
    save_user_catalog,
    tr,
    user_translation_dir,
    validate_catalog,
)

TR_CONTEXT = "foundry.translation_manager"
METADATA_CONTEXT = "_meta"
DISPLAY_NAME_KEY = "display_name"


def _manager_text(key: str, fallback: str) -> str:
    """Resolve Translation Manager chrome through stable catalog keys.

    Parameters
    ----------
    key : str
        ``foundry.translation_manager`` catalog key.
    fallback : str
        English text used when the active catalog has no value.

    Returns
    -------
    str
        Localized UI text. Locale codes, catalog context names, and row keys
        remain stable model data and are never translated for persistence.
    """
    return tr(TR_CONTEXT, key, fallback)


@dataclass
class TranslationRow:
    """Represent one baseline translation entry in the editor model.

    The row carries both immutable source identity and mutable editing state.
    ``context``, ``key``, and ``english`` come from the English baseline and are
    never written to user catalogs. ``translation`` is the active selected
    locale value after fallback and is the only value the table/detail editor
    can change.

    Attributes
    ----------
    context : str
        Catalog namespace for the entry.
    key : str
        Stable code-facing translation key.
    english : str
        English baseline text.
    translation : str
        Active selected-locale text shown and edited by the dialog.
    has_locale_entry : bool
        Whether the selected locale has a bundled or user value for this key.
    has_user_override : bool
        Whether the selected user overlay already overrides this key.
    dirty : bool
        Whether the in-memory value was edited during this dialog session.
    issues : list[CatalogValidationIssue]
        Current validation findings for this row.
    status_kind : str
        Machine-readable status used by filters and tests. Values are ``ok``
        for clean active text, ``edited`` for unsaved user edits, ``missing``
        for selected-locale fallback to English, ``unchanged`` for active text
        that equals English, ``blank`` for an empty edited value, and ``issue``
        for blocking validation problems.
    status_text : str
        Localized status label shown to the user.
    """

    context: str
    key: str
    english: str
    translation: str
    has_locale_entry: bool
    has_user_override: bool
    dirty: bool = False
    issues: list[CatalogValidationIssue] = field(default_factory=list)
    status_kind: str = "ok"
    status_text: str = ""


class TranslationTableModel(QAbstractTableModel):
    """Qt table model for translation catalog rows.

    The model deliberately separates source identity from user-editable text.
    Context, key, English, and status columns are read-only reference columns;
    the translation column is editable and marks rows dirty. Saving is handled
    by :class:`TranslationManagerDialog`, which serializes only dirty rows into
    the selected user overlay.

    Parameters
    ----------
    parent : QObject, optional
        Qt owner used for palette lookups and object lifetime management.

    Attributes
    ----------
    COLUMN_CONTEXT : int
        Read-only column containing the catalog context.
    COLUMN_KEY : int
        Read-only column containing the stable code-facing translation key.
    COLUMN_ENGLISH : int
        Read-only column containing the English baseline display text.
    COLUMN_TRANSLATION : int
        Editable column containing the selected locale's active display text.
    COLUMN_STATUS : int
        Read-only column containing localized row status text.
    rows : list[TranslationRow]
        Source rows built from the English baseline and selected-locale
        catalogs. Rows carry dirty state and validation issues for the dialog.
    headers : list[str]
        Localized table header labels refreshed by ``retranslate_ui``.
    selected_locale : str
        Stable locale code whose user overlay is currently being edited.
    user_catalog : dict[str, dict[str, str]]
        Loaded user overlay for ``selected_locale``. It is reference state for
        row construction; saves are performed by the dialog.

    Notes
    -----
    Model data is display-facing. Stable catalog identity remains the
    ``(context, key)`` pair carried in ``Qt.UserRole`` and in the row objects,
    while edited translations remain separate user-overlay values.

    See Also
    --------
    TranslationRow
        Row payload owned by the model.
    TranslationFilterProxyModel
        Visibility layer that filters these rows without translating identity.
    TranslationManagerDialog
        Dialog that saves dirty model rows to user overlays.
    """

    COLUMN_CONTEXT = 0
    COLUMN_KEY = 1
    COLUMN_ENGLISH = 2
    COLUMN_TRANSLATION = 3
    COLUMN_STATUS = 4

    def __init__(self, parent=None):
        """Create an empty translation table model.

        Parameters
        ----------
        parent : QObject, optional
            Qt owner used for palette lookups and object lifetime management.
        """
        super().__init__(parent)
        self.rows: list[TranslationRow] = []
        self.headers: list[str] = []
        self.selected_locale = "en"
        self.user_catalog: dict[str, dict[str, str]] = {}

    def rowCount(self, _parent: QModelIndex = QModelIndex()) -> int:
        """Provide Qt with the number of baseline catalog entries.

        Qt calls this while sizing and painting the table. The count reflects
        the English-baseline checklist for the selected locale, not the number
        of keys in the user overlay.

        Parameters
        ----------
        _parent : QModelIndex, optional
            Parent index supplied by Qt. The model is flat and ignores it.

        Returns
        -------
        int
            Number of :class:`TranslationRow` objects loaded for the selected
            locale.
        """
        return len(self.rows)

    def columnCount(self, _parent: QModelIndex = QModelIndex()) -> int:
        """Provide Qt with the fixed translation table column count.

        Keeping the column shape fixed lets headers, filters, and ``Qt`` role
        payloads continue to line up while catalogs are reloaded or labels are
        retransmitted through live language switching.

        Parameters
        ----------
        _parent : QModelIndex, optional
            Parent index supplied by Qt. The model is flat and ignores it.

        Returns
        -------
        int
            Five columns: context, key, English, translation, and status.
        """
        return 5

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Expose row fields through Qt roles without changing identity.

        ``UserRole`` carries the stable ``(context, key)`` tuple, and
        ``UserRole + 1`` carries ``status_kind`` so the proxy can filter rows
        without parsing translated status text.

        Display and edit roles move text into the view, while metadata roles
        keep save/filter decisions tied to stable catalog fields. Styling roles
        only highlight validation and dirty-state signals for the user.

        Parameters
        ----------
        index : QModelIndex
            Table index requested by Qt.
        role : int, optional
            Qt data role for display, editing, filtering, tooltip text, or
            background styling.

        Returns
        -------
        object
            Role-specific display value, stable metadata, brush, or ``None``
            when the role/index is unsupported.
        """
        if not index.isValid():
            return None
        row = self.rows[index.row()]
        column = index.column()

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return (
                row.context,
                row.key,
                row.english,
                row.translation,
                row.status_text,
            )[column]
        if role == Qt.ItemDataRole.UserRole:
            return (row.context, row.key)
        if role == Qt.ItemDataRole.UserRole + 1:
            return row.status_kind
        if role == Qt.ItemDataRole.ToolTipRole and column == self.COLUMN_STATUS:
            return self.issue_summary(row)
        if role == Qt.ItemDataRole.BackgroundRole:
            if row.status_kind in {"issue", "blank"}:
                return QBrush(self.palette_color(QPalette.ColorRole.AlternateBase))
            if row.dirty:
                return QBrush(self.palette_color(QPalette.ColorRole.ToolTipBase))
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        """Expose localized table headers to Qt.

        Headers are refreshed by ``retranslate_ui`` and emitted through Qt's
        normal header-data path, so language changes update labels without
        rebuilding rows or touching edited translations. The method only feeds
        Qt display text; source row identity and overlay dirty state stay in
        the model rows.

        Parameters
        ----------
        section : int
            Header section index.
        orientation : Qt.Orientation
            Requested header orientation.
        role : int, optional
            Qt header role.

        Returns
        -------
        object
            Localized horizontal header text, empty text for missing header
            slots, or Qt's default header data for other requests.
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section] if 0 <= section < len(self.headers) else ""
        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Make only the translation column editable.

        This protects catalog identity: users can override display values, but
        cannot rename contexts, keys, or English baseline text from the UI.

        Parameters
        ----------
        index : QModelIndex
            Cell whose edit/select flags Qt is requesting.

        Returns
        -------
        Qt.ItemFlag
            Default item flags, with editability added only for the
            translation column.
        """
        flags = super().flags(index)
        if index.isValid() and index.column() == self.COLUMN_TRANSLATION:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Edit a translation row and refresh its validation status.

        Edits remain in memory until :meth:`TranslationManagerDialog.save_changes`
        writes the dirty rows to a user overlay.

        Parameters
        ----------
        index : QModelIndex
            Translation-column index to edit.
        value : object
            New display text supplied by the table or detail editor.
        role : int, optional
            Qt edit role. Non-edit roles are ignored.

        Returns
        -------
        bool
            ``True`` when the edit was accepted and row status was refreshed.
        """
        if role != Qt.ItemDataRole.EditRole or not index.isValid() or index.column() != self.COLUMN_TRANSLATION:
            return False
        row = self.rows[index.row()]
        row.translation = str(value)
        row.dirty = True
        self.refresh_row_status(row)
        left = self.index(index.row(), 0)
        right = self.index(index.row(), self.COLUMN_STATUS)
        self.dataChanged.emit(left, right, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole])
        return True

    def set_headers(self, headers: list[str]) -> None:
        """Replace localized table headers after live retranslation.

        Parameters
        ----------
        headers : list[str]
            Display labels ordered by model column id.
        """
        self.headers = headers
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, self.columnCount() - 1)

    def load_rows(
        self,
        selected_locale: str,
        english_catalog: dict[str, dict[str, str]],
        active_catalog: dict[str, dict[str, str]],
        locale_catalog: dict[str, dict[str, str]],
        user_catalog: dict[str, dict[str, str]],
    ) -> None:
        """Replace all rows from effective and user catalogs.

        Rows are built from the English effective catalog so the table is a
        complete translation checklist. The selected locale's active value is
        shown after fallback, while ``has_locale_entry`` records whether that
        value came from the selected locale or merely from English fallback.

        Parameters
        ----------
        selected_locale : str
            Concrete locale code being edited.
        english_catalog : dict[str, dict[str, str]]
            English effective baseline.
        active_catalog : dict[str, dict[str, str]]
            Effective selected-locale catalog after fallback.
        locale_catalog : dict[str, dict[str, str]]
            Built-in selected-locale catalog.
        user_catalog : dict[str, dict[str, str]]
            Selected-locale user overlay.
        """
        self.beginResetModel()
        self.selected_locale = selected_locale
        self.user_catalog = user_catalog
        self.rows = []
        source_rows = sorted(
            (context, key, english)
            for context, translations in english_catalog.items()
            if context != METADATA_CONTEXT
            for key, english in translations.items()
        )
        for context, key, english in source_rows:
            has_user_override = bool(user_catalog.get(context, {}).get(key, ""))
            has_locale_entry = bool(locale_catalog.get(context, {}).get(key, "")) or has_user_override
            row = TranslationRow(
                context,
                key,
                english,
                active_catalog.get(context, {}).get(key, english),
                has_locale_entry,
                has_user_override,
            )
            self.refresh_row_status(row)
            self.rows.append(row)
        self.endResetModel()

    def refresh_all_statuses(self) -> None:
        """Refresh row statuses after a language switch or relabeling pass."""
        if not self.rows:
            return
        for row in self.rows:
            self.refresh_row_status(row)
        self.dataChanged.emit(
            self.index(0, self.COLUMN_STATUS),
            self.index(len(self.rows) - 1, self.COLUMN_STATUS),
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole],
        )

    def refresh_row_status(self, row: TranslationRow) -> None:
        """Refresh validation issues and status text for one row.

        Status decision order is part of the table/filter contract:
        validation errors become ``issue`` first, empty values become
        ``blank``, unsaved edits become ``edited``, missing non-English locale
        entries become ``missing``, values equal to English become
        ``unchanged``, and everything else is ``ok``. This keeps missing
        translations distinct from intentional English technical terms.

        Parameters
        ----------
        row : TranslationRow
            Row whose edited display value should be validated against the
            English baseline and mapped to a stable status id.
        """
        row.issues = validate_catalog(self.selected_locale, {row.context: {row.key: row.translation}})
        errors = [issue for issue in row.issues if issue.severity == "error"]
        if errors:
            row.status_kind = "issue"
            row.status_text = _manager_text("status.token_issue", "Token issue")
        elif not row.translation:
            row.status_kind = "blank"
            row.status_text = _manager_text("status.blank", "Blank")
        elif row.dirty:
            row.status_kind = "edited"
            row.status_text = _manager_text("status.edited", "Edited")
        elif self.selected_locale != "en" and not row.has_locale_entry:
            row.status_kind = "missing"
            row.status_text = _manager_text("status.missing", "Missing")
        elif row.translation == row.english:
            row.status_kind = "unchanged"
            row.status_text = _manager_text("status.unchanged", "Unchanged English")
        else:
            row.status_kind = "ok"
            row.status_text = _manager_text("status.ok", "OK")

    def issue_summary(self, row: TranslationRow) -> str:
        """Build the status tooltip text for a translation row.

        The Translation Manager uses this for Qt tooltip and detail status
        display so token-preservation problems are visible before a user saves
        a Foundry overlay catalog.

        Parameters
        ----------
        row : TranslationRow
            Row whose validation messages should be displayed.

        Returns
        -------
        str
            Newline-separated validation messages, or the row's localized
            status label when no issues exist.
        """
        if not row.issues:
            return row.status_text
        return "\n".join(issue.message for issue in row.issues)

    def dirty_rows(self) -> list[TranslationRow]:
        """Collect rows that should be serialized into the user overlay.

        Only these rows are considered when saving a partial user overlay.
        The bundled catalog and unchanged fallback rows remain untouched, so
        Foundry's ROM/editor identities and read-only catalog data stay stable.

        Returns
        -------
        list[TranslationRow]
            Rows with unsaved display-text edits.
        """
        return [row for row in self.rows if row.dirty]

    def has_validation_errors(self) -> bool:
        """Detect dirty rows whose validation state blocks overlay saving.

        The save button and save handler use this guard so token or shape
        issues in edited display text cannot be persisted over a valid bundled
        fallback. Warning-only states such as unchanged English remain
        saveable for partial community workflows, while Foundry placeholders,
        HTML tags, Qt accelerators, and ROM-adjacent object labels are
        protected as display-only text.

        Returns
        -------
        bool
            ``True`` when a dirty row has at least one validation issue with
            ``severity == "error"``. Non-dirty catalog issues and warning-only
            findings do not disable saving because the dialog writes partial
            user overlays rather than replacing bundled catalogs.
        """
        return any(row.dirty and any(issue.severity == "error" for issue in row.issues) for row in self.rows)

    def counts(self) -> dict[str, int]:
        """Summarize model state for the Translation Manager footer.

        The counts communicate Qt table workflow state only: how much of the
        selected locale is visible, edited, inherited from English, or blocked
        by validation issues.

        Returns
        -------
        dict[str, int]
            Mapping with ``total``, ``edited``, ``missing``, and ``issues``.
            ``missing`` reflects selected-locale fallback to English, while
            ``issues`` counts rows whose active text is blank or structurally
            invalid. These counts are display summaries only and are not used
            as catalog identity.
        """
        return {
            "total": len(self.rows),
            "edited": sum(row.dirty for row in self.rows),
            "missing": sum(row.status_kind == "missing" for row in self.rows),
            "issues": sum(row.status_kind in {"issue", "blank"} for row in self.rows),
        }

    def find_row(self, context: str, key: str) -> int:
        """Locate a source row by stable catalog identity.

        Detail selection and tests use this lookup to reconnect Qt view state
        to the source model after filtering or retranslation. It compares
        catalog ids only, never localized labels or SMB3 data names.

        Parameters
        ----------
        context : str
            Catalog context to match.
        key : str
            Stable translation key to match.

        Returns
        -------
        int
            Source row index, or ``-1`` when the Foundry catalog entry is not
            present in the loaded English-baseline checklist.
        """
        for row_index, row in enumerate(self.rows):
            if row.context == context and row.key == key:
                return row_index
        return -1

    def palette_color(self, role: QPalette.ColorRole):
        """Resolve a Qt palette color for model-owned row highlighting.

        The model asks its parent widget for palette colors so dirty and
        validation states follow Foundry's active Qt theme without storing UI
        colors in catalog data.

        Parameters
        ----------
        role : QPalette.ColorRole
            Palette role used for dirty or validation-state backgrounds.

        Returns
        -------
        QColor
            Parent widget palette color when available, otherwise a default Qt
            palette color.
        """
        owner = self.parent()
        if isinstance(owner, QWidget):
            return owner.palette().color(role)
        return QPalette().color(role)


class TranslationFilterProxyModel(QSortFilterProxyModel):
    """Filter translation rows by search text, context, and status.

    Search scans context, key, English source, and active translation text.
    Context and status filters operate on stable row metadata, not localized
    table labels, so filtering remains stable across live language changes.

    Parameters
    ----------
    parent : QObject, optional
        Qt owner for the proxy model.

    Attributes
    ----------
    search_text : str
        Case-folded free-text filter applied to context, key, English, and
        active translation text.
    context_filter : str
        Exact catalog context to show, or ``""`` for all contexts.
    status_filter : str
        Stable status filter id such as ``all``, ``missing``, ``edited``, or
        ``issues``.

    Notes
    -----
    The proxy belongs to the Translation Manager workflow only. It never
    rewrites catalog data; it changes visibility of Qt rows backed by stable
    context/key identity.

    See Also
    --------
    TranslationTableModel
        Source model that owns the row data being filtered.
    """

    def __init__(self, parent=None):
        """Create a proxy with all rows visible.

        Parameters
        ----------
        parent : QObject, optional
            Qt owner for the proxy model.
        """
        super().__init__(parent)
        self.search_text = ""
        self.context_filter = ""
        self.status_filter = "all"
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_search_text(self, text: str) -> None:
        """Normalize and apply the free-text row filter.

        Parameters
        ----------
        text : str
            Case-insensitive substring to match against row text.
        """
        self.search_text = text.casefold().strip()
        self.invalidateFilter()

    def set_context_filter(self, context: str) -> None:
        """Apply an exact catalog-context visibility filter.

        Parameters
        ----------
        context : str
            Exact catalog context to show, or ``""`` for all contexts.
        """
        self.context_filter = context
        self.invalidateFilter()

    def set_status_filter(self, status: str) -> None:
        """Apply a stable row-status visibility filter.

        Parameters
        ----------
        status : str
            Status kind such as ``"missing"``, ``"edited"``, ``"issues"``,
            or ``"all"``.
        """
        self.status_filter = status
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Evaluate a source row against stable Translation Manager filters.

        Qt calls this whenever search text, context, status, sorting, or source
        data changes. The proxy reads row metadata from the source model and
        returns a visibility decision without editing translation values or
        status state.

        Parameters
        ----------
        source_row : int
            Row index in :class:`TranslationTableModel`.
        source_parent : QModelIndex
            Parent index supplied by Qt. The model is flat, so the value is not
            consulted.

        Returns
        -------
        bool
            ``True`` when context, stable status id, and free-text filters all
            match. The check intentionally reads source-row metadata instead
            of localized table text so live language switching does not change
            which rows are visible.
        """
        model = self.sourceModel()
        if not isinstance(model, TranslationTableModel):
            return True
        row = model.rows[source_row]
        if self.context_filter and row.context != self.context_filter:
            return False
        if self.status_filter != "all":
            if self.status_filter == "issues" and row.status_kind not in {"issue", "blank"}:
                return False
            if self.status_filter != "issues" and row.status_kind != self.status_filter:
                return False
        if self.search_text:
            haystack = "\n".join((row.context, row.key, row.english, row.translation)).casefold()
            return self.search_text in haystack
        return True


class TranslationManagerDialog(CustomDialog):
    """Edit and import user translation overlays.

    The dialog presents the English baseline and active selected-locale text in
    a searchable table plus a detail editor. Saves write only user overrides,
    never bundled catalogs.

    The manager is designed around stable locale codes. The settings dialog
    passes a concrete language code into the constructor, imported filenames
    become user-catalog locale codes, and ``catalog_changed`` reports the
    concrete selected locale after import, save, or revert.

    Parameters
    ----------
    locale : str, optional
        Concrete locale code to select initially. ``system`` is resolved before
        callers open the dialog because overlays are saved by concrete code.
    parent : QWidget, optional
        Parent settings dialog or main window.

    Attributes
    ----------
    catalog_changed : SignalInstance
        Emitted with the concrete selected locale code after successful import,
        save, or revert changes user overlay state. Export does not emit it.
        Handlers should refresh language discovery and reinstall/retranslate
        the active language when the changed locale is currently selected.
    DEFAULT_COLUMN_WIDTHS : dict[int, int]
        Initial table widths keyed by ``TranslationTableModel`` column id.
    MINIMUM_TABLE_WIDTH : int
        Lower bound for the dialog's initial table-oriented width.
    selected_locale : str
        Stable locale code selected in the dialog. This code, not the
        translated language name, is used for overlay filenames and emitted
        change notifications.
    _active_source_row : int
        Source-model row currently loaded in the detail editor, or ``-1`` when
        no visible row is selected.
    _is_loading_detail : bool
        Guard that prevents programmatic detail refreshes from being treated as
        user edits.
    close_button : QPushButton
        Closes the dialog without saving new dirty rows.
    context_filter : QComboBox
        Stable context selector used by the proxy model.
    description_label : QLabel
        Localized explanatory text for the user-overlay workflow.
    detail_context_label : QLabel
        Displays the selected row's catalog context.
    detail_english_label : QLabel
        Localized label for the read-only English source editor.
    detail_english_text : QPlainTextEdit
        Read-only English baseline text for the selected row.
    detail_group : QGroupBox
        Container for selected-row details and edit controls.
    detail_key_label : QLabel
        Displays the selected row's stable catalog key.
    detail_status_label : QLabel
        Displays validation and status text for the selected row.
    detail_translation_label : QLabel
        Localized label for the editable active translation field.
    detail_translation_text : QPlainTextEdit
        Editable translation text that commits changes through the table model.
    export_button : QPushButton
        Exports the effective catalog as a complete translator starting point.
    fit_columns_button : QPushButton
        Restores table columns to useful default widths.
    import_button : QPushButton
        Imports a JSON file into the writable user overlay directory.
    locale_dropdown : QComboBox
        Locale-code selector; item data stores stable locale codes.
    locale_label : QLabel
        Localized label for ``locale_dropdown``.
    model : TranslationTableModel
        Source model that owns row state, dirty flags, and validation issues.
    proxy_model : TranslationFilterProxyModel
        Search/context/status proxy for visible table rows.
    revert_button : QPushButton
        Deletes the selected locale's user overlay.
    save_button : QPushButton
        Saves valid dirty rows as a partial user overlay.
    search_input : QLineEdit
        Free-text filter entry for context, key, English, and translation text.
    status_filter : QComboBox
        Stable status selector used by the proxy model.
    summary_label : QLabel
        Footer summary of visible rows, dirty rows, missing translations, and
        validation issues.
    title_label : QLabel
        Localized dialog title shown in the content area.
    translation_table : QTableView
        Table view presenting the proxy model and stable row selection.

    Notes
    -----
    The dialog is a display and overlay-management boundary. It may import,
    export, save, and delete user JSON overlays, but translated labels never
    become Foundry settings values, ROM identifiers, object lookup keys, or
    undo/replay payloads.

    See Also
    --------
    TranslationTableModel
        Owns row dirty state and validation status.
    TranslationFilterProxyModel
        Filters visible rows by search, context, and stable status ids.
    TranslationRow
        Carries one baseline entry and its editable display value.
    """

    catalog_changed: SignalInstance = Signal(str)
    MINIMUM_TABLE_WIDTH = 640
    DEFAULT_COLUMN_WIDTHS = {
        TranslationTableModel.COLUMN_CONTEXT: 160,
        TranslationTableModel.COLUMN_KEY: 260,
        TranslationTableModel.COLUMN_ENGLISH: 420,
        TranslationTableModel.COLUMN_TRANSLATION: 420,
        TranslationTableModel.COLUMN_STATUS: 140,
    }

    def __init__(self, locale: str = "en", parent=None):
        """Create the translation manager for ``locale``.

        Construction creates the Qt controls, connects filtering/editing
        signals, installs localized labels, and then loads the selected
        locale's effective catalog. The loaded data is display-only table
        state until Save serializes valid dirty rows into a user overlay.

        Parameters
        ----------
        locale : str, optional
            Concrete locale code to select initially. ``system`` is not shown
            because user overlay files are saved by concrete locale code.
        parent : QWidget, optional
            Parent settings dialog or window.
        """
        super().__init__(parent, _manager_text("title", "Translations"))
        self._is_loading_detail = False
        self._active_source_row = -1

        self.title_label = QLabel(self)
        self.title_label.setObjectName("translationManagerTitle")
        self.description_label = QLabel(self)
        self.description_label.setWordWrap(True)

        self.locale_label = QLabel(self)
        self.locale_dropdown = QComboBox(self)
        self.locale_dropdown.currentIndexChanged.connect(self._on_locale_changed)

        self.import_button = QPushButton(self)
        self.import_button.clicked.connect(self.import_catalog)
        self.export_button = QPushButton(self)
        self.export_button.clicked.connect(self.export_catalog)
        self.save_button = QPushButton(self)
        self.save_button.clicked.connect(self.save_changes)
        self.revert_button = QPushButton(self)
        self.revert_button.clicked.connect(self.revert_user_catalog)
        self.close_button = QPushButton(self)
        self.close_button.clicked.connect(self.close)

        self.search_input = QLineEdit(self)
        self.search_input.textChanged.connect(self._on_filter_changed)
        self.context_filter = QComboBox(self)
        self.context_filter.currentIndexChanged.connect(self._on_filter_changed)
        self.status_filter = QComboBox(self)
        self.status_filter.currentIndexChanged.connect(self._on_filter_changed)
        self.fit_columns_button = QPushButton(self)
        self.fit_columns_button.clicked.connect(self.fit_columns)
        self.summary_label = QLabel(self)

        self.model = TranslationTableModel(self)
        self.proxy_model = TranslationFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.translation_table = QTableView(self)
        self.translation_table.setModel(self.proxy_model)
        self.translation_table.setSortingEnabled(True)
        self.translation_table.setAlternatingRowColors(True)
        self.translation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.translation_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.translation_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.translation_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.translation_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.translation_table.verticalHeader().setVisible(False)
        self.translation_table.horizontalHeader().setStretchLastSection(False)
        self.translation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.translation_table.selectionModel().currentRowChanged.connect(self._on_selection_changed)

        self.detail_group = QGroupBox(self)
        self.detail_context_label = QLabel(self)
        self.detail_key_label = QLabel(self)
        self.detail_english_label = QLabel(self)
        self.detail_english_text = QPlainTextEdit(self)
        self.detail_english_text.setReadOnly(True)
        self.detail_translation_label = QLabel(self)
        self.detail_translation_text = QPlainTextEdit(self)
        self.detail_translation_text.textChanged.connect(self._on_detail_translation_changed)
        self.detail_status_label = QLabel(self)
        self.detail_status_label.setWordWrap(True)

        self._build_layout()
        self._apply_theme_polish()
        self.retranslate_ui()
        self._refresh_locale_dropdown(locale)
        self._load_selected_locale()
        self._resize_to_table_width()

    @property
    def selected_locale(self) -> str:
        """Expose the locale-code identity selected by the dropdown.

        The combo-box label may be translated, but its item data remains the
        stable code used by catalog loading, overlay filenames, and
        ``catalog_changed`` notifications. Foundry stores and compares this
        code instead of localized language names, just as ROM and SMB3 object
        identifiers remain stable behind translated labels.

        Returns
        -------
        str
            Stable locale code stored in combo-box item data, falling back to
            ``"en"`` when no item is selected. This is the overlay filename
            stem and signal payload, not the translated display name.
        """
        return str(self.locale_dropdown.currentData() or "en")

    def _build_layout(self) -> None:
        """Build the header, filters, table, detail pane, and footer controls.

        This method wires the Qt layout only. Catalog state is loaded later so
        locale discovery, filtering, and dirty-row tracking remain owned by the
        model and refresh helpers.

        The layout is staged as header and locale controls, filterable table,
        selected-row detail editor, then footer actions. That mirrors the user
        workflow: choose locale, find a string, edit its display value, then
        save or revert overlay state.
        """
        locale_layout = QHBoxLayout()
        locale_layout.addWidget(self.locale_label)
        locale_layout.addWidget(self.locale_dropdown, stretch=1)
        locale_layout.addWidget(self.import_button)
        locale_layout.addWidget(self.export_button)

        header_frame = QFrame(self)
        header_layout = QVBoxLayout(header_frame)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.description_label)
        header_layout.addLayout(locale_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.search_input, stretch=3)
        filter_layout.addWidget(self.context_filter, stretch=2)
        filter_layout.addWidget(self.status_filter, stretch=1)
        filter_layout.addWidget(self.fit_columns_button)

        detail_layout = QVBoxLayout(self.detail_group)
        detail_layout.addWidget(self.detail_context_label)
        detail_layout.addWidget(self.detail_key_label)
        detail_layout.addWidget(self.detail_english_label)
        detail_layout.addWidget(self.detail_english_text, stretch=1)
        detail_layout.addWidget(self.detail_translation_label)
        detail_layout.addWidget(self.detail_translation_text, stretch=1)
        detail_layout.addWidget(self.detail_status_label)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        table_area = QWidget(self)
        table_layout = QVBoxLayout(table_area)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addLayout(filter_layout)
        table_layout.addWidget(self.translation_table)
        splitter.addWidget(table_area)
        splitter.addWidget(self.detail_group)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.summary_label, stretch=1)
        bottom_layout.addWidget(self.revert_button)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(header_frame)
        layout.addWidget(splitter, stretch=1)
        layout.addLayout(bottom_layout)

    def _apply_theme_polish(self) -> None:
        """Apply palette-friendly sizing and visual polish to editor widgets.

        The styling keeps the Translation Manager readable inside Foundry's Qt
        theme without encoding catalog state or changing how translations are
        validated, filtered, or saved.
        """
        self.title_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.description_label.setStyleSheet("opacity: 0.85;")
        self.detail_status_label.setStyleSheet("opacity: 0.9;")
        self.translation_table.setWordWrap(False)
        self.translation_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.detail_english_text.setMinimumHeight(72)
        self.detail_translation_text.setMinimumHeight(96)

    def retranslate_ui(self) -> None:
        """Refresh static dialog labels after a language switch.

        The table rows are not rebuilt here. Instead, localized headers,
        buttons, filters, status text, and the detail labels are refreshed in
        place so selection, filters, dirty state, and user-edited text survive
        live language switching.

        This is a Qt live-retranslation hook. It relabels display controls
        only; stable locale codes, context/key row identity, and edited
        translation values remain untouched.

        The refresh order preserves workflow state: static controls are
        relabeled first, filter and locale dropdown labels are rebuilt around
        their stable item data, model row statuses are recalculated with the
        newly installed translator, and the detail pane is reloaded from the
        selected source row.
        """
        self.setWindowTitle(_manager_text("title", "Translations"))
        self.title_label.setText(_manager_text("title", "Translations"))
        self.description_label.setText(
            _manager_text(
                "help.overrides",
                "Edit user overrides for the selected locale. Bundled translation files stay unchanged.",
            )
        )
        self.locale_label.setText(_manager_text("locale.label", "Locale:"))
        self.import_button.setText(_manager_text("button.import_json", "Import JSON..."))
        self.export_button.setText(_manager_text("button.export_json", "Export JSON..."))
        self.save_button.setText(_manager_text("button.save", "Save"))
        self.revert_button.setText(_manager_text("button.revert", "Revert user overrides"))
        self.close_button.setText(_manager_text("button.close", "Close"))
        self.fit_columns_button.setText(_manager_text("button.fit_columns", "Fit columns"))
        self.search_input.setPlaceholderText(_manager_text("filter.search.placeholder", "Search translations..."))
        self.detail_group.setTitle(_manager_text("detail.title", "Selected translation"))
        self.detail_english_label.setText(_manager_text("detail.english", "English source"))
        self.detail_translation_label.setText(_manager_text("detail.translation", "Active translation"))
        self.model.set_headers(
            [
                _manager_text("table.context", "Context"),
                _manager_text("table.key", "Key"),
                _manager_text("table.english", "English"),
                _manager_text("table.translation", "Translation"),
                _manager_text("table.status", "Status"),
            ]
        )
        self._refresh_status_filter_labels()
        current_locale = self.selected_locale
        for index in range(self.locale_dropdown.count()):
            locale_code = self.locale_dropdown.itemData(index)
            self.locale_dropdown.setItemText(index, language_display_name(locale_code))
        self.locale_dropdown.setCurrentIndex(max(0, self.locale_dropdown.findData(current_locale)))
        self.model.refresh_all_statuses()
        self._refresh_summary()
        self._refresh_detail_labels()

    def _refresh_locale_dropdown(self, selected_locale: str) -> None:
        """Rebuild locale choices while preserving a requested selection.

        ``system`` is omitted because the manager edits concrete catalog files.
        Custom user catalogs appear after ``reload_available_languages``
        discovers their JSON stems.

        Parameters
        ----------
        selected_locale : str
            Stable locale code that should remain selected when present.
        """
        self.locale_dropdown.blockSignals(True)
        self.locale_dropdown.clear()
        for language_code in available_languages():
            if language_code == "system":
                continue
            self.locale_dropdown.addItem(language_display_name(language_code), language_code)
        selected_index = self.locale_dropdown.findData(selected_locale)
        self.locale_dropdown.setCurrentIndex(max(0, selected_index))
        self.locale_dropdown.blockSignals(False)

    def _refresh_status_filter_labels(self) -> None:
        """Rebuild localized status filter options while preserving selection."""
        current_status = self.status_filter.currentData() or "all"
        self.status_filter.blockSignals(True)
        self.status_filter.clear()
        for status_key, fallback, status_data in (
            ("filter.status.all", "All statuses", "all"),
            ("filter.status.edited", "Edited", "edited"),
            ("filter.status.missing", "Missing", "missing"),
            ("filter.status.unchanged", "Unchanged", "unchanged"),
            ("filter.status.issues", "Validation issues", "issues"),
        ):
            self.status_filter.addItem(_manager_text(status_key, fallback), status_data)
        self.status_filter.setCurrentIndex(max(0, self.status_filter.findData(current_status)))
        self.status_filter.blockSignals(False)

    def _refresh_context_filter(self) -> None:
        """Rebuild catalog-context filter choices while preserving selection.

        The visible labels are raw catalog contexts because they are stable
        maintainer-facing namespaces, not translated UI prose. Rebuilding the
        list after row loads keeps Qt filters aligned with the selected
        locale's English-baseline checklist and Foundry's catalog structure.
        """
        current_context = self.context_filter.currentData() or ""
        self.context_filter.blockSignals(True)
        self.context_filter.clear()
        self.context_filter.addItem(_manager_text("filter.context.all", "All contexts"), "")
        for context in sorted({row.context for row in self.model.rows}):
            self.context_filter.addItem(context, context)
        self.context_filter.setCurrentIndex(max(0, self.context_filter.findData(current_context)))
        self.context_filter.blockSignals(False)

    def _on_locale_changed(self) -> None:
        """Reload rows for the newly selected concrete locale.

        Selecting another locale intentionally replaces in-memory edits from
        the previous locale. Persisted user overlays remain on disk, bundled
        catalogs remain read-only, and the row set is rebuilt from English
        baseline, selected-locale catalog, and selected-locale user overlay
        data.
        """
        self._load_selected_locale()

    def _load_selected_locale(self) -> None:
        """Populate the table from baseline, selected, and user-overlay catalogs.

        English supplies the source column, the effective selected catalog
        supplies the displayed translation, and the bundled/user selected
        catalogs let the model distinguish inherited text from editable user
        overrides. Filters, detail selection, summary counts, and initial table
        sizing are refreshed after the row set changes.
        """
        self.model.load_rows(
            self.selected_locale,
            load_effective_catalog("en"),
            load_effective_catalog(self.selected_locale),
            load_catalog(self.selected_locale),
            load_user_catalog(self.selected_locale),
        )
        self._refresh_context_filter()
        self._on_filter_changed()
        self.fit_columns()
        self._select_first_visible_row()
        self._refresh_summary()
        self._resize_to_table_width()

    def fit_columns(self) -> None:
        """Fit table columns to useful defaults.

        The header remains interactive after fitting, so users can resize
        columns again without filtering or sorting undoing their manual widths.
        """
        header = self.translation_table.horizontalHeader()
        for column in range(self.model.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)
            self.translation_table.setColumnWidth(column, self.DEFAULT_COLUMN_WIDTHS[column])

    def _resize_to_table_width(self) -> None:
        """Derive the initial dialog width from table columns and screen size.

        This is a presentation helper for the Translation Manager's dense
        catalog table. It affects the initial window size only; users can
        manually resize the dialog wider during the session, and no catalog
        state is read or written.
        """
        table_width = self.translation_table.verticalHeader().width()
        table_width += sum(self.translation_table.columnWidth(column) for column in range(self.model.columnCount()))
        table_width += self.translation_table.frameWidth() * 2
        if self.translation_table.verticalScrollBar().isVisible():
            table_width += self.translation_table.verticalScrollBar().sizeHint().width()

        layout_margins = self.layout().contentsMargins()
        natural_width = table_width + layout_margins.left() + layout_margins.right()
        natural_width = max(self.MINIMUM_TABLE_WIDTH, natural_width)

        screen = self.screen()
        if screen is None:
            window_handle = self.windowHandle()
            screen = window_handle.screen() if window_handle is not None else None
        if screen is not None:
            natural_width = min(natural_width, screen.availableGeometry().width() // 2)

        self.setMinimumSize(QSize(min(self.MINIMUM_TABLE_WIDTH, natural_width), 520))
        self.resize(natural_width, max(self.height(), 720))

    def _on_filter_changed(self) -> None:
        """Apply search, context, and status filters."""
        self.proxy_model.set_search_text(self.search_input.text())
        self.proxy_model.set_context_filter(str(self.context_filter.currentData() or ""))
        self.proxy_model.set_status_filter(str(self.status_filter.currentData() or "all"))
        self._select_first_visible_row()
        self._refresh_summary()

    def _select_first_visible_row(self) -> None:
        """Keep detail selection valid after filtering changes visible rows.

        If the selected proxy row still exists it remains selected and the
        detail pane is reloaded from that row. Otherwise the first visible row
        is selected, or the detail pane is cleared when no rows match. The
        selection is view state only; source row identity remains the
        ``(context, key)`` pair stored in model data.
        """
        if self.proxy_model.rowCount() <= 0:
            self.translation_table.clearSelection()
            self._show_no_selection()
            return
        current = self.translation_table.currentIndex()
        if current.isValid() and current.row() < self.proxy_model.rowCount():
            self._load_detail_from_proxy_index(current)
            return
        first_index = self.proxy_model.index(0, 0)
        self.translation_table.setCurrentIndex(first_index)
        self.translation_table.selectRow(0)

    def _on_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Load detail-editor state for the selected proxy row.

        The table selection drives the detail pane only. It does not save or
        validate text until the user edits the translation field through the
        model.

        Parameters
        ----------
        current : QModelIndex
            Newly selected proxy-model row.
        _previous : QModelIndex
            Previously selected row supplied by Qt and ignored.
        """
        self._load_detail_from_proxy_index(current)

    def _load_detail_from_proxy_index(self, proxy_index: QModelIndex) -> None:
        """Load a proxy-selected table row into the detail editor.

        The proxy index is mapped back to the source model before reading row
        state. The loading guard prevents populating the translation editor
        from being interpreted as a user edit.

        Parameters
        ----------
        proxy_index : QModelIndex
            Visible table index selected by the user or by filter refresh.
        """
        if not proxy_index.isValid():
            self._show_no_selection()
            return
        source_index = self.proxy_model.mapToSource(proxy_index)
        self._active_source_row = source_index.row()
        row = self.model.rows[self._active_source_row]
        self._is_loading_detail = True
        self.detail_context_label.setText(
            _manager_text("detail.context", "Context: {context}").format(context=row.context)
        )
        self.detail_key_label.setText(_manager_text("detail.key", "Key: {key}").format(key=row.key))
        self.detail_english_text.setPlainText(row.english)
        self.detail_translation_text.setPlainText(row.translation)
        self.detail_status_label.setText(self.model.issue_summary(row))
        self._is_loading_detail = False

    def _refresh_detail_labels(self) -> None:
        """Refresh selected detail labels after language changes."""
        if 0 <= self._active_source_row < len(self.model.rows):
            proxy_index = self.proxy_model.mapFromSource(self.model.index(self._active_source_row, 0))
            self._load_detail_from_proxy_index(proxy_index)
        else:
            self._show_no_selection()

    def _show_no_selection(self) -> None:
        """Show an empty detail state when no filtered row is selected.

        This clears Qt display widgets and marks the detail pane as detached
        from any source row so later detail-editor changes cannot be applied to
        a stale Foundry catalog entry.
        """
        self._active_source_row = -1
        self._is_loading_detail = True
        self.detail_context_label.setText(_manager_text("detail.no_selection", "No translation selected."))
        self.detail_key_label.clear()
        self.detail_english_text.clear()
        self.detail_translation_text.clear()
        self.detail_status_label.clear()
        self._is_loading_detail = False

    def _on_detail_translation_changed(self) -> None:
        """Commit detail-editor changes through the model and refresh row state.

        Editing may affect search matches, status filters, validation issues,
        and whether Save is enabled, so the proxy and summary/detail status are
        refreshed after every accepted text change. The edit remains display
        overlay data until validation passes and the user saves it; it never
        rewrites ROM-backed SMB3 data or stable catalog keys.
        """
        if self._is_loading_detail or self._active_source_row < 0:
            return
        index = self.model.index(self._active_source_row, TranslationTableModel.COLUMN_TRANSLATION)
        self.model.setData(index, self.detail_translation_text.toPlainText())
        self.proxy_model.invalidateFilter()
        self._refresh_summary()
        self._refresh_save_button()
        self.detail_status_label.setText(self.model.issue_summary(self.model.rows[self._active_source_row]))

    def _refresh_summary(self) -> None:
        """Refresh visible and model summary counts."""
        counts = self.model.counts()
        self.summary_label.setText(
            _manager_text(
                "summary",
                "{visible}/{total} shown · {edited} edited · {missing} missing · {issues} issues",
            ).format(
                visible=self.proxy_model.rowCount(),
                total=counts["total"],
                edited=counts["edited"],
                missing=counts["missing"],
                issues=counts["issues"],
            )
        )
        self._refresh_save_button()

    def _refresh_save_button(self) -> None:
        """Enable Save only when there are valid pending edits."""
        self.save_button.setEnabled(bool(self.model.dirty_rows()) and not self.model.has_validation_errors())

    def import_catalog(self) -> None:
        """Import a JSON catalog into the user override directory.

        The imported file stem becomes the locale code. The catalog is
        validated before writing, then saved as a user overlay. Bundled
        catalogs are never modified. Validation errors block import; warnings
        are accepted. A successful import refreshes locale discovery, selects
        the imported locale, reloads rows, and emits ``catalog_changed``.
        Foundry runtime identity continues to use locale codes and stable
        catalog keys rather than translated labels, preserving ROM/parser
        boundaries.
        """
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            _manager_text("dialog.import.title", "Import translation catalog"),
            str(user_translation_dir()),
            _manager_text("dialog.json_filter", "JSON files (*.json)"),
        )
        if not path:
            return
        try:
            catalog = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self._show_error(str(error))
            return
        if not isinstance(catalog, dict):
            self._show_error(_manager_text("error.catalog_root", "Catalog root must be a JSON object."))
            return
        issues = validate_catalog(Path(path).stem, catalog)
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            self._show_error("\n".join(issue.message for issue in errors[:5]))
            return
        save_user_catalog(Path(path).stem, catalog)
        reload_available_languages()
        self._refresh_locale_dropdown(Path(path).stem)
        self._load_selected_locale()
        self.catalog_changed.emit(self.selected_locale)

    def export_catalog(self) -> None:
        """Export the effective selected catalog to a JSON file.

        Export includes fallback values, making the result a complete starting
        point for translators rather than only saved user overrides. The
        file path comes from a save dialog, but no runtime catalog is replaced:
        export does not mutate user overlays, refresh language discovery, emit
        ``catalog_changed``, or change the selected stable locale code.
        """
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            _manager_text("dialog.export.title", "Export translation catalog"),
            str(user_translation_dir() / f"{self.selected_locale}.json"),
            _manager_text("dialog.json_filter", "JSON files (*.json)"),
        )
        if not path:
            return
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(
            json.dumps(load_effective_catalog(self.selected_locale), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )

    def save_changes(self) -> None:
        """Save edited table cells as a partial user catalog overlay.

        Only dirty rows are serialized. Non-blank values become user overrides;
        blank edited values remove the key from the overlay so runtime fallback
        can supply bundled or English text. Blocking validation errors prevent
        save. A successful save merges edits into the existing user overlay,
        prunes empty contexts, reloads rows, and emits ``catalog_changed``.
        """
        if self.model.has_validation_errors():
            errors = [
                issue.message for row in self.model.dirty_rows() for issue in row.issues if issue.severity == "error"
            ]
            self._show_error("\n".join(errors[:5]))
            return

        catalog = load_user_catalog(self.selected_locale)
        for row in self.model.dirty_rows():
            if row.translation:
                catalog.setdefault(row.context, {})[row.key] = row.translation
            else:
                if row.context in catalog:
                    catalog[row.context].pop(row.key, None)
                    if not catalog[row.context]:
                        catalog.pop(row.context)

        issues = validate_catalog(self.selected_locale, catalog)
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            self._show_error("\n".join(issue.message for issue in errors[:5]))
            return
        save_user_catalog(self.selected_locale, catalog)
        self._load_selected_locale()
        self.catalog_changed.emit(self.selected_locale)

    def revert_user_catalog(self) -> None:
        """Remove the selected locale's user override catalog.

        Revert is scoped to the selected user overlay. It does not touch
        bundled catalogs or other locale override files. After deletion the
        table falls back to bundled or English effective values, language
        discovery refreshes, and ``catalog_changed`` is emitted.
        """
        remove_user_catalog(self.selected_locale)
        reload_available_languages()
        self._refresh_locale_dropdown(self.selected_locale)
        self._load_selected_locale()
        self.catalog_changed.emit(self.selected_locale)

    def _find_row(self, context: str, key: str) -> int:
        """Delegate stable catalog row lookup to the source model.

        This helper keeps dialog code aligned with the model's context/key
        identity contract when Qt view selection, filters, or tests need to
        locate a Foundry translation row.
        It coordinates lookup only; callers decide whether to select the row,
        refresh detail text, or assert that the catalog entry exists.

        Parameters
        ----------
        context : str
            Catalog context to match.
        key : str
            Stable translation key to match.

        Returns
        -------
        int
            Source row index, or ``-1`` when the entry is absent.
        """
        return self.model.find_row(context, key)

    def _show_error(self, message: str) -> None:
        """Show a modal Translation Manager validation error.

        Parameters
        ----------
        message : str
            User-facing error text describing why import or save was blocked.
        """
        QMessageBox.warning(
            self,
            _manager_text("error.title", "Invalid translation catalog"),
            message,
        )
