from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry import icon
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.asm import load_asm_enemy, load_asm_filename, load_asm_level, save_asm, save_asm_filename
from foundry.gui.m3l import save_m3l, save_m3l_filename
from foundry.gui.settings import Settings


class FileMenu(QMenu):
    def __init__(self, level_ref: LevelRef, settings: Settings, title="&File"):
        super(FileMenu, self).__init__(title)

        self.level_ref = level_ref
        self.settings = settings

        self.triggered.connect(self._on_trigger)

        self.open_rom_action = self.addAction("Open ROM")
        self.open_rom_action.setIcon(icon("folder.svg"))

        self.addSeparator()

        self.save_rom_action = self.addAction("Save ROM")
        self.save_rom_action.setIcon(icon("save.svg"))

        self.save_rom_as_action = self.addAction("Save ROM as ...")
        self.save_rom_as_action.setIcon(icon("save.svg"))

        self.addSeparator()

        m3l_menu = QMenu("M3L")
        m3l_menu.setIcon(icon("file.svg"))

        self.open_m3l_action = m3l_menu.addAction("Open M3L")
        self.open_m3l_action.setIcon(icon("folder.svg"))

        self.save_m3l_action = m3l_menu.addAction("Save M3L")
        self.save_m3l_action.setIcon(icon("save.svg"))

        asm_menu = QMenu("ASM")
        asm_menu.setIcon(icon("cpu.svg"))

        self.open_level_asm_action = asm_menu.addAction("Open Level")
        self.open_level_asm_action.setIcon(icon("folder.svg"))
        # open_level_asm.triggered.connect(self.on_open_asm)

        self.save_level_asm_action = asm_menu.addAction("Save Level")
        self.save_level_asm_action.setIcon(icon("save.svg"))

        asm_menu.addSeparator()

        self.import_enemy_asm_action = asm_menu.addAction("Import Enemies")
        self.import_enemy_asm_action.setIcon(icon("upload.svg"))

        self.export_enemy_asm_action = asm_menu.addAction("Export Enemies")
        self.export_enemy_asm_action.setIcon(icon("download.svg"))

        self.addMenu(m3l_menu)
        self.addMenu(asm_menu)

        self.addSeparator()

        self.settings_action = self.addAction("Editor Settings")
        self.settings_action.setIcon(icon("sliders.svg"))

        self.addSeparator()

        self.exit_action = self.addAction("Exit")
        self.exit_action.setIcon(icon("power.svg"))

    def _on_trigger(self, action: QAction):
        if action is self.save_level_asm_action:
            self.on_save_level_asm()
        elif action is self.export_enemy_asm_action:
            self.on_save_enemy_asm()
        elif action is self.open_level_asm_action:
            self.on_open_level_asm()
        elif action is self.import_enemy_asm_action:
            self.on_import_enemies_from_asm()
        elif action is self.save_m3l_action:
            self.on_save_m3l()

    def on_open_level_asm(self):
        if not (pathname := load_asm_filename("Level ASM", self.settings.value("editor/default dir path"))):
            return

        load_asm_level(pathname, self.level_ref.level)

    def on_import_enemies_from_asm(self):
        if not (pathname := load_asm_filename("Enemy ASM", self.settings.value("editor/default dir path"))):
            return

        load_asm_enemy(pathname, self.level_ref.level)

    def on_save_level_asm(self):
        suggested_file = f"{self.settings.value('editor/default dir path')}/{self.level_ref.name}.asm"

        level_asm, _ = self.level_ref.level.to_asm()

        self.save_asm(suggested_file, level_asm, "Level ASM")

    def on_save_enemy_asm(self):
        suggested_file = f"{self.settings.value('editor/default dir path')}/{self.level_ref.name}_enemy.asm"

        _, enemy_asm = self.level_ref.level.to_asm()

        self.save_asm(suggested_file, enemy_asm, "Enemy ASM")

    def save_asm(self, suggested_file: str, asm: str, what: str):
        if not (pathname := save_asm_filename(what, suggested_file)):
            return

        save_asm(what, pathname, asm)

    def on_save_m3l(self):
        suggested_file = self.settings.value("editor/default dir path") + "/" + self.level_ref.name + ".m3l"

        if not (pathname := save_m3l_filename(suggested_file)):
            return

        m3l_bytes = self.level_ref.level.to_m3l()

        save_m3l(pathname, m3l_bytes)
