"""Debug-menu workflows for command export, replay, and M3L comparison.

This module collects developer-facing tools that inspect or replay the live
editor state. The actions here expose the same command and export boundaries
used elsewhere in Foundry, but package them into a focused surface for
debugging undo streams and serialized level snapshots.

See Also
--------
foundry.gui.commands
    Supplies the command payloads exported and replayed by this menu.
foundry.gui.m3l
    Supplies the snapshot format used for debug comparisons.
"""

import pickle
from typing import Any, cast

from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import QMenu, QMessageBox

from foundry import root_dir
from foundry.gui.commands import UndoCommand

DEBUG_M3L_PATH = "debug.m3l"

EXPORTED_UNDO_STACK_PATH = "undo_stack_export.bin"


class DebugMenu(QMenu):
    """Expose debugging workflows for undo replay and `M3L` comparisons.

    This menu packages developer-facing tools that help reason about editor
    mutations. It can serialize the live undo stack, replay that serialized
    command stream against the open editor window, and compare the live level's
    `M3L` export against a saved debug baseline.

    Parameters
    ----------
    main_window : MainWindow
        Main editor window that owns the undo stack, level reference, and level
        view used by the debug workflows.

    Attributes
    ----------
    _main_window : MainWindow
        Main window that supplies the live undo stack and level state.
    export_stack_action : QAction
        Action that serializes the undo stack to a debug file.
    replay_stack_action : QAction
        Action that rebuilds commands from the serialized debug file.
    save_as_m3l_action : QAction
        Action that writes the active level to the debug `M3L` baseline.
    compare_with_m3l_action : QAction
        Action that compares the active level export against the debug
        baseline.
    """

    def __init__(self, main_window):
        """Create the debug menu for a main editor window.

        The menu is intentionally thin UI over editor internals: every action
        reaches into the live undo stack or current level export so debugging
        workflows observe the same state that save, replay, and comparison code
        sees elsewhere in the application.

        Parameters
        ----------
        main_window
            Main editor window that owns the undo stack, level reference, and
            level view used by the debug workflows.
        """
        super(DebugMenu, self).__init__("Debug")

        self._main_window = main_window

        self.setTitle("Debug")
        self.export_stack_action = self.addAction("Export UndoStack")
        self.export_stack_action.triggered.connect(self._on_export_stack)

        self.replay_stack_action = self.addAction("Replay UndoStack")
        self.replay_stack_action.triggered.connect(self._on_replay_stack)

        self.addSeparator()

        self.save_as_m3l_action = self.addAction("Save as M3L")
        self.save_as_m3l_action.triggered.connect(self._on_save_as_m3l)

        self.compare_with_m3l_action = self.addAction("Compare with M3L")
        self.compare_with_m3l_action.triggered.connect(self._on_compare_with_m3l)

    def _on_export_stack(self):
        """Serialize the live undo stack to the debug export file.

        Individual commands are exported through `UndoCommand.to_data()`.
        Macros are flattened with explicit start and end markers so the replay
        path can reconstruct the same grouping later. The exported file is a
        debugging artifact for replaying or inspecting editor mutations outside
        the live stack.
        """
        undo_stack: QUndoStack = self._main_window.undo_stack

        command_data = []

        with (root_dir / EXPORTED_UNDO_STACK_PATH).open("wb") as f:
            command_index = 0

            while command_index < undo_stack.count():
                command = cast(UndoCommand, undo_stack.command(command_index))

                if command.__class__ is QUndoCommand:
                    # only macros are saved as a pure QUndoCommand
                    macro_data = self._export_macro(self, command)
                    command_data.extend(macro_data)

                else:
                    data_line = self._export_command(command)
                    command_data.append(data_line)

                command_index += 1

            f.write(pickle.dumps(command_data, protocol=pickle.HIGHEST_PROTOCOL))

    @staticmethod
    def _export_macro(self, macro_command: QUndoCommand):
        """Serialize a Qt undo macro and its child commands.

        The sentinel records preserve Qt macro grouping so the replay path can
        call ``beginMacro`` and ``endMacro`` at the same boundaries as the
        original editor session.

        Parameters
        ----------
        macro_command : QUndoCommand
            Macro wrapper stored on the undo stack.

        Returns
        -------
        list[list[str | list[str]]]
            Serialized command records beginning with `MACRO_START`, followed
            by each exported child command, and ending with `MACRO_END`.
        """
        command_data = [["MACRO_START", [macro_command.text()]]]
        print("Macro Start")

        for child_index in range(macro_command.childCount()):
            child_command = macro_command.child(child_index)

            command_data.append(self._export_command(child_command))

        command_data.append(["MACRO_END"])

        print("Macro End")

        return command_data

    @staticmethod
    def _export_command(command: UndoCommand) -> list[str]:
        """Serialize a single undo command.

        The exported record keeps only the command class name and serialized
        payload so replay goes through each command's normal ``from_data``
        reconstruction path.

        Parameters
        ----------
        command : UndoCommand
            Command instance pulled from the undo stack.

        Returns
        -------
        list[str]
            Command class name followed by the data returned from
            `UndoCommand.to_data()`.
        """
        export_dict = command.to_data()

        print(command.__class__.__name__, export_dict)

        data_line = [command.__class__.__name__] + export_dict
        return data_line

    def _on_replay_stack(self):
        """Replay the serialized undo stack into the editor window.

        The debug file is read back into command records, then each record is
        reconstructed against the active editor window so replay exercises the
        same command classes and undo-stack integration used in normal editing.
        """
        undo_stack: QUndoStack = self._main_window.undo_stack

        with (root_dir / EXPORTED_UNDO_STACK_PATH).open("rb") as f:
            command_data = pickle.loads(f.read())

        command_data_index = 0
        while command_data_index < len(command_data):
            class_name, *args = command_data[command_data_index]

            print(class_name, args)

            if class_name == "MACRO_START":
                command_data_index = self._import_macro(command_data, command_data_index, undo_stack)

                continue

            self._import_command(args, class_name, undo_stack)
            command_data_index += 1

    def _import_macro(self, command_data, command_data_index: int | Any, undo_stack: QUndoStack) -> int | Any:
        """Rebuild a macro group from serialized undo-stack records.

        Macro replay walks the serialized records until ``MACRO_END`` and uses
        Qt's macro API so grouped undo history behaves like the original stack
        export.

        Parameters
        ----------
        command_data : list[list]
            Serialized undo records loaded from the debug export file.
        command_data_index : int
            Index of the `MACRO_START` record.
        undo_stack : QUndoStack
            Undo stack that receives the reconstructed commands.

        Returns
        -------
        int
            Index of the next unread record after the macro terminator.
        """
        print(command_data[command_data_index])
        macro_name = command_data[command_data_index][1][0]
        command_data_index += 1

        undo_stack.beginMacro(macro_name)
        while command_data_index < len(command_data):
            class_name, *args = command_data[command_data_index]

            if class_name == "MACRO_END":
                command_data_index += 1

                break

            self._import_command(args, class_name, undo_stack)
            command_data_index += 1

        undo_stack.endMacro()

        return command_data_index

    def _import_command(self, args, class_name, undo_stack):
        """Rebuild one serialized command and push it onto the undo stack.

        Magic placeholders for the active level and level view are resolved
        here so exported command payloads stay portable across editor sessions.

        Parameters
        ----------
        args : list
            Serialized arguments produced by `UndoCommand.to_data()`.
        class_name : str
            Name of the command class to recreate.
        undo_stack : QUndoStack
            Undo stack that receives the reconstructed command.
        """
        command_class = _command_classes.get(class_name, QUndoCommand)

        # replace magic values
        if UndoCommand.MAGIC_VALUE_LEVEL in args:
            level_arg_index = args.index(UndoCommand.MAGIC_VALUE_LEVEL)
            args[level_arg_index] = self._main_window.level_ref

        if UndoCommand.MAGIC_VALUE_LEVEL_VIEW in args:
            level_view_arg_index = args.index(UndoCommand.MAGIC_VALUE_LEVEL_VIEW)
            args[level_view_arg_index] = self._main_window.level_view

        print(class_name, args)

        undo_stack.push(command_class.from_data(*args))

    def _on_save_as_m3l(self):
        """Write the open level to the debug `M3L` baseline file.

        This captures the live level exactly as ``to_m3l()`` currently exports
        it so later comparisons can detect regressions in level serialization.
        """
        level = self._main_window.level_ref.level
        m3l_bytes = level.to_m3l()

        (root_dir / DEBUG_M3L_PATH).write_bytes(m3l_bytes)

    def _on_compare_with_m3l(self):
        """Compare the open level export against the debug `M3L` baseline.

        The comparison is byte-for-byte and reports the first differing offset,
        which makes it useful when validating undo-command replay or serializer
        changes against a known-good debug export.

        Raises
        ------
        ValueError
            If the byte streams differ in length but no differing byte can be
            located.
        """
        level = self._main_window.level_ref.level
        m3l_bytes = level.to_m3l()

        expected_m3l_bytes = (root_dir / DEBUG_M3L_PATH).read_bytes()

        if m3l_bytes != expected_m3l_bytes:
            for i in range(min(len(m3l_bytes), len(expected_m3l_bytes))):
                if m3l_bytes[i] != expected_m3l_bytes[i]:
                    first_difference = (i, m3l_bytes[i], expected_m3l_bytes[i])
                    break

            else:
                raise ValueError("M3L mismatch, but no differences found.")

            QMessageBox.critical(
                self._main_window,
                "M3L mismatch",
                f"First difference at offset {first_difference[0]}: "
                f"{first_difference[1]:#x)} != {first_difference[2]:#x}",
            )


_command_classes = {}

_classes_to_check = [UndoCommand]

while _classes_to_check:
    class_to_check = _classes_to_check.pop()

    sub_classes = class_to_check.__subclasses__()

    _classes_to_check.extend(sub_classes)
    _command_classes.update({cls.__name__: cls for cls in sub_classes})
