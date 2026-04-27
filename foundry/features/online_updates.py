"""Online update checks for stable and nightly Foundry releases.

The update feature queries GitHub release metadata, separates stable tags from
the moving ``nightly`` release, and presents the result according to the user's
release-channel and ignored-version settings. The network work runs on a
:class:`PySide6.QtCore.QThread` during startup so version checks do not block
the editor UI.

This module owns the policy boundary between raw release metadata and
user-facing update prompts. Parsing helpers normalize GitHub release payloads,
:class:`UpdateChecker` performs the background request, and
:class:`UpdateCheckMixin` decides when startup or manual checks should surface
dialogs.

See Also
--------
foundry.gui.settings
    Stores the release-channel and ignored-version settings consulted here.
foundry.features.rom_reload
    Another background maintenance feature that coordinates external state with
    the main editor window.
"""

import json
import urllib.error
import urllib.request
from http.client import IncompleteRead
from typing import Callable

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QPushButton

from foundry import Settings, get_current_version_name, icon, open_url, releases_link
from foundry.gui.settings import ReleaseChannel

SHORT_COMMIT_LENGTH = 8  # characters


def get_release_data(timeout: int = 10) -> bytes:
    """Fetch GitHub release metadata for Foundry.

    The raw response is left as bytes so parsing helpers can be tested
    independently from network access.

    Parameters
    ----------
    timeout : int, optional
        Network timeout in seconds.

    Returns
    -------
    bytes
        Raw GitHub releases API response.

    Raises
    ------
    ValueError
        If the input data or current state is invalid.
    """
    owner = "mchlnix"
    repo = "SMB3-Foundry"

    api_call = f"https://api.github.com/repos/{owner}/{repo}/releases"

    try:
        request = urllib.request.urlopen(api_call, timeout=timeout)
    except urllib.error.URLError as ue:
        raise ValueError(f"Network error {ue}")

    try:
        return request.read()
    except IncompleteRead as icr:
        raise ValueError("Read corrupted data from the internet.") from icr


def get_latest_version_name_from_data(data: bytes) -> str:
    """Return the newest non-nightly release tag.

    GitHub returns releases newest first. Foundry treats the moving ``nightly``
    tag separately, so this parser returns the first stable tag it finds.

    Parameters
    ----------
    data : bytes
        Raw bytes or bytearray being parsed.

    Returns
    -------
    str
        Latest stable release tag.

    Raises
    ------
    LookupError
        If the requested data cannot be found.
    ValueError
        If the input data or current state is invalid.

    Examples
    --------
    >>> payload = (
    ...     b'[{"tag_name": "nightly", "target_commitish": "deadbeef1234"}, '
    ...     b'{"tag_name": "v1.7.0"}]'
    ... )
    >>> get_latest_version_name_from_data(payload)
    'v1.7.0'
    """
    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name != "nightly":
                return version_name
        else:
            raise LookupError("Couldn't find a non-nightly release.")

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        raise ValueError("Parsing the received information failed.")


def get_latest_nightly_hash(data: bytes) -> str:
    """Return the commit hash advertised by the nightly release.

    Nightly builds are represented by a single moving release. Foundry compares
    the shortened target commit hash with the current ``nightly-...`` version
    name.

    Parameters
    ----------
    data : bytes
        Raw bytes or bytearray being parsed.

    Returns
    -------
    str
        Short target commit hash for the nightly release, or an empty string.

    Examples
    --------
    >>> payload = (
    ...     b'[{"tag_name": "nightly", "target_commitish": "deadbeef1234"}, '
    ...     b'{"tag_name": "v1.7.0"}]'
    ... )
    >>> get_latest_nightly_hash(payload)
    'deadbeef'
    """
    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name == "nightly":
                return release_info["target_commitish"][:SHORT_COMMIT_LENGTH]
        else:
            # couldn't find nightly release
            return ""

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        return ""


def is_nightly_new(new_nightly_hash: str):
    """Return whether a nightly hash is newer than this build.

    Stable builds always consider nightly builds newer. Nightly builds compare
    the current version suffix with the advertised nightly commit prefix.

    Parameters
    ----------
    new_nightly_hash : str
        Short commit hash advertised by the nightly release.

    Returns
    -------
    bool
        Whether the requested condition is true.
    """
    current_version = get_current_version_name()

    if not current_version.startswith("nightly-"):
        # current version is a stable release, nightly releases should always be newer than stable releases
        return True

    current_nightly_hash = current_version.removeprefix("nightly-")

    # we expect new hashes to be the same length or longer, but just in case make sure they are the same size
    if len(new_nightly_hash) < len(current_nightly_hash):
        current_nightly_hash = current_nightly_hash[: len(new_nightly_hash)]

    # there's always only one nightly release, and it's the most up to date, so if these don't match, there's a new one
    return not new_nightly_hash.startswith(current_nightly_hash)


def check_for_update() -> tuple[str, str]:
    """Fetch the latest stable and nightly release identifiers.

    The update UI uses the stable tag and nightly commit hash to decide which,
    if any, dialogs to show for the selected release channel. This helper is
    the single fetch-and-parse step shared by startup checks and explicit user
    checks, so both code paths compare the same release snapshot before
    applying different UI policy.

    Returns
    -------
    tuple[str, str]
        Latest stable version name and latest nightly commit hash.

    Examples
    --------
    The helper returns the stable tag and the shortened nightly commit hash as
    a two-item tuple that downstream UI code can compare against settings:

    >>> stable_version, nightly_hash = check_for_update()
    >>> isinstance(stable_version, str), isinstance(nightly_hash, str)
    (True, True)
    """
    data = get_release_data()

    latest_version_name = get_latest_version_name_from_data(data)
    latest_nightly_hash = get_latest_nightly_hash(data)

    return latest_version_name, latest_nightly_hash


class UpdateChecker(QThread):
    """Run the GitHub release check on demand or in the background.

    The main window uses this worker during startup and when the user manually
    checks for updates. The worker stores whether the request came from the
    blocking or background path, performs one GitHub release query, and reports
    the parsed stable/nightly identifiers back to the UI thread through Qt
    signals. It does not decide whether a release should be shown to the user;
    it only carries request mode into the result so the owning widget can apply
    release-channel policy afterward. The lifecycle is intentionally narrow:
    callers stage one request, :meth:`run` performs one fetch-and-parse pass,
    and the result is handed back to :class:`UpdateCheckMixin` for
    user-facing policy.

    Attributes
    ----------
    blocking : bool
        Whether the most recent check was started from the blocking code path.
    check_failed : Signal
        Signal emitted with an error message when the check fails.
    check_finished : Signal
        Signal emitted with stable-tag and nightly-hash results.
    honor_ignore : bool
        Whether ignored versions should still suppress update dialogs.

    Notes
    -----
    :meth:`run_blocking` and :meth:`run_in_background` set the same per-run
    flags and then choose how :meth:`run` executes. That keeps one
    implementation of the network and parsing path while still letting the
    caller distinguish startup checks from explicit user-triggered checks.

    Fully runnable examples would need a live Qt event loop plus either real
    GitHub access or invasive monkeypatching of ``check_for_update``. The
    example below focuses on the worker-state transitions that maintainers most
    often need to reason about when tracing startup versus manual checks.

    See Also
    --------
    UpdateCheckMixin
        Owns the worker and turns its results into startup or user-initiated
        dialogs.

    Examples
    --------
    Manual checks stage a blocking run so the caller can immediately surface
    success or failure dialogs. The worker carries both the execution mode and
    the ignore policy into the one fetch-and-emit pass:

    >>> checker = UpdateChecker()
    >>> checker.check_finished.connect(lambda stable, nightly: None)
    >>> checker.run_blocking(honor_ignore=False)  # doctest: +SKIP
    >>> checker.blocking, checker.honor_ignore
    (True, False)

    Startup checks reuse the same worker state, but they hand execution to the
    Qt thread so the main window can keep launching while release metadata is
    fetched:

    >>> checker = UpdateChecker()
    >>> checker.run_in_background(honor_ignore=True)  # doctest: +SKIP
    >>> checker.blocking, checker.honor_ignore
    (False, True)
    """

    check_finished = Signal(str, str)
    check_failed = Signal(str)

    def __init__(self):
        """Initialize per-run flags used by the update worker."""
        super().__init__()

        self.honor_ignore = False
        """A config that gets set from the outside and that we return to the connected slots."""

        self.blocking = False

    def run_blocking(self, honor_ignore):
        """Check for updates synchronously.

        This path is used when callers need a completed result before
        continuing, such as explicit user-initiated checks.

        Parameters
        ----------
        honor_ignore : bool
            Whether ignored versions should still be honored by the update check.

        Examples
        --------
        A manual "Check for Updates" action stages the worker for the blocking
        path, then performs the fetch immediately in the caller's thread::

            >>> checker = UpdateChecker()
            >>> checker.run_blocking(honor_ignore=False)  # doctest: +SKIP
            >>> checker.blocking, checker.honor_ignore
            (True, False)
        """
        self.honor_ignore = honor_ignore
        self.blocking = True

        self.run()

    def run_in_background(self, honor_ignore):
        """Start the update check on the worker thread.

        This path is used at startup so network latency does not block the main
        editor window.

        Parameters
        ----------
        honor_ignore : bool
            Whether ignored versions should still be honored by the update check.
        """
        self.honor_ignore = honor_ignore
        self.blocking = False

        self.start()

    def run(self):
        """Query release metadata and emit either success or failure signals."""
        try:
            latest_version_name, latest_nightly_hash = check_for_update()
            self.check_finished.emit(latest_version_name, latest_nightly_hash)
        except Exception as e:
            self.check_failed.emit(str(e))


class UpdateCheckMixin:
    # QWidget members
    """Add release-channel-aware update dialogs to a widget.

    The mixin owns one ``UpdateChecker`` and interprets its stable/nightly
    results against persisted settings: release channel, ignored stable version,
    and whether startup checks should run. That keeps networking and version
    parsing separate from the widget-level policy about when dialogs appear,
    which release stream the user follows, and whether a finished check should
    quietly do nothing, open a GitHub link dialog, or report that the editor is
    already up to date.

    The data flow is: ``check_for_update`` stages one request, ``UpdateChecker``
    executes it, ``_on_update_finished`` fans the result into stable and nightly
    policy checks, and the ``_try_query_*`` helpers decide which dialog, if any,
    should open. This mixin is therefore the orchestration layer between
    settings, worker output, and the final update prompts.

    Parameters
    ----------
    *args : tuple
        Positional arguments forwarded to the next widget base class.
    **kwargs : dict
        Keyword arguments forwarded to the next widget base class.

    Attributes
    ----------
    _on_show_settings : Callable
        Callback that opens settings when the user wants to change channels.
    _update_checker : UpdateChecker
        Worker used for network checks.
    setCursor : Callable
        Widget method used to show update-check progress.
    settings : Settings
        Persistent settings that store release-channel and ignore choices.

    Notes
    -----
    Startup checks run in the background so editor launch stays responsive.
    Explicit "check for updates" actions use the blocking path so the user gets
    immediate feedback, including an "Already up to date" dialog when
    appropriate. The mixin is also the point where persisted settings flow back
    into behavior: ignored stable tags suppress repeat prompts, while the
    nightly channel enables the nightly-specific dialog path. In practice,
    ``UpdateChecker`` owns execution, this mixin owns release-channel policy,
    and the ``_try_query_*`` helpers own the final dialog decisions.

    A fully runnable example would have to stand up a Qt widget, persistent
    ``Settings`` storage, and modal dialog interactions. The examples below
    therefore concentrate on the orchestration calls that move update results
    from worker completion into release-channel policy.

    See Also
    --------
    UpdateChecker
        Worker thread that performs the release query.

    Examples
    --------
    A widget that mixes in ``UpdateCheckMixin`` funnels both manual and startup
    checks through the same public entry point while choosing different worker
    modes:

    >>> class UpdateWidget(UpdateCheckMixin):
    ...     def __init__(self):
    ...         self.settings = Settings()
    ...         self._on_show_settings = lambda: None
    ...         super().__init__()
    >>> widget = UpdateWidget()  # doctest: +SKIP
    >>> widget.check_for_update(honor_ignore=False, in_background=False)  # doctest: +SKIP

    The same method can stage the startup path by preserving ignored versions
    and running the worker in the background:

    >>> widget.check_for_update(honor_ignore=True, in_background=True)  # doctest: +SKIP

    Finished results are then routed back through ``_on_update_finished``,
    which decides whether stable or nightly dialogs should open from the saved
    release-channel settings:

    >>> widget._on_update_finished("v1.7.0", "deadbeef")  # doctest: +SKIP
    """
    setCursor: Callable

    # MainWindow members
    settings: Settings
    _on_show_settings: Callable

    def __init__(self, *args, **kwargs):
        """Create the shared update worker and connect its signals.

        The mixin owns one long-lived ``UpdateChecker`` so startup checks and
        manual checks share the same signal wiring, blocking policy, and
        release-channel state stored in Foundry's Qt-backed ``Settings``.

        Parameters
        ----------
        *args : tuple
            Positional arguments forwarded to the next widget base class.
        **kwargs : dict
            Keyword arguments forwarded to the next widget base class.
        """
        super().__init__(*args, **kwargs)

        self._update_checker = UpdateChecker()
        self._update_checker.check_finished.connect(self._on_update_finished)
        self._update_checker.check_failed.connect(self._on_update_failed)

    def _on_update_failed(self, error_message: str):
        """Show an update-check failure dialog.

        Parameters
        ----------
        error_message : str
            Error message produced by the update worker.
        """
        QMessageBox.critical(self, "Update Error", error_message)

    def _on_update_finished(self, stable_version: str, nightly_commit_hash: str):
        """Process stable and nightly update results.

        Manual checks show an "Already up to date" message when neither stable
        nor nightly update prompts were displayed.

        Parameters
        ----------
        stable_version : str
            Latest stable release tag.
        nightly_commit_hash : str
            Short commit hash advertised by the nightly release.
        """
        stable_asked = self._try_query_for_stable_update(stable_version, self._update_checker.honor_ignore)
        nightly_asked = self._try_query_for_nightly_update(nightly_commit_hash)

        # only show this message if we were blocking, aka manually checked for an update
        if not stable_asked and not nightly_asked and self._update_checker.blocking:
            QMessageBox.information(self, "Update", "Already up to date.")

    def _try_query_for_stable_update(self, stable_release_name: str, honor_ignore=True) -> bool:
        """Show the stable-release update dialog when applicable.

        Ignored versions are skipped when requested. Otherwise the dialog links
        to the release tag and lets the user suppress future prompts for that
        stable version. This helper is the policy boundary between fetched
        release data and the stable-channel UI prompt.

        Parameters
        ----------
        stable_release_name : str
            Latest stable release tag.
        honor_ignore : bool, optional
            Whether ignored versions should still be honored by the update check.

        Returns
        -------
        bool
            True when an update dialog was shown.
        """
        assert not stable_release_name.startswith("nightly")

        version_is_ignored = stable_release_name == self.settings.value("editor/version_to_ignore")
        if version_is_ignored and honor_ignore:
            # don't ask for this release again
            return False

        if stable_release_name == get_current_version_name():
            # already have that version
            return False

        latest_release_url = f"{releases_link}/tag/{stable_release_name}"

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
        go_to_github_button.clicked.connect(lambda: open_url(latest_release_url))

        info_box = QMessageBox(
            QMessageBox.Icon.Information,
            "New release available",
            f"New Version '{stable_release_name}' is available.",
        )

        ignore_button = QPushButton(f"Don't ask again for '{stable_release_name}'")
        ignore_button.clicked.connect(lambda: self._ignore_latest_version(stable_release_name))
        info_box.addButton(ignore_button, QMessageBox.ButtonRole.NoRole)

        info_box.addButton(QMessageBox.StandardButton.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.ButtonRole.AcceptRole)

        info_box.exec()

        return True

    def _try_query_for_nightly_update(self, nightly_commit_hash: str) -> bool:
        """Show the nightly update dialog when the user follows nightlies.

        Nightly prompts are shown only for the nightly release channel and only
        when the advertised hash differs from the installed nightly build. This
        keeps stable users out of the nightly path while still surfacing
        nightly-only actions such as switching release channels.

        Parameters
        ----------
        nightly_commit_hash : str
            Short commit hash advertised by the nightly release.

        Returns
        -------
        bool
            True when an update dialog was shown.
        """
        if self.settings.value("editor/release_channel") != ReleaseChannel.NIGHTLY:
            # not interested in nightly
            return False

        if not is_nightly_new(nightly_commit_hash):
            # already have that version
            return False

        info_box = QMessageBox(
            QMessageBox.Icon.Information,
            "Newer nightly release available",
            "A newer 'nightly' version is available for download.",
        )

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest nightly")
        go_to_github_button.clicked.connect(lambda: open_url(releases_link))

        goto_settings_button = QPushButton(icon("sliders.svg"), "Change release channel")
        goto_settings_button.clicked.connect(self._on_show_settings)
        info_box.addButton(goto_settings_button, QMessageBox.ButtonRole.NoRole)

        info_box.addButton(QMessageBox.StandardButton.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.ButtonRole.AcceptRole)

        info_box.exec()

        return True

    def _ignore_latest_version(self, latest_version: str):
        """Persist the stable release tag the user chose to ignore.

        Parameters
        ----------
        latest_version : str
            Stable release tag to suppress in future checks.
        """
        self.settings.setValue("editor/version_to_ignore", latest_version)

    def check_for_update(self, honor_ignore=True, in_background=True):
        """Start an update check through the shared worker.

        Background checks are used at startup. Blocking checks are used for
        explicit user actions so completion feedback can be shown immediately.
        The method is the main Qt entry point that turns user intent and
        persisted ignore policy into either a background startup check or a
        blocking manual check on the shared worker. It also owns the small UI
        state transition around a request: show the wait cursor, prevent
        concurrent checks from reusing the worker, and route the chosen request
        mode into the callbacks that eventually decide whether a startup check,
        manual check, or ignore rule should surface a dialog. The worker then
        returns to this mixin through the connected success and failure dialog
        callbacks.

        Parameters
        ----------
        honor_ignore : bool, optional
            Whether ignored versions should still be honored by the update check.
        in_background : bool, optional
            Whether to run the network check on the worker thread.

        Examples
        --------
        Manual checks use the blocking path so the result can immediately drive
        the finished-dialog policy:

        >>> widget = UpdateWidget()  # doctest: +SKIP
        >>> widget.check_for_update(honor_ignore=False, in_background=False)  # doctest: +SKIP
        >>> widget._update_checker.blocking, widget._update_checker.honor_ignore
        (True, False)

        Startup checks keep the same workflow entry point but switch the worker
        into background mode:

        >>> widget = UpdateWidget()  # doctest: +SKIP
        >>> widget.check_for_update(honor_ignore=True, in_background=True)  # doctest: +SKIP
        >>> widget._update_checker.blocking, widget._update_checker.honor_ignore
        (False, True)
        """
        self.setCursor(Qt.CursorShape.WaitCursor)

        if self._update_checker.isRunning():
            QMessageBox.critical(self, "Update Error", "An update check is already running.")

        elif in_background:
            self._update_checker.run_in_background(honor_ignore)

        else:
            self._update_checker.run_blocking(honor_ignore)

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def check_for_update_on_startup(self):
        """Start the configured startup update check."""
        if not self._should_check():
            return

        self.check_for_update()

    def _should_check(self) -> bool:
        """Determine whether startup should launch an update check.

        The first startup asks the user to choose a release-channel policy, and
        later startups use that persisted setting to decide whether the Qt
        startup path should queue the worker before the main window finishes
        settling and whether the update workflow should run at all for that
        launch.

        Returns
        -------
        bool
            True when the configured release channel should be checked.
        """
        if not self.settings.value("editor/asked_for_startup"):
            self._ask_for_release_channel()

        return self.settings.value("editor/release_channel") != ReleaseChannel.NONE

    def _ask_for_release_channel(self):
        """Ask the user whether startup update checks should run.

        The first acceptance defaults to stable releases. Declining disables
        automatic update checks until settings are changed.
        """
        answer = QMessageBox.question(
            self,
            "Automatic Update Checks",
            "Do you want the editor to automatically check for updates on startup? You can change this later in "
            "the Editor settings.",
        )

        self.settings.setValue("editor/asked_for_startup", True)

        if answer == QMessageBox.StandardButton.Yes:
            # default to stable on first try
            self.settings.setValue("editor/release_channel", ReleaseChannel.STABLE)
        else:
            self.settings.setValue("editor/release_channel", ReleaseChannel.NONE)
