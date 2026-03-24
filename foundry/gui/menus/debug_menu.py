import pickle
from typing import Any, cast

from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import QMenu, QMessageBox

from foundry import root_dir
from foundry.gui.commands import UndoCommand


class DebugMenu(QMenu):
    def __init__(self, main_window):
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
        undo_stack: QUndoStack = self._main_window.undo_stack

        command_data = []

        with (root_dir / "undo_stack_export.bin").open("wb") as f:
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
        export_dict = command.to_data()

        print(command.__class__.__name__, export_dict)

        data_line = [command.__class__.__name__] + export_dict
        return data_line

    def _on_replay_stack(self):
        undo_stack: QUndoStack = self._main_window.undo_stack

        with (root_dir / "undo_stack_export.txt").open("rb") as f:
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
        level = self._main_window.level_ref.level
        m3l_bytes = level.to_m3l()

        (root_dir / "debug.m3l").write_bytes(m3l_bytes)

    def _on_compare_with_m3l(self):
        level = self._main_window.level_ref.level
        m3l_bytes = level.to_m3l()

        expected_m3l_bytes = (root_dir / "debug.m3l").read_bytes()

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
