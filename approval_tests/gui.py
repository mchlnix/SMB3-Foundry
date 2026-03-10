from typing import TypeAlias, cast

from PySide6.QtGui import QGuiApplication, QImage, QPixmap, Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

image_source: TypeAlias = QPixmap | str


def _get_pixmap_from_source(image: image_source) -> QPixmap:
    if isinstance(image, str):
        image = QPixmap(image)

    return image


class ApprovalDialog(QDialog):
    Ignore = 99
    Overwrite = 100
    image_layout: QBoxLayout

    def __init__(self, test_name: str, reference_image: QPixmap, generated_image: QPixmap):
        super(ApprovalDialog, self).__init__()

        self.setWindowTitle(test_name)

        main_layout = QVBoxLayout(self)

        self._reference_image = reference_image
        self._generated_image = generated_image

        ref_image = QLabel()
        ref_image.setPixmap(reference_image)

        gen_image = QLabel()
        gen_image.setPixmap(generated_image)

        scroll_area = QScrollArea()

        self.layout().addWidget(scroll_area)

        screen_width, screen_height = cast(tuple, QGuiApplication.primaryScreen().size().toTuple())

        if reference_image.width() + gen_image.width() >= screen_width:
            self.image_layout = QVBoxLayout()
        else:
            self.image_layout = QHBoxLayout()

        self.image_layout.addStretch()
        self.image_layout.addWidget(ref_image)
        self.image_layout.addWidget(QLabel(">>>"))
        self.image_layout.addWidget(gen_image)
        self.image_layout.addStretch()

        scroll_area.setWidget(QWidget())
        scroll_area.setWidgetResizable(True)

        scroll_area.widget().setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        scroll_area.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        scroll_area.widget().setLayout(self.image_layout)

        def _sizeHint():
            orig_size = scroll_area.widget().sizeHint()

            orig_size.setHeight(orig_size.height() + 20)
            orig_size.setWidth(orig_size.width() + 20)

            if orig_size.width() > screen_width - 20:
                orig_size.setWidth(screen_width - 20)

            if orig_size.height() > screen_height - 20:
                orig_size.setHeight(screen_height - 20)

            return orig_size

        scroll_area.sizeHint = _sizeHint

        button_box = QDialogButtonBox()

        button_box.addButton("Reject", QDialogButtonBox.ButtonRole.RejectRole).clicked.connect(self.reject)
        button_box.addButton(QDialogButtonBox.StandardButton.Ignore).clicked.connect(self._on_ignore)

        apply_button = button_box.addButton("Accept as new Reference", QDialogButtonBox.ButtonRole.ApplyRole)
        apply_button.clicked.connect(self._on_overwrite)
        apply_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_A)

        diff_button = button_box.addButton("Show Diff", QDialogButtonBox.ButtonRole.HelpRole)
        diff_button.clicked.connect(self._on_diff)

        if self._reference_image.size() != self._generated_image.size():
            diff_button.setEnabled(False)

        main_layout.addWidget(scroll_area)
        main_layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)

    def _on_overwrite(self):
        self.done(self.Overwrite)

    def _on_ignore(self):
        self.done(self.Ignore)

    def _on_diff(self):
        # get both images
        ref_img = self._reference_image.toImage()
        ref_bytes = ref_img.bits()
        gen_img = self._generated_image.toImage()
        gen_bytes = gen_img.bits()

        # make a diff of it
        diff_bytes = bytearray()

        for ref_byte, gen_byte in zip(ref_bytes, gen_bytes):
            diff_bytes.append(ref_byte ^ gen_byte)

        # generate new image from it
        diff_img = QImage(
            diff_bytes,
            self._reference_image.width(),
            self._reference_image.height(),
            self._reference_image.toImage().format(),
        )

        # display diff in dialog
        dialog = QDialog()
        dialog.setLayout(QVBoxLayout())

        label = QLabel()
        label.setPixmap(QPixmap.fromImage(diff_img))

        dialog.layout().addWidget(label)

        dialog.exec()

    @staticmethod
    def compare(test_name: str, reference_image: image_source, generated_image: image_source):
        reference_image = _get_pixmap_from_source(reference_image)
        generated_image = _get_pixmap_from_source(generated_image)

        if generated_image.toImage() == reference_image.toImage():
            return QDialog.DialogCode.Accepted

        dialog = ApprovalDialog(test_name, reference_image, generated_image)

        dialog.exec()

        return dialog.result()
